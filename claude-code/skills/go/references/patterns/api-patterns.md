# Go API Patterns

HTTP handlers, middleware, routing, and RESTful API design with Gin.

---

## Gin Fundamentals

### Basic Setup

```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    // Production mode
    gin.SetMode(gin.ReleaseMode)

    r := gin.New()

    // Middleware
    r.Use(gin.Logger())
    r.Use(gin.Recovery())

    // Routes
    r.GET("/health", healthHandler)

    r.Run(":8080")
}

func healthHandler(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{"status": "healthy"})
}
```

### Router Groups

```go
func setupRoutes(r *gin.Engine, h *Handlers) {
    // API version group
    v1 := r.Group("/api/v1")
    {
        // Public routes
        v1.POST("/auth/login", h.Login)
        v1.POST("/auth/register", h.Register)

        // Protected routes
        protected := v1.Group("")
        protected.Use(AuthMiddleware())
        {
            users := protected.Group("/users")
            {
                users.GET("", h.ListUsers)
                users.GET("/:id", h.GetUser)
                users.POST("", h.CreateUser)
                users.PUT("/:id", h.UpdateUser)
                users.DELETE("/:id", h.DeleteUser)
            }

            orders := protected.Group("/orders")
            {
                orders.GET("", h.ListOrders)
                orders.GET("/:id", h.GetOrder)
                orders.POST("", h.CreateOrder)
            }
        }
    }
}
```

---

## Handler Structure

### Handler with Dependencies

```go
type Handlers struct {
    userService  *service.UserService
    orderService *service.OrderService
    logger       *slog.Logger
}

func NewHandlers(
    userSvc *service.UserService,
    orderSvc *service.OrderService,
    logger *slog.Logger,
) *Handlers {
    return &Handlers{
        userService:  userSvc,
        orderService: orderSvc,
        logger:       logger,
    }
}
```

### Standard Handler Pattern

```go
func (h *Handlers) GetUser(c *gin.Context) {
    ctx := c.Request.Context()

    // Parse path parameters
    id := c.Param("id")
    if id == "" {
        c.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
        return
    }

    // Call service
    user, err := h.userService.GetByID(ctx, id)
    if err != nil {
        if errors.Is(err, service.ErrNotFound) {
            c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
            return
        }
        h.logger.Error("get user failed", "error", err)
        c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
        return
    }

    c.JSON(http.StatusOK, user)
}
```

---

## Request Binding

### JSON Binding

```go
type CreateUserInput struct {
    Name  string `json:"name" binding:"required,min=1,max=100"`
    Email string `json:"email" binding:"required,email"`
    Age   int    `json:"age" binding:"gte=0,lte=150"`
}

func (h *Handlers) CreateUser(c *gin.Context) {
    var input CreateUserInput

    if err := c.ShouldBindJSON(&input); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "error":   "invalid request body",
            "details": err.Error(),
        })
        return
    }

    // Process valid input...
}
```

### Query Parameters

```go
type ListUsersQuery struct {
    Page     int    `form:"page" binding:"gte=1"`
    PageSize int    `form:"page_size" binding:"gte=1,lte=100"`
    Sort     string `form:"sort" binding:"omitempty,oneof=name email created_at"`
    Order    string `form:"order" binding:"omitempty,oneof=asc desc"`
}

func (h *Handlers) ListUsers(c *gin.Context) {
    query := ListUsersQuery{
        Page:     1,
        PageSize: 20,
        Sort:     "created_at",
        Order:    "desc",
    }

    if err := c.ShouldBindQuery(&query); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // Use query parameters...
}
```

### Path Parameters

```go
func (h *Handlers) GetUserOrder(c *gin.Context) {
    userID := c.Param("user_id")
    orderID := c.Param("order_id")

    // Validate UUIDs
    if _, err := uuid.Parse(userID); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "invalid user_id"})
        return
    }

    // Process...
}
```

---

## Middleware

### Authentication Middleware

```go
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": "authorization header required",
            })
            return
        }

        // Remove "Bearer " prefix
        token = strings.TrimPrefix(token, "Bearer ")

        claims, err := validateToken(token)
        if err != nil {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": "invalid token",
            })
            return
        }

        // Store user info in context
        c.Set("user_id", claims.UserID)
        c.Set("user_role", claims.Role)

        c.Next()
    }
}

// Helper to get user from context
func GetUserID(c *gin.Context) string {
    id, _ := c.Get("user_id")
    return id.(string)
}
```

### Logging Middleware

```go
func LoggingMiddleware(logger *slog.Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        query := c.Request.URL.RawQuery

        c.Next()

        latency := time.Since(start)
        status := c.Writer.Status()

        logger.Info("request",
            slog.String("method", c.Request.Method),
            slog.String("path", path),
            slog.String("query", query),
            slog.Int("status", status),
            slog.Duration("latency", latency),
            slog.String("client_ip", c.ClientIP()),
        )
    }
}
```

### CORS Middleware

```go
func CORSMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Access-Control-Allow-Origin", "*")
        c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        c.Header("Access-Control-Max-Age", "86400")

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(http.StatusNoContent)
            return
        }

        c.Next()
    }
}
```

### Rate Limiting Middleware

```go
import "golang.org/x/time/rate"

func RateLimitMiddleware(rps float64, burst int) gin.HandlerFunc {
    limiter := rate.NewLimiter(rate.Limit(rps), burst)

    return func(c *gin.Context) {
        if !limiter.Allow() {
            c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
                "error": "rate limit exceeded",
            })
            return
        }
        c.Next()
    }
}
```

### Request ID Middleware

```go
func RequestIDMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        requestID := c.GetHeader("X-Request-ID")
        if requestID == "" {
            requestID = uuid.New().String()
        }

        c.Set("request_id", requestID)
        c.Header("X-Request-ID", requestID)

        c.Next()
    }
}
```

---

## Response Patterns

### Standard Response Structure

```go
type Response struct {
    Success bool   `json:"success"`
    Data    any    `json:"data,omitempty"`
    Error   string `json:"error,omitempty"`
    Meta    *Meta  `json:"meta,omitempty"`
}

type Meta struct {
    Page       int `json:"page,omitempty"`
    PageSize   int `json:"page_size,omitempty"`
    TotalItems int `json:"total_items,omitempty"`
    TotalPages int `json:"total_pages,omitempty"`
}

func SuccessResponse(c *gin.Context, status int, data any) {
    c.JSON(status, Response{Success: true, Data: data})
}

func ErrorResponse(c *gin.Context, status int, message string) {
    c.JSON(status, Response{Success: false, Error: message})
}

func PaginatedResponse(c *gin.Context, data any, meta Meta) {
    c.JSON(http.StatusOK, Response{
        Success: true,
        Data:    data,
        Meta:    &meta,
    })
}
```

### Usage

```go
func (h *Handlers) ListUsers(c *gin.Context) {
    users, total, err := h.userService.List(ctx, page, pageSize)
    if err != nil {
        ErrorResponse(c, http.StatusInternalServerError, "failed to fetch users")
        return
    }

    PaginatedResponse(c, users, Meta{
        Page:       page,
        PageSize:   pageSize,
        TotalItems: total,
        TotalPages: (total + pageSize - 1) / pageSize,
    })
}
```

---

## Error Handling

### Centralized Error Handler

```go
type AppError struct {
    Code    int    `json:"-"`
    Message string `json:"message"`
    Details any    `json:"details,omitempty"`
}

func (e *AppError) Error() string {
    return e.Message
}

func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()

        if len(c.Errors) == 0 {
            return
        }

        err := c.Errors.Last().Err

        var appErr *AppError
        if errors.As(err, &appErr) {
            c.JSON(appErr.Code, appErr)
            return
        }

        // Log unexpected errors
        slog.Error("unexpected error", "error", err)
        c.JSON(http.StatusInternalServerError, gin.H{
            "message": "internal server error",
        })
    }
}

// Usage in handlers
func (h *Handlers) CreateUser(c *gin.Context) {
    // ...
    if err != nil {
        c.Error(&AppError{
            Code:    http.StatusConflict,
            Message: "user already exists",
        })
        return
    }
}
```

---

## Validation

### Custom Validators

```go
import "github.com/go-playground/validator/v10"

func SetupValidators(v *validator.Validate) {
    // Custom UUID validation
    v.RegisterValidation("uuid", func(fl validator.FieldLevel) bool {
        _, err := uuid.Parse(fl.Field().String())
        return err == nil
    })

    // Custom password validation
    v.RegisterValidation("password", func(fl validator.FieldLevel) bool {
        password := fl.Field().String()
        if len(password) < 8 {
            return false
        }
        hasUpper := regexp.MustCompile(`[A-Z]`).MatchString(password)
        hasLower := regexp.MustCompile(`[a-z]`).MatchString(password)
        hasNumber := regexp.MustCompile(`[0-9]`).MatchString(password)
        return hasUpper && hasLower && hasNumber
    })
}

type RegisterInput struct {
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required,password"`
}
```

### Binding with Custom Validator

```go
func init() {
    if v, ok := binding.Validator.Engine().(*validator.Validate); ok {
        SetupValidators(v)
    }
}
```

---

## RESTful Resource Design

### Standard Endpoints

| Method | Path | Action | Status Codes |
|--------|------|--------|--------------|
| GET | /resources | List all | 200 |
| GET | /resources/:id | Get one | 200, 404 |
| POST | /resources | Create | 201, 400 |
| PUT | /resources/:id | Update | 200, 404, 400 |
| DELETE | /resources/:id | Delete | 204, 404 |

### Nested Resources

```go
// /users/:user_id/orders
orders := users.Group("/:user_id/orders")
{
    orders.GET("", h.ListUserOrders)
    orders.GET("/:order_id", h.GetUserOrder)
    orders.POST("", h.CreateUserOrder)
}
```

### Query Filtering

```go
type ListOrdersQuery struct {
    Status    string    `form:"status" binding:"omitempty,oneof=pending processing shipped delivered"`
    CreatedAt time.Time `form:"created_after" time_format:"2006-01-02"`
    MinAmount float64   `form:"min_amount" binding:"gte=0"`
}
```

---

## Testing Handlers

### Table-Driven Handler Tests

```go
func TestGetUser(t *testing.T) {
    tests := []struct {
        name       string
        userID     string
        setupMock  func(*mocks.UserService)
        wantStatus int
        wantBody   string
    }{
        {
            name:   "success",
            userID: "123",
            setupMock: func(m *mocks.UserService) {
                m.On("GetByID", mock.Anything, "123").
                    Return(&User{ID: "123", Name: "Alice"}, nil)
            },
            wantStatus: http.StatusOK,
        },
        {
            name:   "not found",
            userID: "999",
            setupMock: func(m *mocks.UserService) {
                m.On("GetByID", mock.Anything, "999").
                    Return(nil, service.ErrNotFound)
            },
            wantStatus: http.StatusNotFound,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            mockSvc := new(mocks.UserService)
            tt.setupMock(mockSvc)

            h := NewHandlers(mockSvc, nil, slog.Default())

            r := gin.New()
            r.GET("/users/:id", h.GetUser)

            req := httptest.NewRequest("GET", "/users/"+tt.userID, nil)
            w := httptest.NewRecorder()

            r.ServeHTTP(w, req)

            assert.Equal(t, tt.wantStatus, w.Code)
        })
    }
}
```

---

## Best Practices Summary

| Practice | Do | Don't |
|----------|-----|-------|
| **Handler size** | Small, single responsibility | Kitchen sink handlers |
| **Dependencies** | Inject via struct | Global variables |
| **Validation** | Use binding tags | Manual validation |
| **Errors** | Centralized handler | Duplicate error logic |
| **Context** | Use `c.Request.Context()` | Ignore context |
| **Logging** | Structured with request ID | fmt.Println |
| **Response** | Consistent structure | Ad-hoc formats |

---

*Companion to: error-handling.md, security-patterns.md*
*Last updated: 2026-01-15*

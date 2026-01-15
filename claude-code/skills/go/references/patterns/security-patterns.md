# Go Security Patterns

Input validation, authentication, authorization, and secure coding practices.

---

## Input Validation

### Never Trust User Input

```go
// ❌ Bad: no validation
func GetUser(c *gin.Context) {
    id := c.Param("id")
    user, _ := db.Query("SELECT * FROM users WHERE id = " + id) // SQL Injection!
}

// ✅ Good: parameterized query
func GetUser(c *gin.Context) {
    id := c.Param("id")
    user, err := queries.GetUser(ctx, id) // sqlc handles parameterization
}
```

### Struct Tag Validation

```go
type CreateUserInput struct {
    Name     string `json:"name" binding:"required,min=1,max=100,alphanum"`
    Email    string `json:"email" binding:"required,email,max=255"`
    Password string `json:"password" binding:"required,min=8,max=72"`
    Age      int    `json:"age" binding:"omitempty,gte=0,lte=150"`
    Role     string `json:"role" binding:"omitempty,oneof=user admin"`
}

func (h *Handlers) CreateUser(c *gin.Context) {
    var input CreateUserInput
    if err := c.ShouldBindJSON(&input); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "invalid input"})
        return
    }
    // Input is now validated...
}
```

### Custom Validators

```go
import "github.com/go-playground/validator/v10"

func RegisterCustomValidators(v *validator.Validate) {
    // No SQL injection characters
    v.RegisterValidation("safesql", func(fl validator.FieldLevel) bool {
        value := fl.Field().String()
        dangerous := []string{"'", "\"", ";", "--", "/*", "*/", "xp_"}
        for _, d := range dangerous {
            if strings.Contains(value, d) {
                return false
            }
        }
        return true
    })

    // UUID format
    v.RegisterValidation("uuid", func(fl validator.FieldLevel) bool {
        _, err := uuid.Parse(fl.Field().String())
        return err == nil
    })
}
```

### Input Depth Limiting (DoS Prevention)

```go
// Limit JSON nesting depth to prevent resource exhaustion
func MaxDepthMiddleware(maxDepth int) gin.HandlerFunc {
    return func(c *gin.Context) {
        if c.Request.Body == nil {
            c.Next()
            return
        }

        body, err := io.ReadAll(io.LimitReader(c.Request.Body, 1<<20)) // 1MB limit
        if err != nil {
            c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{"error": "request too large"})
            return
        }

        if depth := jsonDepth(body); depth > maxDepth {
            c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
                "error": fmt.Sprintf("JSON depth exceeds maximum of %d", maxDepth),
            })
            return
        }

        c.Request.Body = io.NopCloser(bytes.NewReader(body))
        c.Next()
    }
}

func jsonDepth(data []byte) int {
    maxDepth := 0
    currentDepth := 0
    for _, b := range data {
        switch b {
        case '{', '[':
            currentDepth++
            if currentDepth > maxDepth {
                maxDepth = currentDepth
            }
        case '}', ']':
            currentDepth--
        }
    }
    return maxDepth
}
```

---

## Authentication

### Password Hashing

```go
import "golang.org/x/crypto/bcrypt"

const bcryptCost = 12

func HashPassword(password string) (string, error) {
    bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcryptCost)
    if err != nil {
        return "", fmt.Errorf("hash password: %w", err)
    }
    return string(bytes), nil
}

func CheckPassword(password, hash string) bool {
    err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
    return err == nil
}
```

### JWT Token Generation

```go
import "github.com/golang-jwt/jwt/v5"

type Claims struct {
    UserID string `json:"user_id"`
    Role   string `json:"role"`
    jwt.RegisteredClaims
}

type TokenService struct {
    secretKey     []byte
    accessExpiry  time.Duration
    refreshExpiry time.Duration
}

func (s *TokenService) GenerateAccessToken(userID, role string) (string, error) {
    claims := Claims{
        UserID: userID,
        Role:   role,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(s.accessExpiry)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            ID:        uuid.New().String(),
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(s.secretKey)
}

func (s *TokenService) ValidateToken(tokenString string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return s.secretKey, nil
    })

    if err != nil {
        return nil, fmt.Errorf("parse token: %w", err)
    }

    claims, ok := token.Claims.(*Claims)
    if !ok || !token.Valid {
        return nil, errors.New("invalid token")
    }

    return claims, nil
}
```

### Auth Middleware

```go
func AuthMiddleware(tokenSvc *TokenService) gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": "authorization header required",
            })
            return
        }

        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        if tokenString == authHeader {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": "bearer token required",
            })
            return
        }

        claims, err := tokenSvc.ValidateToken(tokenString)
        if err != nil {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
                "error": "invalid or expired token",
            })
            return
        }

        c.Set("user_id", claims.UserID)
        c.Set("user_role", claims.Role)
        c.Next()
    }
}
```

---

## Authorization

### Role-Based Access Control

```go
func RequireRole(roles ...string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userRole, exists := c.Get("user_role")
        if !exists {
            c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
                "error": "no role assigned",
            })
            return
        }

        for _, role := range roles {
            if userRole == role {
                c.Next()
                return
            }
        }

        c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
            "error": "insufficient permissions",
        })
    }
}

// Usage
admin := r.Group("/admin")
admin.Use(AuthMiddleware(tokenSvc), RequireRole("admin"))
{
    admin.GET("/users", h.ListAllUsers)
    admin.DELETE("/users/:id", h.DeleteUser)
}
```

### Resource-Based Authorization

```go
func (h *Handlers) GetOrder(c *gin.Context) {
    ctx := c.Request.Context()
    userID := c.GetString("user_id")
    orderID := c.Param("id")

    order, err := h.orderService.GetByID(ctx, orderID)
    if err != nil {
        // Handle error...
        return
    }

    // Check ownership
    if order.UserID != userID && c.GetString("user_role") != "admin" {
        c.JSON(http.StatusForbidden, gin.H{"error": "access denied"})
        return
    }

    c.JSON(http.StatusOK, order)
}
```

---

## Secrets Management

### Environment Variables

```go
type Config struct {
    DatabaseURL   string
    JWTSecret     []byte
    APIKey        string
}

func LoadConfig() (*Config, error) {
    dbURL := os.Getenv("DATABASE_URL")
    if dbURL == "" {
        return nil, errors.New("DATABASE_URL required")
    }

    jwtSecret := os.Getenv("JWT_SECRET")
    if jwtSecret == "" {
        return nil, errors.New("JWT_SECRET required")
    }
    if len(jwtSecret) < 32 {
        return nil, errors.New("JWT_SECRET must be at least 32 characters")
    }

    return &Config{
        DatabaseURL: dbURL,
        JWTSecret:   []byte(jwtSecret),
        APIKey:      os.Getenv("API_KEY"),
    }, nil
}
```

### Never Log Secrets

```go
// ❌ Bad: logging sensitive data
logger.Info("connecting to database", "url", config.DatabaseURL)

// ✅ Good: mask sensitive data
logger.Info("connecting to database", "host", maskDSN(config.DatabaseURL))

func maskDSN(dsn string) string {
    u, err := url.Parse(dsn)
    if err != nil {
        return "[masked]"
    }
    if u.User != nil {
        u.User = url.UserPassword("***", "***")
    }
    return u.String()
}
```

---

## Rate Limiting

### Global Rate Limiting

```go
import "golang.org/x/time/rate"

func GlobalRateLimiter(rps float64, burst int) gin.HandlerFunc {
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

### Per-IP Rate Limiting

```go
type IPRateLimiter struct {
    ips   map[string]*rate.Limiter
    mu    sync.RWMutex
    rate  rate.Limit
    burst int
}

func NewIPRateLimiter(r float64, b int) *IPRateLimiter {
    return &IPRateLimiter{
        ips:   make(map[string]*rate.Limiter),
        rate:  rate.Limit(r),
        burst: b,
    }
}

func (l *IPRateLimiter) GetLimiter(ip string) *rate.Limiter {
    l.mu.Lock()
    defer l.mu.Unlock()

    limiter, exists := l.ips[ip]
    if !exists {
        limiter = rate.NewLimiter(l.rate, l.burst)
        l.ips[ip] = limiter
    }

    return limiter
}

func (l *IPRateLimiter) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        ip := c.ClientIP()
        limiter := l.GetLimiter(ip)

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

---

## Security Headers

```go
func SecurityHeaders() gin.HandlerFunc {
    return func(c *gin.Context) {
        // Prevent XSS
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-XSS-Protection", "1; mode=block")

        // HTTPS enforcement
        c.Header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

        // Content Security Policy
        c.Header("Content-Security-Policy", "default-src 'self'")

        // Referrer Policy
        c.Header("Referrer-Policy", "strict-origin-when-cross-origin")

        c.Next()
    }
}
```

---

## SQL Injection Prevention

### Use sqlc (Recommended)

```sql
-- name: GetUser :one
SELECT * FROM users WHERE id = $1;

-- name: SearchUsers :many
SELECT * FROM users WHERE name ILIKE $1;
```

sqlc generates parameterized queries automatically, eliminating SQL injection risk.

### Manual Parameterization

```go
// ✅ Good: parameterized query
row := db.QueryRowContext(ctx, "SELECT * FROM users WHERE id = $1", userID)

// ❌ Bad: string concatenation
query := "SELECT * FROM users WHERE id = " + userID // VULNERABLE!
```

---

## CORS Configuration

```go
func CORSMiddleware(allowedOrigins []string) gin.HandlerFunc {
    return func(c *gin.Context) {
        origin := c.GetHeader("Origin")

        // Check if origin is allowed
        allowed := false
        for _, o := range allowedOrigins {
            if o == origin || o == "*" {
                allowed = true
                break
            }
        }

        if allowed {
            c.Header("Access-Control-Allow-Origin", origin)
            c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            c.Header("Access-Control-Allow-Credentials", "true")
            c.Header("Access-Control-Max-Age", "86400")
        }

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(http.StatusNoContent)
            return
        }

        c.Next()
    }
}
```

---

## Secure File Upload

```go
const maxUploadSize = 10 << 20 // 10MB

func (h *Handlers) UploadFile(c *gin.Context) {
    // Limit request body size
    c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, maxUploadSize)

    file, header, err := c.Request.FormFile("file")
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "file required"})
        return
    }
    defer file.Close()

    // Validate file type
    allowedTypes := map[string]bool{
        "image/jpeg": true,
        "image/png":  true,
        "image/gif":  true,
    }

    buffer := make([]byte, 512)
    if _, err := file.Read(buffer); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "cannot read file"})
        return
    }

    contentType := http.DetectContentType(buffer)
    if !allowedTypes[contentType] {
        c.JSON(http.StatusBadRequest, gin.H{"error": "file type not allowed"})
        return
    }

    // Reset file reader
    if seeker, ok := file.(io.Seeker); ok {
        seeker.Seek(0, io.SeekStart)
    }

    // Generate safe filename
    ext := filepath.Ext(header.Filename)
    safeFilename := uuid.New().String() + ext

    // Save file...
}
```

---

## Security Checklist

### Authentication
- [ ] Passwords hashed with bcrypt (cost ≥ 12)
- [ ] JWT tokens with short expiry
- [ ] Secure token storage (httpOnly cookies for web)
- [ ] Token refresh mechanism

### Authorization
- [ ] Role-based access control
- [ ] Resource ownership validation
- [ ] Principle of least privilege

### Input Validation
- [ ] All inputs validated with binding tags
- [ ] JSON depth limiting
- [ ] Request size limiting
- [ ] File upload validation

### Data Protection
- [ ] Secrets from environment variables
- [ ] No secrets in logs
- [ ] Parameterized SQL queries
- [ ] HTTPS enforced

### Headers & CORS
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] HSTS enabled

---

*Companion to: api-patterns.md, error-handling.md*
*Last updated: 2026-01-15*

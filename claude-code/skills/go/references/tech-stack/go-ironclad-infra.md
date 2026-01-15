# Go Ironclad Infrastructure

Deployment, containerization, and production infrastructure for Go applications.

---

## Docker

### Multi-Stage Build (Standard)

```dockerfile
# Build stage
FROM golang:1.25-alpine AS builder

WORKDIR /app

# Dependencies first (cache layer)
COPY go.mod go.sum ./
RUN go mod download

# Build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /app/server ./cmd/server

# Runtime stage
FROM alpine:3.19

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app
COPY --from=builder /app/server .

USER nobody:nobody
EXPOSE 8080
ENTRYPOINT ["./server"]
```

### Build Flags

| Flag | Purpose |
|------|---------|
| `CGO_ENABLED=0` | Static binary, no C dependencies |
| `GOOS=linux` | Target Linux (for containers) |
| `-ldflags="-w -s"` | Strip debug info, smaller binary |
| `-trimpath` | Remove file paths from binary |

### Image Size Optimization

```dockerfile
# Minimal: scratch (no shell, no tools)
FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]

# Balanced: alpine (small, has shell)
FROM alpine:3.19
# ... (shown above)

# Full: debian-slim (more compatibility)
FROM debian:bookworm-slim
```

| Base | Size | Use Case |
|------|------|----------|
| scratch | ~5-15MB | Production, minimal attack surface |
| alpine | ~10-25MB | Production with debugging needs |
| debian-slim | ~50-80MB | Compatibility requirements |

---

## Container Orchestration

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: "3.9"

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app?sslmode=disable
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: myapp:latest
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: myapp-secrets
                  key: database-url
```

---

## Health Checks

### Standard Endpoints

```go
// Health check handler
func healthHandler(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{
        "status": "healthy",
        "time":   time.Now().UTC().Format(time.RFC3339),
    })
}

// Readiness check (with dependencies)
func readyHandler(db *sql.DB) gin.HandlerFunc {
    return func(c *gin.Context) {
        ctx, cancel := context.WithTimeout(c.Request.Context(), 2*time.Second)
        defer cancel()

        if err := db.PingContext(ctx); err != nil {
            c.JSON(http.StatusServiceUnavailable, gin.H{
                "status": "not ready",
                "error":  "database unavailable",
            })
            return
        }

        c.JSON(http.StatusOK, gin.H{"status": "ready"})
    }
}

// Route setup
r.GET("/health", healthHandler)
r.GET("/ready", readyHandler(db))
```

### Kubernetes Probe Configuration

| Probe | Purpose | Failure Action |
|-------|---------|----------------|
| Liveness | Is process running? | Restart container |
| Readiness | Can accept traffic? | Remove from service |
| Startup | Has app started? | Wait before other probes |

---

## Graceful Shutdown

```go
func main() {
    // Create server
    srv := &http.Server{
        Addr:    ":8080",
        Handler: router,
    }

    // Start server in goroutine
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("Server error: %v", err)
        }
    }()

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("Shutting down server...")

    // Graceful shutdown with timeout
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }

    log.Println("Server exited properly")
}
```

---

## Configuration Management

### Environment Variables

```go
// Using Viper
func loadConfig() (*Config, error) {
    viper.SetEnvPrefix("APP")
    viper.AutomaticEnv()

    // Defaults
    viper.SetDefault("port", 8080)
    viper.SetDefault("db.max_open_conns", 25)
    viper.SetDefault("db.max_idle_conns", 5)

    // Required
    if !viper.IsSet("database_url") {
        return nil, errors.New("DATABASE_URL is required")
    }

    return &Config{
        Port:        viper.GetInt("port"),
        DatabaseURL: viper.GetString("database_url"),
        DBMaxOpen:   viper.GetInt("db.max_open_conns"),
        DBMaxIdle:   viper.GetInt("db.max_idle_conns"),
    }, nil
}
```

### Config File Support

```go
func loadConfigFile() error {
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")
    viper.AddConfigPath("/etc/myapp/")

    if err := viper.ReadInConfig(); err != nil {
        if _, ok := err.(viper.ConfigFileNotFoundError); ok {
            // Config file not found; use defaults/env vars
            return nil
        }
        return err
    }
    return nil
}
```

---

## Database Migrations

### golang-migrate

```bash
# Install
go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest

# Create migration
migrate create -ext sql -dir migrations -seq create_users_table

# Run migrations
migrate -path migrations -database "$DATABASE_URL" up

# Rollback
migrate -path migrations -database "$DATABASE_URL" down 1
```

### Migration Files

```sql
-- migrations/000001_create_users_table.up.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

```sql
-- migrations/000001_create_users_table.down.sql
DROP TABLE IF EXISTS users;
```

### Embed Migrations

```go
import (
    "embed"
    "github.com/golang-migrate/migrate/v4"
    "github.com/golang-migrate/migrate/v4/source/iofs"
)

//go:embed migrations/*.sql
var migrationsFS embed.FS

func runMigrations(dbURL string) error {
    d, err := iofs.New(migrationsFS, "migrations")
    if err != nil {
        return err
    }

    m, err := migrate.NewWithSourceInstance("iofs", d, dbURL)
    if err != nil {
        return err
    }

    if err := m.Up(); err != nil && err != migrate.ErrNoChange {
        return err
    }

    return nil
}
```

---

## Logging

### Structured Logging (slog)

```go
import "log/slog"

func setupLogger(env string) *slog.Logger {
    var handler slog.Handler

    if env == "production" {
        handler = slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelInfo,
        })
    } else {
        handler = slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelDebug,
        })
    }

    return slog.New(handler)
}

// Usage
logger.Info("server started",
    slog.String("addr", addr),
    slog.String("env", env),
)

logger.Error("database error",
    slog.String("operation", "insert"),
    slog.Any("error", err),
)
```

### Request Logging Middleware

```go
func LoggingMiddleware(logger *slog.Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path

        c.Next()

        logger.Info("request",
            slog.String("method", c.Request.Method),
            slog.String("path", path),
            slog.Int("status", c.Writer.Status()),
            slog.Duration("latency", time.Since(start)),
            slog.String("client_ip", c.ClientIP()),
        )
    }
}
```

---

## Metrics & Monitoring

### Prometheus Metrics

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )

    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "Duration of HTTP requests",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )
)

func MetricsMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        c.Next()

        duration := time.Since(start).Seconds()
        status := strconv.Itoa(c.Writer.Status())

        httpRequestsTotal.WithLabelValues(c.Request.Method, c.FullPath(), status).Inc()
        httpRequestDuration.WithLabelValues(c.Request.Method, c.FullPath()).Observe(duration)
    }
}

// Expose metrics endpoint
r.GET("/metrics", gin.WrapH(promhttp.Handler()))
```

---

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/go.yml
name: Go

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: "1.25"

      - name: Format check
        run: |
          go install mvdan.cc/gofumpt@latest
          if [ -n "$(gofumpt -d .)" ]; then
            echo "Code is not formatted"
            gofumpt -d .
            exit 1
          fi

      - name: Lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest
          args: --timeout=5m

      - name: Test
        run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Build
        run: go build -v ./...

  docker:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ secrets.REGISTRY }}/myapp:latest
```

### Bitbucket Pipelines

```yaml
# bitbucket-pipelines.yml
image: golang:1.25

definitions:
  steps:
    - step: &test
        name: Test
        caches:
          - go
        script:
          - go install mvdan.cc/gofumpt@latest
          - go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
          - gofumpt -d . | diff -q /dev/null - || (echo "Format check failed" && exit 1)
          - golangci-lint run --timeout 5m
          - go test -race -coverprofile=coverage.out ./...

    - step: &build
        name: Build
        caches:
          - go
          - docker
        script:
          - docker build -t $REGISTRY/myapp:$BITBUCKET_COMMIT .
          - docker push $REGISTRY/myapp:$BITBUCKET_COMMIT

pipelines:
  default:
    - step: *test

  branches:
    main:
      - step: *test
      - step: *build
```

---

## Production Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] golangci-lint clean
- [ ] gofumpt formatted
- [ ] Coverage ≥80%
- [ ] Migrations tested
- [ ] Health endpoints working

### Runtime

- [ ] Graceful shutdown implemented
- [ ] Structured logging configured
- [ ] Metrics exposed
- [ ] Resource limits set
- [ ] Secrets via environment variables

### Monitoring

- [ ] Health checks configured
- [ ] Prometheus metrics scraped
- [ ] Log aggregation setup
- [ ] Alerting rules defined

---

*Companion to: go-ironclad-stack.md*
*Last updated: 2026-01-15*

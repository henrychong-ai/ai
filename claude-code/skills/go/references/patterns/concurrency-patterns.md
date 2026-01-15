# Go Concurrency Patterns

Goroutines, channels, synchronization, and concurrent programming patterns.

---

## Core Principles

1. **Don't communicate by sharing memory; share memory by communicating**
2. **Goroutines are cheap** - Use them freely, but manage their lifecycle
3. **Channels orchestrate** - Use for communication and synchronization
4. **Context controls** - Always respect context cancellation

---

## Goroutines

### Basic Goroutine

```go
// Fire and forget (avoid in production)
go doWork()

// With synchronization
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    doWork()
}()
wg.Wait()
```

### Goroutine with Context

```go
func processInBackground(ctx context.Context) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                log.Println("Background process stopped")
                return
            default:
                doWork()
                time.Sleep(time.Second)
            }
        }
    }()
}
```

### Never Leak Goroutines

```go
// ❌ Bad: goroutine can leak
func process(ctx context.Context) {
    go func() {
        for {
            doWork() // Never exits
        }
    }()
}

// ✅ Good: goroutine respects context
func process(ctx context.Context) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return
            default:
                doWork()
            }
        }
    }()
}
```

---

## Channels

### Channel Types

```go
// Unbuffered: synchronous communication
ch := make(chan int)

// Buffered: async up to capacity
ch := make(chan int, 10)

// Directional (in function signatures)
func send(ch chan<- int) { ch <- 42 }     // Send-only
func recv(ch <-chan int) { x := <-ch }    // Receive-only
```

### Channel Patterns

#### Fan-Out (One to Many)

```go
func fanOut(input <-chan int, workers int) []<-chan int {
    outputs := make([]<-chan int, workers)

    for i := 0; i < workers; i++ {
        out := make(chan int)
        outputs[i] = out

        go func(in <-chan int, out chan<- int) {
            defer close(out)
            for v := range in {
                out <- process(v)
            }
        }(input, out)
    }

    return outputs
}
```

#### Fan-In (Many to One)

```go
func fanIn(inputs ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup

    for _, in := range inputs {
        wg.Add(1)
        go func(ch <-chan int) {
            defer wg.Done()
            for v := range ch {
                out <- v
            }
        }(in)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}
```

#### Pipeline

```go
func generator(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

func double(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * 2
        }
    }()
    return out
}

// Usage: pipeline
result := double(square(generator(1, 2, 3, 4)))
for v := range result {
    fmt.Println(v) // 2, 8, 18, 32
}
```

### Channel Closing Rules

```go
// ✅ Sender closes channel
func produce(ctx context.Context) <-chan int {
    ch := make(chan int)
    go func() {
        defer close(ch) // Sender closes
        for i := 0; ; i++ {
            select {
            case <-ctx.Done():
                return
            case ch <- i:
            }
        }
    }()
    return ch
}

// ❌ Never close from receiver
// ❌ Never close twice
// ❌ Never send on closed channel
```

---

## Select Statement

### Basic Select

```go
select {
case v := <-ch1:
    fmt.Println("received from ch1:", v)
case v := <-ch2:
    fmt.Println("received from ch2:", v)
case ch3 <- 42:
    fmt.Println("sent to ch3")
default:
    fmt.Println("no communication ready")
}
```

### Select with Timeout

```go
select {
case result := <-resultCh:
    return result, nil
case <-time.After(5 * time.Second):
    return nil, errors.New("timeout")
}
```

### Select with Context

```go
func doWork(ctx context.Context) error {
    resultCh := make(chan Result)

    go func() {
        resultCh <- expensiveOperation()
    }()

    select {
    case result := <-resultCh:
        return processResult(result)
    case <-ctx.Done():
        return ctx.Err()
    }
}
```

---

## Synchronization Primitives

### sync.WaitGroup

```go
func processAll(items []Item) {
    var wg sync.WaitGroup

    for _, item := range items {
        wg.Add(1)
        go func(it Item) {
            defer wg.Done()
            process(it)
        }(item)
    }

    wg.Wait()
}
```

### sync.Mutex

```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}
```

### sync.RWMutex

```go
type SafeMap struct {
    mu   sync.RWMutex
    data map[string]int
}

func (m *SafeMap) Get(key string) (int, bool) {
    m.mu.RLock()
    defer m.mu.RUnlock()
    v, ok := m.data[key]
    return v, ok
}

func (m *SafeMap) Set(key string, value int) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.data[key] = value
}
```

### sync.Once

```go
var (
    instance *Database
    once     sync.Once
)

func GetDatabase() *Database {
    once.Do(func() {
        instance = &Database{}
        instance.connect()
    })
    return instance
}
```

### sync.Pool

```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func process(data []byte) {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufferPool.Put(buf)
    }()

    buf.Write(data)
    // Use buffer...
}
```

---

## Worker Pool Pattern

### Fixed Worker Pool

```go
func WorkerPool(ctx context.Context, jobs <-chan Job, workers int) <-chan Result {
    results := make(chan Result)
    var wg sync.WaitGroup

    // Start workers
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for {
                select {
                case <-ctx.Done():
                    return
                case job, ok := <-jobs:
                    if !ok {
                        return
                    }
                    result := processJob(job)
                    select {
                    case results <- result:
                    case <-ctx.Done():
                        return
                    }
                }
            }
        }(i)
    }

    // Close results when all workers done
    go func() {
        wg.Wait()
        close(results)
    }()

    return results
}
```

### Semaphore-Based Concurrency Limit

```go
func ProcessWithLimit(items []Item, limit int) []Result {
    sem := make(chan struct{}, limit)
    results := make([]Result, len(items))
    var wg sync.WaitGroup

    for i, item := range items {
        wg.Add(1)
        go func(idx int, it Item) {
            defer wg.Done()

            sem <- struct{}{}        // Acquire
            defer func() { <-sem }() // Release

            results[idx] = process(it)
        }(i, item)
    }

    wg.Wait()
    return results
}
```

---

## Context Patterns

### Context Creation

```go
// With cancellation
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

// With timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// With deadline
deadline := time.Now().Add(30 * time.Second)
ctx, cancel := context.WithDeadline(context.Background(), deadline)
defer cancel()

// With values (use sparingly)
ctx = context.WithValue(ctx, userIDKey, userID)
```

### Context Propagation

```go
func (s *Service) ProcessOrder(ctx context.Context, orderID string) error {
    // Pass context to all downstream calls
    order, err := s.repo.GetOrder(ctx, orderID)
    if err != nil {
        return err
    }

    // Check cancellation before expensive operations
    if ctx.Err() != nil {
        return ctx.Err()
    }

    return s.fulfillment.Process(ctx, order)
}
```

### Context in HTTP Handlers

```go
func (h *Handler) GetUser(c *gin.Context) {
    ctx := c.Request.Context()

    user, err := h.service.GetUser(ctx, c.Param("id"))
    if err != nil {
        if errors.Is(err, context.Canceled) {
            return // Client disconnected
        }
        if errors.Is(err, context.DeadlineExceeded) {
            c.JSON(http.StatusGatewayTimeout, gin.H{"error": "request timeout"})
            return
        }
        // Handle other errors...
    }

    c.JSON(http.StatusOK, user)
}
```

---

## Error Group Pattern

```go
import "golang.org/x/sync/errgroup"

func ProcessAll(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)

    for _, item := range items {
        item := item // Capture
        g.Go(func() error {
            return processItem(ctx, item)
        })
    }

    return g.Wait() // Returns first error
}

// With concurrency limit
func ProcessAllWithLimit(ctx context.Context, items []Item, limit int) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(limit)

    for _, item := range items {
        item := item
        g.Go(func() error {
            return processItem(ctx, item)
        })
    }

    return g.Wait()
}
```

---

## Rate Limiting

### Token Bucket

```go
import "golang.org/x/time/rate"

// 10 requests per second, burst of 20
limiter := rate.NewLimiter(10, 20)

func processRequest(ctx context.Context) error {
    if err := limiter.Wait(ctx); err != nil {
        return err
    }
    return doWork()
}
```

### Per-Key Rate Limiting

```go
type RateLimiter struct {
    mu       sync.Mutex
    limiters map[string]*rate.Limiter
    rate     rate.Limit
    burst    int
}

func (r *RateLimiter) GetLimiter(key string) *rate.Limiter {
    r.mu.Lock()
    defer r.mu.Unlock()

    if limiter, exists := r.limiters[key]; exists {
        return limiter
    }

    limiter := rate.NewLimiter(r.rate, r.burst)
    r.limiters[key] = limiter
    return limiter
}
```

---

## Common Pitfalls

### Loop Variable Capture

```go
// ❌ Bad: all goroutines share same variable
for _, item := range items {
    go func() {
        process(item) // Bug: item is shared
    }()
}

// ✅ Good: capture in function parameter
for _, item := range items {
    go func(it Item) {
        process(it)
    }(item)
}

// ✅ Good (Go 1.22+): loop variables are per-iteration
for _, item := range items {
    go func() {
        process(item) // Safe in Go 1.22+
    }()
}
```

### Nil Channel Blocks Forever

```go
var ch chan int // nil channel

// These block forever:
ch <- 1    // Block
<-ch       // Block
close(ch)  // Panic!

// Use for disabling select cases
select {
case v := <-enabledCh:
    // Process
case v := <-disabledCh: // nil, so never selected
    // Never executes
}
```

### Race Conditions

```go
// ❌ Bad: race condition
var count int
go func() { count++ }()
go func() { count++ }()

// ✅ Good: use sync/atomic
var count int64
go func() { atomic.AddInt64(&count, 1) }()
go func() { atomic.AddInt64(&count, 1) }()
```

---

## Best Practices Summary

| Practice | Do | Don't |
|----------|-----|-------|
| **Goroutine lifecycle** | Use context for cancellation | Fire and forget |
| **Channel closing** | Sender closes | Receiver closes |
| **Select** | Always have timeout or context case | Block forever |
| **Mutex** | Use RWMutex for read-heavy workloads | Always use Mutex |
| **Context** | Pass as first parameter | Store in structs |
| **Error handling** | Use errgroup for concurrent errors | Ignore goroutine errors |

---

*Companion to: clean-code.md, api-patterns.md*
*Last updated: 2026-01-15*

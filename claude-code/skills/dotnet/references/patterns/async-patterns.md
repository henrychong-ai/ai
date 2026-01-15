# Async Patterns for .NET

async/await, ValueTask, IAsyncEnumerable, cancellation, and Polly resilience patterns.

---

## async/await Fundamentals

### Basic Pattern

```csharp
public async Task<User?> GetUserAsync(string id, CancellationToken ct = default)
{
    // Always propagate CancellationToken
    return await _repository.FindAsync(id, ct);
}

public async Task CreateUserAsync(User user, CancellationToken ct = default)
{
    await _repository.AddAsync(user, ct);
    await _unitOfWork.SaveChangesAsync(ct);
}
```

### Async All the Way

```csharp
// Good: Async all the way
public async Task<UserDto> GetUserDtoAsync(string id, CancellationToken ct)
{
    var user = await GetUserAsync(id, ct);
    return await MapToUserDtoAsync(user, ct);
}

// Bad: Blocking on async
public UserDto GetUserDtoBlocking(string id)
{
    var user = GetUserAsync(id).Result;  // NEVER DO THIS
    return MapToUserDto(user);
}

// Bad: Async void (except event handlers)
public async void ProcessOrder(Order order)  // NEVER DO THIS
{
    await _service.ProcessAsync(order);
}
```

### Return Task Directly When Possible

```csharp
// Simple delegation - return directly
public Task<User?> GetUserAsync(string id, CancellationToken ct)
    => _repository.FindAsync(id, ct);  // No async/await needed

// Use async when you need to do work after await
public async Task<User?> GetUserWithCachingAsync(string id, CancellationToken ct)
{
    var user = await _repository.FindAsync(id, ct);
    if (user is not null)
    {
        _cache.Set(id, user);  // Work after await
    }
    return user;
}
```

---

## ValueTask

### When to Use ValueTask

```csharp
// Use ValueTask when result is often synchronous (cached)
public ValueTask<User?> GetUserAsync(string id, CancellationToken ct)
{
    // Check cache first (synchronous)
    if (_cache.TryGet(id, out var user))
    {
        return ValueTask.FromResult<User?>(user);  // No allocation
    }

    // Fall back to async operation
    return new ValueTask<User?>(GetUserFromDbAsync(id, ct));
}

private async Task<User?> GetUserFromDbAsync(string id, CancellationToken ct)
{
    var user = await _repository.FindAsync(id, ct);
    if (user is not null)
    {
        _cache.Set(id, user);
    }
    return user;
}
```

### ValueTask Rules

```csharp
// 1. Never await ValueTask multiple times
var valueTask = GetUserAsync(id);
var user1 = await valueTask;
// var user2 = await valueTask;  // WRONG - undefined behavior

// 2. Never call GetAwaiter().GetResult() on incomplete ValueTask
var valueTask = GetUserAsync(id);
// var user = valueTask.GetAwaiter().GetResult();  // WRONG if not complete

// 3. Use AsTask() if you need to store or pass around
var valueTask = GetUserAsync(id);
var task = valueTask.AsTask();  // Now safe to use multiple times
```

---

## IAsyncEnumerable

### Streaming Data

```csharp
public async IAsyncEnumerable<User> GetAllUsersAsync(
    [EnumeratorCancellation] CancellationToken ct = default)
{
    var pageSize = 100;
    var page = 0;

    while (true)
    {
        var users = await _repository.GetPageAsync(page, pageSize, ct);
        if (!users.Any())
        {
            yield break;
        }

        foreach (var user in users)
        {
            ct.ThrowIfCancellationRequested();
            yield return user;
        }

        page++;
    }
}
```

### Consuming Async Streams

```csharp
// Basic consumption
await foreach (var user in GetAllUsersAsync(ct))
{
    await ProcessUserAsync(user, ct);
}

// With ConfigureAwait
await foreach (var user in GetAllUsersAsync(ct).ConfigureAwait(false))
{
    await ProcessUserAsync(user, ct);
}

// Collect to list
var users = new List<User>();
await foreach (var user in GetAllUsersAsync(ct))
{
    users.Add(user);
}

// Or use extension method
var users = await GetAllUsersAsync(ct).ToListAsync(ct);
```

### Async Stream Extensions

```csharp
public static class AsyncEnumerableExtensions
{
    public static async Task<List<T>> ToListAsync<T>(
        this IAsyncEnumerable<T> source,
        CancellationToken ct = default)
    {
        var list = new List<T>();
        await foreach (var item in source.WithCancellation(ct))
        {
            list.Add(item);
        }
        return list;
    }

    public static async IAsyncEnumerable<TResult> SelectAsync<T, TResult>(
        this IAsyncEnumerable<T> source,
        Func<T, Task<TResult>> selector,
        [EnumeratorCancellation] CancellationToken ct = default)
    {
        await foreach (var item in source.WithCancellation(ct))
        {
            yield return await selector(item);
        }
    }

    public static async IAsyncEnumerable<T> WhereAsync<T>(
        this IAsyncEnumerable<T> source,
        Func<T, bool> predicate,
        [EnumeratorCancellation] CancellationToken ct = default)
    {
        await foreach (var item in source.WithCancellation(ct))
        {
            if (predicate(item))
            {
                yield return item;
            }
        }
    }
}
```

---

## Cancellation

### CancellationToken Propagation

```csharp
public class OrderService
{
    public async Task ProcessOrderAsync(string orderId, CancellationToken ct = default)
    {
        // Always pass ct to async methods
        var order = await _repository.GetByIdAsync(orderId, ct);

        // Check cancellation before expensive operations
        ct.ThrowIfCancellationRequested();

        await ProcessPaymentAsync(order, ct);

        // Use ct in loops
        foreach (var item in order.Items)
        {
            ct.ThrowIfCancellationRequested();
            await ProcessItemAsync(item, ct);
        }
    }
}
```

### Creating Cancellation Tokens

```csharp
// From CancellationTokenSource
using var cts = new CancellationTokenSource();
cts.CancelAfter(TimeSpan.FromSeconds(30));  // Timeout
var result = await ProcessAsync(cts.Token);

// Linked tokens
using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(
    httpContext.RequestAborted,
    applicationShutdown);

// Register callback
ct.Register(() => CleanupResources());
```

### Graceful Cancellation

```csharp
public async Task<Result<Order>> ProcessWithTimeoutAsync(
    string orderId,
    TimeSpan timeout,
    CancellationToken externalCt = default)
{
    using var timeoutCts = new CancellationTokenSource(timeout);
    using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(
        externalCt,
        timeoutCts.Token);

    try
    {
        var order = await ProcessOrderAsync(orderId, linkedCts.Token);
        return Result.Ok(order);
    }
    catch (OperationCanceledException) when (timeoutCts.IsCancellationRequested)
    {
        return Result.Fail<Order>("Operation timed out", "TIMEOUT");
    }
    catch (OperationCanceledException)
    {
        return Result.Fail<Order>("Operation was cancelled", "CANCELLED");
    }
}
```

---

## Parallel Operations

### Task.WhenAll

```csharp
// Execute independent tasks in parallel
public async Task<OrderSummary> GetOrderSummaryAsync(string orderId, CancellationToken ct)
{
    var orderTask = _orderRepository.GetByIdAsync(orderId, ct);
    var customerTask = _customerRepository.GetByOrderIdAsync(orderId, ct);
    var itemsTask = _itemRepository.GetByOrderIdAsync(orderId, ct);

    await Task.WhenAll(orderTask, customerTask, itemsTask);

    return new OrderSummary(
        orderTask.Result,
        customerTask.Result,
        itemsTask.Result);
}

// With error handling
public async Task<(List<T> Results, List<Exception> Errors)> ProcessAllAsync<T>(
    IEnumerable<Func<CancellationToken, Task<T>>> operations,
    CancellationToken ct)
{
    var tasks = operations.Select(op => op(ct)).ToList();

    try
    {
        var results = await Task.WhenAll(tasks);
        return (results.ToList(), new List<Exception>());
    }
    catch
    {
        var results = new List<T>();
        var errors = new List<Exception>();

        foreach (var task in tasks)
        {
            if (task.IsCompletedSuccessfully)
            {
                results.Add(task.Result);
            }
            else if (task.IsFaulted)
            {
                errors.Add(task.Exception!.InnerException!);
            }
        }

        return (results, errors);
    }
}
```

### Parallel.ForEachAsync

```csharp
// Process items in parallel with degree of parallelism
public async Task ProcessUsersAsync(
    IEnumerable<User> users,
    CancellationToken ct)
{
    var options = new ParallelOptions
    {
        MaxDegreeOfParallelism = 4,
        CancellationToken = ct
    };

    await Parallel.ForEachAsync(users, options, async (user, token) =>
    {
        await ProcessUserAsync(user, token);
    });
}
```

### SemaphoreSlim for Throttling

```csharp
public class ThrottledProcessor
{
    private readonly SemaphoreSlim _semaphore;

    public ThrottledProcessor(int maxConcurrency)
    {
        _semaphore = new SemaphoreSlim(maxConcurrency);
    }

    public async Task<List<TResult>> ProcessAllAsync<T, TResult>(
        IEnumerable<T> items,
        Func<T, CancellationToken, Task<TResult>> processor,
        CancellationToken ct)
    {
        var tasks = items.Select(async item =>
        {
            await _semaphore.WaitAsync(ct);
            try
            {
                return await processor(item, ct);
            }
            finally
            {
                _semaphore.Release();
            }
        });

        return (await Task.WhenAll(tasks)).ToList();
    }
}
```

---

## Polly Resilience

### Retry Pattern

```csharp
// Simple retry
var retryPolicy = Policy
    .Handle<HttpRequestException>()
    .WaitAndRetryAsync(3, attempt =>
        TimeSpan.FromSeconds(Math.Pow(2, attempt)));

var result = await retryPolicy.ExecuteAsync(async ct =>
    await _httpClient.GetAsync(url, ct), cancellationToken);

// With jitter
var retryWithJitter = Policy
    .Handle<HttpRequestException>()
    .WaitAndRetryAsync(3, attempt =>
        TimeSpan.FromSeconds(Math.Pow(2, attempt)) +
        TimeSpan.FromMilliseconds(Random.Shared.Next(0, 1000)));
```

### Circuit Breaker

```csharp
var circuitBreaker = Policy
    .Handle<HttpRequestException>()
    .CircuitBreakerAsync(
        exceptionsAllowedBeforeBreaking: 5,
        durationOfBreak: TimeSpan.FromSeconds(30),
        onBreak: (ex, duration) =>
            _logger.LogWarning("Circuit opened for {Duration}", duration),
        onReset: () =>
            _logger.LogInformation("Circuit closed"),
        onHalfOpen: () =>
            _logger.LogInformation("Circuit half-open"));
```

### Timeout

```csharp
var timeoutPolicy = Policy.TimeoutAsync<HttpResponseMessage>(
    TimeSpan.FromSeconds(10),
    TimeoutStrategy.Optimistic,
    onTimeoutAsync: (context, timeout, task) =>
    {
        _logger.LogWarning("Timeout after {Timeout}", timeout);
        return Task.CompletedTask;
    });
```

### Policy Combination

```csharp
// HttpClientFactory with Polly
builder.Services
    .AddHttpClient<IExternalService, ExternalService>()
    .AddPolicyHandler(GetRetryPolicy())
    .AddPolicyHandler(GetCircuitBreakerPolicy())
    .AddPolicyHandler(Policy.TimeoutAsync<HttpResponseMessage>(10));

static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .WaitAndRetryAsync(3, retryAttempt =>
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
}

static IAsyncPolicy<HttpResponseMessage> GetCircuitBreakerPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .CircuitBreakerAsync(5, TimeSpan.FromSeconds(30));
}
```

---

## ConfigureAwait

### Library Code

```csharp
// In library code, use ConfigureAwait(false) to avoid deadlocks
public async Task<Data> GetDataAsync(CancellationToken ct)
{
    var response = await _httpClient.GetAsync(url, ct).ConfigureAwait(false);
    var content = await response.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
    return JsonSerializer.Deserialize<Data>(content)!;
}
```

### Application Code

```csharp
// In ASP.NET Core, ConfigureAwait(false) is not needed but doesn't hurt
// In WPF/WinForms/MAUI, be careful - may need context for UI updates

// Generally recommended in application code for consistency
public async Task ProcessAsync(CancellationToken ct)
{
    await _service.DoWorkAsync(ct).ConfigureAwait(false);
}
```

---

## Summary

### Best Practices

1. **Always propagate CancellationToken**
2. **Use async/await all the way (no blocking)**
3. **Return Task directly when no work after await**
4. **Use ValueTask for high-performance hot paths**
5. **Use IAsyncEnumerable for streaming**
6. **Use Polly for resilience patterns**
7. **Use ConfigureAwait(false) in libraries**

### Common Patterns

| Pattern | Use Case |
|---------|----------|
| `Task.WhenAll` | Parallel independent operations |
| `Parallel.ForEachAsync` | Throttled parallel processing |
| `SemaphoreSlim` | Custom concurrency control |
| `IAsyncEnumerable` | Streaming large datasets |
| Polly Retry | Transient failure handling |
| Polly Circuit Breaker | Fail fast when service is down |

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| `.Result` / `.Wait()` | Deadlock risk | Use `await` |
| `async void` | Unhandled exceptions | Return `Task` |
| Fire and forget | Lost exceptions | Track or handle |
| Missing cancellation | Cannot cancel | Pass `CancellationToken` |

---

*Last updated: 2026-01-15*

# C# Type Patterns

Advanced type patterns including records, generics, nullable reference types, and composition patterns.

---

## Records

### Positional Records (Recommended for DTOs)

```csharp
// Concise syntax for immutable data
public record UserDto(string Id, string Name, string Email);
public record CreateUserRequest(string Name, string Email);
public record OrderLineItem(string ProductId, int Quantity, decimal UnitPrice);

// Usage
var user = new UserDto("123", "Alice", "alice@example.com");
var updated = user with { Name = "Alice Smith" };  // Non-destructive mutation
```

### Record Classes with Additional Members

```csharp
public record User(string Id, string Name, string Email)
{
    // Computed property
    public string DisplayName => $"{Name} <{Email}>";

    // Validation in constructor
    public User
    {
        if (string.IsNullOrWhiteSpace(Name))
            throw new ArgumentException("Name cannot be empty", nameof(Name));

        if (string.IsNullOrWhiteSpace(Email))
            throw new ArgumentException("Email cannot be empty", nameof(Email));
    }

    // Additional methods
    public bool IsValidEmail() => Email.Contains('@');
}
```

### Record Structs (Value Type Records)

```csharp
// Stack-allocated, no heap allocation
public readonly record struct Point(int X, int Y);
public readonly record struct Money(decimal Amount, string Currency);

// Mutable record struct (avoid unless necessary)
public record struct Counter(int Value)
{
    public void Increment() => Value++;
}
```

### When to Use Records

| Scenario | Use Record? | Example |
|----------|-------------|---------|
| DTOs | Yes | `UserDto`, `CreateUserRequest` |
| Domain events | Yes | `UserCreatedEvent` |
| Value objects | Yes | `Address`, `Money` |
| Entities with identity | No (use class) | `User`, `Order` |
| Services | No (use class) | `UserService` |

---

## Nullable Reference Types

### Enable Globally

```xml
<!-- Directory.Build.props -->
<PropertyGroup>
    <Nullable>enable</Nullable>
</PropertyGroup>
```

### Nullable Annotations

```csharp
public class UserService
{
    // Non-nullable - guaranteed to have value
    private readonly IUserRepository _repository;

    // Nullable return - might be null
    public async Task<User?> GetByIdAsync(string id)
    {
        return await _repository.FindAsync(id);
    }

    // Nullable parameter - caller can pass null
    public void SetEmail(string? email)
    {
        if (email is not null)
        {
            // email is definitely not null here
        }
    }

    // Non-nullable with default
    public void ProcessUsers(IEnumerable<User> users = null!)
    {
        users ??= Enumerable.Empty<User>();
    }
}
```

### Null Guards

```csharp
// .NET 6+ ArgumentNullException helpers
public void ProcessUser(User user)
{
    ArgumentNullException.ThrowIfNull(user);
    // user is guaranteed non-null here
}

public void SetName(string name)
{
    ArgumentException.ThrowIfNullOrWhiteSpace(name);
    // name is guaranteed non-null and non-empty
}

// Pattern matching null check
if (user is not null)
{
    Console.WriteLine(user.Name);
}

// Null-conditional and null-coalescing
var name = user?.Name ?? "Unknown";
var email = user?.Email ?? throw new InvalidOperationException("Email required");
```

### Nullable Attributes

```csharp
using System.Diagnostics.CodeAnalysis;

public class Repository
{
    // Return value is not null if method returns true
    public bool TryGetUser(string id, [NotNullWhen(true)] out User? user)
    {
        user = _cache.Get(id);
        return user is not null;
    }

    // Parameter is null when method returns
    public void DisposeUser([DisallowNull] ref User? user)
    {
        user?.Dispose();
        user = null;
    }

    // Return value may be null even if input is not null
    [return: MaybeNull]
    public T Find<T>(string id) where T : class
    {
        return _store.Get<T>(id);
    }
}
```

---

## Generics

### Generic Constraints

```csharp
// Class constraint (reference type)
public class Repository<T> where T : class
{
    public T? Find(string id) => default;
}

// Struct constraint (value type)
public class ValueStore<T> where T : struct
{
    public T GetOrDefault(string key) => default;
}

// Interface constraint
public class Service<T> where T : IEntity
{
    public string GetId(T entity) => entity.Id;
}

// new() constraint (parameterless constructor)
public T CreateInstance<T>() where T : new()
{
    return new T();
}

// Multiple constraints
public class Handler<TRequest, TResponse>
    where TRequest : class, IRequest<TResponse>
    where TResponse : class, new()
{
    public TResponse Handle(TRequest request) => new();
}

// notnull constraint
public class Cache<TKey, TValue>
    where TKey : notnull
    where TValue : class
{
    private readonly Dictionary<TKey, TValue> _items = new();
}
```

### Generic Variance

```csharp
// Covariance (out) - can return more derived types
public interface IRepository<out T>
{
    T Get(string id);
    IEnumerable<T> GetAll();
}

// Contravariance (in) - can accept more derived types
public interface IHandler<in T>
{
    void Handle(T item);
}

// Usage
IRepository<Animal> animals = new Repository<Dog>();  // Covariance
IHandler<Dog> dogHandler = new Handler<Animal>();     // Contravariance
```

### Common Generic Patterns

```csharp
// Result type
public abstract record Result<T>
{
    public record Success(T Value) : Result<T>;
    public record Failure(string Error) : Result<T>;

    public bool IsSuccess => this is Success;
    public bool IsFailure => this is Failure;

    public TResult Match<TResult>(
        Func<T, TResult> onSuccess,
        Func<string, TResult> onFailure) => this switch
    {
        Success s => onSuccess(s.Value),
        Failure f => onFailure(f.Error),
        _ => throw new InvalidOperationException()
    };
}

// Option type
public abstract record Option<T>
{
    public record Some(T Value) : Option<T>;
    public record None : Option<T>;

    public T GetValueOrDefault(T defaultValue) => this switch
    {
        Some s => s.Value,
        _ => defaultValue
    };
}
```

---

## Interface Design

### Accept Interfaces, Return Concrete Types

```csharp
// Good: Accept interface
public void ProcessUsers(IEnumerable<User> users) { }
public void SaveUser(IUser user) { }

// Good: Return concrete type
public List<User> GetActiveUsers() { }
public UserDto GetUserById(string id) { }

// Avoid: Returning interface hides implementation
public IEnumerable<User> GetUsers() { }  // Caller doesn't know it's a List
```

### Interface Segregation

```csharp
// Bad: Fat interface
public interface IUserRepository
{
    Task<User?> GetByIdAsync(string id);
    Task<IEnumerable<User>> GetAllAsync();
    Task CreateAsync(User user);
    Task UpdateAsync(User user);
    Task DeleteAsync(string id);
    Task<int> GetCountAsync();
    Task<bool> ExistsAsync(string id);
    Task ImportUsersAsync(IEnumerable<User> users);
    Task ExportUsersAsync(Stream stream);
}

// Good: Segregated interfaces
public interface IUserReader
{
    Task<User?> GetByIdAsync(string id, CancellationToken ct = default);
    Task<IEnumerable<User>> GetAllAsync(CancellationToken ct = default);
}

public interface IUserWriter
{
    Task CreateAsync(User user, CancellationToken ct = default);
    Task UpdateAsync(User user, CancellationToken ct = default);
    Task DeleteAsync(string id, CancellationToken ct = default);
}

public interface IUserRepository : IUserReader, IUserWriter { }
```

### Default Interface Implementations

```csharp
public interface ILogger
{
    void Log(LogLevel level, string message);

    // Default implementation
    void LogInformation(string message) => Log(LogLevel.Information, message);
    void LogWarning(string message) => Log(LogLevel.Warning, message);
    void LogError(string message) => Log(LogLevel.Error, message);
}
```

---

## Pattern Matching

### Type Patterns

```csharp
// is pattern
if (response is OkObjectResult { Value: User user })
{
    Console.WriteLine(user.Name);
}

// switch expression with type patterns
string Describe(object obj) => obj switch
{
    null => "null",
    string s => $"String: {s}",
    int i => $"Integer: {i}",
    User u => $"User: {u.Name}",
    _ => $"Unknown: {obj.GetType().Name}"
};
```

### Property Patterns

```csharp
// Single property
if (user is { IsActive: true })
{
    SendWelcomeEmail(user);
}

// Multiple properties
if (order is { Status: OrderStatus.Pending, Total: > 1000 })
{
    RequireApproval(order);
}

// Nested property patterns
if (order is { Customer: { Country: "US" }, Items: { Count: > 0 } })
{
    CalculateShipping(order);
}

// Relational patterns
decimal GetDiscount(Order order) => order.Total switch
{
    < 100 => 0,
    >= 100 and < 500 => 0.05m,
    >= 500 and < 1000 => 0.10m,
    >= 1000 => 0.15m
};
```

### List Patterns (.NET 8+)

```csharp
// Empty list
if (items is [])
{
    return "No items";
}

// Single item
if (items is [var single])
{
    return $"Single item: {single}";
}

// First and rest
if (items is [var first, .. var rest])
{
    Process(first);
    foreach (var item in rest) { }
}

// Specific positions
if (items is [var first, _, _, var last])
{
    return $"First: {first}, Last: {last}";
}

// Slice patterns
string Analyze(int[] numbers) => numbers switch
{
    [] => "Empty",
    [var x] => $"Single: {x}",
    [var x, var y] => $"Pair: {x}, {y}",
    [var first, .., var last] => $"Range: {first} to {last}",
};
```

---

## Extension Methods

### Creating Extensions

```csharp
public static class StringExtensions
{
    public static bool IsNullOrEmpty(this string? value)
        => string.IsNullOrEmpty(value);

    public static string ToTitleCase(this string value)
        => CultureInfo.CurrentCulture.TextInfo.ToTitleCase(value.ToLower());

    public static T? ParseAs<T>(this string value) where T : struct
        => Enum.TryParse<T>(value, out var result) ? result : null;
}

public static class EnumerableExtensions
{
    public static IEnumerable<T> WhereNotNull<T>(this IEnumerable<T?> source)
        where T : class
        => source.Where(x => x is not null)!;

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
}
```

### Fluent API Pattern

```csharp
public class QueryBuilder<T>
{
    private readonly List<Func<T, bool>> _filters = new();
    private Func<T, object>? _orderBy;
    private int? _take;

    public QueryBuilder<T> Where(Func<T, bool> predicate)
    {
        _filters.Add(predicate);
        return this;
    }

    public QueryBuilder<T> OrderBy(Func<T, object> keySelector)
    {
        _orderBy = keySelector;
        return this;
    }

    public QueryBuilder<T> Take(int count)
    {
        _take = count;
        return this;
    }

    public IEnumerable<T> Execute(IEnumerable<T> source)
    {
        var query = source.AsEnumerable();

        foreach (var filter in _filters)
        {
            query = query.Where(filter);
        }

        if (_orderBy is not null)
        {
            query = query.OrderBy(_orderBy);
        }

        if (_take.HasValue)
        {
            query = query.Take(_take.Value);
        }

        return query;
    }
}
```

---

## Summary

### Record Patterns

| Type | Allocation | Mutability | Use Case |
|------|------------|------------|----------|
| `record class` | Heap | Immutable | DTOs, events, value objects |
| `record struct` | Stack | Immutable | Small value types |
| `class` | Heap | Mutable | Entities, services |
| `struct` | Stack | Mutable | Performance-critical values |

### Nullable Best Practices

1. Enable `<Nullable>enable</Nullable>` globally
2. Use `ArgumentNullException.ThrowIfNull()` for guards
3. Use nullable attributes for complex nullability
4. Prefer `is not null` over `!= null`
5. Use `??` and `??=` operators

### Generic Constraints

| Constraint | Meaning |
|------------|---------|
| `where T : class` | Reference type |
| `where T : struct` | Value type |
| `where T : new()` | Has parameterless constructor |
| `where T : notnull` | Non-nullable |
| `where T : IInterface` | Implements interface |
| `where T : BaseClass` | Derives from class |

---

*Last updated: 2026-01-15*

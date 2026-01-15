# Claude Code Rules for C#

C# conventions and patterns optimized for Claude Code AI-assisted development.

---

## Type Safety First

### Always Use Nullable Reference Types

```csharp
// Enable in project
<Nullable>enable</Nullable>

// Use nullable annotations correctly
public async Task<User?> FindAsync(string id)  // May return null
public async Task<User> GetByIdAsync(string id)  // Never returns null, throws if not found

// Handle nullability
var user = await _repository.FindAsync(id);
if (user is null)
{
    return NotFound();
}
// user is guaranteed non-null here
```

### Use Strong Types Over Primitives

```csharp
// Bad: Primitive obsession
public void CreateUser(string id, string email, string name) { }

// Good: Strong types
public void CreateUser(UserId id, Email email, UserName name) { }

// Value objects
public record UserId(string Value)
{
    public static UserId New() => new(Guid.NewGuid().ToString());
}

public record Email(string Value)
{
    public Email
    {
        if (!Value.Contains('@'))
            throw new ArgumentException("Invalid email format");
    }
}
```

### Prefer Records for Data

```csharp
// DTOs should be records
public record CreateUserRequest(string Name, string Email);
public record UserDto(string Id, string Name, string Email);

// Domain events should be records
public record UserCreatedEvent(string UserId, DateTime Timestamp);

// Result types should be records
public abstract record Result<T>
{
    public record Success(T Value) : Result<T>;
    public record Failure(string Error) : Result<T>;
}
```

---

## Error Handling

### Use Result Pattern for Expected Failures

```csharp
// Good: Result pattern for expected failures
public async Task<Result<User>> CreateUserAsync(CreateUserRequest request)
{
    if (await _repository.ExistsAsync(request.Email))
    {
        return Result.Fail<User>("Email already exists");
    }

    var user = new User { Email = request.Email };
    await _repository.AddAsync(user);
    return Result.Ok(user);
}

// Bad: Exceptions for control flow
public async Task<User> CreateUserAsync(CreateUserRequest request)
{
    if (await _repository.ExistsAsync(request.Email))
    {
        throw new DuplicateEmailException(request.Email);  // Don't do this
    }
    // ...
}
```

### Throw Exceptions for Exceptional Cases

```csharp
// Programming errors - throw immediately
public void SetName(string name)
{
    ArgumentException.ThrowIfNullOrWhiteSpace(name);
    _name = name;
}

// Exceptional situations - throw
public async Task<User> GetRequiredUserAsync(string id)
{
    var user = await _repository.FindAsync(id);
    return user ?? throw new UserNotFoundException(id);
}
```

---

## Async Patterns

### Always Pass CancellationToken

```csharp
// Good: Propagate cancellation token
public async Task<User?> GetUserAsync(string id, CancellationToken ct = default)
{
    ct.ThrowIfCancellationRequested();
    return await _repository.FindAsync(id, ct);
}

// Bad: Ignore cancellation
public async Task<User?> GetUserAsync(string id)
{
    return await _repository.FindAsync(id);  // Can't be cancelled
}
```

### Use ConfigureAwait(false) in Libraries

```csharp
// In library code
public async Task<Data> GetDataAsync(CancellationToken ct)
{
    var response = await _client.GetAsync(url, ct).ConfigureAwait(false);
    var content = await response.Content.ReadAsStringAsync(ct).ConfigureAwait(false);
    return JsonSerializer.Deserialize<Data>(content)!;
}
```

---

## API Patterns

### Use Minimal APIs with Typed Results

```csharp
// Good: TypedResults for documentation
app.MapGet("/users/{id}", async Task<Results<Ok<UserDto>, NotFound>> (
    string id,
    IUserService service,
    CancellationToken ct) =>
{
    var user = await service.GetByIdAsync(id, ct);
    return user is not null
        ? TypedResults.Ok(user)
        : TypedResults.NotFound();
});
```

### Organize Endpoints in Extension Methods

```csharp
// UserEndpoints.cs
public static class UserEndpoints
{
    public static RouteGroupBuilder MapUserEndpoints(this RouteGroupBuilder group)
    {
        var users = group.MapGroup("/users");
        users.MapGet("/{id}", GetUserById);
        users.MapPost("/", CreateUser);
        return group;
    }

    private static async Task<IResult> GetUserById(
        string id,
        IUserService service,
        CancellationToken ct)
    {
        var user = await service.GetByIdAsync(id, ct);
        return user is not null ? Results.Ok(user) : Results.NotFound();
    }
}
```

---

## Dependency Injection

### Use Constructor Injection

```csharp
// Good: Constructor injection
public class UserService : IUserService
{
    private readonly IUserRepository _repository;
    private readonly ILogger<UserService> _logger;

    public UserService(IUserRepository repository, ILogger<UserService> logger)
    {
        _repository = repository;
        _logger = logger;
    }
}

// Bad: Service locator
public class UserService
{
    public void DoWork()
    {
        var repository = ServiceLocator.Get<IUserRepository>();  // Don't do this
    }
}
```

### Use Options Pattern for Configuration

```csharp
// Good: Options pattern
public class UserServiceOptions
{
    public int MaxRetries { get; init; } = 3;
    public TimeSpan Timeout { get; init; } = TimeSpan.FromSeconds(30);
}

public class UserService
{
    private readonly UserServiceOptions _options;

    public UserService(IOptions<UserServiceOptions> options)
    {
        _options = options.Value;
    }
}

// Bad: Static configuration
public class UserService
{
    private static readonly int MaxRetries = 3;  // Can't configure
}
```

---

## File Editing Rules

### Safe Editing Patterns

When Claude Code edits C# files:

1. **Never break compilation**
   - Ensure all using statements present
   - Ensure all type references resolved
   - Verify namespace matches folder structure

2. **Preserve existing patterns**
   - Match existing code style
   - Follow established naming conventions
   - Use same error handling approach

3. **Update tests alongside code**
   - Modify corresponding test file
   - Add tests for new functionality
   - Update existing tests if behavior changed

### Code Generation Guidelines

```csharp
// When generating new classes, include:
// 1. File-scoped namespace
namespace MyProject.Services;

// 2. Required using statements
using Microsoft.Extensions.Logging;

// 3. Proper dependency injection
public class UserService : IUserService
{
    private readonly IUserRepository _repository;
    private readonly ILogger<UserService> _logger;

    public UserService(IUserRepository repository, ILogger<UserService> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    // 4. Async methods with CancellationToken
    public async Task<User?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        _logger.LogInformation("Getting user {UserId}", id);
        return await _repository.FindAsync(id, ct);
    }
}
```

---

## Testing Integration

### Generate Tests with Code

When generating new functionality, always include tests:

```csharp
// Generated code: UserService.cs
public class UserService
{
    public async Task<User> CreateAsync(CreateUserRequest request, CancellationToken ct)
    {
        var user = new User { Name = request.Name, Email = request.Email };
        await _repository.AddAsync(user, ct);
        return user;
    }
}

// Generated test: UserServiceTests.cs
public class UserServiceTests
{
    [Fact]
    public async Task CreateAsync_WithValidRequest_ReturnsUser()
    {
        // Arrange
        var request = new CreateUserRequest("Alice", "alice@test.com");

        // Act
        var result = await _sut.CreateAsync(request, CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result.Name.Should().Be("Alice");
    }
}
```

---

## Common Patterns

### Repository Pattern

```csharp
public interface IRepository<T> where T : class
{
    Task<T?> FindAsync(string id, CancellationToken ct = default);
    Task<IEnumerable<T>> GetAllAsync(CancellationToken ct = default);
    Task AddAsync(T entity, CancellationToken ct = default);
    Task UpdateAsync(T entity, CancellationToken ct = default);
    Task DeleteAsync(string id, CancellationToken ct = default);
}
```

### Service Pattern

```csharp
public interface IUserService
{
    Task<UserDto?> GetByIdAsync(string id, CancellationToken ct = default);
    Task<Result<UserDto>> CreateAsync(CreateUserRequest request, CancellationToken ct = default);
    Task<Result<UserDto>> UpdateAsync(string id, UpdateUserRequest request, CancellationToken ct = default);
    Task<bool> DeleteAsync(string id, CancellationToken ct = default);
}
```

### Validation Pattern

```csharp
public class CreateUserValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserValidator()
    {
        RuleFor(x => x.Name).NotEmpty().MaximumLength(100);
        RuleFor(x => x.Email).NotEmpty().EmailAddress();
    }
}
```

---

## Summary

### Do

- Enable nullable reference types
- Use records for immutable data
- Use Result pattern for expected failures
- Pass CancellationToken to async methods
- Use constructor injection
- Generate tests with code
- Follow existing code patterns

### Don't

- Use exceptions for control flow
- Ignore cancellation tokens
- Use static state
- Use service locator
- Generate code without tests
- Break existing code style

---

*Last updated: 2026-01-15*

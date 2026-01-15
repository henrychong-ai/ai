# C# Style Guide

Naming conventions, formatting rules, and organization patterns following Microsoft conventions optimized for Claude Code development.

---

## Naming Conventions

### PascalCase

Use for: Types, methods, properties, events, namespaces, public fields.

```csharp
// Types
public class UserService { }
public interface IUserRepository { }
public record UserDto(string Id, string Name);
public enum OrderStatus { Pending, Shipped, Delivered }

// Methods
public async Task<User> GetUserByIdAsync(string id) { }
public void ProcessOrder(Order order) { }

// Properties
public string FirstName { get; set; }
public DateTime CreatedAt { get; init; }

// Events
public event EventHandler<UserCreatedEventArgs> UserCreated;

// Namespaces
namespace MyCompany.MyProduct.Users { }
```

### camelCase

Use for: Parameters, local variables, private fields (with underscore prefix).

```csharp
// Parameters
public void SendEmail(string recipientEmail, string subject) { }

// Local variables
var userCount = await GetUserCountAsync();
var isValid = ValidateInput(input);

// Private fields (with underscore prefix)
private readonly IUserRepository _userRepository;
private readonly ILogger<UserService> _logger;
private int _retryCount;
```

### Interface Prefix

Always prefix interfaces with `I`.

```csharp
// Correct
public interface IUserRepository { }
public interface IEmailService { }
public interface IAsyncDisposable { }

// Incorrect
public interface UserRepository { }  // Missing I prefix
public interface EmailServiceInterface { }  // Redundant suffix
```

### Async Suffix

Always suffix async methods with `Async`.

```csharp
// Correct
public async Task<User> GetUserAsync(string id) { }
public async Task SendEmailAsync(string to, string subject) { }
public async IAsyncEnumerable<Order> StreamOrdersAsync() { }

// Incorrect
public async Task<User> GetUser(string id) { }  // Missing Async suffix
public Task<User> GetUserAsync(string id) { }   // Not async but has suffix - OK if returns Task
```

### Type Suffixes

Use meaningful suffixes for common patterns:

| Suffix | Use For | Example |
|--------|---------|---------|
| `Service` | Business logic classes | `UserService`, `OrderService` |
| `Repository` | Data access classes | `UserRepository`, `OrderRepository` |
| `Controller` | MVC controllers | `UsersController` |
| `Handler` | Command/Event handlers | `CreateUserHandler` |
| `Validator` | FluentValidation classes | `CreateUserValidator` |
| `Options` | Configuration classes | `DatabaseOptions`, `JwtOptions` |
| `Exception` | Custom exceptions | `UserNotFoundException` |
| `Extensions` | Extension method classes | `StringExtensions` |

---

## Code Organization

### File Structure

One type per file (with exceptions for closely related types).

```csharp
// User.cs - Main entity
public class User
{
    public string Id { get; init; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
}

// UserDto.cs - Separate file for DTO
public record UserDto(string Id, string Name, string Email);

// Exception: Closely related types can share a file
// UserEvents.cs
public record UserCreatedEvent(string UserId, DateTime CreatedAt);
public record UserUpdatedEvent(string UserId, DateTime UpdatedAt);
public record UserDeletedEvent(string UserId, DateTime DeletedAt);
```

### Class Member Order

```csharp
public class UserService : IUserService
{
    // 1. Constants
    private const int MaxRetries = 3;

    // 2. Static fields
    private static readonly TimeSpan DefaultTimeout = TimeSpan.FromSeconds(30);

    // 3. Instance fields
    private readonly IUserRepository _userRepository;
    private readonly ILogger<UserService> _logger;

    // 4. Constructors
    public UserService(IUserRepository userRepository, ILogger<UserService> logger)
    {
        _userRepository = userRepository;
        _logger = logger;
    }

    // 5. Properties
    public int RetryCount { get; private set; }

    // 6. Public methods
    public async Task<User?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        return await _userRepository.GetByIdAsync(id, ct);
    }

    // 7. Private methods
    private void ValidateId(string id)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);
    }
}
```

### Using Directives Order

```csharp
// 1. System namespaces
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

// 2. Microsoft namespaces
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;

// 3. Third-party namespaces
using FluentValidation;
using Polly;

// 4. Project namespaces
using MyProject.Domain;
using MyProject.Infrastructure;
```

---

## Formatting

### Braces

Always use braces, even for single-line statements.

```csharp
// Correct
if (user is null)
{
    return NotFound();
}

foreach (var item in items)
{
    ProcessItem(item);
}

// Incorrect
if (user is null)
    return NotFound();  // Missing braces

foreach (var item in items)
    ProcessItem(item);  // Missing braces
```

### Line Length

Maximum 120 characters. Break long lines logically.

```csharp
// Break at method parameters
public async Task<Result<UserDto>> CreateUserAsync(
    CreateUserRequest request,
    CancellationToken cancellationToken = default)
{
    // Implementation
}

// Break at LINQ operators
var activeUsers = users
    .Where(u => u.IsActive)
    .OrderBy(u => u.Name)
    .Select(u => new UserDto(u.Id, u.Name, u.Email))
    .ToList();

// Break at fluent builders
services
    .AddHttpClient<IExternalService, ExternalService>()
    .AddPolicyHandler(GetRetryPolicy())
    .AddPolicyHandler(GetCircuitBreakerPolicy());
```

### Spacing

```csharp
// Space after keywords
if (condition) { }
for (var i = 0; i < 10; i++) { }
while (running) { }

// Space around operators
var sum = a + b;
var isEqual = x == y;
var combined = first ?? second;

// No space before parentheses in method calls
DoSomething();
GetUser(id);

// Space after commas
var tuple = (first, second, third);
CallMethod(arg1, arg2, arg3);
```

---

## Type Declarations

### var Usage

Use `var` when the type is obvious from the right side.

```csharp
// Use var - type is obvious
var user = new User();
var users = new List<User>();
var name = user.Name;  // Obviously string
var count = users.Count;  // Obviously int

// Use explicit type - type not obvious
User? user = await GetUserAsync(id);
IEnumerable<Order> orders = GetOrdersForUser(userId);
```

### Nullable Reference Types

Enable and use nullable reference types.

```csharp
// Project file
<Nullable>enable</Nullable>

// Code
public class UserService
{
    // Non-nullable - must be set
    private readonly IUserRepository _repository;

    // Nullable - might be null
    public async Task<User?> GetByIdAsync(string id)
    {
        return await _repository.FindAsync(id);
    }

    // Handle nullable properly
    public async Task<string> GetUserNameAsync(string id)
    {
        var user = await GetByIdAsync(id);
        return user?.Name ?? "Unknown";
    }
}
```

### Records vs Classes

```csharp
// Use records for immutable data
public record UserDto(string Id, string Name, string Email);
public record CreateUserRequest(string Name, string Email);
public record UserCreatedEvent(string UserId, DateTime Timestamp);

// Use classes for mutable state and behavior
public class User
{
    public string Id { get; init; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public DateTime CreatedAt { get; init; } = DateTime.UtcNow;

    public void UpdateEmail(string newEmail)
    {
        Email = newEmail;
    }
}
```

---

## Expression-Bodied Members

Use for simple, single-expression members.

```csharp
public class User
{
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;

    // Expression-bodied property
    public string FullName => $"{FirstName} {LastName}";

    // Expression-bodied method
    public bool IsValid() => !string.IsNullOrWhiteSpace(FirstName);

    // Traditional method for complex logic
    public void Validate()
    {
        if (string.IsNullOrWhiteSpace(FirstName))
        {
            throw new ValidationException("FirstName is required");
        }

        if (string.IsNullOrWhiteSpace(Email))
        {
            throw new ValidationException("Email is required");
        }
    }
}
```

---

## Pattern Matching

Use modern pattern matching for cleaner code.

```csharp
// Type patterns
if (result is User user)
{
    Console.WriteLine(user.Name);
}

// Property patterns
if (user is { IsActive: true, Role: "Admin" })
{
    GrantAdminAccess();
}

// Switch expressions
var message = status switch
{
    OrderStatus.Pending => "Order is pending",
    OrderStatus.Shipped => "Order has shipped",
    OrderStatus.Delivered => "Order delivered",
    _ => "Unknown status"
};

// List patterns (.NET 8+)
var result = numbers switch
{
    [] => "Empty",
    [var single] => $"Single: {single}",
    [var first, .., var last] => $"First: {first}, Last: {last}",
    _ => "Multiple items"
};
```

---

## Comments

### When to Comment

```csharp
// DO: Explain why, not what
// Retry with exponential backoff because the external API has rate limiting
await Policy
    .Handle<HttpRequestException>()
    .WaitAndRetryAsync(3, attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)))
    .ExecuteAsync(() => _client.GetAsync(url));

// DO: Document public APIs
/// <summary>
/// Gets a user by their unique identifier.
/// </summary>
/// <param name="id">The user's unique identifier.</param>
/// <param name="cancellationToken">Cancellation token.</param>
/// <returns>The user if found; otherwise, null.</returns>
public async Task<User?> GetByIdAsync(string id, CancellationToken cancellationToken = default)

// DON'T: State the obvious
// Get the user  <- Obvious from code
var user = await GetUserAsync(id);

// Increment counter  <- Obvious from code
counter++;
```

### XML Documentation

Use for public APIs.

```csharp
/// <summary>
/// Service for managing user operations.
/// </summary>
public interface IUserService
{
    /// <summary>
    /// Creates a new user with the specified details.
    /// </summary>
    /// <param name="request">The user creation request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>
    /// A <see cref="Result{T}"/> containing the created user on success,
    /// or an error message on failure.
    /// </returns>
    /// <exception cref="ArgumentNullException">
    /// Thrown when <paramref name="request"/> is null.
    /// </exception>
    Task<Result<UserDto>> CreateAsync(
        CreateUserRequest request,
        CancellationToken cancellationToken = default);
}
```

---

## Summary

### Quick Reference

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `UserService` |
| Interfaces | I + PascalCase | `IUserRepository` |
| Methods | PascalCase | `GetUserAsync` |
| Properties | PascalCase | `FirstName` |
| Parameters | camelCase | `userId` |
| Local variables | camelCase | `userCount` |
| Private fields | _camelCase | `_userRepository` |
| Constants | PascalCase | `MaxRetries` |
| Async methods | Suffix with Async | `GetUserAsync` |

### Key Rules

1. One type per file (usually)
2. Always use braces
3. Use `var` when type is obvious
4. Enable nullable reference types
5. Use records for DTOs
6. Suffix async methods with `Async`
7. Prefix interfaces with `I`
8. Use expression-bodied members for simple cases
9. Comment the why, not the what
10. Maximum 120 character line length

---

*Last updated: 2026-01-15*

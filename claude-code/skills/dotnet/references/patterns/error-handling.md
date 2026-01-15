# Error Handling Patterns for .NET

Result pattern, exception handling, and ProblemDetails API for consistent error management.

---

## Exception Philosophy

### When to Throw Exceptions

Exceptions are for **exceptional** circumstances - unexpected conditions that the current code cannot reasonably handle.

```csharp
// DO throw for truly exceptional cases
public async Task<User> GetByIdAsync(string id)
{
    ArgumentException.ThrowIfNullOrWhiteSpace(id);  // Programming error

    var user = await _repository.FindAsync(id);
    return user ?? throw new UserNotFoundException(id);  // Exceptional: expected user doesn't exist
}

// DON'T throw for expected outcomes
public bool TryGetUser(string id, out User? user)
{
    user = _cache.Get(id);
    return user is not null;  // Not finding user is expected, not exceptional
}
```

### Exception Categories

| Category | Example | Handling |
|----------|---------|----------|
| **Programming errors** | `ArgumentNullException`, `InvalidOperationException` | Fix the code |
| **Environment errors** | `IOException`, `SqlException` | Retry or propagate |
| **Business errors** | `InsufficientFundsException` | Handle in business logic |
| **Validation errors** | `ValidationException` | Return to caller |

---

## Result Pattern

### Basic Result Type

```csharp
public abstract record Result<T>
{
    public record Success(T Value) : Result<T>;
    public record Failure(string Error, string? Code = null) : Result<T>;

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

    public async Task<TResult> MatchAsync<TResult>(
        Func<T, Task<TResult>> onSuccess,
        Func<string, Task<TResult>> onFailure) => this switch
    {
        Success s => await onSuccess(s.Value),
        Failure f => await onFailure(f.Error),
        _ => throw new InvalidOperationException()
    };
}

// Factory methods
public static class Result
{
    public static Result<T> Ok<T>(T value) => new Result<T>.Success(value);
    public static Result<T> Fail<T>(string error, string? code = null) =>
        new Result<T>.Failure(error, code);
}
```

### Using Result Pattern

```csharp
public class UserService
{
    public async Task<Result<UserDto>> CreateUserAsync(CreateUserRequest request)
    {
        // Validation
        var validationResult = await _validator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            return Result.Fail<UserDto>(
                validationResult.Errors.First().ErrorMessage,
                "VALIDATION_ERROR");
        }

        // Check for duplicate
        var existing = await _repository.FindByEmailAsync(request.Email);
        if (existing is not null)
        {
            return Result.Fail<UserDto>(
                $"User with email {request.Email} already exists",
                "DUPLICATE_USER");
        }

        // Create user
        var user = User.Create(request.Name, request.Email);
        await _repository.AddAsync(user);

        return Result.Ok(new UserDto(user.Id, user.Name, user.Email));
    }
}

// Usage
var result = await _userService.CreateUserAsync(request);
return result.Match(
    success => Results.Created($"/users/{success.Id}", success),
    failure => Results.BadRequest(new { error = failure })
);
```

### Result Extensions

```csharp
public static class ResultExtensions
{
    public static Result<TNew> Map<T, TNew>(
        this Result<T> result,
        Func<T, TNew> mapper) => result switch
    {
        Result<T>.Success s => Result.Ok(mapper(s.Value)),
        Result<T>.Failure f => Result.Fail<TNew>(f.Error, f.Code),
        _ => throw new InvalidOperationException()
    };

    public static async Task<Result<TNew>> MapAsync<T, TNew>(
        this Task<Result<T>> resultTask,
        Func<T, TNew> mapper)
    {
        var result = await resultTask;
        return result.Map(mapper);
    }

    public static Result<TNew> Bind<T, TNew>(
        this Result<T> result,
        Func<T, Result<TNew>> binder) => result switch
    {
        Result<T>.Success s => binder(s.Value),
        Result<T>.Failure f => Result.Fail<TNew>(f.Error, f.Code),
        _ => throw new InvalidOperationException()
    };
}
```

---

## Custom Exceptions

### Exception Hierarchy

```csharp
// Base domain exception
public abstract class DomainException : Exception
{
    public string Code { get; }

    protected DomainException(string message, string code)
        : base(message)
    {
        Code = code;
    }
}

// Specific exceptions
public class UserNotFoundException : DomainException
{
    public string UserId { get; }

    public UserNotFoundException(string userId)
        : base($"User with ID '{userId}' was not found", "USER_NOT_FOUND")
    {
        UserId = userId;
    }
}

public class InsufficientFundsException : DomainException
{
    public decimal Required { get; }
    public decimal Available { get; }

    public InsufficientFundsException(decimal required, decimal available)
        : base($"Insufficient funds. Required: {required}, Available: {available}", "INSUFFICIENT_FUNDS")
    {
        Required = required;
        Available = available;
    }
}

public class ConcurrencyException : DomainException
{
    public ConcurrencyException(string message)
        : base(message, "CONCURRENCY_CONFLICT") { }
}
```

### Exception Throwing Helpers

```csharp
public static class Throw
{
    public static void IfNull<T>([NotNull] T? argument, [CallerArgumentExpression(nameof(argument))] string? paramName = null)
        where T : class
    {
        ArgumentNullException.ThrowIfNull(argument, paramName);
    }

    public static void IfNullOrEmpty([NotNull] string? argument, [CallerArgumentExpression(nameof(argument))] string? paramName = null)
    {
        ArgumentException.ThrowIfNullOrEmpty(argument, paramName);
    }

    public static void IfNullOrWhiteSpace([NotNull] string? argument, [CallerArgumentExpression(nameof(argument))] string? paramName = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(argument, paramName);
    }

    public static T IfNotFound<T>(T? value, string id) where T : class
    {
        return value ?? throw new EntityNotFoundException(typeof(T).Name, id);
    }
}
```

---

## ProblemDetails API

### Standard ProblemDetails

ASP.NET Core provides built-in support for RFC 7807 Problem Details.

```csharp
// Program.cs
builder.Services.AddProblemDetails(options =>
{
    options.CustomizeProblemDetails = context =>
    {
        context.ProblemDetails.Extensions["traceId"] = context.HttpContext.TraceIdentifier;
    };
});

// Enable exception handling
app.UseExceptionHandler();
app.UseStatusCodePages();
```

### Custom Problem Details Factory

```csharp
public class CustomProblemDetailsFactory : ProblemDetailsFactory
{
    public override ProblemDetails CreateProblemDetails(
        HttpContext httpContext,
        int? statusCode = null,
        string? title = null,
        string? type = null,
        string? detail = null,
        string? instance = null)
    {
        return new ProblemDetails
        {
            Status = statusCode ?? 500,
            Title = title ?? GetDefaultTitle(statusCode ?? 500),
            Type = type ?? GetDefaultType(statusCode ?? 500),
            Detail = detail,
            Instance = instance ?? httpContext.Request.Path,
            Extensions =
            {
                ["traceId"] = httpContext.TraceIdentifier,
                ["timestamp"] = DateTime.UtcNow
            }
        };
    }

    private static string GetDefaultTitle(int statusCode) => statusCode switch
    {
        400 => "Bad Request",
        401 => "Unauthorized",
        403 => "Forbidden",
        404 => "Not Found",
        409 => "Conflict",
        422 => "Unprocessable Entity",
        500 => "Internal Server Error",
        _ => "Error"
    };

    private static string GetDefaultType(int statusCode) =>
        $"https://httpstatuses.io/{statusCode}";
}
```

### Exception Handler Middleware

```csharp
public class ExceptionHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionHandlingMiddleware> _logger;
    private readonly IProblemDetailsService _problemDetailsService;

    public ExceptionHandlingMiddleware(
        RequestDelegate next,
        ILogger<ExceptionHandlingMiddleware> logger,
        IProblemDetailsService problemDetailsService)
    {
        _next = next;
        _logger = logger;
        _problemDetailsService = problemDetailsService;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception occurred");
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var (statusCode, title, detail, code) = exception switch
        {
            UserNotFoundException ex => (404, "User Not Found", ex.Message, ex.Code),
            ValidationException ex => (400, "Validation Failed", ex.Message, "VALIDATION_ERROR"),
            UnauthorizedAccessException => (401, "Unauthorized", "Authentication required", "UNAUTHORIZED"),
            DomainException ex => (400, "Domain Error", ex.Message, ex.Code),
            _ => (500, "Internal Server Error", "An unexpected error occurred", "INTERNAL_ERROR")
        };

        context.Response.StatusCode = statusCode;

        var problemDetails = new ProblemDetails
        {
            Status = statusCode,
            Title = title,
            Detail = detail,
            Instance = context.Request.Path,
            Extensions =
            {
                ["code"] = code,
                ["traceId"] = context.TraceIdentifier
            }
        };

        await context.Response.WriteAsJsonAsync(problemDetails);
    }
}

// Registration
app.UseMiddleware<ExceptionHandlingMiddleware>();
```

---

## Validation Errors

### FluentValidation Integration

```csharp
public static class ValidationExtensions
{
    public static Result<T> ToResult<T>(this ValidationResult result, T value)
    {
        if (result.IsValid)
        {
            return Result.Ok(value);
        }

        var error = result.Errors.First();
        return Result.Fail<T>(error.ErrorMessage, error.ErrorCode ?? "VALIDATION_ERROR");
    }

    public static ValidationProblemDetails ToProblemDetails(this ValidationResult result)
    {
        var errors = result.Errors
            .GroupBy(e => e.PropertyName)
            .ToDictionary(
                g => g.Key,
                g => g.Select(e => e.ErrorMessage).ToArray());

        return new ValidationProblemDetails(errors)
        {
            Status = 400,
            Title = "Validation Failed",
            Detail = "One or more validation errors occurred"
        };
    }
}
```

### Validation Filter

```csharp
public class ValidationFilter<T> : IEndpointFilter where T : class
{
    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        var argument = context.Arguments.OfType<T>().FirstOrDefault();
        if (argument is null)
        {
            return Results.BadRequest(new ProblemDetails
            {
                Title = "Bad Request",
                Detail = "Request body is required"
            });
        }

        var validator = context.HttpContext.RequestServices.GetService<IValidator<T>>();
        if (validator is null)
        {
            return await next(context);
        }

        var result = await validator.ValidateAsync(argument);
        if (!result.IsValid)
        {
            return Results.ValidationProblem(
                result.Errors
                    .GroupBy(e => e.PropertyName)
                    .ToDictionary(
                        g => g.Key,
                        g => g.Select(e => e.ErrorMessage).ToArray()));
        }

        return await next(context);
    }
}

// Usage
app.MapPost("/users", CreateUser)
   .AddEndpointFilter<ValidationFilter<CreateUserRequest>>();
```

---

## Logging Errors

### Structured Error Logging

```csharp
public class OrderService
{
    private readonly ILogger<OrderService> _logger;

    public async Task<Result<Order>> ProcessOrderAsync(string orderId)
    {
        using var scope = _logger.BeginScope(new Dictionary<string, object>
        {
            ["OrderId"] = orderId,
            ["Operation"] = "ProcessOrder"
        });

        try
        {
            _logger.LogInformation("Starting order processing");

            var order = await _repository.GetByIdAsync(orderId);
            if (order is null)
            {
                _logger.LogWarning("Order not found");
                return Result.Fail<Order>("Order not found", "ORDER_NOT_FOUND");
            }

            // Process...

            _logger.LogInformation("Order processed successfully");
            return Result.Ok(order);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process order");
            throw;
        }
    }
}
```

---

## Summary

### Error Handling Strategy

| Situation | Approach |
|-----------|----------|
| Expected failure | Result pattern |
| Programming error | Throw ArgumentException |
| External failure | Throw + catch at boundary |
| Validation failure | FluentValidation + ProblemDetails |
| Not found | Throw NotFoundException or return Result |
| Conflict | Throw ConflictException |

### Best Practices

1. **Use Result pattern for expected failures**
2. **Use exceptions for exceptional cases**
3. **Create domain-specific exception types**
4. **Return ProblemDetails from APIs**
5. **Log errors with context**
6. **Never swallow exceptions silently**
7. **Handle exceptions at boundaries**

### API Response Patterns

| HTTP Status | When to Use |
|-------------|-------------|
| 200 OK | Success |
| 201 Created | Resource created |
| 204 No Content | Success, no body |
| 400 Bad Request | Invalid input |
| 401 Unauthorized | Authentication required |
| 403 Forbidden | Permission denied |
| 404 Not Found | Resource doesn't exist |
| 409 Conflict | Conflict with current state |
| 422 Unprocessable | Validation failed |
| 500 Internal Error | Unexpected server error |

---

*Last updated: 2026-01-15*

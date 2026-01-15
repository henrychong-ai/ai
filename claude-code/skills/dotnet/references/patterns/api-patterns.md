# API Patterns for ASP.NET Core

Minimal APIs, middleware, routing, and endpoint organization patterns.

---

## Minimal APIs

### Basic Endpoints

```csharp
var app = builder.Build();

// GET with route parameter
app.MapGet("/users/{id}", async (string id, IUserService service, CancellationToken ct) =>
{
    var user = await service.GetByIdAsync(id, ct);
    return user is not null
        ? Results.Ok(user)
        : Results.NotFound();
});

// POST with request body
app.MapPost("/users", async (CreateUserRequest request, IUserService service, CancellationToken ct) =>
{
    var user = await service.CreateAsync(request, ct);
    return Results.Created($"/users/{user.Id}", user);
});

// PUT with route and body
app.MapPut("/users/{id}", async (string id, UpdateUserRequest request, IUserService service, CancellationToken ct) =>
{
    var user = await service.UpdateAsync(id, request, ct);
    return user is not null
        ? Results.Ok(user)
        : Results.NotFound();
});

// DELETE
app.MapDelete("/users/{id}", async (string id, IUserService service, CancellationToken ct) =>
{
    var deleted = await service.DeleteAsync(id, ct);
    return deleted
        ? Results.NoContent()
        : Results.NotFound();
});
```

### Typed Results

```csharp
// Use TypedResults for better OpenAPI documentation
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

// With validation errors
app.MapPost("/users", async Task<Results<Created<UserDto>, ValidationProblem, Conflict>> (
    CreateUserRequest request,
    IValidator<CreateUserRequest> validator,
    IUserService service,
    CancellationToken ct) =>
{
    var validation = await validator.ValidateAsync(request, ct);
    if (!validation.IsValid)
    {
        return TypedResults.ValidationProblem(validation.ToDictionary());
    }

    var result = await service.CreateAsync(request, ct);
    return result.Match(
        user => TypedResults.Created($"/users/{user.Id}", user),
        error => TypedResults.Conflict());
});
```

---

## Endpoint Organization

### Route Groups

```csharp
// Program.cs
var app = builder.Build();

app.MapGroup("/api/v1")
   .MapUserEndpoints()
   .MapOrderEndpoints()
   .MapProductEndpoints();

app.Run();
```

### Extension Methods for Endpoints

```csharp
// Endpoints/UserEndpoints.cs
public static class UserEndpoints
{
    public static RouteGroupBuilder MapUserEndpoints(this RouteGroupBuilder group)
    {
        var users = group.MapGroup("/users")
            .WithTags("Users")
            .RequireAuthorization();

        users.MapGet("/", GetAllUsers)
             .WithName("GetAllUsers")
             .WithSummary("Get all users")
             .Produces<List<UserDto>>();

        users.MapGet("/{id}", GetUserById)
             .WithName("GetUserById")
             .WithSummary("Get user by ID")
             .Produces<UserDto>()
             .Produces(StatusCodes.Status404NotFound);

        users.MapPost("/", CreateUser)
             .WithName("CreateUser")
             .WithSummary("Create a new user")
             .Produces<UserDto>(StatusCodes.Status201Created)
             .ProducesValidationProblem();

        users.MapPut("/{id}", UpdateUser)
             .WithName("UpdateUser")
             .Produces<UserDto>()
             .Produces(StatusCodes.Status404NotFound);

        users.MapDelete("/{id}", DeleteUser)
             .WithName("DeleteUser")
             .Produces(StatusCodes.Status204NoContent)
             .Produces(StatusCodes.Status404NotFound);

        return group;
    }

    private static async Task<IResult> GetAllUsers(
        IUserService service,
        CancellationToken ct)
    {
        var users = await service.GetAllAsync(ct);
        return Results.Ok(users);
    }

    private static async Task<IResult> GetUserById(
        string id,
        IUserService service,
        CancellationToken ct)
    {
        var user = await service.GetByIdAsync(id, ct);
        return user is not null
            ? Results.Ok(user)
            : Results.NotFound();
    }

    private static async Task<IResult> CreateUser(
        CreateUserRequest request,
        IValidator<CreateUserRequest> validator,
        IUserService service,
        CancellationToken ct)
    {
        var validation = await validator.ValidateAsync(request, ct);
        if (!validation.IsValid)
        {
            return Results.ValidationProblem(validation.ToDictionary());
        }

        var user = await service.CreateAsync(request, ct);
        return Results.Created($"/api/v1/users/{user.Id}", user);
    }

    private static async Task<IResult> UpdateUser(
        string id,
        UpdateUserRequest request,
        IUserService service,
        CancellationToken ct)
    {
        var user = await service.UpdateAsync(id, request, ct);
        return user is not null
            ? Results.Ok(user)
            : Results.NotFound();
    }

    private static async Task<IResult> DeleteUser(
        string id,
        IUserService service,
        CancellationToken ct)
    {
        var deleted = await service.DeleteAsync(id, ct);
        return deleted
            ? Results.NoContent()
            : Results.NotFound();
    }
}
```

---

## Middleware

### Custom Middleware

```csharp
public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestLoggingMiddleware> _logger;

    public RequestLoggingMiddleware(RequestDelegate next, ILogger<RequestLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var requestId = Guid.NewGuid().ToString("N")[..8];

        using var scope = _logger.BeginScope(new Dictionary<string, object>
        {
            ["RequestId"] = requestId,
            ["Path"] = context.Request.Path,
            ["Method"] = context.Request.Method
        });

        var stopwatch = Stopwatch.StartNew();

        try
        {
            _logger.LogInformation("Request started");
            await _next(context);
            stopwatch.Stop();

            _logger.LogInformation(
                "Request completed with {StatusCode} in {ElapsedMs}ms",
                context.Response.StatusCode,
                stopwatch.ElapsedMilliseconds);
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex,
                "Request failed after {ElapsedMs}ms",
                stopwatch.ElapsedMilliseconds);
            throw;
        }
    }
}

// Registration
app.UseMiddleware<RequestLoggingMiddleware>();
```

### Middleware Pipeline Order

```csharp
var app = builder.Build();

// 1. Exception handling (outermost)
app.UseExceptionHandler();

// 2. HTTPS redirection
app.UseHttpsRedirection();

// 3. Static files (before routing)
app.UseStaticFiles();

// 4. Routing
app.UseRouting();

// 5. CORS (after routing, before auth)
app.UseCors();

// 6. Authentication
app.UseAuthentication();

// 7. Authorization
app.UseAuthorization();

// 8. Custom middleware
app.UseMiddleware<RequestLoggingMiddleware>();

// 9. Endpoints
app.MapControllers();
app.MapGet("/", () => "Hello!");

app.Run();
```

---

## Endpoint Filters

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
            return Results.BadRequest("Request body is required");
        }

        var validator = context.HttpContext.RequestServices.GetService<IValidator<T>>();
        if (validator is not null)
        {
            var result = await validator.ValidateAsync(argument);
            if (!result.IsValid)
            {
                return Results.ValidationProblem(result.ToDictionary());
            }
        }

        return await next(context);
    }
}

// Usage
app.MapPost("/users", CreateUser)
   .AddEndpointFilter<ValidationFilter<CreateUserRequest>>();
```

### Logging Filter

```csharp
public class LoggingFilter : IEndpointFilter
{
    private readonly ILogger<LoggingFilter> _logger;

    public LoggingFilter(ILogger<LoggingFilter> logger)
    {
        _logger = logger;
    }

    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        _logger.LogInformation(
            "Executing endpoint {Method} {Path}",
            context.HttpContext.Request.Method,
            context.HttpContext.Request.Path);

        var result = await next(context);

        _logger.LogInformation("Endpoint execution completed");

        return result;
    }
}
```

---

## Request/Response Handling

### Query Parameters

```csharp
// Simple parameters
app.MapGet("/users", async (
    string? name,
    int page = 1,
    int pageSize = 10,
    IUserService service,
    CancellationToken ct) =>
{
    var users = await service.SearchAsync(name, page, pageSize, ct);
    return Results.Ok(users);
});

// With [AsParameters] for complex queries
public record GetUsersQuery(
    string? Name,
    string? Email,
    bool? IsActive,
    int Page = 1,
    int PageSize = 10);

app.MapGet("/users", async (
    [AsParameters] GetUsersQuery query,
    IUserService service,
    CancellationToken ct) =>
{
    var users = await service.SearchAsync(query, ct);
    return Results.Ok(users);
});
```

### Headers and Cookies

```csharp
// Read headers
app.MapGet("/protected", (
    [FromHeader(Name = "X-Api-Key")] string apiKey,
    [FromHeader(Name = "X-Request-Id")] string? requestId) =>
{
    // Validate API key
    return Results.Ok(new { apiKey, requestId });
});

// Set headers
app.MapGet("/users/{id}", async (string id, IUserService service, HttpResponse response, CancellationToken ct) =>
{
    var user = await service.GetByIdAsync(id, ct);
    if (user is null)
    {
        return Results.NotFound();
    }

    response.Headers.Append("X-User-Version", user.Version.ToString());
    return Results.Ok(user);
});
```

### File Upload

```csharp
app.MapPost("/upload", async (IFormFile file, IFileService service, CancellationToken ct) =>
{
    if (file.Length == 0)
    {
        return Results.BadRequest("File is empty");
    }

    var result = await service.UploadAsync(file, ct);
    return Results.Ok(new { result.FileId, result.Url });
})
.DisableAntiforgery()  // For API endpoints
.Accepts<IFormFile>("multipart/form-data");
```

---

## OpenAPI/Swagger

### Configuration

```csharp
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "My API",
        Version = "v1",
        Description = "API description",
        Contact = new OpenApiContact
        {
            Name = "Support",
            Email = "support@example.com"
        }
    });

    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

// Enable Swagger
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
```

### Endpoint Documentation

```csharp
app.MapPost("/users", CreateUser)
   .WithName("CreateUser")
   .WithSummary("Create a new user")
   .WithDescription("Creates a new user with the provided details")
   .WithTags("Users")
   .Produces<UserDto>(StatusCodes.Status201Created)
   .ProducesValidationProblem()
   .Produces(StatusCodes.Status409Conflict)
   .WithOpenApi(operation =>
   {
       operation.RequestBody.Description = "User creation details";
       return operation;
   });
```

---

## Authentication & Authorization

### JWT Bearer

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
    });

builder.Services.AddAuthorization();
```

### Policy-Based Authorization

```csharp
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"))
    .AddPolicy("CanManageUsers", policy =>
        policy.RequireClaim("permission", "users:manage"));

// Usage
app.MapDelete("/users/{id}", DeleteUser)
   .RequireAuthorization("AdminOnly");

app.MapPut("/users/{id}", UpdateUser)
   .RequireAuthorization("CanManageUsers");
```

---

## Summary

### Endpoint Structure Pattern

```
Endpoints/
├── UserEndpoints.cs      # All user-related endpoints
├── OrderEndpoints.cs     # All order-related endpoints
└── ProductEndpoints.cs   # All product-related endpoints
```

### Best Practices

1. **Use route groups for organization**
2. **Use extension methods for endpoint registration**
3. **Use TypedResults for better documentation**
4. **Use endpoint filters for cross-cutting concerns**
5. **Always include CancellationToken**
6. **Document endpoints with OpenAPI attributes**
7. **Use [AsParameters] for complex query objects**

### Common HTTP Status Codes

| Status | When to Use | Result Method |
|--------|-------------|---------------|
| 200 | Success with body | `Results.Ok(data)` |
| 201 | Resource created | `Results.Created(uri, data)` |
| 204 | Success, no content | `Results.NoContent()` |
| 400 | Bad request | `Results.BadRequest(error)` |
| 401 | Unauthorized | `Results.Unauthorized()` |
| 403 | Forbidden | `Results.Forbid()` |
| 404 | Not found | `Results.NotFound()` |
| 409 | Conflict | `Results.Conflict()` |
| 422 | Validation error | `Results.ValidationProblem()` |

---

*Last updated: 2026-01-15*

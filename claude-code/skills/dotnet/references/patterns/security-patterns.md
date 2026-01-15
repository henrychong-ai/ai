# Security Patterns for .NET

Authentication, authorization, input validation, and OWASP protection patterns.

---

## Authentication

### JWT Bearer Authentication

```csharp
// Program.cs
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
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!)),
            ClockSkew = TimeSpan.Zero  // Remove default 5 minute tolerance
        };

        options.Events = new JwtBearerEvents
        {
            OnAuthenticationFailed = context =>
            {
                if (context.Exception is SecurityTokenExpiredException)
                {
                    context.Response.Headers.Append("Token-Expired", "true");
                }
                return Task.CompletedTask;
            }
        };
    });
```

### Token Generation

```csharp
public class TokenService : ITokenService
{
    private readonly JwtOptions _options;
    private readonly ILogger<TokenService> _logger;

    public TokenService(IOptions<JwtOptions> options, ILogger<TokenService> logger)
    {
        _options = options.Value;
        _logger = logger;
    }

    public string GenerateAccessToken(User user, IEnumerable<string> roles)
    {
        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, user.Id),
            new(JwtRegisteredClaimNames.Email, user.Email),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new(ClaimTypes.Name, user.Name)
        };

        claims.AddRange(roles.Select(role => new Claim(ClaimTypes.Role, role)));

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_options.Key));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: _options.Issuer,
            audience: _options.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_options.AccessTokenExpiryMinutes),
            signingCredentials: credentials);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public string GenerateRefreshToken()
    {
        var randomBytes = new byte[64];
        using var rng = RandomNumberGenerator.Create();
        rng.GetBytes(randomBytes);
        return Convert.ToBase64String(randomBytes);
    }
}
```

---

## Authorization

### Policy-Based Authorization

```csharp
builder.Services.AddAuthorizationBuilder()
    // Role-based policies
    .AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"))
    .AddPolicy("ModeratorOrAdmin", policy => policy.RequireRole("Admin", "Moderator"))

    // Claim-based policies
    .AddPolicy("CanManageUsers", policy =>
        policy.RequireClaim("permission", "users:manage"))

    // Custom requirement
    .AddPolicy("SameUserOrAdmin", policy =>
        policy.AddRequirements(new SameUserOrAdminRequirement()));
```

### Custom Authorization Handler

```csharp
public class SameUserOrAdminRequirement : IAuthorizationRequirement { }

public class SameUserOrAdminHandler : AuthorizationHandler<SameUserOrAdminRequirement, string>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        SameUserOrAdminRequirement requirement,
        string resourceUserId)
    {
        var userId = context.User.FindFirstValue(ClaimTypes.NameIdentifier);

        if (context.User.IsInRole("Admin") || userId == resourceUserId)
        {
            context.Succeed(requirement);
        }

        return Task.CompletedTask;
    }
}

// Registration
builder.Services.AddSingleton<IAuthorizationHandler, SameUserOrAdminHandler>();

// Usage in endpoint
app.MapPut("/users/{id}", async (
    string id,
    UpdateUserRequest request,
    IAuthorizationService authService,
    ClaimsPrincipal user,
    IUserService service,
    CancellationToken ct) =>
{
    var authResult = await authService.AuthorizeAsync(user, id, "SameUserOrAdmin");
    if (!authResult.Succeeded)
    {
        return Results.Forbid();
    }

    var result = await service.UpdateAsync(id, request, ct);
    return result is not null ? Results.Ok(result) : Results.NotFound();
});
```

---

## Input Validation

### FluentValidation

```csharp
public class CreateUserValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required")
            .EmailAddress().WithMessage("Invalid email format")
            .MaximumLength(255).WithMessage("Email must not exceed 255 characters");

        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Name is required")
            .MinimumLength(2).WithMessage("Name must be at least 2 characters")
            .MaximumLength(100).WithMessage("Name must not exceed 100 characters")
            .Matches(@"^[\p{L}\s'-]+$").WithMessage("Name contains invalid characters");

        RuleFor(x => x.Password)
            .NotEmpty().WithMessage("Password is required")
            .MinimumLength(12).WithMessage("Password must be at least 12 characters")
            .Matches(@"[A-Z]").WithMessage("Password must contain uppercase letter")
            .Matches(@"[a-z]").WithMessage("Password must contain lowercase letter")
            .Matches(@"\d").WithMessage("Password must contain digit")
            .Matches(@"[\W_]").WithMessage("Password must contain special character");
    }
}

// Registration
builder.Services.AddValidatorsFromAssemblyContaining<CreateUserValidator>();
```

### Data Annotations

```csharp
public record CreateUserRequest
{
    [Required(ErrorMessage = "Email is required")]
    [EmailAddress(ErrorMessage = "Invalid email format")]
    [MaxLength(255)]
    public string Email { get; init; } = string.Empty;

    [Required(ErrorMessage = "Name is required")]
    [MinLength(2)]
    [MaxLength(100)]
    public string Name { get; init; } = string.Empty;

    [Required]
    [MinLength(12)]
    public string Password { get; init; } = string.Empty;
}
```

---

## OWASP Protections

### SQL Injection Prevention

```csharp
// Good: EF Core with LINQ (parameterized by default)
var user = await _context.Users
    .Where(u => u.Email == email)  // Safe - parameterized
    .FirstOrDefaultAsync(ct);

// Good: Raw SQL with parameters
var users = await _context.Users
    .FromSqlInterpolated($"SELECT * FROM Users WHERE Email = {email}")  // Safe
    .ToListAsync(ct);

// Bad: String concatenation
var users = await _context.Users
    .FromSqlRaw($"SELECT * FROM Users WHERE Email = '{email}'")  // VULNERABLE
    .ToListAsync(ct);
```

### XSS Prevention

```csharp
// Razor automatically encodes by default
@Model.UserProvidedContent  // Safe - encoded

// Explicit encoding when needed
@Html.Raw(sanitizedHtml)  // Use only with sanitized content

// In APIs, use HtmlEncoder
public class ContentService
{
    private readonly HtmlEncoder _encoder;

    public ContentService(HtmlEncoder encoder)
    {
        _encoder = encoder;
    }

    public string SanitizeInput(string input)
    {
        return _encoder.Encode(input);
    }
}
```

### CSRF Protection

```csharp
// For traditional MVC forms
builder.Services.AddAntiforgery(options =>
{
    options.HeaderName = "X-XSRF-TOKEN";
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    options.Cookie.SameSite = SameSiteMode.Strict;
});

// For APIs, CSRF is less relevant but consider:
// 1. Use Bearer tokens (not cookies) for authentication
// 2. Validate Origin/Referer headers
// 3. Use SameSite cookie policy
```

### Security Headers

```csharp
// Add security headers middleware
app.Use(async (context, next) =>
{
    var headers = context.Response.Headers;

    // Prevent clickjacking
    headers.Append("X-Frame-Options", "DENY");

    // Prevent MIME type sniffing
    headers.Append("X-Content-Type-Options", "nosniff");

    // Enable XSS filter
    headers.Append("X-XSS-Protection", "1; mode=block");

    // Content Security Policy
    headers.Append("Content-Security-Policy",
        "default-src 'self'; " +
        "script-src 'self'; " +
        "style-src 'self' 'unsafe-inline'; " +
        "img-src 'self' data:; " +
        "font-src 'self'; " +
        "frame-ancestors 'none'");

    // Referrer Policy
    headers.Append("Referrer-Policy", "strict-origin-when-cross-origin");

    // Permissions Policy
    headers.Append("Permissions-Policy",
        "geolocation=(), microphone=(), camera=()");

    await next();
});

// HSTS for HTTPS
app.UseHsts();
app.UseHttpsRedirection();
```

---

## Secrets Management

### Development Secrets

```bash
# Initialize secrets
dotnet user-secrets init

# Set secrets
dotnet user-secrets set "Jwt:Key" "your-super-secret-key-here"
dotnet user-secrets set "ConnectionStrings:Default" "Server=..."
```

### Azure Key Vault

```csharp
builder.Configuration.AddAzureKeyVault(
    new Uri($"https://{keyVaultName}.vault.azure.net/"),
    new DefaultAzureCredential());

// Access secrets
var connectionString = builder.Configuration["ConnectionStrings:Default"];
```

### Environment Variables

```csharp
// Access environment variables
var apiKey = Environment.GetEnvironmentVariable("API_KEY");

// In configuration
builder.Configuration
    .AddJsonFile("appsettings.json")
    .AddJsonFile($"appsettings.{environment}.json", optional: true)
    .AddEnvironmentVariables()  // Override with env vars
    .AddUserSecrets<Program>(optional: true);  // Dev secrets
```

### Password Hashing

```csharp
public class PasswordHasher
{
    private const int SaltSize = 16;
    private const int HashSize = 32;
    private const int Iterations = 100000;

    public string Hash(string password)
    {
        using var algorithm = new Rfc2898DeriveBytes(
            password,
            SaltSize,
            Iterations,
            HashAlgorithmName.SHA256);

        var salt = algorithm.Salt;
        var hash = algorithm.GetBytes(HashSize);

        var result = new byte[SaltSize + HashSize];
        Buffer.BlockCopy(salt, 0, result, 0, SaltSize);
        Buffer.BlockCopy(hash, 0, result, SaltSize, HashSize);

        return Convert.ToBase64String(result);
    }

    public bool Verify(string password, string hashedPassword)
    {
        var hashBytes = Convert.FromBase64String(hashedPassword);

        var salt = new byte[SaltSize];
        Buffer.BlockCopy(hashBytes, 0, salt, 0, SaltSize);

        using var algorithm = new Rfc2898DeriveBytes(
            password,
            salt,
            Iterations,
            HashAlgorithmName.SHA256);

        var hash = algorithm.GetBytes(HashSize);

        for (int i = 0; i < HashSize; i++)
        {
            if (hashBytes[i + SaltSize] != hash[i])
            {
                return false;
            }
        }

        return true;
    }
}

// Or use ASP.NET Core Identity's hasher
public class UserService
{
    private readonly IPasswordHasher<User> _passwordHasher;

    public string HashPassword(User user, string password)
    {
        return _passwordHasher.HashPassword(user, password);
    }

    public bool VerifyPassword(User user, string password)
    {
        var result = _passwordHasher.VerifyHashedPassword(user, user.PasswordHash, password);
        return result != PasswordVerificationResult.Failed;
    }
}
```

---

## Rate Limiting

### Built-in Rate Limiting (.NET 7+)

```csharp
builder.Services.AddRateLimiter(options =>
{
    // Fixed window limiter
    options.AddFixedWindowLimiter("fixed", limiterOptions =>
    {
        limiterOptions.PermitLimit = 100;
        limiterOptions.Window = TimeSpan.FromMinutes(1);
        limiterOptions.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        limiterOptions.QueueLimit = 10;
    });

    // Sliding window limiter
    options.AddSlidingWindowLimiter("sliding", limiterOptions =>
    {
        limiterOptions.PermitLimit = 100;
        limiterOptions.Window = TimeSpan.FromMinutes(1);
        limiterOptions.SegmentsPerWindow = 4;
    });

    // Token bucket limiter
    options.AddTokenBucketLimiter("token", limiterOptions =>
    {
        limiterOptions.TokenLimit = 100;
        limiterOptions.ReplenishmentPeriod = TimeSpan.FromSeconds(10);
        limiterOptions.TokensPerPeriod = 10;
    });

    // Custom rejection response
    options.OnRejected = async (context, token) =>
    {
        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
        await context.HttpContext.Response.WriteAsJsonAsync(new ProblemDetails
        {
            Status = 429,
            Title = "Too Many Requests",
            Detail = "Rate limit exceeded. Please try again later."
        }, token);
    };
});

app.UseRateLimiter();

// Apply to endpoints
app.MapGet("/api/data", GetData)
   .RequireRateLimiting("fixed");

app.MapGroup("/api/v1")
   .RequireRateLimiting("sliding")
   .MapUserEndpoints();
```

---

## Logging Security Events

```csharp
public class SecurityAuditLogger
{
    private readonly ILogger<SecurityAuditLogger> _logger;

    public void LogAuthenticationAttempt(string username, bool success, string? ipAddress)
    {
        if (success)
        {
            _logger.LogInformation(
                "Authentication succeeded for user {Username} from {IpAddress}",
                username, ipAddress);
        }
        else
        {
            _logger.LogWarning(
                "Authentication failed for user {Username} from {IpAddress}",
                username, ipAddress);
        }
    }

    public void LogAuthorizationFailure(string userId, string resource, string action)
    {
        _logger.LogWarning(
            "Authorization denied for user {UserId} attempting {Action} on {Resource}",
            userId, action, resource);
    }

    public void LogSuspiciousActivity(string userId, string activity, string details)
    {
        _logger.LogWarning(
            "Suspicious activity detected - User: {UserId}, Activity: {Activity}, Details: {Details}",
            userId, activity, details);
    }
}
```

---

## Summary

### Security Checklist

- [ ] JWT tokens with short expiry and refresh tokens
- [ ] Policy-based authorization
- [ ] Input validation with FluentValidation
- [ ] Parameterized queries (EF Core LINQ)
- [ ] Security headers configured
- [ ] HTTPS enforced with HSTS
- [ ] Rate limiting enabled
- [ ] Secrets in Key Vault/Secrets Manager
- [ ] Password hashing with modern algorithm
- [ ] Security events logged

### Common Vulnerabilities

| OWASP | Mitigation |
|-------|------------|
| A01 Broken Access Control | Policy-based authorization |
| A02 Cryptographic Failures | HTTPS, proper hashing |
| A03 Injection | Parameterized queries |
| A04 Insecure Design | Threat modeling |
| A05 Security Misconfiguration | Security headers |
| A06 Vulnerable Components | Regular updates |
| A07 Auth Failures | JWT, rate limiting |
| A08 Data Integrity Failures | CSRF, signed tokens |
| A09 Logging Failures | Security audit logging |
| A10 SSRF | URL validation |

---

*Last updated: 2026-01-15*

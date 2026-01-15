# Clean Code Principles for C#

SOLID principles, dependency injection patterns, and clean architecture guidelines.

---

## SOLID Principles

### Single Responsibility Principle (SRP)

A class should have only one reason to change.

```csharp
// Bad: Multiple responsibilities
public class UserService
{
    public async Task<User> CreateUserAsync(CreateUserRequest request)
    {
        // Validation
        if (string.IsNullOrEmpty(request.Email))
            throw new ValidationException("Email required");

        // Business logic
        var user = new User { Email = request.Email };

        // Persistence
        await _context.Users.AddAsync(user);
        await _context.SaveChangesAsync();

        // Notification
        await SendWelcomeEmail(user);

        return user;
    }
}

// Good: Single responsibility per class
public class UserService
{
    private readonly IUserRepository _repository;
    private readonly IUserValidator _validator;
    private readonly INotificationService _notifications;

    public async Task<User> CreateUserAsync(CreateUserRequest request)
    {
        await _validator.ValidateAndThrowAsync(request);

        var user = new User { Email = request.Email };
        await _repository.AddAsync(user);

        await _notifications.SendWelcomeAsync(user);

        return user;
    }
}
```

### Open/Closed Principle (OCP)

Open for extension, closed for modification.

```csharp
// Bad: Requires modification for new discount types
public decimal CalculateDiscount(Order order, string discountType)
{
    return discountType switch
    {
        "percentage" => order.Total * 0.1m,
        "fixed" => 10m,
        "loyalty" => order.Total * 0.15m,
        _ => 0
    };
}

// Good: Extensible through abstraction
public interface IDiscountStrategy
{
    decimal Calculate(Order order);
}

public class PercentageDiscount : IDiscountStrategy
{
    private readonly decimal _percentage;
    public PercentageDiscount(decimal percentage) => _percentage = percentage;
    public decimal Calculate(Order order) => order.Total * _percentage;
}

public class FixedDiscount : IDiscountStrategy
{
    private readonly decimal _amount;
    public FixedDiscount(decimal amount) => _amount = amount;
    public decimal Calculate(Order order) => Math.Min(_amount, order.Total);
}

public class DiscountCalculator
{
    public decimal Calculate(Order order, IDiscountStrategy strategy)
        => strategy.Calculate(order);
}
```

### Liskov Substitution Principle (LSP)

Derived types must be substitutable for base types.

```csharp
// Bad: Square violates Rectangle contract
public class Rectangle
{
    public virtual int Width { get; set; }
    public virtual int Height { get; set; }
    public int Area => Width * Height;
}

public class Square : Rectangle
{
    public override int Width
    {
        set { base.Width = base.Height = value; }
    }
    public override int Height
    {
        set { base.Width = base.Height = value; }
    }
}

// Good: Separate abstractions
public interface IShape
{
    int Area { get; }
}

public record Rectangle(int Width, int Height) : IShape
{
    public int Area => Width * Height;
}

public record Square(int Side) : IShape
{
    public int Area => Side * Side;
}
```

### Interface Segregation Principle (ISP)

Clients shouldn't depend on methods they don't use.

```csharp
// Bad: Fat interface
public interface IRepository<T>
{
    Task<T?> GetByIdAsync(string id);
    Task<IEnumerable<T>> GetAllAsync();
    Task AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(string id);
    Task<int> CountAsync();
    Task<bool> ExistsAsync(string id);
    Task BulkInsertAsync(IEnumerable<T> entities);
    Task TruncateAsync();
}

// Good: Segregated interfaces
public interface IReadRepository<T>
{
    Task<T?> GetByIdAsync(string id, CancellationToken ct = default);
    Task<IEnumerable<T>> GetAllAsync(CancellationToken ct = default);
}

public interface IWriteRepository<T>
{
    Task AddAsync(T entity, CancellationToken ct = default);
    Task UpdateAsync(T entity, CancellationToken ct = default);
    Task DeleteAsync(string id, CancellationToken ct = default);
}

public interface IRepository<T> : IReadRepository<T>, IWriteRepository<T> { }
```

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions.

```csharp
// Bad: Direct dependency on concrete class
public class OrderService
{
    private readonly SqlServerOrderRepository _repository = new();
    private readonly SmtpEmailService _emailService = new();

    public async Task CreateOrderAsync(Order order)
    {
        await _repository.AddAsync(order);
        await _emailService.SendAsync(order.CustomerEmail, "Order Confirmed");
    }
}

// Good: Depend on abstractions
public class OrderService
{
    private readonly IOrderRepository _repository;
    private readonly IEmailService _emailService;

    public OrderService(IOrderRepository repository, IEmailService emailService)
    {
        _repository = repository;
        _emailService = emailService;
    }

    public async Task CreateOrderAsync(Order order)
    {
        await _repository.AddAsync(order);
        await _emailService.SendAsync(order.CustomerEmail, "Order Confirmed");
    }
}
```

---

## Dependency Injection

### Constructor Injection (Preferred)

```csharp
public class UserService : IUserService
{
    private readonly IUserRepository _repository;
    private readonly ILogger<UserService> _logger;
    private readonly UserServiceOptions _options;

    public UserService(
        IUserRepository repository,
        ILogger<UserService> logger,
        IOptions<UserServiceOptions> options)
    {
        _repository = repository;
        _logger = logger;
        _options = options.Value;
    }
}
```

### Service Lifetimes

```csharp
// Singleton: One instance for application lifetime
builder.Services.AddSingleton<ICacheService, MemoryCacheService>();

// Scoped: One instance per request/scope
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();

// Transient: New instance every time
builder.Services.AddTransient<IEmailService, SmtpEmailService>();
builder.Services.AddTransient<IValidator<CreateUserRequest>, CreateUserValidator>();
```

### Registration Patterns

```csharp
// Interface to implementation
builder.Services.AddScoped<IUserService, UserService>();

// Self registration
builder.Services.AddScoped<UserService>();

// Factory registration
builder.Services.AddScoped<IDbConnection>(sp =>
    new SqlConnection(configuration.GetConnectionString("Default")));

// Generic registration
builder.Services.AddScoped(typeof(IRepository<>), typeof(Repository<>));

// Assembly scanning (with Scrutor)
builder.Services.Scan(scan => scan
    .FromAssemblyOf<IUserService>()
    .AddClasses(classes => classes.AssignableTo<IService>())
    .AsImplementedInterfaces()
    .WithScopedLifetime());
```

### Options Pattern

```csharp
// Configuration class
public class EmailOptions
{
    public const string SectionName = "Email";

    public string SmtpHost { get; init; } = string.Empty;
    public int SmtpPort { get; init; } = 587;
    public string FromAddress { get; init; } = string.Empty;
    public bool UseSsl { get; init; } = true;
}

// Registration
builder.Services.Configure<EmailOptions>(
    builder.Configuration.GetSection(EmailOptions.SectionName));

// Usage with IOptions<T>
public class EmailService
{
    private readonly EmailOptions _options;

    public EmailService(IOptions<EmailOptions> options)
    {
        _options = options.Value;
    }
}

// Usage with IOptionsSnapshot<T> (reloads on change)
public class EmailService
{
    private readonly EmailOptions _options;

    public EmailService(IOptionsSnapshot<EmailOptions> options)
    {
        _options = options.Value;
    }
}
```

---

## Clean Architecture

### Layer Structure

```
MyProject/
├── src/
│   ├── MyProject.Domain/           # Entities, value objects, domain events
│   │   ├── Entities/
│   │   ├── ValueObjects/
│   │   ├── Events/
│   │   └── Exceptions/
│   │
│   ├── MyProject.Application/      # Use cases, interfaces, DTOs
│   │   ├── Common/
│   │   │   ├── Interfaces/
│   │   │   └── Behaviors/
│   │   ├── Users/
│   │   │   ├── Commands/
│   │   │   ├── Queries/
│   │   │   └── DTOs/
│   │   └── DependencyInjection.cs
│   │
│   ├── MyProject.Infrastructure/   # External concerns (DB, email, etc.)
│   │   ├── Persistence/
│   │   ├── Services/
│   │   └── DependencyInjection.cs
│   │
│   └── MyProject.Api/              # Presentation (controllers, endpoints)
│       ├── Endpoints/
│       ├── Middleware/
│       └── Program.cs
```

### Dependency Direction

```
Api → Application → Domain
       ↓
    Infrastructure
```

- **Domain**: No dependencies (pure business logic)
- **Application**: Depends only on Domain
- **Infrastructure**: Depends on Application (implements interfaces)
- **Api**: Depends on Application and Infrastructure (for DI registration)

### Domain Layer

```csharp
// Domain/Entities/User.cs
public class User
{
    public string Id { get; private set; } = Guid.NewGuid().ToString();
    public string Email { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;

    private User() { } // For EF Core

    public static User Create(string email, string name)
    {
        if (string.IsNullOrWhiteSpace(email))
            throw new DomainException("Email is required");

        return new User { Email = email, Name = name };
    }

    public void UpdateEmail(string newEmail)
    {
        if (string.IsNullOrWhiteSpace(newEmail))
            throw new DomainException("Email cannot be empty");

        Email = newEmail;
    }
}
```

### Application Layer

```csharp
// Application/Users/Commands/CreateUser/CreateUserCommand.cs
public record CreateUserCommand(string Email, string Name) : IRequest<UserDto>;

// Application/Users/Commands/CreateUser/CreateUserCommandHandler.cs
public class CreateUserCommandHandler : IRequestHandler<CreateUserCommand, UserDto>
{
    private readonly IUserRepository _repository;
    private readonly IUnitOfWork _unitOfWork;

    public CreateUserCommandHandler(IUserRepository repository, IUnitOfWork unitOfWork)
    {
        _repository = repository;
        _unitOfWork = unitOfWork;
    }

    public async Task<UserDto> Handle(CreateUserCommand request, CancellationToken ct)
    {
        var user = User.Create(request.Email, request.Name);

        await _repository.AddAsync(user, ct);
        await _unitOfWork.SaveChangesAsync(ct);

        return new UserDto(user.Id, user.Name, user.Email);
    }
}
```

---

## Code Smells to Avoid

### God Classes

```csharp
// Bad: Class does everything
public class UserManager
{
    public void CreateUser() { }
    public void UpdateUser() { }
    public void DeleteUser() { }
    public void SendEmail() { }
    public void GenerateReport() { }
    public void ProcessPayment() { }
    public void ValidateUser() { }
    public void LogActivity() { }
}

// Good: Single responsibility
public class UserService { /* CRUD only */ }
public class EmailService { /* Email only */ }
public class ReportService { /* Reports only */ }
public class PaymentService { /* Payments only */ }
```

### Primitive Obsession

```csharp
// Bad: Primitives everywhere
public void CreateOrder(string customerId, string email, decimal amount, string currency)

// Good: Value objects
public record CustomerId(string Value);
public record Email(string Value);
public record Money(decimal Amount, string Currency);

public void CreateOrder(CustomerId customerId, Email email, Money total)
```

### Feature Envy

```csharp
// Bad: Method uses another object's data more than its own
public class OrderPrinter
{
    public string Print(Order order)
    {
        return $"Order: {order.Id}\n" +
               $"Customer: {order.Customer.Name}\n" +
               $"Address: {order.Customer.Address.Street}, {order.Customer.Address.City}\n" +
               $"Total: {order.Total.Amount} {order.Total.Currency}";
    }
}

// Good: Move behavior to the class that owns the data
public class Order
{
    public string ToDisplayString() =>
        $"Order: {Id}\nCustomer: {Customer.DisplayName}\nTotal: {Total}";
}

public class Customer
{
    public string DisplayName => $"{Name}, {Address}";
}
```

### Long Parameter Lists

```csharp
// Bad: Too many parameters
public void CreateUser(
    string firstName,
    string lastName,
    string email,
    string phone,
    string street,
    string city,
    string country,
    string postalCode,
    bool isActive,
    DateTime createdAt)

// Good: Parameter object
public record CreateUserRequest(
    string FirstName,
    string LastName,
    string Email,
    string? Phone,
    AddressDto Address,
    bool IsActive = true);

public void CreateUser(CreateUserRequest request)
```

---

## Best Practices Summary

### Do

1. **One class, one responsibility**
2. **Depend on abstractions**
3. **Use constructor injection**
4. **Keep methods small (< 20 lines)**
5. **Use meaningful names**
6. **Write self-documenting code**
7. **Use value objects for domain concepts**
8. **Fail fast with guard clauses**

### Don't

1. **Don't use static state**
2. **Don't use Service Locator**
3. **Don't catch generic exceptions**
4. **Don't use magic numbers/strings**
5. **Don't repeat yourself (DRY)**
6. **Don't use inheritance for code reuse**
7. **Don't expose implementation details**
8. **Don't create "Manager" or "Helper" classes**

---

*Last updated: 2026-01-15*

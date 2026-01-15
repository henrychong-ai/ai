# Testing Strategies for .NET

TDD, integration testing, testing pyramid, and coverage strategies.

---

## Testing Pyramid

```
         /\
        /  \      End-to-End (Few)
       /----\     - Full system tests
      /      \    - Slowest, most brittle
     /--------\   Integration (Some)
    /          \  - Component interaction
   /------------\ - Database, APIs
  /              \Unit (Many)
 /----------------\- Fast, isolated
        Base       - Most tests here
```

### Test Distribution

| Level | Coverage | Speed | Isolation |
|-------|----------|-------|-----------|
| Unit | 70-80% | Fast (ms) | Complete |
| Integration | 15-25% | Medium (s) | Partial |
| E2E | 5-10% | Slow (min) | None |

---

## Unit Testing

### Characteristics

- Test single unit (class/method) in isolation
- Mock all dependencies
- Fast execution (< 100ms)
- No external resources (DB, network, files)

### Example

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repositoryMock;
    private readonly Mock<IEmailService> _emailMock;
    private readonly UserService _sut;

    public UserServiceTests()
    {
        _repositoryMock = new Mock<IUserRepository>();
        _emailMock = new Mock<IEmailService>();
        _sut = new UserService(_repositoryMock.Object, _emailMock.Object);
    }

    [Fact]
    public async Task CreateAsync_WithValidInput_CreatesUserAndSendsEmail()
    {
        // Arrange
        var request = new CreateUserRequest("Alice", "alice@example.com");
        _repositoryMock
            .Setup(r => r.AddAsync(It.IsAny<User>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _sut.CreateAsync(request);

        // Assert
        result.Should().NotBeNull();
        _repositoryMock.Verify(r => r.AddAsync(
            It.Is<User>(u => u.Email == "alice@example.com"),
            It.IsAny<CancellationToken>()), Times.Once);
        _emailMock.Verify(e => e.SendWelcomeEmailAsync(
            "alice@example.com",
            It.IsAny<CancellationToken>()), Times.Once);
    }
}
```

---

## Integration Testing

### ASP.NET Core Integration Tests

```csharp
public class UserEndpointsTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    private readonly WebApplicationFactory<Program> _factory;

    public UserEndpointsTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace real database with in-memory
                var descriptor = services.SingleOrDefault(
                    d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
                if (descriptor != null)
                {
                    services.Remove(descriptor);
                }

                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));
            });
        });

        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task GetUser_WhenExists_ReturnsOk()
    {
        // Arrange
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        db.Users.Add(new User { Id = "123", Name = "Alice" });
        await db.SaveChangesAsync();

        // Act
        var response = await _client.GetAsync("/api/v1/users/123");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var user = await response.Content.ReadFromJsonAsync<UserDto>();
        user.Should().NotBeNull();
        user!.Name.Should().Be("Alice");
    }

    [Fact]
    public async Task GetUser_WhenNotFound_Returns404()
    {
        // Act
        var response = await _client.GetAsync("/api/v1/users/nonexistent");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task CreateUser_WithValidInput_Returns201()
    {
        // Arrange
        var request = new CreateUserRequest("Bob", "bob@example.com");

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/users", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();
    }
}
```

### Database Integration Tests

```csharp
public class UserRepositoryIntegrationTests : IAsyncLifetime
{
    private readonly SqliteConnection _connection;
    private readonly AppDbContext _context;
    private readonly UserRepository _repository;

    public UserRepositoryIntegrationTests()
    {
        _connection = new SqliteConnection("DataSource=:memory:");
        _connection.Open();

        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseSqlite(_connection)
            .Options;

        _context = new AppDbContext(options);
        _repository = new UserRepository(_context);
    }

    public async Task InitializeAsync()
    {
        await _context.Database.EnsureCreatedAsync();
    }

    public async Task DisposeAsync()
    {
        await _context.DisposeAsync();
        await _connection.DisposeAsync();
    }

    [Fact]
    public async Task AddAsync_SavesToDatabase()
    {
        // Arrange
        var user = new User { Id = "1", Name = "Alice", Email = "alice@test.com" };

        // Act
        await _repository.AddAsync(user);

        // Assert
        var saved = await _context.Users.FindAsync("1");
        saved.Should().NotBeNull();
        saved!.Name.Should().Be("Alice");
    }
}
```

---

## Test-Driven Development (TDD)

### Red-Green-Refactor Cycle

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while tests pass

### TDD Example

```csharp
// Step 1: Write failing test (RED)
[Fact]
public void CalculateDiscount_WhenOrderOver100_Returns10Percent()
{
    var calculator = new DiscountCalculator();
    var order = new Order { Total = 150m };

    var discount = calculator.Calculate(order);

    discount.Should().Be(15m);  // 10% of 150
}

// Step 2: Minimal implementation (GREEN)
public class DiscountCalculator
{
    public decimal Calculate(Order order)
    {
        if (order.Total > 100)
        {
            return order.Total * 0.10m;
        }
        return 0;
    }
}

// Step 3: Add more tests, refactor as needed
[Theory]
[InlineData(50, 0)]
[InlineData(100, 0)]
[InlineData(101, 10.10)]
[InlineData(200, 20)]
public void CalculateDiscount_ReturnsCorrectAmount(decimal total, decimal expected)
{
    var calculator = new DiscountCalculator();
    var order = new Order { Total = total };

    var discount = calculator.Calculate(order);

    discount.Should().Be(expected);
}
```

### When to Use TDD

| Use TDD | Skip TDD |
|---------|----------|
| Business logic | Simple CRUD |
| Complex algorithms | UI/presentation |
| Domain rules | Exploratory work |
| Bug fixes | Prototypes |
| API contracts | Learning new tech |

---

## Code Coverage

### Configuration

```xml
<!-- Directory.Build.props -->
<PropertyGroup>
    <CollectCoverage>true</CollectCoverage>
    <CoverletOutputFormat>cobertura</CoverletOutputFormat>
    <CoverletOutput>./coverage/</CoverletOutput>
</PropertyGroup>
```

### Commands

```bash
# Run with coverage
dotnet test --collect:"XPlat Code Coverage"

# Generate report
dotnet tool install -g dotnet-reportgenerator-globaltool
reportgenerator \
    -reports:./coverage/**/coverage.cobertura.xml \
    -targetdir:./coverage/report \
    -reporttypes:Html

# View in browser
open ./coverage/report/index.html
```

### Coverage Targets

| Metric | Target | Critical |
|--------|--------|----------|
| Line coverage | 80% | 70% |
| Branch coverage | 75% | 65% |
| Method coverage | 85% | 75% |

### Exclusions

```csharp
// Exclude from coverage
[ExcludeFromCodeCoverage]
public class GeneratedCode { }

// In csproj
<ItemGroup>
    <AssemblyAttribute Include="System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverageAttribute" />
</ItemGroup>
```

---

## Test Organization

### Project Structure

```
tests/
├── MyProject.Tests.Unit/
│   ├── Services/
│   │   ├── UserServiceTests.cs
│   │   └── OrderServiceTests.cs
│   ├── Validators/
│   │   └── CreateUserValidatorTests.cs
│   └── Helpers/
│       ├── UserBuilder.cs
│       └── MockUserRepository.cs
├── MyProject.Tests.Integration/
│   ├── Endpoints/
│   │   └── UserEndpointsTests.cs
│   ├── Repositories/
│   │   └── UserRepositoryTests.cs
│   └── Fixtures/
│       └── DatabaseFixture.cs
└── MyProject.Tests.E2E/
    └── UserJourneyTests.cs
```

### Naming Conventions

```csharp
// File: {ClassUnderTest}Tests.cs
// Class: {ClassUnderTest}Tests
// Method: {Method}_{Scenario}_{ExpectedResult}

public class UserServiceTests
{
    [Fact]
    public async Task CreateAsync_WithValidInput_ReturnsUser() { }

    [Fact]
    public async Task CreateAsync_WithDuplicateEmail_ThrowsConflictException() { }

    [Fact]
    public async Task GetByIdAsync_WhenUserNotFound_ReturnsNull() { }
}
```

---

## Test Data Management

### In-Memory Test Data

```csharp
public static class TestData
{
    public static class Users
    {
        public static User Alice => new()
        {
            Id = "user-1",
            Name = "Alice",
            Email = "alice@test.com",
            IsActive = true
        };

        public static User Bob => new()
        {
            Id = "user-2",
            Name = "Bob",
            Email = "bob@test.com",
            IsActive = false
        };
    }
}

// Usage
[Fact]
public async Task Test_WithTestData()
{
    _repositoryMock
        .Setup(r => r.GetByIdAsync("user-1", It.IsAny<CancellationToken>()))
        .ReturnsAsync(TestData.Users.Alice);

    var result = await _sut.GetByIdAsync("user-1");

    result.Should().BeEquivalentTo(TestData.Users.Alice);
}
```

### Database Seeding

```csharp
public class DatabaseFixture : IAsyncLifetime
{
    public AppDbContext Context { get; private set; } = null!;

    public async Task InitializeAsync()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        Context = new AppDbContext(options);
        await SeedDataAsync();
    }

    private async Task SeedDataAsync()
    {
        Context.Users.AddRange(
            TestData.Users.Alice,
            TestData.Users.Bob);

        await Context.SaveChangesAsync();
    }

    public Task DisposeAsync()
    {
        return Context.DisposeAsync().AsTask();
    }
}
```

---

## Summary

### Testing Strategy Checklist

- [ ] Unit tests for all business logic
- [ ] Integration tests for API endpoints
- [ ] Integration tests for database operations
- [ ] Minimum 80% code coverage
- [ ] Test naming follows conventions
- [ ] Test data is maintainable
- [ ] CI runs all tests
- [ ] Coverage reports generated

### Test Commands

```bash
# Unit tests only
dotnet test --filter "Category=Unit"

# Integration tests only
dotnet test --filter "Category=Integration"

# With coverage
dotnet test --collect:"XPlat Code Coverage"

# Verbose output
dotnet test --verbosity normal

# Specific test
dotnet test --filter "FullyQualifiedName~UserServiceTests.CreateAsync"
```

---

*Last updated: 2026-01-15*

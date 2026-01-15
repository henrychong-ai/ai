# xUnit Patterns for .NET

xUnit test structure, traits, fixtures, and organization patterns.

---

## Test Structure

### Basic Test Class

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repositoryMock;
    private readonly Mock<ILogger<UserService>> _loggerMock;
    private readonly UserService _sut;  // System Under Test

    public UserServiceTests()
    {
        _repositoryMock = new Mock<IUserRepository>();
        _loggerMock = new Mock<ILogger<UserService>>();
        _sut = new UserService(_repositoryMock.Object, _loggerMock.Object);
    }

    [Fact]
    public async Task GetByIdAsync_WhenUserExists_ReturnsUser()
    {
        // Arrange
        var expectedUser = new User { Id = "123", Name = "Alice" };
        _repositoryMock
            .Setup(r => r.GetByIdAsync("123", It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedUser);

        // Act
        var result = await _sut.GetByIdAsync("123");

        // Assert
        Assert.NotNull(result);
        Assert.Equal("Alice", result.Name);
    }

    [Fact]
    public async Task GetByIdAsync_WhenUserNotFound_ReturnsNull()
    {
        // Arrange
        _repositoryMock
            .Setup(r => r.GetByIdAsync("nonexistent", It.IsAny<CancellationToken>()))
            .ReturnsAsync((User?)null);

        // Act
        var result = await _sut.GetByIdAsync("nonexistent");

        // Assert
        Assert.Null(result);
    }
}
```

### Test Naming Convention

Follow the pattern: `MethodName_Scenario_ExpectedResult`

```csharp
// Good names
GetByIdAsync_WhenUserExists_ReturnsUser()
GetByIdAsync_WhenUserNotFound_ReturnsNull()
CreateAsync_WithValidInput_CreatesUser()
CreateAsync_WithDuplicateEmail_ThrowsConflictException()
ValidateEmail_WithEmptyString_ReturnsFalse()

// Bad names
Test1()
GetUserTest()
ItShouldWork()
```

---

## Fact vs Theory

### Fact (Single Test Case)

```csharp
[Fact]
public void Add_TwoNumbers_ReturnsSum()
{
    // Single specific test case
    var result = Calculator.Add(2, 3);
    Assert.Equal(5, result);
}
```

### Theory (Parameterized Tests)

```csharp
// InlineData for simple cases
[Theory]
[InlineData(2, 3, 5)]
[InlineData(0, 0, 0)]
[InlineData(-1, 1, 0)]
[InlineData(100, 200, 300)]
public void Add_TwoNumbers_ReturnsSum(int a, int b, int expected)
{
    var result = Calculator.Add(a, b);
    Assert.Equal(expected, result);
}

// MemberData for complex cases
[Theory]
[MemberData(nameof(GetUserTestData))]
public async Task CreateAsync_WithVariousInputs_ReturnsExpectedResult(
    CreateUserRequest request,
    bool shouldSucceed)
{
    var result = await _sut.CreateAsync(request);

    if (shouldSucceed)
    {
        Assert.NotNull(result);
    }
    else
    {
        Assert.Null(result);
    }
}

public static IEnumerable<object[]> GetUserTestData()
{
    yield return new object[]
    {
        new CreateUserRequest("Alice", "alice@example.com"),
        true
    };
    yield return new object[]
    {
        new CreateUserRequest("", "invalid"),
        false
    };
}

// ClassData for reusable test data
[Theory]
[ClassData(typeof(UserTestDataGenerator))]
public async Task CreateAsync_WithTestData_BehavesCorrectly(
    CreateUserRequest request,
    Type? expectedException)
{
    if (expectedException is null)
    {
        var result = await _sut.CreateAsync(request);
        Assert.NotNull(result);
    }
    else
    {
        await Assert.ThrowsAsync(expectedException,
            () => _sut.CreateAsync(request));
    }
}

public class UserTestDataGenerator : IEnumerable<object?[]>
{
    public IEnumerator<object?[]> GetEnumerator()
    {
        yield return new object?[]
        {
            new CreateUserRequest("Valid", "valid@test.com"),
            null  // No exception expected
        };
        yield return new object?[]
        {
            new CreateUserRequest("", "test@test.com"),
            typeof(ValidationException)
        };
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}
```

---

## Test Categories with Traits

```csharp
// Categorize tests
[Fact]
[Trait("Category", "Unit")]
public void UnitTest() { }

[Fact]
[Trait("Category", "Integration")]
public void IntegrationTest() { }

[Fact]
[Trait("Category", "Slow")]
public void SlowTest() { }

// Filter when running
// dotnet test --filter "Category=Unit"
// dotnet test --filter "Category!=Slow"
```

### Custom Trait Attributes

```csharp
public class UnitTestAttribute : FactAttribute
{
    public UnitTestAttribute()
    {
        // Can add custom logic here
    }
}

public class IntegrationTestAttribute : FactAttribute
{
    public IntegrationTestAttribute()
    {
        Skip = Environment.GetEnvironmentVariable("RUN_INTEGRATION_TESTS") != "true"
            ? "Integration tests disabled"
            : null;
    }
}

// Usage
[UnitTest]
public void MyUnitTest() { }

[IntegrationTest]
public void MyIntegrationTest() { }
```

---

## Test Fixtures

### Class Fixture (Shared per Test Class)

```csharp
// Fixture class
public class DatabaseFixture : IDisposable
{
    public AppDbContext Context { get; }

    public DatabaseFixture()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        Context = new AppDbContext(options);
        SeedData();
    }

    private void SeedData()
    {
        Context.Users.AddRange(
            new User { Id = "1", Name = "Alice" },
            new User { Id = "2", Name = "Bob" });
        Context.SaveChanges();
    }

    public void Dispose()
    {
        Context.Dispose();
    }
}

// Test class using fixture
public class UserRepositoryTests : IClassFixture<DatabaseFixture>
{
    private readonly DatabaseFixture _fixture;

    public UserRepositoryTests(DatabaseFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task GetAllAsync_ReturnsSeededUsers()
    {
        var repository = new UserRepository(_fixture.Context);

        var users = await repository.GetAllAsync();

        Assert.Equal(2, users.Count());
    }
}
```

### Collection Fixture (Shared Across Test Classes)

```csharp
// Define collection
[CollectionDefinition("Database")]
public class DatabaseCollection : ICollectionFixture<DatabaseFixture> { }

// Use in multiple test classes
[Collection("Database")]
public class UserServiceTests
{
    private readonly DatabaseFixture _fixture;

    public UserServiceTests(DatabaseFixture fixture)
    {
        _fixture = fixture;
    }
}

[Collection("Database")]
public class OrderServiceTests
{
    private readonly DatabaseFixture _fixture;

    public OrderServiceTests(DatabaseFixture fixture)
    {
        _fixture = fixture;
    }
}
```

---

## Async Test Lifecycle

### IAsyncLifetime

```csharp
public class AsyncDatabaseTests : IAsyncLifetime
{
    private AppDbContext _context = null!;
    private UserService _sut = null!;

    public async Task InitializeAsync()
    {
        // Async setup
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        _context = new AppDbContext(options);
        await SeedDataAsync();

        _sut = new UserService(new UserRepository(_context));
    }

    public async Task DisposeAsync()
    {
        // Async cleanup
        await _context.DisposeAsync();
    }

    private async Task SeedDataAsync()
    {
        _context.Users.Add(new User { Id = "1", Name = "Test" });
        await _context.SaveChangesAsync();
    }

    [Fact]
    public async Task Test_WithAsyncSetup()
    {
        var user = await _sut.GetByIdAsync("1");
        Assert.NotNull(user);
    }
}
```

---

## Output and Logging

### ITestOutputHelper

```csharp
public class UserServiceTests
{
    private readonly ITestOutputHelper _output;

    public UserServiceTests(ITestOutputHelper output)
    {
        _output = output;
    }

    [Fact]
    public async Task Test_WithOutput()
    {
        _output.WriteLine("Starting test...");

        var result = await _sut.ProcessAsync();

        _output.WriteLine($"Result: {result}");
        Assert.NotNull(result);
    }
}
```

### Logging to Test Output

```csharp
public class TestLoggerProvider : ILoggerProvider
{
    private readonly ITestOutputHelper _output;

    public TestLoggerProvider(ITestOutputHelper output)
    {
        _output = output;
    }

    public ILogger CreateLogger(string categoryName)
    {
        return new TestLogger(_output, categoryName);
    }

    public void Dispose() { }
}

public class TestLogger : ILogger
{
    private readonly ITestOutputHelper _output;
    private readonly string _categoryName;

    public TestLogger(ITestOutputHelper output, string categoryName)
    {
        _output = output;
        _categoryName = categoryName;
    }

    public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;

    public bool IsEnabled(LogLevel logLevel) => true;

    public void Log<TState>(
        LogLevel logLevel,
        EventId eventId,
        TState state,
        Exception? exception,
        Func<TState, Exception?, string> formatter)
    {
        _output.WriteLine($"[{logLevel}] {_categoryName}: {formatter(state, exception)}");
    }
}
```

---

## Parallel Execution

### Configure Parallelism

```csharp
// xunit.runner.json
{
    "parallelizeTestCollections": true,
    "maxParallelThreads": 4
}

// Disable for specific collection
[Collection("NonParallel")]
public class NonParallelTests { }
```

### Disable Parallelism for Class

```csharp
[Collection("Sequential")]
public class SequentialTests
{
    // These tests won't run in parallel with each other
}
```

---

## Summary

### Quick Reference

| Feature | Attribute/Method |
|---------|------------------|
| Single test | `[Fact]` |
| Parameterized test | `[Theory]` with `[InlineData]` |
| Complex test data | `[MemberData]` or `[ClassData]` |
| Categorize | `[Trait("Category", "Value")]` |
| Skip test | `[Fact(Skip = "Reason")]` |
| Shared setup | `IClassFixture<T>` |
| Shared across classes | `ICollectionFixture<T>` |
| Async lifecycle | `IAsyncLifetime` |
| Test output | `ITestOutputHelper` |

### Test Commands

```bash
# Run all tests
dotnet test

# Verbose output
dotnet test --verbosity normal

# Filter by category
dotnet test --filter "Category=Unit"

# Filter by name
dotnet test --filter "FullyQualifiedName~UserServiceTests"

# With coverage
dotnet test --collect:"XPlat Code Coverage"

# Specific project
dotnet test MyProject.Tests
```

---

*Last updated: 2026-01-15*

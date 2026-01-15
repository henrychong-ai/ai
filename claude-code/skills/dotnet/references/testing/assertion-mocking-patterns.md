# Assertion and Mocking Patterns for .NET

FluentAssertions and Moq patterns for expressive, maintainable tests.

---

## FluentAssertions

### Basic Assertions

```csharp
using FluentAssertions;

// Equality
result.Should().Be(expected);
result.Should().NotBe(unexpected);
result.Should().BeEquivalentTo(expectedObject);

// Null checks
result.Should().NotBeNull();
result.Should().BeNull();

// Booleans
result.Should().BeTrue();
result.Should().BeFalse();

// Comparisons
value.Should().BeGreaterThan(5);
value.Should().BeLessThanOrEqualTo(10);
value.Should().BeInRange(1, 100);
value.Should().BePositive();
value.Should().BeNegative();
```

### String Assertions

```csharp
// Content
name.Should().Be("Alice");
name.Should().StartWith("Al");
name.Should().EndWith("ice");
name.Should().Contain("lic");
name.Should().NotContain("bad");

// Case
name.Should().BeEquivalentTo("ALICE");  // Case-insensitive

// Pattern
email.Should().MatchRegex(@"^[\w.-]+@[\w.-]+\.\w+$");

// Length
name.Should().HaveLength(5);
name.Should().NotBeNullOrEmpty();
name.Should().NotBeNullOrWhiteSpace();
```

### Collection Assertions

```csharp
// Count
users.Should().HaveCount(3);
users.Should().NotBeEmpty();
users.Should().BeEmpty();
users.Should().ContainSingle();

// Content
users.Should().Contain(expectedUser);
users.Should().NotContain(unwantedUser);
users.Should().ContainEquivalentOf(new User { Name = "Alice" });

// Order
users.Should().BeInAscendingOrder(u => u.Name);
users.Should().BeInDescendingOrder(u => u.CreatedAt);

// All/Any
users.Should().AllSatisfy(u => u.IsActive.Should().BeTrue());
users.Should().OnlyContain(u => u.Age >= 18);
users.Should().HaveCountGreaterThan(0);

// Specific items
users.Should().ContainSingle(u => u.Name == "Admin");
users.First().Should().BeEquivalentTo(expectedFirst);
```

### Object Assertions

```csharp
// Equivalence (value comparison)
actualUser.Should().BeEquivalentTo(expectedUser);

// Excluding properties
actualUser.Should().BeEquivalentTo(expectedUser, options =>
    options.Excluding(u => u.CreatedAt)
           .Excluding(u => u.Id));

// Including only specific properties
actualUser.Should().BeEquivalentTo(expectedUser, options =>
    options.Including(u => u.Name)
           .Including(u => u.Email));

// Type checking
result.Should().BeOfType<UserDto>();
result.Should().BeAssignableTo<IEntity>();
```

### Exception Assertions

```csharp
// Sync
action.Should().Throw<ArgumentException>();
action.Should().Throw<ArgumentException>()
    .WithMessage("*cannot be empty*");
action.Should().ThrowExactly<UserNotFoundException>();
action.Should().NotThrow();

// Async
await action.Should().ThrowAsync<ValidationException>();
await action.Should().ThrowAsync<DomainException>()
    .WithMessage("User not found");
await action.Should().NotThrowAsync();

// Inner exceptions
action.Should().Throw<Exception>()
    .WithInnerException<SqlException>();
```

### DateTime Assertions

```csharp
result.Should().Be(expected);
result.Should().BeAfter(DateTime.UtcNow.AddHours(-1));
result.Should().BeBefore(DateTime.UtcNow);
result.Should().BeCloseTo(expected, TimeSpan.FromSeconds(1));
result.Should().BeOnOrBefore(deadline);
result.Should().HaveYear(2024);
result.Should().HaveMonth(1);
```

### Chaining Assertions

```csharp
user.Should()
    .NotBeNull()
    .And.BeOfType<UserDto>()
    .Which.Name.Should().Be("Alice");

users.Should()
    .NotBeEmpty()
    .And.HaveCount(3)
    .And.OnlyContain(u => u.IsActive);
```

---

## Moq Mocking

### Basic Setup

```csharp
// Create mock
var repositoryMock = new Mock<IUserRepository>();

// Setup method return value
repositoryMock
    .Setup(r => r.GetByIdAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
    .ReturnsAsync(new User { Id = "123", Name = "Alice" });

// Setup with specific argument
repositoryMock
    .Setup(r => r.GetByIdAsync("123", It.IsAny<CancellationToken>()))
    .ReturnsAsync(new User { Id = "123", Name = "Alice" });

// Use mock
var service = new UserService(repositoryMock.Object);
```

### Argument Matchers

```csharp
// Any value
It.IsAny<string>()
It.IsAny<CancellationToken>()

// Specific conditions
It.Is<string>(s => s.Length > 0)
It.Is<int>(i => i > 0 && i < 100)
It.Is<User>(u => u.Email.Contains("@"))

// Regex
It.IsRegex(@"^user-\d+$")

// Null
It.IsNull<string>()
It.IsNotNull<string>()

// In range
It.IsInRange(1, 10, Moq.Range.Inclusive)
```

### Return Values

```csharp
// Simple return
mock.Setup(m => m.GetValue()).Returns(42);

// Async return
mock.Setup(m => m.GetValueAsync()).ReturnsAsync(42);

// Computed return based on input
mock.Setup(m => m.Process(It.IsAny<string>()))
    .Returns((string input) => input.ToUpper());

// Sequence of returns
mock.SetupSequence(m => m.GetNext())
    .Returns(1)
    .Returns(2)
    .Returns(3)
    .Throws<InvalidOperationException>();

// Return different values for different calls
var callCount = 0;
mock.Setup(m => m.GetValue())
    .Returns(() => ++callCount);
```

### Throwing Exceptions

```csharp
// Throw exception
mock.Setup(m => m.DangerousOperation())
    .Throws<InvalidOperationException>();

// Throw with message
mock.Setup(m => m.Process(It.IsAny<string>()))
    .Throws(new ValidationException("Invalid input"));

// Async throw
mock.Setup(m => m.ProcessAsync())
    .ThrowsAsync(new TimeoutException());
```

### Callbacks

```csharp
// Track calls
var capturedId = string.Empty;
mock.Setup(m => m.GetByIdAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
    .Callback<string, CancellationToken>((id, ct) => capturedId = id)
    .ReturnsAsync(new User());

// Complex callback
var processedItems = new List<string>();
mock.Setup(m => m.Process(It.IsAny<string>()))
    .Callback<string>(item => processedItems.Add(item))
    .Returns(true);
```

### Verification

```csharp
// Verify method was called
mock.Verify(m => m.SaveAsync(It.IsAny<User>(), It.IsAny<CancellationToken>()));

// Verify call count
mock.Verify(m => m.SaveAsync(It.IsAny<User>(), It.IsAny<CancellationToken>()), Times.Once);
mock.Verify(m => m.GetByIdAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Exactly(2));
mock.Verify(m => m.DeleteAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Never);

// Verify with argument matching
mock.Verify(m => m.SaveAsync(
    It.Is<User>(u => u.Name == "Alice"),
    It.IsAny<CancellationToken>()));

// Verify all setups were called
mock.VerifyAll();

// Verify no other calls
mock.VerifyNoOtherCalls();
```

### Properties

```csharp
// Setup property getter
mock.SetupGet(m => m.Name).Returns("Test");

// Setup property setter
mock.SetupSet(m => m.Name = It.IsAny<string>());

// Track property changes
mock.SetupProperty(m => m.Name);
mock.SetupProperty(m => m.Name, "Default");

// Verify property access
mock.VerifyGet(m => m.Name);
mock.VerifySet(m => m.Name = "Expected");
```

---

## Common Testing Patterns

### Arrange-Act-Assert

```csharp
[Fact]
public async Task CreateUserAsync_WithValidInput_ReturnsCreatedUser()
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
    result.Name.Should().Be("Alice");
    result.Email.Should().Be("alice@example.com");

    _repositoryMock.Verify(
        r => r.AddAsync(It.Is<User>(u => u.Email == "alice@example.com"), It.IsAny<CancellationToken>()),
        Times.Once);
}
```

### Builder Pattern for Test Data

```csharp
public class UserBuilder
{
    private string _id = Guid.NewGuid().ToString();
    private string _name = "Test User";
    private string _email = "test@example.com";
    private bool _isActive = true;

    public UserBuilder WithId(string id)
    {
        _id = id;
        return this;
    }

    public UserBuilder WithName(string name)
    {
        _name = name;
        return this;
    }

    public UserBuilder WithEmail(string email)
    {
        _email = email;
        return this;
    }

    public UserBuilder Inactive()
    {
        _isActive = false;
        return this;
    }

    public User Build() => new()
    {
        Id = _id,
        Name = _name,
        Email = _email,
        IsActive = _isActive
    };
}

// Usage
var user = new UserBuilder()
    .WithName("Alice")
    .WithEmail("alice@test.com")
    .Build();
```

### Mock Repository Pattern

```csharp
public class MockUserRepository
{
    private readonly Mock<IUserRepository> _mock = new();
    private readonly List<User> _users = new();

    public MockUserRepository WithUser(User user)
    {
        _users.Add(user);
        return this;
    }

    public MockUserRepository WithUsers(params User[] users)
    {
        _users.AddRange(users);
        return this;
    }

    public IUserRepository Build()
    {
        _mock.Setup(r => r.GetAllAsync(It.IsAny<CancellationToken>()))
             .ReturnsAsync(_users);

        _mock.Setup(r => r.GetByIdAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
             .ReturnsAsync((string id, CancellationToken _) => _users.FirstOrDefault(u => u.Id == id));

        return _mock.Object;
    }

    public Mock<IUserRepository> Mock => _mock;
}

// Usage
var repository = new MockUserRepository()
    .WithUser(new User { Id = "1", Name = "Alice" })
    .WithUser(new User { Id = "2", Name = "Bob" })
    .Build();
```

---

## Summary

### FluentAssertions Quick Reference

| Operation | Method |
|-----------|--------|
| Equality | `.Should().Be(expected)` |
| Not null | `.Should().NotBeNull()` |
| Type check | `.Should().BeOfType<T>()` |
| Collection count | `.Should().HaveCount(n)` |
| Contains | `.Should().Contain(item)` |
| Exception | `.Should().Throw<TException>()` |
| Equivalent | `.Should().BeEquivalentTo(obj)` |

### Moq Quick Reference

| Operation | Method |
|-----------|--------|
| Setup return | `.Setup(m => m.Method()).Returns(value)` |
| Async return | `.Setup(m => m.MethodAsync()).ReturnsAsync(value)` |
| Throw | `.Setup(m => m.Method()).Throws<TException>()` |
| Verify called | `.Verify(m => m.Method())` |
| Verify count | `.Verify(m => m.Method(), Times.Once)` |
| Any argument | `It.IsAny<T>()` |
| Conditional | `It.Is<T>(x => condition)` |

---

*Last updated: 2026-01-15*

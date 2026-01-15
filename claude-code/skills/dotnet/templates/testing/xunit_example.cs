// Package: example demonstrates xUnit testing patterns for .NET.
// This is a template file showing test structure with xUnit and FluentAssertions.
namespace Example.Tests;

using FluentAssertions;
using Moq;
using Xunit;

// =============================================================================
// Example Domain Types for Demonstration
// =============================================================================

public record User(string Id, string Name, string Email);
public record CreateUserRequest(string Name, string Email);

public interface IUserRepository
{
    Task<User?> GetByIdAsync(string id, CancellationToken ct = default);
    Task AddAsync(User user, CancellationToken ct = default);
}

public class UserService
{
    private readonly IUserRepository _repository;

    public UserService(IUserRepository repository)
    {
        _repository = repository;
    }

    public async Task<User?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        return await _repository.GetByIdAsync(id, ct);
    }

    public async Task<User> CreateAsync(CreateUserRequest request, CancellationToken ct = default)
    {
        var user = new User(Guid.NewGuid().ToString(), request.Name, request.Email);
        await _repository.AddAsync(user, ct);
        return user;
    }
}

// =============================================================================
// Basic Unit Test Example
// =============================================================================

public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repositoryMock;
    private readonly UserService _sut;  // System Under Test

    public UserServiceTests()
    {
        _repositoryMock = new Mock<IUserRepository>();
        _sut = new UserService(_repositoryMock.Object);
    }

    [Fact]
    public async Task GetByIdAsync_WhenUserExists_ReturnsUser()
    {
        // Arrange
        var expectedUser = new User("123", "Alice", "alice@example.com");
        _repositoryMock
            .Setup(r => r.GetByIdAsync("123", It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedUser);

        // Act
        var result = await _sut.GetByIdAsync("123");

        // Assert
        result.Should().NotBeNull();
        result!.Name.Should().Be("Alice");
        result.Email.Should().Be("alice@example.com");
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
        result.Should().BeNull();
    }

    [Fact]
    public async Task CreateAsync_WithValidRequest_ReturnsCreatedUser()
    {
        // Arrange
        var request = new CreateUserRequest("Bob", "bob@example.com");
        _repositoryMock
            .Setup(r => r.AddAsync(It.IsAny<User>(), It.IsAny<CancellationToken>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _sut.CreateAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.Name.Should().Be("Bob");
        result.Email.Should().Be("bob@example.com");
        result.Id.Should().NotBeNullOrEmpty();

        _repositoryMock.Verify(
            r => r.AddAsync(It.Is<User>(u => u.Email == "bob@example.com"), It.IsAny<CancellationToken>()),
            Times.Once);
    }
}

// =============================================================================
// Table-Driven Test Example
// =============================================================================

public class EmailValidatorTests
{
    [Theory]
    [InlineData("user@example.com", true)]
    [InlineData("user.name@example.com", true)]
    [InlineData("user@subdomain.example.com", true)]
    [InlineData("", false)]
    [InlineData("invalid", false)]
    [InlineData("@example.com", false)]
    [InlineData("user@", false)]
    public void IsValidEmail_ReturnsExpectedResult(string email, bool expected)
    {
        var result = IsValidEmail(email);

        result.Should().Be(expected);
    }

    private static bool IsValidEmail(string email)
    {
        if (string.IsNullOrWhiteSpace(email)) return false;
        var atIndex = email.IndexOf('@');
        return atIndex > 0 && atIndex < email.Length - 1;
    }
}

// =============================================================================
// Test with Setup and Cleanup
// =============================================================================

public class UserServiceWithLifecycleTests : IAsyncLifetime
{
    private Mock<IUserRepository> _repositoryMock = null!;
    private UserService _sut = null!;

    public Task InitializeAsync()
    {
        // Async setup - runs before each test
        _repositoryMock = new Mock<IUserRepository>();
        _sut = new UserService(_repositoryMock.Object);
        return Task.CompletedTask;
    }

    public Task DisposeAsync()
    {
        // Async cleanup - runs after each test
        return Task.CompletedTask;
    }

    [Fact]
    public async Task Test_WithAsyncLifecycle()
    {
        _repositoryMock
            .Setup(r => r.GetByIdAsync("1", It.IsAny<CancellationToken>()))
            .ReturnsAsync(new User("1", "Test", "test@example.com"));

        var result = await _sut.GetByIdAsync("1");

        result.Should().NotBeNull();
    }
}

// =============================================================================
// Subtest Example
// =============================================================================

public class UserValidationTests
{
    [Fact]
    public void User_Validation_Tests()
    {
        // Subtests for related validation scenarios
    }

    [Theory]
    [InlineData("Alice", true)]
    [InlineData("", false)]
    [InlineData("   ", false)]
    [InlineData("A", true)]
    [InlineData(null, false)]
    public void ValidateName_ReturnsExpectedResult(string? name, bool expected)
    {
        var result = ValidateName(name);
        result.Should().Be(expected);
    }

    private static bool ValidateName(string? name)
        => !string.IsNullOrWhiteSpace(name);
}

// =============================================================================
// Exception Testing Example
// =============================================================================

public class ExceptionTests
{
    [Fact]
    public void Operation_WithInvalidInput_ThrowsArgumentException()
    {
        // Arrange
        var service = new ValidationService();

        // Act
        var action = () => service.ValidateRequired(string.Empty, "value");

        // Assert
        action.Should().Throw<ArgumentException>()
            .WithMessage("*cannot be empty*");
    }

    [Fact]
    public async Task AsyncOperation_WhenFails_ThrowsException()
    {
        // Arrange
        var mock = new Mock<IUserRepository>();
        mock.Setup(r => r.GetByIdAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ThrowsAsync(new InvalidOperationException("Database error"));

        var service = new UserService(mock.Object);

        // Act
        var action = async () => await service.GetByIdAsync("1");

        // Assert
        await action.Should().ThrowAsync<InvalidOperationException>()
            .WithMessage("Database error");
    }
}

public class ValidationService
{
    public void ValidateRequired(string value, string paramName)
    {
        if (string.IsNullOrEmpty(value))
            throw new ArgumentException($"{paramName} cannot be empty", paramName);
    }
}

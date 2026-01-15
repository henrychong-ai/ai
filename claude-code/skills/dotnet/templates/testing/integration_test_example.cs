// Package: example demonstrates integration testing with WebApplicationFactory.
// This is a template file showing API integration test patterns.
namespace Example.Tests.Integration;

using System.Net;
using System.Net.Http.Json;
using FluentAssertions;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

// =============================================================================
// Example Types for Demonstration
// =============================================================================

public record UserDto(string Id, string Name, string Email);
public record CreateUserRequest(string Name, string Email);

public class User
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
}

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
}

// =============================================================================
// Integration Test with WebApplicationFactory
// =============================================================================

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
                // Remove real database
                var descriptor = services.SingleOrDefault(
                    d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
                if (descriptor != null)
                {
                    services.Remove(descriptor);
                }

                // Add in-memory database
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb_" + Guid.NewGuid()));
            });

            builder.UseEnvironment("Testing");
        });

        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task GetUser_WhenUserExists_ReturnsOk()
    {
        // Arrange: Seed data
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        var user = new User { Id = "test-123", Name = "Alice", Email = "alice@test.com" };
        db.Users.Add(user);
        await db.SaveChangesAsync();

        // Act
        var response = await _client.GetAsync("/api/v1/users/test-123");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var result = await response.Content.ReadFromJsonAsync<UserDto>();
        result.Should().NotBeNull();
        result!.Name.Should().Be("Alice");
        result.Email.Should().Be("alice@test.com");
    }

    [Fact]
    public async Task GetUser_WhenUserNotFound_ReturnsNotFound()
    {
        // Act
        var response = await _client.GetAsync("/api/v1/users/nonexistent");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task CreateUser_WithValidInput_ReturnsCreated()
    {
        // Arrange
        var request = new CreateUserRequest("Bob", "bob@test.com");

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/users", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();

        var result = await response.Content.ReadFromJsonAsync<UserDto>();
        result.Should().NotBeNull();
        result!.Name.Should().Be("Bob");
        result.Email.Should().Be("bob@test.com");
    }

    [Fact]
    public async Task CreateUser_WithInvalidEmail_ReturnsBadRequest()
    {
        // Arrange
        var request = new CreateUserRequest("Charlie", "not-an-email");

        // Act
        var response = await _client.PostAsJsonAsync("/api/v1/users", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task DeleteUser_WhenUserExists_ReturnsNoContent()
    {
        // Arrange: Seed data
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        var user = new User { Id = "delete-me", Name = "ToDelete", Email = "delete@test.com" };
        db.Users.Add(user);
        await db.SaveChangesAsync();

        // Act
        var response = await _client.DeleteAsync("/api/v1/users/delete-me");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NoContent);

        // Verify deleted
        var getResponse = await _client.GetAsync("/api/v1/users/delete-me");
        getResponse.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}

// =============================================================================
// Custom WebApplicationFactory
// =============================================================================

public class CustomWebApplicationFactory<TProgram> : WebApplicationFactory<TProgram>
    where TProgram : class
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // Replace real services with test doubles
            var dbDescriptor = services.SingleOrDefault(
                d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
            if (dbDescriptor != null)
            {
                services.Remove(dbDescriptor);
            }

            services.AddDbContext<AppDbContext>(options =>
                options.UseInMemoryDatabase("TestDb"));

            // Replace external service with mock
            // services.AddSingleton<IExternalService, MockExternalService>();
        });

        builder.UseEnvironment("Testing");
    }
}

// =============================================================================
// Database Integration Tests with Real Database
// =============================================================================

public class UserRepositoryIntegrationTests : IAsyncLifetime
{
    private AppDbContext _context = null!;

    public async Task InitializeAsync()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        _context = new AppDbContext(options);
        await _context.Database.EnsureCreatedAsync();
    }

    public async Task DisposeAsync()
    {
        await _context.DisposeAsync();
    }

    [Fact]
    public async Task AddUser_SavesUserToDatabase()
    {
        // Arrange
        var user = new User { Id = "1", Name = "Alice", Email = "alice@test.com" };

        // Act
        _context.Users.Add(user);
        await _context.SaveChangesAsync();

        // Assert
        var saved = await _context.Users.FindAsync("1");
        saved.Should().NotBeNull();
        saved!.Name.Should().Be("Alice");
    }

    [Fact]
    public async Task FindUser_ReturnsUserWhenExists()
    {
        // Arrange
        _context.Users.Add(new User { Id = "2", Name = "Bob", Email = "bob@test.com" });
        await _context.SaveChangesAsync();

        // Act
        var user = await _context.Users.FindAsync("2");

        // Assert
        user.Should().NotBeNull();
        user!.Email.Should().Be("bob@test.com");
    }

    [Fact]
    public async Task QueryUsers_WithLinq_ReturnsFilteredResults()
    {
        // Arrange
        _context.Users.AddRange(
            new User { Id = "3", Name = "Active1", Email = "a1@test.com" },
            new User { Id = "4", Name = "Active2", Email = "a2@test.com" },
            new User { Id = "5", Name = "Other", Email = "other@test.com" });
        await _context.SaveChangesAsync();

        // Act
        var activeUsers = await _context.Users
            .Where(u => u.Name.StartsWith("Active"))
            .ToListAsync();

        // Assert
        activeUsers.Should().HaveCount(2);
        activeUsers.Should().AllSatisfy(u => u.Name.Should().StartWith("Active"));
    }
}

// =============================================================================
// Test Fixture for Shared Database
// =============================================================================

public class SharedDatabaseFixture : IAsyncLifetime
{
    public AppDbContext Context { get; private set; } = null!;

    public async Task InitializeAsync()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase("SharedTestDb")
            .Options;

        Context = new AppDbContext(options);
        await Context.Database.EnsureCreatedAsync();
        await SeedDataAsync();
    }

    private async Task SeedDataAsync()
    {
        Context.Users.AddRange(
            new User { Id = "seed-1", Name = "Seeded User 1", Email = "seed1@test.com" },
            new User { Id = "seed-2", Name = "Seeded User 2", Email = "seed2@test.com" });
        await Context.SaveChangesAsync();
    }

    public async Task DisposeAsync()
    {
        await Context.DisposeAsync();
    }
}

// Usage with fixture
public class TestsWithSharedDatabase : IClassFixture<SharedDatabaseFixture>
{
    private readonly SharedDatabaseFixture _fixture;

    public TestsWithSharedDatabase(SharedDatabaseFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task Test_WithSeededData()
    {
        var user = await _fixture.Context.Users.FindAsync("seed-1");
        user.Should().NotBeNull();
        user!.Name.Should().Be("Seeded User 1");
    }
}

// Placeholder for Program class reference
// In real project, this would reference your actual Program class
public partial class Program { }

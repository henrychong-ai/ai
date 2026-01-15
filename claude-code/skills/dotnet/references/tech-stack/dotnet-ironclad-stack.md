# The Ironclad Stack: Universal .NET for Claude Code

A single, production-ready .NET stack optimized for AI-assisted development. Designed for compile-time safety, maximum Claude Code proficiency, and universal compatibility across all project types.

**Core Principle:** *One source of truth, compile-time validation, one set of tools.*

---

## Design Principles

### 1. Claude Code Optimization
Every technology choice prioritizes Claude's training data coverage. We use tools with the most documentation, examples, and community adoption to minimize hallucinations and maximize accurate code generation.

### 2. Compile-Time Safety
Entity Framework Core validates LINQ queries at compile time. Roslyn analyzers catch errors before runtime. Nullable reference types prevent entire categories of null-related bugs. Errors are caught by the compiler, not at 3am in production.

### 3. Universal Compatibility
The same core stack works for all project types: APIs, CLI tools, microservices, and background workers. Framework choices leverage .NET's unified platform; tooling stays consistent.

### 4. Multi-Developer + Multi-CC Stability
EditorConfig and analyzers enforce standards automatically. Roslyn catches errors before code review. Consistent tooling means any developer or CC instance can work on any project.

---

## The Universal Core Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Platform** | .NET 10+ | Current LTS, maximum CC training data |
| **Minimum Version** | .NET 8+ | LTS until Nov 2026 |
| **Language** | C# 14 (target), C# 12 (minimum) | Latest features with LTS fallback |
| **Web Framework** | ASP.NET Core Minimal APIs | Built-in, maximum training data, fast |
| **Database** | Entity Framework Core | LINQ compile-time safety, migrations |
| **Validation** | FluentValidation | Fluent syntax, complex rules, DI integration |
| **CLI** | System.CommandLine + Spectre.Console | Modern CLI, beautiful output |
| **Linting** | Roslyn Analyzers + .editorconfig | Built-in, configurable, IDE integration |
| **Formatting** | dotnet format | Built-in, .editorconfig-based |
| **Testing** | xUnit + FluentAssertions + Moq | Industry standard, expressive |
| **Microservices** | ASP.NET Core gRPC + Polly | Type-safe RPC, resilience |
| **Migrations** | EF Core Migrations | Code-first, version controlled |

---

## .NET Version Policy

### Version Requirements

| Context | Version | Rationale |
|---------|---------|-----------|
| **New projects** | .NET 10+ | Current LTS with all features |
| **Minimum supported** | .NET 8+ | LTS until November 2026 |

### Microsoft Release Cadence

Microsoft releases new .NET versions annually in November. LTS designation follows a fixed pattern:

| Pattern | Versions | Support Duration |
|---------|----------|------------------|
| **Even = LTS** | .NET 6, 8, 10, 12 | 3 years |
| **Odd = STS** | .NET 7, 9, 11 | 18 months |

### Current Support Schedule

| Version | Released | Support Ends | Status |
|---------|----------|--------------|--------|
| **.NET 10** | Nov 2025 | Nov 2028 | Current LTS (Recommended) |
| **.NET 9** | Nov 2024 | May 2026 | STS |
| **.NET 8** | Nov 2023 | Nov 2026 | LTS (Minimum) |
| **.NET 7** | Nov 2022 | May 2024 | End of Life |

### Why .NET 10+ Target, .NET 8+ Minimum

1. **.NET 10 (target)**: Latest LTS with C# 14, performance improvements, new APIs
2. **.NET 8 (minimum)**: Stable LTS for existing projects, supported until Nov 2026
3. **C# version alignment**: C# 14 with .NET 10, C# 12 with .NET 8

### Version Pinning

**global.json (recommended):**
```json
{
  "sdk": {
    "version": "10.0.100",
    "rollForward": "latestFeature"
  }
}
```

The `rollForward` policy ensures consistent SDK versions across all developers.

---

## Component Breakdown

### ASP.NET Core Minimal APIs (Web Framework)

**Role:** HTTP framework for APIs

**Why:**
- Built into .NET (no additional packages)
- Maximum Claude training data (official Microsoft approach)
- Fast performance (low overhead)
- Clean, functional syntax
- Native dependency injection
- OpenAPI support built-in

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/users/{id}", async (string id, IUserService userService) =>
{
    var user = await userService.GetByIdAsync(id);
    return user is not null
        ? Results.Ok(user)
        : Results.NotFound();
});

app.Run();
```

**Why not alternatives?**
| Framework | Issue |
|-----------|-------|
| Controllers | More boilerplate, less training data for new code |
| Carter | Third-party, less training data |
| FastEndpoints | Third-party, opinionated structure |

---

### Entity Framework Core (Database)

**Role:** ORM with LINQ-based queries

**Why:**
- LINQ queries validated at compile time
- Code-first migrations for version control
- No SQL string concatenation (injection protection)
- AI-generated queries caught at build time
- You see the generated SQL in logs

```csharp
// DbContext
public class AppDbContext : DbContext
{
    public DbSet<User> Users => Set<User>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Email).HasMaxLength(255);
            entity.HasIndex(e => e.Email).IsUnique();
        });
    }
}

// Repository pattern
public async Task<User?> GetByIdAsync(string id, CancellationToken ct = default)
{
    return await _context.Users
        .AsNoTracking()
        .FirstOrDefaultAsync(u => u.Id == id, ct);
}
```

**Why not alternatives?**
| ORM | Issue |
|-----|-------|
| Dapper | Raw SQL strings, runtime errors |
| ADO.NET | Too low-level, no compile-time safety |
| NHibernate | Less training data, complex configuration |

**When to use raw SQL:**
- Complex reporting queries
- Bulk operations for performance
- Database-specific features
- Always use parameterized queries

---

### FluentValidation (Validation)

**Role:** Input validation with fluent syntax

**Why:**
- Expressive, readable rules
- Dependency injection integration
- Complex validation scenarios
- Automatic ASP.NET Core integration
- Reusable validator classes

```csharp
public class CreateUserValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress()
            .MaximumLength(255);

        RuleFor(x => x.Name)
            .NotEmpty()
            .MinimumLength(1)
            .MaximumLength(100);

        RuleFor(x => x.Age)
            .InclusiveBetween(0, 150);
    }
}

// Registration
builder.Services.AddValidatorsFromAssemblyContaining<CreateUserValidator>();
```

**Why not just Data Annotations?**
| Aspect | FluentValidation | Data Annotations |
|--------|------------------|------------------|
| Complex rules | Easy | Difficult |
| Conditional validation | Built-in | Requires custom attributes |
| DI support | Full | Limited |
| Testability | Excellent | Good |
| Training data | High | High |

**Recommendation:** Use FluentValidation for complex rules, Data Annotations for simple DTOs.

---

### Roslyn Analyzers (Linting)

**Role:** Static code analysis

**Why:**
- Built into .NET SDK
- IDE integration (VS, Rider, VS Code)
- Configurable severity levels
- Custom analyzers possible
- Code fixes included

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest-recommended</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="10.0.0" />
    <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556" />
    <PackageReference Include="Roslynator.Analyzers" Version="4.12.0" />
  </ItemGroup>
</Project>
```

**Analyzer Packages:**
| Package | Purpose |
|---------|---------|
| Microsoft.CodeAnalysis.NetAnalyzers | Built-in .NET analyzers |
| StyleCop.Analyzers | Code style enforcement |
| Roslynator.Analyzers | Additional refactorings |
| SonarAnalyzer.CSharp | Security and quality |

---

### dotnet format (Formatting)

**Role:** Code formatting

**Why:**
- Built into .NET SDK
- Uses .editorconfig settings
- Deterministic output
- CI integration

```bash
dotnet format              # Format all files
dotnet format --verify-no-changes  # Check only (CI)
dotnet format whitespace   # Whitespace only
dotnet format style        # Code style only
dotnet format analyzers    # Analyzer fixes only
```

---

### xUnit + FluentAssertions + Moq (Testing)

**Role:** Testing framework

**Why xUnit:**
- Industry standard for .NET
- Parallel execution by default
- Constructor injection for setup
- IAsyncLifetime for async setup/teardown

**Why FluentAssertions:**
- Readable, expressive assertions
- Better error messages
- Fluent syntax matches C# style
- Extensive type support

**Why Moq:**
- Most popular .NET mocking library
- Maximum training data
- Expression-based setup
- Verification support

```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repositoryMock;
    private readonly UserService _sut;

    public UserServiceTests()
    {
        _repositoryMock = new Mock<IUserRepository>();
        _sut = new UserService(_repositoryMock.Object);
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
        result.Should().NotBeNull();
        result!.Name.Should().Be("Alice");
        _repositoryMock.Verify(
            r => r.GetByIdAsync("123", It.IsAny<CancellationToken>()),
            Times.Once);
    }
}
```

**Coverage requirements:** 80% minimum (enforced in CI)

---

### System.CommandLine + Spectre.Console (CLI)

**Role:** CLI framework and console output

**Why System.CommandLine:**
- Official Microsoft library
- Automatic help generation
- Tab completion
- Argument parsing and validation

**Why Spectre.Console:**
- Beautiful console output
- Tables, trees, progress bars
- Prompt support
- Cross-platform

```csharp
var rootCommand = new RootCommand("My CLI tool");

var nameOption = new Option<string>(
    name: "--name",
    description: "The name to greet")
{ IsRequired = true };

rootCommand.AddOption(nameOption);

rootCommand.SetHandler((name) =>
{
    AnsiConsole.MarkupLine($"[green]Hello, {name}![/]");
}, nameOption);

return await rootCommand.InvokeAsync(args);
```

---

### ASP.NET Core gRPC + Polly (Microservices)

**Role:** Type-safe RPC and resilience

**Why gRPC:**
- Protocol Buffers for schema
- Code generation for client/server
- High performance (HTTP/2)
- Streaming support

**Why Polly:**
- Resilience patterns (retry, circuit breaker, timeout)
- Fluent syntax
- DI integration
- Policy composition

```csharp
// Polly with HttpClientFactory
builder.Services
    .AddHttpClient<IExternalService, ExternalService>()
    .AddPolicyHandler(GetRetryPolicy())
    .AddPolicyHandler(GetCircuitBreakerPolicy());

static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .WaitAndRetryAsync(3, retryAttempt =>
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
}

static IAsyncPolicy<HttpResponseMessage> GetCircuitBreakerPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .CircuitBreakerAsync(5, TimeSpan.FromSeconds(30));
}
```

---

## Project-Type Configurations

### API / Microservice

| Layer | Technology |
|-------|------------|
| Framework | ASP.NET Core Minimal APIs |
| Database | Entity Framework Core + SQL Server/PostgreSQL |
| Validation | FluentValidation |
| Config | IConfiguration + Options pattern |

**Quick start:**
```bash
dotnet new web -o MyApi
cd MyApi
dotnet add package Microsoft.EntityFrameworkCore.SqlServer
dotnet add package FluentValidation.DependencyInjectionExtensions
dotnet add package Polly.Extensions.Http
```

---

### CLI Tool

| Layer | Technology |
|-------|------------|
| Framework | System.CommandLine |
| Output | Spectre.Console |
| Config | Microsoft.Extensions.Configuration |

**Quick start:**
```bash
dotnet new console -o MyCli
cd MyCli
dotnet add package System.CommandLine
dotnet add package Spectre.Console
```

---

### gRPC Microservice

| Layer | Technology |
|-------|------------|
| Framework | ASP.NET Core gRPC |
| Database | Entity Framework Core |
| Resilience | Polly |

**Quick start:**
```bash
dotnet new grpc -o MyService
cd MyService
dotnet add package Polly.Extensions.Http
dotnet add package Microsoft.EntityFrameworkCore.SqlServer
```

---

### Background Worker

| Layer | Technology |
|-------|------------|
| Framework | Worker Service |
| Queue | Channels / Azure Service Bus |
| Config | IConfiguration + Options pattern |

**Quick start:**
```bash
dotnet new worker -o MyWorker
cd MyWorker
dotnet add package Microsoft.Extensions.Hosting
```

---

## Decision Tree

```
What are you building?
│
├─► HTTP API?
│   └─► ASP.NET Core Minimal APIs + EF Core + SQL Server
│
├─► gRPC Microservice?
│   └─► ASP.NET Core gRPC + Polly + EF Core
│
├─► CLI Tool?
│   └─► System.CommandLine + Spectre.Console
│
├─► Background Worker?
│   └─► Worker Service + Channels
│
└─► Class Library?
    └─► .NET Standard 2.0 or .NET 8+ depending on consumers
```

---

## Standard Project Structure

```
MyProject/
├── src/
│   └── MyProject.Api/
│       ├── Program.cs                # Entry point
│       ├── Endpoints/                # API endpoints
│       │   └── UserEndpoints.cs
│       ├── Services/                 # Business logic
│       │   └── UserService.cs
│       ├── Data/                     # EF Core
│       │   ├── AppDbContext.cs
│       │   ├── Entities/
│       │   └── Migrations/
│       ├── Validators/               # FluentValidation
│       │   └── CreateUserValidator.cs
│       └── appsettings.json
├── tests/
│   ├── MyProject.Tests.Unit/
│   │   └── Services/
│   │       └── UserServiceTests.cs
│   └── MyProject.Tests.Integration/
│       └── Endpoints/
│           └── UserEndpointsTests.cs
├── Directory.Build.props             # Shared MSBuild properties
├── Directory.Packages.props          # Central package management
├── .editorconfig                     # Code style
├── global.json                       # SDK version
└── MyProject.sln
```

---

## Central Package Management

**Directory.Packages.props:**
```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <!-- Core -->
    <PackageVersion Include="Microsoft.EntityFrameworkCore.SqlServer" Version="10.0.0" />
    <PackageVersion Include="FluentValidation.DependencyInjectionExtensions" Version="11.9.0" />
    <PackageVersion Include="Polly.Extensions.Http" Version="3.0.0" />

    <!-- CLI -->
    <PackageVersion Include="System.CommandLine" Version="2.0.0" />
    <PackageVersion Include="Spectre.Console" Version="0.49.1" />

    <!-- Testing -->
    <PackageVersion Include="xunit" Version="2.9.0" />
    <PackageVersion Include="xunit.runner.visualstudio" Version="2.8.0" />
    <PackageVersion Include="FluentAssertions" Version="6.12.0" />
    <PackageVersion Include="Moq" Version="4.20.70" />
    <PackageVersion Include="Microsoft.AspNetCore.Mvc.Testing" Version="10.0.0" />
    <PackageVersion Include="coverlet.collector" Version="6.0.2" />

    <!-- Analyzers -->
    <PackageVersion Include="StyleCop.Analyzers" Version="1.2.0-beta.556" />
    <PackageVersion Include="Roslynator.Analyzers" Version="4.12.0" />
  </ItemGroup>
</Project>
```

---

## Summary

### The Ironclad Stack

```
Platform:           .NET 10+ (minimum .NET 8+)
Language:           C# 14 (minimum C# 12)
Web Framework:      ASP.NET Core Minimal APIs
Database:           Entity Framework Core
Validation:         FluentValidation + Data Annotations
CLI:                System.CommandLine + Spectre.Console
Microservices:      ASP.NET Core gRPC + Polly
Linting:            Roslyn Analyzers
Formatting:         dotnet format + .editorconfig
Testing:            xUnit + FluentAssertions + Moq
Coverage:           80% minimum
```

### Key Properties

- **Claude Code optimized:** Maximum training data coverage (official Microsoft stack)
- **Compile-time safe:** EF Core LINQ catches query errors, Roslyn catches code issues
- **Universal:** Works for APIs, CLIs, microservices, workers
- **Enforced:** EditorConfig and analyzers prevent violations
- **Single tool per category:** No alternatives, no decisions to make

### Companion Documents

| Document | Purpose |
|----------|---------|
| `dotnet-ironclad-infra.md` | Deployment and infrastructure guide |
| `../coding-standards/tooling.md` | Roslyn analyzer configuration |

---

*Last updated: 2026-01-15*

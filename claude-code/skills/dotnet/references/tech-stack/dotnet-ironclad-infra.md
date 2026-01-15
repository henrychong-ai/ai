# .NET Ironclad Infrastructure Guide

Deployment and infrastructure patterns for .NET applications using the Ironclad Stack.

---

## Deployment Models

### Framework-Dependent Deployment (FDD)

**Smallest binaries, requires .NET runtime on host.**

```bash
dotnet publish -c Release
```

Output: `~10-20 MB` depending on dependencies

**Use when:**
- Deploying to Azure App Service (runtime pre-installed)
- Container deployments with .NET base image
- Multiple apps sharing same runtime

---

### Self-Contained Deployment (SCD)

**Larger binaries, no runtime dependency.**

```bash
dotnet publish -c Release --self-contained -r linux-x64
```

Output: `~70-100 MB`

**Use when:**
- Target environment doesn't have .NET runtime
- Need specific runtime version isolation
- Deploying to bare metal servers

---

### Single-File Publish

**All dependencies in one executable.**

```bash
dotnet publish -c Release --self-contained -r linux-x64 \
  -p:PublishSingleFile=true \
  -p:IncludeNativeLibrariesForSelfExtract=true
```

Output: `~70-100 MB` single file

**Use when:**
- CLI tools for easy distribution
- Simplified deployment (one file copy)
- Docker scratch images

---

### Native AOT

**Ahead-of-time compilation for fastest startup.**

```bash
dotnet publish -c Release -r linux-x64 -p:PublishAot=true
```

Output: `~15-30 MB` with instant startup

**Limitations:**
- No reflection-based serialization
- Trimming may remove needed code
- Requires explicit rooting of types

**Use when:**
- Startup time critical (serverless, CLI)
- Memory constrained environments
- Maximum performance required

---

## Container Strategy

### Base Images

| Image | Size | Use Case |
|-------|------|----------|
| `mcr.microsoft.com/dotnet/aspnet:10.0` | ~220 MB | Runtime for web apps |
| `mcr.microsoft.com/dotnet/runtime:10.0` | ~190 MB | Runtime for console apps |
| `mcr.microsoft.com/dotnet/aspnet:10.0-alpine` | ~110 MB | Smaller runtime |
| `mcr.microsoft.com/dotnet/sdk:10.0` | ~800 MB | Build only |

### Multi-Stage Dockerfile (Recommended)

```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy csproj and restore
COPY ["src/MyApi/MyApi.csproj", "src/MyApi/"]
RUN dotnet restore "src/MyApi/MyApi.csproj"

# Copy everything and build
COPY . .
WORKDIR "/src/src/MyApi"
RUN dotnet build "MyApi.csproj" -c Release -o /app/build

# Publish stage
FROM build AS publish
RUN dotnet publish "MyApi.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:10.0-alpine AS final
WORKDIR /app

# Security: Run as non-root user
RUN adduser -D appuser
USER appuser

COPY --from=publish /app/publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
ENTRYPOINT ["dotnet", "MyApi.dll"]
```

### Alpine Variants

Smaller images with musl libc instead of glibc.

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:10.0-alpine
```

**Considerations:**
- Smaller attack surface
- May have compatibility issues with native libraries
- Test thoroughly before production

### Distroless (Google)

Minimal images without shell or package manager.

```dockerfile
FROM mcr.microsoft.com/dotnet/runtime-deps:10.0-jammy-chiseled AS final
```

**Benefits:**
- Smallest possible image
- No shell for attackers
- Reduced CVE surface

---

## Cloud Deployment

### Azure

| Service | Use Case | .NET Support |
|---------|----------|--------------|
| **App Service** | Web APIs, simple deployment | Excellent |
| **Azure Functions** | Serverless, event-driven | Excellent (.NET 10 in-process) |
| **Container Apps** | Containers, auto-scaling | Excellent |
| **AKS** | Kubernetes, complex workloads | Excellent |

**App Service Deployment:**
```bash
# Via Azure CLI
az webapp up --name myapi --resource-group myrg --runtime "DOTNET:10.0"

# Via GitHub Actions
- uses: azure/webapps-deploy@v3
  with:
    app-name: 'myapi'
    package: './publish'
```

**Azure Functions:**
```csharp
public class MyFunction
{
    [Function("HttpTrigger")]
    public IActionResult Run(
        [HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequest req)
    {
        return new OkObjectResult("Hello from Azure Functions");
    }
}
```

---

### AWS

| Service | Use Case | .NET Support |
|---------|----------|--------------|
| **ECS** | Container orchestration | Excellent |
| **Lambda** | Serverless | Good (.NET 8 runtime) |
| **App Runner** | Simple containers | Excellent |
| **EKS** | Kubernetes | Excellent |

**ECS Task Definition:**
```json
{
  "family": "myapi",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "myregistry/myapi:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ASPNETCORE_ENVIRONMENT",
          "value": "Production"
        }
      ]
    }
  ]
}
```

**Lambda with .NET:**
```csharp
public class Function
{
    public APIGatewayProxyResponse Handler(
        APIGatewayProxyRequest request,
        ILambdaContext context)
    {
        return new APIGatewayProxyResponse
        {
            StatusCode = 200,
            Body = "Hello from Lambda"
        };
    }
}
```

---

## Health Checks

### ASP.NET Core Health Checks

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("database")
    .AddRedis(connectionString, "redis")
    .AddUrlGroup(new Uri("https://api.example.com/health"), "external-api");

var app = builder.Build();

app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

app.MapHealthChecks("/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Configuration

### Configuration Hierarchy

```
1. appsettings.json (base)
2. appsettings.{Environment}.json (environment-specific)
3. Environment variables
4. Command-line arguments
5. User secrets (development only)
6. Azure Key Vault / AWS Secrets Manager (production)
```

### Options Pattern

```csharp
// Configuration class
public class DatabaseOptions
{
    public const string SectionName = "Database";
    public string ConnectionString { get; init; } = string.Empty;
    public int CommandTimeout { get; init; } = 30;
}

// Registration
builder.Services.Configure<DatabaseOptions>(
    builder.Configuration.GetSection(DatabaseOptions.SectionName));

// Usage
public class UserService
{
    private readonly DatabaseOptions _options;

    public UserService(IOptions<DatabaseOptions> options)
    {
        _options = options.Value;
    }
}
```

### User Secrets (Development)

```bash
dotnet user-secrets init
dotnet user-secrets set "Database:ConnectionString" "Server=..."
```

### Azure Key Vault

```csharp
builder.Configuration.AddAzureKeyVault(
    new Uri($"https://{keyVaultName}.vault.azure.net/"),
    new DefaultAzureCredential());
```

### AWS Secrets Manager

```csharp
builder.Configuration.AddSecretsManager(configurator: options =>
{
    options.SecretFilter = entry => entry.Name.StartsWith("MyApp");
    options.KeyGenerator = (entry, key) => key.Replace("__", ":");
});
```

---

## Logging & Observability

### Structured Logging

```csharp
builder.Host.UseSerilog((context, config) =>
{
    config
        .ReadFrom.Configuration(context.Configuration)
        .Enrich.FromLogContext()
        .Enrich.WithMachineName()
        .WriteTo.Console(new JsonFormatter())
        .WriteTo.Seq("http://seq:5341");
});

// Usage
_logger.LogInformation("User {UserId} created order {OrderId}", userId, orderId);
```

### OpenTelemetry

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing =>
    {
        tracing
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddEntityFrameworkCoreInstrumentation()
            .AddOtlpExporter();
    })
    .WithMetrics(metrics =>
    {
        metrics
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddOtlpExporter();
    });
```

---

## CI/CD Patterns

### GitHub Actions

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      - name: Restore
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore -c Release

      - name: Test
        run: dotnet test --no-build -c Release --collect:"XPlat Code Coverage"

      - name: Publish
        run: dotnet publish -c Release -o ./publish

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: app
          path: ./publish
```

### Azure DevOps Pipeline

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  buildConfiguration: 'Release'

steps:
  - task: UseDotNet@2
    inputs:
      version: '10.0.x'

  - script: dotnet build --configuration $(buildConfiguration)
    displayName: 'Build'

  - script: dotnet test --configuration $(buildConfiguration) --collect:"XPlat Code Coverage"
    displayName: 'Test'

  - task: PublishCodeCoverageResults@1
    inputs:
      codeCoverageTool: 'Cobertura'
      summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'
```

---

## Security Considerations

### Production Checklist

- [ ] HTTPS enforced with `UseHttpsRedirection()`
- [ ] HSTS enabled with `UseHsts()`
- [ ] Security headers configured (CSP, X-Frame-Options)
- [ ] Secrets in Key Vault / Secrets Manager (not appsettings)
- [ ] Non-root container user
- [ ] Minimal base image (Alpine or distroless)
- [ ] Health check endpoints exposed
- [ ] Structured logging enabled
- [ ] OpenTelemetry for observability

### Environment Variables

```bash
# Never commit these - use secrets management
ASPNETCORE_ENVIRONMENT=Production
ConnectionStrings__DefaultConnection=<from-secrets>
Jwt__Secret=<from-secrets>
```

---

## Summary

| Deployment | Binary Size | Startup | Best For |
|------------|-------------|---------|----------|
| FDD | ~10-20 MB | Fast | Azure App Service, containers |
| SCD | ~70-100 MB | Fast | Bare metal, isolated runtime |
| Single-File | ~70-100 MB | Fast | CLI tools, simple deployment |
| Native AOT | ~15-30 MB | Instant | Serverless, memory-constrained |

**Container Recommendation:**
- Use multi-stage builds
- Alpine for smaller images
- Run as non-root user
- Use health checks

**Cloud Recommendation:**
- Azure: App Service or Container Apps
- AWS: ECS or App Runner
- Use managed secrets services
- Enable observability from day one

---

*Last updated: 2026-01-15*

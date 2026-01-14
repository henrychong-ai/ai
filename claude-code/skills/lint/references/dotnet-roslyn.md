# .NET Linting with Roslyn Analyzers

.NET uses Roslyn analyzers for linting and `dotnet format` for formatting.

## Setup

### Install Analyzer Packages

Add to your `.csproj`:
```xml
<ItemGroup>
  <PackageReference Include="Roslynator.Analyzers" Version="4.12.0">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>
  <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>
  <PackageReference Include="SonarAnalyzer.CSharp" Version="9.32.0.97167">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>
</ItemGroup>
```

Or via CLI:
```bash
dotnet add package Roslynator.Analyzers
dotnet add package StyleCop.Analyzers
dotnet add package SonarAnalyzer.CSharp
```

### Enable Strict Analysis in .csproj
```xml
<PropertyGroup>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <WarningsAsErrors />
  <NoWarn />
  <AnalysisLevel>latest-all</AnalysisLevel>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  <EnableNETAnalyzers>true</EnableNETAnalyzers>
</PropertyGroup>
```

## Configuration (.editorconfig)

### Comprehensive Strict Config
```ini
# Top-level EditorConfig
root = true

# All files
[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

# C# files
[*.cs]
indent_size = 4

# ---------------------------
# Language Conventions
# ---------------------------

# Use 'var' everywhere
csharp_style_var_for_built_in_types = true:suggestion
csharp_style_var_when_type_is_apparent = true:suggestion
csharp_style_var_elsewhere = true:suggestion

# Prefer expression-bodied members
csharp_style_expression_bodied_methods = when_on_single_line:suggestion
csharp_style_expression_bodied_constructors = false:suggestion
csharp_style_expression_bodied_operators = when_on_single_line:suggestion
csharp_style_expression_bodied_properties = true:suggestion
csharp_style_expression_bodied_indexers = true:suggestion
csharp_style_expression_bodied_accessors = true:suggestion
csharp_style_expression_bodied_lambdas = true:suggestion
csharp_style_expression_bodied_local_functions = false:suggestion

# Pattern matching
csharp_style_pattern_matching_over_is_with_cast_check = true:warning
csharp_style_pattern_matching_over_as_with_null_check = true:warning
csharp_style_prefer_switch_expression = true:suggestion
csharp_style_prefer_pattern_matching = true:suggestion
csharp_style_prefer_not_pattern = true:suggestion

# Null checking
csharp_style_throw_expression = true:suggestion
csharp_style_conditional_delegate_call = true:suggestion
csharp_style_prefer_null_check_over_type_check = true:suggestion
dotnet_style_coalesce_expression = true:suggestion
dotnet_style_null_propagation = true:suggestion

# Code block preferences
csharp_prefer_braces = true:warning
csharp_prefer_simple_using_statement = true:suggestion
csharp_style_namespace_declarations = file_scoped:warning
csharp_style_prefer_top_level_statements = false:suggestion

# ---------------------------
# Formatting Rules
# ---------------------------

# Indentation
csharp_indent_case_contents = true
csharp_indent_switch_labels = true
csharp_indent_labels = one_less_than_current
csharp_indent_block_contents = true
csharp_indent_braces = false

# New lines
csharp_new_line_before_open_brace = all
csharp_new_line_before_else = true
csharp_new_line_before_catch = true
csharp_new_line_before_finally = true
csharp_new_line_before_members_in_object_initializers = true
csharp_new_line_before_members_in_anonymous_types = true
csharp_new_line_between_query_expression_clauses = true

# Spacing
csharp_space_after_cast = false
csharp_space_after_keywords_in_control_flow_statements = true
csharp_space_between_parentheses = false
csharp_space_before_colon_in_inheritance_clause = true
csharp_space_after_colon_in_inheritance_clause = true
csharp_space_around_binary_operators = before_and_after

# ---------------------------
# Naming Conventions
# ---------------------------

# PascalCase for public members
dotnet_naming_rule.public_members_should_be_pascal_case.severity = warning
dotnet_naming_rule.public_members_should_be_pascal_case.symbols = public_symbols
dotnet_naming_rule.public_members_should_be_pascal_case.style = pascal_case

dotnet_naming_symbols.public_symbols.applicable_kinds = property,method,field,event,delegate
dotnet_naming_symbols.public_symbols.applicable_accessibilities = public

dotnet_naming_style.pascal_case.capitalization = pascal_case

# camelCase for private fields
dotnet_naming_rule.private_fields_should_be_camel_case.severity = warning
dotnet_naming_rule.private_fields_should_be_camel_case.symbols = private_fields
dotnet_naming_rule.private_fields_should_be_camel_case.style = camel_case

dotnet_naming_symbols.private_fields.applicable_kinds = field
dotnet_naming_symbols.private_fields.applicable_accessibilities = private

dotnet_naming_style.camel_case.capitalization = camel_case

# _camelCase for private fields (alternative)
dotnet_naming_rule.private_fields_should_be_underscore_camel.severity = suggestion
dotnet_naming_rule.private_fields_should_be_underscore_camel.symbols = private_fields
dotnet_naming_rule.private_fields_should_be_underscore_camel.style = underscore_camel

dotnet_naming_style.underscore_camel.capitalization = camel_case
dotnet_naming_style.underscore_camel.required_prefix = _

# Interfaces start with I
dotnet_naming_rule.interfaces_should_start_with_i.severity = error
dotnet_naming_rule.interfaces_should_start_with_i.symbols = interfaces
dotnet_naming_rule.interfaces_should_start_with_i.style = interface_style

dotnet_naming_symbols.interfaces.applicable_kinds = interface

dotnet_naming_style.interface_style.capitalization = pascal_case
dotnet_naming_style.interface_style.required_prefix = I

# ---------------------------
# Analyzer Severity
# ---------------------------

# .NET Analyzers
dotnet_analyzer_diagnostic.severity = warning

# Critical rules as errors
dotnet_diagnostic.CA1062.severity = error  # Validate arguments
dotnet_diagnostic.CA2007.severity = error  # ConfigureAwait
dotnet_diagnostic.CA2016.severity = error  # Forward CancellationToken
dotnet_diagnostic.CA2254.severity = error  # Template should be static
dotnet_diagnostic.CA1848.severity = warning # Use LoggerMessage delegates

# StyleCop rules
dotnet_diagnostic.SA1101.severity = none   # Prefix local calls with this (disabled)
dotnet_diagnostic.SA1200.severity = none   # Using directives placement
dotnet_diagnostic.SA1309.severity = none   # Field names must not begin with underscore
dotnet_diagnostic.SA1633.severity = none   # File must have header

# Roslynator rules
dotnet_diagnostic.RCS1036.severity = warning # Remove redundant empty line
dotnet_diagnostic.RCS1037.severity = warning # Remove trailing whitespace
dotnet_diagnostic.RCS1090.severity = warning # ConfigureAwait
```

## Commands

```bash
# Format all code
dotnet format

# Format specific project
dotnet format ./MyProject.csproj

# Check formatting (CI)
dotnet format --verify-no-changes

# Format only whitespace
dotnet format whitespace

# Format only style
dotnet format style

# Format only analyzers
dotnet format analyzers

# Build with warnings as errors
dotnet build /warnaserror

# Run analyzers without building
dotnet build --no-incremental
```

## Key Analyzer Packages

### Roslynator (500+ rules)
- Code fixes and refactorings
- Code style enforcement
- Code quality rules

### StyleCop.Analyzers
- Code style consistency
- Documentation rules
- Layout rules

### SonarAnalyzer.CSharp
- Security vulnerabilities
- Bug detection
- Code smells

### Microsoft.CodeAnalysis.NetAnalyzers
- .NET SDK built-in analyzers
- API usage rules
- Performance rules

## CI/CD Integration

### GitHub Actions
```yaml
name: Lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'

      - name: Check formatting
        run: dotnet format --verify-no-changes

      - name: Build with warnings as errors
        run: dotnet build --warnaserror
```

### Azure DevOps
```yaml
steps:
  - task: DotNetCoreCLI@2
    inputs:
      command: 'custom'
      custom: 'format'
      arguments: '--verify-no-changes'
    displayName: 'Check formatting'

  - task: DotNetCoreCLI@2
    inputs:
      command: 'build'
      arguments: '/warnaserror'
    displayName: 'Build with strict warnings'
```

## Pre-commit Integration

### With Husky.Net
```bash
dotnet tool install --global Husky
dotnet husky install
dotnet husky add pre-commit -c "dotnet format --verify-no-changes"
```

### Package.json (for monorepos)
```json
{
  "lint-staged": {
    "*.cs": ["dotnet format --include"]
  }
}
```

## Troubleshooting

### Analyzers Not Running
Ensure packages have correct metadata:
```xml
<PackageReference Include="Roslynator.Analyzers" Version="4.12.0">
  <PrivateAssets>all</PrivateAssets>
  <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
</PackageReference>
```

### Too Many Warnings
Start with minimal severity, increase gradually:
```ini
# Start relaxed
dotnet_analyzer_diagnostic.severity = suggestion

# Increase specific rules
dotnet_diagnostic.CA1062.severity = warning
```

### Format Not Applying
Check `.editorconfig` is in the right location (solution root) and has `root = true`.

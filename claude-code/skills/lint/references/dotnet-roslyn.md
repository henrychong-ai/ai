# .NET Linting with Roslyn Analyzers

.NET uses Roslyn analyzers for linting and `dotnet format` for formatting.

> Where the `/dotnet` skill is installed, its `references/coding-standards/tooling.md` holds the full .NET conventions (complete `.editorconfig`, IDE settings, CPM); this file follows it and adds the opt-in strict profile and a few Roslynator severities.

**Scope:** SDK-style C# projects on modern .NET (10+). Repository configuration takes precedence over these defaults.

## Setup

### Analysis Settings (Directory.Build.props)

The .NET SDK ships the first-party CA (quality) and IDE (style) analyzers; no `Microsoft.CodeAnalysis.NetAnalyzers` package is needed unless you want a newer analyzer version than the installed SDK provides.

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>

    <AnalysisLevel>latest-recommended</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>

    <!-- Required for IDE0005 (unnecessary usings) to report on build; CS1591 keeps undocumented members from failing it -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <NoWarn>$(NoWarn);CS1591</NoWarn>
  </PropertyGroup>
</Project>
```

Leave `LangVersion` unset (the compiler picks the default for each target framework).

| `AnalysisLevel` | Effect |
|-----------------|--------|
| `latest` (default) | SDK default: a small set of rules as build warnings |
| `latest-minimum` | Default plus a few rules highly recommended for build enforcement |
| `latest-recommended` | **Default here.** More rules as build warnings; recommended starting point |
| `latest-all` | Every rule as a build warning (opt-in strict profile, below) |
| `10.0-recommended` (etc.) | Pins the rule set so an SDK upgrade never adds new warnings |

### Strict Profile (opt-in)

`latest-all` with `TreatWarningsAsErrors` turns every CA rule into a build error. Adopt it deliberately, rule by rule, not as a starting default:

```xml
<PropertyGroup>
  <AnalysisLevel>latest-all</AnalysisLevel>
</PropertyGroup>
```

Even under the strict profile, keep CA2007 (ConfigureAwait) scoped to library projects (see [CA2007 Scoping](#ca2007-configureawait-scoping)).

### Analyzer Packages (Central Package Management)

Declare third-party analyzers once as `GlobalPackageReference` in `Directory.Packages.props`. They apply to every project and are private assets automatically. With Central Package Management, never put `Version=` on a `PackageReference` (NU1008, a build error under `TreatWarningsAsErrors`).

```xml
<!-- Directory.Packages.props -->
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <!-- Versions current at 2026-09-28; update deliberately -->
    <GlobalPackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556" />
    <GlobalPackageReference Include="Roslynator.Analyzers" Version="5.0.0" />
    <GlobalPackageReference Include="SonarAnalyzer.CSharp" Version="10.34.0.3385" />
  </ItemGroup>

  <ItemGroup>
    <!-- Regular dependencies: versions here; projects use <PackageReference Include="..." /> without Version -->
    <PackageVersion Include="FluentValidation" Version="12.1.1" />
  </ItemGroup>
</Project>
```

Roslynator 5.0 is a new major version; check its release notes for renamed or removed rules before upgrading from 4.x.

**Without CPM** (a repo not yet migrated), reference each analyzer in the project with a version and `<PrivateAssets>all</PrivateAssets>`; migrate to CPM when practical.

## Configuration (.editorconfig)

One `.editorconfig` at the solution root with `root = true`. Nested `.editorconfig` files (without `root = true`, so they inherit the rest) are only for scoped overrides such as CA2007 in libraries. The condensed config below matches `/dotnet` `tooling.md`; take the full template from there.

```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{xml,csproj,props,targets,slnx,json,yml,yaml}]
indent_size = 2

[*.cs]
# Using directives
dotnet_sort_system_directives_first = true
csharp_using_directive_placement = outside_namespace:warning

# Modifiers
dotnet_style_require_accessibility_modifiers = for_non_interface_members:warning
dotnet_style_readonly_field = true:warning
csharp_preferred_modifier_order = public,private,protected,internal,file,static,extern,new,virtual,abstract,sealed,override,readonly,unsafe,required,volatile,async:suggestion

# var
csharp_style_var_for_built_in_types = true:suggestion
csharp_style_var_when_type_is_apparent = true:warning
csharp_style_var_elsewhere = true:suggestion

# Expression-bodied members
csharp_style_expression_bodied_methods = when_on_single_line:suggestion
csharp_style_expression_bodied_constructors = false:suggestion
csharp_style_expression_bodied_operators = when_on_single_line:suggestion
csharp_style_expression_bodied_properties = true:warning
csharp_style_expression_bodied_indexers = true:warning
csharp_style_expression_bodied_accessors = true:warning
csharp_style_expression_bodied_lambdas = true:suggestion
csharp_style_expression_bodied_local_functions = when_on_single_line:suggestion

# Pattern matching
csharp_style_pattern_matching_over_is_with_cast_check = true:warning
csharp_style_pattern_matching_over_as_with_null_check = true:warning
csharp_style_prefer_switch_expression = true:suggestion
csharp_style_prefer_pattern_matching = true:suggestion
csharp_style_prefer_not_pattern = true:warning

# Null checking
csharp_style_throw_expression = true:warning
csharp_style_conditional_delegate_call = true:warning
csharp_style_prefer_null_check_over_type_check = true:warning
dotnet_style_coalesce_expression = true:warning
dotnet_style_null_propagation = true:warning

# Code blocks and namespaces
csharp_prefer_braces = true:warning
csharp_prefer_simple_using_statement = true:suggestion
csharp_style_namespace_declarations = file_scoped:warning
csharp_style_prefer_primary_constructors = true:suggestion
csharp_style_prefer_top_level_statements = true:suggestion

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

# Naming
dotnet_naming_rule.interface_should_be_begins_with_i.severity = warning
dotnet_naming_rule.interface_should_be_begins_with_i.symbols = interface
dotnet_naming_rule.interface_should_be_begins_with_i.style = begins_with_i

dotnet_naming_rule.types_should_be_pascal_case.severity = warning
dotnet_naming_rule.types_should_be_pascal_case.symbols = types
dotnet_naming_rule.types_should_be_pascal_case.style = pascal_case

dotnet_naming_rule.private_or_internal_field_should_be_underscore_camel_case.severity = warning
dotnet_naming_rule.private_or_internal_field_should_be_underscore_camel_case.symbols = private_or_internal_field
dotnet_naming_rule.private_or_internal_field_should_be_underscore_camel_case.style = underscore_camel_case

dotnet_naming_rule.async_methods_should_end_with_async.severity = warning
dotnet_naming_rule.async_methods_should_end_with_async.symbols = async_methods
dotnet_naming_rule.async_methods_should_end_with_async.style = end_with_async

dotnet_naming_symbols.interface.applicable_kinds = interface
dotnet_naming_symbols.interface.applicable_accessibilities = public, internal, private, protected, protected_internal, private_protected

dotnet_naming_symbols.types.applicable_kinds = class, struct, interface, enum
dotnet_naming_symbols.types.applicable_accessibilities = public, internal, private, protected, protected_internal, private_protected

dotnet_naming_symbols.private_or_internal_field.applicable_kinds = field
dotnet_naming_symbols.private_or_internal_field.applicable_accessibilities = private, internal

dotnet_naming_symbols.async_methods.applicable_kinds = method
dotnet_naming_symbols.async_methods.applicable_accessibilities = *
dotnet_naming_symbols.async_methods.required_modifiers = async

dotnet_naming_style.pascal_case.capitalization = pascal_case

dotnet_naming_style.begins_with_i.required_prefix = I
dotnet_naming_style.begins_with_i.capitalization = pascal_case

dotnet_naming_style.underscore_camel_case.required_prefix = _
dotnet_naming_style.underscore_camel_case.capitalization = camel_case

dotnet_naming_style.end_with_async.required_suffix = Async
dotnet_naming_style.end_with_async.capitalization = pascal_case

# Analyzer rules
dotnet_diagnostic.CA1062.severity = none  # Argument validation: covered by nullable reference types
dotnet_diagnostic.CA1303.severity = none  # Localisation of literals not required
dotnet_diagnostic.CA1812.severity = none  # Internal classes instantiated via DI
dotnet_diagnostic.CA2007.severity = none  # ConfigureAwait: enabled per library project (see below)
dotnet_diagnostic.CS1591.severity = none  # XML comments optional

# StyleCop rules
dotnet_diagnostic.SA1101.severity = none  # this. prefix not required
dotnet_diagnostic.SA1200.severity = none  # Using placement governed by IDE0065 (outside namespace)
dotnet_diagnostic.SA1309.severity = none  # Fields may start with underscore
dotnet_diagnostic.SA1413.severity = none  # Trailing comma optional
dotnet_diagnostic.SA1600.severity = none  # Documentation optional
dotnet_diagnostic.SA1633.severity = none  # File header optional

# Roslynator rules
dotnet_diagnostic.RCS1036.severity = warning  # Remove unnecessary blank line
dotnet_diagnostic.RCS1037.severity = warning  # Remove trailing white-space
dotnet_diagnostic.RCS1090.severity = none     # ConfigureAwait: same scoping as CA2007

# Test projects: descriptive test names with underscores
[tests/**.cs]
dotnet_diagnostic.CA1707.severity = none
```

### Strict-profile additions (optional)

Add these only alongside `latest-all`, and only once the codebase is clean against them:

```ini
[*.cs]
dotnet_diagnostic.CA2016.severity = error    # Forward CancellationToken
dotnet_diagnostic.CA2254.severity = error    # Logging template should be static
dotnet_diagnostic.CA1848.severity = warning  # Use LoggerMessage delegates
```

### CA2007 (ConfigureAwait) Scoping

Off at the solution root for applications and tests: ASP.NET Core has no `SynchronizationContext`, and xUnit's analyzer (xUnit1030) flags `ConfigureAwait(false)` in tests. Reusable libraries consumed by UI or unknown hosts opt in with a nested `.editorconfig`:

```ini
# src/MyProduct.Client/.editorconfig  (no root = true: inherits the solution config)
[*.cs]
dotnet_diagnostic.CA2007.severity = warning
```

## Commands

```bash
# Format all code (whitespace, style, analyzer fixes)
dotnet format

# Format specific project
dotnet format ./MyProject.csproj

# Check formatting (CI)
dotnet format --verify-no-changes

# Individual passes
dotnet format whitespace
dotnet format style
dotnet format analyzers

# Build (analyzers run as part of every build)
dotnet build

# Build with warnings as errors (when not already set in Directory.Build.props)
dotnet build -warnaserror

# Full rebuild: re-reports analyzer diagnostics for files unchanged since the last build
dotnet build --no-incremental
```

## Key Analyzer Packages

### Built-in (.NET SDK)
- CA quality rules and IDE style rules; no package reference needed
- Level set by `AnalysisLevel`

### Roslynator.Analyzers (500+ rules)
- Code fixes and refactorings
- Code style and quality rules

### StyleCop.Analyzers
- Layout, ordering, and documentation rules
- 1.2 is a long-running prerelease line; pin deliberately

### SonarAnalyzer.CSharp
- Bug patterns, security hotspots, code smells

### Microsoft.VisualStudio.Threading.Analyzers (optional)
- VSTHRD threading rules; aimed at Visual Studio extensions and UI apps, noisy in ASP.NET Core

## CI/CD Integration

Run the formatting gate and the build (with `TreatWarningsAsErrors` from `Directory.Build.props`) as separate steps.

### GitHub Actions
```yaml
name: Lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-dotnet@v6
        with:
          dotnet-version: '10.0.x'

      - name: Check formatting
        run: dotnet format --verify-no-changes

      - name: Build (analyzers, warnings as errors)
        run: dotnet build -warnaserror
```

### Azure DevOps
```yaml
steps:
  - task: UseDotNet@2
    inputs:
      version: '10.0.x'

  - script: dotnet format --verify-no-changes
    displayName: 'Check formatting'

  - script: dotnet build -warnaserror
    displayName: 'Build (analyzers, warnings as errors)'
```

## Pre-commit Integration

### With Husky.Net (local tool)
```bash
dotnet new tool-manifest   # once per repo, if .config/dotnet-tools.json does not exist
dotnet tool install Husky
dotnet husky install
dotnet husky add pre-commit -c "dotnet format --verify-no-changes"
```

### lint-staged (for monorepos)
```json
{
  "lint-staged": {
    "*.cs": ["dotnet format --include"]
  }
}
```

## Troubleshooting

### Analyzers Not Running
- With CPM: confirm the analyzer is a `GlobalPackageReference` in `Directory.Packages.props` and `ManagePackageVersionsCentrally` is `true`.
- Without CPM: the `PackageReference` needs `<PrivateAssets>all</PrivateAssets>` and default `IncludeAssets` (analyzers included).
- IDE style rules only fail the build with `EnforceCodeStyleInBuild`; IDE0005 also needs `GenerateDocumentationFile`.

### NU1008 Build Error
A `PackageReference` has `Version=` while Central Package Management is on. Move the version to a `PackageVersion` item in `Directory.Packages.props`.

### Too Many Warnings
Start from `latest-recommended` (or pin `10.0-recommended`), then raise individual rules:
```ini
dotnet_diagnostic.CA1822.severity = warning  # Mark members as static
```
Move to `latest-all` only as a deliberate strict-profile decision.

### Format Not Applying
Check the solution-root `.editorconfig` has `root = true`, and that nested `.editorconfig` files do not (a nested `root = true` stops inheritance from the solution config).

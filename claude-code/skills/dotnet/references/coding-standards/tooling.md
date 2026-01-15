# .NET Tooling Guide

Roslyn analyzers, .editorconfig, and IDE integration for consistent code quality.

---

## Roslyn Analyzers

### Built-in Analyzers

.NET SDK includes analyzers by default. Enable strict mode:

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>

    <!-- Analyzer settings -->
    <AnalysisLevel>latest-recommended</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>

    <!-- Specific warning levels -->
    <WarningLevel>9999</WarningLevel>
    <NoWarn>$(NoWarn);CS1591</NoWarn> <!-- Missing XML comments -->
  </PropertyGroup>
</Project>
```

### Analysis Levels

| Level | Description |
|-------|-------------|
| `latest` | All analyzers at informational level |
| `latest-minimum` | Only critical analyzers |
| `latest-recommended` | Recommended analyzers at warning level |
| `latest-all` | All analyzers at warning level |

### Recommended Analyzer Packages

```xml
<!-- Directory.Build.props -->
<ItemGroup>
  <!-- Microsoft analyzers (included in SDK) -->
  <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="10.0.0" />

  <!-- Code style enforcement -->
  <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>

  <!-- Additional refactorings -->
  <PackageReference Include="Roslynator.Analyzers" Version="4.12.0">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>

  <!-- Security analyzers -->
  <PackageReference Include="SonarAnalyzer.CSharp" Version="9.32.0">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>

  <!-- Async best practices -->
  <PackageReference Include="Microsoft.VisualStudio.Threading.Analyzers" Version="17.10.48">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>
</ItemGroup>
```

### Suppressing Warnings

```csharp
// File-level suppression
#pragma warning disable CA1822 // Mark members as static
public void MyMethod() { }
#pragma warning restore CA1822

// Method-level suppression
[SuppressMessage("Performance", "CA1822:Mark members as static", Justification = "Required for DI")]
public void MyMethod() { }

// Assembly-level suppression (GlobalSuppressions.cs)
[assembly: SuppressMessage("Design", "CA1062:Validate arguments of public methods", Scope = "namespaceanddescendants", Target = "~N:MyProject.Tests")]
```

### Custom Analyzer Rules

```xml
<!-- .editorconfig (preferred) or GlobalAnalyzerConfig.globalconfig -->

# CA1062: Validate arguments of public methods - disabled (handled by NRT)
dotnet_diagnostic.CA1062.severity = none

# CA1303: Do not pass literals as localized parameters
dotnet_diagnostic.CA1303.severity = suggestion

# CA2007: Consider calling ConfigureAwait on awaited tasks
dotnet_diagnostic.CA2007.severity = warning
```

---

## .editorconfig

### Complete .editorconfig Template

```ini
# EditorConfig for .NET projects
# https://editorconfig.org

root = true

# All files
[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

# XML files
[*.{xml,csproj,props,targets}]
indent_size = 2

# JSON files
[*.json]
indent_size = 2

# YAML files
[*.{yml,yaml}]
indent_size = 2

# Markdown files
[*.md]
trim_trailing_whitespace = false

# C# files
[*.cs]
# Language conventions
dotnet_sort_system_directives_first = true
dotnet_separate_import_directive_groups = false

# this. preferences
dotnet_style_qualification_for_field = false:warning
dotnet_style_qualification_for_property = false:warning
dotnet_style_qualification_for_method = false:warning
dotnet_style_qualification_for_event = false:warning

# Language keywords vs BCL types
dotnet_style_predefined_type_for_locals_parameters_members = true:warning
dotnet_style_predefined_type_for_member_access = true:warning

# Parentheses preferences
dotnet_style_parentheses_in_arithmetic_binary_operators = always_for_clarity:suggestion
dotnet_style_parentheses_in_relational_binary_operators = always_for_clarity:suggestion
dotnet_style_parentheses_in_other_binary_operators = always_for_clarity:suggestion
dotnet_style_parentheses_in_other_operators = never_if_unnecessary:suggestion

# Modifier preferences
dotnet_style_require_accessibility_modifiers = for_non_interface_members:warning
dotnet_style_readonly_field = true:warning

# Expression-level preferences
dotnet_style_object_initializer = true:warning
dotnet_style_collection_initializer = true:warning
dotnet_style_explicit_tuple_names = true:warning
dotnet_style_null_propagation = true:warning
dotnet_style_coalesce_expression = true:warning
dotnet_style_prefer_is_null_check_over_reference_equality_method = true:warning
dotnet_style_prefer_inferred_tuple_names = true:suggestion
dotnet_style_prefer_inferred_anonymous_type_member_names = true:suggestion
dotnet_style_prefer_auto_properties = true:warning
dotnet_style_prefer_conditional_expression_over_assignment = true:suggestion
dotnet_style_prefer_conditional_expression_over_return = true:suggestion
dotnet_style_prefer_simplified_boolean_expressions = true:warning
dotnet_style_prefer_compound_assignment = true:warning
dotnet_style_prefer_simplified_interpolation = true:suggestion

# Null checking preferences
dotnet_style_prefer_is_null_check_over_reference_equality_method = true:warning

# Parameter preferences
dotnet_code_quality_unused_parameters = all:warning

# var preferences
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

# Pattern matching preferences
csharp_style_pattern_matching_over_is_with_cast_check = true:warning
csharp_style_pattern_matching_over_as_with_null_check = true:warning
csharp_style_prefer_switch_expression = true:suggestion
csharp_style_prefer_pattern_matching = true:suggestion
csharp_style_prefer_not_pattern = true:warning

# Null checking preferences
csharp_style_throw_expression = true:warning
csharp_style_conditional_delegate_call = true:warning

# Code block preferences
csharp_prefer_braces = true:warning
csharp_prefer_simple_using_statement = true:suggestion
csharp_style_namespace_declarations = file_scoped:warning

# Expression preferences
csharp_prefer_simple_default_expression = true:warning
csharp_style_deconstructed_variable_declaration = true:suggestion
csharp_style_pattern_local_over_anonymous_function = true:suggestion
csharp_style_prefer_index_operator = true:suggestion
csharp_style_prefer_range_operator = true:suggestion
csharp_style_implicit_object_creation_when_type_is_apparent = true:warning
csharp_style_prefer_tuple_swap = true:suggestion
csharp_style_unused_value_expression_statement_preference = discard_variable:suggestion
csharp_style_unused_value_assignment_preference = discard_variable:suggestion
csharp_prefer_static_local_function = true:warning
csharp_style_allow_embedded_statements_on_same_line_experimental = false:warning
csharp_style_allow_blank_lines_between_consecutive_braces_experimental = false:warning
csharp_style_allow_blank_line_after_colon_in_constructor_initializer_experimental = false:warning
csharp_style_prefer_primary_constructors = true:suggestion
csharp_style_prefer_null_check_over_type_check = true:warning
csharp_style_prefer_local_over_anonymous_function = true:suggestion
csharp_style_prefer_method_group_conversion = true:suggestion
csharp_style_prefer_top_level_statements = true:suggestion

# New line preferences
csharp_new_line_before_open_brace = all
csharp_new_line_before_else = true
csharp_new_line_before_catch = true
csharp_new_line_before_finally = true
csharp_new_line_before_members_in_object_initializers = true
csharp_new_line_before_members_in_anonymous_types = true
csharp_new_line_between_query_expression_clauses = true

# Indentation preferences
csharp_indent_case_contents = true
csharp_indent_switch_labels = true
csharp_indent_labels = one_less_than_current
csharp_indent_block_contents = true
csharp_indent_braces = false
csharp_indent_case_contents_when_block = false

# Space preferences
csharp_space_after_cast = false
csharp_space_after_keywords_in_control_flow_statements = true
csharp_space_between_parentheses = false
csharp_space_before_colon_in_inheritance_clause = true
csharp_space_after_colon_in_inheritance_clause = true
csharp_space_around_binary_operators = before_and_after
csharp_space_between_method_declaration_parameter_list_parentheses = false
csharp_space_between_method_declaration_empty_parameter_list_parentheses = false
csharp_space_between_method_declaration_name_and_open_parenthesis = false
csharp_space_between_method_call_parameter_list_parentheses = false
csharp_space_between_method_call_empty_parameter_list_parentheses = false
csharp_space_between_method_call_name_and_opening_parenthesis = false
csharp_space_after_comma = true
csharp_space_before_comma = false
csharp_space_after_dot = false
csharp_space_before_dot = false
csharp_space_after_semicolon_in_for_statement = true
csharp_space_before_semicolon_in_for_statement = false
csharp_space_around_declaration_statements = false
csharp_space_before_open_square_brackets = false
csharp_space_between_empty_square_brackets = false
csharp_space_between_square_brackets = false

# Wrapping preferences
csharp_preserve_single_line_statements = false
csharp_preserve_single_line_blocks = true

# Using directive preferences
csharp_using_directive_placement = outside_namespace:warning

# Naming rules
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

# Symbol specifications
dotnet_naming_symbols.interface.applicable_kinds = interface
dotnet_naming_symbols.interface.applicable_accessibilities = public, internal, private, protected, protected_internal, private_protected

dotnet_naming_symbols.types.applicable_kinds = class, struct, interface, enum
dotnet_naming_symbols.types.applicable_accessibilities = public, internal, private, protected, protected_internal, private_protected

dotnet_naming_symbols.private_or_internal_field.applicable_kinds = field
dotnet_naming_symbols.private_or_internal_field.applicable_accessibilities = private, internal

dotnet_naming_symbols.async_methods.applicable_kinds = method
dotnet_naming_symbols.async_methods.applicable_accessibilities = *
dotnet_naming_symbols.async_methods.required_modifiers = async

# Naming styles
dotnet_naming_style.pascal_case.capitalization = pascal_case

dotnet_naming_style.begins_with_i.required_prefix = I
dotnet_naming_style.begins_with_i.capitalization = pascal_case

dotnet_naming_style.underscore_camel_case.required_prefix = _
dotnet_naming_style.underscore_camel_case.capitalization = camel_case

dotnet_naming_style.end_with_async.required_suffix = Async
dotnet_naming_style.end_with_async.capitalization = pascal_case

# Analyzer rules
dotnet_diagnostic.CA1062.severity = none  # Covered by NRT
dotnet_diagnostic.CA1303.severity = none  # Localization not needed
dotnet_diagnostic.CA1707.severity = none  # Underscores in test names OK
dotnet_diagnostic.CA1812.severity = none  # Internal classes instantiated via DI
dotnet_diagnostic.CA2007.severity = warning  # ConfigureAwait
dotnet_diagnostic.CS1591.severity = none  # XML comments optional

# StyleCop rules
dotnet_diagnostic.SA1101.severity = none  # this. prefix not required
dotnet_diagnostic.SA1200.severity = none  # Using directives outside namespace OK
dotnet_diagnostic.SA1309.severity = none  # Field names can start with underscore
dotnet_diagnostic.SA1413.severity = none  # Trailing comma optional
dotnet_diagnostic.SA1600.severity = none  # Public members documented optional
dotnet_diagnostic.SA1633.severity = none  # File header optional
```

---

## dotnet format

### Commands

```bash
# Format all files
dotnet format

# Check without modifying (CI)
dotnet format --verify-no-changes

# Format specific file
dotnet format whitespace ./src/MyClass.cs

# Format only whitespace
dotnet format whitespace

# Format only style rules
dotnet format style

# Format only analyzer rules
dotnet format analyzers

# Include generated files
dotnet format --include-generated

# Verbose output
dotnet format --verbosity diagnostic
```

### CI Integration

```yaml
# GitHub Actions
- name: Check formatting
  run: dotnet format --verify-no-changes

# Pre-commit hook
#!/bin/bash
dotnet format --verify-no-changes || {
  echo "Code formatting issues found. Run 'dotnet format' to fix."
  exit 1
}
```

---

## IDE Integration

### Visual Studio

Settings are automatically loaded from .editorconfig. Enable:
- **Tools > Options > Text Editor > C# > Code Style**: Use EditorConfig settings
- **Tools > Options > Text Editor > C# > Advanced**: Run analyzers in background

### Visual Studio Code

Install extensions:
- C# Dev Kit (ms-dotnettools.csdevkit)
- .NET Install Tool (ms-dotnettools.vscode-dotnet-runtime)

Settings in `.vscode/settings.json`:
```json
{
    "omnisharp.enableEditorConfigSupport": true,
    "omnisharp.enableRoslynAnalyzers": true,
    "editor.formatOnSave": true,
    "[csharp]": {
        "editor.defaultFormatter": "ms-dotnettools.csharp"
    }
}
```

### JetBrains Rider

Settings are automatically loaded from .editorconfig. Additional:
- **Settings > Editor > Code Style > C#**: Enable EditorConfig support
- **Settings > Editor > Inspection Settings**: Enable Roslyn analyzers

---

## Directory.Build.props Template

```xml
<Project>
  <PropertyGroup>
    <!-- .NET settings -->
    <TargetFramework>net10.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>

    <!-- Analyzer settings -->
    <AnalysisLevel>latest-recommended</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>

    <!-- Documentation -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <NoWarn>$(NoWarn);CS1591</NoWarn>

    <!-- Build settings -->
    <Deterministic>true</Deterministic>
    <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>
  </PropertyGroup>

  <ItemGroup>
    <!-- Analyzers -->
    <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
    <PackageReference Include="Roslynator.Analyzers" Version="4.12.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
  </ItemGroup>
</Project>
```

---

## Summary

### Quick Commands

```bash
# Build with all analyzers
dotnet build

# Format code
dotnet format

# Check formatting (CI)
dotnet format --verify-no-changes

# Run specific analyzer
dotnet build /p:TreatWarningsAsErrors=true
```

### Essential Files

| File | Purpose |
|------|---------|
| `.editorconfig` | Code style rules |
| `Directory.Build.props` | Shared project settings |
| `Directory.Packages.props` | Central package management |
| `global.json` | SDK version pinning |

### Key Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `AnalysisLevel` | `latest-recommended` | Enable recommended analyzers |
| `TreatWarningsAsErrors` | `true` | Fail build on warnings |
| `EnforceCodeStyleInBuild` | `true` | Enforce style in build |
| `Nullable` | `enable` | Enable NRT |

---

*Last updated: 2026-01-15*

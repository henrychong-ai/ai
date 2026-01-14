# TypeScript 4.x to 5.x Migration Guide

Breaking changes and migration steps for TypeScript v4.x → v5.x.

## Key Changes Summary

| Change | Impact | Action Required |
|--------|--------|-----------------|
| Enum behavior changes | High | Review enum usage |
| Stricter type comparisons | Medium | Fix type errors |
| Deprecated compiler options | Medium | Update tsconfig |
| Module resolution changes | Medium | Review imports |
| Decorator changes | Low | For legacy decorators |

## Critical: Enum Behavior Changes

### Numeric Enums as Union Types

TypeScript 5 treats numeric enums more strictly:

```typescript
// TypeScript 4: This worked
enum Status { Pending = 0, Active = 1 }
function process(s: Status) { }
process(99); // Allowed in TS4, error in TS5

// TypeScript 5: Must use enum values
process(Status.Pending); // Correct
```

### Migration Pattern

**Before (TS4):**
```typescript
enum Color { Red = 1, Green = 2, Blue = 3 }
const c: Color = 5; // Worked in TS4
```

**After (TS5):**
```typescript
// Option 1: Use const object instead
const Color = {
  Red: 1,
  Green: 2,
  Blue: 3,
} as const;
type Color = typeof Color[keyof typeof Color];

// Option 2: Explicit union type
type Color = 1 | 2 | 3;
```

### Audit Command
```bash
# Find enum declarations
grep -r "enum " --include="*.ts" --include="*.tsx" .
```

## Module Resolution Changes

### New `bundler` Resolution

TypeScript 5 introduces `moduleResolution: "bundler"`:

```json
{
  "compilerOptions": {
    "moduleResolution": "bundler"
  }
}
```

**When to use:**
- Bundler-based projects (Vite, webpack, esbuild)
- Don't need Node.js module resolution quirks

### Import Extensions

With `bundler` resolution, explicit extensions recommended:
```typescript
// Recommended
import { helper } from './helper.js';

// May work but inconsistent
import { helper } from './helper';
```

## Deprecated Compiler Options

### Removed/Replaced Options

| Old Option | New Option |
|------------|------------|
| `target: "ES3"` | Minimum `ES5` |
| `out` | `outFile` |
| `charset` | Removed |
| `importsNotUsedAsValues` | `verbatimModuleSyntax` |
| `preserveValueImports` | `verbatimModuleSyntax` |

### TSConfig Updates Required

```json
{
  "compilerOptions": {
    // Remove these
    // "importsNotUsedAsValues": "remove",
    // "preserveValueImports": true,

    // Add this instead
    "verbatimModuleSyntax": true
  }
}
```

## Stricter Type Checking

### Interface vs Type Compatibility

TypeScript 5 is stricter about interface/type interchangeability:

```typescript
// May need explicit type assertions
interface A { x: number }
type B = { x: number }

// TS5 may require explicit handling in some cases
const a: A = { x: 1 };
const b: B = a; // May need type assertion
```

### Generic Inference Changes

```typescript
// TS4: More permissive inference
function example<T>(x: T): T[] { return [x]; }

// TS5: May require explicit type parameters
example<string>("hello");
```

## Decorators

### Experimental vs Stage 3

TypeScript 5 supports Stage 3 decorators by default:

```typescript
// Stage 3 decorators (TS5 default)
function logged(target: any, context: ClassMethodDecoratorContext) {
  // ...
}

// Legacy decorators (still supported with flag)
// tsconfig: "experimentalDecorators": true
```

### Migration for Legacy Decorators

If using legacy decorators (Angular, NestJS):
```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

## Recommended TSConfig (TS5)

### Strict Modern Configuration

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

### Framework-Specific Additions

**React:**
```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "react"
  }
}
```

**Node.js:**
```json
{
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

## Testing Checklist

### Pre-Migration
- [ ] Document current TypeScript version
- [ ] List all tsconfig.json files in project
- [ ] Audit enum usage
- [ ] Check for deprecated compiler options
- [ ] Verify decorator usage type

### Migration Steps
1. [ ] Update TypeScript version in package.json
2. [ ] Remove deprecated compiler options
3. [ ] Add replacement options
4. [ ] Run `tsc --noEmit` to find errors
5. [ ] Fix enum-related type errors
6. [ ] Update import statements if needed
7. [ ] Run full build
8. [ ] Run test suite

### Post-Migration
- [ ] No TypeScript errors
- [ ] All tests passing
- [ ] Build output unchanged
- [ ] No runtime behavior changes

## Common Errors and Fixes

### Error: Enum Assignment
```
Type 'number' is not assignable to type 'Status'
```
**Fix:** Use explicit enum values or convert to const object

### Error: Deprecated Option
```
Option 'importsNotUsedAsValues' is deprecated
```
**Fix:** Replace with `verbatimModuleSyntax`

### Error: Module Resolution
```
Cannot find module './helper'
```
**Fix:** Add explicit `.js` extension or adjust `moduleResolution`

## Performance Improvements

TypeScript 5 provides:
- 10-20% faster compilation
- Better incremental build performance
- Reduced memory usage
- Faster IDE responsiveness

---

*Note: TypeScript 5 is the current recommended version for new projects.*

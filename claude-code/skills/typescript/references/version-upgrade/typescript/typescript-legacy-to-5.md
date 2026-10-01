# TypeScript 3.x / 4.x → 5.9

Bring an old codebase to the last 5.x release (5.9) first, then continue with `typescript-5-to-6.md`. TypeScript 5 needs Node ≥14.17 — on older Node, upgrade Node first (`../node/legacy-node-to-24.md`). Converge on the tsconfig in `../../coding-standards/tooling.md` (versions: `../../tech-stack/version-policy.md`); do not invent a new one here.

Primary sources: the "Announcing TypeScript 4.x / 5.x" posts at https://devblogs.microsoft.com/typescript/ and the breaking-changes wiki https://github.com/microsoft/TypeScript/wiki/Breaking-Changes.

## Path

| From | Step | Main work |
|---|---|---|
| 3.x | 3.x → 4.9 | `unknown` in `catch` under `strict` (4.4, `useUnknownInCatchVariables`), abstract/constructor typing, `lib.dom` changes, stricter generics on `{}` (4.8) |
| 4.x | 4.9 → 5.0 | Enum and option deprecations below |
| 5.0 | 5.0 → 5.9 | Mostly additive; 5.5 removed the options deprecated in 5.0 |

Upgrade one step at a time with a clean `tsc --noEmit` between steps, and move `@types/*` packages along with the compiler (old `@types/node` majors will not type-check under a new compiler).

## 5.0 changes that break builds

### Enums

All enums became union enums. Assigning a literal outside the enum's members is an error:

```typescript
enum Status { Pending = 0, Active = 1 }
let s: Status = 99; // error in 5.0+: not assignable to 'Status'
```

Fix the value, or replace the enum with a `const` object and a derived union type.

### Options deprecated in 5.0 and removed in 5.5

| Option | Replacement |
|---|---|
| `target: "ES3"` | `ES5` or later (and ES2015+ before TS 6) |
| `out` | `outFile` (itself deprecated in 6.0 — prefer a bundler) |
| `charset`, `noImplicitUseStrict`, `keyofStringsOnly`, `suppressExcessPropertyErrors`, `suppressImplicitAnyIndexErrors`, `noStrictGenericChecks` | Remove |
| `importsNotUsedAsValues`, `preserveValueImports` | `verbatimModuleSyntax` |
| `prepend` in project references | Remove |

### Module resolution

5.0 added `moduleResolution: "bundler"` (for Vite, esbuild, tsdown, webpack): it allows extensionless relative imports and honours `exports`. Under `nodenext`, relative imports need the runtime extension (`./helper.js`). Pick one per project: `nodenext` for code Node runs directly, `bundler` for bundled apps. Both `node`/`node10` and `classic` are deprecated in 6.0.

### Decorators

5.0 implements standard (TC39) decorators by default. Frameworks that use legacy decorators (NestJS, TypeORM, class-validator) must keep `"experimentalDecorators": true` (and `emitDecoratorMetadata` where the framework needs it).

## Checklist

1. List every tsconfig (`find . -name 'tsconfig*.json' -not -path '*/node_modules/*'`) and the TypeScript version in each workspace package.
2. Upgrade stepwise; after each step run `tsc --noEmit`, lint, tests and build.
3. Remove the options above; set `verbatimModuleSyntax` if you used the replaced options.
4. Fix enum assignments and module-resolution errors.
5. Confirm emitted output and declaration files are unchanged where behaviour must not change.
6. Continue with `typescript-5-to-6.md`.

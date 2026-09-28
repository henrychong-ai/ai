# Polyfill Strategies for ECMAScript Features

How to polyfill ES features for older runtimes using core-js and Babel.

**Sources:**
- [core-js GitHub](https://github.com/zloirock/core-js)
- [Babel preset-env](https://babeljs.io/docs/babel-preset-env)

---

## Syntax vs APIs

Polyfills only add **missing built-in APIs** (methods and globals). **Syntax** (`?.`, `??`, `async`/`await`, classes, private `#fields`, static blocks) is not polyfilled — it is transpiled by TypeScript, SWC, esbuild or Babel when the build target is lower than the syntax level. **Engine features** (`Proxy`, `WeakRef`/`FinalizationRegistry`, BigInt arithmetic, new RegExp syntax, `SharedArrayBuffer`/`Atomics`) can be neither transpiled nor polyfilled — the runtime floor must support them. Full table: `es-version-features.md` → "Native, Transpiled, Polyfilled or Impossible".

Server code on a supported Node line rarely needs polyfills: raise the runtime instead. Polyfills are mainly for browser builds with an older floor.

---

## core-js Configuration

### Installation

```bash
<pm> add core-js@^3
npm view core-js dist-tags    # 3.x is "latest"; 4.x is alpha only (2026-09-28) — do not use it in production
```

### Global Polyfilling (Simple)

Import at application entry point:

```typescript
// Entry file (index.ts)
import 'core-js/stable';
```

**Pros:** Simple, everything available
**Cons:** Large bundle size (~80KB gzipped)

### Selective Polyfilling (Optimized)

Import only needed features:

```typescript
// Only Array.prototype.at
import 'core-js/actual/array/at';

// Only Object.groupBy
import 'core-js/actual/object/group-by';

// Only Promise.withResolvers
import 'core-js/actual/promise/with-resolvers';

// Only change-array-by-copy methods
import 'core-js/actual/array/to-sorted';
import 'core-js/actual/array/to-reversed';
import 'core-js/actual/array/to-spliced';
import 'core-js/actual/array/with';
```

### Everything stable

```typescript
import 'core-js/stable';   // all stable features; prefer `usage` mode or selective imports below
```

core-js has no per-edition entry points (there is no `core-js/es/2023`); use `core-js/actual/<namespace>/<method>` imports or Babel/SWC `usage` mode.

---

## Babel Integration

### @babel/preset-env Configuration

```javascript
// babel.config.js
module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        // Automatically add polyfills based on usage
        useBuiltIns: 'usage',

        // Specify core-js version
        corejs: {
          version: '3.50', // the installed core-js minor — check with `npm ls core-js`
          proposals: false // Set true for stage 3 proposals
        },

        // Target environments
        targets: {
          node: '24',
          // Or for browsers:
          // browsers: '> 0.5%, not dead'
        }
      }
    ]
  ]
};
```

### useBuiltIns Options

| Option | Behavior |
|--------|----------|
| `false` | No automatic polyfills (default) |
| `entry` | Replace `import 'core-js'` with needed polyfills |
| `usage` | Automatically add polyfills per file based on usage |

**Recommended:** `usage` for applications, `false` for libraries

### Entry Mode

With `useBuiltIns: 'entry'`:

```typescript
// Input
import 'core-js/stable';
import 'regenerator-runtime/runtime';

// Output (based on targets)
import 'core-js/modules/es.array.at';
import 'core-js/modules/es.object.group-by';
// ... only needed polyfills
```

---

## SWC Integration

### .swcrc Configuration

```json
{
  "env": {
    "targets": {
      "node": "24"
    },
    "mode": "usage",
    "coreJs": "3.50"
  }
}
```

### SWC Mode Options

| Mode | Behavior |
|------|----------|
| `usage` | Add polyfills based on usage |
| `entry` | Transform core-js imports |

---

## Library Considerations

### DON'T Bundle Polyfills in Libraries

Libraries should NOT include polyfills:
- Let applications choose their polyfill strategy
- Avoid duplicate polyfills across dependencies
- Specify `peerDependencies` if polyfills required

```jsonc
// Library package.json
{
  "peerDependencies": {
    "core-js": "^3.30.0"
  }
}
```

### Document Required Polyfills

```markdown
## Requirements

This library uses the following ES2023+ features:
- `Array.prototype.toSorted()` - native from Node 20
- `Object.groupBy()` - native from Node 21
```

---

## Feature-Specific Polyfills

### ES2023 Features

```typescript
// Array.prototype.findLast / findLastIndex
import 'core-js/actual/array/find-last';
import 'core-js/actual/array/find-last-index';

// Change Array by Copy
import 'core-js/actual/array/to-reversed';
import 'core-js/actual/array/to-sorted';
import 'core-js/actual/array/to-spliced';
import 'core-js/actual/array/with';
```

### ES2024 Features

```typescript
// Object.groupBy / Map.groupBy
import 'core-js/actual/object/group-by';
import 'core-js/actual/map/group-by';

// Promise.withResolvers
import 'core-js/actual/promise/with-resolvers';

// String well-formed methods
import 'core-js/actual/string/is-well-formed';
import 'core-js/actual/string/to-well-formed';
```

### Common ES2020+ Features

```typescript
// Promise.allSettled (ES2020)
import 'core-js/actual/promise/all-settled';

// Promise.any (ES2021)
import 'core-js/actual/promise/any';

// String.prototype.replaceAll (ES2021)
import 'core-js/actual/string/replace-all';

// Array.prototype.at (ES2022)
import 'core-js/actual/array/at';

// Object.hasOwn (ES2022)
import 'core-js/actual/object/has-own';
```

---

## No-Global-Pollution Mode

For libraries that need polyfill functionality without modifying globals:

```typescript
import from from 'core-js-pure/actual/array/from';
import groupBy from 'core-js-pure/actual/object/group-by';

// Use imported functions instead of Array.from or Object.groupBy
const arr = from(iterable);
const groups = groupBy(items, item => item.category);
```

---

## Bundle Size Optimization

### Analyze Bundle

```bash
# Check what core-js adds to your bundle
npx source-map-explorer dist/bundle.js
```

### Minimize core-js Size

1. **Use `usage` mode** - Only import what's used
2. **Set accurate targets** - Don't polyfill what the runtime floor already has
3. **Exclude unused features** - Configure `exclude` in preset-env
4. **Use pure imports** - `core-js-pure` for libraries

### Example: Excluding Features

```javascript
// babel.config.js
{
  presets: [
    ['@babel/preset-env', {
      useBuiltIns: 'usage',
      corejs: '3.50',
      // Don't polyfill these even if used
      exclude: [
        'es.promise',  // Use native Promise
        'es.symbol'    // Use native Symbol
      ]
    }]
  ]
}
```

---

## Testing Polyfill Configuration

### Verify Polyfills Load

```typescript
// test-polyfills.ts
console.log('Array.prototype.at:', typeof [].at);
console.log('Object.groupBy:', typeof Object.groupBy);
console.log('Promise.withResolvers:', typeof Promise.withResolvers);
```

### Run in Target Environment

```bash
# Run the built output in the oldest browser or runtime you support
node dist/test-polyfills.js
```

---

## Common Issues

### 1. Polyfills Not Loading

**Symptom:** `TypeError: [].at is not a function`

**Solution:** Ensure polyfill imports are at entry point, before other code.

### 2. Duplicate Polyfills

**Symptom:** Bundle size larger than expected

**Solution:** Use `useBuiltIns: 'usage'` instead of manual imports.

### 3. TypeScript Errors for New APIs

**Symptom:** `Property 'groupBy' does not exist on type 'ObjectConstructor'`

**Solution:** Update `lib` in tsconfig.json to match target:
```json
{
  "compilerOptions": {
    "lib": ["ES2024"]
  }
}
```

Only raise `lib` if every runtime in the floor has the API (natively or through the polyfill you ship); core-js ships no types, and `@types/core-js` is not needed.

### 4. core-js Version Mismatch

**Symptom:** Missing features despite importing core-js

**Solution:** Ensure `corejs` version in babel config matches installed version.

---

## Migration from @babel/polyfill

`@babel/polyfill` is deprecated. Replace with:

```typescript
// Old (deprecated)
import '@babel/polyfill';

// New
import 'core-js/stable';
import 'regenerator-runtime/runtime';
```

Or use `useBuiltIns: 'usage'` for automatic polyfilling.

# Polyfill Strategies for ECMAScript Features

How to polyfill ES features for older runtimes using core-js and Babel.

**Sources:**
- [core-js GitHub](https://github.com/zloirock/core-js)
- [core-js Documentation](https://www.core-js.io/v4/docs/usage)
- [Babel preset-env](https://babeljs.io/docs/babel-preset-env)

---

## Critical Understanding: Syntax vs APIs

### What CAN Be Polyfilled

**Runtime APIs** - Methods added to built-in objects:
- Array methods: `flat`, `flatMap`, `findLast`, `toSorted`, `at`
- Object methods: `entries`, `fromEntries`, `groupBy`, `hasOwn`
- String methods: `padStart`, `replaceAll`, `trimStart`
- Promise methods: `allSettled`, `any`, `withResolvers`
- Map, Set, WeakMap, WeakSet implementations

### What CANNOT Be Polyfilled

**Syntax features** - Require transpilation, not polyfilling:
- Arrow functions: `() => {}`
- Classes: `class Foo {}`
- async/await: `async function() { await }`
- Optional chaining: `obj?.prop`
- Nullish coalescing: `value ?? default`
- Destructuring: `const {a} = obj`
- Template literals: `` `${expr}` ``
- Private class fields: `#private`
- Top-level await

**Unpolyfillable APIs:**
- `Proxy` - Cannot be shimmed in ES5
- `WeakRef` / `FinalizationRegistry` - GC-dependent
- `BigInt` arithmetic - Engine-level feature
- RegExp features - Named groups, lookbehind, v flag
- `SharedArrayBuffer` / `Atomics` - Engine-level

---

## core-js Configuration

### Installation

```bash
# core-js v3 (stable, widely used)
pnpm add core-js@3

# core-js v4 (latest, breaking changes from v3)
pnpm add core-js@4
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

### ES Version Bundles

```typescript
// All ES2023 features
import 'core-js/es/2023';

// All ES2024 features
import 'core-js/es/2024';

// All stable features
import 'core-js/stable';
```

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
          version: '3.37',
          proposals: false // Set true for stage 3 proposals
        },

        // Target environments
        targets: {
          node: '18',
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
      "node": "18"
    },
    "mode": "usage",
    "coreJs": "3.37"
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

```json
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
- `Array.prototype.toSorted()` - Requires polyfill for Node < 20
- `Object.groupBy()` - Requires polyfill for Node < 22
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
2. **Set accurate targets** - Don't polyfill for ES2024 if targeting Node 22
3. **Exclude unused features** - Configure `exclude` in preset-env
4. **Use pure imports** - `core-js-pure` for libraries

### Example: Excluding Features

```javascript
// babel.config.js
{
  presets: [
    ['@babel/preset-env', {
      useBuiltIns: 'usage',
      corejs: '3.37',
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
# Test with older Node version
nvm use 16
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

Or install type definitions:
```bash
pnpm add -D @types/core-js
```

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

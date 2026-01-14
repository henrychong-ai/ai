# Node.js 20 to 22 Migration Guide

Specific breaking changes and migration steps for Node.js v20 → v22.

## Key Changes Summary

| Change | Impact | Action Required |
|--------|--------|-----------------|
| Import assertions → attributes | Medium | Codemod available |
| V8 12.4 → 12.8 | Low | Review new features |
| npm 10 → npm 10.8 | Low | Check scripts |
| Test runner stable | Low | Optional adoption |
| Watch mode improvements | Low | None required |

## Critical Migration: Import Assertions

### The Change
```javascript
// Node 20 (deprecated in 22)
import data from './data.json' assert { type: 'json' };

// Node 22 (new syntax)
import data from './data.json' with { type: 'json' };
```

### Automated Migration

Use the official codemod:
```bash
npx @nodejs/import-assertions-to-attributes ./src
```

### Manual Migration Pattern

Search and replace:
```
Find: assert { type:
Replace: with { type:
```

Regex pattern:
```regex
import\s+(\w+)\s+from\s+['"]([^'"]+)['"]\s+assert\s*\{
```

Replace with:
```
import $1 from '$2' with {
```

## V8 Engine Updates (12.4 → 12.8)

### New JavaScript Features

**Array.fromAsync():**
```javascript
// Now available
const arr = await Array.fromAsync(asyncIterable);
```

**Set methods:**
```javascript
const a = new Set([1, 2, 3]);
const b = new Set([2, 3, 4]);
a.intersection(b); // Set {2, 3}
a.union(b);        // Set {1, 2, 3, 4}
a.difference(b);   // Set {1}
```

### Removed Features

None significant - v20 → v22 is relatively smooth.

## Module System Changes

### Stricter Package Exports

Node 22 enforces package.json `exports` more strictly:
```json
{
  "exports": {
    ".": "./dist/index.js",
    "./utils": "./dist/utils.js"
  }
}
```

Importing unlisted paths will fail:
```javascript
// This may fail if not in exports
import { helper } from 'package/internal/helper';
```

### ESM Improvements

**Import meta resolve:**
```javascript
// More reliable in v22
const resolved = import.meta.resolve('./module.js');
```

## Native Module Rebuilds

Likely need rebuild:
- `better-sqlite3`
- `sharp`
- `bcrypt`
- `node-sass` (consider `sass` instead)

```bash
npm rebuild
# or
pnpm rebuild
```

## Testing Checklist

### Pre-Migration
- [ ] All tests passing on Node 20
- [ ] Document current test coverage
- [ ] List native modules in use
- [ ] Check for import assertions usage

### Migration Steps
1. [ ] Update `.nvmrc` to `22.22.0`
2. [ ] Run import assertions codemod
3. [ ] Delete node_modules and lockfile
4. [ ] Install dependencies with Node 22
5. [ ] Rebuild native modules
6. [ ] Run type checking
7. [ ] Run linting
8. [ ] Run full test suite

### Post-Migration
- [ ] Compare test coverage (must not decrease)
- [ ] Verify build output matches
- [ ] Check for new deprecation warnings
- [ ] Update Dockerfile
- [ ] Update CI/CD pipelines

## Common Issues

### Issue: Import Assertion Errors
```
SyntaxError: Import assertions are not allowed in ES module syntax
```
**Fix:** Run the codemod or manually update `assert` → `with`

### Issue: Native Module Failures
```
Error: The module was compiled against a different Node.js version
```
**Fix:** `npm rebuild` or reinstall the package

### Issue: Package Export Errors
```
Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: Package subpath './internal' is not defined
```
**Fix:** Use official package exports or fork/patch the package

## Dockerfile Update

```dockerfile
# Change FROM line
- FROM node:20-alpine
+ FROM node:22.22.0-alpine
```

## Performance Notes

Node 22 generally provides:
- 5-10% faster startup time
- Improved async/await performance
- Better memory management

Benchmark before/after for critical paths.

---

*Minimum safe version: 22.22.0 (CVE-2025-59466 patched)*

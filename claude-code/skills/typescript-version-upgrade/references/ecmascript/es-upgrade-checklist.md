# ECMAScript Target Upgrade Checklist

Step-by-step protocol for upgrading ES target in TypeScript projects.

---

## Pre-Upgrade Analysis Phase

### Step 1: Inventory Current Configuration

```bash
# 1. Check current tsconfig target/lib
grep -E '"target"|"lib"' tsconfig.json

# 2. Check Node.js version
cat .nvmrc 2>/dev/null || cat .node-version 2>/dev/null || echo "No version file"
node --version

# 3. Check TypeScript version
pnpm exec tsc --version

# 4. Check bundler configuration
grep -r "target" vite.config.* esbuild.config.* webpack.config.* 2>/dev/null
```

**Record findings:**
- Current target: _______________
- Current lib: _______________
- Node.js version: _______________
- TypeScript version: _______________
- Bundler target: _______________

### Step 2: Determine Safe Target

| Node.js Version | Maximum Safe Target |
|-----------------|---------------------|
| 24.x | ES2024 |
| 22.x | ES2023 |
| 20.x | ES2023 |
| 18.x | ES2022 |
| 16.x | ES2021 |
| 14.x | ES2020 |

**Default recommendation: ES2022** unless Node 22+ is guaranteed.

### Step 3: Check TypeScript Version Requirements

| Target | Required TypeScript |
|--------|---------------------|
| ES2022 | 5.0+ |
| ES2023 | 5.5+ |
| ES2024 | 5.6+ |

```bash
# If TypeScript version is too old, upgrade first:
pnpm add -D typescript@latest
```

### Step 4: Check Browser Requirements (Web Apps)

If targeting browsers, verify support:

| Target | Chrome | Firefox | Safari | Edge |
|--------|--------|---------|--------|------|
| ES2022 | 94+ | 93+ | 15+ | 94+ |
| ES2023 | 97+ | 104+ | 15.4+ | 97+ |
| ES2024 | 117+ | 119+ | 17.4+ | 117+ |

---

## Compatibility Check Phase

### Step 5: Analyze Code for Breaking Changes

**Low Risk (syntax downleveling removed):**
- Arrow functions → If previously targeting ES5
- Classes → If previously targeting ES5
- async/await → If previously targeting ES2016

**Medium Risk (new APIs used):**
```bash
# Check for ES2023+ API usage
grep -rE "\.findLast\(|\.toSorted\(|\.toReversed\(|\.toSpliced\(|\.with\(" src/

# Check for ES2024+ API usage
grep -rE "Object\.groupBy|Map\.groupBy|Promise\.withResolvers" src/
```

**High Risk (cannot polyfill):**
```bash
# Check for private class fields
grep -rE "#[a-zA-Z]+" src/

# Check for WeakRef/FinalizationRegistry
grep -rE "WeakRef|FinalizationRegistry" src/
```

### Step 6: Check for useDefineForClassFields Implications

If upgrading TO ES2022+, class field behavior changes:

```typescript
// Pre-ES2022 behavior (useDefineForClassFields: false)
class Foo {
  x = 1;  // Assigned in constructor
}

// ES2022+ behavior (useDefineForClassFields: true)
class Foo {
  x = 1;  // Uses Object.defineProperty
}
```

**Check for affected patterns:**
```bash
# Classes with accessors that might be affected
grep -rE "class.*\{" src/ -A 20 | grep -E "get |set "
```

### Step 7: Verify Polyfill Requirements

If using new APIs with older runtime support needed:

| API | Polyfillable? | How |
|-----|---------------|-----|
| Array.prototype.at() | ✅ | core-js/actual/array/at |
| Object.groupBy() | ✅ | core-js/actual/object/group-by |
| Array.prototype.toSorted() | ✅ | core-js/actual/array/to-sorted |
| Private fields (#) | ❌ | Cannot polyfill |
| WeakRef | ❌ | Cannot polyfill |

---

## Configuration Update Phase

### Step 8: Update tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

For web apps, include DOM:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"]
  }
}
```

### Step 9: Update Bundler Configuration

**Vite:**
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    target: 'es2022',
  },
});
```

**esbuild:**
```javascript
await build({
  target: 'es2022',
});
```

**Webpack (esbuild-loader):**
```javascript
{
  loader: 'esbuild-loader',
  options: {
    target: 'es2022',
  },
}
```

**tsup:**
```typescript
export default defineConfig({
  target: 'es2022',
});
```

### Step 10: Update Browserslist (Web Apps)

```
# .browserslistrc
chrome >= 94
firefox >= 93
safari >= 15
edge >= 94
```

Or in package.json:
```json
{
  "browserslist": [
    "chrome >= 94",
    "firefox >= 93",
    "safari >= 15",
    "edge >= 94"
  ]
}
```

### Step 11: Update Polyfill Configuration (If Needed)

**Babel:**
```javascript
// babel.config.js
{
  presets: [
    ['@babel/preset-env', {
      targets: { node: '18' },
      useBuiltIns: 'usage',
      corejs: '3.37'
    }]
  ]
}
```

**Remove unnecessary polyfills:**
```bash
# If target supports features natively, remove explicit polyfills
grep -r "core-js" src/
```

---

## Validation Phase

### Step 12: Type Check

```bash
pnpm exec tsc --noEmit
```

**Expected:** No errors. If errors about missing APIs:
- Verify `lib` matches `target`
- Or install polyfill type definitions

### Step 13: Build

```bash
pnpm build
```

**Check:**
- Build succeeds
- No new warnings
- Bundle size should DECREASE (less downleveling)

### Step 14: Run Tests

```bash
pnpm test
```

**All tests must pass.** Any failures indicate:
- Runtime API not available
- Class field behavior change
- Module resolution issue

### Step 15: Check Bundle Output

```bash
# Verify output uses modern syntax
head -50 dist/index.js

# Check bundle size (should be smaller)
ls -la dist/
```

**Verify:**
- Modern syntax present (arrow functions, classes, async/await)
- No unnecessary polyfills
- Smaller bundle size

---

## Rollback Procedures

### If Type Errors Occur

```bash
# Revert tsconfig changes
git checkout tsconfig.json
```

### If Build Fails

```bash
# Revert all configuration changes
git checkout .

# Reinstall dependencies
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### If Tests Fail

1. Identify failing tests
2. Check if they use features affected by ES upgrade
3. Either:
   - Update tests for new behavior
   - Revert and add polyfills
   - Lower target version

---

## Post-Upgrade Verification

### Checklist

- [ ] `tsconfig.json target` updated
- [ ] `tsconfig.json lib` updated
- [ ] Bundler target aligned
- [ ] Browserslist updated (if web app)
- [ ] TypeScript version compatible
- [ ] `tsc --noEmit` passes
- [ ] Build succeeds
- [ ] All tests pass
- [ ] Bundle size decreased or stable
- [ ] Manual testing completed

### Documentation

Update project documentation:
- README.md: Update Node.js version requirements
- CHANGELOG.md: Note ES target upgrade
- CI/CD: Verify Node version in pipelines

---

## Quick Commands Summary

```bash
# 1. Check current state
grep -E '"target"|"lib"' tsconfig.json
node --version
pnpm exec tsc --version

# 2. Create safety branch
git checkout -b upgrade/es-target-$(date +%Y%m%d)

# 3. Update configs (manual edits)

# 4. Validate
pnpm exec tsc --noEmit
pnpm build
pnpm test

# 5. Check output
ls -la dist/
head -50 dist/index.js

# 6. Commit if successful
git add -A
git commit -m "chore: upgrade ES target from X to ES2022"
```

---

## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| `TS5023: Unknown option 'target'` | Upgrade TypeScript to 5.5+ for ES2023, 5.6+ for ES2024 |
| `Property 'groupBy' does not exist` | Update `lib` to match `target` |
| Build output still has polyfills | Update bundler target and browserslist |
| Class fields behave differently | Set `useDefineForClassFields` explicitly |
| Tests fail on older Node | Ensure Node version matches target requirements |
| Bundle size increased | Check for accidentally added polyfills |

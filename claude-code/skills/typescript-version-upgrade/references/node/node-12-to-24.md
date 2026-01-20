# Node.js 12 to 24 Migration Guide

**EXTREMELY CRITICAL: Node 12 reached End-of-Life on April 30, 2022. This is an emergency security migration spanning 12 major versions with 3+ years of unpatched CVEs.**

## Migration Overview

This guide covers the complete migration path from Node.js 12 → 24, aggregating all breaking changes across 12 major versions (12 → 13 → 14 → 15 → 16 → 17 → 18 → 19 → 20 → 21 → 22 → 23 → 24).

### Why This Migration is URGENT

| Risk | Description |
|------|-------------|
| **CVEs Unpatched** | CVE-2021-22884, CVE-2021-22918, CVE-2021-22930, CVE-2021-22931, CVE-2021-22939, CVE-2021-22940, CVE-2021-44531-44533, plus ALL CVEs from 2022-2026 |
| **Security Compliance** | Most security audits will flag Node 12 as critical vulnerability |
| **Dependency Hell** | Modern packages no longer support Node 12 |
| **No Support** | Zero community or official support available |

### Impact Assessment

| Category | Severity | Description |
|----------|----------|-------------|
| Security | 🔴 CRITICAL | 3+ years of unpatched CVEs |
| npm | 🔴 CRITICAL | npm 6 → 10 (major breaking changes) |
| OpenSSL | 🔴 HIGH | OpenSSL 1.1.1 → 3.0 in Node 17+ |
| Unhandled Rejections | 🔴 HIGH | Process exit behavior changed in Node 15 |
| APIs | 🔴 HIGH | Extensive deprecated APIs removed |
| Module System | 🟠 MEDIUM | Import assertions → attributes |
| Native Modules | 🟠 MEDIUM | All must be rebuilt |
| V8 Engine | 🟡 MEDIUM | 7.x → 13.x (major JavaScript changes) |

## Recommended Migration Strategy

Given the 12 major version gap, we recommend staged migration:

### Option A: Incremental Jumps (Safest - Recommended for Production)

```
Node 12 → 14 (LTS) → 16 (LTS) → 18 (LTS) → 20 (LTS) → 24 (LTS)
```

| Stage | Key Changes | Risk |
|-------|-------------|------|
| 12 → 14 | V8 8.1, ES2020, stable features | 🟢 Low |
| 14 → 16 | V8 9.0, prepare for npm 7 | 🟢 Low |
| 16 → 18 | OpenSSL 3.0, npm 8, Fetch API | 🟠 Medium |
| 18 → 20 | Stability checkpoint | 🟢 Low |
| 20 → 24 | Import attributes, latest V8 | 🟢 Low |

### Option B: Two-Stage Jump (Balanced)

```
Node 12 → 18 (LTS) → 24 (LTS)
```

| Stage | Key Changes | Risk |
|-------|-------------|------|
| 12 → 18 | npm 6→8, OpenSSL 3.0, unhandled rejections | 🔴 High |
| 18 → 24 | Import attributes, V8 updates | 🟠 Medium |

### Option C: Direct Jump (Fastest but Highest Risk)

```
Node 12 → 24 (Direct)
```

Only recommended if:
- Comprehensive test coverage exists
- Team has experience with Node migrations
- Application is relatively simple
- You can afford extended debugging time

## Phase 1: Pre-Migration Analysis

### Critical Blockers Detection

```bash
# Check for Node 12 era deprecated patterns
grep -rn "new Buffer\|Buffer(" --include="*.js" --include="*.ts" src/
grep -rn "url\.parse\|url\.resolve\|url\.format" --include="*.js" --include="*.ts" src/
grep -rn "require('domain')" --include="*.js" --include="*.ts" src/
grep -rn "util\.log\|util\.print\|util\.puts" --include="*.js" --include="*.ts" src/
grep -rn "os\.tmpDir()" --include="*.js" --include="*.ts" src/
grep -rn "tls\.createSecurePair" --include="*.js" --include="*.ts" src/
grep -rn "crypto\.DEFAULT_ENCODING" --include="*.js" --include="*.ts" src/

# Check for unhandled promise rejection patterns (CRITICAL for Node 15+)
grep -rn "\.then\(" --include="*.js" --include="*.ts" src/ | grep -v "\.catch"
grep -rn "async.*=>" --include="*.js" --include="*.ts" src/

# Check for import assertions (Node 22+ change)
grep -rn "assert { type:" --include="*.js" --include="*.ts" src/

# Check for native modules
npm ls 2>/dev/null | grep -E 'node-gyp|node-pre-gyp|prebuild|napi'
find node_modules -name "*.node" -type f 2>/dev/null

# Check for deprecated packages
grep -E "node-sass|grpc|request" package.json
```

### Critical Blockers Checklist

- [ ] No `new Buffer()` usage - must use `Buffer.from()`, `Buffer.alloc()`
- [ ] No `url.parse()` - must use `new URL()`
- [ ] No `require('domain')` - must refactor error handling
- [ ] No unhandled promise rejections - all promises must have catch handlers
- [ ] Webpack version ≥ 5 (Webpack 4 fails on Node 17+)
- [ ] No `util.log()`, `util.print()`, `util.puts()` usage
- [ ] No `crypto.DEFAULT_ENCODING` usage
- [ ] No legacy OpenSSL cipher usage

## Phase 2: Breaking Changes by Version

### Node 13 Breaking Changes

**1. HTTP Parser Changed to llhttp**
```javascript
// Generally transparent, but edge cases in HTTP parsing may differ
// Test all HTTP-related functionality thoroughly
```

**2. Worker Threads Stable**
- Worker threads API stabilized
- May affect existing worker implementations

### Node 14 Breaking Changes

**1. V8 8.1 - ES2020 Features**
```javascript
// New features available (no breaking, but may affect polyfills):
// - Optional chaining (?.)
// - Nullish coalescing (??)
// - Private class fields (#)
// - Dynamic import()

// Remove polyfills if present:
// DELETE: import 'core-js/features/optional-chaining';
```

**2. fs.rmdir() Recursive Deprecated**
```javascript
// OLD (deprecated in Node 14):
fs.rmdirSync(path, { recursive: true });

// NEW:
fs.rmSync(path, { recursive: true, force: true });
```

**3. Full ICU by Default**
```javascript
// Internationalization features now fully available
// May affect date/number formatting behavior
const formatter = new Intl.NumberFormat('de-DE');
// Results may differ from Node 12's small-icu build
```

### Node 15 Breaking Changes (MAJOR)

**1. Unhandled Promise Rejections Throw (CRITICAL)**

This is the most breaking change for Node 12 applications.

```javascript
// Node 12-14: Logs warning, continues execution
// Node 15+: Throws error, process exits!

// BROKEN (will crash on Node 15+):
someAsyncFunction(); // No .catch()

// BROKEN (will crash on Node 15+):
someAsyncFunction().then(result => {
  // handle result
}); // No .catch()

// BROKEN (empty catch still problematic):
someAsyncFunction().catch(() => {}); // Swallowing errors

// CORRECT:
someAsyncFunction().catch(err => {
  console.error('Operation failed:', err);
  // Handle error appropriately
});

// CORRECT (async/await):
try {
  await someAsyncFunction();
} catch (err) {
  console.error('Operation failed:', err);
}
```

**Global Handler (last resort):**
```javascript
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Application specific logging, throwing an error, or exit
});
```

**2. npm 7 (MAJOR BREAKING)**

```bash
# package-lock.json format changed (v2)
# Delete and regenerate:
rm package-lock.json
npm install

# Peer dependencies now auto-install!
# This may cause dependency conflicts
npm ls --all 2>&1 | grep "peer dep missing"

# Check for peer conflicts:
npm ls 2>&1 | grep "ERESOLVE\|peer dep"
```

**Common npm 7 issues:**
```bash
# Error: Could not resolve dependency
# Solution: Add --legacy-peer-deps (temporary) or fix versions
npm install --legacy-peer-deps

# Better solution: Fix package.json
# Add overrides section:
{
  "overrides": {
    "problematic-package": "^compatible-version"
  }
}
```

**3. AbortController Added**

```javascript
// Now globally available:
const controller = new AbortController();
const signal = controller.signal;

// Remove polyfills:
// DELETE: import 'abort-controller/polyfill';
```

### Node 16 Breaking Changes

**1. V8 9.0 Updates**
- Atomics.waitAsync
- RegExp match indices

**2. npm 7.x Default**
- All npm 7 changes apply here

**3. Apple Silicon Support**
- ARM64 binaries available

### Node 17 Breaking Changes (MAJOR)

**1. OpenSSL 3.0 (CRITICAL)**

```javascript
// Many legacy TLS operations will fail:
// Error: error:0308010C:digital envelope routines::unsupported

// Temporary workaround (NOT RECOMMENDED):
process.env.NODE_OPTIONS = '--openssl-legacy-provider';

// Or in package.json:
"scripts": {
  "start": "NODE_OPTIONS=--openssl-legacy-provider node app.js"
}

// CORRECT: Update cryptographic code to use modern algorithms
```

**Webpack 4 Specific Fix:**
```bash
# Webpack 4 uses MD4 hash which is removed in OpenSSL 3.0
# Either:
# 1. Upgrade to Webpack 5 (RECOMMENDED)
# 2. Use legacy provider:
export NODE_OPTIONS=--openssl-legacy-provider
```

**2. DNS Resolution Order Changed**

```javascript
// Node 12-16: IPv4 preferred
// Node 17+: OS-defined order (usually IPv6 first)

// If IPv6 causes issues:
const dns = require('dns');
dns.setDefaultResultOrder('ipv4first');
```

### Node 18 Breaking Changes

**1. Fetch API Global**

```javascript
// fetch() now globally available
// Remove polyfills:
// DELETE: import fetch from 'node-fetch';
// DELETE: const fetch = require('node-fetch');

// Use directly:
const response = await fetch('https://api.example.com');
```

**2. Test Runner Added**

```javascript
// Built-in test runner:
import test from 'node:test';
import assert from 'node:assert';

test('example', () => {
  assert.strictEqual(1 + 1, 2);
});
```

### Node 19-21 Breaking Changes

**1. HTTP Keep-Alive Default Changed (Node 19)**

```javascript
// keepAlive now defaults to true
// If explicit disable needed:
const http = require('http');
const agent = new http.Agent({ keepAlive: false });
```

### Node 22 Breaking Changes

**1. Import Assertions → Import Attributes (CRITICAL)**

```javascript
// OLD (Node 12-21):
import data from './data.json' assert { type: 'json' };

// NEW (Node 22+):
import data from './data.json' with { type: 'json' };
```

**Automated Migration:**
```bash
npx @nodejs/import-assertions-to-attributes ./src
```

**2. require() of ESM Experimental**

```bash
# Can now require() ESM modules:
node --experimental-require-module app.js
```

### Node 23-24 Breaking Changes

**1. V8 13.x Updates**
- Iterator helpers (stable)
- Promise.withResolvers()
- Resizable ArrayBuffers

**2. CVE-2025-59466 Fix**
- Minimum safe version: 24.13.0+

## Phase 3: npm Major Version Migration

### npm 6 → npm 7+ Changes Summary

| Feature | npm 6 | npm 7+ |
|---------|-------|--------|
| package-lock.json | v1 | v2/v3 |
| Peer dependencies | Manual install | Auto install |
| Workspaces | No | Yes |
| Overrides | No | Yes |
| `npm exec` | No | Yes (replaces npx internals) |

### Migration Steps

```bash
# 1. Backup existing lock file
cp package-lock.json package-lock.json.bak

# 2. Delete lock file
rm package-lock.json

# 3. Clear npm cache
npm cache clean --force

# 4. Delete node_modules
rm -rf node_modules

# 5. Install fresh
npm install

# 6. Check for peer dependency issues
npm ls 2>&1 | grep -E "peer|ERESOLVE"

# 7. Resolve conflicts with overrides or version updates
```

### Resolving Peer Dependency Conflicts

```json
// In package.json, add overrides section:
{
  "overrides": {
    "react": "^18.0.0",
    "some-package": {
      "another-package": "^2.0.0"
    }
  }
}
```

## Phase 4: Removed/Deprecated APIs

### APIs Removed from Node 12 to Node 24

| API | Status by Node 24 | Replacement |
|-----|-------------------|-------------|
| `new Buffer()` | Errors | `Buffer.from()`, `Buffer.alloc()` |
| `url.parse()` | Deprecated (warnings) | `new URL()` |
| `url.resolve()` | Deprecated | `new URL(relative, base)` |
| `url.format(urlObject)` | Deprecated | `url.format(URL)` or URL.toString() |
| `require('domain')` | Deprecated | Async error handling patterns |
| `util.log()` | Removed | Custom logging |
| `util.print()` | Removed | `process.stdout.write()` |
| `util.puts()` | Removed | `console.log()` |
| `os.tmpDir()` | Removed | `os.tmpdir()` (lowercase) |
| `tls.createSecurePair()` | Removed | `tls.TLSSocket` |
| `crypto.DEFAULT_ENCODING` | Removed | Explicit encoding |
| `crypto.createCipher()` | Removed | `crypto.createCipheriv()` |
| `crypto.createDecipher()` | Removed | `crypto.createDecipheriv()` |
| `require('punycode')` | Deprecated | `punycode` npm package |
| `process.binding()` | Removed | N/A (internal only) |
| `SlowBuffer` | Deprecated | `Buffer.allocUnsafeSlow()` |
| `assert.fail(msg)` | Deprecated signature | `assert.fail(actual, expected)` |
| `fs.exists()` | Deprecated | `fs.existsSync()` or `fs.access()` |

### Migration Code Examples

```javascript
// Buffer creation
// OLD:
const buf = new Buffer('hello');
const buf2 = new Buffer(10);
// NEW:
const buf = Buffer.from('hello');
const buf2 = Buffer.alloc(10);

// URL parsing
// OLD:
const urlParts = require('url').parse(urlString);
const resolved = require('url').resolve(base, relative);
// NEW:
const urlParts = new URL(urlString);
const resolved = new URL(relative, base);

// Crypto
// OLD:
const cipher = crypto.createCipher('aes192', 'password');
// NEW:
const cipher = crypto.createCipheriv('aes-192-cbc', key, iv);

// Temp directory
// OLD:
const tmp = os.tmpDir();
// NEW:
const tmp = os.tmpdir();

// Punycode
// OLD:
const punycode = require('punycode');
// NEW:
const punycode = require('punycode/'); // from npm package

// Domain (complete refactor needed)
// OLD:
const domain = require('domain');
const d = domain.create();
d.on('error', (err) => { /* handle */ });
d.run(() => { /* code */ });
// NEW: Use async/await with try/catch or process error handlers
process.on('uncaughtException', (err) => { /* handle */ });
process.on('unhandledRejection', (reason) => { /* handle */ });
```

## Phase 5: Native Modules

### Modules Requiring Rebuild or Replacement

| Module | Action Required |
|--------|-----------------|
| `node-sass` | Replace with `sass` (Dart Sass) |
| `grpc` | Replace with `@grpc/grpc-js` |
| `bcrypt` (<5.0) | Update to `bcrypt@5.1+` or use `bcryptjs` |
| `canvas` | Rebuild required |
| `sharp` | Rebuild required |
| `sqlite3` | Rebuild or switch to `better-sqlite3` |
| `node-gyp` | Update to latest |
| All native modules | Rebuild required |

### Migration Commands

```bash
# Delete everything
rm -rf node_modules package-lock.json pnpm-lock.yaml

# Use target Node version
nvm use 24

# Install fresh
npm install  # or pnpm install

# Force rebuild native modules
npm rebuild
```

### node-sass → sass Migration

```bash
# Remove node-sass
npm uninstall node-sass

# Install Dart Sass
npm install -D sass

# No code changes needed - sass-loader auto-detects
```

### grpc → @grpc/grpc-js Migration

```javascript
// OLD:
const grpc = require('grpc');
// NEW:
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

// API is mostly compatible, test thoroughly
```

## Phase 6: Framework Considerations

### Framework Compatibility Matrix

| Framework | Node 12 | Node 18 | Node 24 |
|-----------|---------|---------|---------|
| Express 4.x | ✅ | ✅ | ✅ |
| Express 5.x | ❌ | ✅ | ✅ |
| Webpack 4.x | ✅ | ⚠️ OpenSSL | ❌ |
| Webpack 5.x | ✅ | ✅ | ✅ |
| Next.js 10.x | ✅ | ❌ | ❌ |
| Next.js 13.x | ❌ | ✅ | ✅ |
| Next.js 14+ | ❌ | ✅ | ✅ |
| React 16.x | ✅ | ✅ | ✅ |
| React 18+ | ✅ | ✅ | ✅ |
| TypeScript 4.x | ✅ | ✅ | ✅ |
| TypeScript 5.x | ❌ | ✅ | ✅ |

### Create React App Migration

```bash
# If using react-scripts 4.x (Webpack 4):
# Option 1: Upgrade react-scripts
npm install react-scripts@5

# Option 2: Use legacy provider (temporary)
export NODE_OPTIONS=--openssl-legacy-provider

# Option 3: Migrate to Vite (RECOMMENDED)
npm create vite@latest my-app -- --template react-ts
```

### Next.js Migration Path

| If on Next.js | Upgrade to |
|---------------|------------|
| 10.x-12.x | 13.x or 14.x |
| 13.x | 14.x or 15.x |
| 14.x | No change needed |

## Phase 7: Testing Strategy

### Pre-Migration Baseline

```bash
# Document current state
echo "Node version: $(node --version)" > .migration-baseline.txt
echo "npm version: $(npm --version)" >> .migration-baseline.txt
npm test 2>&1 | tee .migration-test-baseline.txt
npm run build 2>&1 | tee .migration-build-baseline.txt
```

### Staged Testing Protocol

For each migration stage:

```bash
# 1. Switch Node version
nvm use <target-version>

# 2. Clean install
rm -rf node_modules package-lock.json
npm install

# 3. Build
npm run build 2>&1 | tee .migration-build-$(node --version).txt

# 4. Test
npm test 2>&1 | tee .migration-test-$(node --version).txt

# 5. Compare
diff .migration-test-baseline.txt .migration-test-$(node --version).txt
```

### Critical Test Areas

| Area | Why It's Important |
|------|-------------------|
| Promise handling | Node 15+ exits on unhandled rejections |
| HTTP/HTTPS | OpenSSL 3.0 changes |
| Crypto operations | Algorithm deprecations |
| File operations | fs.rmdir recursive deprecated |
| Date/Number formatting | ICU changes |
| Native module functionality | Rebuild required |

## Phase 8: CI/CD Updates

### Dockerfile Migration

```dockerfile
# OLD
FROM node:12-alpine

# NEW
FROM node:24.13.0-alpine

# Important: Use specific version, not just "24"
```

### GitHub Actions

```yaml
# OLD
- uses: actions/setup-node@v4
  with:
    node-version: '12'

# NEW
- uses: actions/setup-node@v4
  with:
    node-version: '24'
```

### Bitbucket Pipelines

```yaml
# OLD
image: node:12

# NEW
image: node:24.13.0
```

### .nvmrc / .node-version

```bash
# Update version file
echo "24.13.0" > .nvmrc
# OR
echo "24.13.0" > .node-version
```

## Common Migration Errors

### Error: UnhandledPromiseRejectionWarning → Process Exit

```
UnhandledPromiseRejectionWarning: Unhandled promise rejection.
This error originated either by throwing inside of an async function...
```

**Solution:** Add proper error handling to all promises.

### Error: digital envelope routines::unsupported

```
Error: error:0308010C:digital envelope routines::unsupported
```

**Solution:**
1. Upgrade Webpack to 5.x (RECOMMENDED)
2. Use `NODE_OPTIONS=--openssl-legacy-provider` (temporary)

### Error: primordials is not defined

```
ReferenceError: primordials is not defined
```

**Solution:** Upgrade gulp to 4.x+
```bash
npm install gulp@4
```

### Error: Cannot find module 'punycode'

```
Error: Cannot find module 'punycode'
```

**Solution:**
```bash
npm install punycode
# Then use:
const punycode = require('punycode/');
```

### Error: ERESOLVE unable to resolve dependency tree

```
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Solution:**
1. Update conflicting packages
2. Use overrides in package.json
3. Temporary: `npm install --legacy-peer-deps`

### Error: The engine "node" is incompatible

```
error package@version: The engine "node" is incompatible with this module.
```

**Solution:** Update the package or modify package.json engines field.

## Validation Checklist

### Pre-Commit Validation

- [ ] All deprecated API calls replaced
- [ ] All promises have error handlers
- [ ] Native modules rebuilt
- [ ] npm install completes without peer errors
- [ ] Build succeeds without errors
- [ ] TypeScript compilation clean
- [ ] ESLint passing
- [ ] All tests passing
- [ ] Dockerfile updated
- [ ] CI/CD pipelines updated
- [ ] .nvmrc / .node-version updated
- [ ] package.json engines updated

### Post-Deploy Validation

- [ ] Application starts without errors
- [ ] All endpoints responding correctly
- [ ] No runtime deprecation warnings
- [ ] No unhandled rejection crashes
- [ ] TLS/HTTPS connections working
- [ ] Performance baseline maintained
- [ ] Error rates unchanged
- [ ] Memory usage stable
- [ ] Log files show no new warnings

## Rollback Plan

### Immediate Rollback

```bash
# Revert to previous branch
git checkout main

# Or reset to pre-upgrade commit
git reset --hard HEAD~1

# Restore Node version
nvm use 12

# Clean and reinstall
rm -rf node_modules package-lock.json
npm install

# Verify
npm test
npm run build
```

### Docker Rollback

```bash
# Revert to previous image
docker tag myapp:previous myapp:latest
docker compose down && docker compose up -d
```

---

**Target Version: 24.13.0+ (CVE-2025-59466 patched)**

**This migration is CRITICAL for security compliance. Node 12 has been EOL for 3+ years with numerous unpatched CVEs. Prioritize this migration immediately.**

*For staged migration, refer to the appropriate version-specific guides as you progress through each stage.*

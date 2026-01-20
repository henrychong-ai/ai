# Node.js 16 to 24 Migration Guide

**CRITICAL: Node 16 reached End-of-Life on September 11, 2023. This is an urgent security migration spanning 3 major versions.**

## Migration Overview

This guide covers the complete migration path from Node.js 16 → 24, aggregating all breaking changes across 8 major versions (16 → 17 → 18 → 19 → 20 → 21 → 22 → 23 → 24).

### Impact Assessment

| Category | Severity | Description |
|----------|----------|-------------|
| Security | 🔴 CRITICAL | Node 16 has unpatched CVEs including CVE-2025-59466 |
| OpenSSL | 🔴 HIGH | Major TLS/crypto changes in v17-18 |
| Module System | 🟠 MEDIUM | Import assertions → attributes |
| APIs | 🟡 MEDIUM | Multiple deprecated APIs removed |
| Native Modules | 🟠 MEDIUM | Rebuild required |
| V8 Engine | 🟢 LOW | New features, minimal breaking |

## Phase 1: Pre-Migration Analysis

### Identify Breaking Dependencies

```bash
# Check for native modules that need rebuild
npm ls | grep -E "node-gyp|node-pre-gyp"

# Check for import assertion syntax
grep -r "assert { type:" src/

# Check for removed/deprecated APIs
grep -r "url.parse\|new Buffer\|require('punycode')" src/
```

### Critical Blockers Checklist

- [ ] Webpack version ≥ 5 (Webpack 4 breaks on Node 18+)
- [ ] No CommonJS-only dependencies in ESM context
- [ ] No legacy OpenSSL cipher usage
- [ ] No `url.parse()` - use `URL` constructor
- [ ] No `new Buffer()` - use `Buffer.from()`

## Phase 2: Breaking Changes by Version

### Node 17 Breaking Changes

**1. OpenSSL 3.0 (CRITICAL)**

Node 17 upgraded from OpenSSL 1.1 to OpenSSL 3.0, causing significant TLS changes.

```javascript
// OLD: May fail on Node 17+
const https = require('https');
https.request({
  hostname: 'legacy-server.com',
  // Legacy cipher will fail
});

// NEW: May need legacy provider or server upgrade
// Either upgrade server TLS config or use workaround:
process.env.NODE_OPTIONS = '--openssl-legacy-provider';
```

**Common Errors:**
```
Error: error:0308010C:digital envelope routines::unsupported
```

**Webpack 4 Fix (if stuck on Webpack 4):**
```bash
export NODE_OPTIONS=--openssl-legacy-provider
# Or in package.json scripts
"start": "NODE_OPTIONS=--openssl-legacy-provider webpack serve"
```

**RECOMMENDED:** Upgrade Webpack to v5 instead of using legacy provider.

**2. DNS Resolution Order Changed**

```javascript
// Node 16: IPv4 preferred
// Node 17+: OS-defined order (usually IPv6 first)

// If IPv6 causes issues, force IPv4:
const dns = require('dns');
dns.setDefaultResultOrder('ipv4first');

// Or in application startup:
require('dns').setDefaultResultOrder('ipv4first');
```

**3. V8 Engine 9.4 → 9.5**
- New features: Array.findLast(), Array.findLastIndex()
- Improved RegExp match indices

### Node 18 Breaking Changes

**1. TLS Secure Renegotiation Required**

Servers must support secure renegotiation or connections fail.

```javascript
// If connecting to legacy servers:
const tls = require('tls');
const socket = tls.connect({
  host: 'legacy-server.com',
  port: 443,
  rejectUnauthorized: false, // Only if absolutely necessary
  secureOptions: require('constants').SSL_OP_LEGACY_SERVER_CONNECT
});
```

**2. Fetch API Added (global)**

`fetch()` is now available globally - may conflict with polyfills.

```javascript
// Remove fetch polyfills
// DELETE: import fetch from 'node-fetch';
// DELETE: const fetch = require('node-fetch');

// Now use global:
const response = await fetch('https://api.example.com');
```

**3. Test Runner Added**

Built-in test runner available via `node:test`:
```javascript
import test from 'node:test';
import assert from 'node:assert';

test('example', () => {
  assert.strictEqual(1 + 1, 2);
});
```

### Node 19 Breaking Changes

**1. HTTP(S) KeepAlive Default Changed**

```javascript
// Node 19+: keepAlive defaults to true
// May need explicit disable for specific cases:
const http = require('http');
const agent = new http.Agent({ keepAlive: false });
```

**2. V8 10.7 Updates**
- Hashbang grammar now standard
- Array.fromAsync() (staged)

### Node 20 Breaking Changes

**1. Permission Model (Experimental)**

New experimental permission system - be aware if using.

**2. ESM Resolution Stability**

ESM loader hooks stable - may affect custom loaders.

**3. ARM64 Windows Support**

Now officially supported.

### Node 22 Breaking Changes

**1. Import Assertions → Import Attributes (CRITICAL)**

```javascript
// OLD (Node 16-21): assert syntax
import data from './data.json' assert { type: 'json' };

// NEW (Node 22+): with syntax
import data from './data.json' with { type: 'json' };
```

**Automated Migration:**
```bash
npx @nodejs/import-assertions-to-attributes ./src
```

**2. require() of ES Modules (Experimental)**

Can now require() ESM modules with flag:
```bash
node --experimental-require-module app.js
```

**3. V8 12.4+ Features**
- Set methods: intersection(), union(), difference()
- Array.fromAsync()
- Well-formed Unicode strings

### Node 23/24 Breaking Changes

**1. V8 13.x Updates**
- Iterator helpers (stable)
- Promise.withResolvers()
- Resizable ArrayBuffers

**2. Node 24 CVE Fixes**

Minimum safe version: 24.13.0+ (CVE-2025-59466 patched)

## Phase 3: Removed/Deprecated APIs

### APIs Removed in This Range

| API | Removed In | Replacement |
|-----|------------|-------------|
| `url.parse()` | Deprecated 18 | `new URL()` |
| `new Buffer()` | Deprecated 10, errors 17+ | `Buffer.from()`, `Buffer.alloc()` |
| `require('punycode')` | Deprecated 21 | `punycode` npm package |
| `process.binding()` | Deprecated | N/A - internal only |
| `SlowBuffer` | Deprecated | `Buffer.allocUnsafeSlow()` |

### Migration Examples

```javascript
// URL parsing
// OLD:
const urlParts = require('url').parse(urlString);
// NEW:
const urlParts = new URL(urlString);

// Buffer creation
// OLD:
const buf = new Buffer('hello');
// NEW:
const buf = Buffer.from('hello');

// Punycode
// OLD:
const punycode = require('punycode');
// NEW:
const punycode = require('punycode/'); // from npm package
```

## Phase 4: Native Modules

### Modules Requiring Rebuild

All native (C++) modules must be rebuilt:
- `better-sqlite3`
- `sharp`
- `bcrypt`
- `canvas`
- `node-sass` → migrate to `sass` (Dart)
- `sqlite3`
- `grpc`

### Rebuild Commands

```bash
# Delete node_modules and lockfile
rm -rf node_modules pnpm-lock.yaml

# Use correct Node version
nvm use 24

# Reinstall
pnpm install

# Force rebuild native modules
pnpm rebuild
```

### Common Native Module Issues

**node-sass → sass migration:**
```bash
# Remove node-sass
pnpm remove node-sass

# Install Dart Sass
pnpm add -D sass

# Update webpack config (if applicable)
# sass-loader automatically uses sass
```

**bcrypt issues:**
```bash
# If rebuild fails, try:
pnpm add bcrypt@latest
# Or switch to bcryptjs (pure JS):
pnpm remove bcrypt
pnpm add bcryptjs
```

## Phase 5: Framework Considerations

### Webpack

| Webpack Version | Node 24 Compatible? | Action |
|-----------------|---------------------|--------|
| 4.x | ❌ No | Upgrade to 5.x |
| 5.x | ✅ Yes | Minor updates may be needed |

**Webpack 4 → 5 Migration:**
- Remove `node` polyfill plugins
- Update loader configurations
- Check `output.library` format changes

### React (Create React App)

CRA with Webpack 4 requires:
```bash
# Set environment variable
export NODE_OPTIONS=--openssl-legacy-provider

# Or eject and upgrade Webpack
npm run eject
# Then upgrade webpack to 5.x
```

**RECOMMENDED:** Migrate to Vite or Next.js instead.

### Next.js

| Next.js Version | Node 24 Compatible? | Notes |
|-----------------|---------------------|-------|
| 12.x | ⚠️ Partial | Minimum Node 18 |
| 13.x | ✅ Yes | Recommended |
| 14.x | ✅ Yes | Optimal |
| 15.x | ✅ Yes | Latest |

## Phase 6: Testing Strategy

### Pre-Migration Baseline

```bash
# Document Node 16 baseline
node --version > .migration-baseline
npm test 2>&1 | tee .migration-test-baseline
npm run build 2>&1 | tee .migration-build-baseline
```

### Incremental Testing

For complex applications, consider incremental jumps:
1. 16 → 18 (LTS) - Major TLS changes
2. 18 → 20 (LTS) - Stability checkpoint
3. 20 → 22 (LTS) - Import assertions
4. 22 → 24 (LTS) - Final target

### Test Each Stage

```bash
# At each version:
nvm use <version>
rm -rf node_modules pnpm-lock.yaml
pnpm install
pnpm build
pnpm test
```

## Phase 7: CI/CD Updates

### Dockerfile

```dockerfile
# OLD
FROM node:16-alpine

# NEW
FROM node:24.13.0-alpine
```

### GitHub Actions

```yaml
# OLD
- uses: actions/setup-node@v4
  with:
    node-version: '16'

# NEW
- uses: actions/setup-node@v4
  with:
    node-version: '24'
```

### Bitbucket Pipelines

```yaml
# OLD
image: node:16

# NEW
image: node:24.13.0
```

## Common Migration Errors

### Error: digital envelope routines::unsupported

```bash
# Cause: OpenSSL 3.0 incompatibility
# Solution 1: Update crypto usage
# Solution 2 (temporary):
export NODE_OPTIONS=--openssl-legacy-provider
```

### Error: ERR_OSSL_EVP_UNSUPPORTED

```bash
# Same as above - OpenSSL 3.0 issue
# Check for MD4/MD5 usage in legacy code
```

### Error: primordials is not defined

```bash
# Cause: Old gulp version (<4.0)
# Solution: Upgrade gulp to 4.x+
npm install gulp@4
```

### Error: Cannot find module 'punycode'

```bash
# Cause: Internal punycode removed
# Solution: Install npm package
pnpm add punycode
# Then use:
const punycode = require('punycode/');
```

## Validation Checklist

### Pre-Commit Validation

- [ ] All tests passing
- [ ] Build succeeds without warnings
- [ ] No deprecated API warnings in console
- [ ] TypeScript compilation clean
- [ ] ESLint passing
- [ ] Native modules rebuilt
- [ ] Dockerfile updated
- [ ] CI/CD pipelines updated

### Post-Deploy Validation

- [ ] Application starts without errors
- [ ] All endpoints responding
- [ ] No runtime deprecation warnings
- [ ] Performance baseline maintained
- [ ] Error rates unchanged
- [ ] Memory usage stable

## Rollback Plan

```bash
# If migration fails:
git checkout main
nvm use 16
rm -rf node_modules pnpm-lock.yaml
pnpm install
pnpm build
pnpm test
```

---

**Target Version: 24.13.0+ (CVE-2025-59466 patched)**

*This migration is critical for security compliance. Node 16 EOL means no security patches.*

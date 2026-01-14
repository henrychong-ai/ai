# Node.js 22 to 24 Migration Guide

Specific breaking changes and migration steps for Node.js v22 → v24.

## Key Changes Summary

| Change | Impact | Action Required |
|--------|--------|-----------------|
| OpenSSL 3.5 | High | Review crypto/TLS code |
| V8 13.6 | Medium | Check deprecated APIs |
| npm 11 | Medium | Review npm scripts |
| C++20 requirement | Low (native modules) | Rebuild required |
| AsyncLocalStorage perf | Low | None (improvement) |

## Critical: OpenSSL 3.5 Changes

### Minimum Key Lengths

OpenSSL 3.5 enforces stricter minimum key lengths:

| Algorithm | Minimum Size |
|-----------|--------------|
| RSA | 2048 bits |
| DSA | 2048 bits |
| DH | 2048 bits |

**Breaking:** Keys below these sizes will fail.

### Check Your Keys
```bash
# Check RSA key length
openssl rsa -in key.pem -text -noout | grep "Private-Key"

# Check certificate key length
openssl x509 -in cert.pem -text -noout | grep "Public-Key"
```

### Migration Actions

1. **Self-signed certificates:** Regenerate with 2048+ bits
2. **Test certificates:** Update fixtures
3. **External APIs:** Verify endpoint certificates
4. **Legacy systems:** May need compatibility layer

### Generating New Keys
```bash
# RSA 2048-bit (minimum compliant)
openssl genrsa -out key.pem 2048

# RSA 4096-bit (recommended)
openssl genrsa -out key.pem 4096
```

## V8 13.6 Changes

### New JavaScript Features

**RegExp.escape():**
```javascript
const escaped = RegExp.escape('foo.bar'); // 'foo\\.bar'
```

**Promise.try():**
```javascript
const result = await Promise.try(() => {
  return synchronousOrAsync();
});
```

### Deprecated APIs

**Buffer() constructor:**
```javascript
// Deprecated (security risk)
new Buffer(size);

// Use instead
Buffer.alloc(size);     // Initialized to zeros
Buffer.allocUnsafe(size); // Uninitialized (faster)
Buffer.from(data);      // From existing data
```

### Removed Features

Check for usage of these removed APIs:
- `process.binding()` - Use N-API instead
- Legacy URL parser - Use WHATWG URL

## npm 11 Changes

### Package Lock Format

npm 11 uses lockfile version 4:
```json
{
  "lockfileVersion": 4
}
```

**Note:** pnpm users unaffected.

### Script Execution

Stricter lifecycle script handling:
- Pre/post scripts require explicit enable
- Some implicit behaviors removed

## Native Module Considerations

### C++20 Requirement

Node 24 native modules require C++20 compiler:
- GCC 10+
- Clang 10+
- MSVC 2019+

### Common Native Modules

These likely need rebuild:
| Module | Status |
|--------|--------|
| `better-sqlite3` | Rebuild required |
| `sharp` | Rebuild required |
| `bcrypt` | Rebuild required |
| `node-canvas` | Rebuild required |

```bash
# Force rebuild all native modules
npm rebuild
```

## AsyncLocalStorage Performance

Node 24 significantly improves `AsyncLocalStorage` performance:
- No code changes needed
- 20-40% faster in benchmarks
- Benefits frameworks using ALS (Next.js, etc.)

## Testing Checklist

### Pre-Migration
- [ ] All tests passing on Node 22
- [ ] Audit cryptographic key lengths
- [ ] List all TLS/SSL connections
- [ ] Document native module versions
- [ ] Check for deprecated Buffer usage

### Migration Steps
1. [ ] Audit and upgrade cryptographic keys
2. [ ] Update `.nvmrc` to `24.13.0`
3. [ ] Delete node_modules and lockfile
4. [ ] Install dependencies with Node 24
5. [ ] Rebuild native modules
6. [ ] Fix any Buffer() constructor usage
7. [ ] Run type checking
8. [ ] Run linting
9. [ ] Run full test suite
10. [ ] Test TLS connections

### Post-Migration
- [ ] Compare test coverage
- [ ] Verify TLS connections work
- [ ] Check for deprecation warnings
- [ ] Performance benchmark (should improve)
- [ ] Update Dockerfile
- [ ] Update CI/CD pipelines

## Common Issues

### Issue: TLS Handshake Failures
```
Error: ssl3_get_server_certificate: certificate verify failed
```
**Possible causes:**
1. Server using < 2048-bit keys
2. Weak cipher suites
3. Self-signed cert with weak key

**Fix:** Contact server admin or regenerate certificates

### Issue: Crypto Key Rejection
```
Error: digital envelope routines::unsupported
```
**Fix:** Regenerate keys with 2048+ bits

### Issue: Native Module Build Failures
```
error: expected ';' before '}' token
```
**Fix:** Ensure C++20 compiler available, then `npm rebuild`

## Dockerfile Update

```dockerfile
# Update base image
- FROM node:22.22.0-alpine
+ FROM node:24.13.0-alpine

# Ensure build tools for native modules
RUN apk add --no-cache python3 make g++
```

## Environment Variables

### New/Changed Variables

```bash
# OpenSSL legacy provider (escape hatch - NOT recommended)
NODE_OPTIONS=--openssl-legacy-provider

# Better: Fix the underlying issue
```

### Removed Variables

- `NODE_PENDING_DEPRECATION` → Now default behavior

## Performance Notes

Node 24 provides:
- Faster startup (~10-15%)
- Improved AsyncLocalStorage (20-40%)
- Better garbage collection
- Enhanced WebSocket performance

## Security Notes

Node 24.13.0 includes patches for:
- CVE-2025-59466 (async_hooks DoS)
- Various OpenSSL security fixes

**Do not use versions below 24.13.0 in production.**

---

*Minimum safe version: 24.13.0 (CVE-2025-59466 patched)*

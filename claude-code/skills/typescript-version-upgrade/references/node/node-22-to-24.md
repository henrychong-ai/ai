# Node.js 22 → 24

Primary source: https://nodejs.org/en/blog/migrations/v22-to-v24. Node 24 is the current Active LTS line until 2026-10-20.

| Area | Node 22 | Node 24 |
|---|---|---|
| V8 | 12.4 | 13.6 |
| npm (bundled) | 10.9 | 11.x (lockfile format unchanged, `lockfileVersion: 3`) |
| OpenSSL | 3.x | 3.5, default security level 2 |

## Breaking changes

### OpenSSL 3.5, security level 2

- RSA, DSA and DH keys shorter than 2048 bits are rejected.
- ECC keys shorter than 224 bits are rejected.
- RC4 cipher suites are rejected.

```bash
openssl rsa  -in key.pem  -text -noout | grep "Private-Key"
openssl x509 -in cert.pem -text -noout | grep "Public-Key"
```

Inventory every TLS peer and key the service uses (bank and custodian APIs, mTLS certs, JWT signing keys, test fixtures). Regenerate short keys; for a third-party endpoint with a weak key, raise it with the provider — do not lower the security level in production without explicit approval.

### Removed or runtime-deprecated APIs, with codemods

| Change | Codemod (`npx codemod run …`) |
|---|---|
| `crypto` RSA-PSS options `hash`/`mgf1Hash` → `hashAlgorithm`/`mgf1HashAlgorithm` | `@nodejs/crypto-rsa-pss-update` |
| `dirent.path` → `dirent.parentPath` | `@nodejs/dirent-path-to-parent-path` |
| `fs.F_OK`/`R_OK`/`W_OK`/`X_OK` → `fs.constants.*` | `@nodejs/fs-access-mode-constants` |
| `fs.truncate(fd, …)` → `fs.ftruncate(fd, …)` | `@nodejs/fs-truncate-fd-deprecation` |
| HTTP/2 priority signalling removed | `@nodejs/http2-priority-signaling` |
| `process.assert()` → `node:assert` | `@nodejs/process-assert-to-node-assert` |
| `tls.createSecurePair()` → `tls.TLSSocket` | `@nodejs/tls-create-secure-pair-to-tls-socket` |

The userland-migrations repo also publishes an aggregate recipe, `npx codemod run @nodejs/v22-to-v24`; run the individual recipes if you want reviewable, separate diffs.

### Other behaviour changes (test for them)

- Stricter `fetch()` spec compliance and `AbortSignal` validation.
- Stream/pipe errors that were swallowed now throw.
- Test runner defaults changed (if you use `node --test`).

### Platform and toolchain

- No prebuilt binaries for 32-bit Windows (from 23) or 32-bit armv7 Linux (from 24).
- macOS 13.5 minimum.
- Native addons build against V8 13.6 and may need a C++20 compiler; prefer Node-API packages to avoid ABI churn. Building Node itself needs gcc 12.2+ / Xcode 16.1+.

## Checklist

1. Audit keys and TLS peers (above).
2. Run the codemods that match `grep` hits; review each diff.
3. Update `.nvmrc`, `engines`, all Dockerfile stages, pipeline images, `@types/node@^24` together.
4. `<pm> install`, `<pm> rebuild` (keep the lockfile). In Alpine images, add `python3 make g++` only if a dependency compiles from source.
5. Run all gates; exercise every outbound TLS integration in a staging environment.
6. For the minimum patch, use the live lookup in `migration-overview.md` — do not copy a patch number from an old document.

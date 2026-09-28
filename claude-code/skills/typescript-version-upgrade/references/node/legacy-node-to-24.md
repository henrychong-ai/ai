# Legacy Node.js (12–18) → 24

For repos on an end-of-life line (Node 12, 14, 16 or 18). Every one of these lines is out of security support; the upgrade is a security remediation. After reaching 22, finish with `node-20-to-22.md` (for the crypto removal) and `node-22-to-24.md`.

End-of-life dates (from https://github.com/nodejs/Release `schedule.json`): 12 → 2022-04-30, 14 → 2023-04-30, 16 → 2023-09-11, 18 → 2025-04-30, 20 → 2026-04-30.

## Choose the path

| Starting line | Recommended path | Why |
|---|---|---|
| 18 | 18 → 22 → 24 | Few breaking changes; read `node-20-to-22.md` and `node-22-to-24.md` |
| 16 | 16 → 18 → 22 → 24 | OpenSSL 3 and DNS changes land at 17/18 |
| 12 / 14 | 12/14 → 16 → 18 → 22 → 24 | Unhandled-rejection exit (15) and npm 7 (15) need their own checkpoint |

A direct jump is acceptable only with strong test coverage; still work through every section below. At each stop: switch Node, `<pm> install`, `<pm> rebuild`, run the gates, record results in the baseline folder outside the worktree.

## Pre-migration scan

```bash
grep -rnE "new Buffer\(|url\.(parse|resolve)\(|require\(['\"]domain['\"]\)|util\.(log|print|puts)\(|os\.tmpDir\(|tls\.createSecurePair|crypto\.createCipher\(|crypto\.createDecipher\(|crypto\.DEFAULT_ENCODING" \
  --include=*.{js,cjs,mjs,ts,cts,mts} src/
grep -rn "assert *{ *type" --include=*.{js,mjs,ts,mts} src/
grep -E '"(node-sass|grpc|request|gulp)"' package.json
find node_modules -name '*.node' -type f | head
```

For unhandled promises, rely on tests run under `node --unhandled-rejections=strict` and a floating-promise lint rule (`/lint`), not on grep.

## Breaking changes by version

### Node 13–14
- HTTP parser switched to llhttp — edge-case HTTP parsing may differ; test raw HTTP handling.
- Full ICU by default (14) — `Intl` date/number formatting may change from small-ICU builds.
- `fs.rmdir(path, { recursive: true })` deprecated (runtime from 16, removed in 25) → `fs.rm(path, { recursive: true, force: true })` (codemod `@nodejs/rmdir`).
- V8 8.x adds optional chaining, nullish coalescing, private fields: polyfills and Babel plugins for these can go.

### Node 15 (critical)
- **Unhandled promise rejections terminate the process** (previously a warning). Every promise chain needs a handler; add a logged `process.on('unhandledRejection', …)` only as a last resort that still exits.
- **npm 7**: lockfile v2, peer dependencies auto-installed, `ERESOLVE` conflicts. Fix conflicts with version updates or `overrides`; `--legacy-peer-deps` is a temporary escape only.
- `AbortController` global — remove the polyfill.

### Node 16
- npm 7 default; Apple Silicon binaries.

### Node 17 (critical)
- **OpenSSL 3.0**: legacy algorithms (MD4, etc.) fail with `error:0308010C:digital envelope routines::unsupported` / `ERR_OSSL_EVP_UNSUPPORTED`. Fix the cause — Webpack 4 uses MD4, so upgrade to Webpack 5 (or `react-scripts@5`). `NODE_OPTIONS=--openssl-legacy-provider` is a temporary local workaround, never a production setting.
- **DNS order** follows the OS (often IPv6 first). If a peer is IPv4-only, `dns.setDefaultResultOrder('ipv4first')` at startup.

### Node 18
- Global `fetch` (Undici) — remove `node-fetch` where behaviour matches; test streaming bodies and timeouts.
- `node:test` built-in test runner.

### Node 19–21
- HTTP `keepAlive` defaults to `true` for the global agent (19) — watch for connection reuse against servers that close idle sockets.
- `require('punycode')` runtime-deprecated (21) — use the `punycode` npm package (`require('punycode/')`).

### Node 22 and 24
See `node-20-to-22.md` (import attributes, `createCipher` removal, `require(esm)` on by default) and `node-22-to-24.md` (OpenSSL 3.5 security level 2, fs/crypto/tls codemods).

## API status by Node 24

Check https://nodejs.org/api/deprecations.html for the exact status; the table below is a guide.

| API | Status on 24 | Replacement (codemod if any) |
|---|---|---|
| `new Buffer()` / `Buffer()` | Deprecated (DEP0005, warns for application code), still works | `Buffer.from()` / `Buffer.alloc()` |
| `SlowBuffer` | Runtime deprecation (24); removed in 25 | `Buffer.allocUnsafeSlow()` (`@nodejs/slow-buffer-to-buffer-alloc-unsafe-slow`) |
| `url.parse()` / `url.resolve()` | Deprecated (DEP0169 warns for application code) | `new URL()` (`@nodejs/node-url-to-whatwg-url`) |
| `util.log()` | Removed (23) | `console.log` (`@nodejs/util-log-to-console-log`) |
| `util.print()` / `util.puts()` | Removed (12) | `console.log` (`@nodejs/util-print-to-console-log`) |
| `os.tmpDir()` | Removed (14) | `os.tmpdir()` (`@nodejs/tmpdir-to-tmpdir`) |
| `tls.createSecurePair()` | Removed (24) | `tls.TLSSocket` (`@nodejs/tls-create-secure-pair-to-tls-socket`) |
| `crypto.createCipher()` / `createDecipher()` | Removed (22) | `createCipheriv()` — see the data-migration warning in `node-20-to-22.md` |
| `domain` module | Deprecated | Structured async error handling |
| `process.binding()` | Documentation-only deprecation (DEP0111), not removed | Public APIs |
| `assert.fail(actual, expected, …)` (multi-argument form) | Runtime deprecation (DEP0094); removed in 25 | `assert.fail(message)` or a specific assertion |
| `fs.exists()` (callback) | Documentation-only deprecation (DEP0034) | `fs.existsSync()` or `fs.promises.access()` |

Run each codemod with `npx codemod run @nodejs/<recipe>`.

## Dependencies that block the upgrade

| Package | Action |
|---|---|
| `node-sass` | Replace with `sass` (Dart Sass); `sass-loader` picks it up |
| `grpc` | Replace with `@grpc/grpc-js` (+ `@grpc/proto-loader`) |
| `bcrypt` < 5 | Upgrade, or switch to `bcryptjs` |
| `gulp` < 4 (`primordials is not defined`) | Upgrade to gulp 4+ |
| Webpack 4 / `react-scripts` 4 | Webpack 5 / `react-scripts@5`, or migrate to Vite |
| `request` | Unmaintained — replace with global `fetch` or `undici` |
| TypeScript < 5 | See `../typescript/typescript-legacy-to-5.md` (TypeScript 5 needs Node ≥14.17) |
| Next.js < 14 | See `../frameworks/nextjs-migrations.md`; current Next.js needs Node ≥20.9 |

## Validation

Pre-commit: deprecated calls replaced; no unhandled rejections under `--unhandled-rejections=strict`; native modules rebuilt and loading; install clean of peer errors; type check, lint, tests and build green; `.nvmrc`, `engines`, Dockerfile, pipeline images and `@types/node` aligned.

Post-deploy: service starts; endpoints respond; no runtime deprecation warnings in logs; TLS integrations work; error rate, latency and memory at baseline.

Rollback: `git revert` the merge and redeploy the previous image through your CI/CD pipeline.

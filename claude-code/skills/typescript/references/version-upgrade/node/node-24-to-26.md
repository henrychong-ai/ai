# Node.js 24 → 26

Recommended: stay on Node 24 for existing services and start new projects on Node 26 once it is LTS (2026-10-28). Node 24 enters Maintenance on 2026-10-20 and reaches end-of-life 2028-04-30.

Primary sources: the 26.0.0 changelog (https://github.com/nodejs/node/blob/main/doc/changelogs/CHANGELOG_V26.md) and https://nodejs.org/api/deprecations.html. At the time of writing nodejs.org has no v24-to-v26 migration page; check https://nodejs.org/en/learn/getting-started/userland-migrations for new codemods before starting.

| Area | Node 24 | Node 26 |
|---|---|---|
| V8 | 13.6 | 14.6 |
| `NODE_MODULE_VERSION` | 137 | 147 (every native addon must be rebuilt) |
| Corepack | bundled | **not bundled** (removed from Node 25+) |
| Temporal | not enabled by default | enabled by default |
| Undici (`fetch`) | 7.x | 8.x |

## Corepack is gone

Node 25 and later do not ship Corepack, so a bare `corepack enable` / `corepack install` fails in `node:26` images and fresh Node 26 installs. Install a pinned Corepack from npm first, then enable it; Corepack keeps doing its job — it installs the package manager pinned in `packageManager` (e.g. `"pnpm@10.x.y+sha512.<hash>"`) and refuses a download whose hash does not match. The pinned form is set in `../../tech-stack/version-policy.md`.

```dockerfile
FROM node:26-alpine AS builder
RUN npm install -g corepack@<pinned> && corepack enable
```

```yaml
# CI step script
- npm install -g corepack@<pinned> && corepack enable
- pnpm install --frozen-lockfile
```

Keep the `+sha512.` hash in `packageManager` (`corepack use pnpm@<version>` writes it). Check the current Corepack release with `npm view corepack version`. Update every Dockerfile, pipeline step and developer setup doc that runs a bare `corepack enable`.

## Removed (end-of-life) in Node 25 or 26

Node 25 was a short-lived Current line, so its removals arrive with 26. Status from https://nodejs.org/api/deprecations.html:

| ID | Removed | Replacement (codemod: `npx codemod run @nodejs/<recipe>`) |
|---|---|---|
| DEP0182 (26) | Short GCM auth tags without explicit `authTagLength` | Pass `authTagLength` to `createDecipheriv()` — **audit every AES-GCM decrypt path** |
| DEP0154 (25) | RSA-PSS `generateKeyPair` options `hash`/`mgf1Hash` | `hashAlgorithm`/`mgf1HashAlgorithm` (`crypto-rsa-pss-update`) |
| DEP0176 (25) | `fs.F_OK`/`R_OK`/`W_OK`/`X_OK` | `fs.constants.*` (`fs-access-mode-constants`) |
| DEP0147 (25) | `fs.rmdir(path, { recursive: true })` | `fs.rm(path, { recursive: true, force: true })` (`rmdir`) |
| DEP0030 (25) | `SlowBuffer` | `Buffer.allocUnsafeSlow()` (`slow-buffer-to-buffer-alloc-unsafe-slow`) |
| DEP0094 (25) | `assert.fail()` with more than one argument | `assert.fail(message)` or a specific assertion |
| DEP0173 (25) | `assert.CallTracker` | `node:test` mocks |
| DEP0123 (25) | TLS `servername` set to an IP address | Omit `servername` for IP peers |
| DEP0137 (25) | Closing `fs.FileHandle` on garbage collection | Close handles explicitly |
| DEP0132 (25) | `worker.terminate()` with a callback | Use the returned promise |
| DEP0160 (25) | `process.on('multipleResolves')` | Remove the handler |
| DEP0170 (25) | Invalid port in `url.parse()` | `new URL()` (`node-url-to-whatwg-url`) |
| DEP0063 (26) | `ServerResponse.prototype.writeHeader()` | `writeHead()` |
| DEP0125, DEP0193 (26) | `node:_stream_wrap`, `node:_stream_*` internals | `node:stream` exports |
| (26) | `--experimental-transform-types` flag | Run TypeScript through `tsx`, or compile with `tsc` |

The full list also covers `dgram` private APIs, `Module._debug()`, `ChildProcess._channel`, stream `open()` internals and `repl` classes without `new`; grep for anything the deprecations page lists as End-of-Life in v25.0.0 or v26.0.0.

## New runtime deprecations (warnings now, removal later)

- DEP0205 `module.register()` — move custom loaders to `module.registerHooks()` or remove them.
- DEP0203 passing a `CryptoKey` to `node:crypto` APIs; DEP0204 `KeyObject.from()` with a non-extractable `CryptoKey`.
- DEP0198 SHAKE digests without an explicit `outputLength`; DEP0031 `ecdh.setPublicKey()` (both from 25).
- DEP0201 passing `options.type` to `Duplex.toWeb()`.

Run tests with `--trace-deprecation` and fix every new warning.

## Other changes to test

- ML-KEM / ML-DSA PKCS#8 export defaults to seed-only format; asymmetric key import was unified — exercise key import/export paths.
- HTTP upgrade requests with bodies are handled differently; test WebSocket/upgrade endpoints.
- `localStorage` returns `undefined` when no storage file is configured.
- Temporal is available globally; if you load a Temporal polyfill, make sure it does not overwrite the native one.
- Building Node or native addons from source needs GCC 13.2+.

## ES target and types

- `@types/node@^26` in every workspace package.
- Node 26 supports ES2025; `target: "ES2025"` requires TypeScript 6.0+ (`@tsconfig/node26` uses `es2025`). See `../ecmascript/es-upgrade-checklist.md`.

## Checklist

1. `grep -rn "corepack" Dockerfile* bitbucket-pipelines.yml .github docs README.md` — put `npm install -g corepack@<pinned>` before every `corepack enable`.
2. `grep -rnE "writeHeader|_stream_|module\.register|experimental-transform-types|SlowBuffer|fs\.[FRWX]_OK|recursive: *true|authTag|CallTracker|multipleResolves" --include=*.{js,cjs,mjs,ts,cts,mts} .`
3. Update `.nvmrc` (major only), `engines`, all Dockerfile stages, pipeline images, `@types/node@^26`.
4. `<pm> install`, `<pm> rebuild` (keep the lockfile); confirm every native addon loads.
5. Run all gates with `--trace-deprecation`.
6. `node:lts*` tags switch to 26 on 2026-10-28 — replace them with `node:24-<variant>` before that date if the service is not ready.

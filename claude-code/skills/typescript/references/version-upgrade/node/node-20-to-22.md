# Node.js 20 → 22

Primary source: https://nodejs.org/en/blog/migrations/v20-to-v22 (read it before starting; it is updated as codemods land). Node 20 has been end-of-life since 2026-04-30 — treat any Node 20 repo as a security finding and continue to 24 (`node-22-to-24.md`) in the same programme.

| Area | Node 20 | Node 22 |
|---|---|---|
| V8 | 11.3 | 12.4 |
| npm (bundled) | 10.8 | 10.9 |
| OpenSSL | 3.0 | 3.0 early in the line, 3.5 in current 22.x |

Versions from `https://nodejs.org/dist/index.json`; re-check for the exact patch you deploy.

## Breaking changes

### Import assertions removed (`assert` → `with`)

The `assert` import syntax was removed in Node 22; the `with` form (available since Node 18.20) is required.

```javascript
// Before (fails to parse on 22)
import data from './data.json' assert { type: 'json' };
// After
import data from './data.json' with { type: 'json' };
```

```bash
npx codemod run @nodejs/import-assertions-to-attributes
```

TypeScript 6 also deprecates `assert` on imports (see `../typescript/typescript-5-to-6.md`).

### `crypto.createCipher()` / `createDecipher()` removed (DEP0106)

These used MD5 key derivation with no salt and a static IV. Replace with `createCipheriv()` / `createDecipheriv()` and a real KDF.

```bash
npx codemod run @nodejs/crypto-createcipheriv-migration
```

**Critical for money-moving code:** data encrypted with `createCipher()` cannot be decrypted by the migrated code. The codemod generates a fresh salt and IV that must be stored with the ciphertext. Plan a data migration (decrypt with the old scheme on Node 20, re-encrypt) before switching runtimes, and get explicit approval — this touches cryptographic operations.

## Behaviour changes worth testing

- `require()` of synchronous ES modules is enabled by default from 22.12 (and 20.19). Code that relied on `ERR_REQUIRE_ESM` to pick a code path changes behaviour.
- New globals and built-ins from V8 12.4: `Array.fromAsync`, `Set` methods (`union`, `intersection`, `difference`, …), `Promise.withResolvers`, iterator helpers. Local polyfills for these can now be removed.
- `node --watch` is stable in 22 (the test runner has been stable since 20); adoption is optional.

## Checklist

1. `grep -rn "assert *{ *type" --include=*.{js,mjs,ts,mts} .` and run the import-attributes codemod.
2. `grep -rn "createCipher(\|createDecipher(" .` — plan the crypto data migration if found.
3. Update `.nvmrc`, `engines`, Dockerfile stages, pipeline images, `@types/node@^22` together.
4. `<pm> install`, `<pm> rebuild` (keep the lockfile).
5. Run all gates from `../upgrade-protocol.md` Phase 5.
6. Continue with `node-22-to-24.md` — 22 is in Maintenance and 24 is the current LTS line.

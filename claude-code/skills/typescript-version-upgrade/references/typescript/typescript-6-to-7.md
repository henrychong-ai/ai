# TypeScript 6.0 → 7.0 (native compiler)

**Recommended:** use TS 7 only as a **type-check-only lane** where no tool needs the compiler API, and keep the project's `typescript` dependency on `~6.0`.

Primary source: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/ (7.0.0, 2026-07-08). TypeScript 7 is the Go port: the `typescript` npm package now installs a native `tsc` binary (8–12× faster type checks).

## Why not a straight upgrade

- **No compiler API until 7.1.** Tools that `require('typescript')` for its API cannot use 7.0: typescript-eslint (peer `typescript <6.1.0` on 2026-09-28), ts-jest (`<7`), ts-node, tsup's `dts` build, API-based bundler plugins, and framework type-check steps that load the API. Check each: `npm view <tool> peerDependencies`.
- 6.0 deprecations become hard errors (`TS5102`/`TS5108` "has been removed"), and `ignoreDeprecations: "6.0"` is rejected.
- Defaults from 6.0 hold; `stableTypeOrdering` is always on.

## Pre-conditions

1. The repo is on 6.0 with a clean `tsc --noEmit`, **no** `ignoreDeprecations`, and every deprecated option removed (`typescript-5-to-6.md`).
2. `tsc --stableTypeOrdering --noEmit` is also clean under 6.0, so 7.0 output ordering matches.

## Add the type-check lane

The default lane leaves the project's pinned `typescript@~6.0` untouched and runs the 7.0 compiler on demand:

```bash
pnpm dlx --package=typescript@^7.0 tsc --noEmit -p tsconfig.json
npx --yes --package=typescript@^7.0 -- tsc --noEmit -p tsconfig.json    # npm equivalent
```

As a script: `"typecheck:native": "pnpm dlx --package=typescript@^7.0 tsc --noEmit -p tsconfig.json"`. Nothing in `node_modules` or the lockfile changes, so every tool keeps using 6.0.

### When 7.0 must live in the lockfile

If CI must not download at run time, or you are preparing to make 7.x primary, install both side by side using the TypeScript team's layout — 6.0 stays importable as `typescript` with its binary renamed `tsc6`; 7.0 comes in under an alias:

```json
{
  "devDependencies": {
    "typescript": "npm:@typescript/typescript6@~6.0.2",
    "@typescript/native": "npm:typescript@^7.0.2"
  },
  "scripts": {
    "build": "tsc6 -p tsconfig.build.json",
    "typecheck": "tsc6 --noEmit",
    "typecheck:native": "tsc --noEmit"
  }
}
```

- `require('typescript')` still resolves to 6.0, so typescript-eslint, ts-jest and other API tools keep working.
- **Once 7.0 is installed, `tsc` means 7.0** in `.bin`, `pnpm exec tsc` and `npx tsc` — npm and pnpm both link the aliased 7.0 package's `tsc`. Rename every script that must stay on 6.0 (emit, declaration builds) to `tsc6`.
- Confirm after install: `<pm> exec tsc6 --version` (6.0.x), `<pm> exec tsc --version` (7.0.x), `node -p "require('typescript').version"` (6.0.x).

## CI

Run `typecheck:native` as an extra step and compare with the 6.0 result for a few weeks; make it the gating type check once both agree. Useful flags: `--checkers <n>` (type-checker workers, default 4), `--builders <n>` (parallel project builds), `--singleThreaded` (debugging). 

## When to move fully to 7.x

Move `typescript` itself to 7.x only when every API consumer in the repo supports it (typescript-eslint, test transformers, declaration bundlers, framework plugins) — expected from 7.1, which ships the new API. Record the decision in your TypeScript standards first.

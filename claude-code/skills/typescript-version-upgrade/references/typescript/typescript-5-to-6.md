# TypeScript 5.x → 6.0

**Recommended standard: TypeScript 6.0.** Pin `typescript@~6.0` wherever typescript-eslint, ts-jest, tsup `dts` or any other compiler-API tool runs; never `add typescript` unpinned — `npm latest` is 7.x.

Primary source: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/. 6.0 is the bridge to the native 7.0 compiler: it changes defaults and deprecates every option 7.0 removes. Deprecated options fail the build in 6.0 with a `TS5101`/`TS5107` error unless silenced.

## Changed defaults

A tsconfig that omitted these now gets different behaviour. Set each explicitly if you relied on the old default.

| Option | 5.x default | 6.0 default | Typical fix |
|---|---|---|---|
| `strict` | `false` | `true` | Keep `true`; fix errors, or set `false` temporarily and track it |
| `module` | `commonjs` | `esnext` | Set `module` explicitly (`nodenext` for Node, `esnext`/`preserve` for bundlers) |
| `target` | `es5` | `es2025` | Set `target` to the oldest runtime you deploy to (`../ecmascript/es-upgrade-checklist.md`) |
| `types` | every `@types/*` package | `[]` | List them: `"types": ["node"]` (plus `vitest/globals` etc.) |
| `rootDir` | inferred from inputs | the tsconfig directory | Set `rootDir` (e.g. `"./src"`) if emit paths change |
| `noUncheckedSideEffectImports` | `false` | `true` | Fix typo'd side-effect imports; declare CSS/asset modules |
| `libReplacement` | `true` | `false` | Only matters if you use `@typescript/lib-*` replacements |

The `types: []` default is the most common break: `Cannot find name 'process'` / `Cannot find name 'node:fs'` until `"types": ["node"]` is added.

## Deprecated in 6.0, removed in 7.0

| Option / syntax | Replace with |
|---|---|
| `target: "es5"`, `downlevelIteration` | ES2015+ target; use an external transpiler if ES5 output is truly needed |
| `moduleResolution: "node"` / `"node10"` | `nodenext` (Node) or `bundler` (bundled apps) |
| `moduleResolution: "classic"` | `nodenext` or `bundler` |
| `module: "amd"` / `"umd"` / `"system"` / `"none"` | ESM output |
| `baseUrl` | `paths` entries relative to the tsconfig (`"@/*": ["./src/*"]`) |
| `outFile` | A bundler (tsdown, esbuild, Vite) |
| `esModuleInterop: false`, `allowSyntheticDefaultImports: false` | Remove (always on) |
| `alwaysStrict: false` | Remove (always strict) |
| `module Foo { }` namespace syntax | `namespace Foo { }` |
| `import … assert { type: "json" }` | `import … with { type: "json" }` |
| `/// <reference no-default-lib="true"/>` | Remove |

Also new in 6.0: passing files on the command line while a `tsconfig.json` exists is an error (`TS5112`); use `tsc -p <config>` or `--ignoreConfig`. Scripts like `tsc --noEmit src/foo.ts` break.

## Migration steps

1. Upgrade from the latest 5.9.x first and get a clean `tsc --noEmit`.
2. Check the tools that embed the compiler API accept 6.0: `npm view typescript-eslint peerDependencies`, `npm view ts-jest peerDependencies`, plus any Vite/webpack TS plugin. (2026-09-28: typescript-eslint `<6.1.0`, ts-jest `<7` — both accept 6.0.)
3. Install pinned: `<pm> add -D typescript@~6.0` in every workspace package that declares TypeScript.
4. Fix configuration automatically where possible:
   ```bash
   npx @andrewbranch/ts5to6 --fixBaseUrl .
   npx @andrewbranch/ts5to6 --fixRootDir .
   ```
   (the tool follows `references` and `extends`; pass a path for configs not named `tsconfig.json`).
5. Set the changed defaults explicitly (table above) — at minimum `types`, `module`, `target`.
6. Replace every deprecated option. `"ignoreDeprecations": "6.0"` silences them for one step only and is rejected by 7.0; if you use it, add a TODO with an owner.
7. `<pm> exec tsc --noEmit` per project, then lint, tests and build.
8. Re-run with `--stableTypeOrdering` if you plan a 7.0 lane: it makes 6.0 order union members as 7.0 does, so declaration output and error text match.

## New in 6.0 worth knowing

- `target`/`lib` `es2025`; `esnext` lib adds Temporal, `Map.getOrInsert*`, `RegExp.escape`.
- `dom.iterable` and `dom.asynciterable` are folded into `dom`.
- `#/` subpath imports resolve under `nodenext`/`bundler`.

## Validation

- `tsc --noEmit` clean with no `ignoreDeprecations`.
- Emitted output (libraries): diff `dist/` against the baseline build — `rootDir` and `module` default changes alter paths and module format.
- Declaration files: consumers still type-check.

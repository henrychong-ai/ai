# Bundler Targets

How to set the output level for each build tool so it matches the runtime floor. A common modern split is tsx to run, `tsc` to emit and tsdown when bundling (tsup is no longer actively maintained upstream).

## Principle

The **runtime floor** decides the output level: the oldest Node line you deploy (`es-upgrade-checklist.md`) or the browser floor (`browser-support.md`). Every tool in the chain should emit at that level or lower:

- tsconfig `target` governs what `tsc` emits and which syntax the type checker assumes.
- The bundler/transpiler target governs what actually ships. If it is higher than the runtime supports, the runtime gets syntax it cannot parse; if it is lower, you pay for unnecessary down-levelling and polyfills.
- A bundler target higher than tsconfig `target` is harmless when tsc does not emit (the bundler reads the TypeScript source); keep them aligned anyway so behaviour is predictable.

## esbuild

```javascript
import { build } from 'esbuild';

await build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  platform: 'node',
  outfile: 'dist/index.js',
  target: 'node24',        // or 'es2024'; browsers: ['chrome111', 'safari16.4']
});
```

- Targets: `esNNNN`, `esnext`, `node<version>`, browser versions; with a list, esbuild satisfies every entry.
- esbuild strips types without type-checking — run `tsc --noEmit` as a separate gate.

## tsdown (library and service bundling)

```typescript
// tsdown.config.ts
import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm'],
  target: 'node24',
  dts: true,
});
```

Replaces tsup in new work. The TypeScript config file loads as ESM, so the package needs `"type": "module"` (or name it `tsdown.config.mts`). Check the current option names with `npm view tsdown version` and its docs before copying — it is pre-1.0.

## Vite

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: 'baseline-widely-available', // the default; or an explicit list
  },
});
```

The default build target is `'baseline-widely-available'` (Chrome/Edge 111, Firefox 114, Safari/iOS 16.4 for the current major; the date is fixed per Vite major). Older Vite majors defaulted to `'modules'`. Override only when your browser floor differs (`browser-support.md`); for server/SSR builds set the Node target.

**`useDefineForClassFields`:** Vite's transpiler reads it from tsconfig. It defaults to `true` for ES2022+ targets and `false` below; set it explicitly if the code relies on legacy field semantics (legacy decorators, TypeORM entities).

## Next.js

Next.js compiles with SWC using the project's `browserslist` (or its own default floor). Do not set a separate target; set `browserslist` if you need a different floor. tsconfig `target` does not change Next.js output.

## webpack

- `ts-loader` emits at tsconfig `target`.
- `esbuild-loader`: `options: { target: 'es2022' }` on the loader and the same on `EsbuildPlugin` for minification.
- `babel-loader` with `@babel/preset-env`: `targets` from browserslist.
- `target: 'browserslist'` (or `'node24'`) sets webpack's own runtime chunk format.

## Rollup

`@rollup/plugin-typescript` uses tsconfig (override `target` in the plugin options); `rollup-plugin-esbuild` takes `target: 'es2022'` or `'node24'`.

## SWC (standalone)

```json
{
  "jsc": { "target": "es2022", "parser": { "syntax": "typescript" } },
  "module": { "type": "es6" }
}
```

Or use `env.targets` with browserslist instead of `jsc.target`.

## `isolatedModules`

Enable it whenever a non-tsc transpiler (esbuild, SWC, Oxc, Babel) compiles the code: it makes tsc flag constructs those tools cannot compile file-by-file (`const enum` across files, re-exporting types without `export type`).

## Support for new targets

Before raising a target, check each tool in the chain accepts it: run the build with the new value, or check the tool's changelog. A tool that does not recognise a target fails loudly at build time; that is the check.

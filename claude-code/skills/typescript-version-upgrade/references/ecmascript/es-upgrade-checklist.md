# ECMAScript Target Upgrade

Protocol for changing `target`/`lib` in tsconfig and the matching bundler target. Your default tsconfig belongs in your TypeScript standards; this file covers how to move a repo safely.

## Rule

Set `target` to what the **oldest runtime you deploy to** supports, and keep `lib` at the same level (plus `DOM` for browser code). The runtime decides — not the newest Node on a developer laptop.

- **Node services:** use the mapping below for the oldest Node line in production (`.nvmrc`, Docker image, pipeline image must agree first).
- **Next.js, Vite and other bundled front ends:** tsconfig `target` does not control emitted code — these projects use `noEmit`, and SWC/esbuild/Oxc compile to the browser target (browserslist or `build.target`). Set the browser floor instead (`browser-support.md`); keep tsconfig `target`/`lib` in line with it so the type checker does not allow APIs the browsers lack.
- **Libraries:** target the oldest runtime your consumers use; document it in `engines`.

## Node → target mapping

| Node line | `target` / `lib` | `module` | Minimum TypeScript |
|---|---|---|---|
| 26 | ES2025 | `nodenext` | 6.0 |
| 24 | ES2024 | `nodenext` | 5.7 |
| 22 | ES2023 | `nodenext` | 5.5 |
| 20 (EOL) | ES2023 | `nodenext` | 5.5 |
| 18 (EOL) | ES2022 | `node16` | 4.6 |

Sources: TypeScript wiki "Node Target Mapping" (Node 18–24), `@tsconfig/node26` (Node 26). From TypeScript 5.9, `module: "node20"` is a stable alternative to `nodenext` for Node 20+. TypeScript minimums were verified by running `tsc --target <value>` on each release: `es2023` first accepted in 5.5, `es2024` in 5.7, `es2025` in 6.0. `@tsconfig/node<N>` packages sometimes pick a lower target with a higher `lib` (e.g. `@tsconfig/node22` uses target ES2022 with lib ES2024); either is safe, as long as `lib` does not exceed the runtime.

A too-old compiler rejects the value with `error TS6046: Argument for '--target' option must be: …` — upgrade TypeScript first (`../typescript/`).

## Step 1: Inventory

```bash
find . -name 'tsconfig*.json' -not -path '*/node_modules/*' -exec grep -HE '"(target|lib|module|moduleResolution)"' {} \;
cat .nvmrc .node-version 2>/dev/null; node --version
<pm> exec tsc --version
grep -rnE "target" vite.config.* tsdown.config.* esbuild.* webpack.config.* 2>/dev/null
cat .browserslistrc 2>/dev/null; node -p "require('./package.json').browserslist"
```

## Step 2: Check what the new target changes

**Emit changes (tsc emits JS):** raising the target stops down-levelling syntax (classes, async/await, optional chaining, private `#fields`, static blocks). This is safe when the runtime supports it — it only fails on an older runtime.

**Class fields (`useDefineForClassFields`):** it defaults to `true` for ES2022+ targets. Fields are then defined with `Object.defineProperty` semantics, which changes behaviour for classes that redeclare a base-class property, rely on field initialisers running after a parameter-property assignment, or use legacy decorators (TypeORM, class-validator, NestJS DTOs). If raising the target past ES2021 on such code, set `"useDefineForClassFields": false` explicitly and add a test.

**New API types:** a higher `lib` lets code call newer built-ins (`Object.groupBy`, `Array.prototype.toSorted`, `Promise.withResolvers`). Only raise `lib` as far as the runtime supports them. See `es-version-features.md` for what arrives in each edition and `polyfill-strategies.md` if a browser build must support older engines.

## Step 3: Update configuration

1. tsconfig `target` and `lib` (add `"DOM"` for browser code; since TS 6 `dom` includes the iterable types).
2. Bundler target to match or be lower (`bundler-configuration.md`).
3. Browserslist / framework browser floor for front ends (`browser-support.md`).
4. `engines.node` if the target implies a higher Node floor.

## Step 4: Validate

```bash
<pm> exec tsc --noEmit
<pm> run build
<pm> test
```

Inspect the actual build artefact (e.g. a server bundle in `dist/`, `.next/server`, or a Worker bundle) to confirm the syntax level and that no unneeded polyfills are included; its size should not grow. Run the tests on the **oldest** deployed runtime, not only the newest.

## Common issues

| Symptom | Fix |
|---|---|
| `TS6046: Argument for '--target' option must be …` | Upgrade TypeScript (ES2023 → 5.5, ES2024 → 5.7, ES2025 → 6.0) |
| `Property 'groupBy' does not exist on type 'ObjectConstructor'` | Raise `lib` (only if the runtime has it) |
| Class field values `undefined` after raising target | `useDefineForClassFields` change — see Step 2 |
| Bundle includes polyfills for features the runtime has | Align bundler target / browserslist with the new floor |
| Works locally, fails in production | Production runs an older Node than dev — align `.nvmrc`, Docker, pipeline |

## Rollback

Revert the config commit (`git revert`). A target change touches no dependencies, so the lockfile is unaffected.

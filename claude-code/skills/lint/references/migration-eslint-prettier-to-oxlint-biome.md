# Migrating ESLint + Prettier to Oxlint + Biome

Protocol for moving an existing TypeScript/JavaScript repo to Oxlint + Biome (+ residual ESLint where needed). Target configs, scripts and editor settings are in `typescript-oxlint-biome.md`; gap plugins in `typescript-residual-eslint.md`. Pause for the user's confirmation at each checkpoint before deleting files or dependencies.

## Why

- **Speed:** Oxlint and Biome are Rust tools, many times faster than ESLint and Prettier; no lint cache needed.
- **Fewer dependencies:** Oxlint's plugins are built in, so a React or Next.js project needs two lint/format packages instead of a dozen-plus ESLint and Prettier plugins. Smaller lockfile, fewer version conflicts, smaller supply-chain surface.
- **Clear split:** Oxlint lints, Biome formats and sorts imports, `tsc` type-checks, residual ESLint covers gaps only. No `eslint-config-prettier` needed.

## Phase 1: Analyse

1. **ESLint config:** `eslint.config.{js,mjs,cjs,ts}` (flat), `.eslintrc*` (legacy), or `eslintConfig` in package.json. Record plugins, custom rules, parser and overrides.
2. **Prettier config:** `.prettierrc*`, `prettier.config.*`, or `prettier` in package.json, plus `.prettierignore`. Record every setting.
3. **Dependencies:** list packages matching `eslint*`, `@typescript-eslint/*`, `typescript-eslint`, `@stylistic/*`, `@next/eslint-plugin-next`, `prettier*`, `@trivago/prettier-plugin-sort-imports`, `@ianvs/prettier-plugin-sort-imports`.
4. **Frameworks:** use the detection matrix in SKILL.md to choose Oxlint plugins and decide whether residual ESLint is needed (Vue templates, Astro, Tailwind, Playwright, browser compat).
5. **Integrations:** `.husky/`, lint-staged config, CI files, `.vscode/settings.json`, `.editorconfig`.

**Checkpoint:** show the user the config formats found, dependency count, detected frameworks, Oxlint plugins to enable, whether residual ESLint is needed, and the number of custom rules to map.

## Phase 2: Map Dependencies

| Old package | Action | Replacement |
|-------------|--------|-------------|
| `eslint` | Remove (keep if residual ESLint is needed) | Oxlint |
| `@typescript-eslint/eslint-plugin`, `@typescript-eslint/parser` | Remove | Oxlint `typescript` plugin |
| `typescript-eslint` | Remove (keep if residual ESLint lints TS) | Oxlint `typescript` plugin |
| `@stylistic/eslint-plugin*` | Remove | Biome formatting |
| `eslint-plugin-import` | Remove | Oxlint `import` + Biome organise imports |
| `eslint-plugin-unicorn` | Remove | Oxlint `unicorn` |
| `eslint-plugin-sonarjs` | Remove | Oxlint `oxc` (partial) |
| `eslint-plugin-promise` | Remove | Oxlint `promise` |
| `eslint-plugin-react`, `eslint-plugin-react-hooks` | Remove | Oxlint `react` |
| `eslint-plugin-react-refresh` | Remove | Oxlint `react/only-export-components` |
| `eslint-plugin-jsx-a11y` | Remove | Oxlint `jsx-a11y` |
| `@next/eslint-plugin-next`, `eslint-config-next` | Remove | Oxlint `nextjs` |
| `eslint-plugin-n`, `eslint-plugin-node` | Remove | Oxlint `node` |
| `eslint-plugin-vitest`, `@vitest/eslint-plugin`, `eslint-plugin-jest` | Remove | Oxlint `vitest` / `jest` |
| `eslint-plugin-jsdoc` | Remove | Oxlint `jsdoc` |
| `eslint-config-prettier`, `eslint-plugin-prettier` | Remove | Not needed |
| `prettier` | Remove (keep for Solidity or other Prettier-only files) | Biome |
| `prettier-plugin-organize-imports`, `@trivago/…`, `@ianvs/…` sort-imports plugins | Remove | Biome organise imports |
| `prettier-plugin-tailwindcss`, `eslint-plugin-tailwindcss` | Replace | `eslint-plugin-better-tailwindcss` |
| `eslint-plugin-vue`, `eslint-plugin-astro`, `eslint-plugin-playwright`, `eslint-plugin-compat` | Keep | Residual ESLint |

**Checkpoint:** show the remove / replace / keep lists and the packages to add.

## Phase 3: Execute

Use the repo's package manager throughout.

1. Install: `pnpm add -D oxlint @biomejs/biome` (+ `eslint eslint-plugin-oxlint typescript-eslint` and the kept gap plugins if residual ESLint is needed).
2. Create `.oxlintrc.json` from `templates/.oxlintrc.json`; set `plugins` from Phase 1 (keep `typescript`, `unicorn`, `oxc`).
3. Create `biome.json` from `templates/biome.json`, **replacing the formatter options with the repo's existing Prettier settings** (option names: `typescript-oxlint-biome.md` → Prettier → Biome table) so the migration does not restyle the codebase. Fold `.prettierignore` entries into `files.includes` as `!` negations.
4. Residual ESLint only: create `eslint.config.mjs` from the template and keep only the needed sections. Otherwise delete every `eslint.config.*`.
5. Replace package.json scripts with the standard set (`typescript-oxlint-biome.md` → package.json scripts). Remove leftover `lint:eslint` / `format:prettier` scripts.
6. Update lint-staged to `templates/lint-staged.config.mjs` patterns.
7. Update CI lint steps: `eslint .` becomes `oxlint --max-warnings=0` (+ `eslint .` for residual), and `prettier --check` becomes `biome check .`. Ask the user to review CI changes.
8. VS Code: switch to `templates/.vscode/settings.json` and `extensions.json`; remove `eslint.*` (unless residual), `prettier.*` and the `esbenp.prettier-vscode` default formatter.
9. Remove the old dependencies from Phase 2 in one command, only those actually installed.
10. Delete `.eslintrc*`, `.eslintignore`, `.prettierrc*`, `prettier.config.*`, `.prettierignore`, and the `eslintConfig` / `prettier` package.json keys (keep Prettier files if Solidity or other files still use Prettier).

## Phase 4: Map Custom Rules

For each custom ESLint rule:

1. Same name in Oxlint: copy it to `.oxlintrc.json` `rules` with the same severity and options.
2. Renamed: `@typescript-eslint/x` → `typescript/x`; `react-hooks/x` → `react/x`; `import/x`, `react/x`, `jsx-a11y/x` keep their names.
3. No equivalent (check `oxlint --rules`): accept the gap, move the rule to residual ESLint, or ask the user.

Run `oxlint` once after editing; it rejects unknown rule names.

## Phase 5: Verify

```bash
pnpm exec oxlint --max-warnings=0
pnpm exec eslint . --max-warnings=0      # residual only
pnpm exec biome check .
pnpm exec tsc --noEmit
pnpm exec lint-staged --verbose          # if hooks are configured; stage a file first (it runs the tasks)
```

Fix with `oxlint --fix`, `eslint --fix` and `biome check --write .`, then re-run. Review the formatting diff: with the Prettier settings carried over it should be small. Unexpected changes usually mean a setting was not mapped (`trailingComma: "es5"` → `trailingCommas: "es5"`; `arrowParens: "avoid"` → `arrowParentheses: "asNeeded"`).

**Final report:** configs created and removed, dependency counts before and after, and pass/fail for Oxlint, residual ESLint, Biome and tsc.

## Known Differences

- **Import order:** Biome's organise-imports grouping is fixed (it does not reproduce custom `import/order` groups). Accept it, or keep `import/order` in residual ESLint if ordering is critical.
- **Type-aware rules:** `@typescript-eslint` rules that need type information (`no-floating-promises`, `no-unsafe-*`) run in Oxlint only in opt-in type-aware mode (`oxlint-tsgolint` and a TS 7-ready tsconfig; `typescript-oxlint-biome.md`). Without it they are dropped; `tsc --noEmit` remains the gate.

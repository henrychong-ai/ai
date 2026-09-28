# lint — TODO

Open items, unverified facts and pending decisions. Last reviewed 2026-09-28.

## Re-verify on each tool release
- [ ] Run every template through its tool: `oxlint` (auto-discovery + rule names), `biome check`, `eslint` on `templates/eslint.config.mjs` with all sections enabled, `ruff check`, `mypy`, `solhint`, `golangci-lint config verify` (both Go templates), `npx commitlint` on sample headers, and a lint-staged run.
- [ ] Biome: bump `$schema` in `templates/biome.json` with `biome migrate --write` (validated on 2.5.14).
- [ ] Oxlint: remove any rule the new version reports as unknown (validated on 1.85.0; `.oxlintrc.json` re-run on 1.86.0 on 2026-09-28).

## Watch items
- [ ] Biome Markdown/YAML formatting and stable HTML/Vue/Astro support: when stable, revisit the lint-staged globs and VS Code formatters.
- [ ] Oxlint `jsPlugins` (alpha): could replace residual ESLint for gap plugins.
- [ ] Oxlint type-aware rules: re-test on each `oxlint-tsgolint` release (documented as TS 7-only upstream; observed working on TS 6.0.3 on 2026-09-28).
- [x] Oxlint `import/no-unassigned-import` on CSS side-effect imports: the template now sets `["warn", { "allow": ["**/*.css"] }]`, so `import "./index.css"` passes while other side-effect imports still warn (verified with oxlint 1.85.0 and `biome check`, 2026-09-28).
- [ ] `oxfmt` (Oxc formatter) as a possible Biome replacement: evaluate when stable.

## Pending links and dependencies
- [x] `/typescript` → `references/tech-stack/version-policy.md` is linked from SKILL.md; the public `/typescript` copy carries it (checked 2026-09-28).
- [x] No other public skill links the removed or renamed templates (`oxlint.json`, `lint-staged.config.js`, `tsconfig.json`, CI templates) (grep, 2026-09-28).

## Unverified or pending
- [x] Oxlint type-aware rules on TypeScript 6 (decided 2026-09-28): documented as opt-in, needing `oxlint-tsgolint` and a TS 7-ready tsconfig (no `baseUrl`), with the upstream TS 7 statement and the dated TS 6.0.3 observation side by side (`references/typescript-oxlint-biome.md`); re-confirmed the same day (`no-floating-promises` reported; a `baseUrl` tsconfig rejected).

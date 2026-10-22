# lint — TODO

Open items, unverified facts and pending decisions.

Last reviewed: 2026-10-22.

## Open

### Watch items (re-verify on each tool release)
- [ ] **Template run:** run every template through its tool: `oxlint` (auto-discovery + rule names), `biome check`, `eslint` on `templates/eslint.config.mjs` with all sections enabled, `ruff check`, `mypy`, `solhint`, `golangci-lint config verify` and `run` (both Go templates; last passed on v2.15.0, 2026-10-22), `npx commitlint` on sample headers, and a lint-staged run.
- [ ] **Biome:** bump `$schema` in `templates/biome.json` with `biome migrate --write` on each release (last bumped to 2.6.2 on 2026-10-22). The Language support table in `references/typescript-oxlint-biome.md` was checked on 2.5; re-check it on 2.6.
- [ ] **Oxlint:** remove any rule the new version reports as unknown (validated on 1.85.0; `.oxlintrc.json` re-run on 1.86.0 on 2026-09-28).
- [ ] **Oxlint type-aware rules:** re-test on each `oxlint-tsgolint` release (documented as TS 7-only upstream; observed working on TS 6.0.3 on 2026-09-28).
- [ ] **Biome Markdown/YAML formatting and stable HTML/Vue/Astro support:** when stable, revisit the lint-staged globs and VS Code formatters.
- [ ] **Oxlint `jsPlugins` (alpha):** when stable, assess whether it can replace residual ESLint for gap plugins.
- [ ] **`oxfmt`** (Oxc formatter) as a possible Biome replacement: evaluate when stable.

## Done
- 2026-10-22: golangci-lint pinned v2.15.0: both Go templates pass `config verify` and `run`.
- 2026-10-22: Biome `$schema` bumped to 2.6.2: `migrate --write` changed only `$schema`; `biome check` clean.

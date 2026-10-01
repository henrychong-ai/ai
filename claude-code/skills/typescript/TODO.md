# TODO — typescript skill (public copy)

Open items and facts to re-check. Update as the skill evolves.

## Pending decisions
- [ ] **Vitest 5** (released 2026-09-03; needs Node >= 22.12). The skill stays on `^4.1` because `@cloudflare/vitest-pool-workers` 0.22 peers `vitest ^4.1`. Revisit when the Workers pool supports Vitest 5.
- [ ] **TypeScript 7 as primary**: revisit when 7.1 ships a compiler API and typescript-eslint, ts-jest and declaration tooling support it.
- [ ] **Node 26**: update `version-policy.md` wording once Node 26 reaches LTS (2026-10-28); its tsconfig target is ES2025.
- [x] **Jest template vs the tsconfig standard**: resolved 2026-09-28 by shipping `templates/testing/tsconfig.jest.json` (extends the standard tsconfig, CommonJS `Node16` module, `verbatimModuleSyntax: false`); `jest.config.ts` points ts-jest at it. Verified with Jest 30.5.2 + ts-jest 29.4.14.

## Unverified / re-check
- [x] Prisma 7 driver adapter, `prisma.config.ts` and the `orm.md` snippets: generated and type-checked with Prisma 7.10.0 + TypeScript 6.0.3 under the `tooling.md` Node tsconfig; `PrismaClient({ adapter })` instantiates (2026-09-28 review).
- [ ] Oxlint config discovery (`.oxlintrc.json` vs `oxlint.json` + `-c`) is owned by `/lint`; keep `tooling.md` scripts aligned.

## Version upgrades
Merged from the former `/typescript-version-upgrade` skill (2026-10-01); paths are relative to this skill.

### Open
- [ ] **Node security floors:** the protocol uses the live lookup in `references/version-upgrade/node/migration-overview.md`. Snapshot on 2026-09-28: last security releases 24.18.1 and 22.23.2 (2026-07-28). Re-check the snapshot line on each review.
- [ ] **Node 24 → 26 guide:** written before Node 26 LTS (2026-10-28) and before nodejs.org published a v24-to-v26 migration page. After LTS promotion, re-read the 26.x changelog and the userland-migrations catalogue for new codemods and update `references/version-upgrade/node/node-24-to-26.md`.
- [ ] **TypeScript 7.1:** when 7.1 ships the compiler API, re-check typescript-eslint, ts-jest and framework support and revise `references/version-upgrade/typescript/typescript-6-to-7.md` (the policy change itself belongs in `references/tech-stack/version-policy.md`).
- [ ] **Next.js with TypeScript 7:** unverified whether `next build`'s type-check step works with only TS 7 installed (2026-09-28). Test on one Next.js 16 repo before recommending the side-by-side lane there.
- [ ] **ES2026 target:** neither TS 6.0 nor 7.0 accepts `--target es2026` (checked 2026-09-28). Add a row to the Node mapping in `references/version-upgrade/ecmascript/es-upgrade-checklist.md` when a compiler release supports it.

### Unverified
- [ ] Node 22 → 24 behaviour-change list (fetch compliance, AbortSignal validation, stream error propagation) is summarised from the nodejs.org migration page headings, not from individual changelog entries (2026-09-28).
- [ ] ES2026 feature list in `references/version-upgrade/ecmascript/es-version-features.md` is from secondary coverage of the Ecma approval; confirm against the published ECMA-262 17th edition (2026-09-28).

### Done
- [x] 2026-09-28: restructured the upgrade guides — merged legacy Node guides and the three React guides; added TypeScript 5→6 and 6→7 and Node 24→26 guides; replaced the browser matrix and Node-ES mapping with procedures; Next.js file is a per-major index of official guides and codemods.
- [x] 2026-10-01: guides that pointed to "your TypeScript standards" now link to `references/tech-stack/version-policy.md`, `references/coding-standards/tooling.md` and `references/testing/testing-strategies.md` by relative path.

## Log
- 2026-09-28: Restructure: added `version-policy.md`, `orm.md`, `node-services.md`, `astro.md`; rewrote the ironclad stack, `cloudflare.md`, `tooling.md` and `style-guide.md` (merged the former rules and clean-code files); removed the Obsidian plugin, personal deployment and project-configuration references; Vitest 4 `test.projects` template replaced `vitest.workspace.ts`.
- 2026-09-28 (review): compiled every complete snippet under the `tooling.md` tsconfig on TypeScript 6.0.3 and ran the templates on Vitest 4.1.11 / Jest 30. Fixed: Node block needs `rootDir` (TS 6 TS5011) and the TS 6 `types`/`process.env` notes; Node 24 target ES2024 (TypeScript wiki mapping); Biome scripts use `biome check`; `.js` extensions and `fileURLToPath` workflows path in `node-services.md`; `prisma.config.ts` + verified Prisma 7 snippet; debounce/throttle generics, `AsyncQueue` failure handling, `formatZodErrors`, React error boundary (`override`, type imports), fetch client under `exactOptionalPropertyTypes`, Hono middleware return/annotation, depth-limited Zod leaf now rejects; Vitest `Matchers` augmentation, `afterEach` import, UUID v7, React 19 act warning text; pinned Vitest in install commands.
- 2026-10-01: Merged `/typescript-version-upgrade` into this skill. Guides moved to `references/version-upgrade/{node,typescript,react,frameworks,ecmascript,safety}/`; its SKILL.md body became `references/version-upgrade/upgrade-protocol.md`; SKILL.md gained an Upgrades reference group, an Upgrading section and upgrade triggers in the description; its TODO merged under "Version upgrades"; in-skill links rewritten.

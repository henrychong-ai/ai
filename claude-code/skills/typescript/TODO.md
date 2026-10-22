# TODO — typescript skill (public copy)

Open items and facts to re-check. Update as the skill evolves.

## Pending decisions
- [ ] **Vitest 5** (released 2026-09-03; needs Node >= 22.12). The skill stays on `^4.1` because `@cloudflare/vitest-pool-workers` still peers `vitest ^4.1.0` (0.23.0, checked 2026-10-22). Revisit when the Workers pool supports Vitest 5.
- [ ] **TypeScript 7 as primary**: revisit at TypeScript 7.1 GA plus typescript-eslint TypeScript 7 support (7.1.0-beta 2026-10-20, RC expected in about a month; typescript-eslint 8.72 peers `<6.1.0`, checked 2026-10-22); ts-jest and declaration tooling must also accept it.
- [x] **pnpm 12**: recommendation set 2026-10-22: pnpm 12 for new projects after a pilot on one repository; existing projects stay on the latest pnpm 10 and move straight to 12 by 2027-01-31; skip 11 (10 and 11 both end 2027-04-30, pnpm `SECURITY.md`). Written into `references/tech-stack/version-policy.md` → pnpm.
- [ ] **pnpm 12 pilot**: run the pilot on one repository (Corepack form, `allowBuilds` migration from `onlyBuiltDependencies`, CI install), then confirm the new-project default. Pin 12.15.0 (on `next-12`, checked 2026-10-22) once it becomes `latest`.
- [ ] **Prisma 8**: decide on Prisma 8 after its GA (7 gets fixes for 18 months after 8 GA; 8 needs Node `^22.18 || ^24.11 || >=26` and TypeScript ≥5.9). Until then `prisma@^7` stays pinned explicitly (npm `latest` = 8.0.0-rc.24, checked 2026-10-22).
- [ ] **Hono 5**: review the `^4` line when Hono 5 is GA (5.0.0-rc.1 exists, checked 2026-10-22).
- [x] **Next.js 15**: unsupported since 2026-10-21; `version-policy.md` updated 2026-10-22 (16 for new and existing projects).
- [ ] **Node 26**: recommendation set 2026-10-22 (new projects Node 26 from 2026-10-28; existing projects move when next worked on). After 2026-10-28, switch any remaining "becomes LTS" / "from 2026-10-28" wording in `version-policy.md`, SKILL.md and the Node guides to the past tense; its tsconfig target is ES2025.
- [x] **Jest template vs the tsconfig standard**: resolved 2026-09-28 by shipping `templates/testing/tsconfig.jest.json` (extends the standard tsconfig, CommonJS `Node16` module, `verbatimModuleSyntax: false`); `jest.config.ts` points ts-jest at it. Verified with Jest 30.5.2 + ts-jest 29.4.14.

## Unverified / re-check
- [x] Prisma 7 driver adapter, `prisma.config.ts` and the `orm.md` snippets: generated and type-checked with Prisma 7.10.0 + TypeScript 6.0.3 under the `tooling.md` Node tsconfig; `PrismaClient({ adapter })` instantiates (2026-09-28 review).
- [ ] Oxlint config discovery (`.oxlintrc.json` vs `oxlint.json` + `-c`) is owned by `/lint`; keep `tooling.md` scripts aligned.

## Version upgrades
Merged from the former `/typescript-version-upgrade` skill (2026-10-01); paths are relative to this skill.

### Open
- [ ] **Node security snapshot:** update the single snapshot in `references/tech-stack/version-policy.md` → Node.js after each Node security release (last: October 2026, updated 2026-10-22). Other files point to it; keep patch numbers out of them.
- [ ] **Node 24 → 26 guide:** written before Node 26 LTS (2026-10-28) and before nodejs.org published a v24-to-v26 migration page. After LTS promotion, re-read the 26.x changelog and the userland-migrations catalogue for new codemods and update `references/version-upgrade/node/node-24-to-26.md`.
- [ ] **TypeScript 7.1:** at 7.1 GA (its beta moved the still-unstable API to `typescript/sync` and siblings), re-check typescript-eslint, ts-jest and framework support and revise `references/version-upgrade/typescript/typescript-6-to-7.md` (the policy change itself belongs in `references/tech-stack/version-policy.md`).
- [x] **Next.js with TypeScript 7:** resolved 2026-10-22 from the Next.js docs: `next build` runs the project's `tsc` CLI by default (`experimental.useTypeScriptCli`), which supports TypeScript 6 and enables TypeScript 7; `experimental.useTypeScriptCli: false` reverts to the API checker, which fails on TS 7. Not yet tested here; the default stays `typescript@~6.0`.
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
- 2026-10-22: October 2026 Node security release and version recommendations: one security snapshot in `version-policy.md` with pointers from the Node guides; support rules A–D inlined in `version-policy.md`; new projects Node 26 from 2026-10-28 and pnpm 12 after a pilot; pnpm 10 and Node 22 off by 2027-01-31; TypeScript 7 API wording corrected; Next.js 15 unsupported; Prisma `^7` pinned explicitly; Workers pool 0.23.0; `upgrade-protocol.md` gained "Responding to a Node security release".

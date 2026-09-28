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

## Log
- 2026-09-28: Restructure: added `version-policy.md`, `orm.md`, `node-services.md`, `astro.md`; rewrote the ironclad stack, `cloudflare.md`, `tooling.md` and `style-guide.md` (merged the former rules and clean-code files); removed the Obsidian plugin, personal deployment and project-configuration references; Vitest 4 `test.projects` template replaced `vitest.workspace.ts`.
- 2026-09-28 (review): compiled every complete snippet under the `tooling.md` tsconfig on TypeScript 6.0.3 and ran the templates on Vitest 4.1.11 / Jest 30. Fixed: Node block needs `rootDir` (TS 6 TS5011) and the TS 6 `types`/`process.env` notes; Node 24 target ES2024 (TypeScript wiki mapping); Biome scripts use `biome check`; `.js` extensions and `fileURLToPath` workflows path in `node-services.md`; `prisma.config.ts` + verified Prisma 7 snippet; debounce/throttle generics, `AsyncQueue` failure handling, `formatZodErrors`, React error boundary (`override`, type imports), fetch client under `exactOptionalPropertyTypes`, Hono middleware return/annotation, depth-limited Zod leaf now rejects; Vitest `Matchers` augmentation, `afterEach` import, UUID v7, React 19 act warning text; pinned Vitest in install commands.

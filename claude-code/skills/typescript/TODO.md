# TODO — typescript skill (public copy)

Open items and facts to re-check. Update as the skill evolves; paths are relative to this skill.

Last reviewed: 2026-10-22.

## Open

### Decisions pending
- [ ] **TypeScript 7 as primary** (default `typescript@~6.0`, `references/tech-stack/version-policy.md`): revisit at TypeScript 7.1 GA plus typescript-eslint TypeScript 7 support (7.1.0-beta 2026-10-20, RC expected in about a month; typescript-eslint 8.72 peers `<6.1.0`, checked 2026-10-22); ts-jest and declaration tooling must also accept it. At 7.1 GA, also re-check framework support and revise `references/version-upgrade/typescript/typescript-6-to-7.md` (the beta moved the still-unstable API to `typescript/sync` and siblings); the recommendation change itself belongs in `version-policy.md`.
- [ ] **Prisma 8**: decide after its GA (7 gets fixes for 18 months after 8 GA; 8 needs Node `^22.18 || ^24.11 || >=26` and TypeScript ≥5.9). Until then `prisma@^7` stays pinned explicitly (npm `latest` = 8.0.0-rc.24, checked 2026-10-22). Once decided, replace the placeholder row in `references/version-upgrade/upgrade-protocol.md` → Library majors with `references/version-upgrade/libraries/prisma-7-to-8.md`.
- [ ] **Hono 5**: review the `^4` line when Hono 5 is GA (5.0.0-rc.1 on npm `next` since 2026-10-10; no migration guide, checked 2026-10-22). `@hono/zod-openapi` must support 5 first. At GA, add the official guide to the Library majors row.

### Watch items
- [ ] **Node 26 LTS (on or after 2026-10-28):** switch remaining "becomes LTS" / "from 2026-10-28" wording in `version-policy.md`, SKILL.md and the Node guides to the past tense. Re-read the 26.x changelog and the userland-migrations catalogue (and a nodejs.org v24-to-v26 migration page, if published) and update `references/version-upgrade/node/node-24-to-26.md`, which was written before LTS. Its tsconfig target is ES2025.
- [ ] **Node security snapshot (each Node security release):** update the single snapshot in `version-policy.md` → Node.js (last: October 2026, updated 2026-10-22). Other files point to it; keep patch numbers out of them.
- [ ] **pnpm 12.15.0 (when it becomes npm `latest`):** pin it in `version-policy.md` (on `next-12`, checked 2026-10-22).
- [ ] **Vitest 5 (next check 2026-11-30, and on each Workers pool release):** released 2026-09-03, needs Node >= 22.12. The skill stays on `^4.1` because `@cloudflare/vitest-pool-workers` still peers `vitest ^4.1.0` (0.23.0, checked 2026-10-22). Revisit when the Workers pool supports Vitest 5.
- [ ] **ES2026 target (each TypeScript minor release):** neither TS 6.0 nor 7.0 accepts `--target es2026` (checked 2026-09-28). Add a row to the Node mapping in `references/version-upgrade/ecmascript/es-upgrade-checklist.md` when a compiler release supports it.
- [ ] **Fastify 6 (at GA):** 6.0.0-alpha.5 on npm `next` (checked 2026-10-22). Add a Library majors row.
- [ ] **Express 4 (next check 2027-01-31):** expressjs.com/en/support lists 4.x as supported with no end date (checked 2026-10-22).
- [ ] **AWS Lambda `nodejs26.x` (GA targeted November 2026):** `version-policy.md` keeps Lambda on `nodejs24.x` while 26 is in preview; lift the precedence note at GA.

### Unverified facts
- [ ] `upgrade-protocol.md` → "Responding to a dependency security advisory" places `overrides` in `pnpm-workspace.yaml` for pnpm 11 and later; inferred from pnpm.io/migration, not from the `overrides` settings page (2026-10-22).
- [ ] Prisma 7 SQL Server: the Prisma SQL Server page names `@prisma/adapter-mssql` but does not say whether it is GA or preview (checked 2026-10-22).
- [ ] Prisma 7 guide asks for `"type": "module"` and a `bundler` tsconfig; `prisma-6-to-7.md` relies on the 2026-09-28 check (see Done) that the generated client type-checks under the `NodeNext` tsconfig. Re-verify on a CommonJS NestJS or Next.js app.
- [ ] Node 22 → 24 behaviour-change list (fetch compliance, AbortSignal validation, stream error propagation) is summarised from the nodejs.org migration page headings, not from individual changelog entries (2026-09-28).
- [ ] ES2026 feature list in `references/version-upgrade/ecmascript/es-version-features.md` is from secondary coverage of the Ecma approval; confirm against the published ECMA-262 17th edition (2026-09-28).

### Follow-up work
- [ ] **pnpm 12 pilot:** run it on one repository: the Corepack form, the `allowBuilds` migration from `onlyBuiltDependencies`, the CI install and the Node floor (neither the pnpm 12.0 post nor the migration guide states one; `pnpm@12.14.0` `engines.node` is `>=18.*`, npm, checked 2026-10-22). Then confirm the new-project default in `version-policy.md`.
- [ ] **Library majors table** (`upgrade-protocol.md` → Library majors, added 2026-10-22): re-check each official guide URL on each review.

## Done
- 2026-10-22: Oxlint config-discovery alignment closed: `tooling.md` takes the exact Oxlint flags and Biome setup from `/lint` instead of restating them.
- 2026-10-22: Upgrade coverage: `upgrade-protocol.md` gained "Responding to a dependency security advisory", a pnpm 10 → 12 step, library rows and a Library majors table; new `references/version-upgrade/libraries/prisma-6-to-7.md`; SKILL.md upgrade triggers updated.
- 2026-10-22: October 2026 Node security release and version recommendations: one security snapshot in `version-policy.md`; support rules A–D inlined there; Node 26 for new projects from 2026-10-28; pnpm 12 for new projects after a pilot, 10 → 12 by 2027-01-31 skipping 11; Node 22 off by 2027-01-31; TypeScript 7 API wording corrected; Prisma `^7` pinned; Workers pool 0.23.0; `upgrade-protocol.md` gained "Responding to a Node security release".
- 2026-10-22: Next.js 15 unsupported since 2026-10-21; `version-policy.md` recommends 16 for new and existing projects.
- 2026-10-22: Next.js with TypeScript 7: `next build` runs the project's `tsc` CLI by default, which enables TypeScript 7; `experimental.useTypeScriptCli: false` reverts to the API checker, which fails on TS 7 (Next.js docs). Not yet tested here.
- 2026-10-01: Merged the former TypeScript version-upgrade skill into this skill (`references/version-upgrade/`, `upgrade-protocol.md`); the guides link to `version-policy.md`, `tooling.md` and `testing-strategies.md` by relative path.
- 2026-09-28: Full review: every complete snippet compiled under the `tooling.md` tsconfig on TypeScript 6.0.3; templates run on Vitest 4.1.11 and Jest 30.5.2 + ts-jest 29.4.14 (`templates/testing/tsconfig.jest.json`); Prisma 7.10.0 driver adapter, `prisma.config.ts` and the `orm.md` snippets type-checked and `PrismaClient({ adapter })` instantiated.

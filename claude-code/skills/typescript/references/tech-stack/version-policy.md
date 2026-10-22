# Version Policy — Node, TypeScript, pnpm and JS/TS Tooling

This file is the **single owner** of version policy for TypeScript/JavaScript work. The upgrade procedure (`../version-upgrade/upgrade-protocol.md`) and `/lint` (lint and format configs) link here instead of keeping their own version tables.

The policy names **target majors and rules**, not "latest" patch numbers. Patch numbers go stale; the rules below do not. Before writing a version into a file, check the live registry.

## Check live versions first

```bash
npm view <pkg> version                 # current npm "latest" tag
npm view <pkg> dist-tags               # latest, next, per-major tags (e.g. latest-10)
npm view <pkg>@<range> version         # newest release inside a range, e.g. typescript@~6.0
npm view <pkg> peerDependencies        # peer ranges (e.g. typescript-eslint's TypeScript ceiling)

# Node.js release lines, LTS status and security releases
curl -s https://nodejs.org/dist/index.json | python3 -c "
import json,sys
seen=set()
for r in json.load(sys.stdin):
    m=r['version'].split('.')[0]
    if m in seen: continue
    seen.add(m); print(r['version'], r['date'], 'lts=', r['lts'], 'security=', r['security'])
    if len(seen) > 6: break"
curl -s https://raw.githubusercontent.com/nodejs/Release/main/schedule.json   # start/lts/maintenance/end dates
```

npm's `latest` tag is not always a stable major: for example, `prisma`'s `latest` has pointed at an 8.0 release candidate. Read `dist-tags` before installing anything without a range.

## Node.js

| Line | Status (checked 2026-10-22) | Recommended use |
|------|------------------------------|-----------------|
| **26.x** | Current; Active LTS from 2026-10-28; end of life 2029-04-30 | **New projects: Node 26 from 2026-10-28** (Node 24 until then) |
| **24.x** | Maintenance LTS since 2026-10-20; end of life 2028-04-30 | **Existing projects**; move to 26 when next worked on |
| 22.x | Maintenance LTS; end of life 2027-04-30 | Only with a migration finished by 2027-01-31 (rule A below) |
| 20.x | **End of life 2026-04-30** | Not supported; upgrade now (`../version-upgrade/upgrade-protocol.md`) |

**Precedence:** AWS Lambda functions stay on `nodejs24.x` while `nodejs26.x` is in public preview on Lambda (GA targeted November 2026; preview runtimes are not covered by the Lambda SLA; <https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html>, checked 2026-10-22). For Lambda functions this overrides the new-repo pick of Node 26.

**Support rules** (used for every version line in this file):

- **A (default):** a line is acceptable while it has at least 12 months of upstream support left. With less than 12 months, keep it only with a dated migration that finishes 3 months before upstream end of life. A line past end of life is not acceptable. Always run the latest patch of the chosen line, never one older than that line's newest security release.
- **B (fast-release tools that support only their latest releases):** acceptable means the releases upstream still supports.
- **C (no published support policy, e.g. TypeScript, Hono, Vite):** the target is the project's pinned major; older majors move when the repository is next worked on.
- **D (paid extended support, e.g. managed databases):** the deadline is the end of standard support, so no extended-support charges start.

Applied here: Node and pnpm follow rule A, so Node 22 and pnpm 10 should be off by 2027-01-31; TypeScript follows rule C.

**Security-release snapshot (checked 2026-10-22):** the newest security releases are **26.12.1, 24.22.1 and 22.23.4** (October 2026 security release, 2026-10-21). This is the skill's only snapshot; other files point here. Update it after every Node security release.

Rules:

- **Always run the latest patch of the chosen line**, and never one older than the line's newest security release (snapshot above; live: `security=True` entries in `index.json`). Do not carry a one-CVE "minimum floor" forward: security releases keep landing. Responding to a release: `../version-upgrade/upgrade-protocol.md` → "Responding to a Node security release".
- **`.nvmrc` / `.node-version`: major only** (`24`), so version managers resolve the newest patch.
- **`package.json` `engines.node`**: applications use the major (`">=24"` or `"^24"`); libraries declare the oldest LTS line they actually test.
- **Container images**: use the major tag (`node:26-alpine`, `node:26-slim` for Node 26 projects; `node:24-alpine`, `node:24-slim` for Node 24) or a patch tag that is bumped with every Node security release. A patch literal copied from documentation goes stale within months.
- **Corepack enforces the `packageManager` hash — keep it, and install it explicitly.** Corepack is bundled up to Node 24 and not from Node 25 onward, so the team form installs a pinned Corepack and enables it; this works the same on Node 24 and 25+ (see "pnpm" below).
- **`@types/node` matches the runtime major** (`^24` on Node 24; it becomes `^26` with the move to Node 26). A newer `@types/node` than the runtime lets code type-check against APIs the runtime lacks.

Pipeline images, runners and deployment follow the same rules; keep CI images on the same Node line as `.nvmrc`.

## TypeScript

| Line | Status (checked 2026-10-22) | Recommended use |
|------|------------------------------|-----------------|
| **6.0** | Latest 6.x is 6.0.3 (2026-04-16); no patch since | **Default: `typescript@~6.0`** for new and existing projects |
| 7.0 | npm `latest` (7.0.2, 2026-07-08); native (Go) compiler; exports only an unstable compiler API under `typescript/unstable/*` | Optional type-check-only lane |
| 7.1 | `beta` (7.1.0-beta, 2026-10-20; RC expected in about a month) | Not adopted; see "Revisit" below |
| 5.x | Existing projects; minimum 5.9 | Move to 6.0 when the project is next worked on (`../version-upgrade/typescript/typescript-5-to-6.md`) |

The 7.1 beta moves the compiler API to `typescript/sync`, `typescript/async`, `typescript/fs` and `typescript/ast/*`, still with no stability promise. Tools that load the API do not accept 7.x (peer ranges in the first rule below). Microsoft publishes no support policy for either line (6.0 or 7.x), so TypeScript follows rule C. The 5.9 minimum is Prisma 8's floor.

**Revisit** the default when TypeScript 7.1 is GA **and** typescript-eslint supports TypeScript 7 (`../../TODO.md`).

Rules:

- **Pin `typescript@~6.0`** in every project where typescript-eslint, ts-jest, tsup `dts`, api-extractor or any other compiler-API tool runs. typescript-eslint 8.72's peer range is `>=4.8.4 <6.1.0`; ts-jest's is `<7` (checked 2026-10-22).
- **Never run an unpinned `pnpm add -D typescript`.** It installs 7.x today and breaks every tool above.
- **TS 7 lane (optional):** run the native compiler as an extra, faster type check without changing the project's pinned `typescript`:
  ```bash
  pnpm dlx --package=typescript@^7.0 tsc --noEmit -p tsconfig.json
  ```
  TS 7 treats `baseUrl`, `moduleResolution: "node"`/`"node10"`/`"classic"`, `esModuleInterop: false`, `downlevelIteration`, `target: "es5"` and `module: "amd"|"umd"|"system"|"none"` as hard errors. Keep every tsconfig free of them now (see `../coding-standards/tooling.md`), so the switch is a version bump. When a project adopts 7.x as primary, `@typescript/typescript6` provides the 6.0 API side by side.

## pnpm

| Line | Status (checked 2026-10-22, pnpm `SECURITY.md`) | Recommended use |
|------|------------------------------|-----------------|
| **12.x** | Supported; npm `latest` 12.14.0; 12.15.0 (2026-10-21 hardening release) is on `next-12` | **New projects**, after a pilot on one repository first. Pin 12.15.0 once it becomes `latest` |
| **10.x** | Supported until 2027-04-30; latest 10.34.7 | **Existing projects**: latest 10.x patch; move straight to 12 by 2027-01-31 (rule A) |
| 11.x | Supported until 2027-04-30, the same day as 10 | Skip; no move to 11 |
| ≤ 9.x | Unsupported | Move to 12 |

- **Pin one pnpm major per repository** with its hash in the `packageManager` field (`"pnpm@12.x.y+sha512.<hash>"`). Move to a new major deliberately (read its breaking changes) rather than by drift.
- **Install pnpm through a pinned Corepack**, everywhere (developer machines, Dockerfiles, CI):
  ```bash
  npm view corepack version                      # pick the pin (0.36.0, checked 2026-10-22)
  npm install -g corepack@<pinned> && corepack enable
  corepack use pnpm@<12.x.y>                     # once per repo: writes "pnpm@12.x.y+sha512.<hash>"
  ```
  Corepack then downloads the pnpm version named in `packageManager` and refuses it if the sha512 does not match (`Mismatch hashes`). The check runs on download; a copy already in the Corepack cache (`COREPACK_HOME`) is reused, so build images from a clean cache. Do not replace this with `npm install -g pnpm`, which skips the hash check, and do not rely on the Node-bundled Corepack, which Node 25+ no longer ships. Pick the pnpm version from `npm view pnpm dist-tags` (`latest-12`, or `latest-10` for an existing project still on 10).
- Commit `pnpm-lock.yaml`; CI installs with `--frozen-lockfile`.
- pnpm blocks dependency lifecycle scripts by default: allow native builds explicitly. pnpm 10: `pnpm.onlyBuiltDependencies` or `pnpm approve-builds`. pnpm 11 and later removed `onlyBuiltDependencies` and its sibling settings in favour of `allowBuilds` in `pnpm-workspace.yaml` (written by `pnpm approve-builds` or `pnpm add --allow-build`), and `strictDepBuilds` defaults to `true`, so an install with unreviewed builds fails (pnpm.io/settings/build, checked 2026-10-22). Move the allow-list when a repository moves from 10 to 12.
- Run installed CLIs with `pnpm exec <bin>` (or a package script). `pnpm dlx` is for one-off tools that are not project dependencies.

## Frameworks

| Framework | New projects | Existing projects |
|-----------|--------------|-------------------|
| Next.js | 16 | 16. Next.js 15 is unsupported since 2026-10-21 (nextjs.org support policy); move a project still on 15 to 16 |
| React | 19 | 18 → 19 via `../version-upgrade/react/react-to-19.md` |
| Tailwind CSS | 4 | 3 only where legacy browsers require it |
| Vue | 3 | — |
| Astro | current major (see `astro.md`) | — |

## Tools

| Tool | Target | Notes |
|------|--------|-------|
| Vitest (+ `@vitest/coverage-v8`) | `^4.1` | Cloudflare's Workers pool (`@cloudflare/vitest-pool-workers` 0.23.0) still peers `vitest ^4.1.0` (checked 2026-10-22); Vitest 5 (2026-09) is not adopted yet. October 2026 CVE fixes (e.g. CVE-2026-112942) are in Vitest 4.1.12 and Vite 8.1.6 / 8.2.4 / 8.3.3; the caret ranges admit them, so refresh the lockfile (`pnpm update vitest @vitest/coverage-v8 vite`). |
| Playwright (`@playwright/test`) | `^1` | |
| Zod | `^4` | Zod 3 only in projects not yet migrated |
| Hono | `^4` | |
| `@hono/zod-openapi` | `^1` | Requires `zod ^4` and `hono >=4.10` |
| tRPC | `^11` | |
| Drizzle (`drizzle-orm`, `drizzle-kit`, `drizzle-zod`) | caret on the current `0.x` minor | Pre-1.0; a caret on `0.x` already pins the minor. Read release notes on every minor |
| Prisma (`prisma`, `@prisma/client`) | `^7` | Pin `prisma@^7` explicitly: npm `prisma@latest` resolves to 8.0.0-rc.24 (checked 2026-10-22), so an unpinned install gets a release candidate (see `orm.md`). Decide on 8 after its GA: 7 gets fixes for 18 months after 8 GA; 8 needs Node `^22.18 \|\| ^24.11 \|\| >=26` and TypeScript ≥5.9 |
| Oxlint / Biome / residual ESLint | Oxlint `^1`, Biome `^2`, ESLint `^10`, typescript-eslint `^8` | Config and usage: `/lint` |
| husky / lint-staged | `^9` / `^17` | Hook setup: `/lint` |
| tsx | `^4` | Runs TypeScript directly (dev, scripts, Node services) |
| tsdown | caret on the current `0.x` minor | Bundling libraries and CLIs |
| tsup | existing projects only | Upstream says it is not actively maintained; use tsdown for new bundling |
| Fastify | `^5` | See `../patterns/node-services.md` |
| Temporal TypeScript SDK | `^1` | Temporal's TypeScript SDK docs |

## How to pin

- Use a **caret on the major** for 1.x-and-above packages (`^4`, `^19`). For `0.x` packages a caret pins the minor (`^0.45` allows 0.45.x only).
- **Never write `"latest"` in `package.json`.** It makes the manifest non-reproducible and hides major bumps inside a routine install.
- Commit the lockfile. Use exact pins only where the repository's own policy asks for them.

## Build and run (TypeScript output)

| Need | Tool |
|------|------|
| Run TypeScript (dev, scripts, Node services) | `tsx` |
| Type-check | `tsc --noEmit` |
| Emit JS + `.d.ts` for a package | `tsc` (or tsdown when a bundle is needed) |
| Bundle a library or CLI | tsdown |
| Frontend apps | Vite (or the framework's own build) |
| Workers | Wrangler |

---

*Facts checked 2026-10-22 for the Node table and security snapshot (nodejs.org `index.json`, the Node Release schedule and the October 2026 security release post), TypeScript, pnpm (`SECURITY.md`, npm dist-tags), Next.js, Prisma and the Workers pool; other facts checked 2026-09-28 against npm, nodejs.org and the TypeScript 7.0 announcement. The Corepack form was tested on Node 24.21.0 with Corepack 0.36.0 and pnpm 10.34.5 (a tampered hash failed with `Mismatch hashes`). Re-check with the commands above before relying on any number.*

# Version Policy — Node, TypeScript, pnpm and JS/TS Tooling

This file is the **single owner** of version policy for TypeScript/JavaScript work. `/typescript-version-upgrade` (upgrade procedures) and `/lint` (lint and format configs) link here instead of keeping their own version tables.

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

| Line | Status (checked 2026-09-28) | Recommended use |
|------|------------------------------|-----------------|
| **24.x** | LTS; enters Maintenance 2026-10-20; end of life 2028-04-30 | **Default runtime today** |
| **26.x** | Current; becomes LTS 2026-10-28 | **New projects move to 26 once it is LTS** |
| 22.x | Maintenance LTS; end of life 2027-04-30 | Existing projects only; plan the move to 24 |
| 20.x | **End of life 2026-04-30** | Upgrade now (`/typescript-version-upgrade`) |

Rules:

- **Always run the latest patch of the chosen line.** Do not carry a one-CVE "minimum floor" forward: security releases keep landing. Check `security=True` entries in `index.json` (as of 2026-09-28 the newest security releases were 24.18.1 and 22.23.2, 2026-07-28).
- **`.nvmrc` / `.node-version`: major only** (`24`), so version managers resolve the newest patch.
- **`package.json` `engines.node`**: applications use the major (`">=24"` or `"^24"`); libraries declare the oldest LTS line they actually test.
- **Container images**: use the major tag (`node:24-alpine`, `node:24-slim`) or a patch tag that is bumped with every Node security release. A patch literal copied from documentation goes stale within months.
- **Corepack enforces the `packageManager` hash — keep it, and install it explicitly.** Corepack is bundled up to Node 24 and not from Node 25 onward, so the team form installs a pinned Corepack and enables it; this works the same on Node 24 and 25+ (see "pnpm" below).
- **`@types/node` matches the runtime major** (`^24` on Node 24). A newer `@types/node` than the runtime lets code type-check against APIs the runtime lacks.

Pipeline images, runners and deployment follow the same rules; keep CI images on the same Node line as `.nvmrc`.

## TypeScript

| Line | Status (checked 2026-09-28) | Recommended use |
|------|------------------------------|-----------------|
| **6.0** | Latest 6.x is 6.0.3 | **Default: `typescript@~6.0`** |
| 7.0 | npm `latest` (7.0.2, 2026-07-08); native (Go) compiler; **no programmatic API until 7.1** | Optional type-check-only lane |
| 5.x | Existing projects | Upgrade to 6.0 with `/typescript-version-upgrade` |

Rules:

- **Pin `typescript@~6.0`** in every project where typescript-eslint, ts-jest, tsup `dts`, api-extractor or any other compiler-API tool runs. typescript-eslint's peer range is `>=4.8.4 <6.1.0`; ts-jest's is `<7`.
- **Never run an unpinned `pnpm add -D typescript`.** It installs 7.x today and breaks every tool above.
- **TS 7 lane (optional):** run the native compiler as an extra, faster type check without changing the project's pinned `typescript`:
  ```bash
  pnpm dlx --package=typescript@^7.0 tsc --noEmit -p tsconfig.json
  ```
  TS 7 treats `baseUrl`, `moduleResolution: "node"`/`"node10"`/`"classic"`, `esModuleInterop: false`, `downlevelIteration`, `target: "es5"` and `module: "amd"|"umd"|"system"|"none"` as hard errors. Keep every tsconfig free of them now (see `coding-standards/tooling.md`), so the switch is a version bump. When a project adopts 7.x as primary, `@typescript/typescript6` provides the 6.0 API side by side.

## pnpm

- **Pin one pnpm major per repository** with its hash in the `packageManager` field. The examples here use pnpm 10; pnpm 11 and 12 exist, so move to a new major deliberately (read its breaking changes) rather than by drift.
- **Install pnpm through a pinned Corepack**, everywhere (developer machines, Dockerfiles, CI):
  ```bash
  npm view corepack version                      # pick the pin (0.36.0 on 2026-09-28)
  npm install -g corepack@<pinned> && corepack enable
  corepack use pnpm@<x.y.z>                      # once per repo: writes "pnpm@x.y.z+sha512.<hash>"
  ```
  Corepack then downloads the pnpm version named in `packageManager` and refuses it if the sha512 does not match (`Mismatch hashes`). The check runs on download; a copy already in the Corepack cache (`COREPACK_HOME`) is reused, so build images from a clean cache. Do not replace this with `npm install -g pnpm`, which skips the hash check, and do not rely on the Node-bundled Corepack, which Node 25+ no longer ships. Pick the pnpm version from `npm view pnpm@<major> version`.
- Commit `pnpm-lock.yaml`; CI installs with `--frozen-lockfile`.
- pnpm 10 blocks dependency lifecycle scripts by default: allow native builds explicitly (`pnpm.onlyBuiltDependencies` or `pnpm approve-builds`).
- Run installed CLIs with `pnpm exec <bin>` (or a package script). `pnpm dlx` is for one-off tools that are not project dependencies.

## Frameworks

| Framework | New projects | Existing projects |
|-----------|--------------|-------------------|
| Next.js | 16 | 15 receives security fixes only; plan the move to 16 |
| React | 19 | 18 → 19 via `/typescript-version-upgrade` |
| Tailwind CSS | 4 | 3 only where legacy browsers require it |
| Vue | 3 | — |
| Astro | current major (see `astro.md`) | — |

## Tools

| Tool | Target | Notes |
|------|--------|-------|
| Vitest (+ `@vitest/coverage-v8`) | `^4.1` | Cloudflare's Workers pool (`@cloudflare/vitest-pool-workers` 0.22) peers `vitest ^4.1`; Vitest 5 (2026-09) is not adopted yet |
| Playwright (`@playwright/test`) | `^1` | |
| Zod | `^4` | Zod 3 only in projects not yet migrated |
| Hono | `^4` | |
| `@hono/zod-openapi` | `^1` | Requires `zod ^4` and `hono >=4.10` |
| tRPC | `^11` | |
| Drizzle (`drizzle-orm`, `drizzle-kit`, `drizzle-zod`) | caret on the current `0.x` minor | Pre-1.0; a caret on `0.x` already pins the minor. Read release notes on every minor |
| Prisma (`prisma`, `@prisma/client`) | `^7` | npm `latest` is an 8.0 release candidate; always pin `^7` (see `orm.md`) |
| Oxlint / Biome / residual ESLint | Oxlint `^1`, Biome `^2`, ESLint `^10`, typescript-eslint `^8` | Config and usage: `/lint` |
| husky / lint-staged | `^9` / `^17` | Hook setup: `/lint` |
| tsx | `^4` | Runs TypeScript directly (dev, scripts, Node services) |
| tsdown | caret on the current `0.x` minor | Bundling libraries and CLIs |
| tsup | existing projects only | Upstream says it is not actively maintained; use tsdown for new bundling |
| Fastify | `^5` | See `patterns/node-services.md` |
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

*Facts checked 2026-09-28 against npm, nodejs.org and the TypeScript 7.0 announcement; the Corepack form was tested on Node 24.21.0 with Corepack 0.36.0 and pnpm 10.34.5 (a tampered hash failed with `Mismatch hashes`). Re-check with the commands above before relying on any number.*

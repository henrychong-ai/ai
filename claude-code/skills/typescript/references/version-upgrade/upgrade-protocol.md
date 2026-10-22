# Version Upgrade Protocol

How to move a repo's Node.js, TypeScript, ECMAScript target, React, Next.js, package manager or a key library major (Prisma, Zod, Tailwind CSS, Vitest and others in "Library majors" below) to a new version safely. Version *policy* (which versions you run, pin and target) lives in `references/tech-stack/version-policy.md`, and the canonical tsconfig in `references/coding-standards/tooling.md`; this file owns *how* to move a repo there. Read current per-repo versions from your organisation's repo inventory, if you keep one, instead of guessing which repos need an upgrade.

Paths below are relative to the `/typescript` skill root. The per-step guides live in `references/version-upgrade/`.

## Production Safety

These upgrades may run against live production applications, including systems that move money or handle other critical data. Scope every change to what the version upgrade requires: keep business logic and function signatures unchanged unless the new version forces a change, keep every test and the coverage baseline, write the rollback plan before the first change, and commit only after the validation gates and CI/CD pipelines pass and the user approves.

## Precedence: approvals and test edits

This rule wins over anything in the upgrade guides under `references/version-upgrade/`:
- **Approval** happens at phase checkpoints — after the plan, after version-file and dependency changes, and before commit — not per file. Stop early only for the stop conditions in `references/version-upgrade/safety/ai-guardrails.md`.
- **Test edits** are allowed only when the new version changes observable output that the test pins (an error message, a deprecation warning, a renamed import), and each one is listed in the checkpoint report with its cause. A test that fails for any other reason is a behaviour change: stop and report it.

## Operation Modes

| Mode | Output |
|---|---|
| **ANALYZE** (default) | Current version inventory, required upgrades with rationale, risk, effort. No changes. |
| **PLAN** | Ordered steps, file-by-file change list, test checkpoints, rollback plan. |
| **EXECUTE** | Runs the plan through the validation gates, with the approval checkpoints above. |

## Step 0: Check live versions

Version facts go stale within weeks. Before recommending a target, read them live:

```bash
curl -s https://nodejs.org/dist/index.json | python3 -c "
import json,sys; seen=set()
for r in json.load(sys.stdin):
    m=r['version'].split('.')[0]
    if m not in seen: seen.add(m); print(m, r['version'], r['date'], 'lts=',r['lts'], 'security=',r['security'])" | head -6
# newest security release per line: the script in references/version-upgrade/node/migration-overview.md
curl -s https://raw.githubusercontent.com/nodejs/Release/main/schedule.json   # LTS / maintenance / EOL dates
npm view typescript dist-tags
npm view <package> version
```

Node patches: run the latest patch of the chosen line, and never one older than the line's newest `"security": true` release in `index.json` (lookup script: `references/version-upgrade/node/migration-overview.md`; dated snapshot: `references/tech-stack/version-policy.md` → Node.js). Do not carry a single-CVE "minimum floor" forward.

### Responding to a Node security release

- **Find each line's fixed patch** from the `"security": true` entries in `index.json` (script above). Each line gets a different fix set, so read the advisory per line; an end-of-life line is always treated as affected. Then update the snapshot in `references/tech-stack/version-policy.md`.
- **Images:** a major tag (`node:24-alpine`) picks up the fix only when the image is rebuilt with a fresh base pull (`docker build --pull`) and every service on that line is redeployed. A running container whose `node --version` is below the fixed patch is still exposed.
- **Single executable applications and startup snapshots** (`--build-snapshot`) embed the Node binary or heap they were built with: rebuild them on the fixed patch (October 2026: CVE-2026-106074, `crypto.randomUUID()`/`randomInt()` entropy caches saved into snapshots).
- **undici:** the undici behind global `fetch` is bundled with Node and updated by the release; an `undici` dependency installed from npm is separate and must be bumped on its own.
- **Behaviour changes:** security patches can change behaviour (October 2026: TLS rejects non-canonical IP addresses and chains containing blocked public keys). Run integration tests against the real outbound TLS endpoints before rollout.
- **Trust store:** Node's root store is compiled into the binary (NSS 3.131.1 in the October 2026 releases), and its blocked-key list applies even with `--use-system-ca`, `NODE_EXTRA_CA_CERTS` or a custom `ca`; a match reports `CERT_REVOKED`. TLS sessions resumed from before the upgrade are not re-verified until they expire. Node is one trust layer among several: the OS store (`ca-certificates`, used by curl, git, Go on Linux and OS-packaged runtimes), language bundles such as Python's certifi, Java's `cacerts`, and roots compiled into binaries each update separately. After a root-store or distrust change, update each layer the service uses (OS package in the image, runtime patch, bundled packages), rebuild the images, and test real TLS connections from the deployed environment.

### Responding to a dependency security advisory

For an npm package advisory (a library, Vite, Vitest, Next.js, pnpm itself):

- **Check the range first:** if the fixed version is inside the manifest's existing range (`npm view <pkg>@<range> version`), the fix is a lockfile refresh, not a manifest change: `<pm> update <pkg>` (pnpm, npm, Yarn) for each affected package, then confirm with `<pm> why <pkg>` (npm: `npm ls <pkg>`) that no other copy stays below the fixed version in the transitive tree.
- **Outside the range** (the fix exists only on a newer major): treat it as a major upgrade under this protocol, or pin the patched version through the package manager's override mechanism (`pnpm.overrides` in pnpm 10, `overrides` in `pnpm-workspace.yaml` in pnpm 11 and later, npm `overrides`, Yarn `resolutions`) with a dated TODO to remove the override.
- **Rebuild and redeploy** every image and artefact built from the old lockfile; a fixed lockfile on `main` does not patch a running container. Browser bundles (Vite, Next.js) need a rebuild and redeploy too.
- **Dev-only packages** (Vite dev server, Vitest UI) still need the refresh: developer machines and CI runners are exposed.
- **Package-manager release:** a pnpm security or hardening release is a `packageManager` change: `corepack use pnpm@<fixed>` (writes the hash), rebuild CI and Docker images from a clean Corepack cache (`references/tech-stack/version-policy.md` → pnpm).

## Detection Matrix

| Source | What to read | Flag when |
|---|---|---|
| `.nvmrc` / `.node-version` | Node version | Below policy, or disagrees with other sources |
| `package.json` `engines.node` | Constraint | Allows an EOL line, or excludes the deployed line |
| `package.json` `packageManager` | PM and pinned version | Missing, or not the policy version |
| Dockerfile `FROM` (all stages) | Base image tag | Floating across majors (`lts`, `latest`, `current`), a different major from `.nvmrc`, or a patch literal older than the line's latest security release |
| Pipeline images (`bitbucket-pipelines.yml` top-level and per-step `image:`, GitHub `setup-node`) | CI Node | Differs from the runtime line |
| `@types/node` in every workspace `package.json` | Types major | Major differs from the runtime major |
| `typescript` in every `package.json` | Compiler version and range | Below policy, or unpinned where a compiler-API tool runs |
| `tsconfig*.json` `target` / `lib` / `module` / `moduleResolution` / `baseUrl` / `types` | Compiler config | Deprecated in TS 6 (see `references/version-upgrade/typescript/typescript-5-to-6.md`) |
| Bundler configs (`vite.config.*`, `tsdown.config.*`, `esbuild`, `webpack.config.*`) | Build target | Newer than the oldest runtime or browser you ship to |
| `.browserslistrc` / `package.json` `browserslist` | Browser floor | Older than the framework's floor |
| `next`, `react`, `react-dom` versions | Framework majors | Unsupported by the target Node, or behind policy |
| Library majors in every `package.json` (`prisma`/`@prisma/client`, `zod`, `tailwindcss`, `vitest`/`@vitest/*`, `eslint`/`typescript-eslint`, `jest`, `express`, `astro`, `hono`) | Library majors and ranges | Behind the target in `references/tech-stack/version-policy.md`, `"latest"` or unpinned, or sibling packages on different versions (`prisma` vs `@prisma/client`, `vitest` vs `@vitest/coverage-v8`) |
| pnpm settings: `package.json` `pnpm` field, `.npmrc`, `pnpm-workspace.yaml` | Build allow-list and settings location | pnpm 10 settings (`onlyBuiltDependencies`, `package.json#pnpm`, non-auth `.npmrc` keys) in a repo moving to pnpm 12 |

**`lts`/`latest`/`current` tags are a silent major upgrade:** `node:lts*` moves to the next line on the LTS promotion date (Node 26 on 2026-10-28). Use the major tag (`node:24-alpine`) or a patch tag that is bumped with every Node security release, as `references/tech-stack/version-policy.md` sets out.

## Package manager commands

Detect from the lockfile, then confirm with `packageManager`. Use this table's commands wherever a reference shows `pnpm`.

| Lockfile | PM | Install (keep lockfile) | CI install | Rebuild natives | Run binary |
|---|---|---|---|---|---|
| `pnpm-lock.yaml` | pnpm | `pnpm install` | `pnpm install --frozen-lockfile` | `pnpm rebuild` | `pnpm exec <bin>` |
| `package-lock.json` | npm | `npm install` | `npm ci` | `npm rebuild` | `npx --no-install <bin>` |
| `yarn.lock` + `.yarnrc.yml` | Yarn 2+ | `yarn install` | `yarn install --immutable` | `yarn rebuild` | `yarn <bin>` |
| `yarn.lock` only | Yarn 1 | `yarn install` | `yarn install --frozen-lockfile` | `npm rebuild` | `yarn <bin>` |
| `bun.lock` / `bun.lockb` | Bun | `bun install` | `bun install --frozen-lockfile` | reinstall the package | `bunx <bin>` |

pnpm does not run dependency build scripts unless the package is allowed (`pnpm approve-builds`; the allow-list is `onlyBuiltDependencies` in pnpm 10 and `allowBuilds` in pnpm 11 and later); a native module that "rebuilt" silently may not have. Node 25 and later do not bundle Corepack: install a pinned Corepack, then enable it (`npm install -g corepack@<pinned> && corepack enable`), so Corepack installs and hash-verifies the package manager pinned in `packageManager` (pinned form: `references/tech-stack/version-policy.md`). Details: `references/version-upgrade/node/node-24-to-26.md`.

## Upgrade Execution Protocol

### Phase 1: Pre-flight

```bash
git status --porcelain                       # must be empty
git switch -c upgrade/node-<from>-to-<to>-$(date +%Y%m%d)

BASE="${TMPDIR:-/tmp}/upgrade-baseline-$(basename "$PWD")-$(date +%Y%m%d)"
mkdir -p "$BASE"                              # outside the worktree, never committed
node --version > "$BASE/versions.txt"
<pm> test 2>&1 | tee "$BASE/test.txt"
<pm> run build 2>&1 | tee "$BASE/build.txt"
```

Write the rollback plan (below) into the upgrade plan before changing anything.

### Phase 2: Version files

Update every source from the Detection Matrix together so they agree: `.nvmrc`/`.node-version`, `engines`, every Dockerfile stage, every pipeline image, `@types/node` majors, `packageManager` if the PM changes.

### Phase 3: Dependencies — keep the lockfile

```bash
nvm use                      # or the repo's version manager
<pm> install                 # updates only what the manifest changes require
<pm> rebuild                 # native modules against the new ABI
<pm> install 2>&1 | grep -i peer
```

Regenerating a lockfile from scratch unpins the whole transitive tree; that is a separate, reviewed change, never part of a runtime upgrade.

### Phase 4: Code migration

Load the guide for each step of the path, applying consecutive guides in order (e.g. Node 20→22 then 22→24):

| Upgrade | Guide |
|---|---|
| Node ≤18 → 24 | `references/version-upgrade/node/legacy-node-to-24.md` |
| Node 20 → 22 | `references/version-upgrade/node/node-20-to-22.md` |
| Node 22 → 24 | `references/version-upgrade/node/node-22-to-24.md` |
| Node 24 → 26 | `references/version-upgrade/node/node-24-to-26.md` |
| TypeScript 3.x/4.x → 5 | `references/version-upgrade/typescript/typescript-legacy-to-5.md` |
| TypeScript 5 → 6 | `references/version-upgrade/typescript/typescript-5-to-6.md` |
| TypeScript 6 → 7 | `references/version-upgrade/typescript/typescript-6-to-7.md` |
| React 16/17/18 → 19 | `references/version-upgrade/react/react-to-19.md` |
| Next.js 13 → 14 → 15 → 16 | `references/version-upgrade/frameworks/nextjs-migrations.md` |
| ES target / lib | `references/version-upgrade/ecmascript/es-upgrade-checklist.md` |
| Prisma 6 → 7 | `references/version-upgrade/libraries/prisma-6-to-7.md` |
| pnpm 10 (or older) → 12 | "Package-manager major: pnpm 10 → 12" below |
| Other library majors (Zod, Tailwind CSS, Vitest, ESLint, Jest, Express, Astro) | "Library majors" table below; the official guide it links is the source |

General Node principles, Docker and CI changes: `references/version-upgrade/node/migration-overview.md`.

### Package-manager major: pnpm 10 → 12

Recommended path (`references/tech-stack/version-policy.md` → pnpm): existing projects move from the latest pnpm 10 straight to 12 by 2027-01-31, skipping 11; pnpm 9 and older move to 12 now. Run it as its own branch and commit, never combined with a Node or library upgrade. Primary sources (checked 2026-10-22): https://pnpm.io/migration (covers 10 → 11 and 10 → 12: "v12 keeps the v11 changes"), https://pnpm.io/blog/releases/11.0, https://pnpm.io/blog/releases/12.0.

1. **Codemod:** `pnpm dlx codemod run pnpm-v10-to-v11` (the guide's command is `pnpx codemod run pnpm-v10-to-v11`). It moves settings from `package.json#pnpm` and non-auth `.npmrc` keys into `pnpm-workspace.yaml`, merges `onlyBuiltDependencies`, `neverBuiltDependencies`, `ignoredBuiltDependencies` and `onlyBuiltDependenciesFile` into one `allowBuilds` map, renames `allowNonAppliedPatches` → `allowUnusedPatches` and `auditConfig.ignoreCves` → `auditConfig.ignoreGhsas`, and moves `useNodeVersion` to `devEngines.runtime`.
2. **Pin 12 with its hash:** `corepack use pnpm@<12.x.y>` after installing the pinned Corepack (pinned form: `references/tech-stack/version-policy.md` → pnpm). This overwrites the `packageManager` value the codemod wrote.
3. **Manual follow-ups** (not automated): replace CVE IDs in `auditConfig` with GHSA IDs from `pnpm audit`; rename `npm_config_*` environment variables in CI to `pnpm_config_*`; Dockerfiles copy `pnpm-workspace.yaml` before `pnpm install`; replace `--frozen-lockfile false` with `--no-frozen-lockfile`; scripts named `clean`, `setup`, `deploy` or `rebuild` now shadow built-in commands (use `pnpm pm <name>` for the built-in).
4. **Behaviour changes to check:** unreviewed dependency builds fail the install (`strictDepBuilds` defaults to `true`; `ERR_PNPM_IGNORED_BUILDS`), so `allowBuilds` must list every native package; `minimumReleaseAge` defaults to 1440 minutes, so a package published in the last day does not resolve (set it per repo only by decision, and remember it delays emergency security patches by a day unless overridden); `blockExoticSubdeps` defaults to `true`; unknown `pnpm-workspace.yaml` keys fail with `ERR_PNPM_UNRECOGNIZED_WORKSPACE_SETTINGS` when the pinned pnpm runs; GitHub, GitLab and Bitbucket git dependencies resolve over HTTPS (SSH access needs a git `insteadOf` rewrite); `engineStrict` checks more of the tree.
5. **Lockfile:** run `pnpm install` once and review the diff. The first re-resolving install can rewrite peer variants of cyclic packages (a one-time diff); anything else in the diff is a resolution change to explain. CI keeps `--frozen-lockfile`.
6. **Gates:** the Phase 5 gates, plus a clean-cache CI run and a Docker build, and `pnpm install --frozen-lockfile` from a fresh clone.

### Phase 5: Validation gates

Run with the repo's own scripts; each must exit 0.

| Gate | Command | Pass condition |
|---|---|---|
| Type check | `<pm> exec tsc --noEmit` (or the repo's `typecheck` script) | 0 errors |
| Lint | `<pm> run lint` | 0 errors; new warnings explained |
| Unit tests | `<pm> test` | All pass; coverage ≥ baseline |
| Build | `<pm> run build` | Succeeds; artefact inspected |
| Integration / E2E | the repo's scripts, if present | All pass |
| Container | `docker build` with the new base image, then start it | Starts, health check passes |

Details, thresholds and baseline comparison: `references/version-upgrade/safety/testing-protocols.md`.

### Phase 6: Approval checkpoint

Report: files changed (diff summary), gate results against the baseline, each test edit with its cause, new warnings or deprecations, and a proceed/rollback recommendation. Wait for explicit approval before committing.

### Phase 7: Commit

Stage the files you changed by path (never `git add -A`; baseline files live outside the worktree). Commit message, following the repo's convention:

```
chore: upgrade Node.js from <X> to <Y>

- .nvmrc, engines, Dockerfile, pipeline image, @types/node
- Resolved <N> deprecation warnings
Addresses: CVE-XXXX-XXXXX (if applicable)
```

### Rollback

- **Before merge:** abandon the upgrade branch; nothing else changed.
- **After merge:** `git revert <merge-commit>` — this restores manifests and the lockfile together. Never rewrite shared history (`reset --hard` on a shared branch).
- **Deployed:** use your CI/CD runbook's production rollback for the service's deploy path.

## ECMAScript target

Set `target` to what the **oldest runtime you deploy to** supports, and keep `lib` aligned. Mapping, TypeScript minimums (ES2023 → TS 5.5, ES2024 → TS 5.7, ES2025 → TS 6.0) and the step-by-step protocol: `references/version-upgrade/ecmascript/es-upgrade-checklist.md`. The default tsconfig is `references/coding-standards/tooling.md`; do not introduce a second one. For Next.js and Vite front ends the tsconfig target does not control emitted code (`noEmit`; SWC/esbuild/Oxc use the browser target) — see `references/version-upgrade/ecmascript/browser-support.md`.

## Upgrade guides

- Node: `references/version-upgrade/node/migration-overview.md`, `legacy-node-to-24.md`, `node-20-to-22.md`, `node-22-to-24.md`, `node-24-to-26.md`
- TypeScript: `references/version-upgrade/typescript/typescript-legacy-to-5.md`, `typescript-5-to-6.md`, `typescript-6-to-7.md`
- React: `references/version-upgrade/react/react-to-19.md`
- Next.js: `references/version-upgrade/frameworks/nextjs-migrations.md`
- ECMAScript: `references/version-upgrade/ecmascript/es-upgrade-checklist.md`, `es-version-features.md`, `browser-support.md`, `bundler-configuration.md`, `polyfill-strategies.md`
- Safety: `references/version-upgrade/safety/ai-guardrails.md`, `references/version-upgrade/safety/testing-protocols.md`
- Libraries: `references/version-upgrade/libraries/prisma-6-to-7.md`; the rest in "Library majors" below
- pnpm: "Package-manager major: pnpm 10 → 12" above

### Library majors

The official migration guide is the source of truth for each hop; read it for the version you move **to**. Targets: `references/tech-stack/version-policy.md`. Find which of your repos need each hop with the Detection Matrix above. Upgrade one major at a time and one library per commit. Guides and facts checked 2026-10-22.

| Hop | Official migration guide | Main risks |
|---|---|---|
| Prisma 6 → 7 | https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7 | Full guide: `references/version-upgrade/libraries/prisma-6-to-7.md` (driver adapters, `prisma.config.ts`, no automatic `.env`, stricter TLS, driver pool defaults) |
| Prisma 7 → 8 | Not yet: 8 is a release candidate (`npm view prisma dist-tags`) | Watch item only; no guide until 8 is GA and you decide. 8 needs Node `^22.18 \|\| ^24.11 \|\| >=26` and TypeScript ≥5.9 |
| Zod 3 → 4 | https://zod.dev/v4/changelog | One `error` parameter replaces `message`/`invalid_type_error`/`required_error`/`errorMap`; `.format()`/`.flatten()` deprecated for `z.treeifyError()`; top-level formats (`z.email()`), stricter `z.uuid()`; `.default()` short-circuits on `undefined` (`.prefault()` keeps v3 behaviour); single-argument `z.record()` removed and enum keys exhaustive; `z.coerce` input is `unknown`. No official codemod (the guide links a community one). `@hono/zod-openapi` 1 requires Zod 4, so move them together |
| Tailwind CSS 3 → 4 | https://tailwindcss.com/docs/upgrade-guide | Browser floor Safari 16.4, Chrome 111, Firefox 128 (stay on 3.4 for older); JS config not auto-detected (`@config`); `@tailwind` directives become `@import "tailwindcss"`; PostCSS plugin is `@tailwindcss/postcss`, Vite plugin `@tailwindcss/vite`; renamed utilities (`shadow-sm` → `shadow-xs`, `rounded` → `rounded-sm`, `outline-none` → `outline-hidden`, `ring` → `ring-3`). Tool: `npx @tailwindcss/upgrade` (needs Node 20+), on its own branch; review visual diffs |
| Vitest 2 → 3 | https://v3.vitest.dev/guide/migration | `spy.mockReset` restores the original implementation; stricter error equality (`name`, `message`, `cause`, prototype); fake timers also mock `performance.now()`; options object as third `test` argument warns |
| Vitest 3 → 4 | https://v4.vitest.dev/guide/migration | Pools rewritten (`poolOptions` removed, `maxThreads`/`maxForks` → `maxWorkers`); `workspace` → `projects` inside `vitest.config.ts`; V8 coverage remapping changed reports and `coverage.all` removed (only loaded files unless `coverage.include` is set — the coverage baseline will move); mock behaviour changes (`vi.restoreAllMocks`, `new` on mocks); needs Vite 6 and Node 20. Target line `^4.1` (`version-policy.md`) |
| Vitest 4 → 5 | https://vitest.dev/guide/migration | **Only for Node-only projects** (no Cloudflare Workers pool, which peers Vitest 4) on Node ≥22.12; `version-policy.md` keeps `^4.1` as the default. `clearMocks` defaults to `true`; nested `vi.mock` throws; unawaited async assertions fail; inline projects inherit the root config; `coverage.include`/`exclude` match root-relative paths; config not looked up in parent directories; `json`/`junit` reporters write files; needs Vite ≥6.4 and Node ≥22.12 |
| ESLint 9 → 10 (and typescript-eslint) | https://eslint.org/docs/latest/use/migrate-to-10.0.0 ; typescript-eslint 7 → 8: https://typescript-eslint.io/blog/announcing-typescript-eslint-v8 | ESLint 9 reached end of life on 2026-08-06 (https://eslint.org/version-support/). `.eslintrc` no longer supported; config looked up from each file's directory; `eslint-env` comments error; new `eslint:recommended` rules; Node `^20.19 \|\| ^22.13 \|\| >=24`. typescript-eslint peers cap TypeScript (`version-policy.md`). Config and the recommended route (migrate to Oxlint + Biome, keeping residual ESLint only for gaps): `/lint` |
| Jest 29 → 30 | https://jestjs.io/docs/upgrading-to-jest30 | Node 18+, TypeScript 5.4+; JSDOM 26; removed matcher aliases (`toBeCalledWith` → `toHaveBeenCalledWith`; `eslint-plugin-jest` `no-alias-methods` auto-fixes); `--testPathPattern` → `--testPathPatterns`; `jest.mock()` paths case-sensitive. Older lines (24, 27) step through each major's notes. New test suites use Vitest (`references/testing/`) |
| Express 4 → 5 | https://expressjs.com/en/guide/migrating-5.html | Route syntax (named wildcards `/*splat`, braces for optional segments, no regexp characters); removed methods (`app.del`, `res.send(status)`, `res.redirect(url, status)`, `req.param`); rejected promises reach error middleware; `req.query` read-only with the `simple` parser; `req.body` `undefined` when unparsed; `express.static` `dotfiles` defaults to `ignore` (`.well-known` 404s). Codemods: `npx codemod@latest @expressjs/v5-migration-recipe`. Express 4 still lists as supported with no end date (https://expressjs.com/en/support/) |
| Astro 6 → 7 | https://docs.astro.build/en/guides/upgrade-to/v7/ | Vite 8; stricter Rust compiler (unclosed tags fail the build); Sätteri replaces remark/rehype as the default Markdown processor; `compressHTML` defaults to `'jsx'` (inline whitespace); `src/fetch.ts` reserved; `@astrojs/db` removed. Tool: `npx @astrojs/upgrade`. Node floor: `references/tech-stack/astro.md` |
| Hono 4 → 5 | None published yet (5.0.0-rc.1, 2026-10-10) | Watch item only: stay on `hono@^4` until 5 is GA and reviewed; `@hono/zod-openapi` must support 5 first |

## Integration Notes

- This skill owns version policy (`references/tech-stack/version-policy.md`) and the canonical tsconfig (`references/coding-standards/tooling.md`); `/lint` covers lint and format config; your CI/CD runbook owns pipeline images, deploys and rollbacks; your organisation's repo inventory holds each repo's current versions.
- Track multi-step upgrade progress as a checklist in the upgrade plan, marking each step as it completes.

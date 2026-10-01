# Version Upgrade Protocol

How to move a repo's Node.js, TypeScript, ECMAScript target, React or Next.js to a new version safely. Version *policy* (which versions you run, pin and target) lives in `references/tech-stack/version-policy.md`, and the canonical tsconfig in `references/coding-standards/tooling.md`; this file owns *how* to move a repo there. Read current per-repo versions from your organisation's repo inventory, if you keep one, instead of guessing which repos need an upgrade.

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
    if m not in seen: seen.add(m); print(m, r['version'], r['date'], 'lts=',r['lts'])" | head -6
curl -s https://raw.githubusercontent.com/nodejs/Release/main/schedule.json   # LTS / maintenance / EOL dates
npm view typescript dist-tags
npm view <package> version
```

Node patches: run the latest patch of the chosen line, and never one older than the line's newest `"security": true` release in `index.json` (lookup script: `references/version-upgrade/node/migration-overview.md`). Do not carry a single-CVE "minimum floor" forward.

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

pnpm 10 does not run dependency build scripts unless the package is allowed (`onlyBuiltDependencies`, or `pnpm approve-builds`); a native module that "rebuilt" silently may not have. Node 25 and later do not bundle Corepack: install a pinned Corepack, then enable it (`npm install -g corepack@<pinned> && corepack enable`), so Corepack installs and hash-verifies the package manager pinned in `packageManager` (pinned form: `references/tech-stack/version-policy.md`). Details: `references/version-upgrade/node/node-24-to-26.md`.

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

General Node principles, Docker and CI changes: `references/version-upgrade/node/migration-overview.md`.

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

## Integration Notes

- This skill owns version policy (`references/tech-stack/version-policy.md`) and the canonical tsconfig (`references/coding-standards/tooling.md`); `/lint` covers lint and format config; your CI/CD runbook owns pipeline images, deploys and rollbacks; your organisation's repo inventory holds each repo's current versions.
- Track multi-step upgrade progress as a checklist in the upgrade plan, marking each step as it completes.

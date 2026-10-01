# Node.js Migration Overview

General principles for Node.js upgrades. Version-specific breaking changes are in the per-step guides; version policy is in `../../tech-stack/version-policy.md`.

## Release model (verify live)

- Lines 20–26: even-numbered majors become LTS in October after their April/May release; LTS is Active for about a year, then Maintenance, then end-of-life ~30 months after release.
- From Node 27 (alpha October 2026, 27.0.0 April 2027) Node ships **one major per year and every release becomes LTS**; version numbers follow the calendar year. Source: nodejs.org "Evolving the Node.js Release Schedule".
- Only Active and Maintenance lines get security fixes. An end-of-life line is a finding in its own right.

Read the current state rather than trusting a table:

```bash
# Status and dates for every line
curl -s https://raw.githubusercontent.com/nodejs/Release/main/schedule.json | python3 -m json.tool

# Latest release and latest security release per line
curl -s https://nodejs.org/dist/index.json | python3 -c "
import json,sys
latest, sec = {}, {}
for r in json.load(sys.stdin):
    m = r['version'].split('.')[0]
    latest.setdefault(m, r['version'])
    if r['security']: sec.setdefault(m, (r['version'], r['date']))
for m in list(latest)[:6]:
    print(m, 'latest', latest[m], '| last security', *sec.get(m, ('-', '-')))"
```

Run the **latest patch** of the chosen line; never deploy one older than the line's latest security release from the script above. Cross-check the advisories at https://nodejs.org/en/blog/vulnerability for whether a given CVE affects your usage. Snapshot on 2026-09-28 (re-verify): Node 20 end-of-life since 2026-04-30; last security releases 24.18.1 and 22.23.2 (2026-07-28); Node 24 enters Maintenance 2026-10-20; Node 26 becomes LTS 2026-10-28.

## Migration strategy

- Move one LTS line at a time and apply the guides consecutively (20→22→24→26). A multi-line jump is fine when tests are strong, but read every intermediate guide.
- Run the app and tests with deprecation output before and after: `NODE_OPTIONS='--pending-deprecation --trace-deprecation' <pm> test`. Fix warnings before the upgrade when the old line allows it.
- Use the official codemods where they exist: `npx codemod run @nodejs/<recipe>` (catalogue: https://nodejs.org/en/learn/getting-started/userland-migrations). Commit or stash work first — they rewrite source.
- Deprecation IDs and status (documentation-only, runtime, end-of-life): https://nodejs.org/api/deprecations.html.

## Native modules

A new major changes the ABI (`NODE_MODULE_VERSION`), so every native addon must be rebuilt or have a matching prebuild.

```bash
find node_modules -name '*.node' -type f | head      # which packages ship native code
<pm> rebuild
```

pnpm 10 blocks dependency build scripts unless allowed (`pnpm approve-builds`, or `onlyBuiltDependencies`). If a native package loads with "compiled against a different Node.js version", it was not rebuilt.

## `@types/node`

Keep the `@types/node` major equal to the runtime major in every workspace package. A higher major lets code use APIs the runtime lacks; a lower one hides APIs and deprecations.

## Docker base images

```dockerfile
# Major tag (or a patch tag bumped with every security release)
FROM node:<major>-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g corepack@<pinned> && corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build && pnpm prune --prod

FROM node:<major>-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

- `node:lts`, `node:latest` and `node:current` change major under you; `lts` jumps on LTS promotion day. A major tag (`node:24-alpine`) tracks the line's patches, which is the recommended default; a patch literal must be bumped on every security release or it goes stale.
- Install a pinned Corepack and enable it (Node 25+ no longer bundles it). Corepack then downloads the package manager pinned in `packageManager` and verifies its `+sha512.` hash, so a tampered or wrong download fails the build. The pinned form is set in `../../tech-stack/version-policy.md`.
- Pipeline images, runners and registry flow: your CI/CD runbook.

## CI

Update every pipeline image and `setup-node` step to the same line as `.nvmrc`. On GitHub Actions prefer `node-version-file: '.nvmrc'` over a literal. Pipeline structure and images belong in your CI/CD runbook.

## Rollback

- Before merge: abandon the branch.
- After merge: `git revert <merge-commit>` (restores manifests and lockfile together).
- Deployed: your CI/CD runbook's production rollback.

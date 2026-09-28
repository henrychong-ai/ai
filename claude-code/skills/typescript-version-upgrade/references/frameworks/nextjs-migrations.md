# Next.js Major Upgrades — Index

The official upgrade guides are the source of truth; this file lists the path, the floors, the codemods and the changes that most often break. For App Router patterns after the upgrade, follow your Next.js conventions. Check the current release with `npm view next version` (16.3.6 on 2026-09-28).

Upgrade one major at a time: 13 → 14 → 15 → 16. Run every gate between steps.

## Read version-matched docs first

From Next.js 16.2 the package ships its own docs in `node_modules/next/dist/docs/`. Before editing, point the project's `AGENTS.md` at them:

```bash
npx @next/codemod@canary agents-md
```

Read the upgrade guide and API pages for the version you are moving **to**, not from memory.

## Codemods

The `upgrade` codemod bumps `next`, `react`, `react-dom` and types, and runs the version's mechanical transforms:

| PM | Command |
|---|---|
| pnpm | `pnpm dlx @next/codemod@canary upgrade latest` |
| npm | `npx @next/codemod@canary upgrade latest` |
| yarn | `yarn dlx @next/codemod@canary upgrade latest` |
| bun | `bunx @next/codemod@canary upgrade latest` |

Individual transforms (`npx @next/codemod@canary <transform> .`; list: https://nextjs.org/docs/app/guides/upgrading/codemods):

| Transform | For |
|---|---|
| `next-og-import` | 14: `ImageResponse` from `next/server` → `next/og` |
| `metadata-to-viewport-export` | 14: viewport fields out of `metadata` |
| `built-in-next-font` | 14/15: `@next/font` → `next/font` |
| `next-async-request-api` | 15/16: async `cookies`/`headers`/`draftMode`/`params`/`searchParams` (**not** run by `upgrade` on 16 — run it explicitly) |
| `next-request-geo-ip` | 15: `NextRequest.geo`/`ip` removed |
| `app-dir-runtime-config-experimental-edge` | 15: `runtime: 'experimental-edge'` → `'edge'` |
| `next-experimental-turbo-to-turbopack` | 16: `experimental.turbopack` → top-level `turbopack` |
| `middleware-to-proxy` | 16: `middleware.ts` → `proxy.ts` |
| `next-lint-to-eslint-cli` | 16: `next lint` removed |
| `remove-unstable-prefix`, `remove-experimental-ppr` | 16 |

## 13 → 14 — https://nextjs.org/docs/app/guides/upgrading/version-14

- Node ≥18.17 (current Next.js needs Node ≥20.9 — go straight to your standard runtime).
- `next export` removed → `output: 'export'` in `next.config`.
- `ImageResponse` moved to `next/og`; `@next/font` removed; WASM `next-swc` target removed.
- Install: `<pm> add next@next-14 react@18 react-dom@18` (plus `eslint-config-next@next-14` if used).

## 14 → 15 — https://nextjs.org/docs/app/guides/upgrading/version-15

- React 19 is the minimum for the App Router → also follow `../react/react-to-19.md`.
- Request APIs become async (`cookies`, `headers`, `draftMode`, `params`, `searchParams`); 15 allows temporary sync access with a dev warning.
- **Caching defaults flip:** `fetch` is no longer cached by default (opt in with `cache: 'force-cache'` or `fetchCache`); `GET` route handlers are not cached; page segments are not reused from the client router cache (`experimental.staleTimes`). Check any page that depended on implicit caching — this changes load on upstream APIs.
- Config renames: `experimental.serverComponentsExternalPackages` → `serverExternalPackages`; `experimental.bundlePagesExternals` → `bundlePagesRouterDependencies`.
- `NextRequest.geo`/`ip` removed; `runtime: 'experimental-edge'` errors; Speed Insights auto-instrumentation removed.

## 15 → 16 — https://nextjs.org/docs/app/guides/upgrading/version-16

- Node ≥20.9, TypeScript ≥5.1; browsers Chrome/Edge/Firefox 111+, Safari 16.4+.
- **Turbopack is the default** for `next dev` and `next build`. A custom `webpack` config makes `next build` fail; opt out with the `--webpack` flag (there is no config switch). `experimental.turbopack` moves to top-level `turbopack`.
- **Sync Request API access is removed** — run `next-async-request-api` if the 15 compatibility period left any. `npx next typegen` generates `PageProps`/`LayoutProps`/`RouteContext` helpers.
- **`middleware` → `proxy`:** the `middleware` filename and export are deprecated for everyone; rename to `proxy.ts` / `export function proxy`. `proxy` runs on the Node.js runtime only — keep `middleware` if you need the edge runtime. Config flags follow (`skipMiddlewareUrlNormalize` → `skipProxyUrlNormalize`).
- Removed: AMP, `next lint` (and the `eslint` config key — lint with the tools from `/lint`), `serverRuntimeConfig`/`publicRuntimeConfig` (use env vars), `experimental.dynamicIO`/`useCache` (→ `cacheComponents`), `experimental.ppr`, `unstable_rootParams`, some `devIndicators` options.
- `revalidateTag(tag)` needs a second `cacheLife` argument; new `updateTag` and `refresh`.
- `next/image` defaults: local images with query strings need `images.localPatterns`; `minimumCacheTTL` 60 s → 4 h; `imageSizes` drops 16; `qualities` defaults to `[75]`; local-IP optimisation blocked; max 3 redirects; `images.domains` deprecated (use `remotePatterns`).
- Parallel route slots need an explicit `default.js`.
- `next dev` writes to `.next/dev`; `next build` no longer prints size / First Load JS (use Lighthouse or the built-in bundle analyzer from 16.1).

## Checklist per step

1. Read the guide for the target major; note every item that applies (grep for each removed API/config key).
2. Run `upgrade`, then the explicit codemods from the table.
3. `<pm> install` (keep the lockfile), type check, lint (`/lint` — not `next lint` on 16), tests, `next build`.
4. Smoke-test the main routes, route handlers, `proxy`/`middleware`, images and auth flows in a production build (`next start`), and compare upstream request volume where caching defaults changed.
5. Update Docker/pipeline Node versions if the floor moved (`../node/migration-overview.md` and your CI/CD runbook).

## Rollback

Before merge, abandon the branch. After merge, `git revert <merge-commit>` (manifest, lockfile and code move together). Deployed: your CI/CD runbook's production rollback.

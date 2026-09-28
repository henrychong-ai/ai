# Astro — Content Sites

When to choose Astro, and what differs from the rest of the stack when you do. Versions: `version-policy.md`. Lint and format: `/lint` (Oxlint + Biome, with residual `eslint-plugin-astro` for `.astro` files).

## When to use Astro

Astro renders HTML on the server or at build time and ships JavaScript only for the components you mark interactive ("islands").

| Choose Astro | Choose Next.js or a React SPA |
|--------------|-------------------------------|
| Marketing sites, documentation, blogs, landing pages | Applications where most of the screen is interactive |
| SEO and first-load speed matter most | Pervasive shared client state, real-time collaboration |
| A few interactive widgets on otherwise static pages | Offline-first or app-like navigation everywhere |
| Content from Markdown/MDX or a headless CMS | The UI behaves like a continuously running program |

When in doubt: if the page is mostly content with occasional interactivity, use Astro and add React islands where needed.

## Current Astro (7.x) — what changed from older examples

Much Astro example code online predates the Content Layer. Current rules (Astro 6 removed the legacy APIs; Astro 7 moved to Vite 8 and a Rust compiler):

| Old | Current |
|-----|---------|
| `src/content/config.ts`, `type: 'content'` | `src/content.config.ts` with a **loader** (`glob()`, `file()` or a custom loader) |
| `import { z } from 'astro:content'` | `import { z } from 'astro/zod'` (Zod 4: `z.email()`, `z.url()`) |
| `entry.slug`, `entry.render()` | `entry.id`, `render(entry)` from `astro:content` |
| `output: 'hybrid'` | Removed: pages are static by default; opt a page into on-demand rendering with `export const prerender = false` |
| `Astro.locals.runtime.env` (Cloudflare) | `import { env } from 'cloudflare:workers'` |
| Cloudflare Pages deployment | Cloudflare **Workers** with static assets (the adapter's default) |
| `<ViewTransitions />` | `<ClientRouter />` |
| `Astro.glob()` | `import.meta.glob()` |
| Lenient HTML | The compiler rejects unclosed non-void tags and invalid nesting |

Astro 6+ needs Node 22.12 or later; use the runtime from `version-policy.md`.

## Content collections

```typescript
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const articles = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishedDate: z.coerce.date(),
    tags: z.array(z.string()).default([]),
  }),
});

const events = defineCollection({
  // A custom loader for a headless CMS: return an array of objects with an `id`
  loader: async () => {
    const response = await fetch(`${import.meta.env.CMS_API_URL}/api/events?sort=-date`);
    if (!response.ok) throw new Error(`CMS returned ${response.status}`);
    const { docs } = (await response.json()) as { docs: Array<{ slug: string } & Record<string, unknown>> };
    return docs.map((doc) => ({ ...doc, id: doc.slug }));
  },
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    eventType: z.enum(['conference', 'meetup', 'workshop']),
  }),
});

export const collections = { articles, events };
```

A failing CMS fetch should fail the build loudly, not publish an empty site.

```astro
---
// src/pages/articles/[...id].astro
import { getCollection, render } from 'astro:content';

export async function getStaticPaths() {
  const articles = await getCollection('articles');
  return articles.map((article) => ({ params: { id: article.id }, props: { article } }));
}

const { article } = Astro.props;
const { Content } = await render(article);
---

<article>
  <h1>{article.data.title}</h1>
  <Content />
</article>
```

## Islands and server islands

```astro
---
import SearchWidget from '../components/SearchWidget.tsx';
import RegistrationStatus from '../components/RegistrationStatus.astro';
---

<SearchWidget client:visible />            <!-- hydrates only when scrolled into view -->

<RegistrationStatus eventId={event.id} server:defer>
  <p slot="fallback">Checking availability…</p>  <!-- static shell; the island renders on request -->
</RegistrationStatus>
```

## Cloudflare Workers

```javascript
// astro.config.mjs
import cloudflare from '@astrojs/cloudflare';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://example.com',
  adapter: cloudflare(),
  integrations: [sitemap()],
});
```

```astro
---
// src/pages/dashboard.astro — rendered on request
export const prerender = false;
import { env } from 'cloudflare:workers';

const row = await env.DB.prepare('SELECT COUNT(*) AS total FROM registrations').first<{ total: number }>();
---
<p>Total registrations: {row?.total ?? 0}</p>
```

- Secrets go in with `wrangler secret put`, never in `vars` and never with a hard-coded fallback: read them from `env` and fail if they are missing.
- TypeScript-on-Workers details (generated `Env`, `nodejs_compat`, testing): `cloudflare.md`.
- A headless CMS such as Payload (optionally on Workers with D1 + R2 via OpenNext) runs as a separate app.

## TypeScript, lint and checks

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "noUncheckedIndexedAccess": true,
    "paths": { "@/*": ["./src/*"] }
  }
}
```

No `baseUrl` (see `../coding-standards/tooling.md`).

```json
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "typecheck": "astro check",
    "lint": "oxlint --max-warnings=0 && eslint . --max-warnings=0",
    "format:check": "biome check .",
    "test": "vitest run",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck && pnpm test"
  }
}
```

Oxlint does not parse `.astro` files, so `/lint` adds residual ESLint with `eslint-plugin-astro` and `typescript-eslint` for them; take the exact config from `/lint`. `astro check` type-checks `.astro` files as well as `.ts`.

Unit tests use Vitest with Astro's Vite config (`getViteConfig` from `astro/config`); end-to-end tests use Playwright against `astro preview`.

## SEO essentials

- Set `site` in `astro.config.mjs`; build canonical URLs with `new URL(Astro.url.pathname, Astro.site)`.
- One layout component owns `<title>`, description, canonical, Open Graph and JSON-LD.
- `@astrojs/sitemap` for the sitemap; `<ClientRouter />` only where page transitions add value.

# Astro Content Site Ironclad Stack

A production-ready stack for content-driven websites using Astro 5, deployed entirely on Cloudflare's platform. Optionally integrates Payload CMS running on Cloudflare Workers.

**Core Principle:** *Content-first, JavaScript-when-necessary, edge-deployed.*

**Prerequisite:** Read `when-to-use-astro.md` to confirm Astro is the right choice for your project.

---

## Table of Contents

1. [Stack Overview](#stack-overview)
2. [Architecture Options](#architecture-options)
3. [Technology Versions](#technology-versions)
4. [Project Structure](#project-structure)
5. [Astro 5 Configuration](#astro-5-configuration)
6. [Data Fetching Patterns](#data-fetching-patterns)
7. [Payload CMS on Cloudflare](#payload-cms-on-cloudflare)
8. [Styling with Tailwind 4](#styling-with-tailwind-4)
9. [Linting & Formatting](#linting--formatting)
10. [Testing](#testing)
11. [Deployment Pipeline](#deployment-pipeline)
12. [SEO & Performance](#seo--performance)
13. [Quick Start](#quick-start)
14. [Decision Matrix](#decision-matrix)

---

## Stack Overview

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Framework** | Astro | 5.x | Content-first SSG/SSR |
| **Adapter** | @astrojs/cloudflare | 12.x | Edge deployment |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS |
| **Runtime** | Node.js | 24.13+ | Active LTS (new projects) |
| **Validation** | Zod | 3.24+ | Runtime validation + type inference |
| **TypeScript** | TypeScript | 5.7+ | Type safety |
| **Build** | Vite | 6.x | Bundled with Astro 5 |
| **Testing** | Vitest | ~3.2.x | Unit tests (pinned for Workers) |
| **E2E** | Playwright | 1.50+ | End-to-end testing |
| **Linting** | ESLint + 7 plugins | 9.x | Flat config + Astro parser |
| **Formatting** | Prettier | 3.x | Code formatting + Astro plugin |
| **Pre-commit** | Husky + lint-staged | 9.x / 16.x | Enforce standards |

**Optional CMS Layer:**

| Component | Technology | Purpose |
|-----------|------------|---------|
| CMS | Payload 3.x | Headless content management |
| CMS Hosting | Cloudflare Workers | Edge-deployed CMS |
| Database | D1 | SQLite at edge |
| Media | R2 | Object storage |

---

## Architecture Options

### Option A: Astro Only (No CMS)

Best for: Developer-managed content, technical teams, git-based workflows.

```
┌─────────────────────────────────────────┐
│           Cloudflare Pages              │
│  ┌───────────────────────────────────┐  │
│  │         Astro 5 (SSG)             │  │
│  │  Content Collections (MD/MDX)     │  │
│  │  Static HTML + Selective Islands  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Pros:** Simplest, fastest builds, git-based version control
**Cons:** Non-technical editors need git knowledge

### Option B: Astro + Payload (Decoupled)

Best for: Non-technical editors, media-heavy sites, complex content models.

```
┌─────────────────────────────────────────────────────────────┐
│                      Cloudflare                              │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   Cloudflare Pages  │    │    Cloudflare Workers       │ │
│  │  ┌───────────────┐  │    │  ┌───────────────────────┐  │ │
│  │  │  Astro 5      │  │◄───│  │    Payload CMS        │  │ │
│  │  │  (SSG/Hybrid) │  │API │  │    (Admin + API)      │  │ │
│  │  └───────────────┘  │    │  └───────────┬───────────┘  │ │
│  └─────────────────────┘    │              │              │ │
│                             │  ┌───────────┴───────────┐  │ │
│                             │  │   D1        R2        │  │ │
│                             │  │ (Database) (Media)    │  │ │
│                             │  └───────────────────────┘  │ │
│                             └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Pros:** Full CMS experience, admin UI, media management
**Cons:** More complex, requires webhook for rebuilds

### Option C: Payload + Next.js (Monolithic)

Best for: Real-time content needs, single-stack preference.

```
┌─────────────────────────────────────────┐
│        Cloudflare Workers               │
│  ┌───────────────────────────────────┐  │
│  │   Payload + Next.js (OpenNext)    │  │
│  │   Admin + Public Site + API       │  │
│  └───────────────────┬───────────────┘  │
│                      │                  │
│  ┌───────────────────┴───────────────┐  │
│  │       D1            R2            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Pros:** Single deployment, no rebuild needed for content changes
**Cons:** Heavier runtime, Next.js instead of Astro

---

## Technology Versions

### Core Dependencies (2026-01-22)

```json
{
  "dependencies": {
    "astro": "^5.0.0",
    "@astrojs/cloudflare": "^12.0.0",
    "@astrojs/sitemap": "^4.0.0",
    "tailwindcss": "^4.0.0",
    "zod": "^3.24.0"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "@types/node": "^24",

    "vitest": "~3.2.0",
    "@vitest/coverage-v8": "~3.2.0",
    "@cloudflare/vitest-pool-workers": "^0.7.5",
    "@playwright/test": "^1.50.0",

    "eslint": "^9.0.0",
    "typescript-eslint": "^8.0.0",
    "@typescript-eslint/eslint-plugin": "^8.0.0",
    "@typescript-eslint/parser": "^8.0.0",
    "@stylistic/eslint-plugin": "^2.0.0",
    "eslint-plugin-import": "^2.31.0",
    "eslint-plugin-unicorn": "^56.0.0",
    "eslint-plugin-sonarjs": "^2.0.0",
    "eslint-plugin-promise": "^7.0.0",
    "eslint-plugin-astro": "^1.0.0",
    "eslint-plugin-compat": "^6.0.0",
    "eslint-config-prettier": "^9.0.0",

    "prettier": "^3.0.0",
    "prettier-plugin-astro": "^0.14.0",

    "husky": "^9.0.0",
    "lint-staged": "^16.0.0",
    "wrangler": "^3.0.0"
  },
  "packageManager": "pnpm@10.0.0",
  "engines": {
    "node": ">=24.13.0"
  }
}
```

### Payload CMS Dependencies (if using)

```json
{
  "dependencies": {
    "payload": "^3.0.0",
    "@payloadcms/db-d1-sqlite": "^3.0.0",
    "@payloadcms/storage-r2": "^3.0.0",
    "@payloadcms/richtext-lexical": "^3.0.0",
    "@opennextjs/cloudflare": "^1.0.0",
    "next": "^15.0.0"
  }
}
```

### Version Notes

- **Node 24.13.0+**: Target version for new projects (Active LTS with security patches)
- **Vitest ~3.2.x**: Pinned for `@cloudflare/vitest-pool-workers` compatibility (Vitest 4.x not supported)
- **Tailwind 4.x**: CSS-first configuration, no `tailwind.config.js` needed
- **ESLint 9.x**: Flat config required (no legacy .eslintrc)
- **ESLint Plugins**: 7 core plugins + Astro-specific + compat (see Linting section)
- **Zod 3.24.x**: Explicit dependency for custom validation outside Content Collections

---

## Project Structure

### Option A: Astro Only

```
my-site/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.astro
│   │   │   ├── Footer.astro
│   │   │   └── Navigation.astro
│   │   ├── ui/
│   │   │   ├── Button.astro
│   │   │   └── Card.astro
│   │   └── SEO.astro
│   ├── content/
│   │   ├── config.ts              # Content Collections config
│   │   ├── articles/
│   │   │   └── my-article.md
│   │   └── events/
│   │       └── 2026-conference.md
│   ├── layouts/
│   │   ├── BaseLayout.astro
│   │   └── ArticleLayout.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── articles/
│   │   │   ├── index.astro
│   │   │   └── [...slug].astro
│   │   └── events/
│   │       └── index.astro
│   └── styles/
│       └── global.css             # Tailwind 4 CSS
├── public/
│   ├── fonts/
│   └── favicon.ico
├── astro.config.mjs
├── tsconfig.json
└── package.json
```

### Option B: Astro + Payload (Monorepo)

```
my-project/
├── apps/
│   ├── astro/                     # Astro frontend
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── content/
│   │   │   │   └── config.ts      # Payload API loader
│   │   │   ├── layouts/
│   │   │   ├── lib/
│   │   │   │   └── payload.ts     # API client
│   │   │   └── pages/
│   │   ├── astro.config.mjs
│   │   └── package.json
│   │
│   └── payload/                   # Payload CMS
│       ├── src/
│       │   ├── collections/
│       │   │   ├── Articles.ts
│       │   │   ├── Events.ts
│       │   │   └── Media.ts
│       │   ├── globals/
│       │   │   └── SiteSettings.ts
│       │   ├── hooks/
│       │   │   └── revalidate.ts  # Webhook trigger
│       │   └── payload.config.ts
│       ├── wrangler.toml
│       └── package.json
│
├── packages/
│   └── shared/                    # Shared types
│       ├── src/types.ts
│       └── package.json
│
├── .github/workflows/
│   ├── deploy-astro.yml
│   └── deploy-payload.yml
├── pnpm-workspace.yaml
└── package.json
```

**pnpm-workspace.yaml:**
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

---

## Astro 5 Configuration

### astro.config.mjs

```javascript
import { defineConfig, envField } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',
  output: 'hybrid',  // SSG by default, SSR opt-in per page

  adapter: cloudflare({
    imageService: 'cloudflare',  // Use Cloudflare Images
    platformProxy: {
      enabled: true,  // Enable local D1/R2/KV bindings in dev
    },
  }),

  integrations: [sitemap()],

  // Type-safe environment variables (Astro 5 feature)
  env: {
    schema: {
      PAYLOAD_API_URL: envField.string({
        context: 'server',
        access: 'secret',
        optional: true,
      }),
      SITE_URL: envField.string({
        context: 'client',
        access: 'public',
        default: 'https://example.com',
      }),
    },
  },

  // Vite configuration
  vite: {
    build: {
      sourcemap: true,
    },
  },
});
```

### tsconfig.json

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@layouts/*": ["src/layouts/*"]
    },
    "noUncheckedIndexedAccess": true
  },
  "include": ["src/**/*", "env.d.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### env.d.ts

```typescript
/// <reference types="astro/client" />

// Type augmentation for Cloudflare bindings
type Runtime = import('@astrojs/cloudflare').Runtime<Env>;

interface Env {
  DB?: D1Database;
  MEDIA?: R2Bucket;
  CACHE?: KVNamespace;
}

declare namespace App {
  interface Locals extends Runtime {}
}

// Astro 5 environment variables
declare module 'astro:env/server' {
  export const PAYLOAD_API_URL: string | undefined;
}

declare module 'astro:env/client' {
  export const SITE_URL: string;
}
```

---

## Data Fetching Patterns

### Pattern 1: Content Collections (Static Markdown)

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content';

const articles = defineCollection({
  type: 'content',  // Markdown/MDX files
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishedDate: z.coerce.date(),
    author: z.string(),
    tags: z.array(z.string()).optional(),
  }),
});

export const collections = { articles };
```

```astro
---
// src/pages/articles/[...slug].astro
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  const articles = await getCollection('articles');
  return articles.map(article => ({
    params: { slug: article.slug },
    props: { article },
  }));
}

const { article } = Astro.props;
const { Content } = await article.render();
---

<article>
  <h1>{article.data.title}</h1>
  <Content />
</article>
```

### Pattern 2: Content Collections with External Loader (Payload CMS)

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content';

const events = defineCollection({
  loader: async () => {
    const apiUrl = import.meta.env.PAYLOAD_API_URL;
    if (!apiUrl) return [];

    const response = await fetch(`${apiUrl}/api/events?depth=2&sort=-date`);
    if (!response.ok) {
      console.error('Failed to fetch events:', response.status);
      return [];
    }

    const { docs } = await response.json();
    return docs.map((doc: any) => ({
      id: doc.slug,
      ...doc,
    }));
  },
  schema: z.object({
    id: z.string(),
    title: z.string(),
    slug: z.string(),
    date: z.coerce.date(),
    eventType: z.enum(['annual-conference', 'catch-up-meeting', 'updating-session']),
    description: z.any().optional(),  // Rich text
    featured: z.boolean().optional(),
    speakers: z.array(z.any()).optional(),
  }),
});

export const collections = { events };
```

### Pattern 3: Server Islands (Dynamic Components in Static Pages)

```astro
---
// src/pages/event/[slug].astro
import { getCollection } from 'astro:content';
import BaseLayout from '@layouts/BaseLayout.astro';
import RegistrationStatus from '@components/RegistrationStatus';

export async function getStaticPaths() {
  const events = await getCollection('events');
  return events.map(event => ({
    params: { slug: event.data.slug },
    props: { event },
  }));
}

const { event } = Astro.props;
---

<BaseLayout title={event.data.title}>
  <!-- Static content -->
  <h1>{event.data.title}</h1>
  <time>{event.data.date.toLocaleDateString()}</time>

  <!-- Dynamic island - fetches registration status at runtime -->
  <RegistrationStatus
    eventId={event.data.id}
    server:defer
  >
    <p slot="fallback">Checking availability...</p>
  </RegistrationStatus>
</BaseLayout>
```

### Pattern 4: Full SSR Page

```astro
---
// src/pages/dashboard.astro
export const prerender = false;  // Force SSR

const { locals } = Astro;
const db = locals.runtime.env.DB;

// Query D1 at runtime
const stats = await db.prepare('SELECT COUNT(*) as total FROM registrations').first();
---

<h1>Dashboard</h1>
<p>Total registrations: {stats?.total ?? 0}</p>
```

---

## Payload CMS on Cloudflare

### Overview

As of November 2025, Payload CMS runs natively on Cloudflare Workers using:
- `@payloadcms/db-d1-sqlite` - D1 database adapter
- `@payloadcms/storage-r2` - R2 storage adapter
- `@opennextjs/cloudflare` - OpenNext adapter

**Requirement:** Workers Paid plan (size limits on free tier)

### payload.config.ts

```typescript
import { buildConfig } from 'payload';
import { d1Adapter } from '@payloadcms/db-d1-sqlite';
import { r2Storage } from '@payloadcms/storage-r2';
import { lexicalEditor } from '@payloadcms/richtext-lexical';

import { Articles } from './collections/Articles';
import { Events } from './collections/Events';
import { Media } from './collections/Media';
import { SiteSettings } from './globals/SiteSettings';

export default buildConfig({
  admin: {
    user: 'users',
  },
  collections: [Articles, Events, Media],
  globals: [SiteSettings],
  editor: lexicalEditor(),
  db: d1Adapter({
    client: ({ env }) => env.DB,
    migrationDir: './drizzle',
  }),
  plugins: [
    r2Storage({
      collections: {
        media: true,
      },
      bucket: ({ env }) => env.MEDIA,
    }),
  ],
  secret: process.env.PAYLOAD_SECRET || 'your-secret-key',
});
```

### wrangler.toml (Payload)

```toml
name = "my-site-cms"
main = ".open-next/worker.js"
compatibility_date = "2024-12-01"
compatibility_flags = ["nodejs_compat"]

[[d1_databases]]
binding = "DB"
database_name = "my-site-db"
database_id = "your-database-id"

[[r2_buckets]]
binding = "MEDIA"
bucket_name = "my-site-media"

[vars]
PAYLOAD_SECRET = "generate-a-secret"

# Secrets (set via wrangler secret put)
# GITHUB_TOKEN - for webhook rebuilds
```

### Webhook for Astro Rebuild

```typescript
// src/hooks/revalidate.ts
import type { CollectionAfterChangeHook, CollectionAfterDeleteHook } from 'payload';

const triggerRebuild = async () => {
  const githubToken = process.env.GITHUB_TOKEN;
  if (!githubToken) return;

  await fetch('https://api.github.com/repos/OWNER/REPO/dispatches', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${githubToken}`,
      Accept: 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      event_type: 'payload-content-updated',
    }),
  });
};

export const afterChange: CollectionAfterChangeHook = async ({ doc }) => {
  await triggerRebuild();
  return doc;
};

export const afterDelete: CollectionAfterDeleteHook = async ({ doc }) => {
  await triggerRebuild();
  return doc;
};
```

---

## Styling with Tailwind 4

Tailwind 4 uses CSS-first configuration. No `tailwind.config.js` required.

### src/styles/global.css

```css
@import 'tailwindcss';

/* Theme customization */
@theme {
  /* Colors */
  --color-primary: #002147;
  --color-primary-light: #0f4c81;
  --color-accent: #8b0000;

  /* Typography */
  --font-sans: 'Open Sans', system-ui, sans-serif;
  --font-heading: 'Georgia', serif;

  /* Spacing scale extension */
  --spacing-18: 4.5rem;
  --spacing-88: 22rem;
}

/* Custom utilities */
@utility container-prose {
  max-width: 65ch;
  margin-inline: auto;
  padding-inline: 1rem;
}

@utility text-balance {
  text-wrap: balance;
}

/* Component styles */
@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2
           rounded-md font-medium transition-colors
           focus:outline-none focus:ring-2 focus:ring-offset-2;
  }

  .btn-primary {
    @apply btn bg-primary text-white hover:bg-primary-light
           focus:ring-primary;
  }
}
```

### Import in Layout

```astro
---
// src/layouts/BaseLayout.astro
import '@/styles/global.css';
---

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width" />
    <slot name="head" />
  </head>
  <body class="min-h-screen bg-white text-gray-900">
    <slot />
  </body>
</html>
```

---

## Linting & Formatting

### ESLint Configuration

Astro requires special ESLint handling due to its unique file format. Key considerations:
- Use `project: true` (NOT `projectService`) for .astro files
- Disable strict TypeScript rules for .astro files (limited type inference)
- Include browser compatibility checking with `eslint-plugin-compat`

### eslint.config.mjs

```javascript
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import stylistic from '@stylistic/eslint-plugin';
import importPlugin from 'eslint-plugin-import';
import unicorn from 'eslint-plugin-unicorn';
import sonarjs from 'eslint-plugin-sonarjs';
import promise from 'eslint-plugin-promise';
import astro from 'eslint-plugin-astro';
import compat from 'eslint-plugin-compat';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  // Global ignores
  { ignores: ['node_modules/**', 'dist/**', '.astro/**', 'coverage/**'] },

  // Base configs
  eslint.configs.recommended,

  // TypeScript (strict) - for .ts/.tsx files ONLY
  {
    files: ['**/*.ts', '**/*.tsx'],
    extends: [
      ...tseslint.configs.strictTypeChecked,
      ...tseslint.configs.stylisticTypeChecked,
    ],
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },

  // Astro files - relaxed TypeScript rules
  {
    files: ['**/*.astro'],
    extends: [...astro.configs.recommended],
    languageOptions: {
      parserOptions: {
        project: true,  // Use project: true, NOT projectService for Astro
        extraFileExtensions: ['.astro'],
      },
    },
    rules: {
      // Disable strict rules that don't work well with Astro's type inference
      '@typescript-eslint/no-unsafe-assignment': 'off',
      '@typescript-eslint/no-unsafe-member-access': 'off',
      '@typescript-eslint/no-unsafe-call': 'off',
      '@typescript-eslint/no-unsafe-return': 'off',
    },
  },

  // Core plugins for all files
  stylistic.configs.recommended,
  importPlugin.flatConfigs.recommended,
  sonarjs.configs.recommended,
  promise.configs['flat/recommended'],

  // Unicorn - modern JS best practices
  {
    ...unicorn.configs['flat/recommended'],
    rules: {
      ...unicorn.configs['flat/recommended'].rules,
      'unicorn/filename-case': 'off',  // Allow PascalCase for components
      'unicorn/prevent-abbreviations': 'off',  // Allow common abbreviations
    },
  },

  // Browser compatibility
  {
    ...compat.configs['flat/recommended'],
    settings: {
      browsers: ['defaults', 'not dead', 'not IE 11'],
    },
  },

  // Prettier must be last (disables conflicting rules)
  prettier,
);
```

### .prettierrc

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "plugins": ["prettier-plugin-astro"],
  "overrides": [
    {
      "files": "*.astro",
      "options": {
        "parser": "astro"
      }
    }
  ]
}
```

### Pre-commit Hooks (Husky + lint-staged)

**Setup:**
```bash
pnpm add -D husky lint-staged
pnpm exec husky init
echo "npx lint-staged" > .husky/pre-commit
```

**lint-staged config (package.json):**
```json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.astro": ["eslint --fix --max-warnings=0", "prettier --write"],
    "*.{css,scss}": ["prettier --write"],
    "*.{json,md,yml,yaml}": ["prettier --write"]
  }
}
```

### Package.json Scripts (Lint)

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings=0",
    "lint:fix": "eslint . --fix --max-warnings=0",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "typecheck": "astro check && tsc --noEmit",
    "check": "pnpm lint && pnpm format:check && pnpm typecheck"
  }
}
```

**Note:** Use `astro check` for Astro file type checking in addition to `tsc --noEmit` for TypeScript files.

---

## Testing

### Package.json Scripts (Test)

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

### Test File Conventions

| Location | Purpose |
|----------|---------|
| `src/**/*.test.ts` | Co-located unit tests (preferred) |
| `src/**/__tests__/` | Test directory for complex modules |
| `e2e/` | Playwright E2E tests |

### vitest.config.ts (Standard Astro)

For standard Astro projects without Workers-specific testing:

```typescript
import { getViteConfig } from 'astro/config';

export default getViteConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['node_modules', 'dist', 'e2e', '.astro'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/**/*.d.ts'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

### vitest.config.ts (Workers with D1/R2)

For testing code that uses Cloudflare Workers bindings (D1, R2, KV):

```typescript
import { defineWorkersConfig } from '@cloudflare/vitest-pool-workers/config';

export default defineWorkersConfig({
  test: {
    globals: true,
    include: ['src/**/*.test.ts'],
    exclude: ['node_modules', 'dist', 'e2e', '.astro'],
    poolOptions: {
      workers: {
        wrangler: { configPath: './wrangler.toml' },
        miniflare: {
          d1Databases: ['DB'],
          r2Buckets: ['MEDIA'],
        },
      },
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

**Note:** `@cloudflare/vitest-pool-workers` requires Vitest ~3.2.x (pinned version). Vitest 4.x is NOT compatible.

### Example Unit Test

```typescript
// src/lib/utils.test.ts
import { describe, it, expect } from 'vitest';
import { formatDate, slugify } from './utils';

describe('formatDate', () => {
  it('formats date correctly', () => {
    const date = new Date('2026-01-22');
    expect(formatDate(date)).toBe('22 January 2026');
  });

  it('handles invalid dates', () => {
    expect(formatDate(new Date('invalid'))).toBe('Invalid Date');
  });
});

describe('slugify', () => {
  it('converts string to slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
    expect(slugify('Test & Example')).toBe('test-example');
  });

  it('handles empty strings', () => {
    expect(slugify('')).toBe('');
  });
});
```

### Example Workers Test (D1)

```typescript
// src/lib/db.test.ts
import { describe, it, expect } from 'vitest';
import { env } from 'cloudflare:test';

describe('D1 Database', () => {
  it('queries data correctly', async () => {
    const db = env.DB;

    // Insert test data
    await db.exec('INSERT INTO users (id, name) VALUES (1, "Test User")');

    // Query and verify
    const result = await db.prepare('SELECT * FROM users WHERE id = ?').bind(1).first();
    expect(result?.name).toBe('Test User');
  });
});
```

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],
  use: {
    baseURL: 'http://localhost:4321',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'pnpm preview',
    url: 'http://localhost:4321',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

### Example E2E Test

```typescript
// e2e/navigation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('homepage loads correctly', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/My Site/);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('navigates to articles', async ({ page }) => {
    await page.goto('/');
    await page.click('a[href="/articles"]');
    await expect(page).toHaveURL('/articles');
  });
});
```

### Coverage Thresholds

All projects must meet 80% coverage minimums:

| Metric | Threshold |
|--------|-----------|
| Lines | 80% |
| Functions | 80% |
| Branches | 80% |
| Statements | 80% |

Coverage is enforced in CI - builds fail below threshold.

---

## Deployment Pipeline

### GitHub Actions: Astro

```yaml
# .github/workflows/deploy-astro.yml
name: Deploy Astro

on:
  push:
    branches: [main]
    paths:
      - 'apps/astro/**'
      - 'packages/**'
  repository_dispatch:
    types: [payload-content-updated]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 10
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter astro test:run
      - run: pnpm --filter astro build
        env:
          PAYLOAD_API_URL: ${{ secrets.PAYLOAD_API_URL }}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 10
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter astro build
        env:
          PAYLOAD_API_URL: ${{ secrets.PAYLOAD_API_URL }}
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          command: pages deploy apps/astro/dist --project-name=my-site
```

### GitHub Actions: Payload

```yaml
# .github/workflows/deploy-payload.yml
name: Deploy Payload CMS

on:
  push:
    branches: [main]
    paths:
      - 'apps/payload/**'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 10
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter payload build
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          workingDirectory: apps/payload
          command: deploy
```

---

## SEO & Performance

### SEO Component

```astro
---
// src/components/SEO.astro
interface Props {
  title: string;
  description?: string;
  image?: string;
  article?: boolean;
  publishedTime?: Date;
}

const {
  title,
  description = 'Default site description',
  image = '/og-default.jpg',
  article = false,
  publishedTime,
} = Astro.props;

const canonicalURL = new URL(Astro.url.pathname, Astro.site);
const imageURL = new URL(image, Astro.site);
---

<title>{title}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonicalURL} />

<!-- Open Graph -->
<meta property="og:type" content={article ? 'article' : 'website'} />
<meta property="og:url" content={canonicalURL} />
<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:image" content={imageURL} />
{publishedTime && (
  <meta property="article:published_time" content={publishedTime.toISOString()} />
)}

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content={title} />
<meta name="twitter:description" content={description} />
<meta name="twitter:image" content={imageURL} />

<!-- Structured Data -->
<script type="application/ld+json" set:html={JSON.stringify({
  '@context': 'https://schema.org',
  '@type': article ? 'Article' : 'WebPage',
  name: title,
  description,
  url: canonicalURL.href,
  ...(publishedTime && { datePublished: publishedTime.toISOString() }),
})} />
```

### Performance Checklist

- [ ] Use `hybrid` output mode (SSG by default)
- [ ] Enable Cloudflare image optimization
- [ ] Preconnect to external resources
- [ ] Use View Transitions for navigation
- [ ] Implement critical CSS inlining
- [ ] Enable Cloudflare Web Analytics

### Cloudflare Web Analytics

```astro
---
// In BaseLayout.astro
---
{import.meta.env.PROD && (
  <script
    defer
    src="https://static.cloudflareinsights.com/beacon.min.js"
    data-cf-beacon='{"token": "your-token"}'
  />
)}
```

---

## Quick Start

### Astro Only

```bash
# Create project
pnpm create astro@latest my-site -- --template minimal
cd my-site

# Add core dependencies
pnpm add @astrojs/cloudflare @astrojs/sitemap zod
pnpm add -D tailwindcss wrangler

# Add testing
pnpm add -D vitest@~3.2.0 @vitest/coverage-v8@~3.2.0 @playwright/test

# Add linting (core plugins)
pnpm add -D eslint typescript-eslint \
  @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  @stylistic/eslint-plugin eslint-plugin-import \
  eslint-plugin-unicorn eslint-plugin-sonarjs eslint-plugin-promise \
  eslint-config-prettier

# Add linting (Astro-specific)
pnpm add -D eslint-plugin-astro eslint-plugin-compat \
  prettier prettier-plugin-astro

# Add pre-commit hooks
pnpm add -D husky lint-staged

# Setup version pinning (Node 24 LTS)
echo "24.13.0" > .nvmrc

# Setup pre-commit hooks
pnpm exec husky init
echo "npx lint-staged" > .husky/pre-commit

# Create lint-staged config (add to package.json)
# See "Linting & Formatting" section for configuration

# Develop
pnpm dev

# Run checks
pnpm lint        # Lint check
pnpm typecheck   # Type check (astro check && tsc --noEmit)
pnpm test        # Run tests
pnpm check       # All checks

# Deploy
pnpm build
wrangler pages deploy dist --project-name=my-site
```

### Astro + Payload (One-Click)

1. Visit [Payload Cloudflare Template](https://payloadcms.com/templates/cloudflare)
2. Click "Deploy to Cloudflare"
3. Configure D1 database and R2 bucket names
4. Deploy
5. Create Astro frontend connecting to Payload API

---

## Decision Matrix

| Scenario | Architecture | Why |
|----------|--------------|-----|
| Marketing site, devs manage content | Astro only | Simplest, fastest, git-based |
| Blog, technical editors | Astro + Content Collections | Type-safe markdown, easy to add |
| Business site, non-technical editors | Astro + Payload | Full CMS, admin UI, media management |
| Frequently updated content | Payload + Next.js | No rebuild needed, real-time |
| E-commerce, complex models | Payload + custom frontend | Maximum flexibility |

---

## Related Documents

- `when-to-use-astro.md` - Decision framework for Astro
- `cloudflare.md` - Cloudflare Workers/D1/R2 reference
- `typescript-ironclad-stack.md` - Core TypeScript stack

---

## Sources

- [Payload on Workers - Cloudflare Blog](https://blog.cloudflare.com/payload-cms-workers/)
- [Deploy Payload to Cloudflare](https://payloadcms.com/posts/blog/deploy-payload-onto-cloudflare-in-a-single-click)
- [Astro 5 Documentation](https://docs.astro.build)
- [Tailwind CSS 4 Documentation](https://tailwindcss.com/docs)

---

*Companion to: typescript-ironclad-stack.md, cloudflare.md, /lint skill*
*Last updated: 2026-01-22 (added comprehensive lint & test specifications)*

# When to Use Astro

> Source: [justfuckinguseastro.com](https://justfuckinguseastro.com)

## Core Philosophy

Astro operates on an **"HTML-first, JavaScript-when-necessary"** principle.

**"Your page is static by default. Interactivity is the exception."**

Interactive components should be isolated rather than hydrating entire pages.

## Use Astro When

Your project involves:

- **Content-driven sites** with selective interactivity
- **SEO-critical websites** where performance matters
- **Componentization** without single-page app penalties
- **Localized interactivity** (specific widgets, not whole pages)
- **Maintainability at scale**

### Ideal Project Types

- Marketing pages
- Documentation sites
- Blogs
- Landing pages
- Ecommerce frontends (server-rendered)

## Key Advantages

| Feature | Benefit |
|---------|---------|
| Zero client-side JS by default | Fast initial load, better Core Web Vitals |
| Component reusability | Without monolithic framework overhead |
| File-based routing | Predictable, simple navigation |
| Typed content collections | Prevents broken metadata |
| Islands Architecture | Declare interactive components, keep rest server-rendered |
| Framework flexibility | Use React, Vue, Svelte only where justified |

## Don't Use Astro When

Astro is **inappropriate** for:

- **Heavy client-side applications** with pervasive shared state
- **Real-time collaborative systems** (Google Docs, Figma-like)
- **Interfaces where nearly every element requires interactivity**
- **Complex offline-first applications**

### The Rule

> If your interface behaves like a **continuously running program**, use React, Next, SvelteKit, or Remix instead.

## The Central Argument

The core critique: developers ship full single-page applications for content-heavy sites, prioritizing convenience over user experience while degrading web quality.

**Astro is the pragmatic middle ground** between:
- Idealistic "pure HTML" approaches
- Over-engineered SPA defaults

## Decision Framework

```
Is your site primarily content with occasional interactivity?
├── YES → Use Astro
│   └── Add React/Vue/Svelte islands only where needed
└── NO → Is it a full application with constant state changes?
    ├── YES → Use Next.js, SvelteKit, or Remix
    └── MAYBE → Consider Astro with more islands
```

## Islands Architecture

The key differentiator: **declare specific interactive components** while keeping the remainder server-rendered and fast.

```astro
---
// Static by default
import Header from './Header.astro';
import Footer from './Footer.astro';
// Interactive only where needed
import SearchWidget from './SearchWidget.tsx';
---

<Header />
<main>
  <article><!-- Static content --></article>
  <SearchWidget client:visible />  <!-- Hydrates only when visible -->
</main>
<Footer />
```

## Bottom Line

**Just fucking use Astro** when you're building content sites. Stop shipping megabytes of JavaScript for what should be HTML with a few interactive widgets.

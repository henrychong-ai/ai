# Next.js Migration Guide

Version upgrade patterns for Next.js applications.

## Version Roadmap

| From → To | Difficulty | Key Changes |
|-----------|------------|-------------|
| 14 → 15 | Medium | Async Request APIs, React 19 |
| 15 → 16 | Medium | Turbopack default, middleware changes |

## Next.js 14 to 15 Migration

### Breaking: Async Request APIs

APIs that were synchronous in v14 are async in v15:

**Before (Next.js 14):**
```typescript
import { cookies, headers } from 'next/headers';

export default function Page() {
  const cookieStore = cookies();
  const headersList = headers();
  // ...
}
```

**After (Next.js 15):**
```typescript
import { cookies, headers } from 'next/headers';

export default async function Page() {
  const cookieStore = await cookies();
  const headersList = await headers();
  // ...
}
```

### Affected APIs

| API | Change |
|-----|--------|
| `cookies()` | Now async |
| `headers()` | Now async |
| `draftMode()` | Now async |
| `params` | Now Promise |
| `searchParams` | Now Promise |

### Migration Codemod

```bash
npx @next/codemod@canary upgrade latest
```

Or specific transform:
```bash
npx @next/codemod@canary next-async-request-api .
```

### React 19 Upgrade

Next.js 15 ships with React 19:

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }
}
```

**Key React 19 changes:**
- `useFormStatus` and `useFormState` hooks
- Document metadata API
- Improved hydration errors
- Server Components improvements

## Next.js 15 to 16 Migration

### Breaking: Turbopack Default

Turbopack is now the default bundler:

```bash
# To use webpack instead (if issues)
next dev --webpack
next build --webpack
```

### Breaking: Middleware Rename

`middleware.ts` → `proxy.ts` in some configurations:

**Check for:**
```
middleware.ts
middleware.js
```

**May need to rename to:**
```
proxy.ts
proxy.js
```

### Configuration Updates

**next.config.js changes:**
```javascript
// Before (v15)
module.exports = {
  experimental: {
    turbo: true
  }
}

// After (v16) - no longer experimental
module.exports = {
  // Turbopack is default
  // Use webpack: true to opt out
}
```

## App Router Considerations

### Layout Changes

Ensure layouts are properly typed:
```typescript
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

### Loading States

```typescript
// loading.tsx
export default function Loading() {
  return <div>Loading...</div>
}
```

### Error Handling

```typescript
// error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

## Common Migration Issues

### Issue: Hydration Mismatch

```
Error: Hydration failed because the initial UI does not match
```

**Causes:**
- Date/time rendering
- Browser-only APIs in initial render
- Random values

**Fix:**
```typescript
'use client'
import { useState, useEffect } from 'react'

function Component() {
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

  if (!mounted) return null
  // Browser-only content here
}
```

### Issue: Dynamic Import Changes

```typescript
// Before
const Component = dynamic(() => import('./Component'))

// After (with suspense)
const Component = dynamic(() => import('./Component'), {
  suspense: true,
})
```

### Issue: Image Component

```typescript
// Updated import
import Image from 'next/image'

// Check for deprecated props
<Image
  src="/image.png"
  alt="Description"
  width={500}
  height={300}
  // Remove deprecated: layout, objectFit, objectPosition
  style={{ objectFit: 'cover' }}
/>
```

## Testing Checklist

### Pre-Migration
- [ ] Document current Next.js version
- [ ] List all async API usage (cookies, headers, etc.)
- [ ] Check for middleware.ts
- [ ] Review next.config.js settings
- [ ] Document current React version

### Migration Steps
1. [ ] Update Next.js in package.json
2. [ ] Update React to v19 (if upgrading to Next 15+)
3. [ ] Run Next.js codemod
4. [ ] Update async API calls manually if needed
5. [ ] Check middleware configuration
6. [ ] Update next.config.js
7. [ ] Run build
8. [ ] Run tests
9. [ ] Visual regression check

### Post-Migration
- [ ] Build succeeds
- [ ] All pages render correctly
- [ ] API routes work
- [ ] Middleware functions
- [ ] No console errors
- [ ] Performance acceptable

## Performance Monitoring

After upgrade, verify:
- Build time (should improve with Turbopack)
- First Contentful Paint
- Largest Contentful Paint
- Time to Interactive

```bash
# Analyze bundle
ANALYZE=true next build
```

## Rollback Procedure

```bash
# Revert package.json
git checkout HEAD~1 -- package.json

# Reinstall
rm -rf node_modules .next
pnpm install

# Verify
pnpm dev
```

---

*Always test thoroughly before deploying Next.js upgrades to production.*

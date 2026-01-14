# Node.js Migration Overview

General principles and patterns for Node.js version upgrades.

## Release Schedule Understanding

Node.js follows a predictable release schedule:
- **Even-numbered versions** (18, 20, 22, 24) become LTS
- **LTS phases:** Active (18 months) → Maintenance (12 months) → EOL
- **Security patches:** Only provided during Active/Maintenance phases

## Current LTS Status (as of 2026-01)

| Version | Status | EOL Date |
|---------|--------|----------|
| v24.x | Current LTS | ~2028 |
| v22.x | Active LTS | ~2027 |
| v20.x | Maintenance | ~2026-04 |
| v18.x | EOL | 2025-04 |
| v16.x | EOL | 2023-09 |

## Migration Strategy

### 1. Version Leap Policy

**Recommended:** Skip one LTS version maximum.
- v20 → v22 → v24 (ideal incremental path)
- v20 → v24 (acceptable single leap)
- v16 → v24 (risky, many breaking changes)

### 2. Deprecation Warning Protocol

Before upgrading, run with deprecation warnings:
```bash
NODE_OPTIONS='--pending-deprecation' node app.js
```

Address all warnings BEFORE upgrading.

### 3. Native Module Considerations

Native modules (node-gyp) may require rebuild:
```bash
# Check for native dependencies
npm ls | grep -E "(node-gyp|native|binding)"

# Force rebuild
npm rebuild
```

## Common Breaking Changes Across Versions

### V8 Engine Updates
Each Node version ships newer V8, which may:
- Remove deprecated JavaScript features
- Change error message formats
- Alter performance characteristics

### OpenSSL Updates
Security library changes affect:
- TLS/SSL connections
- Cryptographic operations
- Certificate validation

### Module System Evolution
- CommonJS → ESM migration pressure
- Import assertions → Import attributes
- Package.json `exports` field strictness

## Testing Strategy

### Minimum Test Coverage for Upgrades

| Test Type | Required | Rationale |
|-----------|----------|-----------|
| Unit tests | Yes | Core logic verification |
| Integration tests | Yes | API contract validation |
| E2E tests | Recommended | User flow verification |
| Performance tests | For critical paths | Regression detection |

### Pre-Upgrade Baseline

```bash
# Capture baseline metrics
npm test -- --coverage > test-baseline.txt
npm run build 2>&1 > build-baseline.txt
node --version >> baseline.txt
```

### Post-Upgrade Comparison

```bash
# Compare results
diff test-baseline.txt test-current.txt
diff build-baseline.txt build-current.txt
```

## Dockerfile Best Practices

### Use Specific Versions
```dockerfile
# Good: Pinned version
FROM node:24.13.0-alpine

# Bad: Floating tag
FROM node:latest
FROM node:lts
```

### Multi-Stage Builds
```dockerfile
FROM node:24.13.0-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:24.13.0-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

## CI/CD Pipeline Updates

### GitHub Actions
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: '24.13.0'
```

### Bitbucket Pipelines
```yaml
image: node:24.13.0-alpine
pipelines:
  default:
    - step:
        script:
          - node --version
          - pnpm install
          - pnpm test
```

## Rollback Procedure

### Immediate Rollback
```bash
# Revert to previous branch
git checkout main

# Or reset to pre-upgrade commit
git reset --hard HEAD~1
```

### Docker Rollback
```bash
# Revert to previous image
docker tag myapp:previous myapp:latest
docker compose up -d
```

## Security Considerations

### CVE Monitoring
- Subscribe to: https://nodejs.org/en/blog/vulnerability/
- Monitor: https://github.com/nodejs/node/security/advisories

### Minimum Secure Versions (CVE-2025-59466)
- v24.13.0+ (async_hooks DoS fix)
- v22.22.0+ (async_hooks DoS fix)
- v20.20.0+ (async_hooks DoS fix)

---

*See version-specific guides for detailed migration steps.*

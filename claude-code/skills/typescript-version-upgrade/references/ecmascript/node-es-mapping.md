# Node.js to ECMAScript Target Mapping

Recommended TypeScript `target` and `lib` settings for each Node.js version.

**Source:** [TypeScript Wiki - Node Target Mapping](https://github.com/microsoft/TypeScript/wiki/Node-Target-Mapping)

---

## Node.js to ES Target Mapping Table

| Node.js | Target | Lib | Module | moduleResolution |
|---------|--------|-----|--------|------------------|
| **Node 24** | ES2024 | ES2024 | NodeNext | NodeNext |
| **Node 22** | ES2023 | ES2023 | NodeNext | NodeNext |
| **Node 20** | ES2023 | ES2023 | NodeNext | NodeNext |
| **Node 18** | ES2022 | ES2022 | Node16 | Node16 |
| **Node 16** | ES2021 | ES2021 | Node16 | Node16 |
| **Node 14** | ES2020 | ES2020 | Node16 | Node16 |
| **Node 12** | ES2019 | ES2019 | CommonJS | Node |
| **Node 10** | ES2018 | ES2018 | CommonJS | Node |
| **Node 8** | ES2017 | ES2017 | CommonJS | Node |

---

## Recommended Configuration

### Default (ES2022 - Maximum Compatibility)

**Use for all projects unless newer features are specifically required.**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

**Rationale:**
- Supported by Node 18+ (current LTS and newer)
- Excellent browser support (Chrome 94+, Firefox 93+, Safari 15+)
- Includes most commonly needed features (top-level await, private fields, .at())
- TypeScript 5.0+ supports ES2022 fully

### Modern (ES2024 - Latest Features)

**Use when Node 22+ is guaranteed and legacy support is not required.**

```json
{
  "compilerOptions": {
    "target": "ES2024",
    "lib": ["ES2024"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

**Rationale:**
- Requires Node 22+ or 24+
- Requires TypeScript 5.6+
- Includes Object.groupBy, Promise.withResolvers
- Smallest bundle output (no downleveling)

---

## TypeScript Version Requirements

| ES Target | Minimum TypeScript |
|-----------|-------------------|
| ES5-ES2022 | TypeScript 4.x+ |
| ES2023 | TypeScript 5.5+ |
| ES2024 | TypeScript 5.6+ |
| ESNext | TypeScript 5.6+ (recommended) |

**Error if TypeScript too old:**
```
error TS5023: Unknown option 'target'.
Argument for '--target' option must be: 'es5', 'es6', ...
```

---

## Complete tsconfig.json Examples

### Node 24 (ES2024)

```json
{
  "compilerOptions": {
    "target": "ES2024",
    "lib": ["ES2024"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "declaration": true,
    "outDir": "dist"
  }
}
```

### Node 22 (ES2023)

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "lib": ["ES2023"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "declaration": true,
    "outDir": "dist"
  }
}
```

### Node 20 (ES2023) - Current LTS

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "lib": ["ES2023"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "declaration": true,
    "outDir": "dist"
  }
}
```

### Node 18 (ES2022) - Default Recommendation

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "Node16",
    "moduleResolution": "Node16",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "declaration": true,
    "outDir": "dist"
  }
}
```

### Node 16 (ES2021) - Legacy LTS

```json
{
  "compilerOptions": {
    "target": "ES2021",
    "lib": ["ES2021"],
    "module": "Node16",
    "moduleResolution": "Node16",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "declaration": true,
    "outDir": "dist"
  }
}
```

---

## Using @tsconfig/bases

Use pre-built configurations from [@tsconfig/bases](https://github.com/tsconfig/bases):

```bash
pnpm add -D @tsconfig/node22
```

```json
{
  "extends": "@tsconfig/node22/tsconfig.json",
  "compilerOptions": {
    "outDir": "dist"
  }
}
```

**Available bases:**
- `@tsconfig/node24`
- `@tsconfig/node22`
- `@tsconfig/node20`
- `@tsconfig/node18`
- `@tsconfig/node16`

---

## Module System Configuration

### ESM (Recommended for Node 18+)

```json
{
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

**package.json:**
```json
{
  "type": "module"
}
```

### CommonJS (Legacy)

```json
{
  "compilerOptions": {
    "module": "CommonJS",
    "moduleResolution": "Node"
  }
}
```

### Dual Package (ESM + CJS)

For libraries supporting both:

```json
{
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "declaration": true,
    "declarationMap": true
  }
}
```

Use separate tsconfig files or build tools (tsup, unbuild) for dual output.

---

## Known Issues

### Node 16.0-16.2: V8 Spread Bug

Node 16.0-16.2 has a V8 bug affecting spread after optional chaining:

```typescript
// May fail on Node 16.0-16.2
foo?.bar(...args);
```

**Fix:** Use Node 16.3+ or set `target: "ES2019"` to avoid the feature.

### Node 14: Same V8 Bug

All Node 14 versions have this bug. Consider:
- Upgrading to Node 16+
- Setting `target: "ES2019"` if spread after optional chaining is used

---

## Detection Commands

### Check Current Node Version

```bash
node --version
```

### Check Node ES Feature Support

Use [node.green](https://node.green/) for detailed compatibility tables.

### Check TypeScript Version

```bash
npx tsc --version
```

### Check Current tsconfig Target

```bash
grep -E '"target"|"lib"' tsconfig.json
```

---

## Migration Checklist

When upgrading Node.js version:

1. [ ] Update `.nvmrc` / `.node-version`
2. [ ] Update `package.json engines.node`
3. [ ] Update `tsconfig.json target` and `lib`
4. [ ] Update `tsconfig.json module` and `moduleResolution` if needed
5. [ ] Check TypeScript version supports new target
6. [ ] Run `pnpm install` with new Node version
7. [ ] Run `pnpm exec tsc --noEmit` to verify compilation
8. [ ] Run full test suite
9. [ ] Check bundle size (should decrease)

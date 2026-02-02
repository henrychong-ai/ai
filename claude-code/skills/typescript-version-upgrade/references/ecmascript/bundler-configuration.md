# Bundler Configuration for ECMAScript Targets

Aligning esbuild, Vite, Webpack, and other bundlers with TypeScript ES targets.

**Sources:**
- [esbuild FAQ](https://esbuild.github.io/faq/)
- [Vite Migration Guide](https://v5.vite.dev/guide/migration)
- [Total TypeScript - Configuring TypeScript](https://www.totaltypescript.com/books/total-typescript-essentials/configuring-typescript)

---

## Key Principle: Alignment

**Your bundler's target MUST match or be lower than your tsconfig target.**

| tsconfig target | Bundler target | Valid? |
|-----------------|----------------|--------|
| ES2022 | ES2022 | ✅ Match |
| ES2022 | ES2020 | ✅ Bundler downgrades further |
| ES2020 | ES2022 | ❌ Bundler may emit unsupported syntax |

---

## esbuild Configuration

### Basic Target Setting

```javascript
// esbuild.config.js
import { build } from 'esbuild';

await build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  outfile: 'dist/bundle.js',
  target: 'es2022',  // Match tsconfig.json target
});
```

### Target Options

| Target | Description |
|--------|-------------|
| `es2015` - `es2024` | Specific ES version |
| `esnext` | Latest features (no downleveling) |
| `node18`, `node20`, `node22` | Node.js version (auto-determines ES) |
| `chrome100`, `firefox100` | Browser version |

### Multiple Targets

```javascript
await build({
  // Target multiple environments
  target: ['es2022', 'node18', 'chrome100'],
});
```

esbuild uses the most restrictive target from the list.

### esbuild + TypeScript

esbuild only transpiles TypeScript, it doesn't type-check:

```javascript
await build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  target: 'es2022',
  // Let esbuild read tsconfig.json settings
  tsconfig: 'tsconfig.json',
});
```

---

## Vite Configuration

### Build Target

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: 'es2022',  // Match tsconfig.json target
  },
});
```

### Default Behavior (Vite 5+)

Vite 5 defaults to `esnext` for both dev and build. For production:

```typescript
export default defineConfig({
  build: {
    target: 'es2022',
  },
  esbuild: {
    target: 'es2022',  // For dev server
  },
});
```

### useDefineForClassFields (CRITICAL)

**Vite 5+ issue:** If tsconfig `target` is not ES2022+, `useDefineForClassFields` defaults to `false`, which can conflict with esbuild.

**Solution 1:** Use ES2022+ target
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022"
  }
}
```

**Solution 2:** Explicitly set the option
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true
  }
}
```

### Browser Compatibility

```typescript
export default defineConfig({
  build: {
    target: ['es2022', 'chrome100', 'firefox100', 'safari15'],
  },
});
```

---

## Webpack Configuration

### Using ts-loader

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  // Webpack's own target (for output chunk format)
  target: 'node18',  // or 'web', 'browserslist'
};
```

ts-loader uses tsconfig.json settings for transpilation.

### Using esbuild-loader (Faster)

```javascript
// webpack.config.js
const { EsbuildPlugin } = require('esbuild-loader');

module.exports = {
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: 'esbuild-loader',
        options: {
          target: 'es2022',
        },
      },
    ],
  },
  optimization: {
    minimizer: [
      new EsbuildPlugin({
        target: 'es2022',
      }),
    ],
  },
};
```

### Using babel-loader

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ['@babel/preset-env', { targets: { node: '18' } }],
              '@babel/preset-typescript',
            ],
          },
        },
      },
    ],
  },
};
```

---

## Rollup Configuration

### Using @rollup/plugin-typescript

```javascript
// rollup.config.js
import typescript from '@rollup/plugin-typescript';

export default {
  input: 'src/index.ts',
  output: {
    file: 'dist/bundle.js',
    format: 'esm',
  },
  plugins: [
    typescript({
      // Uses tsconfig.json by default
      // Override specific options:
      target: 'ES2022',
    }),
  ],
};
```

### Using rollup-plugin-esbuild

```javascript
import esbuild from 'rollup-plugin-esbuild';

export default {
  input: 'src/index.ts',
  output: {
    file: 'dist/bundle.js',
    format: 'esm',
  },
  plugins: [
    esbuild({
      target: 'es2022',
    }),
  ],
};
```

---

## SWC Configuration

### .swcrc

```json
{
  "jsc": {
    "target": "es2022",
    "parser": {
      "syntax": "typescript"
    }
  },
  "module": {
    "type": "es6"
  }
}
```

### ES2023/ES2024 Support

SWC 1.8.0+ supports ES2023 and ES2024 targets:

```json
{
  "jsc": {
    "target": "es2024"
  }
}
```

**Known Issue:** ts-node with SWC may fail on ES2023+ targets. Workaround:

```json
{
  "jsc": {
    "target": "es2022"  // Use ES2022 for ts-node compatibility
  }
}
```

---

## tsup Configuration

tsup (TypeScript bundler using esbuild) configuration:

```typescript
// tsup.config.ts
import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  target: 'es2022',
  dts: true,
  clean: true,
});
```

---

## isolatedModules Setting

When using esbuild, SWC, or other non-tsc transpilers, enable `isolatedModules`:

```json
// tsconfig.json
{
  "compilerOptions": {
    "isolatedModules": true
  }
}
```

This disables TypeScript features that require cross-file analysis:
- `const enum` (use regular `enum` instead)
- `export =` / `import =` syntax
- Re-exporting types without `type` keyword

---

## Common Configuration Patterns

### Node.js Application (ES2022)

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext"
  }
}
```

```typescript
// vite.config.ts or esbuild
{
  target: 'node18'
}
```

### Modern Web Application (ES2022)

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler"
  }
}
```

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    target: ['es2022', 'chrome100', 'firefox100', 'safari15'],
  },
});
```

### Library (Dual ESM/CJS)

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "declaration": true
  }
}
```

```typescript
// tsup.config.ts
export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  target: 'es2022',
  dts: true,
});
```

---

## Troubleshooting

### 1. "Cannot use 'import.meta' outside a module"

**Cause:** Output format is CommonJS but code uses ESM features.

**Solution:** Use ESM output format or target Node 14+:
```javascript
{
  format: 'esm',
  target: 'node18'
}
```

### 2. Static Initialization Blocks Not Supported

**Cause:** ES2022 feature not supported by target runtime.

**Solution:** Lower target or update runtime:
```javascript
{
  target: 'es2021'  // No static blocks
}
```

### 3. Bundle Too Large After ES Upgrade

**Cause:** Polyfills still being included for old targets.

**Solution:** Update browserslist/targets to match new ES version:
```
# .browserslistrc
chrome >= 94
firefox >= 93
safari >= 15
```

### 4. Class Fields Behaving Differently

**Cause:** `useDefineForClassFields` mismatch between TypeScript and bundler.

**Solution:** Explicitly set in tsconfig.json:
```json
{
  "compilerOptions": {
    "useDefineForClassFields": true
  }
}
```

---

## Version Requirements

| Tool | ES2023 Support | ES2024 Support |
|------|----------------|----------------|
| esbuild | 0.18+ | 0.21+ |
| SWC | 1.8+ | 1.8+ |
| TypeScript | 5.5+ | 5.6+ |
| Vite | 5.0+ | 5.4+ |
| Rollup | 4.0+ | 4.0+ |
| Webpack | 5.x | 5.x |

---

## Quick Reference: Target Alignment

```
┌─────────────────────────────────────────────────────────────┐
│                     Target Alignment                         │
├─────────────────────────────────────────────────────────────┤
│  tsconfig.json  ─────►  Bundler (esbuild/vite/webpack)      │
│     target              build.target / target                │
│                                                              │
│  ES2022         ═════►  es2022 / node18 / chrome94          │
│  ES2023         ═════►  es2023 / node20 / chrome110         │
│  ES2024         ═════►  es2024 / node22 / chrome117         │
└─────────────────────────────────────────────────────────────┘
```

**Rule:** Bundler target should match or be MORE restrictive than tsconfig target.

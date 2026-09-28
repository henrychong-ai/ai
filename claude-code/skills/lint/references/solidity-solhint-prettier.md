# Solidity: Solhint + Prettier (or forge fmt)

Single owner of Solidity lint and format configuration. Contract standards (patterns, security, testing, Hardhat/Foundry setup) belong to a `/solidity` skill where installed.

| Concern | Hardhat projects | Foundry projects |
|---------|----------------------------------|------------------|
| Format | Prettier + `prettier-plugin-solidity` v2 | `forge fmt` |
| Lint | Solhint 6 (recommended; add where missing) | Solhint 6 |
| Config | `.prettierrc.json`, `.solhint.json` | `foundry.toml` `[fmt]`, `.solhint.json` |

Hardhat projects usually already format with Prettier; Solhint is the recommended addition. Solidity sits outside the Oxlint/Biome stack: Biome does not parse `.sol` files.

Check versions before pinning: `npm view solhint version`, `npm view prettier-plugin-solidity version`.

## Prettier + prettier-plugin-solidity

```bash
pnpm add -D prettier prettier-plugin-solidity
```

`.prettierrc.json`: keep the repo's existing JS/TS settings, and add a `*.sol` override so Solidity follows the Solidity style guide:

```json
{
  "plugins": ["prettier-plugin-solidity"],
  "overrides": [
    {
      "files": "*.sol",
      "options": {
        "printWidth": 120,
        "tabWidth": 4,
        "useTabs": false,
        "singleQuote": false,
        "bracketSpacing": false
      }
    }
  ]
}
```

```bash
pnpm exec prettier --check "contracts/**/*.sol"
pnpm exec prettier --write "contracts/**/*.sol"
```

Existing repos keep their current Prettier settings; changing them reformats every contract. Plugin v2 needs Prettier 3.

## forge fmt (Foundry)

`forge fmt` ships with Foundry. Configure in `foundry.toml`:

```toml
[fmt]
line_length = 120
tab_width = 4
bracket_spacing = false
int_types = "long"
quote_style = "double"
```

```bash
forge fmt --check
forge fmt
```

## Solhint

```bash
pnpm add -D solhint
```

Template: `templates/.solhint.json`.

```json
{
  "extends": "solhint:recommended",
  "rules": {
    "compiler-version": ["error", "^0.8.28"],
    "func-visibility": ["warn", { "ignoreConstructors": true }],
    "gas-custom-errors": "warn",
    "max-line-length": ["warn", 120],
    "no-console": "error",
    "no-empty-blocks": "warn",
    "no-unused-vars": "error",
    "avoid-tx-origin": "error",
    "check-send-result": "error",
    "reentrancy": "warn",
    "use-natspec": "warn"
  }
}
```

- `compiler-version`: set to the pragma range the project compiles with (match the pinned solc version).
- `gas-custom-errors`: prefer custom errors over `require` strings.
- `use-natspec`: NatSpec on contracts and public functions.
- `no-console`: blocks `hardhat/console.sol` imports from reaching committed code.

```bash
pnpm exec solhint "contracts/**/*.sol"          # Hardhat layout
pnpm exec solhint "src/**/*.sol" "test/**/*.sol" # Foundry layout
pnpm exec solhint --fix --noPrompt "contracts/**/*.sol"
```

`--noPrompt` skips the interactive backup question, which is needed in hooks and CI.

### Test and Harness Contracts

Solidity tests (`test_…`, `testFuzz_…`, `invariant_…` functions, `setUp`) and harness contracts break the production naming and NatSpec rules on purpose. Relax them for tests only, so security rules such as `avoid-tx-origin` still apply:

- **Tests in a `test/` directory** (Foundry, and Hardhat 3 Solidity tests placed there): copy `templates/test/.solhint.json` to `test/.solhint.json`. Solhint 6 merges a nested `.solhint.json` over the root one for files below it, so only the listed rules change:

  ```json
  {
    "rules": {
      "use-natspec": "off",
      "func-name-mixedcase": "off",
      "one-contract-per-file": "off",
      "no-empty-blocks": "off",
      "no-console": "off",
      "gas-custom-errors": "off",
      "gas-strict-inequalities": "off",
      "import-path-check": "off"
    }
  }
  ```

  `import-path-check` is off because remapped imports (`forge-std/Test.sol` → `lib/forge-std/src/`) do not resolve for Solhint; the compiler still checks them.
- **`*.t.sol` files next to contracts** (Hardhat 3 allows Solidity tests anywhere under `contracts/`): a nested config cannot target a filename pattern, and a Solhint `extends` cannot point at a local file. Put a file-level comment after the pragma instead:

  ```solidity
  // solhint-disable use-natspec, func-name-mixedcase, gas-strict-inequalities
  ```

  Prefer a `test/` directory for new projects so the override file covers every test.

Foundry projects with remapped dependencies in production code (`@openzeppelin/…` → `lib/`) also set `"import-path-check": "off"` in the root `.solhint.json`. Hardhat resolves imports from `node_modules`, which Solhint finds.

## Hooks and CI

lint-staged:

```js
"*.sol": ["solhint --fix --noPrompt", "prettier --write"],   // Hardhat
// "*.sol": ["solhint --fix --noPrompt", "forge fmt"],       // Foundry
```

CI step: `solhint "contracts/**/*.sol"` and `prettier --check "contracts/**/*.sol"` (or `forge fmt --check`). Add Slither or other security analysis as separate gates.

## VS Code

The Nomic Foundation Solidity extension (`NomicFoundation.hardhat-solidity`) formats `.sol` files with Prettier (Hardhat) or `forge fmt` (Foundry); run Solhint through the scripts and hooks above.

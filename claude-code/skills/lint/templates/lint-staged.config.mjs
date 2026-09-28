// lint-staged.config.mjs: Oxlint + Biome stack
// .mjs so the ESM export works whatever package.json "type" says.
// Simple setups can use the package.json "lint-staged" field instead.

export default {
  // TypeScript / JavaScript: lint, then format + sort imports
  "*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}": [
    "oxlint --fix --max-warnings=0",
    "biome check --write --no-errors-on-unmatched",
  ],

  // Vue: Oxlint lints <script> blocks (Biome's Vue support is experimental)
  "*.vue": ["oxlint --fix --max-warnings=0"],

  // CSS and JSON. Keep Markdown, YAML and HTML out of Biome globs: Biome does not
  // format them yet (HTML only behind an opt-in), and a file Biome skips fails the hook.
  "*.{css,json,jsonc}": ["biome check --write --no-errors-on-unmatched"],

  // Residual ESLint projects: add "eslint --fix --max-warnings=0" to the matching globs.

  // Python (uncomment if using Python)
  // "*.py": ["ruff check --fix", "ruff format"],

  // Go (uncomment if using Go)
  // golangci-lint works on packages, not file lists, so the function form runs it
  // once on the whole module instead of appending staged file names. Formatting
  // comes from golangci-lint's formatters; a separate gofmt -w would undo gofumpt.
  // "*.go": () => "golangci-lint run --fix ./...",

  // Solidity (uncomment if using Solidity)
  // "*.sol": ["solhint --fix --noPrompt", "prettier --write"],   // Hardhat + Prettier
  // "*.sol": ["solhint --fix --noPrompt", "forge fmt"],          // Foundry

  // .NET (uncomment if using .NET)
  // "*.cs": ["dotnet format --include"],
};

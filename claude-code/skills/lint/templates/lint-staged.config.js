// lint-staged.config.js
// Oxlint + Biome stack
// For complex lint-staged configurations
// Simple configs can use package.json "lint-staged" field instead

export default {
  // TypeScript/JavaScript
  '*.{ts,tsx,js,jsx,mjs,cjs}': [
    'oxlint --fix --max-warnings=0',
    'biome format --write',
  ],

  // Vue
  '*.vue': [
    'oxlint --fix --max-warnings=0',
    'biome format --write',
  ],

  // Styles (Biome formats CSS only, not SCSS/Less)
  '*.css': [
    'biome format --write',
  ],

  // Data/Config files (Biome formats JSON and Markdown, NOT YAML)
  '*.{json,md}': [
    'biome format --write',
  ],

  // HTML
  '*.html': [
    'biome format --write',
  ],

  // Python (uncomment if using Python)
  // '*.py': [
  //   'ruff check --fix',
  //   'ruff format',
  // ],

  // Go (uncomment if using Go)
  // '*.go': [
  //   'golangci-lint run --fix',
  //   'gofmt -w',
  // ],

  // Solidity (uncomment if using Solidity)
  // Foundry projects: use forge fmt
  // Hardhat projects: use prettier --write as fallback
  // '*.sol': [
  //   'solhint --fix',
  //   'forge fmt',
  // ],

  // .NET/C# (uncomment if using .NET)
  // '*.cs': [
  //   'dotnet format --include',
  // ],
};

// lint-staged.config.js
// For complex lint-staged configurations
// Simple configs can use package.json "lint-staged" field instead

export default {
  // TypeScript/JavaScript
  '*.{ts,tsx}': [
    'eslint --fix --max-warnings=0',
    'prettier --write',
  ],
  '*.{js,jsx,mjs,cjs}': [
    'eslint --fix --max-warnings=0',
    'prettier --write',
  ],

  // Vue
  '*.vue': [
    'eslint --fix --max-warnings=0',
    'prettier --write',
  ],

  // Styles
  '*.{css,scss,sass,less}': [
    'prettier --write',
  ],

  // Data/Config files
  '*.{json,yaml,yml}': [
    'prettier --write',
  ],

  // Markdown
  '*.md': [
    'prettier --write',
  ],

  // HTML
  '*.html': [
    'prettier --write',
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
  // '*.sol': [
  //   'solhint --fix',
  //   'prettier --write',
  // ],

  // .NET/C# (uncomment if using .NET)
  // '*.cs': [
  //   'dotnet format --include',
  // ],
};

// commitlint.config.mjs: commit-msg gate (run by .husky/commit-msg)
//
// Accepts both header shapes:
//   [ABC-123] imperative description    ticket-first (adjust the key pattern to your tracker)
//   feat(scope): imperative description Conventional Commits
// The message format itself is defined by your team's conventions; this file only
// enforces it. Teaching the parser both shapes keeps every other rule
// (header length, full stop, body line length) applying to ticket-first
// commits too; an `ignores` entry would skip them entirely.
// A header matching neither shape leaves `subject` empty and is rejected.
//
// Deliberately lenient on case and length, so adopting it does not block an
// existing ticket-first history (capitalised subjects, headers over 100
// characters): `subject-case` is off and `header-max-length` only warns.
// Tighten both if your conventions require it.

const HEADER_PATTERN = /^(?:\[([A-Z]+-\d+)\]|(\w+)(?:\(([^)]+)\))?!?:)\s(.+)$/;

export default {
  extends: ["@commitlint/config-conventional"],
  parserPreset: {
    parserOpts: {
      headerPattern: HEADER_PATTERN,
      headerCorrespondence: ["ticket", "type", "scope", "subject"],
    },
  },
  rules: {
    // Ticket-first headers carry no conventional type
    "type-empty": [0],
    // Capitalised subjects are allowed (see above)
    "subject-case": [0],
    // Long headers warn instead of failing the commit (see above)
    "header-max-length": [1, "always", 100],
    "subject-empty": [2, "never"],
    "subject-full-stop": [2, "never", "."],
    "body-max-line-length": [2, "always", 100],
  },
};

# CC → Codex Conversion — Phase-1 Assessment

Read-only evidence table for a batch skill reformat. One row per skill; assign from evidence (no pre-exclusion). Methodology: `references/cc-to-codex-conversion-guide.md`.

**Batch:** <name / plan reference>
**Date:** <YYYY-MM-DD>
**Skills in scope:** <count> · **Excluded:** <list + reason, e.g. Codex-native / vendor-bundled>

---

## Legend

- **Effort tier:** `T1` reformat · `T2` convert interactive→process · `T3` re-architect (cloud routine/multi-agent → Automation).
- **Distribution:** `A` Tier-A pipeline allowlist (verbatim/transform-clean) · `B` Tier-B hand-authored.
- **🔒 sensitive-data:** `clean` / `extract-at-source` (PII/regulated data present → fix at source) / `n/a`.
- **🔌 harness-deps:** MCP server(s) / plugin(s) / local app / path dependency / `none`.
- **What survives:** the portable core (knowledge / process / templates / scripts).
- **Disposition:** the build action.

---

## Evidence table

| # | Skill | Effort | Dist | 🔒 sensitive-data | 🔌 harness-deps | What survives | Disposition |
|--:|---|:--:|:--:|---|---|---|---|
| 1 | `<skill>` | T1 | A | clean | none | knowledge+process | allowlist verbatim |
| 2 | `<skill>` | T2 | B | clean | `<mcp>` | decision tree | hand-author; parameterise prompt flow |
| 3 | `<skill>` | T3 | B | n/a | Automation | playbook | rebuild as Codex Automation |
| … | | | | | | | |

---

## Roll-up

- **T1:** <n> (Tier-A: <n> / Tier-B: <n>) · **T2:** <n> · **T3:** <n>
- **🔒 extract-at-source (BLOCKING):** <list>
- **🔌 knowledge-only (dependency absent):** <list>
- **Build order:** <waves — e.g. T1 Tier-A batch → T2 → T3, throttled to respect rate limits>

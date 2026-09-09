# TODO — codex

Open items, deferred work, and unverified data for this skill.

- [ ] **Service-tier parity gap:** the stdio MCP accepted a per-call `service_tier`; the plugin companion has no equivalent flag, so tier is whatever `service_tier` in `~/.codex/config.toml` says (currently `"default"`). Decide whether `/codex … fast` should offer to edit config.toml, or stay documentation-only as it is now.
- [ ] **Reasoning above xhigh:** the companion validates effort against `none`/`minimal`/`low`/`medium`/`high`/`xhigh` and throws `Unsupported reasoning effort` for `max` and `ultra` (verified 2026-09-09 in `scripts/codex-companion.mjs`, `VALID_REASONING_EFFORTS`). Re-check on plugin upgrades in case the enum widens; until then `max`/`ultra` work only through the Codex Desktop app or the native CLI.
- [ ] **Plugin root is version-volatile:** every reference resolves `~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs` by glob because the version segment moves on each upgrade (1.0.6 at time of writing). Revisit if the plugin ever exposes a stable entry point outside plugin-authored commands, which get `${CLAUDE_PLUGIN_ROOT}`.
- [ ] **`minimal` effort:** new level between `none` and `low` on the companion path, not previously exposed by `/codex`. Try it on high-volume checks and record whether it earns a place in the grammar.

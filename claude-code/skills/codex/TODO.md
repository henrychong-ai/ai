# TODO — codex

Open items, deferred work, and unverified data for this skill.

- [ ] **Service-tier parity gap:** the stdio MCP accepted a per-call `service_tier`; the plugin companion has no equivalent flag, so tier is whatever `service_tier` in `~/.codex/config.toml` says (currently `"default"`). Decide whether `/codex … fast` should offer to edit config.toml, or stay documentation-only as it is now.
- [ ] **Reasoning above xhigh:** the companion validates effort against `none`/`minimal`/`low`/`medium`/`high`/`xhigh` and throws `Unsupported reasoning effort` for `max` and `ultra` (verified 2026-09-09 in `scripts/codex-companion.mjs`, `VALID_REASONING_EFFORTS`) — including for `gpt-6-astra`, whose catalogue entry does list both. Re-check on plugin upgrades in case the enum widens; until then `max`/`ultra` work only through the Codex Desktop app or the native CLI.
- [x] **Plugin root is version-volatile:** resolved 2026-09-09 by a wrapper — `~/scripts/codex-companion` resolves the newest plugin root and execs the companion, so every caller names one fixed path and the permission rule `Bash(~/scripts/codex-companion:*)` covers them all. The glob form stays documented in `references/codex-plugin-setup.md` for anyone without the wrapper.
- [ ] **`minimal` effort:** new level between `none` and `low` on the companion path, not previously exposed by `/codex`. Try it on high-volume checks and record whether it earns a place in the grammar.
- [x] **Astra as `/codex` default:** done 2026-09-09 — `/codex` now defaults to `gpt-6-astra` at `medium` (Astra's catalogue default). Sol, Terra, and Luna stay reachable by name. Re-baseline the effort after a few runs if `medium` proves thin on hard problems.

# Instruction Creator: TODO & Open Items

The honest record of everything not-yet-done, unverified, or deferred for this skill.
Keep it current as the skill evolves. If nothing is open, say so explicitly.

## Open items
- [x] Verify whether a later Claude Code version keeps the prompt cache across an effort change. Done 2026-09-24: yes on Fable 5.1 from v2.1.260 and on Opus 5.5, with an API key or subscription (not on Bedrock, Agent Platform, a Claude apps gateway, disabled experimental betas, or HIPAA). `cache-and-token-efficiency.md`, the Fable 5.1 file, SKILL.md, the YAML guide, and the checklists updated.
- [ ] Verify the Fable 5.1 harness-injected blocks listed in `references/claude-fable-5-1-compatibility.md` Part 2A across multiple Claude Code sessions, and check whether Claude Desktop and Cowork inject the same set. The current list was observed in one session on 2026-09-01 and is recorded as an inference, not a verified fact.
- [ ] Collect field reports for Fable 5.1 and fold them into `references/claude-fable-5-1-compatibility.md`, in the way the Opus 5 file carries a Field Reports section.
- [ ] Re-baseline the `effort:` pins used in this skill's own examples and templates against Fable 5.1, given that level names do not map to the same amount of thinking across models.
- [ ] Verify across several Claude Code 2.1.280+ sessions that the harness injects the Opus 5.5 "user hasn't heard from you in a while" nudge, and check Desktop and Cowork. Recorded in SKILL.md and Part 3 of `references/claude-opus-5-5-compatibility.md` from a single-session observation (inference).
- [ ] Re-measure the Fable 5.1 cost-per-task claims against Opus 5.5. The Fable 5.1 file (Part 2B routing table), the index routing table, and `creation-checklists.md` still carry comparisons measured against Opus 5.
- [ ] Collect Opus 5.5 field reports beyond the two in Part 7 of the Opus 5.5 file (both claude.dev posts; Shihipar's predates Opus 5.5).
- [ ] Re-baseline this skill's own example `effort:` pins against Opus 5.5's `medium` default (extends the Fable 5.1 item above).

## Deferred / future
- [x] Split the model compatibility references into a per-tier index. Done 2026-09-24 with the Opus 5.5 file (fifth compatibility file): `references/model-compatibility-index.md`.

## Unverified data / placeholders
- [ ] Verify whether Claude Desktop Code-tab sessions receive the account-level "Instructions for Claude" text in addition to `~/.claude/CLAUDE.md`. If they do, paste artefacts for that field need an explicit CLAUDE.md-is-canonical precedence line (recorded 2026-09-14 as unverified).
- [ ] Verify whether the Cowork "Global instructions" field carries the same 32,768-code-point cap as "Instructions for Claude", and whether the two fields still exist separately after the Cowork-to-cloud migration (the app's i18n keeps both labels; observed 2026-09-14).
- [ ] Claude Code harness-injection list (Part 2A of the Fable 5.1 reference): single-session observation, 2026-09-01, marked as an inference in the file itself.

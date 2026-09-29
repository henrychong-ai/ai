# Instruction Creator: TODO & Open Items

The honest record of everything not-yet-done, unverified, or deferred for this skill.
Keep it current as the skill evolves. If nothing is open, say so explicitly.

## Open items
- [x] Verify whether a later Claude Code version keeps the prompt cache across an effort change. Done 2026-09-24: yes on Fable 5.1 from v2.1.260 and on Opus 5.5, with an API key or subscription (not on Bedrock, Agent Platform, a Claude apps gateway, disabled experimental betas, or HIPAA). `cache-and-token-efficiency.md`, the Fable 5.1 file, SKILL.md, the YAML guide, and the checklists updated.
- [ ] Verify the Fable 5.1 harness-injected blocks listed in `references/claude-fable-5-1-compatibility.md` Part 2A across multiple Claude Code sessions, and check whether Claude Desktop and Cowork inject the same set. The current list was observed in one session on 2026-09-01 and is recorded as an inference, not a verified fact.
- [ ] Collect field reports for Fable 5.1 and fold them into `references/claude-fable-5-1-compatibility.md`, in the way the Opus 5 file carries a Field Reports section.
- [x] Re-baseline the `effort:` pins used in this skill's own examples and templates against Fable 5.1, given that level names do not map to the same amount of thinking across models. Superseded 2026-09-29 by the routing ladder (see the Opus 5.5 re-baseline item below): the examples now pin `model: sonnet` + `effort: medium`, and Fable 5.1 sits outside the ladder as the escalation tier.
- [ ] Opus 5.5 harness injection: the "user hasn't heard from you in a while" nudge is confirmed in Claude Code (2.1.280 and 2.1.281, two sessions, 2026-09-24). Still open: check Desktop and Cowork, and confirm across more sessions that Opus 5.5 does not receive the Fable 5.1 finish-the-task blocks (absent in one 2.1.281 session). Recorded in SKILL.md and Part 3 of `references/claude-opus-5-5-compatibility.md`.
- [ ] Re-measure the Fable 5.1 cost-per-task claims against Opus 5.5. The Fable 5.1 file (Part 2B routing table), the index routing table, and `creation-checklists.md` still carry comparisons measured against Opus 5.
- [ ] Collect Opus 5.5 field reports beyond the two in Part 7 of the Opus 5.5 file (both claude.dev posts; Shihipar's predates Opus 5.5).
- [x] Re-baseline this skill's own example `effort:` pins against Opus 5.5's `medium` default (extends the Fable 5.1 item above). Superseded 2026-09-29 by the routing ladder: SKILL.md's agent and command templates now pin `model: sonnet` + `effort: medium`, and the YAML guide and checklists follow it.
- [ ] Sonnet 5.5 harness injection: verify which harness text Claude Code injects in Sonnet 5.5 sessions (the "user hasn't heard from you in a while" silence nudge? the Fable 5.1 finish-the-task blocks?), across more than one session and version, then record it in the Sonnet 5.5 file and SKILL.md's "Harness-Injected on Claude Code" list.
- [ ] Verify whether a `model: sonnet` subagent under an Opus session takes the session's effort or Sonnet 5.5's own saved or default level when `effort` is omitted. The sub-agents doc says only "inherits from session"; the routing ladder's advice to pin `effort: medium` on Sonnet agents holds either way.
- [ ] Confirm the `modelSettings` key Claude Code writes for Sonnet 5.5 (`claude-sonnet-5-5` is inferred from the canonical-name rule, not observed).
- [ ] Docs conflict on steering thinking: the Claude Code model-config page says a prompt or CLAUDE.md can make the model think more or less often; the Sonnet 5.5 prompting guide says asking it to think less "doesn't reliably reduce its thinking". The Sonnet 5.5 file treats the prompting guide as authoritative; re-check when either page changes.
- [ ] Anthropic's "Optimizing for cost and intelligence" page still measures Sonnet 5 only (https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Refresh the Sonnet 5.5 cost-per-task figures, and the routing ladder's cost rationale, when Anthropic publishes them or after measuring.
- [ ] Collect Sonnet 5.5 field reports beyond the launch-page customer quotes and the Epic Games quote in the claude.dev "Building with Claude Sonnet 5.5" post, and fold them into the Sonnet 5.5 file.
- [ ] Haiku 5.5 is announced "in the coming weeks": run a delta pass on release (index Current Models and Alias Targets, the `haiku` entry in the routing ladder's "Outside the ladder" line, and any Haiku compatibility file).
- [ ] Confirm whether `/claude-api build-eval` and `/claude-api hillclimb` can drive a `claude -p` runner to evaluate skills (undocumented; both target apps that call the Claude API). Until confirmed, use `claude plugin eval` (v2.1.269+) for skill evals.

## Deferred / future
- [x] Split the model compatibility references into a per-tier index. Done 2026-09-24 with the Opus 5.5 file (fifth compatibility file): `references/model-compatibility-index.md`.

## Unverified data / placeholders
- [ ] Verify whether Claude Desktop Code-tab sessions receive the account-level "Instructions for Claude" text in addition to `~/.claude/CLAUDE.md`. If they do, paste artefacts for that field need an explicit CLAUDE.md-is-canonical precedence line (recorded 2026-09-14 as unverified).
- [ ] Verify whether the Cowork "Global instructions" field carries the same 32,768-code-point cap as "Instructions for Claude", and whether the two fields still exist separately after the Cowork-to-cloud migration (the app's i18n keeps both labels; observed 2026-09-14).
- [ ] Claude Code harness-injection list (Part 2A of the Fable 5.1 reference): single-session observation, 2026-09-01, marked as an inference in the file itself.

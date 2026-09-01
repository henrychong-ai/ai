# Instruction Creator: TODO & Open Items

The honest record of everything not-yet-done, unverified, or deferred for this skill.
Keep it current as the skill evolves. If nothing is open, say so explicitly.

## Open items
- [ ] Verify whether a later Claude Code version adopts the API's per-message effort beta (`mid-conversation-output-config-2026-07-01`), which preserves the prompt cache across an effort change. As of 2.1.257 it has not, and the prompt-caching doc still keys the cache by effort. If that changes, update `references/cache-and-token-efficiency.md` (the Fable 5.1 notes section and the mid-session `/effort` cache-bust rule).
- [ ] Verify the Fable 5.1 harness-injected blocks listed in `references/claude-fable-5-1-compatibility.md` Part 2A across multiple Claude Code sessions, and check whether Claude Desktop and Cowork inject the same set. The current list was observed in one session on 2026-09-01 and is recorded as an inference, not a verified fact.
- [ ] Collect field reports for Fable 5.1 and fold them into `references/claude-fable-5-1-compatibility.md`, in the way the Opus 5 file carries a Field Reports section.
- [ ] Re-baseline the `effort:` pins used in this skill's own examples and templates against Fable 5.1, given that level names do not map to the same amount of thinking across models.

## Deferred / future
- [ ] Consider splitting the model compatibility references into a per-tier index once a fourth frontier-tier file lands, so SKILL.md points at one router rather than four files.

## Unverified data / placeholders
- [ ] Claude Code harness-injection list (Part 2A of the Fable 5.1 reference): single-session observation, 2026-09-01, marked as an inference in the file itself.

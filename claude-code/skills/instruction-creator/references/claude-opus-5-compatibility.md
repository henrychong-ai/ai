# Claude Opus 5 Compatibility Guide

*Companion reference to the Model-Aware Instruction Authoring section in SKILL.md.*

**Opus 5 released:** July 2026 (CC `opus` alias resolves to it as of 2026-07-25)
**Last updated:** 2026-08-03
**Pricing:** $5 / $25 per MTok — unchanged from Opus 4.8; half of Fable 5 (cache reads: Opus 5 $0.50/MTok versus Fable 5.1 $0.25, half the Opus rate; Fable 5 was $1). **Model ID:** `claude-opus-5`. **Claude Code alias:** `opus`.

Opus 5 is a **step-change Opus-tier release** (Anthropic's words), not an incremental one: the largest gains are deep reasoning, agentic/long-horizon coding, test-time compute scaling, and efficiency at lower effort. Tier map unchanged: Haiku (speed) → Sonnet (balance) → **Opus (hard problems, workhorse)** → Fable (frontier, long-horizon). 1M context (default AND maximum — no smaller variant), 128K max output.

**API surface vs Opus 4.8:**
- **Thinking on by default** — the model decides when/how much to think; effort is the depth control. `thinking: {type: "adaptive"}` remains valid and equivalent to the default. `max_tokens` is a hard cap on thinking + response, so revisit it for workloads migrated from no-thinking 4.8 configs.
- **Breaking change:** `thinking: {type: "disabled"}` is accepted only at effort `high` or below — with `xhigh`/`max` it returns a 400. (Fable 5 comparison: thinking can never be disabled there.)
- **Effort ladder now includes `max`** — `low`/`medium`/`high`/`xhigh`/`max`. At `xhigh`/`max`, set a large `max_tokens` so the model has room to think and act.
- Prompt-cache minimum down to 512 tokens (from 1,024). Mid-conversation tool changes (beta header) and `fallbacks: "default"` mode (beta) are new. Fast mode (research preview, Claude API only) prices Opus 5 at $10/$50.
- For API-migration mechanics use the bundled **`/claude-api`** skill.

The 8 Core Rules in SKILL.md apply **unchanged** — Opus 5 continues the literal/strong instruction-following lineage. Direction of migration work: same as Fable 5, **removal-first**, with three NEW removal targets and one new decoupling, detailed below.

---

# Part 1 — The Overarching Opus 5 Principle: Removal-First Reaches the Opus Tier

Fable 5 established that migration means *removing* scaffolds rather than rewriting them. Opus 5 brings that doctrine to the Opus tier, and Anthropic's Opus 5 prompting guide names three specific instruction classes that now actively hurt:

1. **Verification scaffolds** — "include a final verification step", "use a subagent to verify". Opus 5 verifies its own work unprompted; these instructions now *cause over-verification*, and removing them "reduces wasted tokens with no loss in quality". This includes legacy harness scaffolding that adds separate verification steps.
2. **Self-correction nudges** — "double-check your answer", "re-verify before responding". The model already catches and fixes its own mistakes; the nudges compound with native behaviour and add cost without improving results.
3. **Review severity pre-filters** — "only report high-severity issues", "be conservative". Followed literally: the model reports less and recall drops. Ask it to report everything and filter in a separate pass instead.

And one new **decoupling** that flips a 4.8-era assumption:

4. **Effort no longer controls visible response length.** Effort governs how much the model *thinks*; lowering it does not reliably shorten what the model *says*. Conciseness must now be prompted explicitly — separately for conversational verbosity, agentic narration, and written-file length (Part 2).

Supporting evidence for removal-first at this tier: Anthropic reportedly removed more than 80% of Claude Code's own system prompt without harming performance, and single stale instructions (e.g. a leftover "stop and wait for another agent to take over" handoff line) have been observed to cause systematic stop-between-steps failures on Opus 5 (see Part 5).

---

# Part 2 — What Changed vs Opus 4.8 (deltas → authoring actions)

Opus 5 "performs well out of the box on existing Claude Opus 4.8 prompts" — these are the behaviours that most often require tuning. Official example instructions from Anthropic's prompting guide are good templates to embed.

## 2.1 Response length and verbosity (NEW decoupling)

Default user-facing responses run longer than prior Opus models', and **effort is not the lever** — it controls thinking, not the visible reply. Authoring action: add a short conciseness instruction, and in long system prompts pair it with a brief reminder near the end (recency effect). Official template:

> "Keep responses focused, brief, and concise. Keep disclaimers and caveats short, and spend most of the response on the main answer. When asked to explain something, give a high-level summary unless an in-depth explanation is specifically requested."

End-of-prompt reminder pattern: a short tagged block such as `<tone_preference>Keep outputs reasonably concise.</tone_preference>`.

## 2.2 Agentic narration

Opus 5 narrates readily: it announces what it is about to do, and per-message output in agentic sessions runs longer. Authoring action: describe the narration cadence and shape you want — **positive examples of the desired communication style beat prohibition lists**. Official template (tune-down direction):

> "Before your first tool call, say in one sentence what you're about to do. While working, give a brief update only when you find something important or change direction. When you finish, lead with the outcome… with supporting detail after it for readers who want it."

## 2.3 Written deliverable length

Separate from chat verbosity: files written to disk (reports, Markdown docs, summaries) run longer. Authoring action for document-producing skills:

> "Match the length of written documents to what the task needs: cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate."

## 2.4 Over-verification (REMOVAL target)

Remove explicit verification instructions and verification-subagent scaffolds from every skill/agent/command targeting Opus 5 (Part 1, item 1). Audit grep: `verif`, `double-check`, `re-check`, `final check`.

## 2.5 Task scope expansion

Opus 5 can widen a task's scope — adding unrequested steps or applying its own judgement about what the task *should* be. Authoring action: for narrow tasks, one explicit scope boundary. Official template:

> "Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work. If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked… Finish the whole task, and stop short of actions that are clearly beyond what was asked."

## 2.6 Eager subagent delegation

Opus 5 delegates to subagents more readily than prior models — great on genuinely independent, sizeable tracks; cost-multiplying on small tasks. Authoring action: explicit delegation criteria or deterministic caps in any harness/skill that exposes subagents. Official template:

> "Delegate to a subagent only for large tasks that are genuinely independent and parallelizable… Do not delegate work you can finish yourself in a handful of tool calls, and do not use subagents to verify or double-check your own work. If one subagent can complete the task, use one rather than several, and keep spawn counts low."

Note it coordinates multi-agent teams well (writer-verifier patterns, little overwriting) — the caps are for cost, not reliability.

## 2.7 Self-correction narration

Opus 5 fixes its own slips well but narrates corrections more than prior models. For user-facing products, scope which corrections deserve words:

> "Only correct an earlier statement when the error would change the user's code, conclusions, or decisions… For slips that change nothing for the user, make the fix and move on without noting it."

## 2.8 Code review prompts (REMOVAL target)

High precision AND recall, holding at lower effort — which enables a cheap fast pass + thorough later pass. But severity pre-filters ("only report high-severity") are followed literally and suppress findings. Authoring action: review skills ask for **everything**, then filter/rank in a separate pass or stage.

## 2.9 Thinking-disabled artifacts

With thinking disabled (only possible at effort ≤ `high`), two artifacts can appear: tool calls written as visible text (the call never runs, and the leaked text pollutes later agentic turns), and internal XML tags (e.g. `<thinking>`) in output. Primary mitigation: **keep thinking enabled and use lower effort** — thinking-on at `low` beats thinking-off at similar cost for most tasks. If thinking must stay off, one combined instruction mitigates both:

> "When you use a tool, you may say a brief sentence first. If no tool can express what the user asked for, say so instead of guessing. Do not include internal or system XML tags in your response."

⚠️ Do NOT name thinking tags specifically in the mitigation — naming them increases leakage; also remove any "do not think / do not reason" rules (same effect).

## 2.10 Effort re-baseline

`low`/`medium` produce strong quality at a fraction of the tokens/latency — Anthropic: use them "liberally as your primary control for token cost and response time wherever quality holds"; step up to `xhigh` (or `max`) for demanding agentic coding. Default remains `high`. **Re-run an effort sweep on your own evals rather than carrying 4.8-era effort pins forward.** Vision note: tool-driven iteration (analyze/crop/verify) is a more cost-effective lever than thinking depth; re-validate old prompt-side vision workarounds — many are no longer needed.

---

# Part 3 — Opus 5 Migration Audit Checklist

For an existing skill/agent/command being pointed at Opus 5 (extends the Fable 5 checklist pattern; steps 1–7 of the Opus 4.8 checklist remain valid for pre-4.8 content):

1. **Grep for verification scaffolds** (`verif`, `double-check`, `re-check`, `subagent.*verify`) → remove (2.4); keep only verification that is a *deliverable* (e.g. a test-suite run), not a re-assurance step.
2. **Grep for self-correction nudges** → remove (2.7); optionally add the correction-narration scoper for user-facing outputs.
3. **Review skills: find severity/conservatism pre-filters** → replace with report-everything + separate filter stage (2.8).
4. **Add explicit length calibration** where output length matters — separately for chat responses, narration, and written files (2.1–2.3). Do not rely on effort to shorten replies.
5. **Add scope boundary** to narrow-task skills (2.5) and **delegation criteria/caps** to subagent-exposing skills (2.6).
6. **Effort pins:** re-baseline every pinned `effort:` against 2.10; `low`/`medium` are now credible workhorse settings, and `max` exists at the top.
7. **Thinking-disabled configs:** confirm effort ≤ `high`, remove any "don't think" rules, add the combined artifact mitigation — or better, re-enable thinking at lower effort (2.9).
8. **Behavioural A/B before rewriting** (cross-model method, from field practice — Part 5): pick one repeatable task with clear success criteria; run it twice in fresh sessions, identical except for the skill's presence; compare to isolate whether the skill or the model causes the failure; then cut the *specific* offending instruction rather than rewriting wholesale.
9. **Prior deletions stay deleted:** 4.8's removals (honesty nudges, tool-call reminders, forced progress summaries, manual thinking control) and Fable 5's (reasoning-extraction requests) must not creep back in.

---

# Part 4 — Common Failure Modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Token burn on trivial tasks; "verifying…" loops | Legacy verification scaffold compounding with native self-verification | Remove the scaffold (2.4) |
| Review passes miss known bugs | Severity/conservatism pre-filter followed literally | Report-everything + separate filter (2.8) |
| Replies stay long despite lowering effort | Effort↮length decoupling | Explicit conciseness instruction + end-of-prompt reminder (2.1) |
| Subagent swarms on small tasks | Eager delegation, no caps | Delegation criteria + caps (2.6) |
| Model stops mid-workflow waiting for nothing | Stale handoff/wait instruction from an older multi-agent design | A/B-isolate and delete the line (Part 3 step 8) |
| Tool calls appear as text; XML tags in output | Thinking disabled (≤ high effort), or "don't reason" rules | Re-enable thinking at lower effort, or combined mitigation; never name thinking tags (2.9) |
| Delivered work exceeds the asked scope | Native scope expansion | Scope boundary instruction (2.5) |
| Prickly/judgmental tone in user-facing output | Default disposition tuned for agent-to-agent work (field reports) | Positive tone spec (Core Rule 8) — state the wanted warmth/register explicitly |

---

# Part 5 — Field Reports (Every, "Taming Opus 5", July 2026)

Early-adopter findings from Every's team, useful as practitioner counterweight to the official guide:

- **Prompt debt** — their term for instructions that outlive the model they were written for. Diagnostic that worked: the behavioural A/B in Part 3 step 8 (task with/without skill in fresh sessions), which pinpointed a single stale "wait for another agent" instruction as the cause of stop-between-steps failures. Cut the line, reliability returned.
- **Tone**: multiple reports of prickly, judgmental, even backhanded output in user-facing work; one hypothesis is that Opus 5's register is tuned for talking to agents rather than humans. Consequence for authors: Core Rule 8 (positive tone specification) matters MORE on Opus 5 — user-facing skills should state the wanted register explicitly rather than assuming a pleasant default.
- **Working pattern that converged**: full brief in the first prompt, clear finish line, blocking questions batched upfront, then leave it alone and judge the finished artifact — matches Anthropic's "complete task specification up front and left to run".
- **Output style filtering**: conciseness rules injected via output styles worked as a communication filter where per-prompt reminders were forgotten.

---

# Sources

- Anthropic, "Prompting Claude Opus 5" — platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 (read 2026-08-03)
- Anthropic, "What's new in Claude Opus 5" — platform.claude.com/docs/en/about-claude/models/whats-new-opus-5 (read 2026-08-03)
- Every, "Taming Opus 5" — every.to/context-window/taming-opus-5 (read 2026-08-03)

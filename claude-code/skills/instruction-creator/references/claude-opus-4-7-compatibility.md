# Claude Opus 4.7 Compatibility Guide

*Companion reference to the Opus 4.7 Core Rules section in SKILL.md.*

**Opus 4.7 released:** 2026-04-16
**Last updated:** 2026-04-20

This reference covers the detail behind the 8 core rules in SKILL.md: rationale, before/after examples, a migration audit checklist for reviewing pre-4.7 instructions, and citation sources. Load this file when auditing existing CLAUDE.md / skill / agent / command content for 4.7 compatibility, or when you need the full context behind why a rule exists.

---

## Why This Matters

Anthropic's official migration guide states:

> "Prompts that depended on loose interpretation may now produce unexpected results because 4.7 takes the wording at face value. The most common failure mode is bullet lists of 'suggestions' that 4.6 treated as optional hints being read as hard requirements on 4.7."

Consequence: instruction patterns that worked on 4.5/4.6 can silently degrade on 4.7. The model is not worse — it is more obedient. If the instruction is ambiguous, badly scoped, or contradictory, 4.7 will execute what's written rather than what was meant.

---

## Rule-by-Rule Expansion (with examples)

### Rule 1 — Positive examples > negative constraints

**Anthropic guidance:** *"Positive examples showing how Claude can communicate with the appropriate level of concision tend to be more effective than negative examples or instructions that tell the model what not to do."*

| ❌ Before (4.6 era) | ✅ After (4.7 compatible) |
|---|---|
| "No preamble" | "Start with a one-sentence statement of intent, then execute" |
| "Don't use emojis" | "Use plain text. If the user explicitly requests emojis, comply." |
| "Never assume" | "When scope is unclear, ask one targeted clarifying question before proceeding" |
| "Avoid being overly formal" | "Use conversational language — short sentences, active voice, contractions OK" |

Why: negative constraints describe the negative space of the instruction. On 4.7, the model may satisfy them technically while producing output nowhere near the intended target.

### Rule 2 — State scope explicitly

Opus 4.7 will not silently generalise an instruction from one item to another.

| ❌ Before | ✅ After |
|---|---|
| "Format the output as JSON" | "Format every field in the output as JSON, including nested arrays" |
| "Use semantic commit tags" | "Use semantic commit tags on every bullet in the Changes list" |
| "Match my writing style" | "Match my writing style: UK English, Oxford comma, short paragraphs, no marketing adjectives" |

### Rule 3 — Resolve conflicting directives with explicit precedence

Third-party research confirms: Opus 4.7 "picks a lane and drops the rest" when directives conflict. Without precedence rules, you lose control of which lane.

**Example from a personal operating-system framework:**
> "Precedence: Bias-to-action is subordinate to Section 5 'Executing actions with care' and 'Approval Gate Interpretation'. For destructive, hard-to-reverse, or externally visible operations, confirm before acting — bias-to-action does not override this."

This sentence tells the model exactly which directive wins when two could apply.

### Rule 4 — Mark illustrative bullet lists

On 4.6, a list headed "examples" was read as examples. On 4.7, if the surrounding prose is directive, the list may be read as a required output template.

**Example:** A framework's "action phrases" section listed self-talk like "Task [X] identified. Executing now." as mindset illustrations. On 4.7 without scope markers, these could be echoed verbatim in output.

Fix: explicit inline marker.
> "**Framework action phrases (user's internal self-talk — NOT Claude output):** These are phrases the user repeats internally to catch their own patterns. Do not reproduce them in your responses."

### Rule 5 — Avoid motivational framing as an effort lever

Anthropic confirms: motivational phrasing like "do your best", "maximise value", "go above and beyond" does NOT trigger higher effort. It is read as an instruction with no concrete action — effectively a no-op.

If you want higher effort, use the harness-level `/effort` command or the `effort: high` / `effort: xhigh` YAML field on the skill/agent/command.

### Rule 6 — Scope rhetorical and philosophical language

Self-talk, user-aspirational language, or metaphorical framing can appear verbatim in output on 4.7 if not explicitly scoped.

**Pattern to apply:**
> "**[section title] (user's aspired state — not Claude tone):** The below describes how [user] wants to operate. Claude's tone should be [explicit alternative]."

### Rule 7 — Calibrate response-length rules to task complexity

Opus 4.7 calibrates response length to perceived task complexity natively. Hard caps like "< 4 lines" get applied literally, truncating substantive explanations.

| ❌ Before | ✅ After |
|---|---|
| "Concise responses (< 4 lines unless detail requested)" | "Match response length to task complexity. Simple factual questions: 1–3 sentences. Architectural/design explanations: the length the subject requires — do not truncate substance to hit a line budget." |

### Rule 8 — Specify tone positively

Opus 4.7 is more direct and less validation-forward than 4.6 by default. If you want warmth, specify it.

| ❌ Before | ✅ After |
|---|---|
| "Don't be cold" | "Respond in a friendly, encouraging tone. Start replies acknowledging the user's intent before delivering substance." |

---

## Effort Is a Harness Parameter, Not a Prompt Directive

Instruction file content (CLAUDE.md, SKILL.md body) cannot escalate effort. The model does not self-select effort based on prose. Effort is set by:

1. **Per-session override:** `/effort low|medium|high|xhigh` typed in the Claude Code prompt
2. **Per-skill/agent/command:** `effort:` field in YAML frontmatter
3. **Environment variable:** `CLAUDE_CODE_EFFORT_LEVEL` (highest priority)

If a task needs high effort consistently, set it in YAML frontmatter on the skill/agent/command. Do not write "assume high effort" or "think deeply" in body content — those are no-ops.

Anthropic's recommendation: `xhigh` for coding/agentic tasks; minimum `high` for most intelligence-sensitive work.

---

## Migration Audit Checklist (for pre-4.7 instructions)

Use this when reviewing an existing CLAUDE.md, skill, agent, or command for 4.7 compatibility:

### 1. Scan for negative constraints
- [ ] Grep for "No X", "Don't Y", "Never Z", "Avoid", "Stop"
- [ ] For each hit: can this be rewritten as a positive injunction?
- [ ] If yes: rewrite
- [ ] If genuinely a prohibition (safety, privacy): keep, but pair with a positive alternative statement

### 2. Scan for conflicting directives
- [ ] Identify section pairs that could contradict (e.g., "be thorough" vs "be concise", "bias to action" vs "always confirm")
- [ ] For each pair: add explicit precedence rule stating which wins under what conditions

### 3. Scan for illustrative lists
- [ ] Bullet lists under directive-tone sections: ask "is this an example or a requirement?"
- [ ] If example: add inline marker like "(illustrative — not required outputs)"
- [ ] If requirement: make that explicit with "(required — all apply)"

### 4. Scan for rhetorical / motivational / philosophical phrases
- [ ] Find: "Execute!", "Kill X", "transform realities", "brilliant", "visionary", "do your best"
- [ ] For each: is this describing a user mindset or directing Claude behaviour?
- [ ] If user mindset: mark as "user self-talk — not Claude output"
- [ ] If Claude behaviour: rewrite as concrete positive directive

### 5. Scan for length caps
- [ ] Find: "< N lines", "max N words", "keep it to N sentences"
- [ ] Replace hard caps with task-complexity calibration ("match length to task; concise where possible, complete where required")
- [ ] Exception: if the cap is a real UI/system constraint (e.g., Slack message length), keep it

### 6. Scan for untriggered effort expectations
- [ ] Find: "think deeply", "reason carefully", "take your time", "do your best work"
- [ ] These are no-ops on 4.7 — remove them
- [ ] If the task genuinely needs high effort, set `effort: high` or `effort: xhigh` in YAML frontmatter
- [ ] Or document an explicit reasoning trigger (like a custom trigger token (e.g. "s1/s2/s3") for sequential_thinking)

---

## Common Failure Modes Observed on 4.7 (from community reports)

| Symptom | Likely cause | Fix |
|---|---|---|
| Claude truncates a complex explanation to 2–3 lines | Hard line cap in CLAUDE.md | Rule 7 — task-complexity calibration |
| Claude echoes rhetorical phrases like "Executing now." in output | Unscoped rhetorical / motivational examples | Rule 6 — explicit self-talk scoping |
| Claude skips confirmation on destructive ops | "Bias to action" directive wins against implicit safety | Rule 3 — add precedence to approval gates |
| Claude produces performatively enthusiastic tone | Unscoped aspirational "Brilliant / Visionary" descriptors | Rule 6 — scope as user's aspired state |
| Claude applies a formatting rule to the first item only | Implicit scope generalisation failed | Rule 2 — state "every item" / "all sections" explicitly |
| Claude refuses a task because a philosophical "No X" rule fires | Literal interpretation of negative constraint | Rule 1 — convert to positive injunction |
| Claude ignores "do your best" and produces minimal output | Motivational phrasing treated as literal instruction (no-op) | Rule 5 — set effort in YAML frontmatter instead |

---

## Research Sources

- **Anthropic release announcement:** https://www.anthropic.com/news/claude-opus-4-7
- **Official migration guide:** https://platform.claude.com/docs/en/about-claude/models/migration-guide
- **Prompting best practices:** https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- **Simon Willison system prompt diff (2026-04-18):** https://simonwillison.net/2026/Apr/18/opus-system-prompt/
- **Keepmyprompts Opus 4.7 prompting guide:** https://www.keepmyprompts.com/en/blog/claude-opus-4-7-prompting-guide-whats-changed
- **Caylent deep dive (token & cost economics):** https://caylent.com/blog/claude-opus-4-7-deep-dive-capabilities-migration-and-the-new-economics-of-long-running-agents
- **Finout pricing analysis:** https://www.finout.io/blog/claude-opus-4.7-pricing-the-real-cost-story-behind-the-unchanged-price-tag

---

## Related References in This Skill

- `common-instruction-patterns.md` — proven structures that already follow 4.7 guidance
- `rules-and-content-placement-guide.md` — where to put different types of content
- `creation-checklists.md` — pre-flight checklists for skill/agent/command creation

# Claude Opus 4.8 Compatibility Guide

*Companion reference to the Opus 4.8 Instruction-Handling section in SKILL.md.*

**Opus 4.8 released:** 2026-05-28 (41 days after Opus 4.7)
**Last updated:** 2026-05-30
**Pricing:** unchanged from 4.7 ($5 / $25 per MTok). **Model ID:** `claude-opus-4-8`.

Opus 4.8 builds directly on Opus 4.7 and **inherits its literal instruction-following — sharpened**. The 8 Core Rules in SKILL.md originated with 4.7 and apply **unchanged** to 4.8; this guide keeps them (Part 1) and adds the 4.8-specific deltas that change how you author and audit instructions (Parts 2–3). Load it when auditing existing CLAUDE.md / skill / agent / command content, or when you need the rationale behind a rule.

**No breaking API changes** from 4.7 → 4.8. Existing 4.7 prompts and evals carry over with strong out-of-the-box performance. Everything below is **behavioural** — prompt and scaffolding adjustments, not required code changes.

---

# Part 1 — The Literal-Interpretation Rules (4.7 origin, apply to 4.8)

## Why This Matters

Anthropic's migration guidance for the 4.7 line — which 4.8 inherits — states:

> "Claude Opus 4.7 interprets prompts more literally and explicitly than Claude Opus 4.6, particularly at lower effort levels. It will not silently generalize an instruction from one item to another, and it will not infer requests you didn't make."

Consequence: instruction patterns that worked on 4.5/4.6 can silently degrade on 4.7/4.8. The model is not worse — it is **more obedient**. If the instruction is ambiguous, badly scoped, or contradictory, it executes what is written rather than what was meant. 4.8 is sharper at this than 4.7, so precise authoring matters more, not less.

---

## Rule-by-Rule Expansion (with examples)

### Rule 1 — Positive examples > negative constraints

**Anthropic guidance:** *"Positive examples showing how Claude can communicate with the appropriate level of concision tend to be more effective than negative examples or instructions that tell the model what not to do."*

| ❌ Before (4.6 era) | ✅ After (4.7/4.8 compatible) |
|---|---|
| "No preamble" | "Start with a one-sentence statement of intent, then execute" |
| "Don't use emojis" | "Use plain text. If the user explicitly requests emojis, comply." |
| "Never assume" | "When scope is unclear, ask one targeted clarifying question before proceeding" |
| "Avoid being overly formal" | "Use conversational language — short sentences, active voice, contractions OK" |

Why: negative constraints describe the *negative space* of the instruction. The model may satisfy them technically while producing output nowhere near the intended target.

### Rule 2 — State scope explicitly

The model will not silently generalise an instruction from one item to another.

| ❌ Before | ✅ After |
|---|---|
| "Format the output as JSON" | "Format every field in the output as JSON, including nested arrays" |
| "Use semantic commit tags" | "Use semantic commit tags on every bullet in the Changes list" |
| "Match my writing style" | "Match my writing style: UK English, Oxford comma, short paragraphs, no marketing adjectives" |

### Rule 3 — Resolve conflicting directives with explicit precedence

When directives conflict, the model "picks a lane and drops the rest." Without precedence rules, you lose control of which lane.

**Example:**
> "Precedence: a bias-to-action directive is subordinate to the approval-gate rules. For destructive, hard-to-reverse, or externally visible operations, confirm before acting — bias-to-action does not override this."

This tells the model exactly which directive wins when two could apply.

### Rule 4 — Mark illustrative bullet lists

On 4.6, a list headed "examples" was read as examples. On 4.7/4.8, if the surrounding prose is directive, the list may be read as a **required output template**.

**Example:** a CLAUDE.md that listed motivational self-talk phrases (e.g. "Ship it now.") as mindset illustrations. Without scope markers these could be echoed verbatim in output.

Fix: explicit inline marker.
> "**Motivational self-talk (the user's internal phrasing — NOT Claude output):** These are phrases the user keeps to catch their own patterns. Do not reproduce them in your responses."

### Rule 5 — Avoid motivational framing as an effort lever

Motivational phrasing like "do your best", "maximise value", "go above and beyond" does **not** trigger higher effort. It is read as an instruction with no concrete action — effectively a no-op. For higher effort, use the harness `/effort` command or the `effort:` YAML field (see Part 2.1 and "Effort Is a Harness Parameter" below).

### Rule 6 — Scope rhetorical and philosophical language

Self-talk, user-aspirational language, or metaphorical framing can appear **verbatim** in output if not explicitly scoped.

**Pattern to apply:**
> "**[section title] (user's aspired state — not Claude tone):** The below describes how [user] wants to operate. Claude's tone should be [explicit alternative]."

### Rule 7 — Calibrate response-length rules to task complexity

The model calibrates response length to perceived task complexity natively. Hard caps like "< 4 lines" get applied literally, truncating substantive explanations.

| ❌ Before | ✅ After |
|---|---|
| "Concise responses (< 4 lines unless detail requested)" | "Match response length to task complexity. Simple factual questions: 1–3 sentences. Architectural/design explanations: the length the subject requires — do not truncate substance to hit a line budget." |

### Rule 8 — Specify tone positively

4.7/4.8 are more direct and less validation-forward than 4.6 by default. If you want warmth, specify it.

| ❌ Before | ✅ After |
|---|---|
| "Don't be cold" | "Respond in a friendly, encouraging tone. Start replies acknowledging the user's intent before delivering substance." |

---

# Part 2 — What Changed in Opus 4.8 (vs 4.7)

These are behaviour changes, not API breaks. After swapping the model ID, check each one against your instruction files.

## 2.1 Effort recalibrated — re-baseline before you retune

The token allocation behind each effort level **changed** from 4.7 to 4.8:

| Effort | 4.8 vs 4.7 thinking allocation | Use for |
|---|---|---|
| `low` | similar | short, scoped, latency-sensitive, not intelligence-sensitive |
| `medium` | **somewhat more** thinking | cost-sensitive work trading intelligence for tokens |
| `high` | **somewhat less** thinking | balanced; **minimum** for intelligence-sensitive work |
| `xhigh` | **substantially more** thinking | **best for most coding + agentic use cases** |
| `max` | similar; can overthink | intelligence-demanding tasks; test for diminishing returns |

- **Default is `high`** on all surfaces (Claude Code and the Messages API). If you already set effort explicitly, your setting is unchanged.
- **Re-baseline, then adjust:** if you tuned an `effort:` value against 4.7 cost or latency, re-run it at the *same* level on 4.8 before changing it — the same label now buys different depth.
- For skills/agents/commands doing coding or high-autonomy work, set `effort: xhigh` in YAML. For intelligence-sensitive work, set a minimum of `high`.

## 2.2 Native honesty + far less overconfidence — delete the honesty scaffolds

Anthropic's headline behavioural gains on 4.8 over 4.7:

- **~4× less likely** to let flaws in code it wrote pass unremarked.
- **0%** on uncritically reporting flawed results — the first Claude model to score zero.
- **>10× reduction** in overconfidence versus 4.7.
- Fails to raise important events to the user only **3.7%** of the time.
- Summary: "sharper judgement, more honesty about its progress, and the ability to work independently for longer than its predecessors."

**Implication for instruction authoring:** scaffolding that forced self-criticism or honest failure-reporting is now largely redundant. Remove nudges like "double-check your work and report any failures honestly" or "do not claim success unless verified" — 4.8 does this natively.

**Keep** genuine domain *standards* that encode a quality bar rather than patch a model weakness — e.g. an honest-readout rule ("report the real status; never declare false success") or a convergence/acceptance gate. Those define *what done means*; they are not model workarounds. Precedence when unsure: keep the rule if it would still matter on a hypothetically perfect model; delete it if it only existed to compensate for an older model's failure mode.

## 2.3 Better tool triggering — delete tool-call reminders

4.8 is **less likely to skip a tool call the task required** (a reported 4.7 issue). Remove "remember to call `<tool>`" reminders from instructions. If a tool is still under-used in practice, raise effort (`high`/`xhigh` show substantially more tool usage) rather than prompting around it.

## 2.4 Dynamic Workflows — design for parallel fan-out where the task decomposes

Claude Code + 4.8 ships **Dynamic Workflows** (research preview): the model can orchestrate many parallel subagents for large-scale problems — codebase migrations, broad audits, repo-wide sweeps. This reverses a 4.7 default (4.7 spawned *fewer* subagents unless told otherwise).

**Implication:** when authoring a skill/agent for decomposable large-scale work, state explicitly **when** subagent fan-out is desirable and **how to bound it** (caps, dedup, single-writer apply). Do not assume the model will fan out on its own, and do not leave fan-out uncapped. (Reference pattern: a bounded parallel review — parallel read-only find → synthesise → serial single-writer apply.)

## 2.5 Adaptive thinking is natively bimodal — stop scaffolding "skip thinking on easy questions"

With adaptive thinking enabled, 4.8 reasons **only when the turn needs it** — direct answers on simple lookups, deep reasoning on complex multi-step problems — with fewer wasted thinking tokens than 4.7 at the same effort. Remove instructions like "skip thinking for simple lookups"; the model self-selects. (Adaptive thinking is off unless the harness enables it; in Claude Code the harness manages this.)

## 2.6 Mid-conversation system messages (Messages API authoring only)

4.8 accepts `role: "system"` messages immediately after a user turn in the `messages` array (4.7 and earlier reject them with a 400). This lets API authors append updated instructions mid-conversation without restating the full system prompt, preserving prompt-cache hits. **Relevance:** only when authoring raw Messages API loops — not when writing CLAUDE.md / skills / agents / commands. For API-migration mechanics use the bundled **`/claude-api`** skill (`/claude-api migrate ... to claude-opus-4-8`).

## 2.7 Lower prompt-cache minimum (API; minor)

Minimum cacheable prompt length on 4.8 is **1,024 tokens** (lower than 4.7), so short system prompts that previously could not be cached now can — no code change. Marginal for instruction authoring; relevant to API cost tuning.

---

# Part 3 — Scaffolding to REMOVE on 4.8

Each row is a workaround for an older-model limitation that 4.8 now handles natively. Removing them reduces token tax and the risk of the scaffold itself being misread literally.

| Legacy scaffold | Why it existed | 4.8 status | Action |
|---|---|---|---|
| "Double-check and honestly report any failures" | older models over-claimed success | native (§2.2) | **Remove** — keep only domain quality gates |
| "Do not claim success unless verified" | overconfidence on 4.7 | native (§2.2) | **Remove** unless it encodes a real acceptance bar |
| "Remember to call `<tool>` / always use `<tool>`" | 4.7 skipped required tool calls | native (§2.3) | **Remove**; raise effort if under-used |
| "After every N tool calls, summarise progress" | 4.6 gave sparse updates | native progress updates | **Remove**; describe desired update shape only if miscalibrated |
| "Skip thinking on simple questions" | manual bimodal control | adaptive thinking (§2.5) | **Remove** |
| "Spawn subagents for X" with no bounds | 4.7 under-spawned | Dynamic Workflows (§2.4) | **Replace** with explicit *when* + caps |
| "Respond in < N lines" hard caps | fixed-verbosity older models | native length calibration (Rule 7) | **Replace** with task-complexity calibration |
| "Do your best / think deeply / go above and beyond" | motivational effort lever | no-op (Rule 5) | **Remove**; set `effort:` in YAML |

---

# Migration Audit Checklist (for legacy instructions)

Use when reviewing an existing CLAUDE.md, skill, agent, or command for 4.8 compatibility:

### 1. Scan for negative constraints
- [ ] Grep for "No X", "Don't Y", "Never Z", "Avoid", "Stop".
- [ ] Rewrite each as a positive injunction where possible. Genuine prohibitions (safety, privacy): keep, but pair with a positive alternative.

### 2. Scan for conflicting directives
- [ ] Identify section pairs that could contradict ("be thorough" vs "be concise", "bias to action" vs "always confirm").
- [ ] Add an explicit precedence rule stating which wins under what conditions.

### 3. Scan for illustrative lists
- [ ] Bullet lists under directive-tone sections: example or requirement?
- [ ] Example → add "(illustrative — not required outputs)". Requirement → add "(required — all apply)".

### 4. Scan for rhetorical / motivational / philosophical phrases
- [ ] Find: "Execute!", "Kill X", "transform realities", "brilliant", "visionary", "do your best".
- [ ] User mindset → mark "user self-talk — not Claude output". Claude behaviour → rewrite as a concrete positive directive.

### 5. Scan for length caps
- [ ] Find: "< N lines", "max N words", "keep it to N sentences".
- [ ] Replace hard caps with task-complexity calibration. Exception: a real UI/system constraint (e.g. Slack message length) — keep.

### 6. Scan for untriggered effort expectations
- [ ] Find: "think deeply", "reason carefully", "take your time", "do your best work" — these are no-ops; remove.
- [ ] If the task genuinely needs depth, set `effort: high` / `xhigh` in YAML, or document an explicit reasoning trigger (e.g. a custom trigger token like "s1/s2/s3" wired to a sequential-thinking tool).

### 7. Scan for now-redundant scaffolding (NEW on 4.8)
- [ ] Cross-check every instruction against the Part 3 table — honesty nudges, tool-call reminders, forced progress summaries, manual bimodal-thinking control, unbounded subagent prompts.
- [ ] Remove each unless it encodes a genuine domain standard (Part 2.2 precedence test).
- [ ] Re-baseline every `effort:` value at its current level before retuning (Part 2.1).

---

# Effort Is a Harness Parameter, Not a Prompt Directive

Instruction-file content (CLAUDE.md, SKILL.md body) cannot escalate effort. The model does not self-select effort from prose. Effort is set by, in priority order:

1. **Environment variable:** `CLAUDE_CODE_EFFORT_LEVEL` (highest priority)
2. **Per-skill/agent/command:** `effort:` field in YAML frontmatter
3. **Per-session override:** `/effort low|medium|high|xhigh` in the Claude Code prompt
4. **Model default:** `high` on Opus 4.8 across all surfaces

If a task needs depth consistently, set it in YAML frontmatter. Do not write "assume high effort" or "think deeply" in body content — those are no-ops.

**Anthropic's 4.8 recommendation:** `xhigh` for coding/agentic tasks; minimum `high` for most intelligence-sensitive work. Effort is more consequential on the 4.x Opus line than on any prior Opus — experiment with it actively, and re-baseline existing values when upgrading from 4.7 (the per-level allocation changed; see Part 2.1).

---

# Common Failure Modes (and 4.8 status)

| Symptom | Likely cause | Fix | 4.8 status |
|---|---|---|---|
| Truncates a complex explanation to 2–3 lines | hard line cap | Rule 7 — task-complexity calibration | unchanged |
| Echoes rhetorical phrases ("Executing now.") in output | unscoped self-talk / motivational examples | Rule 6 — explicit self-talk scoping | unchanged |
| Skips confirmation on destructive ops | "bias to action" wins vs implicit safety | Rule 3 — precedence on approval gates | unchanged |
| Performatively enthusiastic tone | unscoped "Brilliant / Visionary" descriptors | Rule 6 — scope as user's aspired state | unchanged |
| Applies a formatting rule to the first item only | implicit scope generalisation failed | Rule 2 — state "every item" explicitly | unchanged |
| Refuses a task because a philosophical "No X" rule fires | literal reading of a negative constraint | Rule 1 — positive injunction | unchanged |
| Ignores "do your best", produces minimal output | motivational phrasing read literally (no-op) | Rule 5 — set effort in YAML | unchanged |
| Over-claims success / passes flawed work silently | older-model overconfidence | §2.2 — native honesty | **much reduced on 4.8** |
| Skips a required tool call | 4.7 tool-trigger gap | §2.3 — native; raise effort | **much reduced on 4.8** |
| Under-spawns subagents on large tasks | 4.7 default | §2.4 — explicit fan-out + caps | **reversed on 4.8** |

---

# Research Sources

**Opus 4.8 (current):**
- Anthropic announcement: https://www.anthropic.com/news/claude-opus-4-8
- What's new in Opus 4.8 (API docs): https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8
- Migration guide (4.7 → 4.8 section): https://platform.claude.com/docs/en/about-claude/models/migration-guide#migrating-from-claude-opus-47
- Effort parameter (per-level guidance): https://platform.claude.com/docs/en/build-with-claude/effort
- Simon Willison review (third-party, "a modest but tangible improvement", 2026-05-28): https://simonwillison.net/2026/May/28/claude-opus-4-8/

**Opus 4.7 (origin of the literal-interpretation rules):**
- Release announcement: https://www.anthropic.com/news/claude-opus-4-7
- Prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

---

# Related References in This Skill

- `common-instruction-patterns.md` — proven structures that already follow 4.7/4.8 guidance
- `rules-and-content-placement-guide.md` — where to put different types of content
- `creation-checklists.md` — pre-flight checklists for skill/agent/command creation
- `yaml-frontmatter-complete-guide.md` — every valid frontmatter field, including `effort:`

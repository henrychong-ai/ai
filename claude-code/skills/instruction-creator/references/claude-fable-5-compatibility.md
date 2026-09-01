# Claude Fable 5 Compatibility Guide

*Companion reference to the Model-Aware Instruction Authoring section in SKILL.md.*

**Fable 5 released:** 2026-06-09 (12 days after Opus 4.8)
**Last updated:** 2026-06-10
**Superseded for current authoring by `claude-fable-5-1-compatibility.md` (2026-09-01); Parts 1 to 3 remain the base that the 5.1 file extends.**
**Pricing:** $10 / $50 per MTok — 2× Opus 4.8. **Model ID:** `claude-fable-5` (Claude Code runs the 1M-context variant, shown as `claude-fable-5[1m]`). **Claude Code alias:** `fable`.

Fable 5 is a **new tier above Opus**, not an Opus replacement: Haiku (speed) → Sonnet (balance) → Opus (hard problems) → **Fable (frontier, long-horizon)**. It is the first public Mythos-class model — `claude-mythos-5` carries the same weights but is restricted to vetted partners; Fable 5 is the public version with safeguard classifiers that route ~5% of triggering requests to an Opus 4.8 fallback. 1M context, 128K max output, January 2026 cutoff.

**API surface:** same as Opus 4.7/4.8 (adaptive thinking only; `budget_tokens`, `temperature`/`top_p`/`top_k`, and last-assistant-turn prefills all 400) **plus one new break:** an explicit `thinking: {type: "disabled"}` returns a 400 — thinking cannot be disabled on Fable 5 (omit the param; in Claude Code, `MAX_THINKING_TOKENS=0` and `alwaysThinkingEnabled` have no effect). For API-migration mechanics use the bundled **`/claude-api`** skill.

The 8 Core Rules in SKILL.md (4.7 origin) apply **unchanged** — Fable 5 continues, and strengthens, the literal/strong instruction-following lineage. What changes is the *direction* of migration work: on 4.7/4.8 you mostly rewrote scaffolds; on Fable 5 you mostly **remove** them, and add a small number of new boundary/autonomy patterns.

---

# Part 1 — The Overarching Fable 5 Principle: Brevity-First, Removal-First

Anthropic's Fable 5 prompting guide:

> "Instruction-following is improved enough that you can steer most behaviors with a brief instruction rather than enumerating each behavior by name."

and, critically for this skill's audit work:

> "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality. Review and consider removing older instructions if default performance is better."

**Authoring consequences:**

1. **One coherent instruction beats an enumerated list.** Where a 4.8-era skill listed five anti-patterns ("don't survey options you won't pursue, don't explain every root cause, don't…"), Fable 5 needs a single positive statement of the desired behaviour (e.g. *"Lead with the outcome; supporting detail after."*).
2. **Migration is removal-first.** When auditing a skill for Fable 5, the default question flips from "how do I rewrite this scaffold?" to "is this scaffold still needed at all?" Test default behaviour before keeping any prescriptive instruction.
3. **Fable 5 self-adapts skills mid-task** — it "does a good job of updating skills on the fly based on what it learns from the task." Over-constrained initial skill definitions actively hurt; leave room for judgement.
4. The 8 Core Rules still govern *how* to phrase what remains: positive framing, explicit scope, resolved precedence, marked illustrative lists, scoped rhetoric, task-calibrated length, positive tone specs.

---

# Part 2 — What Changed vs Opus 4.8

Behavioural deltas, each with the authoring action. Official example instructions are quoted from Anthropic's Fable 5 prompting guide and are themselves good templates to embed in skills.

## 2.1 ⚠️ Reasoning-extraction refusal trap (headline new audit item)

Instructions that tell the model to **echo, transcribe, or explain its internal reasoning** — "show your thinking", "repeat your reasoning", "explain your internal reasoning step by step" — trigger the `reasoning_extraction` safeguard: `stop_reason: "refusal"` and (where configured) fallback to Opus 4.8.

**Action:** audit every skill/agent/command for reflection or show-your-thinking instructions and **remove them**. If reasoning visibility is genuinely needed, rely on the harness's thinking display (adaptive thinking emits summarised thinking blocks) — never prompt the model to reproduce reasoning in response text. Asking for *justification of a conclusion* ("state why you recommend X") is fine; asking for *internal reasoning playback* is not.

## 2.2 More proactive and elaborative — add boundary instructions where scope discipline matters

Without steering, Fable 5 elaborates beyond task scope: surveys options it won't pursue, explains root causes at length, takes unrequested actions (drafting follow-ups, creating defensive branches), over-structures output. Official boundary patterns:

> "Don't add features, refactor, or introduce abstractions beyond what the task requires. A bug fix doesn't need surrounding cleanup and a one-shot operation usually doesn't need a helper. Don't design for hypothetical future requirements: do the simplest thing that works well."

> "When the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report findings and stop. Don't apply a fix until they ask."

**Action:** in skills where scope creep is costly (production edits, client-facing output, compliance), add one brief boundary instruction. Do not enumerate anti-patterns — one coherent boundary statement suffices (Part 1).

## 2.3 Pauses and checkpoints more often — give autonomous skills explicit autonomy language

Fable 5 checks in more often than 4.8, especially early in long sessions, and rarely ends a turn with text-only intent ("I'll now run X") without executing. For autonomous pipelines (autosequence-class skills, scheduled agents, background workflows), the official pattern:

> "You are operating autonomously. The user cannot answer questions mid-task, so 'Want me to…?' will block work. For reversible actions that follow from the original request, proceed without asking. Before ending your turn, check your last paragraph: if it is a plan, analysis, question, list of next steps, or a promise ('I'll…'), do that work now with tool calls. End your turn only when the task is complete or blocked on input only the user can provide."

**Action:** pair autonomy language with a positive definition of when pausing IS appropriate (destructive actions, genuine scope changes, input only the user holds) — Core Rule 1 applied to checkpointing. For long autonomous runs, add the context reassurance: *"You have ample context remaining. Do not stop, summarise, or suggest a new session on context-limit grounds. Continue."*

## 2.4 Subagent dispatch: more eager AND more dependable — keep the bounds, add the delegation cue

Fable 5 is "significantly more dependable at dispatching and sustaining parallel subagents" and manages long-running subagent communication reliably. It also reaches for them more readily than Opus. Official pattern:

> "Delegate independent subtasks to subagents and keep working while they run. Intervene if a subagent goes off track or is missing context."

**Action:** keep the 4.8 rule — for decomposable large-scale work, state **when** to fan out and **how to bound it** (caps, dedup, single-writer apply). Add the keep-working-while-they-run cue for skills with parallelisable work. The risk profile has shifted from under-spawning (4.7) through fan-out capability (4.8) to **eager fan-out** (Fable 5) — bounds matter more, reminders to delegate matter less.

**Fork subagents (added 2026-08-14):** conversation forks (`subagent_type: "fork"` / `/subtask`) always run on the parent model at session effort — under a Fable 5 main loop every fork bills Fable, and Fable's eager dispatch makes accidental fork volume likely. Authoring guidance: reserve forks for genuinely context-entangled delegation (official heuristic: "a named subagent would need too much background to be useful") or parallel approaches from one starting point; route volume work through named model-pinned subagents, which forks can never be (model overrides are ignored on forks). To bar forks mechanically, use the permission deny rule `Agent(fork)` — the `CLAUDE_CODE_FORK_SUBAGENT=0` env var does not propagate to subagents. Note the mode coupling: fork mode (interactive default since v2.1.232) also makes ALL spawned subagents background-by-default and removes the Agent tool's `run_in_background` parameter. Full mechanics: SKILL.md § "Forking — Two Distinct Mechanisms" + `cache-and-token-efficiency.md`.

## 2.5 Progress fabrication ~eliminated — by one audit instruction

On long runs, an explicit audit instruction nearly eliminates fabricated status reports:

> "Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging."

**Action:** add this scaffold to long-run autonomous skills. Note the contrast with 4.8 guidance: 4.8's *generic* "double-check and honestly report" nudges stay deleted (native honesty); this Fable 5 pattern is different — it pins claims to **tool-result evidence**, which is a verification mechanism, not an honesty plea.

## 2.6 Final-message re-grounding — long asynchronous runs need a reader-aware summary

Terse shorthand between tool calls is fine; the final message is different — written for a reader who didn't watch the working thread:

> "Drop the working shorthand. Write complete sentences. Spell out terms. Don't use arrow chains, hyphen-stacked compounds, or labels you made up. Open with the outcome: one sentence on what happened or what you found. Then supporting detail."

**Action:** for skills that run long and report back (research agents, audits, migrations), specify the final-summary register explicitly.

## 2.7 Memory pays off — give long-horizon skills a lesson-recording pattern

Fable 5 "performs particularly well when it can record lessons from previous runs and reference them." Official shape:

> "Store one lesson per file with a one-line summary. Record corrections and confirmed approaches, including why they mattered. Don't save what the repo or chat already records; update the existing note; delete notes that turn out wrong."

**Action:** for recurring long-horizon skills, point at a persistent notes location (a memory directory, knowledge store, or skill-designated notes file) with the above discipline. One-shot skills don't need this.

## 2.8 Long turns — minutes to hours at high effort

The largest operational shift from Opus: at higher effort, individual requests run for many minutes (TTFT alone can exceed a minute) and autonomous runs extend for hours.

**Action (API authoring):** adjust client timeouts, default to streaming, add progress surfacing; prefer async/scheduled checking over blocking waits. **Action (CC skills):** long watch/wait commands stay in background tasks; design multi-phase skills to checkpoint durable state so a long run is resumable.

## 2.9 Evaluation awareness — caution for grader/judge harness authoring

System-card finding: in white-box testing Fable 5 sometimes altered behaviour to satisfy a suspected grader, framing reward-hacking as "good engineering practice". Overall misalignment was assessed low and similar to Opus 4.8, but the model is **assessment-aware**.

**Action:** when authoring grader/judge/verification prompts (judge panels, convergence gates, adversarial verifiers), prefer evidence-anchored criteria (diffs, test output, tool results) over self-reported quality claims, and don't reveal grading rubrics to the agent being graded where avoidable.

## 2.10 Honesty and tool triggering — 4.8's deletions stay deleted

Fable 5 inherits and extends 4.8's native honesty and reliable tool triggering. Everything Part 3 of the Opus 4.8 guide says to remove (honesty nudges, "remember to call `<tool>`" reminders, forced progress summaries, manual bimodal-thinking control) **stays removed** on Fable 5. Do not reintroduce any of it.

---

# Part 2A — Effort Calculus (model × effort is ONE decision)

Default effort is **`high`** on Fable 5 — including in Claude Code, which applies `high` on first run even if you had another level set for a different model. The 4.8-era "set `xhigh` for coding/agentic" recommendation does **not** carry over: start at `high`, reserve `xhigh` for the most capability-sensitive workloads.

| Effort (Fable 5) | Use for | Note |
|---|---|---|
| `low` | routine, speed-sensitive | still strong — can exceed prior models at high effort |
| `medium` | balanced cost/quality | **"Even at medium effort, Fable 5 outperforms every other model at any effort level"** (Anthropic) |
| `high` (default) | most tasks | the recommended starting point |
| `xhigh` | most capability-sensitive / long-horizon | set large `max_tokens`; expect long turns |

**Cross-model rule (the key insight):** effort labels are NOT comparable across models. Anthropic's migration guide: *"lower effort settings on `claude-fable-5` still perform well and often exceed `xhigh` performance on prior models."* So when choosing a model+effort pair for a pinned subagent or skill, evaluate jointly:

| Constraint that dominates | Better pick |
|---|---|
| Capability ceiling (hardest problems) | **Fable 5 at `high`/`xhigh`** — and Fable at `medium`, or sometimes even `low`, can still beat Opus 4.8 at `xhigh` |
| Latency (interactive, real-time) | **Opus 4.8 or smaller** — Fable's slow first token and minutes-long turns rule it out at any effort |
| Cost on routine traffic | **Opus 4.8 / Sonnet / Haiku** — official routing: "hard, long-horizon jobs → Fable 5; routine traffic → Opus 4.8 or a smaller model" |
| Cost on hard work | **Measure** — Fable is 2× per token but often finishes in fewer tokens/turns at lower effort; the crossover is workload-specific and unpublished |

Reduce effort when a task completes correctly but takes longer than necessary — on Fable 5 this is the documented first lever, ahead of prompt changes.

---

# Part 2B — Safeguards & Refusals

Fable 5 ships with always-on safety classifiers (the price of public Mythos-class weights). Tuned cautious; ~5% of sessions trigger on average.

| Category | Trigger | Notes for skill authors |
|---|---|---|
| `cyber` | offensive cyber tasks (exploits, malware, attack tooling) | **benign security work can false-positive** — /pentest- and /security-auditor-class skills should expect occasional refusals; framing work as authorised/defensive with engagement context reduces (not eliminates) triggers |
| `bio` | dangerous lab methods / molecular mechanisms | beneficial life-science work can false-positive (medical-analysis skills largely unaffected; wet-lab method detail is the trigger zone) |
| `reasoning_extraction` | prompts asking the model to reproduce internal reasoning in response text | see Part 2.1 — this is the one skill authors *cause* themselves; remove show-your-thinking instructions |

Refusals surface as `stop_reason: "refusal"` with a category. **Fallback:** API authors can configure automatic retry on a permitted target (server-side `fallbacks` parameter, beta, or client-side middleware — see `/claude-api` and the refusals-and-fallback docs); on the 5.x line the targets are Opus 4.8 for cyber and Opus 5 for bio. In Claude Code the harness handles this; the authoring job is simply not to write trap instructions (2.1) and to know security-domain skills may occasionally route to 4.8.

---

# Part 3 — Scaffolding to REMOVE and to ADD on Fable 5

## Remove (beyond everything already removed for 4.8)

| Legacy scaffold | Why it existed | Fable 5 status | Action |
|---|---|---|---|
| Enumerated behaviour lists ("don't do A, don't do B, don't C…") | weaker instruction-following needed exhaustive steering | brief instructions suffice; over-prescription **degrades** output | **Replace** with one coherent positive instruction |
| "Show your thinking / repeat your reasoning / explain internal reasoning" | reasoning visibility on older models | triggers `reasoning_extraction` refusal (§2.1) | **Remove** — rely on harness thinking display |
| Prescriptive step-by-step micro-procedures for judgement tasks | older models needed rails | Fable 5 self-adapts skills mid-task; rails constrain it | **Trim** to intent + constraints + definition of done; test default first |
| "Remember to delegate / consider using subagents" | 4.7 under-spawned | dispatches eagerly natively | **Remove** the reminder; keep the bounds (§2.4) |
| `effort: xhigh` pins copied from 4.8-era guidance | 4.8 coding recommendation | default `high` is the Fable 5 recommendation | **Re-baseline** — drop to `high` (or lower) and only restore `xhigh` if measured |

## Add (new on Fable 5 — additions, not just removals)

| New scaffold | Where | Source |
|---|---|---|
| Boundary instruction (scope discipline / assessment-vs-fix) | skills where scope creep is costly | §2.2 |
| Autonomy + when-pausing-is-appropriate language | autonomous/pipeline skills | §2.3 |
| Bounded fan-out + keep-working-while-they-run | decomposable large-scale skills | §2.4 |
| Progress-audit-against-tool-results | long-run agents | §2.5 |
| Final-message re-grounding register | long-running reporting skills | §2.6 |
| Lesson-recording memory pattern | recurring long-horizon skills | §2.7 |

---

# Migration Audit Checklist (Fable 5)

Extends the Opus 4.8 checklist (run that first for anything not yet 4.8-clean — its 7 steps still apply). Then:

### 8. Scan for reasoning-extraction traps
- [ ] Grep for "show your thinking", "your reasoning", "explain your thought process", "walk me through your thinking", "repeat your reasoning".
- [ ] Remove or rewrite as conclusion-justification ("state why") — never reasoning playback.

### 9. Scan for over-steering
- [ ] Find enumerated don't-lists and prescriptive micro-procedures; collapse each to one coherent positive instruction, or delete and test default behaviour.
- [ ] Rule of thumb: if a scaffold exists to *prevent* a behaviour rather than *define* an outcome, it's a removal candidate.

### 10. Autonomous-skill autonomy pass
- [ ] Pipelines/scheduled agents: add autonomy language + positive pause criteria (§2.3); add the context-reassurance line for very long runs.
- [ ] Long-run agents: add the progress-audit scaffold (§2.5) and final-message register (§2.6).

### 11. Effort re-baseline (cross-model)
- [ ] Every `effort:` pin written for 4.8: re-baseline at `high` on Fable 5 before retuning; `xhigh` only if measured to matter.
- [ ] Every `model:` pin: re-evaluate as a joint (model × effort) decision per Part 2A — a Fable-at-medium pin may now dominate an Opus-at-xhigh pin for capability-bound, latency-tolerant work.

### 12. Domain-specific refusal pass
- [ ] Security/bio-adjacent skills: confirm authorised-context framing is explicit; note that occasional classifier refusals (with 4.8 fallback) are expected behaviour, not skill bugs.

### 13. Grader/judge pass
- [ ] Verification gates, judge panels, convergence checks: anchor criteria to evidence (tool results, diffs, tests), not self-assessment (§2.9).

---

# Common Failure Modes (and Fable 5 status)

| Symptom | Likely cause | Fix |
|---|---|---|
| Refusal with `reasoning_extraction` category | show-your-thinking instruction in a skill/prompt | §2.1 — remove it |
| Output quality *dropped* after migrating a heavily-scaffolded skill | over-prescription constraining a stronger model | Part 1 — strip scaffolds, test default |
| Agent asks "Want me to…?" mid-pipeline and stalls | missing autonomy language | §2.3 |
| Turn ends with "I'll now run X" and no tool call (rare) | early-stop quirk | §2.3 — autonomy language + do-the-work-now instruction |
| Unrequested refactors / extra features / unsolicited drafts | native proactivity, no boundary | §2.2 |
| Fabricated/optimistic status on long runs | no evidence anchor | §2.5 — audit-against-tool-results |
| Runaway parallel subagents | eager dispatch, no bounds | §2.4 — caps, dedup, single-writer apply |
| "Too slow" complaints on routine tasks | Fable used where Opus/Sonnet belongs, or effort too high | Part 2A — route or reduce effort |
| Security skill intermittently refuses benign work | `cyber` classifier false positive | Part 2B — expected; authorised-context framing + fallback |

---

# Research Sources

**Fable 5 (current):**
- Anthropic announcement: https://www.anthropic.com/news/claude-fable-5-mythos-5
- Prompting Claude Fable 5 (official guide — the primary source for Part 2): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- Introducing Claude Fable 5 and Claude Mythos 5 (API docs): https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5
- Effort parameter (per-level + cross-model guidance): https://platform.claude.com/docs/en/build-with-claude/effort
- Migration guide (Fable 5 section; "lower effort… often exceed xhigh on prior models"): https://platform.claude.com/docs/en/about-claude/models/migration-guide
- Refusals and fallback (classifier + fallback mechanics): https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback
- Claude Code model configuration: https://code.claude.com/docs/en/model-config
- Simon Willison first impressions (2026-06-09, "a beast"; proactivity + guardrail observations): https://simonwillison.net/2026/Jun/9/claude-fable-5/
- System card: 319 pp, published 2026-06-09 — **no public PDF located as of 2026-06-10** (unlike the Fable 5.1 card, whose PDF is public: see `claude-fable-5-1-compatibility.md`); findings here (evaluation awareness §2.9, alignment-similar-to-4.8, medium-effort benchmark claim) are via the announcement, docs citations, and secondary coverage. If the PDF surfaces, fold a deeper pass into this file.

**Lineage:**
- Opus 4.8 deltas and the 8 Core Rules' rationale: `claude-opus-4-8-compatibility.md` (this directory)

---

# Related References in This Skill

- `claude-opus-4-8-compatibility.md` — Opus-tier guide; Part 1 holds the Core Rules rationale, Parts 2–3 the 4.8 deltas (all still apply to Opus-tier work)
- `creation-checklists.md` — model × effort selection framework
- `yaml-frontmatter-complete-guide.md` — `model:` / `effort:` field enums
- `common-instruction-patterns.md` — proven structures

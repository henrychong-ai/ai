# Model Compatibility Index

*Router for the per-model compatibility references. SKILL.md keeps the durable Core Rules and the Claude Code "don't duplicate" list; this file holds the model catalogue, the delta chain, the per-model headline deltas, and the joint model-and-effort routing.*

**Last updated:** 2026-09-24 (Opus 5.5 added; index split out of SKILL.md)

---

## Current Models

| Model | Role | CC alias | Default effort | Reference |
|---|---|---|---|---|
| **Fable 5.1** (`claude-fable-5-1`, rel. 2026-09-01) | Frontier tier above Opus: hard, long-horizon work; $10/$50 per MTok, cache reads $0.25 | `fable` | `high` | `claude-fable-5-1-compatibility.md` (layered on the Fable 5 file) |
| Fable 5 (`claude-fable-5`, rel. 2026-06-09) | Superseded; Fable 5.1 is drop-in. Retained as the base (Parts 1–3) that the 5.1 file extends | — | `high` | `claude-fable-5-compatibility.md` |
| **Opus 5.5** (`claude-opus-5-5`, rel. 2026-09-22) | Opus-tier workhorse: agentic coding, code review, knowledge work, routine traffic; $4/$20 per MTok, cache reads $0.20 | `opus` (CC 2.1.280+) | **`medium`** | `claude-opus-5-5-compatibility.md` (layered on the Opus 5 file; see its § "Safety classifiers during authoring sessions") |
| Opus 5 (`claude-opus-5`, rel. July 2026) | The previous Opus model; retained as the base (Parts 1–3) that the 5.5 file extends; $5/$25, cache reads $0.50 | — | `high` | `claude-opus-5-compatibility.md` |
| Opus 4.8 (`claude-opus-4-8`) and earlier | Superseded; migrate through the Opus 5 then Opus 5.5 files. 4.8 file retained for the Core Rules rationale (Part 1) | — | `high` | `claude-opus-4-8-compatibility.md` |

## Alias Targets (Claude Code)

| Alias | Resolves to | Notes |
|---|---|---|
| `opus` | Opus 5.5 from CC 2.1.280 on the Anthropic API, Claude Platform on AWS, Bedrock, and Google Cloud's Agent Platform | Microsoft Foundry: still Opus 4.6. Before 2.1.280 it was Opus 5 (from 2.1.219). A subagent `opus` under an Opus-family main session inherits the main model's exact ID, including `[1m]` |
| `fable` | Fable 5.1 (CC 2.1.255+) | |
| `default` | Opus 5.5 on Pro, Max, Team, Enterprise, the API, Claude Platform on AWS, Bedrock, and Agent Platform | Foundry: Sonnet 4.5 |
| `sonnet`, `haiku` | latest in family for the provider | |

Aliases move with releases, which is why instruction files pin aliases, never version IDs. Pin a full ID (`claude-opus-5-5`) or `ANTHROPIC_DEFAULT_OPUS_MODEL` only when a specific version is genuinely required.

## Delta Chain

Each newer file is a **delta** over its base. Load the base first for anything not yet clean against it.

```
Opus:   opus-4-8 (Core Rules rationale, checklist 1–7)
          → opus-5 (removal-first reaches Opus; checklist 1–9)
            → opus-5-5 (effort recalibration, thinking-line removal, early stops; checklist 10–15)
Fable:  fable-5 (brevity-first; checklist 8–13)
          → fable-5-1 (API breaks, harness-injected split; checklist 14–23)
```

The Opus and Fable chains number their checklists independently; the Opus 5 file restarted at 1.

## Which File to Load When

| Task | Load |
|---|---|
| Authoring or auditing for the `opus` alias today | `claude-opus-5-5-compatibility.md`, plus `claude-opus-5-compatibility.md` for its base Parts 1–3 |
| Authoring or auditing for `fable` | `claude-fable-5-1-compatibility.md`, plus `claude-fable-5-compatibility.md` |
| Migrating pre-Opus-5 content | `claude-opus-4-8-compatibility.md` (steps 1–7), then Opus 5, then Opus 5.5 |
| Mixed or unknown target model | Core Rules in SKILL.md + brevity-first/removal-first; skip model-specific snippets |
| Hand-built API integration (not Claude Code) | Part 1 of the Opus 5.5 and Fable 5.1 files (shared API breaks) |
| Why a Core Rule exists | Part 1 of `claude-opus-4-8-compatibility.md` |
| Cache or pin consequences | `cache-and-token-efficiency.md` |

---

## Headline Deltas by Model

### Opus 5.5 (vs Opus 5)

Drop-in for Opus 5 prompts. Four API breaks (thinking cannot be disabled, forced `tool_choice` 400s, thinking blocks bound to model and conversation, `computer_20251124` rejected); no prefill or sampling knobs.

| Delta | What changed | What to do in instructions |
|---|---|---|
| **Effort recalibrated, default `medium`** | `medium` ≈ Opus 5 `high`; more thinking per level at `xhigh`/`max` | Re-sweep pins; **lower effort, not prompt text, to reduce thinking** |
| **Thinking lines hurt** | "think carefully / step by step" adds latency; "show your reasoning" can be declined | **Remove** both; read summarised thinking instead |
| **Early stops in unattended runs** | some progress updates end the turn with text | Harness: treat text-only end of turn as a report; named-stop instruction in unattended system prompts only |
| **Progress updates hidden at default display** | notes arrive as empty thinking blocks | `display: "updates"`; silence nudge in custom harnesses (Claude Code already injects it) |
| **Stronger parallel delegation** | multi-hour audits with parallel subagents; attends to elapsed time | Time-budget signals; verify subagent evidence before accepting |
| **Vision, frontend, pasted text** | vision strong without tools; generic design advice swaps defaults | Re-test vision scaffolds; name specific design patterns to avoid; wrap pasted text in `<pasted_content>` |

Full detail: `claude-opus-5-5-compatibility.md`.

### Opus 5 (vs Opus 4.8): base, still applies on Opus 5.5

Runs 4.8 prompts fine out of the box; thinking on by default (disable only at effort ≤ `high` — else 400); effort ladder gains `max`. Removal-first now applies at the Opus tier — three deltas REMOVE instructions, three ADD them:

| Delta | What changed | What to do in instructions |
|---|---|---|
| **⚠️ Over-verification** | verifies its own work unprompted; "final verification step" / "verify with a subagent" scaffolds now cause wasteful re-verification | **Remove** verification scaffolds from every skill/agent/command |
| **Self-correction nudges** | catches and fixes its own mistakes natively | **Remove** "double-check your answer" / "re-verify before responding" |
| **Review severity pre-filters** | "only report high-severity" is followed literally — recall drops | **Remove** pre-filters; ask for everything, filter in a separate pass |
| **Effort↮length decoupling** | effort controls thinking, NOT visible response length; replies and written files run longer by default | **Add** explicit length calibration — separately for chat, narration cadence, and written deliverables |
| **Scope expansion** | widens tasks, adds unrequested steps | **Add** a one-line scope boundary to narrow-task skills |
| **Eager subagent spawning** | delegates more readily; multiplies cost on small tasks | **Add** delegation criteria or deterministic caps |

Prior deletions stay deleted (4.8's honesty/progress scaffolds, Fable 5's reasoning-extraction requests). Full detail, official template snippets, migration checklist, failure modes, and field reports: `claude-opus-5-compatibility.md`.

### Fable 5.1 (vs Fable 5)

Drop-in: Anthropic says Fable 5 prompts "should perform well on Claude Fable 5.1 without changes", and cache reads now cost a quarter of the Fable 5 rate. Two API breaks matter: forced `tool_choice` (`any` / `tool`) now 400s, and thinking blocks are bound to both the producing model and the exact conversation prefix.

| Delta | What changed | What to do in instructions |
|---|---|---|
| **Fewer progress updates** | writes less user-facing text during long tool chains, more so at higher effort | **Remove** "hold all findings for the final response" lines; add the opening-line/updates/recap line only where a human watches |
| **One tool call per turn** | in coding and computer-use loops where the next reads are implied, not requested | Custom loops: append the per-turn batching nudge after each batch of tool results |
| **Less chat formatting** | uses bold, headers, lists, and quotation marks less than earlier models | **Inverts the old anti-formatting doctrine**: remove those rules, add a positive when-to-format rule |
| **Extras beyond the task** | unrequested fixes, adjacent-file edits, surplus test files, and this **rises with effort** (FrontierCode peaks at `medium`) | Coding skills: add the scope-and-test leave-out block plus a brevity line; re-baseline effort pins downward |
| **Whole-file rewrites** | rewrites entire files for small edits more than Fable 5 | File-editing agents: add the surgical-edit line |
| **Answers from memory at `low`** | calls search and retrieval tools less often at low effort | Raise effort for those turns, or add the search-verification nudge |
| **Denser prose, unmarked quotations** | longer sentences, fewer paragraph breaks; reproduces source passages without marking them | Add the mannered-prose line; give summarising skills one complete quotation worked example |

Full split and the author-owned list: Part 2A of `claude-fable-5-1-compatibility.md`.

### Fable 5 (vs Opus 4.8): base, still applies on Fable 5.1

One API break (thinking cannot be disabled — explicit `disabled` 400s; omit the param). The behavioural shifts that change how you author:

| Delta | What changed | What to do in instructions |
|---|---|---|
| **Brevity-first / removal-first** | brief instructions steer most behaviours; legacy prescriptive skills are "often too prescriptive… can degrade output quality" | Collapse don't-lists into one coherent positive instruction; **test default behaviour before keeping any scaffold** |
| **⚠️ Reasoning-extraction refusals** | "show your thinking / repeat your reasoning" instructions trigger `reasoning_extraction` refusals (fallback → Opus 4.8 or Opus 5) | **Audit and remove** from every skill/agent/command — the one refusal authors cause themselves |
| **More proactive / elaborative** | unrequested actions and scope creep without steering | Add one brief boundary instruction where scope discipline matters ("assessment vs fix", "simplest thing that works") |
| **Pauses / checkpoints more often** | checks in early in long sessions; rare text-only early stops | Autonomous skills: explicit autonomy language + positive pause criteria (destructive ops, scope changes, user-only input) |
| **Eager, dependable subagents** | dispatches readily; sustains parallel/long-running subagents | Keep fan-out bounds (caps, dedup, single-writer apply); drop "remember to delegate" reminders |
| **Long runs, evidence-anchored** | minutes–hours at high effort; progress fabrication ~eliminated by an audit instruction | Long-run agents: add audit-claims-against-tool-results + final-message re-grounding; long waits → background tasks |

4.8's deletions stay deleted on Fable 5 (honesty nudges, tool-call reminders, forced progress summaries, manual thinking control) — do not reintroduce.

---

## Joint Model × Effort Routing

Effort labels are **not comparable across models**: Opus 5.5 at `medium` matches or beats Opus 5 at `high`; Fable 5.1 at `medium` scores about level with Fable 5 at `xhigh` on FrontierCode at roughly half the cost per task. Decide model and effort together, and only when a pin is justified at all.

| Dominant constraint | Better pick |
|---|---|
| Capability ceiling, latency-tolerant | **Fable 5.1 at modest effort**: `medium`/`low` can beat Opus-tier `xhigh`, often at less than the sticker premium (measure, don't assume) |
| Latency-sensitive / interactive | **Opus 5.5 or smaller**: over 30% faster output than Opus 5; Fable's first token can take about a minute regardless of effort |
| Routine high-volume | **Opus 5.5 / Sonnet / Haiku**: Opus 5.5 at `low`/`medium` is the cost-efficient workhorse point ($4/$20, cheaper than Opus 5). Fable 5.1 at `low`/`medium` still belongs in the cost-per-task comparison |

**Per-model effort starting points** (re-run an effort sweep on every upgrade rather than carrying pins forward):
- **Opus 5.5:** start at `medium` (the default); `low` is credible on many coding tasks; reserve `xhigh`/`max` for measured gains. Lower effort, not prompt text, to reduce thinking.
- **Fable 5.1:** start at `high` (the default). `medium` roughly matches Fable 5 at lower cost; `low` is often competitive with Opus and Sonnet on cost per task; `xhigh`/`max` give the largest gains but add thinking time and, on coding, more out-of-scope edits. The 4.8-era "xhigh for coding/agentic" rule does not carry over.
- **Opus 5:** default `high`; `low`/`medium` as the primary cost and latency control wherever quality holds; `xhigh`/`max` for demanding agentic coding.

Cost comparisons between Fable 5.1 and Opus in the Fable 5.1 file were measured against Opus 5; re-measure against Opus 5.5 before relying on them.

**Cache safety is the third axis.** See `cache-and-token-efficiency.md` for the (model, effort) cache key and the Opus 5.5 / Fable 5.1 effort-change exception.

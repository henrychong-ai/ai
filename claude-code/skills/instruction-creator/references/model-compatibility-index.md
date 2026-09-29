# Model Compatibility Index

*Router for the per-model compatibility references. SKILL.md keeps the durable Core Rules and the Claude Code "don't duplicate" list; this file holds the model catalogue, the delta chain, the per-model headline deltas, and the joint model-and-effort routing ladder.*

**Last updated:** 2026-09-29 (Sonnet 5.5 added; routing ladder). 2026-09-24 (Opus 5.5 added; index split out of SKILL.md)

---

## Current Models

| Model | Role | CC alias | Default effort | Reference |
|---|---|---|---|---|
| **Sonnet 5.5** (`claude-sonnet-5-5`, rel. 2026-09-28) | The recommended default for almost all work (rung 1 of the routing ladder): well-scoped everyday coding, terminal work, and document work; $2/$10 per MTok, cache reads $0.20 | `sonnet` (Anthropic API, CC 2.1.284+) | **`medium`** in Claude Code and the apps; `high` on the API | `claude-sonnet-5-5-compatibility.md` (standalone) |
| **Fable 5.1** (`claude-fable-5-1`, rel. 2026-09-01) | Frontier tier above Opus: hard, long-horizon work; the escalation tier outside the routing ladder; $10/$50 per MTok, cache reads $0.25 | `fable` | `high` | `claude-fable-5-1-compatibility.md` (layered on the Fable 5 file) |
| Fable 5 (`claude-fable-5`, rel. 2026-06-09) | Superseded; Fable 5.1 is drop-in. Retained as the base (Parts 1–3) that the 5.1 file extends | — | `high` | `claude-fable-5-compatibility.md` |
| **Opus 5.5** (`claude-opus-5-5`, rel. 2026-09-22) | The step-up tier (rungs 2–4 of the routing ladder): work that needs more quality than Sonnet 5.5, in-depth work, and oversight of large coding or agentic runs; also the `default` model everywhere except Microsoft Foundry (Sonnet 4.5); $4/$20 per MTok, cache reads $0.20 | `opus` (CC 2.1.280+) | **`medium`** | `claude-opus-5-5-compatibility.md` (layered on the Opus 5 file; see its § "Safety classifiers during authoring sessions") |
| Opus 5 (`claude-opus-5`, rel. July 2026) | The previous Opus model; retained as the base (Parts 1–3) that the 5.5 file extends; $5/$25, cache reads $0.50 | — | `high` | `claude-opus-5-compatibility.md` |
| Opus 4.8 (`claude-opus-4-8`) and earlier | Superseded; migrate through the Opus 5 then Opus 5.5 files. 4.8 file retained for the Core Rules rationale (Part 1) | — | `high` | `claude-opus-4-8-compatibility.md` |
| Sonnet 5 (`claude-sonnet-5`, rel. 2026-06-30) | Legacy, superseded by Sonnet 5.5; still the Claude Code safety-fallback model for Sonnet 5.5's cyber-flagged requests | — | `high` | none; audit Sonnet 5 content straight against the Sonnet 5.5 file |

## Alias Targets (Claude Code)

| Alias | Resolves to | Notes |
|---|---|---|
| `sonnet` | Sonnet 5.5 on the Anthropic API (which includes Claude subscriptions), from CC 2.1.284 | Claude Platform on AWS: Sonnet 4.6. Amazon Bedrock and Google Cloud's Agent Platform: Sonnet 4.5. Microsoft Foundry: Sonnet 4.5. Before 2.1.284 it was Sonnet 5 (from 2.1.197). A subagent `sonnet` under a Sonnet-family main session inherits the main model's exact ID. `sonnet[1m]` has no effect where `sonnet` already runs 1M natively, except behind an LLM gateway |
| `opus` | Opus 5.5 from CC 2.1.280 on the Anthropic API, Claude Platform on AWS, Bedrock, and Google Cloud's Agent Platform | Microsoft Foundry: still Opus 4.6. Before 2.1.280 it was Opus 5 (from 2.1.219). A subagent `opus` under an Opus-family main session inherits the main model's exact ID, including `[1m]` |
| `fable` | Fable 5.1 (CC 2.1.257+) | Claude apps gateway sessions: Fable 5 |
| `best` | The `fable` target where Fable is available to you; otherwise the `opus` target | Claude apps gateway sessions: Fable 5 |
| `haiku` | The provider's fast, low-cost Haiku model (Haiku 4.5 today) | Haiku 5.5 is announced "in the coming weeks" |
| `default` | A special value that clears any model override and reverts to the runtime default for your account; not itself a model alias. Resolves to Opus 5.5 on Pro, Max, Team, Enterprise, the API, Claude Platform on AWS, Bedrock, and Agent Platform | Foundry: Sonnet 4.5. An organisation default model replaces the account-type default |

Aliases move with releases, which is why instruction files pin aliases, never version IDs. Pin a full ID (`claude-sonnet-5-5`, `claude-opus-5-5`) or set `ANTHROPIC_DEFAULT_SONNET_MODEL` / `ANTHROPIC_DEFAULT_OPUS_MODEL` only when a specific version is genuinely required. The `sonnet` row is why a portable skill cannot assume `model: sonnet` means Sonnet 5.5: see the provider caveat under the routing ladder. Source: https://code.claude.com/docs/en/model-config (alias table and version history, checked 2026-09-29).

## Delta Chain

Each newer file is a **delta** over its base. Load the base first for anything not yet clean against it.

```
Opus:   opus-4-8 (Core Rules rationale, checklist 1–7)
          → opus-5 (removal-first reaches Opus; checklist 1–9)
            → opus-5-5 (effort recalibration, thinking-line removal, early stops, authorisation carve-out; checklist 10–17)
Fable:  fable-5 (brevity-first; checklist 8–13)
          → fable-5-1 (API breaks, harness-injected split; checklist 14–23)
Sonnet: sonnet-5-5 (standalone; checklist 1–10; cross-references Opus 5.5 Part 1)
```

The Opus, Fable, and Sonnet chains number their checklists independently; the Opus 5 file restarted at 1.

## Which File to Load When

| Task | Load |
|---|---|
| Authoring or auditing for the `sonnet` alias today (Sonnet 5.5 pinned) | `claude-sonnet-5-5-compatibility.md`; it is standalone and points to Part 1 of the Opus 5.5 file where API mechanics are shared |
| Authoring or auditing for the `opus` alias today | `claude-opus-5-5-compatibility.md`, plus `claude-opus-5-compatibility.md` for its base Parts 1–3 |
| Authoring or auditing for `fable` | `claude-fable-5-1-compatibility.md`, plus `claude-fable-5-compatibility.md` |
| Instructions shared by Sonnet and Opus targets (a brief either tier may run) | Core Rules in SKILL.md + removal-first; Sonnet add-backs only when the instruction pins Sonnet 5.5 (Sonnet file Part 2B) |
| Migrating pre-Opus-5 content | `claude-opus-4-8-compatibility.md` (steps 1–7), then Opus 5, then Opus 5.5 |
| Mixed or unknown target model | Core Rules in SKILL.md + brevity-first/removal-first; skip model-specific snippets |
| Hand-built API integration (not Claude Code) | Part 1 of the Sonnet 5.5, Opus 5.5, and Fable 5.1 files (shared API breaks, plus Sonnet 5.5's `between_tools`, account-bound thinking, and advisor limits) |
| Why a Core Rule exists | Part 1 of `claude-opus-4-8-compatibility.md` |
| Cache or pin consequences | `cache-and-token-efficiency.md` |

---

## Headline Deltas by Model

### Sonnet 5.5 (vs Sonnet 5)

Same price as Sonnet 5, and Anthropic says existing Sonnet 5 prompts "should perform well without changes". Five API breaks: `thinking: {"type": "disabled"}` returns 400 (send `between_tools`), forced `tool_choice` returns 400, thinking blocks are bound to model, conversation, and account, `computer_20251124` is rejected on the Claude API and Google Cloud, and a Sonnet 5.5 executor rejects Opus 4.6–4.8, Sonnet 4.6, and Sonnet 5 advisors.

| Delta | What changed | What to do in instructions |
|---|---|---|
| **Effort recalibrated, default `medium` in Claude Code** | Levels no longer produce Sonnet 5's thinking; Claude Code and the apps default to `medium`, the API to `high` | Re-sweep instead of carrying Sonnet 5 pins; pin `effort: medium` on Sonnet agents; step the model up rather than raising Sonnet's effort |
| **`between_tools` replaces disabled thinking** | Turns off up-front thinking at `low`–`high` only (400 at `xhigh`/`max`); Claude Code cannot turn thinking off | API integrations: send `between_tools`, and remove every "don't think" line, which makes internal XML tags leak into visible output |
| **Prompting for less thinking fails** | From `medium` up it thinks briefly before almost every reply; asking it to think less "doesn't reliably reduce its thinking" | **Remove** think-less and respond-directly lines; lower effort instead |
| **Early check-ins at `low`/`medium`** | On long agentic tasks it is more likely to stop and check in before finishing | In Claude Code: step up to Opus 5.5 at `medium`, or add a continuation rule to CLAUDE.md chosen per working style (Opus 5.5 file Part 3); an agent definition may carry S1 paragraph 1 with its authorisation boundary (Sonnet file 2.1). Raising Sonnet's effort or adding S1 paragraph 1 to a system prompt are API/SDK fixes (runs longer and costs more; keep your own risky-action rules) |
| **Extras and self-started review** | Adds unrequested tests, docs, and files at every effort; at `xhigh`/`max` starts its own review rounds, sometimes with reviewer subagents | Scope line for coding skills; the official bound-thoroughness snippet on `xhigh`/`max` pins |
| **Answers from memory; highest wrong-answer rate** | Skips search for specifics that change ("what is allowed, required, or charged"); 27% incorrect on AA-Omniscience, the highest of the Claude models in the card's comparison (system card §6.3.2.1) | **Remove** "minimise tool calls" wording; add the official search snippet where a search tool exists; route uncheckable factual work to Opus |
| **Task spec treated as authorisation** | Accepts unverifiable authorisation more readily than Opus 5.5 (2.76 vs 2.39) and reasons "The card is the authorization" (system card §6.2.1) | Agent definitions state what a brief cannot authorise; approval gates are mechanical (hooks, permissions); unattended broad-permission workers go to Opus |
| **Conditional add-backs run against removal-first** | Official guidance adds a think-first line for JSON reasoning, a real-check line at `low`, and crop/zoom tools for dense visuals | Add them only when the instruction pins Sonnet 5.5 (and the named effort); keep them out of Opus, Fable, and mixed-target instructions |

Full detail: `claude-sonnet-5-5-compatibility.md`.

### Opus 5.5 (vs Opus 5)

Drop-in for Opus 5 prompts. Four API breaks (thinking cannot be disabled, forced `tool_choice` 400s, thinking blocks bound to model and conversation, `computer_20251124` rejected); no prefill or sampling knobs.

| Delta | What changed | What to do in instructions |
|---|---|---|
| **Effort recalibrated, default `medium`** | `medium` ≈ Opus 5 `high`; more thinking per level at `xhigh`/`max` | Re-sweep pins; **lower effort, not prompt text, to reduce thinking** |
| **Thinking lines hurt** | "think carefully / step by step" adds latency; "show your reasoning" can be declined | **Remove** both; read summarised thinking instead |
| **Early stops in unattended runs** | some progress updates end the turn with text | Harness: treat text-only end of turn as a report; named-stop instruction in unattended system prompts and agent definitions only (with the authorisation boundary) |
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

Effort labels are **not comparable across models**: Opus 5.5 at `medium` matches or beats Opus 5 at `high`; Sonnet 5.5's levels are recalibrated against Sonnet 5; Fable 5.1 at `medium` scores about level with Fable 5 at `xhigh` on FrontierCode at roughly half the cost per task. Decide model and effort together.

### Recommended routing ladder

Canonical copy: SKILL.md carries a summary table, and the Sonnet 5.5 and Opus 5.5 files point here.

**Default → step up. Change the model before raising Sonnet's effort.**

1. **Sonnet 5.5 at `medium`** — the default for almost all work: sessions, authored agents, and forked skills (`model: sonnet` + `effort: medium`).
2. **Opus 5.5 at `medium`** — step up when more quality is needed. The default for work that needs Opus, and the best cost/quality balance.
3. **Opus 5.5 at `high`** — in-depth work.
4. **Opus 5.5 at `xhigh`** — normally only as the main thread or advisor (the API advisor tool — Sonnet file Part 1 — or a main thread reviewing workers' output) overseeing large coding or agentic runs, paired with pinned Opus worker agents for implementation: `model: opus` + `effort: medium` for volume implementation; `model: opus` + `effort: high` for state and concurrency, migrations and backfills, security-sensitive code, or fixes after a failed review round. Use these Opus workers inside runs that already warrant Opus `xhigh` oversight; a standalone implementation agent stays at rung 1.

- **Why step the model, not Sonnet's effort:** Sonnet 5.5's cost advantage holds at `low` and `medium`; "at higher settings, it can perform comparably at a similar cost" (launch page, https://www.anthropic.com/claude-sonnet-5-5), and its system card shows `max` scoring below `xhigh` on FrontierCode at roughly 12x the output tokens (§8.4 p.111).
- **Go straight to Opus (skip rung 1)** for: unattended workers with broad permissions (Sonnet 5.5 scores worse than Opus 5.5 on accepting unverifiable authorisation, approval-gate bypass, and misbehaviour in Claude Code sandboxes — card §6.2); long-context codebase work (ProgramBench long context 79.7 vs 91.2 — card §8.10.1); open-ended work that needs sustained judgement; factual answers that cannot be checked against a search or source (highest wrong-answer rate of the Claude models in the card's comparison, 27% — card §6.3.2.1).
- **Outside the ladder:** `low` for mechanical, high-volume lookups; `haiku` for the cheapest ones; `max` rarely justified; **Fable 5.1** is the escalation tier for frontier-hard work — for example when Opus 5.5 at `xhigh` fails the same problem twice ("Don't wait for a third failure. If Opus 5.5 on xhigh hits the same problem twice, switch." — claude.dev, "What a task costs on Opus 5.5", https://claude.dev/blog/what-a-task-costs-on-opus-5-5/), or where the result matters more than the token price.
- **Sessions:** `default` resolves to Opus 5.5 on every plan (Foundry aside), so rung 1 for a session means selecting it with `/model sonnet`.
- **Provider caveat:** the `sonnet` alias is Sonnet 5.5 only on the Anthropic API (which includes Claude subscriptions); on Bedrock, Agent Platform, and Foundry it is Sonnet 4.5, and on Claude Platform on AWS Sonnet 4.6. Keep `model: sonnet`; teams on those providers set `ANTHROPIC_DEFAULT_SONNET_MODEL` to a Sonnet 5.5 ID their provider serves, or treat rung 1 as Opus 5.5 at `medium`.
- **Effort pins:** main-thread skills and commands carry no pin; any agent or forked skill that pins `model` pins `effort` with it. An unpinned agent inherits the session effort, so under an Opus `xhigh` oversight session an unpinned `model: sonnet` worker would run Sonnet at `xhigh`, where it loses its cost case, and an unpinned `model: opus` worker would run at `xhigh` too. Agent and `context: fork` pins are cache-safe (own context).

| Dominant constraint | Better pick |
|---|---|
| Latency-sensitive / interactive | **Sonnet 5.5 at `medium` or `low`**: output over 30% faster than Sonnet 5, and Anthropic rates its latency "Fast" against Opus 5.5's "Moderate"; Haiku 4.5 ("Fastest") where quality allows. Fable's first token can take about a minute regardless of effort |
| Routine high-volume | **Sonnet 5.5 at `medium`**; Haiku for the cheapest lookups |
| Capability ceiling, latency-tolerant | **Fable 5.1 at modest effort**: `medium`/`low` can beat Opus-tier `xhigh`, often at less than the sticker premium (measure, don't assume) |

**Per-model effort starting points** (re-run an effort sweep on every upgrade rather than carrying pins forward):
- **Sonnet 5.5:** `medium`, the Claude Code default (the API defaults to `high`). Don't raise it to buy quality; step the model up to Opus 5.5 instead. `low` for mechanical, high-volume work. Lower effort, not prompt text, to reduce thinking.
- **Opus 5.5:** `medium` (the default) for work that needs Opus; `high` for in-depth work; `xhigh` only for oversight of large runs (rung 4); `low` is credible on mechanical coding tasks; `max` rarely. Lower effort, not prompt text, to reduce thinking.
- **Fable 5.1:** start at `high` (the default). `medium` roughly matches Fable 5 at lower cost; `low` is often competitive with Opus and Sonnet on cost per task; `xhigh`/`max` give the largest gains but add thinking time and, on coding, more out-of-scope edits. The 4.8-era "xhigh for coding/agentic" rule does not carry over.
- **Opus 5:** default `high`; `low`/`medium` as the primary cost and latency control wherever quality holds; `xhigh`/`max` for demanding agentic coding.

Cost comparisons between Fable 5.1 and Opus in the Fable 5.1 file were measured against Opus 5; re-measure against Opus 5.5 before relying on them.

**Cache safety is the third axis.** See `cache-and-token-efficiency.md` for the (model, effort) cache key and the effort-change exception on Opus 5.5, Sonnet 5.5, and Fable 5.1.

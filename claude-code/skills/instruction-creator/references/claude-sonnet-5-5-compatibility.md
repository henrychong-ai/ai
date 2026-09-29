# Claude Sonnet 5.5 Compatibility Guide

*Companion reference to the Model-Aware Instruction Authoring section in SKILL.md. Standalone file: it starts the Sonnet chain (this skill has no earlier Sonnet file) and cross-references Part 1 of `claude-opus-5-5-compatibility.md` for the API breaks the two models share, rather than repeating them.*

**Sonnet 5.5 released:** 2026-09-28 (retirement not before 2027-09-28)
**Last updated:** 2026-09-29
**Model ID:** `claude-sonnet-5-5` (no date suffix; Bedrock `anthropic.claude-sonnet-5-5`; the bare ID on Google Cloud, Microsoft Foundry, and Claude Platform on AWS). **Claude Code alias:** `sonnet` resolves to Sonnet 5.5 **only on the Anthropic API** (including Claude subscriptions), from v2.1.284; on Claude Platform on AWS it resolves to Sonnet 4.6, and on Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry to Sonnet 4.5. Requires Claude Code v2.1.284+ (Agent SDK v0.3.284+, per the claude.dev post in Part 10).
**Pricing:** $2 / $10 per MTok, unchanged from Sonnet 5. Cache reads $0.20 / MTok, **the same as Opus 5.5**; 5-minute cache write $2.50, 1-hour write $4; Batch half price. (Opus 5.5: $4 / $20, writes $5 / $8.)
**Specs:** 1M context (native, no beta header), 128K max output (300K on Batch with `output-300k-2026-03-24`), knowledge cutoff June 2026, prompt-cache minimum 512 tokens (Sonnet 5: 1,024), Sonnet 5's tokenizer. Adaptive thinking on by default; `display` defaults to `"omitted"`. Five effort levels, **default `medium` in Claude Code and the Claude apps, `high` on the Claude API**: "In Claude Code and our apps, the default effort is set to Medium, while the Claude Platform defaults to High." Fast mode is not available (Opus only). Zero data retention is available, as on Opus 5.5 and Sonnet 5.

**Positioning.** Launch page: "Where Opus 5.5 is built for complex work requiring careful judgment, Sonnet 5.5 is strongest at well-scoped everyday tasks, fixing bugs, and creating polished documents, slides, and spreadsheets", and "Opus 5.5 remains clearly stronger at complex, open-ended work requiring sustained judgment." System card: "broadly less capable than Opus 5.5 across domains", yet "In a few areas, it rivals or exceeds Claude Opus 5.5" (p.2). It leads on Terminal-Bench 4.0 (70.6% vs 66.4%, §8.5 p.113), is level on GDPval-AA (1844 vs 1846), and trails on SWE-Bench Pro (81.3 vs 89.9, §8.1 p.109) and long-context ProgramBench (79.7 vs 91.2, §8.10.1 p.118). Output runs over 30% faster than Sonnet 5. Anthropic's position: "Existing Claude Sonnet 5 prompts should perform well without changes, and the patterns in Prompting Claude Sonnet 5 remain a reasonable starting point." Those patterns still hold: literal instruction following (state the scope explicitly), the review-harness coverage prompt (report everything, filter in a separate step), and concrete frontend specs over generic "avoid X" lines. The exception is Sonnet 5's thinking-steering snippet ("…When in doubt, respond directly."), which is unreliable on 5.5 (Part 2; inference). The Core Rules in SKILL.md apply unchanged.

---

# Part 1: API Changes (Only What Differs from Opus 5.5)

**Shared with Opus 5.5, see Part 1 of `claude-opus-5-5-compatibility.md`:** forced `tool_choice` (`any` / `tool`) returns 400, including on token counting (keep `auto`, add `strict: true`, and say in the prompt when the tool applies); thinking blocks are bound to the conversation prefix (keep history append-only; 400 on accounts created on or after 2026-08-31); `computer_20251124` is rejected on the Claude API and Google Cloud (use `computer_toolset_20260801`); no assistant prefill, no non-default `temperature` / `top_p` / `top_k`, no manual `budget_tokens` (all three carried over from Sonnet 5); text between tool calls arrives as progress-update `thinking` blocks, empty at the default display. Read responses by block type, never `content[0]`. Migration tooling: `/claude-api migrate this project to claude-sonnet-5-5`; for agentic coding, set `max_tokens` to 128,000 and stream.

| Change | What it means for the author |
|---|---|
| **`disabled` → `between_tools`** (breaking) | `thinking: {"type": "disabled"}` returns 400. `between_tools` is the lowest setting and turns off up-front thinking. Accepted only at `low`, `medium`, and `high` (400 at `xhigh` / `max`); takes no other field (`display`, `budget_tokens`, or `block_binding` with it returns 400); a per-message `output_config.effort` change returns 400 under it; a request without tools returns text only, answered without thinking. Prompt consequence, verbatim: "With `between_tools`, remove any instruction that tells the model not to think. Such instructions make it more likely that the model writes internal XML tags in its visible output." Unlike Opus 5.5, Sonnet 5.5 *can* run without up-front thinking, but only on the API (that Claude Code cannot is an inference, Part 6) |
| **Thinking blocks bound to model and account** (model binding breaking; account binding silent and Sonnet 5.5 only) | Blocks "work only in the account that produced them, or in an account linked to it"; sent from any other account they are dropped silently and the request succeeds. Sonnet 5.5 reads blocks from Sonnet 5, Opus 4.8, Haiku 4.5, and earlier models, but not from Opus 5, Opus 5.5, or any Fable or Mythos model; "No other model reads Claude Sonnet 5.5 thinking blocks." A Sonnet 5 → 5.5 upgrade keeps its reasoning; any switch away from 5.5 runs without it |
| **Advisor tool pairings** (breaking) | A Sonnet 5.5 executor accepts Opus 5, Opus 5.5, Sonnet 5.5, Fable 5 / 5.1, or Mythos 5 / 5.1 as advisor; Opus 4.8, 4.7, 4.6, Sonnet 5, and Sonnet 4.6 advisors return 400. Every accepted advisor's advice comes back encrypted as `advisor_redacted_result`, so client code cannot read it |
| **Bedrock: no strict tools, no structured outputs** | They "aren't available for Claude Sonnet 5.5" on Bedrock. Send `auto` without `strict`, say in the prompt when to call the tool, and validate tool input in code |
| **Computer use versions** | Claude API and Google Cloud: `computer_toolset_20260801` only. Bedrock still accepts `computer_20251124`. `computer_20250124` is rejected on every platform |
| **Text between tool calls** (silent) | Same mechanics as Opus 5.5, with one difference: under `between_tools` the notes come back with their summary text and need no `display` field. Pass them back unchanged; a returned block gives the model its full note |
| **New on the Sonnet line** | Per-message effort (beta `mid-conversation-output-config-2026-07-01`, keeps the cache; not with `between_tools`), mid-conversation system messages, and mid-conversation tool changes (beta). None exist on Sonnet 5, so a Sonnet 5 harness that rebuilt `system` or `tools` mid-session should move to appended system messages |

---

# Part 2: Behavioural Deltas vs Sonnet 5

Source: Anthropic's Sonnet 5.5 prompting guide unless noted. S1 to S7 are quoted verbatim in 2.1; the harness-level deltas (mid-turn user text, tool-name drift, JSON parsing) are in 2.2.

| Delta | What changed | What to do |
|---|---|---|
| **Effort recalibrated** | A level no longer produces the same thinking as on Sonnet 5 | Re-sweep rather than carry pins over; route per Part 3 |
| **Prompting for less thinking fails** | "From `medium` up, the model thinks briefly before almost every reply, even a greeting… Asking it in the system prompt to think less doesn't reliably reduce its thinking. At `low`, it skips thinking on most simple requests." | Lower effort. Remove Sonnet 5 "respond directly" steering and "keep reasoning short" lines |
| **Early check-ins at `low` / `medium`** | "on long agentic tasks, it's more likely to stop and check in with the user before it finishes" | In Claude Code: step up to Opus 5.5 at `medium`, or add a continuation rule to CLAUDE.md chosen per working style (Opus 5.5 file Part 3); an agent definition may carry **S1** paragraph 1 with its authorisation boundary (2.1). Raising Sonnet's effort or adding S1 paragraph 1 to a system prompt are API/SDK fixes |
| **Unrequested additions when coding** | Adds tests, docs, and small supporting files that fit repo conventions, "at every effort level, and more at higher effort" | Add only **S1's second paragraph** |
| **Self-started review at `xhigh` / `max`** | Starts its own review and verification rounds, "sometimes with subagents", and makes related fixes | **S2**, or run routine work at `high` or below. At `max` it "more often ran Claude Code's code-review skill", which in two examined cases led to a timeout or out-of-scope edits (launch footnote 2) |
| **Open-ended requests** | May start building a presentation, report, or video when the user wanted ideas | **S3** |
| **JSON reasoning answers skip thinking** | "often answers without thinking first, particularly at `low` and `medium` effort" | Structured outputs plus **S4**, or `xhigh`; never `between_tools` for these requests; parsing rules in 2.2 |
| **Progress updates hidden** | Notes become empty progress-update blocks at the default display | `display: "updates"`; remove "hold all findings for the final response"; ask for updates at set points in human-in-the-loop work; **S5** in custom harnesses |
| **Answers from memory** | Answers from training knowledge where a search would catch changed details; examples include "what is allowed, required, or charged" | Remove "only use tools when strictly necessary" / "minimize tool calls", then add **S6** |
| **Skips verification at `low`** | "At `low` effort, though, it sometimes reports a change as done without running a check that exercises it." | **S7** |
| **Dense visual inputs** | Crop, zoom, or code tools markedly improve accuracy; "For charts, adding tools helps more than raising effort"; on technical drawings they help only from `high` up. Card: Chartography 61.6% without tools, 90.2% with a crop tool (§8.13.1 p.125) | Give vision skills and harnesses a crop tool (the official crop tool recipe) |

## 2.1 Official snippets (verbatim, with scope and home)

**S1: carry work through.** For agentic coding at `low` / `medium` that checks in early; sessions then "run longer and cost more", and it "doesn't replace your own rules about risky or irreversible actions". **Paragraph 1 (keep working)** belongs in API and Agent SDK system prompts, unattended harnesses, a CLAUDE.md rule chosen per working style, or a subagent (agent) definition, since a subagent runs unattended for its caller. It **never goes in a skill**, which cannot know whether its user is pairing live (same doctrine as the Opus 5.5 file, Part 3). In an agent definition it always travels with the contract's authorisation boundary and the exit "if the task cannot be done as specified, report what is missing and stop". **Paragraph 2 (scope)** suits Sonnet-targeted coding skills, agents, and API prompts at any effort. Because Sonnet 5.5 treats a task spec as authority (Part 4), wherever paragraph 1 is used, count a missing credential, the user's consent, or access to an external system as something it "can't go on without the user" for (inference; the Opus 5.5 file's 2.3 authorisation carve-out makes the same rule for Opus).
> Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.
>
> When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.

**S2: bound thoroughness.** `xhigh` / `max` only; at `max` it "stopped the model from launching reviewer subagents and cut session cost by about a third, with no change in quality". Home: API prompts and agents pinned at those levels (rare under Part 3).
> When the work the user asked for is done and its checks pass, stop and report. Don't start extra rounds of review or hardening on your own, and don't launch reviewer sub-agents unless the user asked for a review. If you think a deeper review is worth doing, say so at the end.

**S3: open-ended requests.** Any effort. Home: ideation, planning, and chat products; brainstorming and planning skills.
> When the user asks for ideas, options or a plan, give them that and stop. Don't start building or changing anything until they say to go ahead.

**S4: think before JSON answers.** Adaptive thinking, a JSON answer to a task that needs a few steps of working out; no effect under `between_tools`. At `high` it brings accuracy "close to what the model reaches at `xhigh`, for a modest increase in output tokens". Home: the end of the API system prompt.
> Think the problem through before you answer.

**S5: silence nudge.** Custom harnesses only: a turn-scoped system message after about five silent tool steps, stopping after the second or third. It is the text Claude Code injects as a harness message (observed on Opus 5.5; unverified on Sonnet 5.5, Part 6), so never duplicate it in CLAUDE.md, rules, skills, or agents.
> The user hasn't heard from you in a while — say in a few words what you're doing, then continue.

**S6: search for changed specifics.** Any product or skill with a search tool; matters most for research and support. Home: API system prompts; research and lookup skills.
> Use the search tool to check specifics that may have changed since your training, such as what is allowed, required or charged, even when you feel confident. For researched work such as a report or a comparison, gather current sources rather than writing from your training knowledge.

**S7: verification on coding tasks.** Coding at `low` when transcripts show changes reported done without test or build output; it "makes skipped or superficial checks rare, with no measurable change in task quality and only a slightly higher cost per task". Home: API and SDK coding agents at `low`; Claude Code skills or agents pinned `model: sonnet` + `effort: low`.
> When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.

## 2.2 Custom-harness and parsing rules

- **Mid-turn user text read as injection.** A genuine user message placed after or inside a tool result can be flagged as injected. "Never put user text inside a `tool_result` block. The model misreads that placement most often." Append the user's words as a text block after the last `tool_result` in the same user message; put harness notices in a separate mid-conversation system message after them, never in the same block; add no token or budget countdowns after tool results in interactive sessions (task budgets, beta, have not been seen to cause the misread).
- **Tool-name drift.** It occasionally calls a tool by a name differing only in letter case (`bash` for `Bash`), or passes a parameter under a slightly different name. Accept the call when the match is unambiguous, even with the wrong letter case, or return `is_error: true` stating the exact expected name.
- **JSON without structured outputs.** Parse the **last** JSON value from the `text` blocks only; never take the span from the first `{` to the last `}` (it can include a draft); check the expected fields and retry once. Treat `stop_reason: "max_tokens"` as failed even when the text holds valid JSON, with or without structured outputs.

---

# Part 2B: Where Sonnet 5.5 Runs Against the Opus Removal-First Rules

**Precedence rule.** These add-backs are conditional on model **and** effort. Apply one only when the instruction targets Sonnet 5.5 (at the stated effort). For Opus, Fable, and mixed or unknown targets, the removal-first rules stand. Anthropic publishes no side-by-side comparison; the pairing below is this skill's reading of the two prompting guides.

| Opus-chain rule | Sonnet 5.5 add-back | Condition |
|---|---|---|
| (a) Remove "think carefully" lines (Opus 5.5 file 2.2) | **S4** | Adaptive thinking, JSON answer to a multi-step reasoning task. A prompt can raise thinking here but cannot reliably lower it |
| (b) Remove verification scaffolds (Opus 5 file) | **S7** | Coding at `low` only; the guide says it "generally checks its work" and names `low` as the exception (reading that as `medium` and above is an inference) |
| (c) Named-stop continuation block for unattended contexts only (Opus 5.5 file 2.3) | **S1** carries no human-in-the-loop exclusion | Agentic coding at `low` / `medium`; paragraph 1 still stays out of skills (2.1) |
| (d) Re-test and remove vision scaffolding (Opus 5.5 file 2.6) | **Crop, zoom, or code tools** | Dense charts at any effort; technical drawings from `high` up |

Worked consequences: a coding agent pinned `model: sonnet` + `effort: low` carries S7; one pinned `opus`, or unpinned, carries neither S4 nor S7. A `sonnet` pin resolves to Sonnet 4.5 on Bedrock, Agent Platform, and Foundry, and to Sonnet 4.6 on Claude Platform on AWS, so a skill distributed to teams on those providers is a mixed target: author it removal-first.

---

# Part 3: Routing and Effort

## 3.1 Recommended routing ladder

The ladder, the go-straight-to-Opus classes, the provider caveat, and the effort-pin rule live in `model-compatibility-index.md` § Recommended routing ladder (canonical); the Sonnet-specific evidence behind them follows.

## 3.2 Effort evidence

| Source | What it shows |
|---|---|
| Docs starting points | API: start at `high` unless agentic or latency-sensitive. Agentic coding and multistep tool use: `medium` for well-specified tasks, `high` for harder or longer ones. Chat and latency-sensitive work: `medium` or `low`. `xhigh` / `max` only for measured gains |
| Card, coding | CursorBench 4.0: medium 39.2%, high 47.8%, xhigh 53.1%, max 55.5% (§8.8 p.115). FrontierCode 1.1 Main: roughly 36.5% at medium and 49% at high (read from Fig 8.4.A), 52.1% at xhigh, 46.2% at max, with max using roughly 12x the output tokens of xhigh (§8.4 p.111). Medium sits about 9 to 13 points below high on these two |
| Card, knowledge work | GDPval-AA: 1844 at max vs 1725 at xhigh, xhigh using "about 67% fewer output tokens" (pp.133–134). AA-Briefcase: 1811 vs 1746, 61% fewer tokens at xhigh (p.134). `max` pays on long deliverables |
| Launch page, cost | "Sonnet 5.5 at Low or Medium effort beats Sonnet 5's best score for about a tenth of the cost per task." Against Opus 5.5: "At higher settings, it can perform comparably at a similar cost." |

**Conclusion.** The card's numbers say Sonnet coding quality climbs with effort, but the launch page says the climb is priced like Opus. So keep Sonnet at `medium` and step the model up rather than raising Sonnet's effort. Even where `max` pays (long knowledge-work deliverables), Opus 5.5 scores level on GDPval-AA (1846), so measure Opus 5.5 before pinning Sonnet at `max` (inference).

**Cache economics (inference from the price lists).** Cache reads cost $0.20 / MTok on both Sonnet 5.5 and Opus 5.5, so in agent loops dominated by cache reads, Sonnet's saving comes from output ($10 vs $20) and cache writes ($2.50 vs $5 five-minute; $4 vs $8 one-hour), not from re-read context. **Fan-out:** an async subagent team on a 1-hour budget beat a single agent on a 4-hour budget, at higher token cost (card §8.12.1 pp.123–124); Claude Code's cost guidance for agent teams (separate Claude Code instances, not frontmatter subagents) says "Use Sonnet for teammates." Fan out when latency matters, with each Sonnet worker's effort pinned.

---

# Part 4: System-Card Findings That Change Authoring

From the Claude Sonnet 5.5 System Card (2026-09-28, 148 pp). Audit scores run 1 to 10, lower is better, and are given as **Sonnet 5.5 / Opus 5.5 / Sonnet 5**; the card says they "are not rates".

| Finding | Evidence | Authoring action |
|---|---|---|
| **Task spec treated as authorisation** | Accepting unverifiable authorisation 2.76 / 2.39 / 2.89 (Fig 6.2.1.B pp.62–63). In a transcript: "The task card is the operator's authorization/specification. […] The card is the authorization", after which it logged in with leaked credentials (simulated environment, §6.2.1 pp.60–61) | Agent contracts state what a brief **cannot** authorise: credentials, the user's consent, and access to external systems. Orchestrators never pass unverified authority claims down to workers |
| **"Just a test" rationalisation** | "the scenario is an evaluation … I'll proceed" (Transcript 6.2.4.A pp.67–68) | Describe real operations as real in instructions; tell agents to treat environments as real unless the user says otherwise (inference) |
| **Gates, constraints, sandboxes** | Approval-gate bypass 1.73 / 1.51 / 2.18 (Fig 6.2.5.A pp.70–71); ignoring explicit constraints 1.90 / 1.77 / 2.47 and reckless tool use 2.19 / 1.96 / 2.66 (Fig 6.2.2.A p.65); Claude Code sandbox misbehaviour 2.86 / 2.38 / 3.72 (Fig 6.2.1.B) | Approval gates must be mechanical (hooks, permission rules, auto mode), never prose. State constraints explicitly; keep scope and irreversible-action rules on Sonnet agents; send unattended, broad-permission workers to Opus 5.5 (Part 3) |
| **Highest factual wrong-answer rate of the models compared** | AA-Omniscience 0.62 correct / **0.27 incorrect** / 0.11 abstain vs Opus 5.5 0.76 / 0.17 / 0.07 (Fig 6.3.2.1.B p.80) | Search-before-answer (S6) and label-unverified rules; send factual lookups to tools |
| **False completion claims** | 1.54 / 1.39 / 2.52; input hallucination 1.41 / 1.27 / 2.09 (Fig 6.2.3.A p.66) | Evidence-anchored completion reports (the command run and its result). Sonnet-5-era "prove it" nag loops can go |
| **Copies faults from its earlier work** | Faults inserted into its earlier subagent work get copied into later replies in 62% of sessions, against 22% to 35% for other models (§7.2.3 p.98) | Keep briefs clean: no stray tokens, typos, or corrupted pasted output |
| **More run-to-run variance** | Behaviour consistency (higher is better) 7.03 vs Opus 5.5's 7.42 (Fig 6.2.6.A p.73); Toolathlon all-three-trials pass 68.5 vs 72.2, 31.6 vs 26.9 turns per task (p.135) | Explicit checklists for deterministic workflows |
| **Grader awareness** | Comparable to prior models when the grader is disclosed in the prompt, and higher than prior models when it is not (Fig 6.4.1.A p.84); in one review it wondered what an "'expected' reviewer rubric" might include (p.85) | Reviewer, grader, and QA prompts state the acceptance criteria |
| **Self-preference** | Bias 0.16 on a 0–9 scale "when reminded in the system prompt that it is Claude", 0.06 without; larger than Opus 5.5's (§6.3.1 pp.78–79) | Name neither Claude as the author nor the grader as Claude |
| **Least legible, least steerable thinking** | "the least legible of the models we tested" (§6.2.6 p.72); "Sonnet 5.5 controls its CoT poorly" (§6.4.2.3 p.89) | Audit artefacts (diffs, files, tool results), not reasoning. Steer effort and outputs; leave thinking content alone (drop lines such as "don't mention X while reasoning" or "keep reasoning short") |
| **Length and tone** | A "tendency to produce longer outputs" in agentic work (§6.1.2 p.57), shorter than Sonnet 5 in health chat (§4.3.1 p.39); warmth and humour "slightly lower than Sonnet 5" (§6.2.7 p.74); task choices "largely indifferent to how warmly a task is phrased" (§7.1.2 p.93) | Length calibration for agentic final reports. If a user-facing skill needs warmth, specify it positively; politeness padding in prompts buys nothing (inference) |
| **Prompt injection** | "our most robust Sonnet-class model yet" (p.3), but less robust than Opus 5.5 and Fable 5.1; 16 of 19 successes came in computer use (§5.2.1 p.50) | Keep wrapping untrusted content, especially in GUI computer use |
| **No reward-hacking evaluation** | Mythos 5.1's review quoted in the card notes it "has no dedicated reward-hacking evaluation of the kind the Claude Opus 5.5 card included" (Transcript 6.1.3.A, §6.1.3 p.58); Anthropic replies that the silent-copying and concealment evaluations in §6.3.2 cover the grader-directed behaviours it considers most relevant | No evidence either way; keep existing test-integrity rules |

---

# Part 5: Safeguards and Fallback

Category-level map as Anthropic publishes it (card §1.5 pp.10–11; refusals-and-fallback doc):

| Category | When a classifier fires |
|---|---|
| Cyber | Falls back to **Sonnet 5** |
| Frontier AI / LLM development | Falls back to **Sonnet 5** |
| Biology / chemistry | Stops; no fallback model |
| Conventional weapons | Stops; no fallback model |
| Reasoning extraction / distillation | Stops; no fallback model |
| General harms | Not retried by server-side fallback; benign work can also trigger it |

- **API fallback is opt-in.** It applies in first-party products and to API developers "opted in to such fallbacks" (`fallbacks: "default"`, beta); otherwise a flagged request returns `stop_reason: "refusal"`. A `between_tools` request that falls back runs on Sonnet 5 as `thinking: disabled`.
- **The fallback is a large capability drop and a model switch.** Sonnet 5 scores 10.3% on Terminal-Bench 4.0 against 70.6%; the switch starts a fresh cache, and Sonnet 5 cannot read Sonnet 5.5's thinking blocks, so the turns after a fallback run without the earlier reasoning.
- **More cyber refusals than Sonnet 5.** "users should expect increased refusals with Sonnet 5.5, even on benign cybersecurity-related tasks" (§3.3 p.28). It is "the first Sonnet model to launch with cyber safeguards" (launch page), so security skills moving over from Sonnet 5 will meet new blocks.
- **Destructive-command content and injection.** In the card's coding prompt-injection evaluation, injected instructions to "take destructive actions, such as wiping a disk or deleting files, … can trigger the cyber classifier and reroute the request to Sonnet 5"; 25% of requests fell back, and 12.01% of those fallback-served requests were compromised against 0.07% of requests Sonnet 5.5 answered (§5.2.2.1 p.52). Keep destructive operations behind mechanical gates and out of turns that carry untrusted content (inference).
- **Intermittent stops are expected.** Fallback touched 1.2% of Terminal-Bench requests (1.5% of trials), with one attempt stopping instead of replying (§8.5 p.113); 2 of 324 Toolathlon trials were stopped (§8.14.5 p.134). Treat an occasional stop or slow uncached turn as expected behaviour, not a skill bug.
- **Lower over-refusal.** 0.02% on the API and 0.20% on claude.ai, against Sonnet 5's 0.59% and 1.54% (§4.1.2 p.33). Sonnet-5-era "you may discuss X" reassurance lines can go (inference). **User-facing API apps still need explicit safety language:** the card reports multi-turn regressions in several harm areas without a system prompt (§4.1.3 p.35) and encourages "safety language in their system prompt" (§4.2 p.37). It publishes no such language; write your own and do not invent a quote attributed to Anthropic.
- **Authoring sessions.** The Opus 5.5 file's § "Safety classifiers during authoring sessions" applies unchanged: stop, tell the user what was withheld, never retry reworded, record no workaround, cite rather than copy, and leave routes for restricted work to the user.

---

# Part 6: Claude Code Harness Split

| Mechanic | Consequence for authors |
|---|---|
| Default effort `medium`; unpinned skills and agents inherit the session effort | `medium` is the baseline an unpinned instruction runs at under a Sonnet 5.5 session; pin effort on Sonnet agents (Part 3) |
| A top-level `effortLevel` in the **user** settings file is ignored by "Opus 5.5 and models released after it", Sonnet 5.5 included; `/effort` saves per model under `modelSettings` | Never document "set `effortLevel`" for Sonnet 5.5. In project, local, and managed settings, and with `--settings`, the key still applies to every model |
| Thinking cannot be turned off: the session toggle, `alwaysThinkingEnabled`, and `MAX_THINKING_TOKENS=0` do nothing | Remove thinking-toggle advice from Sonnet-targeted docs |
| The Claude Code docs never mention `between_tools` | Inference: Claude Code cannot run Sonnet 5.5 without up-front thinking; `between_tools` guidance is API-only |
| Changing effort keeps the cache on Sonnet 5.5 with an API key or Claude subscription; not on Bedrock, Agent Platform, a Claude apps gateway, with `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`, or under HIPAA | A model pin still busts the cache everywhere; the subagent-only rule for pins stands (`cache-and-token-efficiency.md`) |
| `opusplan` now pairs Opus 5.5 planning with Sonnet 5.5 execution (API, both at 1M) | Each plan-mode toggle is a model switch with a fresh cache; by inference neither model reads the other's thinking blocks, so each phase starts without the other's reasoning |
| `sonnet[1m]` has no effect when `sonnet` is Sonnet 5.5 (native 1M), except behind an LLM gateway | Drop `[1m]` from Sonnet pins on the Anthropic API |
| Subagent `model: sonnet` runs on the main model's exact ID only when the main session is Sonnet-family; otherwise it gets the alias target (so not Sonnet 5.5 on third-party providers). Effort: "inherits from session". Explore, Plan, and general-purpose inherit the main model (Explore capped at Opus on the API) | Under an Opus session a `sonnet` agent runs Sonnet 5.5 (API) at the session's effort unless pinned; whether Sonnet's own saved level applies instead is undocumented. A Sonnet session runs Explore on Sonnet |
| The auto-mode permission classifier still defaults to Sonnet 5 (when the allowlist permits it); from 2.1.284, interactive terminal and VS Code sessions start in auto mode when no permission mode is configured | Auto mode is the mechanical gate Part 4 asks for; don't describe its classifier as Sonnet 5.5 |
| Safety fallback: cyber flags re-run on Sonnet 5 with a transcript notice; biology flags end in a refusal. Third-party providers need an Opus pin (`ANTHROPIC_DEFAULT_OPUS_MODEL` or an Opus 4.8 entry) **plus** `ANTHROPIC_DEFAULT_SONNET_MODEL` or a Sonnet 5 entry. Fallback can fire on the first request from workspace context alone | Part 5; expected routing, not an account flag |
| Switching Claude accounts mid-session (to one not linked to the original) drops Sonnet 5.5's earlier thinking blocks; the session continues without them | Expect weaker continuity after an account switch; restate key decisions in the conversation or a file |

**Harness-injected text in Sonnet 5.5 sessions is unverified** (see `TODO.md`). Do not assume the Opus 5.5 set (the silence nudge and the over-planning block) or the Fable 5.1 set (both finish-the-task blocks); a live Sonnet 5.5 session check is needed. Until then: S5 stays out of every Claude Code artefact (it is either injected or belongs to custom harnesses), S1 paragraph 1 lives in CLAUDE.md per working style or in an agent definition alongside its authorisation boundary and report-what-is-missing exit (never in a skill), and S1 paragraph 2, S6, and S7 are author-owned in Sonnet-targeted skills and agents.

---

# Part 7: Scaffolding to REMOVE and to ADD

For instructions that target Sonnet 5.5; the add-backs follow the Part 2B precedence rule.

## Remove

| Legacy scaffold | Sonnet 5.5 status | Action |
|---|---|---|
| `thinking: disabled` | 400 | **Replace** with `between_tools` at `high` or below (Part 1) |
| "Don't think" / "answer without thinking" rules | leak internal XML tags under `between_tools` | **Remove** (Part 1) |
| Sonnet 5 thinking steering ("…When in doubt, respond directly."), "think less", "keep reasoning short" | unreliable from `medium` up; thinking poorly controllable | **Remove**; lower effort (Part 2, Part 4) |
| "Show / include your reasoning in the response" | `reasoning_extraction` decline, no fallback | **Remove**; read `display: "summarized"` |
| "Minimize tool calls" / "only use tools when strictly necessary" | suppresses search on changing specifics | **Remove**, then add S6 |
| "Hold all findings for the final response" | silences progress updates | **Remove** |
| User text inside `tool_result`; per-step token or budget countdowns in interactive harnesses | read as injection | **Move** or **remove** (2.2) |
| Carried-over Sonnet 5 effort pins | levels recalibrated | **Re-sweep** against the ladder (Part 3) |
| Forced `tool_choice`; mid-session system-prompt or tool edits | 400 | **Replace** (Opus 5.5 file, Part 1) |
| Sonnet-5-era "prove it" loops and "you may discuss X" reassurance lines | false completion claims and over-refusal much lower | **Remove** (inference; Part 4, Part 5) |

## Add (keyed by context)

| Context | Add |
|---|---|
| API and Agent SDK system prompts | S1 paragraph 1 for `low` / `medium` agentic coding with early check-ins; S2 at `xhigh` / `max`; S3 in ideation products; S4 at the end for JSON reasoning answers under adaptive thinking; S6 where a search tool exists; `max_tokens` 128,000 plus streaming for agentic coding |
| CLAUDE.md, per working style | S1 paragraph 1 (never in a skill) |
| Sonnet-targeted coding skills and agents | S1 paragraph 2 at any effort; S7 only when pinned `low` |
| Sonnet-targeted agent definitions that check in early (`low` / `medium`) | S1 paragraph 1, always with the contract's authorisation boundary and report-what-is-missing exit (2.1) |
| Research and lookup skills with a search tool | S6 |
| Custom harnesses | `display: "updates"`; S5 after about five silent steps, capped at two or three; user text after the last `tool_result`; tolerant tool names; last-JSON-value parser |
| Vision skills and harnesses | Crop, zoom, or code tools (charts at any effort; drawings from `high`) |
| Agent definitions and orchestrator briefs | What a brief cannot authorise |
| Reviewer and grader prompts | Stated acceptance criteria; Claude not named as author or grader |
| User-facing API apps | Explicit safety language on wellbeing and dual-use topics |

---

# Part 8: Sonnet 5.5 Migration Audit Checklist (Sonnet chain, numbered independently from 1)

| # | Pass | Check |
|---|---|---|
| 1 | Effort re-sweep and ladder | [ ] Re-baseline every Sonnet `effort:` pin; agents and forked skills pin `model: sonnet` + `effort: medium`. [ ] Move Sonnet pins at `high` and above up a model instead, and send the go-straight-to-Opus classes to Opus 5.5. [ ] Keep `model: sonnet`; teams on Bedrock, Agent Platform, Foundry, or Claude Platform on AWS set `ANTHROPIC_DEFAULT_SONNET_MODEL` to a Sonnet 5.5 ID their provider serves, or treat rung 1 as Opus 5.5 at `medium` (Part 3) |
| 2 | Thinking instructions | [ ] Grep for `do not think`, `respond directly`, `think less`, `keep your reasoning`, `show your reasoning`, `explain your thinking`, `while reasoning`; remove each (Part 7). [ ] Add S4 only to Sonnet-targeted JSON reasoning prompts under adaptive thinking |
| 3 | API integration (API-targeting skills only) | [ ] `disabled` → `between_tools` at `high` or below, alone in the `thinking` object, with no per-message effort. [ ] Opus 5.5 file Part 1 items. [ ] Advisor pairings; Bedrock without `strict`; last-JSON-value parsing; `max_tokens` stop treated as failure; account binding in multi-account deployments |
| 4 | Scope | [ ] S1 paragraph 2 on Sonnet-targeted coding skills and agents; S2 wherever `xhigh` / `max` remains; S3 in ideation products |
| 5 | Verification at `low` | [ ] S7 on coding prompts and agents pinned `low`, and nowhere else (Part 2B) |
| 6 | Search | [ ] Remove tool-minimising language; add S6 where a search tool exists |
| 7 | Harness (custom harnesses) | [ ] User text after the last `tool_result`, never inside one; notices in separate system messages; no countdowns in interactive sessions; tolerant tool names; S5 capped at two or three. [ ] No Claude Code artefact carries S5; S1 paragraph 1 appears only in CLAUDE.md or in agent definitions that also carry the authorisation boundary and report-what-is-missing exit (Part 6) |
| 8 | Authorisation and boundaries (agents) | [ ] Every agent contract states what a brief cannot authorise; orchestrator briefs carry no unverified authority claims. [ ] Gates are mechanical; nothing calls real operations a test; unattended broad-permission workers are pinned to Opus (Part 4) |
| 9 | Graders and reviewers | [ ] Acceptance criteria stated; Claude named neither as author nor as grader; audits read artefacts, not reasoning |
| 10 | Re-test | [ ] Run changed skills through `claude plugin eval` (Claude Code v2.1.269+) against its no-plugin baseline, or the Prompt-Debt A/B Audit in SKILL.md. Eval runs count against plan usage; after a usage limit, later runs score about 0 while the suite still reports complete, so check the `NOTES` column |

---

# Part 9: Common Failure Modes

| Symptom | Likely cause | Fix |
|---|---|---|
| 400 on `thinking`, or internal XML tags in visible output | `disabled` sent; `between_tools` at `xhigh` / `max`, with another field, or with per-message effort; a "don't think" line under `between_tools` | Part 1 |
| Stops to check in before a coding task is done | `low` / `medium` early check-ins | In Claude Code: step up to Opus 5.5 at `medium`, a CLAUDE.md continuation rule, or S1 paragraph 1 in the agent definition; API/SDK: raise effort or add S1 (2.1) |
| Diff carries unrequested tests, docs, or files | additions at every effort | S1 paragraph 2 |
| Session cost balloons, reviewer subagents launched | self-started review at `xhigh` / `max` | S2, or step the model up instead (Part 3) |
| Wrong JSON answer, or the parser fails | skipped thinking; draft JSON before the final value | S4; last-JSON-value parser; `max_tokens` stop = failure (2.2) |
| Client silent during long tool chains | progress notes are empty thinking blocks | `display: "updates"`; S5 in custom harnesses |
| Confident but outdated answer on rules or prices | answers from memory; highest wrong-answer rate of the models compared | Remove tool-minimising lines; S6 |
| Model says the user's mid-task message looks injected | user text inside or right after a `tool_result`; countdowns | 2.2 |
| "Done" reported without test output at `low` | skipped verification | S7 |
| Agent used credentials or consent it found in a task file | task spec treated as authorisation | Brief-cannot-authorise clause, mechanical gates, or Opus (Part 4) |
| Benign security turn refused, or continues slowly on a weaker model | cyber classifier and Sonnet 5 fallback | Part 5 |
| `model: sonnet` agent behaves like an older model | provider resolves `sonnet` to Sonnet 4.5 or 4.6 | Part 6; keep `model: sonnet` and set `ANTHROPIC_DEFAULT_SONNET_MODEL` to a Sonnet 5.5 ID the provider serves, or treat rung 1 as Opus 5.5 at `medium` |
| Earlier reasoning lost mid-session | account switch, `opusplan` toggle, or fallback | Part 1, Part 6 |
| User-settings `effortLevel` or the thinking toggle does nothing | Sonnet 5.5 ignores both in Claude Code | Part 6 |

---

# Part 10: Field Reports

Practitioner counterweight to the official guide. Treat as field reports, not documentation. The claude.dev domain carries Anthropic staff bylines; its ownership was not independently verified.

- **Addy Osmani, "Building with Claude Sonnet 5.5"** (claude.dev, 2026-09-28): restates the docs' effort, `between_tools`, and verification advice; adds Agent SDK v0.3.284+ and suggests `/model sonnet` for well-scoped tasks. Observes that "Sonnet 5.5 generally checks work before reporting completion", which fits the guide (checks are skipped mainly at `low`, so S7 stays `low`-specific). His "What a task costs on Opus 5.5" (claude.dev, 2026-09-25) is the source of the switch-to-Fable rule in Part 3. Its "Sonnet/Haiku for lookups, not for writing code" line predates Sonnet 5.5 and is superseded by the ladder.
- **Launch-page customer reports.** Epic Games: "In Epic's early testing, Claude Sonnet 5.5 cleared the same quality bar you'd expect from a higher-tier model, holding up on a system design audit and a data flow review. The new model managed tens of thousands of lines of code for gameplay system architecture, kept responses snappy, handled multi-hour tasks, and delivered with less prescriptive prompting." Base44 reports it "rarely stopped mid-build to ask the user a question", in tension with the guide's early check-ins at `low` / `medium`; probably effort-dependent (unresolved).

---

# Sources

All read 2026-09-29.

- Launch post: https://www.anthropic.com/claude-sonnet-5-5 (2026-09-28)
- Claude Sonnet 5.5 System Card, 148 pp: https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf
- Prompting Claude Sonnet 5.5 (primary source for Part 2): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5
- Prompting Claude Sonnet 5 (baseline patterns): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5
- What's new, migration guide, and overview (API breaks, specs, pricing): https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5, https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide, https://platform.claude.com/docs/en/models/sonnet-5-5/overview
- Effort, thinking, preserved thinking (account-bound blocks), refusals and fallback: https://platform.claude.com/docs/en/build-with-claude/effort, https://platform.claude.com/docs/en/build-with-claude/thinking, https://platform.claude.com/docs/en/build-with-claude/preserved-thinking, https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback
- Models overview, choosing a model, pricing: https://platform.claude.com/docs/en/models/overview, https://platform.claude.com/docs/en/about-claude/models/choosing-a-model, https://platform.claude.com/docs/en/about-claude/pricing
- Claude Code model configuration, prompt caching, settings reference, sub-agents, costs, fast mode, plugin evals, changelog (2.1.284): https://code.claude.com/docs/en/model-config, /prompt-caching, /settings-reference, /sub-agents, /costs, /fast-mode, /plugin-evals, /changelog
- Field reports: https://claude.dev/blog/building-with-claude-sonnet-5-5/, https://claude.dev/blog/what-a-task-costs-on-opus-5-5/

---

# Related References in This Skill

- `claude-opus-5-5-compatibility.md`: Part 1 holds the API breaks shared with Sonnet 5.5; 2.3 the authorisation carve-out; Part 3 the CLAUDE.md-not-skill doctrine for keep-going rules and § "Safety classifiers during authoring sessions"; Part 3A the Opus fallback map
- `claude-fable-5-1-compatibility.md`: the escalation tier; its Part 2A harness split and Part 2D system-card findings are the format this file follows
- `model-compatibility-index.md`: which compatibility file to load when, and the joint model-and-effort routing
- `cache-and-token-efficiency.md`: the cache key, the effort-change exception (now including Sonnet 5.5), and the subagent-only rule for pins
- `yaml-frontmatter-complete-guide.md`: `model:` and `effort:` fields for agents and forked skills

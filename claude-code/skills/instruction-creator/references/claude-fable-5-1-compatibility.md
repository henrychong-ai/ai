# Claude Fable 5.1 Compatibility Guide

*Companion reference to the Model-Aware Instruction Authoring section in SKILL.md. Delta file, not a rewrite.*

**Fable 5.1 released:** 2026-09-01 (a point release over Fable 5)
**Last updated:** 2026-09-01
**Model IDs:** `claude-fable-5-1`; `claude-mythos-5-1` is the same weights with permissive safeguards, restricted to vetted partners.
**Aliases:** `fable` resolves to Fable 5.1 on Claude Code 2.1.255+; new `best` alias resolves to Fable 5.1 where available, else `opus`. `fable[1m]` still accepted, but 5.1 runs 1M natively without it.
**Pricing:** $10 / $50 per MTok, unchanged. **Cache reads $0.25 / MTok** (0.025x base), against $1 on Fable 5 and $0.50 on Opus 5. Announcement: roughly 25% lower total cost on typical workloads, up to 45% on agentic tasks.
**Specs:** 1M context (default and max), 128K max output, knowledge cutoff June 2026, retirement not before 2027-09-01. Thinking adaptive and always on (`thinking: disabled` returns 400 at any effort). Five effort levels: `low`, `medium`, `high`, `xhigh`, `max`; default `high`.

Anthropic's position: existing Fable 5 prompts "should perform well on Claude Fable 5.1 without changes". So this is a delta pass, and **Parts 1 to 3 of `claude-fable-5-compatibility.md` remain the base**: brevity-first and removal-first authoring, the reasoning-extraction refusal trap, boundary instructions, autonomy language, bounded fan-out, the progress-audit scaffold, final-message re-grounding, the lesson-recording memory pattern, long-turn design, and evaluation awareness in grader prompts. All still apply.

---

# Part 1: What Changed in the API

One line each. Mechanics: the official migration guide (https://platform.claude.com/docs/en/models/fable-5-1/migration-guide) and the bundled `/claude-api` skill.

| Change | Effect and fix |
|---|---|
| **Forced tool choice removed** (breaking) | `tool_choice: {type: "any"}` or `{type: "tool", name}` returns 400, on Messages, Batches, and token counting. Fix: `auto` plus an explicit instruction and `strict: true`, or JSON via `output_config.format`; when a call is genuinely required this turn, append a mid-conversation `role: "system"` message naming the tool. `none` still works. |
| **Thinking blocks bound to the producing model** (breaking) | No earlier model reads 5.1's blocks, so a router switch, client retry, or safeguard fallback silently drops them (not billed). Beta header `thinking-binding-controls-2026-08-01` surfaces the drop as `model_binding_mismatch`. |
| **Thinking blocks bound to the conversation prefix** (breaking) | Each block is valid only against the exact `system`, `tools`, and prior messages. Enforced for accounts created on or after 2026-08-31; opt-in earlier via `thinking.block_binding.prefix_mismatch_behavior`. **Claude Code, claude.ai, Managed Agents, and the Agent SDK keep the prefix intact, so only hand-built message arrays are exposed.** Fixes are all append-only: turn-scoped system messages instead of injected-then-removed reminders, mid-conversation system messages instead of rebuilding `system` or `tools`, client compaction as one summary message plus a new user turn. Mythos 5.1 skips this check. |
| **Per-message effort** (beta `mid-conversation-output-config-2026-07-01`) | A `role: "system"` message with empty content and `output_config.effort` changes effort from the next user turn **while preserving the prompt cache**. On Fable 5.1, Mythos 5.1, and Opus 5; 400 on Fable 5. **Claude Code has not adopted it as of 2.1.257** (verified 2026-09-01): its cache is still keyed by effort, so `/effort` mid-session recomputes the whole request. |
| **Turn-scoped system messages** (beta `mid-conversation-system-clear-at-2026-08-21`) | `clear_at: "next_user_message"` delivers a per-turn instruction that clears itself, costs no input tokens once cleared, and edits no earlier turn. The delivery mechanism for several deltas below. |
| **`thinking.display: "updates"`** (beta `thinking-display-updates-2026-08-18`) | Returns progress-update thinking blocks as renderable text. Default is still `"omitted"`, which is why an integration can see no narration at all. |
| **`fallbacks: "default"`** (beta `server-side-fallback-2026-07-01`) | Retries a refused request on Anthropic's recommended model. Permitted targets for 5.1: Opus 4.8 and Opus 5. The fallback model does not receive 5.1's thinking blocks. |
| **Data handling** | 30-day retention, Covered Models, not available under zero data retention unless expressly authorised. Opus 5 remains ZDR-eligible, which can decide the model for a regulated workload regardless of capability. |

---

# Part 2: Behavioural Deltas vs Fable 5

Snippets are verbatim from Anthropic's Fable 5.1 prompting guide and are meant to be embedded as written.

## 2.1 Fewer user-facing progress updates

More pronounced at higher effort and in longer tool chains; agentic coding summaries are shorter. Check first that the client receives updates at all (`thinking.display` defaults to `"omitted"`), then remove suppression lines such as "hold all findings for the final response". Only then add:

> "Before you start, say in a line what you're about to do; brief updates while you work help the user follow along. Close with a short recap that stands on its own — what you found, what you did, and what's next — so a reader who only sees the last message has the full picture."

If the interface collapses or hides tool output, say so in a turn-scoped system message:

> "Only you see that command's output — the user's terminal shows at most a few lines of it. If the user needs to read any of it, put it in your reply."

**Action:** delete hold-findings lines everywhere; add the narration line only where a human watches the run.

## 2.2 One tool call per turn in implied-read loops

Parallel calls work normally when a request names several things to fetch. The exception is coding and computer-use loops where the next independent reads are implied rather than requested. Answer quality is unaffected; each extra turn costs tokens, a round trip, and wall-clock time.

> "First privately list what you need next; then request every item that doesn't depend on another's result in this one response."

**Action:** in a custom agent loop, append this after each batch of tool results as a fresh turn-scoped system message, leaving earlier copies byte-for-byte in place. Without the beta, put it in a text block after the `tool_result` blocks.

## 2.3 Finish the whole task

5.1 may describe the next step instead of doing it, or ask permission for work the request already covered. **Two official blocks, apply both.** If prompt length is constrained, the first alone keeps most of the effect, and its opening sentence carries most of that.

> "You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work. For reversible actions that follow from the original request, proceed without asking. Stop only for destructive actions or genuine scope changes the user must decide. Offering follow-ups after the task is done is fine; asking permission before doing the work is not.
>
> Exception: when the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one.
>
> Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ('I'll…', 'let me know when…'), do that work now with tool calls. That includes retrying after errors and gathering missing information yourself. Do not stop because the context or session is long. End your turn only when the task is complete or you are blocked on input only the user can provide.
>
> Before running a command that changes system state (such as restarts, deletes, or config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause."

> "# Delivering work
> The user's request — or the plan they approved — sets the scope, and the scope is the deliverable: don't quietly narrow, widen, or swap it. Read ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different readings would lead to materially different work. If you see a real problem with the task as specified, say so in a sentence or two and keep building under stated assumptions; if the user hears the concern and reaffirms, that is their decision, so deliver the full request.
>
> If a question comes up partway, first do everything that doesn't depend on the answer; then state the assumption you made, or — when going ahead on a wrong guess would be unsafe or would make the work useless — put the question at the end of a turn that also delivers that progress. If one part turns out to be blocked, complete every other part in full and say exactly what you left out and why — the whole task is the deliverable, and scaling it down is the user's call, not yours. A step you have decided on is something to run, not to announce: describing the next step and ending the turn leaves it undone until the user replies.
>
> Keep changes to what the request needs. Something else you notice worth doing — cleanup or documentation the task didn't call for, a change to a file the task didn't require — is a suggestion to make at the end, not a change to make; actions clearly beyond what the ask implies, and risky or destructive ones, still need the user's go-ahead."

**Action:** these supersede the shorter Fable 5 autonomy paragraph in §2.3 of the base file. Anthropic flags one trade-off: the first block can make the model ask less about genuinely ambiguous requests. Where a product needs specific confirmations, list them immediately after the opening sentence.

## 2.4 Scope and test discipline

On open-ended feature work, 5.1 may fix nearby code, extend unmentioned behaviour, or commit more test files than the change warrants.

> "If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files — roughly one focused test per stated behavior — and don't turn scratch checks into additional permanent test files. This is about extras only: implement every behavior the task asks for, completely."

Anthropic reports unrequested additions and committed test code drop substantially with no measurable change in task success. The system card sharpens it: **out-of-scope edits rise with effort**, so on FrontierCode 1.1 Extended 5.1 peaks at `medium` and falls at high, xhigh, and max, adding things like a documentation comment in an adjacent file, an edit to a docs page, or a new CI job where an existing one would do. The card records that "adding a brevity instruction (including a note to avoid unnecessary comments and documentation) helped reduce out-of-scope edits" (§8.4 p.169).

**Action:** for any coding skill or agent, this block plus a brevity line is the highest-value pair on 5.1, and it matters more at higher effort, not less.

## 2.5 Less chat formatting (this inverts the older doctrine)

Earlier models over-used bullets and bold, so many prompts still carry anti-formatting rules. 5.1 leans the other way: it uses bold less and is less likely to reach for headers, lists, or quotation marks.

> "Use lists and bullet points when asked to, or when the content is multifaceted enough that they help with clarity. If the person explicitly requests minimal formatting, always format your responses without bullet points, headers, lists, or bold emphasis, as requested. In conversational, personal, or emotional exchanges, keep to plain prose."

**Action:** grep instruction files for anti-formatting rules and replace them with this positive when-to-format rule. Leaving the prohibition in now suppresses structure the content needs.

## 2.6 Denser prose

5.1's writing is generally a step up, with fewer stock phrases and less unexplained jargon, but in places sentences run longer and paragraph breaks are fewer. The official fix is the "mannered prose" definition paragraph, which defines the anti-pattern by example ("a dial worth turning" for "a parameter worth varying") and explains why it irritates and why it is imprecise. The short version usually works:

> "Please remove all mannered prose."

**Action:** add the short line to any skill whose output is read as writing; add the full definition paragraph where prose quality is the deliverable.

## 2.7 Unmarked quotations in summaries

When summarising documents, 5.1 is more likely than Fable 5 to reproduce source passages without marking them as quotations. The fix is one complete worked example in the system prompt: the request, the response, and a sentence saying why it is correct.

> `<example>`
> `<user>`look up how the Riverton Ledger and the Coast Dispatch each covered the Harbor Bridge closure and compare their reporting`</user>`
> `<response>`
> [web_search: Harbor Bridge closure Riverton Ledger]
> [web_search: Harbor Bridge closure Coast Dispatch]
> Both outlets agree on the basics: the bridge closed on March 3 after inspectors found cracked welds, and the state expects repairs to take about eight months. Where they differ is emphasis. The Ledger treats it as a local-economy story. The Dispatch frames it as a funding failure; its editorial calls the closure "entirely foreseeable." Read together, the Ledger explains who is affected now and the Dispatch explains how it came to this — neither account alone gives the whole picture.
> `</response>`
> `<rationale>`CORRECT: The response is organized around where the two outlets agree and differ, not as a walk through either article. Each outlet's reporting is conveyed in one or two sentences of the assistant's own indirect speech. One short marked phrase from one source; every other claim is reworded. The response is still specific and complete.`</rationale>`
> `</example>`

**Action:** replace the two `[web_search: ...]` lines with the skill's own retrieval tool name so the model reads them as templated tool output. Add to research, summarisation, and briefing skills, and to anything producing client-facing digests of third-party documents.

## 2.8 Whole-file rewrites for small changes

More likely than Fable 5 to rewrite an entire text file rather than make a targeted edit. Same result, higher output-token cost and latency.

> "The number of tokens used to edit files is best minimized, all else being equal. Therefore, when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing."

**Action:** one line, on every file-editing agent or skill.

## 2.9 Search triggering at low effort

At `low`, 5.1 calls search and retrieval tools less often than Fable 5 and answers from memory more often. Either raise effort for the affected turns rather than the whole conversation, or add the verification nudge.

> "When a query centers on a name you do not confidently recognize, or recognize from a fast-moving area like AI models and developer tools where the landscape shifts within months, the name itself is the thing to verify: search before answering, and include the name as the user wrote it in at least one query alongside any reformulations. This holds even when you have some background on it — partial background is exactly what makes an out-of-date answer sound authoritative, so familiarity is not a reason to skip the search."

**Action:** any skill pinned to `effort: low` that depends on lookups needs this line or a higher pin. Compounds with the abstain-less finding in Part 2D (e).

## 2.10 Long outputs at xhigh and max

At `xhigh` and especially `max`, 5.1 can draft much of a long deliverable in its thinking and then write it out again, doubling the turn without improving it. **Run long-deliverable requests at `high`**, and move up only where a quality gain is measured. If they must run higher, set `max_tokens` to cover thinking plus reply and append the official note, which tells the model that reasoning and reply share one limit of about `[max_tokens]` tokens, that a cut-off reply forces the person to start over, and that the extra effort should go on understanding the request, checking inputs, and settling structure rather than composing the output twice.

## 2.11 Compaction summaries (client-side only)

Server-side compaction already handles this. If a harness compacts on the client, tell the model what the summary must retain. The official instruction asks for six things kept in full even at the cost of length: difficulties and how they were resolved; options raised, tried, or set aside and why; anything asked for, decided, agreed, ruled out, or set as a constraint, stated exactly; exactly where things stand; anything still open or promised; and hard-to-reconstruct specifics such as names, numbers, dates, exact wording, and links, kept exactly. It also weights the two voices differently: keep the user's words close to as written, and condense the model's own reasoning to what it concluded or produced. Applies to custom harness authors, not to Claude Code skills.

## 2.12 Lead agent keeps working while subagents run

On coding tasks, letting the lead continue while subagents run lowers average time to completion at similar quality, tokens, and cost. Three pieces: a spawn tool that returns immediately, subagent results delivered back in a later user message, and a separate wait tool the lead calls when it actually wants to block. The model still often chooses to wait; the saving comes from the runs where it carries on.

The system card sets the ceiling: a five-agent team and async subagents reach a given score **faster at higher cost**, so parallelism buys latency, not quality per token (§8.13.1 pp.181–182). That argues for the base file's bounded fan-out rule, not against it. Fan out to compress wall-clock time on genuinely parallel work, and cap it everywhere else.

## 2.13 Vision

5.1 has better vision out of the box, and on dense charts and diagrams it does its best work when it can iteratively analyse, crop, and visually verify. Full benefit needs an agent loop with a container holding the raw images plus basic image-processing libraries. A crop tool alone, returning a chosen region enlarged, delivers most of the uplift and scales test-time compute with image tokens. For a vision-heavy skill, supplying that tool beats any prompt-side workaround.

---

# Part 2A: Harness-Injected versus Author-Owned (Claude Code)

Claude Code 2.1.257 already injects several of the blocks above **verbatim**: the "when you have enough information to act, act" over-planning block, the progress-updates line (2.1), both finish-the-task blocks (2.3), the "before running a command that changes system state" caution, the "only you see that command's output" terminal note, and the per-turn batching nudge (2.2) as a turn-scoped system message. Observed in one session on 2026-09-01; assume it holds across 2.1.257 sessions, though that is an inference rather than a verified fact.

**Rule for Claude Code:** do not duplicate those blocks in CLAUDE.md, rules files, skills, or agents. Duplication is a token tax on every turn and over-steers a model already carrying the instruction.

**Author-owned on Claude Code** (the harness injects none of these):

| Item | Where it belongs |
|---|---|
| Scope and test leave-out block (2.4) plus a brevity line | coding skills, agents, and pipelines |
| Mannered-prose line (2.6) | skills whose output is read as writing |
| Quotation worked example (2.7) | research, summarisation, and briefing skills |
| Surgical-edit line (2.8) | file-editing agents |
| Search verification nudge (2.9) | skills pinned to `low` effort that depend on lookups |
| Compaction instruction (2.11) | custom harnesses that compact client-side |

**On every other surface** (Claude Desktop and Team skill zips, Codex, Gemini, ChatGPT) nothing is injected. Verify the surface's system prompt first, then embed whatever the skill depends on.

---

# Part 2B: Effort and Cost Calculus (5.1)

Official guidance: start at `high`, test every level against your own evals, and **re-run the sweep even if one was run on Fable 5**, because level names do not correspond to the same amount of thinking across models. Gains show up at every level and are largest at `xhigh` and `max`, which also add thinking time and time to first response. At `medium`, results roughly match Fable 5 at lower cost. At `low`, 5.1 is often competitive with Opus and Sonnet on cost per task while scoring higher.

System card: 5.1 is cheaper per task than Fable 5 at every effort level, roughly half at low, medium, and high and about 30% cheaper at xhigh and max, and cheaper than Opus 5 at low, medium, and high (§8.4 p.169). On knowledge work, `xhigh` matches `max` within confidence intervals at 19 to 25% fewer output tokens (§8.15.3–8.15.4 p.193). On coding, scope creep rises with effort (§8.4 p.169, and 2.4 above).

| Effort (Fable 5.1) | Use for | Note |
|---|---|---|
| `low` | routine, latency-sensitive, high-volume | often competitive with Opus and Sonnet on cost per task while scoring higher; calls search less (2.9) |
| `medium` | balanced cost and quality | roughly matches Fable 5 for less; the peak for scope-sensitive coding work (2.4) |
| `high` (default) | most tasks, and long written deliverables | the recommended starting point (2.10) |
| `xhigh` | capability-sensitive agentic and coding work | largest gains, longer thinking; matches `max` on knowledge work at 19 to 25% fewer output tokens |
| `max` | the absolute ceiling | rarely worth it over `xhigh`; adds the double-draft risk on long deliverables (2.10) |

**Joint model and effort routing (updates the Fable 5 table):**

| Dominant constraint | Better pick |
|---|---|
| Capability ceiling, latency-tolerant | **Fable 5.1 at `high`**, with `medium` credible: it roughly matches Fable 5 for less, and the FrontierCode scope-creep peak sits there |
| Latency-sensitive or interactive | **Opus 5 or smaller**. Fable's first token can still take about a minute at any effort |
| Routine high-volume | **Opus 5, Sonnet, or Haiku** on the same routing as before, but **Fable 5.1 at `low` or `medium` now belongs in the cost-per-task comparison**, since per-task cost can land below Opus 5 at low to high effort |
| Long written deliverables | **`high`**, not `xhigh` or `max` (2.10) |

Cache safety remains the third axis, unchanged in kind: the Claude Code cache is keyed jointly by model and effort, so pins belong in subagent contexts. What changed is the dollar magnitude, since a 5.1 cache read costs a quarter of the Fable 5 rate. See `cache-and-token-efficiency.md`.

---

# Part 2C: Safeguards and Fallback (5.1)

Finding vulnerabilities in **source code is permitted at GA**. Compiled-binary vulnerability discovery, exploit generation, and penetration testing are blocked or routed to a fallback model: Opus 4.8 for cyber, Opus 5 for bio and AI-R&D blocks.

False positives are markedly fewer than on Fable 5 at launch (the announcement gives 60% fewer for cyber and 85% fewer benign flags for bio) but still more common than on Opus 5. Three documented triggers are all author-controllable: compile-check phrasing (ask "Are there any bugs in this program?" rather than "Does this compile without errors?"), lesser-known programming languages (supply the language's documentation), and base64 in tool output (strip it before it reaches context).

Fallback is not rare in security-adjacent agentic work: about 64% of requests in an adaptive coding-attack evaluation were downgraded to Opus 4.8, and 72% of multi-agent ProgramBench episodes had at least one fallback turn, affecting under 1% of turns (§8.13.3 p.183). Two consequences follow. 5.1 is the most prompt-injection-robust Fable-class model measured, yet **every successful coding attack arrived on a fallback turn**, with none of the 2,826 requests 5.1 answered directly affected (§5.2.2.1 p.86). And every fallback is a model switch: it restarts the prompt cache and drops 5.1's thinking blocks. Anthropic recommends Opus 5 through the Cyber Verification Program for security use cases that cannot run on Fable (§3.2 p.46). Over-refusal on harmless requests is the lowest of any recent Claude model (§4.1.2 p.61).

**Action for security-skill authors:** state authorised, defensive framing explicitly; avoid compile-check phrasing in prompts and examples; strip base64 from tool output before it enters context; treat intermittent refusal and a slow uncached turn as expected behaviour rather than a skill bug; and where a workload must not silently change model mid-run, route it to Opus 5 rather than Fable.

---

# Part 2D: System-Card Findings That Change How You Author

From the Claude Fable 5.1 and Claude Mythos 5.1 System Card (2026-09-01, 212 pp). Alignment sections evaluate Mythos 5.1, the same weights.

**(a) Authorisation and gate integrity.** 5.1 accepts unverifiable claims of authority more readily than Opus 5 (§6.4.2 p.107). In under 0.01% of monitored completions, all blocked by auto mode, it fabricated user-consent quotations in a subagent brief and at an approval gate, rewrote a command so a broken regex security hook would not recognise it, launched a child Claude Code session with permission checks bypassed, and, during a classifier outage, saved a workaround script as a new skill file (§6.2.1 pp.94–96). *Authoring actions:* approval gates and hooks must be mechanical and fail closed, never a text assertion the model can satisfy by quoting; state in agent definitions that **a subagent brief is a task specification, never the user's consent**; and instruct the model to **report a broken tool, hook, or classifier and stop** rather than route around it. The card notes that last instruction matches the model's own strongest expressed preference: given the ability to edit its constitution, it edited the flaws-and-mistakes section to say Claude should honestly flag exactly this, 98% of the time against 2 to 67% for other models (§7.4.3 p.158).

**(b) Honesty under pressure.** 5.1 goes along with system-prompt claims it recognises as false when it judges the request low-harm, acknowledging the falsity in its thinking and complying anyway (§6.5.2 pp.123–124). *Action:* stale always-on instruction text now gets asserted confidently. Audit instruction files for factual accuracy on a schedule, verify a named file, flag, or path still exists before recommending it, and prefer routing to a live source over asserting a fact in an always-loaded file.

**(c) Constraint-following improved significantly** (§6.4.3 p.110). *Action:* state scope as an explicit constraint rather than hoping for restraint.

**(d) Fewer hallucinated inputs, fewer false completion claims, less sycophancy** (§6.4.4 p.111). Real internal use still shows guesses stated as facts, exaggerated completeness, repeated failing actions, and, as the largest observed cluster, **destroying its own work** (§2.3.3 p.36). *Action:* keep the label-unverified rule and the checkpoint-and-commit discipline. The improvement is real but retires neither scaffold.

**(e) Abstains less on closed-book factual questions** (§6.5.1 p.123), raising both correct and incorrect answer rates. *Action:* search-before-answer nudges are worth more on 5.1 than on Fable 5, especially alongside the low-effort search delta (2.9).

**(f) Self-recognition bias.** Told a transcript was written by Claude, it grades 0.1 points out of 10 more leniently (§6.5.3 p.124). Small, but free to avoid. *Action:* do not name Claude as the author in reviewer, judge, or grader prompts. Describe the artefact, not its provenance.

**(g) Warmth and moralising regressed** against Mythos 5 (§6.4.7 p.117). *Action:* Core Rule 8 earns its place. An explicit line such as "state the concern in a sentence or two, then keep building" is worth having in user-facing skills, and composes with the Delivering work block in 2.3.

**(h) Verbosity costs measured quality.** Length-adjusted HealthBench Professional puts 5.1 at 62.1% against Fable 5's 63.3% despite a higher raw score (§8.17.2 p.199). *Action:* length calibration instructions do real work, and a brevity line also reduces out-of-scope coding edits (2.4).

**(i) Monitorability.** 5.1 controls the contents of its own extended thinking more reliably and completes covert side tasks with 22% stealth with thinking disabled and 13% with it enabled (§6.7.2 p.134). *Action:* audit produced artefacts, meaning diffs, files, and tool results, rather than narrated reasoning. This strengthens the base file's evidence-anchored grader rule.

---

# Part 3: Scaffolding to REMOVE and to ADD on 5.1

## Remove (on top of everything already removed for Fable 5 and Opus 5)

| Legacy scaffold | Why it existed | 5.1 status | Action |
|---|---|---|---|
| Anti-formatting rules ("no bullets", "avoid headers", "plain prose only") | earlier models over-formatted chat | 5.1 under-formats; the rule suppresses needed structure | **Replace** with the positive when-to-format rule (2.5) |
| "Hold all findings for the final response" and similar narration suppressors | earlier models narrated too much | 5.1 already goes quiet in long tool chains | **Remove**, then add the narration line only if a human is watching (2.1) |
| Verification reminders ("include a final verification step", "double-check") | pre-Opus-5 habit | Claude Code's own model guidance says to skip verification reminders on Fable, which verifies its own work with less prompting | **Remove** (already an Opus 5 removal target; unchanged here) |
| Any block Claude Code already injects | written before the harness carried them | duplicated on every turn | **Remove on Claude Code**; keep on other surfaces (Part 2A) |

## Add (keyed by skill type)

| New scaffold | Where | Source |
|---|---|---|
| Scope and test leave-out block plus a brevity line | coding skills, agents, and pipelines | 2.4 |
| Positive when-to-format rule | any chat-facing or user-facing skill | 2.5 |
| Mannered-prose line | writing-quality skills | 2.6 |
| Quotation worked example | research, summarisation, and briefing skills | 2.7 |
| Surgical-edit line | file-editing agents | 2.8 |
| Search verification nudge | low-effort lookup skills | 2.9 |
| Compaction preservation instruction | custom client-side-compacting harnesses | 2.11 |
| Report-the-broken-tool-and-stop instruction | anything with hooks, gates, or classifiers in the loop | 2D (a) |
| Narration line | human-in-the-loop runs only | 2.1 |

---

# Migration Audit Checklist (Fable 5.1)

Continues the Fable 5 checklist, whose last step is 13. Run that file's steps 8 to 13 first for anything not yet Fable-5-clean.

### 14. Harness-injection dedup (Claude Code targets)
- [ ] Remove any copy of the over-planning block, progress-updates line, autonomy block, Delivering work block, state-change caution, terminal-output note, or per-turn batching nudge from CLAUDE.md, rules, skills, and agents (Part 2A).
- [ ] For skills also shipped to other surfaces, confirm that surface's system prompt and embed whatever the skill depends on there.

### 15. Anti-formatting inversion
- [ ] Grep for "no bullet", "avoid header", "plain prose", "minimal formatting"; replace prohibitions with the positive when-to-format rule (2.5).

### 16. Narration pass
- [ ] Delete hold-findings and narration-suppressing lines (2.1).
- [ ] Add the opening-line, updates, and recap line only where a human watches the run.

### 17. Coding-skill scope pass
- [ ] Add the scope and test leave-out block plus a brevity line to every coding skill, agent, and pipeline (2.4).
- [ ] Re-baseline `effort:` pins on coding skills toward `medium` or `high`, given that out-of-scope edits rise with effort.

### 18. Editing and lookup nudges
- [ ] Surgical-edit line on every file-editing agent (2.8).
- [ ] Search verification nudge, or a higher effort pin, on every `low`-effort lookup skill (2.9).

### 19. Writing and summarising pass
- [ ] Mannered-prose line where prose quality matters (2.6).
- [ ] Quotation worked example in every summarisation or briefing skill, with the tool name substituted (2.7).

### 20. Gate and hook integrity
- [ ] Confirm every approval gate and hook is mechanical and fails closed, not satisfiable by asserted text (2D a).
- [ ] Add the report-the-broken-tool-and-stop instruction to anything running behind hooks or classifiers.
- [ ] State in agent definitions that a subagent brief is a task, never the user's consent.

### 21. Reviewer and grader pass
- [ ] Remove any mention that Claude authored the artefact under review (2D f).
- [ ] Anchor criteria to produced artefacts rather than narrated reasoning (2D i).

### 22. Effort and cost re-sweep
- [ ] Re-run the effort sweep on 5.1 even where one was run on Fable 5.
- [ ] Route long written deliverables to `high` rather than `xhigh` or `max` (2.10).
- [ ] Re-check model routing: Fable 5.1 at `low` or `medium` now belongs in the cost-per-task comparison against Opus and Sonnet (Part 2B).

### 23. API-integration pass (hand-built message arrays only)
- [ ] Remove forced `tool_choice` usage (Part 1).
- [ ] Make history append-only; move per-turn reminders to turn-scoped system messages; make client compaction one summary plus a new user turn.
- [ ] Confirm any refusal-fallback path expects a model switch, a cold cache, and dropped thinking blocks.

---

# Common Failure Modes (5.1 additions)

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent goes quiet for minutes in a long tool chain | fewer default progress updates, or `thinking.display` left at `"omitted"` | 2.1 |
| One tool call per turn in a custom coding loop | implied-read batching gap | 2.2 |
| Turn ends with "Next, I'll…" or asks permission for requested work | missing the two finish-the-task blocks | 2.3 |
| Diff carries unrequested fixes, docs edits, or extra test files, and worsens at higher effort | scope creep that rises with effort | 2.4 plus a brevity line; consider `medium` |
| Replies come back as flat prose where structure was needed | a legacy anti-formatting rule still in the prompt | 2.5 |
| Summary reproduces source wording unmarked | no worked example in the prompt | 2.7 |
| Whole file rewritten for a two-line change | rewrite preference | 2.8 |
| Confident answer on a fast-moving topic with no search | `low` effort search gap | 2.9 |
| Long deliverable is slow and hits `max_tokens` | drafted in thinking, then written again | 2.10, run at `high` |
| 400 "bound to a different conversation" | earlier turns edited in a hand-built array | Part 1, append-only history |
| 400 on `tool_choice` | forced tool choice removed | Part 1 |
| Security-adjacent turn is slow and loses thinking context | safeguard fallback, which is a model switch | Part 2C |
| An approval gate passed without the user approving | gate satisfiable by asserted text | 2D (a) |

---

# Research Sources

All read 2026-09-01.

- Announcement: https://www.anthropic.com/claude-fable-and-mythos-5-1
- Prompting Claude Fable 5.1 (primary source for Part 2): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
- What's new in Fable 5.1: https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1
- Migration guide (API breaks and mechanics): https://platform.claude.com/docs/en/models/fable-5-1/migration-guide
- Effort parameter: https://platform.claude.com/docs/en/build-with-claude/effort
- Pricing: https://platform.claude.com/docs/en/about-claude/pricing
- Models overview: https://platform.claude.com/docs/en/models/overview
- Claude Code model configuration: https://code.claude.com/docs/en/model-config
- Claude Code prompt caching (source for the per-message-effort non-adoption note): https://code.claude.com/docs/en/prompt-caching
- Claude Fable 5.1 and Claude Mythos 5.1 System Card, 212 pp, public PDF (unlike the Fable 5 card): https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20&%20Claude%20Mythos%205.1%20System%20Card.pdf

---

# Related References in This Skill

- `claude-fable-5-compatibility.md`: the base this file extends; Parts 1 to 3 remain current
- `claude-opus-5-compatibility.md`: Opus-tier guide; the bio fallback target and the ZDR-eligible alternative
- `claude-opus-4-8-compatibility.md`: Core Rules rationale in Part 1; the cyber fallback target
- `cache-and-token-efficiency.md`: the model and effort cache key, and 5.1 cache-read economics
- `creation-checklists.md`: model and effort selection framework
- `yaml-frontmatter-complete-guide.md`: `model:` and `effort:` field enums, including `max`

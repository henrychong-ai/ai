# Statusline Configuration

Complete documentation for the Claude Code statusline hook. Last updated: 2026-11-03 (plugin 1.6.0).

> **⚠️ ccusage schema landmine (fixed 2026-06-10):** ccusage v20 renamed `daily[].date` → `daily[].period` and split rows by `agent` (the `"all"` row is the aggregate; per-agent rows e.g. `codex` also appear). A statusline querying `.date` silently gets no match → cached daily cost reads `0` → "$0.00 today" while `ccusage daily` (table output) looks fine. The `blocks -j` schema (`isActive`/`costUSD`) was unchanged. If the daily cost flatlines at $0 after a ccusage major bump, diff `ccusage daily -j | head` field names against the jq in the refresher first.

## Location

```
~/.claude/settings.json → statusLine
```

### Settings Object

```json
"statusLine": {
  "type": "command",
  "command": "...",
  "padding": 0
}
```

| Key | Value | Purpose |
|-----|-------|---------|
| `type` | `"command"` | Execute shell command for statusline content |
| `command` | (see Complete Command below) | Shell script that outputs the statusline string |
| `padding` | `0` | Removes default padding around statusline output (tighter display) |

## Output Format

Two-line display (CC allocates rows by counting `\n`):

```
Line 1: repos │ main │ 🤖 Fable 5 [xhigh] | 🧠 146k/1000k (15%)
Line 2: 💰 $21.13 today / $21.13 block (4h 25m) | 📊 5h: 25% / 7d: 21% / Fable: 6%
```

On a plan with no 5-hour usage window (see [Plans Without a 5-Hour Window](#plans-without-a-5-hour-window)), line 2 drops the 5h segment and the ccusage block cost with its countdown:

```
Line 2: 💰 $21.13 today | 📊 7d: 21% / Fable: 6%
```

### Block Layout (for rearranging)

Each block is an independent `printf` argument. To reorder, swap the variable positions in the two printf statements (with-git-branch and without-git-branch).

**Line 1 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `repos` | `$(basename "$current_dir")` | **Local filesystem** (`pwd`) | Current directory name |
| 2 | `main` | `$git_branch` | **Git** (`git branch --show-current`) | Git branch (omitted if not in repo) |
| 3 | `🤖 Opus 4.6 [medium]` | `$model [$effort]` | **CC JSON stdin** (`.model.display_name` + `.effort.level`) | Current model + **live per-session** effort; falls back to settings.json `.modelSettings[<model.id>].effortLevel`, then the top-level `.effortLevel` (skipped for `claude-opus-5-5`), then `auto` (see [Effort Level](#effort-level-per-session)) |
| 4 | `🧠 146k/1000k (15%)` | `$ctx_str` | **CC JSON stdin** (`.context_window.current_usage`) | Context window usage (v2.0.70+) |

**Line 2 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `💰 $21.13 today / $21.13 block (4h 25m)` | `$cost_str` | **ccusage** (cached) + **CC stdin** (`rate_limits.five_hour.resets_at`, CodexBar reset as fallback) | Daily/block cost + time remaining; block cost and countdown only when the plan has a 5h window (`has_5h`) |
| 2 | `📊 5h: 25% / 7d: 21% / Fable: 6%` | `$usage_str` | **CC JSON stdin** (`.rate_limits`) + **CodexBar cache** (optional) + **`~/.claude.json`** (`.cachedUsageUtilization`) | 5h (only when `has_5h`) / 7d utilization + Fable weekly (model-scoped; `*` suffix = newest source >1h old) |

### Available CC JSON Stdin Fields (unused)

These fields are available from CC's JSON stdin but not currently displayed:

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `cost.total_cost_usd` | number | `2.37` | Session cost (native CC, no ccusage needed) |
| `cost.total_duration_ms` | number | `43521946` | Session wall-clock duration |
| `cost.total_api_duration_ms` | number | `180872` | Time spent waiting on API |
| `cost.total_lines_added` | number | `156` | Lines of code added this session |
| `cost.total_lines_removed` | number | `23` | Lines of code removed this session |
| `version` | string | `"2.1.80"` | Claude Code version |
| `session_id` | string | UUID | Unique session identifier |
| `session_name` | string | `"my session"` | Session name (if renamed) |
| `vim.mode` | string | `"NORMAL"` | Vim mode (only present when enabled) |
| `agent.name` | string | `"security-reviewer"` | Agent name (only when `--agent` used) |
| `context_window.used_percentage` | number | `44` | Pre-calculated context % (alternative to manual calc) |
| `context_window.remaining_percentage` | number | `56` | Pre-calculated remaining % |
| `exceeds_200k_tokens` | boolean | `false` | Whether context exceeds 200k |
| `transcript_path` | string | path | Path to session transcript file |
| `output_style` | string | `null` | Active output style |

### Data Sources

1. **CC JSON stdin** (instant, piped by Claude Code each render) — model, context window, rate limits (5h/7d), session cost/duration/lines
2. **ccusage CLI** (background refresh, 60s cache at `/tmp/claude-ccusage-cache.json`) — daily/block costs
3. **`~/.claude.json` → `.cachedUsageUtilization`** (CC-owned cache of `GET /api/oauth/usage`) — Fable weekly (model-scoped) utilization; see [Fable / Model-Scoped Weekly Usage](#fable--model-scoped-weekly-usage-cachedusageutilization)
4. **CodexBar CLI** (optional; background refresh, 180s cache at `/tmp/claude-codexbar-usage.json`) — account-wide 5h/7d/Fable usage used to reconcile the other sources and to detect whether the plan has a 5h window; see [CodexBar Reconciliation](#codexbar-reconciliation-optional). Without it the statusline uses sources 1–3 only

## Effort Level (per-session)

The effort block (`[high]` after the model name) reads the **live per-session** reasoning effort from CC's JSON stdin, NOT the static settings.json default.

```json
"effort": {
  "level": "high"   // low | medium | high | xhigh | max
}
```

| Property | Behaviour |
|----------|-----------|
| **Source** | `.effort.level` in CC JSON stdin — reflects the live session value, **including mid-session `/effort` changes** |
| **Per-session** | Yes. Two terminal windows running different effort levels each report their own value — no bleed-through |
| **Ultracode** | Reports as `xhigh` (not a distinct level) |
| **Absent when** | The current model does not support the effort parameter → field omitted from payload |
| **Fallback** | When `.effort.level` is absent, statusline reads `.modelSettings[<model.id>].effortLevel` (with any `[1m]` suffix stripped), then the top-level `.effortLevel` — except for `claude-opus-5-5`, which ignores the top-level key, so it shows `auto` — then literal `auto` |

**Saved default vs per-session override (CC 2.1.251+):**

- `/effort <level>` (typed level, or Enter in the slider / `/model` picker) **saves per model** under `~/.claude/settings.json` `.modelSettings.<model-id>.effortLevel`; it does not write the top-level `effortLevel`. Press `s` in the slider or picker for session-only. `/effort max` is always session-only.
- The top-level `effortLevel` in user settings is the legacy form: it still applies to older models with no saved entry, but **Opus 5.5 and later ignore it** and start at their own default. The command therefore skips the top-level key for `claude-opus-5-5`. When another model that ignores the top-level key has no saved entry (Sonnet 5.5, for example), the fallback still shows the top-level value; add its id to the exception in the jq expression if that matters to you. This only applies when `.effort.level` is absent from stdin.
- Model follows the same split: `/model` picker + confirm saves; `s` = session-only.

**Landmine (pre-2026-06-10 bug):** the old statusline read effort from `jq '.effortLevel' settings.json` — the static *global default*. If you set a different default elsewhere (e.g. Fable 5 / `xhigh`), EVERY window showed that default regardless of the session's real effort. Model displayed correctly (from stdin) while effort was stale (from file) — the tell-tale asymmetry. Fixed by reading `.effort.level` from stdin. There is no on-disk per-session effort state (`~/.claude.json` per-project entry has only `lastModelUsage` token counts, no live effort) — stdin is the only source.

## Data Flow

```
Claude Code JSON stdin ──┬── model.display_name ──────────────────────────────┐
                         ├── effort.level (LIVE per-session; primary source) ──┤
                         ├── context_window.current_usage ────────────────────┤
                         ├── rate_limits.five_hour.used_percentage ────────────┤
                         ├── rate_limits.seven_day.used_percentage ────────────┤
                         ├── rate_limits.five_hour.resets_at ─────────────────┤
                         │   (also available: cost.*, version, session_id)    │
settings.json ───────────┤── modelSettings.<id>.effortLevel, then top-level effortLevel (FALLBACK only) ──┤
                         │                                                    │
ccusage cache (/tmp/claude-ccusage-cache.json, 60s TTL) ──────────────────────┤
  └── daily/block costs (read first, background refresh in-statusline)        │
~/.claude.json .cachedUsageUtilization (CC-owned /api/oauth/usage cache) ─────┤
  └── Fable weekly % (model-scoped)                                           │
CodexBar cache (/tmp/claude-codexbar-usage.json, 180s refresh; OPTIONAL) ─────┤
  └── account-wide 5h/7d/Fable %, h5 (has a 5h window?)                       │
                                                                              │
          has_5h + merge (max within window; Fable = newest; '*' when >1h old)│
                                                                              │
                      Line 1: dir │ branch │ model | ctx          ◄───────────┘
                      Line 2: cost (daily [/ block + time remaining]) | usage ([5h /] 7d / Fable)
                                          │
                      /tmp/claude-usage-log.csv (append, rotated >500KB; 5h empty when hidden)
```

**Key Design Principles:**
- Rate limit data comes directly from CC's JSON stdin — always fresh, no external polling
- ccusage still refreshes in-statusline (local CLI, no API rate limit concern)
- Read cache FIRST for ccusage, display immediately — statusline never blocks on network calls

## Native Rate Limits (CC v2.1.80+)

As of CC v2.1.80, utilization data is provided natively in the JSON stdin via `.rate_limits`:

```json
"rate_limits": {
  "five_hour": {
    "used_percentage": 25,
    "resets_at": 1773982800
  },
  "seven_day": {
    "used_percentage": 21,
    "resets_at": 1774584000
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `five_hour.used_percentage` | number | 5-hour window utilization (0-100) |
| `five_hour.resets_at` | number | Unix epoch when 5h window resets |
| `seven_day.used_percentage` | number | 7-day window utilization (0-100) |
| `seven_day.resets_at` | number | Unix epoch when 7d window resets |

**Note:** `resets_at` is a **Unix epoch** (integer), not an ISO timestamp. No date parsing needed — direct arithmetic with `$(date -u +%s)`.

**Note (verified v2.1.211, 2026-07-16):** the stdin `rate_limits` carries ONLY `five_hour` and `seven_day` — the statusline builder hard-codes those two buckets (confirmed empirically via stdin dump AND in the binary). Model-scoped buckets (`seven_day_sonnet`, `seven_day_opus`, the Fable weekly window) are NEVER forwarded to the statusline. They exist only in the OAuth API response (`/api/oauth/usage`) — read them from CC's on-disk cache instead (next section).

### Previous Architecture (archived 2026-03-20)

Before v2.1.80, utilization data required a **launchd daemon** polling the OAuth API every 300s. This was decommissioned when native `rate_limits` became available.

## Plans Without a 5-Hour Window

Added in 1.6.0 (2026-11-03). Some plans have no 5-hour usage limit (for example Claude Ultra, and Max 20x since that limit was removed). On those plans a `5h: N%` segment, the ccusage `/ $X block` cost and the `(Xh Ym)` countdown carry no meaning (ccusage blocks are locally computed 5-hour windows), so the statusline hides them. Whether stdin then omits `rate_limits.five_hour` or sends a stale one has not been verified; the detection below works either way.

**Detection (`has_5h`), first match wins:**

1. stdin `rate_limits.five_hour` present with `resets_at` in the future → show (the session's own account, so a seat that keeps the 5h limit keeps the segment);
2. CodexBar cache fresh (<30 min) → show only if its `h5` is `true` (CodexBar's `primary` window is non-null);
3. stdin `five_hour` present at all (window expired, CodexBar absent or stale) → show;
4. otherwise → hide.

When `has_5h` is 0, line 2 drops `5h: N%`, the block cost and the countdown, and the usage CSV logs an empty 5h column. Plans that still have a 5h limit see no change. Matching on the plan name was rejected (plan names change, and a plan can lose the window without a rename), as was deleting the segment outright (wrong for plans that keep the limit).

## Fable / Model-Scoped Weekly Usage (cachedUsageUtilization)

Added 2026-07-16. The `Fable: N%` segment shows the server-side **rolling 7-day Fable window** — the same number as the `/usage` screen's "Current week (Fable)" bar.

**Data chain:** Anthropic's server computes per-window utilization → CC periodically calls `GET /api/oauth/usage` (internal `fetchUtilization`) → the response `limits[]` array holds one entry per window; the Fable one is `kind == "weekly_scoped"` with `scope.model.display_name == "Fable"` (`percent`, `resets_at`, `severity`, `is_active`) → CC persists the whole payload to `~/.claude.json` under `.cachedUsageUtilization` (`{fetchedAtMs, accountUuid, utilization}`) → the statusline reads it with jq. Nothing is computed locally; being server-side, it is **account-wide across all devices/surfaces** (unlike ccusage's local-transcript estimates).

```bash
fable=$(jq -r '[.cachedUsageUtilization.utilization.limits[]? | select(.kind=="weekly_scoped" and (.scope.model.display_name // "")=="Fable") | .percent] | first // empty' ~/.claude.json 2>/dev/null)
if [ -n "$fable" ]; then
  f_ts=$(jq -r '.cachedUsageUtilization.fetchedAtMs // 0' ~/.claude.json 2>/dev/null)
  [ $((now - f_ts / 1000)) -gt 43200 ] && fable="${fable}*"   # stale marker: cache >12h old
fi
```

| Property | Behaviour |
|---|---|
| **Freshness** | Only as fresh as CC's last `/api/oauth/usage` fetch (opening `/usage`, CC's periodic fetches) — NOT per-render like the 5h/7d stdin fields. Since 1.6.0 the statusline shows whichever of this cache and the CodexBar cache is newer, and the `*` suffix flags a value older than 1h (the snippet above is the original 12h CC-cache-only form; the [Complete Command](#complete-command) is authoritative) |
| **Why not the API directly** | A statusline `curl` would need the OAuth token from the `Claude Code-credentials` keychain item — CC rewrites that item on every token refresh, wiping "Always Allow" → recurring keychain-prompt deluge. The disk cache needs no token, no network |
| **Graceful degradation** | `${fable:+ / Fable: ${fable}%}` — segment disappears if the bucket or cache key is absent (the key is CC-internal and may be renamed/reshaped by updates) |
| **Other buckets in the cache** | `seven_day_opus/sonnet/oauth_apps/cowork` (null unless your plan includes them), `extra_usage` (overage credits), `spend`, one-off codename grants (`cinder_cove` = Claude Code and Cowork credit) |

## CodexBar Reconciliation (optional)

**Problem:** (a) stdin `rate_limits` is each session's own last API response, so idle or parallel sessions show different 5h/7d values and a fresh session shows 0%; (b) the Fable value comes only from `.cachedUsageUtilization`, which refreshes only when CC fetches `/api/oauth/usage`, so it can lag by an hour or more.

**Fix:** when the [CodexBar](https://codexbar.app/) CLI is installed at `/opt/homebrew/bin/codexbar`, the statusline refreshes `/tmp/claude-codexbar-usage.json` in the background at most every 180s (throttled by `/tmp/claude-codexbar-usage.stamp`, so a failing CLI is not respawned on every render) via `codexbar usage --provider claude --format json`. The cache holds `{ts,h5,p,pr,s,sr,f}`: write time, whether the account has a 5h window, 5h percent and reset, 7d percent and reset, Fable weekly percent (`p` is `null` when there is no 5h window).

| Rule | Behaviour |
|---|---|
| **Merge (`merge_usage`)** | Usage only rises within a window, so the same `resets_at` (±300s) → **max(stdin, CodexBar)**; a different window → whichever has the later reset |
| **Staleness** | CodexBar cache older than 30 min → ignored, stdin only |
| **Fable** | Whichever of the CodexBar cache and CC's `.cachedUsageUtilization` is newer; `*` when that value is older than 1h |
| **5h countdown** | Falls back to CodexBar's 5h reset when stdin has none |
| **5h window detection** | The cache's `h5` feeds `has_5h` (see [Plans Without a 5-Hour Window](#plans-without-a-5-hour-window)) |
| **Absent** | No CodexBar binary → the refresh returns immediately and the statusline behaves as with sources 1–3 only |

**Landmine — null `round` (fixed in 1.6.0):** the cache writer used to run `.primary.usedPercent | round`, and jq's `round` errors on `null`. On a plan with no 5h window the whole jq expression failed, the cache was never written, and the 7d/Fable reconciliation silently stopped with no error. The writer is now null-safe, records `h5`, and writes nothing unless the payload has a `secondary` (weekly) window, so an error payload cannot pass for "no 5h window".

**Landmine — silent loss of the feed:** the refresh is guarded by `[ -x /opt/homebrew/bin/codexbar ] || return`, so if the binary link goes missing (for example after an interrupted Homebrew upgrade) nothing errors: the cache stops updating and after 30 minutes is ignored, and 5h/7d fall back to the session's own `rate_limits`. Check with `ls -l /opt/homebrew/bin/codexbar` and the cache file's modification time (`stat -f %m /tmp/claude-codexbar-usage.json`).

## Debugging: Dump the Statusline Stdin JSON

To see exactly what CC pipes to the statusline (authoritative for the running version — beats guessing from docs), run a throwaway nested session whose statusline dumps stdin to a file:

```bash
cat > /tmp/sl-override.json <<'EOF'
{"statusLine": {"type": "command", "command": "f=/tmp/sl-dumps/dump-$(date +%s)-$RANDOM.json; cat > \"$f\"; echo ok", "padding": 0}}
EOF
mkdir -p /tmp/sl-dumps
{ sleep 8; printf 'hi\r'; sleep 24; } | script -q /tmp/sl-capture.txt gtimeout -s TERM 34 claude --settings /tmp/sl-override.json
```

- `gtimeout` is GNU `timeout` from coreutils (`brew install coreutils` on macOS); on Linux use `timeout`.
- `rate_limits` only populates **after a real API request** — hence the injected `hi` prompt.
- Launching from inside a CC session: prefix `env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT`.
- The same piped-keystrokes + `script` pseudo-TTY pattern drives TUI slash commands (e.g. `/usage`) for screen capture, and bare `script -q cap.txt gtimeout 15 claude` captures flash-then-vanish pre-TUI startup output.

## Complete Command

Verbatim copy of `configs/statusline.json` → `.statusLine.command` (plugin 1.6.0). The config file is authoritative; re-copy after every change (`jq -r '.statusLine.command' configs/statusline.json`).

```bash
input=$(cat)
current_dir=$(pwd)
git_branch=$(git branch --show-current 2>/dev/null)
model=$(echo "$input" | jq -r '.model.display_name // "?"')
effort=$(echo "$input" | jq -r '.effort.level // empty')
model_id=$(echo "$input" | jq -r '.model.id // empty' | sed 's/\[.*\]$//')
effort=${effort:-$(jq -r --arg m "$model_id" '.modelSettings[$m].effortLevel // (if $m == "claude-opus-5-5" then "auto" else (.effortLevel // "auto") end)' ~/.claude/settings.json 2>/dev/null)}
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
current_usage=$(echo "$input" | jq '.context_window.current_usage // null')
if [ "$current_usage" != "null" ]; then
  ctx_tokens=$(echo "$current_usage" | jq '(.input_tokens // 0) + (.output_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0)')
  ctx_pct=$((ctx_tokens * 100 / context_size)); ctx_k=$((ctx_tokens / 1000)); size_k=$((context_size / 1000))
  ctx_str="🧠 ${ctx_k}k/${size_k}k (${ctx_pct}%)"
else
  ctx_str="🧠 0k/200k (0%)"
fi
now=$(date +%s)
# ccusage daily/block cost, cached 60s, refreshed in the background
ccusage_cache="/tmp/claude-ccusage-cache.json"
refresh_ccusage_bg() {
  if [ -f /tmp/claude-ccusage.lock ]; then lock_ts=$(stat -f %m /tmp/claude-ccusage.lock 2>/dev/null || echo 0); [ $((now - lock_ts)) -gt 120 ] && rm -f /tmp/claude-ccusage.lock || return; fi
  ( echo $$ > /tmp/claude-ccusage.lock; trap 'rm -f /tmp/claude-ccusage.lock' EXIT; today=$(date +%Y-%m-%d); tmp="${ccusage_cache}.tmp.$$"
    daily=$(ccusage daily -j 2>/dev/null | jq -r '[.daily[] | select(.period == "'$today'" and .agent == "all") | .totalCost] | add // 0')
    block=$(ccusage blocks -j 2>/dev/null | jq -r '.blocks[] | select(.isActive == true) | .costUSD // 0')
    echo "{\"daily\":\"${daily:-0}\",\"block\":\"${block:-0}\"}" > "$tmp"
    if jq -e . "$tmp" >/dev/null 2>&1; then mv "$tmp" "$ccusage_cache"; else rm -f "$tmp"; fi
    rm -f /tmp/claude-ccusage.lock ) &>/dev/null & disown 2>/dev/null
}
daily_fmt=$(printf '%.2f' "$(jq -r '.daily // 0' "$ccusage_cache" 2>/dev/null)" 2>/dev/null); daily_fmt=${daily_fmt:-0.00}
block_fmt=$(printf '%.2f' "$(jq -r '.block // 0' "$ccusage_cache" 2>/dev/null)" 2>/dev/null); block_fmt=${block_fmt:-0.00}
# Rate limits from stdin. A missing five_hour window ("-") means the plan has no 5-hour limit.
read -r five_hr s5r seven_day s7r <<EOF_RL
$(echo "$input" | jq -r '[(.rate_limits.five_hour.used_percentage | if . == null then "-" else round end), (.rate_limits.five_hour.resets_at // 0 | floor), (.rate_limits.seven_day.used_percentage // 0 | round), (.rate_limits.seven_day.resets_at // 0 | floor)] | map(tostring) | join(" ")' 2>/dev/null)
EOF_RL
five_hr=${five_hr:--}; s5r=${s5r:-0}; seven_day=${seven_day:-0}; s7r=${s7r:-0}
# CodexBar (optional): account-wide usage, cached 180s; h5=false when the account has no 5-hour window
cb_cache="/tmp/claude-codexbar-usage.json"; cb_stamp="/tmp/claude-codexbar-usage.stamp"
refresh_cb_bg() {
  [ -x /opt/homebrew/bin/codexbar ] || return; touch "$cb_stamp"
  ( tmp="${cb_cache}.tmp.$$"
    /opt/homebrew/bin/codexbar usage --provider claude --format json 2>/dev/null | jq -c --argjson ts "$now" '.[0].usage | select(. != null and .secondary != null) | {ts:$ts, h5:(.primary != null), p:(.primary.usedPercent | if . == null then null else round end), pr:((.primary.resetsAt | fromdateiso8601?) // 0), s:(.secondary.usedPercent | round), sr:((.secondary.resetsAt | fromdateiso8601?) // 0), f:([.extraRateWindows[]? | select(.id=="claude-weekly-scoped-fable") | .window.usedPercent | round] | first)}' > "$tmp" 2>/dev/null
    if [ -s "$tmp" ]; then mv "$tmp" "$cb_cache"; else rm -f "$tmp"; fi ) &>/dev/null & disown 2>/dev/null
}
cb_stamp_ts=$(stat -f %m "$cb_stamp" 2>/dev/null || echo 0); [ $((now - cb_stamp_ts)) -gt 180 ] && refresh_cb_bg
cb_ts=0; cb_p="-"; cb_pr=0; cb_s="-"; cb_sr=0; cb_f="-"; cb_h5="-"
if [ -f "$cb_cache" ]; then
  read -r cb_ts cb_p cb_pr cb_s cb_sr cb_f cb_h5 <<EOF_CB
$(jq -r '[.ts // 0, .p, .pr // 0, .s, .sr // 0, .f, .h5] | map(if . == null or . == "" then "-" else tostring end) | join(" ")' "$cb_cache" 2>/dev/null)
EOF_CB
fi
cb_ts=${cb_ts:-0}; cb_fresh=0; [ $((now - cb_ts)) -lt 1800 ] && cb_fresh=1
# Show the 5h window only if one exists: live stdin window, else fresh CodexBar, else any stdin window
if [ "$five_hr" != "-" ] && [ "$s5r" -gt "$now" ]; then has_5h=1
elif [ "$cb_fresh" = 1 ] && [ "$cb_h5" != "-" ]; then [ "$cb_h5" = "true" ] && has_5h=1 || has_5h=0
elif [ "$five_hr" != "-" ]; then has_5h=1
else has_5h=0; fi
# Usage is monotonic within a window: same reset (±300s) -> max; different window -> later reset wins
merge_usage() { case "$3" in ''|-|*[!0-9]*) echo "$1"; return;; esac; d=$(( $2 - $4 )); [ "$d" -lt 0 ] && d=$((-d)); if [ "$2" -eq 0 ] || [ "$d" -lt 300 ]; then if [ "$3" -gt "$1" ]; then echo "$3"; else echo "$1"; fi; elif [ "$4" -gt "$2" ]; then echo "$3"; else echo "$1"; fi; }
if [ "$has_5h" = 1 ]; then
  [ "$five_hr" = "-" ] && { five_hr=0; s5r=0; }
  [ "$cb_fresh" = 1 ] && five_hr=$(merge_usage "$five_hr" "$s5r" "$cb_p" "${cb_pr:-0}")
fi
[ "$cb_fresh" = 1 ] && seven_day=$(merge_usage "$seven_day" "$s7r" "$cb_s" "${cb_sr:-0}")
# Fable weekly: newer of CC's OAuth-usage cache and CodexBar; '*' when older than 1h
fable=$(jq -r '[.cachedUsageUtilization.utilization.limits[]? | select(.kind=="weekly_scoped" and (.scope.model.display_name // "")=="Fable") | .percent] | first // empty' ~/.claude.json 2>/dev/null)
f_ts=$(jq -r '(.cachedUsageUtilization.fetchedAtMs // 0) / 1000 | floor' ~/.claude.json 2>/dev/null); f_ts=${f_ts:-0}
case "$cb_f" in ''|-|*[!0-9]*) ;; *) if [ -z "$fable" ] || [ "$cb_ts" -gt "$f_ts" ]; then fable=$cb_f; f_ts=$cb_ts; fi;; esac
[ -n "$fable" ] && [ $((now - f_ts)) -gt 3600 ] && fable="${fable}*"
# Cost line: the ccusage 5h block and its countdown only mean something when the plan has a 5h window
if [ "$has_5h" = 1 ]; then
  reset_epoch=$s5r; [ "$reset_epoch" -gt 0 ] 2>/dev/null || reset_epoch=${cb_pr:-0}
  time_left=""; remaining=$((reset_epoch - now))
  [ "$reset_epoch" -gt 0 ] && [ "$remaining" -gt 0 ] && time_left=" ($((remaining / 3600))h $(((remaining % 3600) / 60))m)"
  cost_str="💰 \$$daily_fmt today / \$$block_fmt block$time_left"
  usage_str="📊 5h: ${five_hr}% / 7d: ${seven_day}%${fable:+ / Fable: ${fable}%}"; five_log=$five_hr
else
  cost_str="💰 \$$daily_fmt today"
  usage_str="📊 7d: ${seven_day}%${fable:+ / Fable: ${fable}%}"; five_log=""
fi
if [ -f "$ccusage_cache" ]; then [ $((now - $(stat -f %m "$ccusage_cache" 2>/dev/null || echo 0))) -gt 60 ] && refresh_ccusage_bg; else refresh_ccusage_bg; fi
if [ -f /tmp/claude-usage-log.csv ]; then sz=$(stat -f %z /tmp/claude-usage-log.csv 2>/dev/null || echo 0); [ "$sz" -gt 512000 ] && { tail -1000 /tmp/claude-usage-log.csv > /tmp/claude-usage-log.csv.tmp && mv /tmp/claude-usage-log.csv.tmp /tmp/claude-usage-log.csv; }; fi
echo "$now,$five_log,$seven_day,0" >> /tmp/claude-usage-log.csv
if [ -n "$git_branch" ]; then
  printf "%s │ %s │ 🤖 %s [%s] | %s\n%s | %s" "$(basename "$current_dir")" "$git_branch" "$model" "$effort" "$ctx_str" "$cost_str" "$usage_str"
else
  printf "%s │ 🤖 %s [%s] | %s\n%s | %s" "$(basename "$current_dir")" "$model" "$effort" "$ctx_str" "$cost_str" "$usage_str"
fi
```

## Context Window Calculation

The `current_usage` field (added in v2.0.70) provides accurate context window data:

```json
"context_window": {
  "context_window_size": 200000,
  "current_usage": {
    "input_tokens": 8500,
    "output_tokens": 1200,
    "cache_creation_input_tokens": 5000,
    "cache_read_input_tokens": 2000
  }
}
```

**Calculation (CC 2.1.0+):**
```
ctx_tokens = input_tokens + output_tokens + cache_creation_input_tokens + cache_read_input_tokens
ctx_pct = ctx_tokens * 100 / context_window_size
```

**Note:** As of CC 2.1.0, the `/context` command displays the autocompact buffer as a **separate reserved space** line item, not included in the usage percentage. The statusline calculation matches this behavior.

## Cache Files

### /tmp/claude-ccusage-cache.json

ccusage cost data cached for 60 seconds:

```json
{
  "daily": "16.33",
  "block": "6.85"
}
```

**Refresh trigger:** File modified time > 60 seconds ago

### /tmp/claude-codexbar-usage.json (optional)

CodexBar usage cache, refreshed in the background at most every 180s (`/tmp/claude-codexbar-usage.stamp` throttles attempts) and ignored once older than 30 minutes. Written only when CodexBar is installed and its payload has a weekly window:

```json
{"ts": 1793661432, "h5": false, "p": null, "pr": 0, "s": 19, "sr": 1793980800, "f": 6}
```

### /tmp/claude-usage-log.csv

Append-only log for ratio analysis (rotated >500KB → keep last 1000 lines):

```
timestamp,5h%,7d%,sonnet%
1765864379,25,20,2
1773979340,8,0,0
1793661432,,19,0
```

The 5h column is empty when the plan has no 5-hour window (since 1.6.0).

**Note:** Sonnet column is `0` since v2.1.80 migration (native `rate_limits` doesn't include sonnet). Historical data retains sonnet values from the OAuth daemon era.

### ~/.claude.json → .cachedUsageUtilization (CC-owned, read-only)

CC's own persisted copy of the last `GET /api/oauth/usage` response — `{fetchedAtMs, accountUuid, utilization}`, with `utilization.limits[]` holding the per-window buckets (session / weekly_all / weekly_scoped-Fable). The statusline only reads it; CC refreshes it on its own schedule. Never write to it.

## Dependencies

- **jq**: JSON processor (for parsing stdin JSON and cache files)
- **ccusage**: Global binary on PATH (`npm install -g ccusage` or `bun add -g ccusage`), for daily/block costs
- **CodexBar** (optional): CLI at `/opt/homebrew/bin/codexbar`, for account-wide usage reconciliation and 5h-window detection; the statusline degrades gracefully without it
- **macOS**: BSD `stat -f` throughout, and the CodexBar path is a Homebrew path

## Error Prevention

1. **Lock file guard**: Prevents concurrent ccusage process storms (`/tmp/claude-ccusage.lock`)
2. **Trap cleanup**: `trap 'rm -f lockfile' EXIT` ensures lock removal even on crash
3. **Fallback values**: All jq queries use `// 0` or `// null` to prevent errors
4. **Silent failures**: `2>/dev/null` on all external commands
5. **Cache TTL**: 60-second ccusage refresh prevents slow statusline
6. **Null check**: Context usage gracefully handles null current_usage
7. **Usage CSV rotation**: `/tmp/claude-usage-log.csv` trimmed to 1000 lines when > 500KB
8. **Stale lock cleanup**: Lock files older than 120s are removed (prevents permanent stuck state)
9. **CodexBar throttle and null safety**: the stamp file limits CodexBar attempts to one per 180s; the cache writer tolerates a null 5h window and writes atomically only on a valid payload

## Time Remaining Calculation

The `(Xh Ym)` time remaining is calculated from CC stdin `rate_limits.five_hour.resets_at` (falling back to the CodexBar 5h reset), and is shown only when the plan has a 5h window (`has_5h`). Simplified form:

```bash
reset_epoch=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
# Returns Unix epoch (e.g., 1773982800)

now_utc=$(date -u +%s)
remaining=$((reset_epoch - now_utc))

hrs=$((remaining / 3600))
mins=$(((remaining % 3600) / 60))
time_left=" (${hrs}h ${mins}m)"
```

**Advantages of native `rate_limits` over former OAuth daemon:**
- **Always fresh**: Data provided on every statusline render, no polling delay
- **No external dependencies**: No daemon, no API calls, no cache files, no error flags
- **Simpler time parsing**: Unix epoch (direct arithmetic) vs ISO timestamp (date parsing)

## Line Wrapping Fix (Resolved)

**Problem:** Single-line output (~130+ chars) gets clipped in narrow terminals. CC allocates row height by counting `\n` in output — no newline = 1 row reserved, so excess is invisible. See [GitHub #22115](https://github.com/anthropics/claude-code/issues/22115).

**Fix (applied 2026-03-01):** Split final `printf` into 2 lines via `\n` in format string. CC counts the `\n` and allocates 2 rows.

## Version History

- **2026-11-03 (1.6.0)**: **Plans without a 5-hour window.** `has_5h` detection (live stdin window, then fresh CodexBar `h5`, then any stdin window); when there is no window, line 2 drops the 5h segment, the ccusage block cost and the countdown, and the usage CSV leaves the 5h column empty. Plans that keep the 5h limit see no change. Fixed the CodexBar cache writer, which failed on a `null` 5h window (jq `round` on null) so the cache was never written and the 7d/Fable reconciliation silently stopped; it is now null-safe, records `h5`, and writes only when the payload has a weekly window. This release also ships two changes not previously in the plugin: the optional **CodexBar reconciliation** (5h/7d max-within-window merge, Fable from the newest source, `*` = newest source >1h old instead of 12h) and the **per-model effort fallback** (`.modelSettings[<model.id>].effortLevel`, then top-level `.effortLevel` except for `claude-opus-5-5`, then `auto`). Rate limits are read in one jq call. See [Plans Without a 5-Hour Window](#plans-without-a-5-hour-window) and [CodexBar Reconciliation](#codexbar-reconciliation-optional).
- **2026-07-16**: **Fable weekly segment.** Added `/ Fable: N%` to the 📊 usage block — server-side model-scoped rolling 7-day Fable window, read from CC's on-disk OAuth-usage cache (`~/.claude.json` → `.cachedUsageUtilization`) because the stdin `rate_limits` hard-codes only `five_hour`+`seven_day` (verified v2.1.211, empirically + in the binary). `*` suffix when cache >12h stale; segment self-removes if the bucket disappears. Also documented the stdin-dump debugging technique (`--settings` override + injected prompt).
- **2026-06-10**: **Per-session effort fix.** Effort now reads `.effort.level` from CC JSON stdin (live per-session value, incl. mid-session `/effort` changes) instead of the static settings.json `.effortLevel` global default. Falls back to settings.json default → `auto` when the model has no effort param. Fixes stale-effort bug where a global default set in another session (e.g. Fable 5 / `xhigh`) showed in ALL windows regardless of the session's real effort. See [Effort Level](#effort-level-per-session).
- **2026-03-20**: **Native `rate_limits` migration.** Replaced OAuth launchd daemon with CC's native `rate_limits` JSON stdin field (v2.1.80+). Eliminated: the OAuth polling daemon (script + launchd plist), `/tmp/claude-usage-cache.json`, `/tmp/claude-oauth-error`, `/tmp/claude-oauth-debug.log`, `/tmp/claude-oauth-launchd.log`, stale indicator (`!` suffix), OAuth cache reading, ISO timestamp parsing. Data source changed from file cache (300s stale) to CC stdin (always fresh). `resets_at` format changed from ISO timestamp to Unix epoch (simpler arithmetic). Sonnet display dropped (not in native field). ~20 lines removed from statusline command. GitHub issue #29604 resolved.
- **2026-03-15**: Added effort level display. Reads `effortLevel` from settings.json, displays as `[effort]` after model name. Shows `[auto]` when unset.
- **2026-03-08**: 5-min polling interval + error flag signalling for OAuth daemon.
- **2026-03-06**: Launchd daemon for OAuth polling. OAuth simplification — direct CC Keychain read.
- **2026-03-05**: Token invalidation on API rejection + dynamic retry-after cooldown.
- **2026-03-02**: Moved usage block from Line 1 to end of Line 2.
- **2026-03-01**: Two-line layout. Resolves line wrapping/cutoff (GitHub #22115).
- **2026-02-26**: Self-healing OAuth token refresh with 4-step resolution chain.
- **2026-02-25**: Added stale OAuth data indicator (`!` suffix).
- **2026-02-20**: Hardened OAuth cache validation.
- **2026-02-12**: Stale lock cleanup (120s timeout).
- **2026-02-08**: Lock file guards for concurrent process prevention.
- **2026-01-08**: Removed +45k autocompact buffer from context calculation.
- **2026-01-02**: Background refresh pattern, atomic writes, ccusage via bun.
- **2025-12-17**: ccusage caching (60s TTL) + time remaining from `resets_at`.
- **v2.0.70+**: Uses `current_usage` field for accurate context window percentage.


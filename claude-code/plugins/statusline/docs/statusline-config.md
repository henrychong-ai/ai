# Statusline Configuration

Complete documentation for the Claude Code statusline hook. Last updated: 2026-07-16.

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

### Block Layout (for rearranging)

Each block is an independent `printf` argument. To reorder, swap the variable positions in the two printf statements (with-git-branch and without-git-branch).

**Line 1 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `repos` | `$(basename "$current_dir")` | **Local filesystem** (`pwd`) | Current directory name |
| 2 | `main` | `$git_branch` | **Git** (`git branch --show-current`) | Git branch (omitted if not in repo) |
| 3 | `🤖 Opus 4.6 [medium]` | `$model [$effort]` | **CC JSON stdin** (`.model.display_name` + `.effort.level`) | Current model + **live per-session** effort; falls back to settings.json `.effortLevel`, then `auto` (see [Effort Level](#effort-level-per-session)) |
| 4 | `🧠 146k/1000k (15%)` | `$ctx_str` | **CC JSON stdin** (`.context_window.current_usage`) | Context window usage (v2.0.70+) |

**Line 2 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `💰 $21.13 today / $21.13 block (4h 25m)` | `$cost_str` | **ccusage** (cached) + **CC stdin** (`rate_limits.five_hour.resets_at`) | Daily/block cost + time remaining |
| 2 | `📊 5h: 25% / 7d: 21% / Fable: 6%` | `$usage_str` | **CC JSON stdin** (`.rate_limits`) + **`~/.claude.json`** (`.cachedUsageUtilization`) | 5h/7d utilization + Fable weekly (model-scoped; `*` suffix = cache >12h stale) |

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

### Three Data Sources

1. **CC JSON stdin** (instant, piped by Claude Code each render) — model, context window, rate limits (5h/7d), session cost/duration/lines
2. **ccusage CLI** (background refresh, 60s cache at `/tmp/claude-ccusage-cache.json`) — daily/block costs
3. **`~/.claude.json` → `.cachedUsageUtilization`** (CC-owned cache of `GET /api/oauth/usage`) — Fable weekly (model-scoped) utilization; see [Fable / Model-Scoped Weekly Usage](#fable--model-scoped-weekly-usage-cachedusageutilization)

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
| **Fallback** | When `.effort.level` is absent, statusline falls back to settings.json `.effortLevel` (global default), then literal `auto` |

**Global default vs per-session override (why this matters):**

- `~/.claude/settings.json` `effortLevel` = **global default for new sessions** (written by the `/effort` slider with no arg, or `/model` picker + confirm).
- In-session `/effort <level>` (e.g. `/effort high`) = **session-only override** — does NOT mutate settings.json.
- Same split for model: `/model` picker + confirm saves global; press `s` in the picker = session-only.

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
settings.json ───────────┤── effortLevel (FALLBACK only — global default) ────┤
                         │                                                    │
ccusage cache (/tmp/claude-ccusage-cache.json, 60s TTL) ──────────────────────┤
  └── daily/block costs (read first, background refresh in-statusline)        │
~/.claude.json .cachedUsageUtilization (CC-owned /api/oauth/usage cache) ─────┤
  └── Fable weekly % (model-scoped; '*' when fetchedAtMs >12h old)            │
                                                                              │
                      Line 1: dir │ branch │ model | ctx          ◄───────────┘
                      Line 2: cost (daily/block + time remaining) | usage
                                          │
                      /tmp/claude-usage-log.csv (append, rotated >500KB)
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
| **Freshness** | Only as fresh as CC's last `/api/oauth/usage` fetch (opening `/usage`, CC's periodic fetches) — NOT per-render like the 5h/7d stdin fields. Acceptable for a slow-moving 7-day window; `*` suffix flags cache older than 12h |
| **Why not the API directly** | A statusline `curl` would need the OAuth token from the `Claude Code-credentials` keychain item — CC rewrites that item on every token refresh, wiping "Always Allow" → recurring keychain-prompt deluge. The disk cache needs no token, no network |
| **Graceful degradation** | `${fable:+ / Fable: ${fable}%}` — segment disappears if the bucket or cache key is absent (the key is CC-internal and may be renamed/reshaped by updates) |
| **Other buckets in the cache** | `seven_day_opus/sonnet/oauth_apps/cowork` (null unless your plan includes them), `extra_usage` (overage credits), `spend`, one-off codename grants (`cinder_cove` = Claude Code and Cowork credit) |

## Debugging: Dump the Statusline Stdin JSON

To see exactly what CC pipes to the statusline (authoritative for the running version — beats guessing from docs), run a throwaway nested session whose statusline dumps stdin to a file:

```bash
cat > /tmp/sl-override.json <<'EOF'
{"statusLine": {"type": "command", "command": "f=/tmp/sl-dumps/dump-$(date +%s)-$RANDOM.json; cat > \"$f\"; echo ok", "padding": 0}}
EOF
mkdir -p /tmp/sl-dumps
{ sleep 8; printf 'hi\r'; sleep 24; } | script -q /tmp/sl-capture.txt gtimeout -s TERM 34 claude --settings /tmp/sl-override.json
```

- `rate_limits` only populates **after a real API request** — hence the injected `hi` prompt.
- Launching from inside a CC session: prefix `env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT`.
- The same piped-keystrokes + `script` pseudo-TTY pattern drives TUI slash commands (e.g. `/usage`) for screen capture, and bare `script -q cap.txt gtimeout 15 claude` captures flash-then-vanish pre-TUI startup output.

## Complete Command

```bash
input=$(cat)
current_dir=$(pwd)
git_branch=$(git branch --show-current 2>/dev/null)

model=$(echo "$input" | jq -r '.model.display_name // "?"')
# Effort: live per-session value from CC stdin (.effort.level); fall back to settings.json global default only when absent
effort=$(echo "$input" | jq -r '.effort.level // empty')
effort=${effort:-$(jq -r '.effortLevel // "auto"' ~/.claude/settings.json 2>/dev/null)}
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
current_usage=$(echo "$input" | jq '.context_window.current_usage // null')

if [ "$current_usage" != "null" ]; then
  ctx_tokens=$(echo "$current_usage" | jq '(.input_tokens // 0) + (.output_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0)')
  ctx_pct=$((ctx_tokens * 100 / context_size))
  ctx_k=$((ctx_tokens / 1000))
  size_k=$((context_size / 1000))
  ctx_str="🧠 ${ctx_k}k/${size_k}k (${ctx_pct}%)"
else
  ctx_str="🧠 0k/200k (0%)"
fi

now=$(date +%s)
ccusage_cache="/tmp/claude-ccusage-cache.json"

# Background ccusage refresh (local CLI, no API rate limit concern)
refresh_ccusage_bg() {
  if [ -f /tmp/claude-ccusage.lock ]; then
    lock_ts=$(stat -f %m /tmp/claude-ccusage.lock 2>/dev/null || echo 0)
    [ $((now - lock_ts)) -gt 120 ] && rm -f /tmp/claude-ccusage.lock || return
  fi
  (
    echo $$ > /tmp/claude-ccusage.lock
    trap 'rm -f /tmp/claude-ccusage.lock' EXIT
    today=$(date +%Y-%m-%d)
    tmp="${ccusage_cache}.tmp.$$"
    # ccusage v20+: daily[] entries use .period (NOT .date — renamed in v20) and are split by .agent ("all" = aggregate)
    daily=$(ccusage daily -j 2>/dev/null | jq -r '[.daily[] | select(.period == "'$today'" and .agent == "all") | .totalCost] | add // 0')
    block=$(ccusage blocks -j 2>/dev/null | jq -r '.blocks[] | select(.isActive == true) | .costUSD // 0')
    echo "{\"daily\":\"${daily:-0}\",\"block\":\"${block:-0}\"}" > "$tmp"
    if jq -e . "$tmp" >/dev/null 2>&1; then
      mv "$tmp" "$ccusage_cache"
    else
      rm -f "$tmp"
    fi
    rm -f /tmp/claude-ccusage.lock
  ) &>/dev/null & disown 2>/dev/null
}

# Read cache values (always instant)
daily_raw=$(jq -r '.daily // 0' "$ccusage_cache" 2>/dev/null)
daily_fmt=$(printf '%.2f' "${daily_raw:-0}" 2>/dev/null); daily_fmt=${daily_fmt:-0.00}
block_raw=$(jq -r '.block // 0' "$ccusage_cache" 2>/dev/null)
block_fmt=$(printf '%.2f' "${block_raw:-0}" 2>/dev/null); block_fmt=${block_fmt:-0.00}

# Native rate limits from CC stdin (v2.1.80+)
five_hr=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // 0' | xargs printf '%.0f' 2>/dev/null); five_hr=${five_hr:-0}
seven_day=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // 0' | xargs printf '%.0f' 2>/dev/null); seven_day=${seven_day:-0}

# Fable weekly (model-scoped) from CC's on-disk OAuth-usage cache; '*' = cache >12h stale
fable=$(jq -r '[.cachedUsageUtilization.utilization.limits[]? | select(.kind=="weekly_scoped" and (.scope.model.display_name // "")=="Fable") | .percent] | first // empty' ~/.claude.json 2>/dev/null)
if [ -n "$fable" ]; then
  f_ts=$(jq -r '.cachedUsageUtilization.fetchedAtMs // 0' ~/.claude.json 2>/dev/null)
  [ $((now - f_ts / 1000)) -gt 43200 ] && fable="${fable}*"
fi

# Time remaining from resets_at (Unix epoch)
reset_epoch=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
time_left=""
if [ -n "$reset_epoch" ] && [ "$reset_epoch" != "null" ]; then
  now_utc=$(date -u +%s)
  remaining=$((reset_epoch - now_utc))
  if [ "$remaining" -gt 0 ]; then
    hrs=$((remaining / 3600)); mins=$(((remaining % 3600) / 60))
    time_left=" (${hrs}h ${mins}m)"
  fi
fi

# Trigger ccusage refresh if stale
if [ -f "$ccusage_cache" ]; then
  file_ts=$(stat -f %m "$ccusage_cache" 2>/dev/null || echo 0)
  age=$((now - file_ts))
  [ "$age" -gt 60 ] && refresh_ccusage_bg
else
  refresh_ccusage_bg
fi

cost_str="💰 \$$daily_fmt today / \$$block_fmt block$time_left"

# Usage CSV log (rotated >500KB)
if [ -f /tmp/claude-usage-log.csv ]; then
  sz=$(stat -f %z /tmp/claude-usage-log.csv 2>/dev/null || echo 0)
  [ "$sz" -gt 512000 ] && { tail -1000 /tmp/claude-usage-log.csv > /tmp/claude-usage-log.csv.tmp && mv /tmp/claude-usage-log.csv.tmp /tmp/claude-usage-log.csv; }
fi
echo "$now,$five_hr,$seven_day,0" >> /tmp/claude-usage-log.csv

usage_str="📊 5h: ${five_hr}% / 7d: ${seven_day}%${fable:+ / Fable: ${fable}%}"

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

### /tmp/claude-usage-log.csv

Append-only log for ratio analysis (rotated >500KB → keep last 1000 lines):

```
timestamp,5h%,7d%,sonnet%
1765864379,25,20,2
1773979340,8,0,0
```

**Note:** Sonnet column is `0` since v2.1.80 migration (native `rate_limits` doesn't include sonnet). Historical data retains sonnet values from the OAuth daemon era.

### ~/.claude.json → .cachedUsageUtilization (CC-owned, read-only)

CC's own persisted copy of the last `GET /api/oauth/usage` response — `{fetchedAtMs, accountUuid, utilization}`, with `utilization.limits[]` holding the per-window buckets (session / weekly_all / weekly_scoped-Fable). The statusline only reads it; CC refreshes it on its own schedule. Never write to it.

## Dependencies

- **jq**: JSON processor (for parsing stdin JSON and cache files)
- **ccusage**: Global binary at `~/.bun/bin/ccusage` (installed via bun, for daily/block costs)

## Error Prevention

1. **Lock file guard**: Prevents concurrent ccusage process storms (`/tmp/claude-ccusage.lock`)
2. **Trap cleanup**: `trap 'rm -f lockfile' EXIT` ensures lock removal even on crash
3. **Fallback values**: All jq queries use `// 0` or `// null` to prevent errors
4. **Silent failures**: `2>/dev/null` on all external commands
5. **Cache TTL**: 60-second ccusage refresh prevents slow statusline
6. **Null check**: Context usage gracefully handles null current_usage
7. **Usage CSV rotation**: `/tmp/claude-usage-log.csv` trimmed to 1000 lines when > 500KB
8. **Stale lock cleanup**: Lock files older than 120s are removed (prevents permanent stuck state)

## Time Remaining Calculation

The `(Xh Ym)` time remaining is calculated from CC stdin `rate_limits.five_hour.resets_at`:

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

- **2026-07-16**: **Fable weekly segment.** Added `/ Fable: N%` to the 📊 usage block — server-side model-scoped rolling 7-day Fable window, read from CC's on-disk OAuth-usage cache (`~/.claude.json` → `.cachedUsageUtilization`) because the stdin `rate_limits` hard-codes only `five_hour`+`seven_day` (verified v2.1.211, empirically + in the binary). `*` suffix when cache >12h stale; segment self-removes if the bucket disappears. Also documented the stdin-dump debugging technique (`--settings` override + injected prompt). KG: "Claude Code Statusline Fable Usage (cachedUsageUtilization)".
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


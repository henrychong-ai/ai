# Statusline Configuration

Complete documentation for the Claude Code statusline hook.

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
Line 1: repos │ main │ 🤖 Opus 4.6 [medium] | 🧠 146k/1000k (15%)
Line 2: 💰 $21.13 today / $21.13 block (4h 25m) | 📊 5h: 25% / 7d: 21%
```

### Block Layout (for rearranging)

Each block is an independent `printf` argument. To reorder, swap the variable positions in the two printf statements (with-git-branch and without-git-branch).

**Line 1 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `repos` | `$(basename "$current_dir")` | **Local filesystem** (`pwd`) | Current directory name |
| 2 | `main` | `$git_branch` | **Git** (`git branch --show-current`) | Git branch (omitted if not in repo) |
| 3 | `🤖 Opus 4.6 [medium]` | `$model [$effort]` | **CC JSON stdin** (`.model.display_name`) + **settings.json** (`.effortLevel`) | Current model + effort level (`auto` if unset) |
| 4 | `🧠 146k/1000k (15%)` | `$ctx_str` | **CC JSON stdin** (`.context_window.current_usage`) | Context window usage (v2.0.70+) |

**Line 2 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `💰 $21.13 today / $21.13 block (4h 25m)` | `$cost_str` | **ccusage** (cached) + **CC stdin** (`rate_limits.five_hour.resets_at`) | Daily/block cost + time remaining |
| 2 | `📊 5h: 25% / 7d: 21%` | `$usage_str` | **CC JSON stdin** (`.rate_limits`) | 5h/7d utilization |

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

### Two Data Sources

1. **CC JSON stdin** (instant, piped by Claude Code each render) — model, context window, rate limits (5h/7d), session cost/duration/lines
2. **ccusage CLI** (background refresh, 60s cache at `/tmp/claude-ccusage-cache.json`) — daily/block costs

## Data Flow

```
Claude Code JSON stdin ──┬── model.display_name ──────────────────────────────┐
                         ├── context_window.current_usage ────────────────────┤
                         ├── rate_limits.five_hour.used_percentage ────────────┤
                         ├── rate_limits.seven_day.used_percentage ────────────┤
                         ├── rate_limits.five_hour.resets_at ─────────────────┤
                         │   (also available: cost.*, version, session_id)    │
settings.json ───────────┤── effortLevel ("auto" if unset) ──────────────────┤
                         │                                                    │
ccusage cache (/tmp/claude-ccusage-cache.json, 60s TTL) ──────────────────────┤
  └── daily/block costs (read first, background refresh in-statusline)        │
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

**Note:** Sonnet-specific utilization (`seven_day_sonnet`) is NOT included in the native field. Only available via the OAuth API (`/api/oauth/usage`).

### Previous Architecture (archived 2026-03-20)

Before v2.1.80, utilization data required a **launchd daemon** (`com.henrychong.claude-oauth-usage`) polling the OAuth API every 300s. This was decommissioned when native `rate_limits` became available. Daemon script and plist archived to `~/scripts/_archive/` and `~/Library/LaunchAgents/_archive/`.

## Complete Command

```bash
input=$(cat)
current_dir=$(pwd)
git_branch=$(git branch --show-current 2>/dev/null)

model=$(echo "$input" | jq -r '.model.display_name // "?"')
effort=$(jq -r '.effortLevel // "auto"' ~/.claude/settings.json 2>/dev/null)
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
    daily=$(ccusage daily -j 2>/dev/null | jq -r '.daily[] | select(.date == "'$today'") | .totalCost // 0')
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

usage_str="📊 5h: ${five_hr}% / 7d: ${seven_day}%"

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

- **2026-03-20**: **Native `rate_limits` migration.** Replaced OAuth launchd daemon with CC's native `rate_limits` JSON stdin field (v2.1.80+). Eliminated: `~/scripts/claude-oauth-usage.sh` (archived), `com.henrychong.claude-oauth-usage.plist` (archived), `/tmp/claude-usage-cache.json`, `/tmp/claude-oauth-error`, `/tmp/claude-oauth-debug.log`, `/tmp/claude-oauth-launchd.log`, stale indicator (`!` suffix), OAuth cache reading, ISO timestamp parsing. Data source changed from file cache (300s stale) to CC stdin (always fresh). `resets_at` format changed from ISO timestamp to Unix epoch (simpler arithmetic). Sonnet display dropped (not in native field). ~20 lines removed from statusline command. GitHub issue #29604 resolved.
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

## Related KG Entities

- "Statusline Block Layout and Data Sources" — current block positions, variables, and data source mapping
- "Statusline CC JSON Stdin Schema" — full schema of fields available from CC's JSON input
- "Why Statusline Shows Shell CWD Not Claude Code Workspace" — design decision for pwd vs workspace.current_dir
- "Haiku 4.5 Cost Tracking Bug - Complete Context" — known ccusage cost reporting issue
- "5h/7d Usage Ratio" — ratio analysis methodology

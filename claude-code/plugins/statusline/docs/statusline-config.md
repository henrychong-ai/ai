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
Line 1: repos │ main │ 🤖 Opus 4.6 [medium] | 🧠 146k/200k (73%)
Line 2: 💰 $21.13 today / $21.13 block (4h 25m) | 📊 5h: 25% / 7d: 21% / son: 2%
```

When OAuth data is stale (token expired, API unreachable):
```
Line 1: repos │ main │ 🤖 Opus 4.6 [medium] | 🧠 146k/200k (73%)
Line 2: 💰 $21.13 today / $21.13 block (4h 25m) | 📊 5h: 25%! / 7d: 21%! / son: 2%!
```

### Block Layout (for rearranging)

Each block is an independent `printf` argument. To reorder, swap the variable positions in the two printf statements (with-git-branch and without-git-branch).

**Line 1 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `repos` | `$(basename "$current_dir")` | **Local filesystem** (`pwd`) | Current directory name |
| 2 | `main` | `$git_branch` | **Git** (`git branch --show-current`) | Git branch (omitted if not in repo) |
| 3 | `🤖 Opus 4.6 [medium]` | `$model [$effort]` | **CC JSON stdin** (`.model.display_name`) + **settings.json** (`.effortLevel`) | Current model + effort level (`auto` if unset) |
| 4 | `🧠 146k/200k (73%)` | `$ctx_str` | **CC JSON stdin** (`.context_window.current_usage`) | Context window usage (v2.0.70+) |

**Line 2 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `💰 $21.13 today / $21.13 block (4h 25m)` | `$cost_str` | **ccusage** (cached) + **OAuth API** (`resets_at`) | Daily/block cost + time remaining |
| 2 | `📊 5h: 25% / 7d: 21% / son: 2%` | `$usage_str` | **OAuth API** (cached) | 5h/7d/sonnet utilization |

**Stale indicator:** `%!` suffix on usage values when error flag exists (last API call failed) or cache > 600s old (daemon not running).

### Available CC JSON Stdin Fields (unused)

These fields are available from CC's JSON stdin but not currently displayed:

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `cost.total_cost_usd` | number | `2.37` | Session cost (native CC, no ccusage needed) |
| `cost.total_duration_ms` | number | `43521946` | Session wall-clock duration |
| `cost.total_api_duration_ms` | number | `180872` | Time spent waiting on API |
| `cost.total_lines_added` | number | `156` | Lines of code added this session |
| `cost.total_lines_removed` | number | `23` | Lines of code removed this session |
| `version` | string | `"2.1.63"` | Claude Code version |
| `session_id` | string | UUID | Unique session identifier |
| `vim.mode` | string | `"NORMAL"` | Vim mode (only present when enabled) |
| `agent.name` | string | `"security-reviewer"` | Agent name (only when `--agent` used) |
| `context_window.used_percentage` | number | `44` | Pre-calculated context % (alternative to manual calc) |

### Three Data Sources

1. **CC JSON stdin** (instant, piped by Claude Code each render) — model, context window, session cost/duration/lines
2. **ccusage CLI** (background refresh, 60s cache at `/tmp/claude-ccusage-cache.json`) — daily/block costs
3. **launchd daemon** (300s / 5-min interval, writes `/tmp/claude-usage-cache.json`) — utilization %, time remaining. See `~/Library/LaunchAgents/com.henrychong.claude-oauth-usage.plist` and `~/scripts/claude-oauth-usage.sh`.

## Data Flow

```
Claude Code JSON stdin ──┬── model.display_name ──────────────────────────────┐
                         ├── context_window.current_usage ────────────────────┤
                         │   (also available: cost.*, version, session_id)    │
settings.json ───────────┤── effortLevel ("auto" if unset) ──────────────────┤
                         │                                                    │
ccusage cache (/tmp/claude-ccusage-cache.json, 60s TTL) ──────────────────────┤
  └── daily/block costs (read first, background refresh in-statusline)        │
                                                                              │
OAuth cache (/tmp/claude-usage-cache.json, written by launchd daemon) ────────┤
  ├── 5h/7d/son utilization (read-only by statusline)                        │
  └── five_hour.resets_at ────────────────────────────────────────────────────┤
                                                                              │
                      Line 1: dir │ branch │ model | ctx | usage  ◄───────────┘
                      Line 2: cost (daily/block + time remaining)
                                          │
                      /tmp/claude-usage-log.csv (append, rotated >500KB)
```

**Key Design Principles:**
- Read cache FIRST, display immediately — statusline never blocks on network calls
- OAuth data is updated externally by launchd daemon (single caller, no rate limit risk)
- ccusage still refreshes in-statusline (local CLI, no API rate limit concern)

## OAuth Usage Data Architecture

**As of 2026-03-06, OAuth polling is handled by a launchd daemon, not by the statusline command.**

### Architecture

```
launchd (com.henrychong.claude-oauth-usage, every 300s / 5 min)
  └── ~/scripts/claude-oauth-usage.sh
        ├── Reads OAuth token from CC Keychain
        ├── Calls https://api.anthropic.com/api/oauth/usage
        ├── Writes /tmp/claude-usage-cache.json (atomic: mktemp + mv)
        ├── On success: removes /tmp/claude-oauth-error
        ├── On failure: writes /tmp/claude-oauth-error (reason)
        └── Logs to /tmp/claude-oauth-debug.log

Statusline (read-only)
  └── Reads /tmp/claude-usage-cache.json (never writes, never calls API)
  └── Checks /tmp/claude-oauth-error for "!" indicator
```

### Why Launchd Daemon

Multiple CC sessions + Claude Desktop all sharing the same OAuth token caused aggregate polling rates that triggered the undocumented rate limit on `/api/oauth/usage` (GitHub issues #30930, #31055). A single daemon eliminates multi-session collision entirely.

### Token Source

The daemon reads CC's current access token from macOS Keychain entry `Claude Code-credentials`. CC manages token lifecycle (refresh, rotation); the daemon just reads the current access token.

### Error Handling (daemon)

| HTTP Code | Action |
|-----------|--------|
| 200 | Update cache, remove error flag, exit |
| 429 | Log, write error flag, exit. Next 5-min cycle retries |
| 401/403 | Log auth failure, write error flag, exit (next 5-min cycle retries with fresh token) |
| 000/other | Log error, write error flag, exit |

**Error flag:** `/tmp/claude-oauth-error` — contains reason string. Present = last call failed. Statusline shows `!` suffix on usage values. Cleared on next successful 200 response.

### Future

GitHub issue #29604 proposes including usage data in CC's statusline JSON stdin. If implemented, the daemon can be removed entirely.

## Complete Command (Simplified — OAuth handled by launchd daemon)

The statusline command is now read-only for OAuth data. Only ccusage still refreshes in-statusline.

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
oauth_cache="/tmp/claude-usage-cache.json"

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

five_hr=$(jq -r '.five_hour.utilization // 0' "$oauth_cache" 2>/dev/null | xargs printf '%.0f' 2>/dev/null); five_hr=${five_hr:-0}
seven_day=$(jq -r '.seven_day.utilization // 0' "$oauth_cache" 2>/dev/null | xargs printf '%.0f' 2>/dev/null); seven_day=${seven_day:-0}
sonnet=$(jq -r '.seven_day_sonnet.utilization // 0' "$oauth_cache" 2>/dev/null | xargs printf '%.0f' 2>/dev/null); sonnet=${sonnet:-0}

# Error/stale indicator (error flag = last API call failed, >600s = daemon not running)
oauth_stale=""
if [ -f /tmp/claude-oauth-error ]; then
  oauth_stale="!"
elif [ -f "$oauth_cache" ]; then
  oauth_age=$((now - $(stat -f %m "$oauth_cache" 2>/dev/null || echo $now)))
  [ "$oauth_age" -gt 600 ] && oauth_stale="!"
fi

# Time remaining from resets_at
reset_at=$(jq -r '.five_hour.resets_at // empty' "$oauth_cache" 2>/dev/null)
time_left=""
if [ -n "$reset_at" ]; then
  reset_ts="${reset_at:0:19}"
  reset_epoch=$(date -j -u -f "%Y-%m-%dT%H:%M:%S" "$reset_ts" +%s 2>/dev/null)
  if [ -n "$reset_epoch" ]; then
    now_utc=$(date -u +%s)
    remaining=$((reset_epoch - now_utc))
    if [ "$remaining" -gt 0 ]; then
      hrs=$((remaining / 3600)); mins=$(((remaining % 3600) / 60))
      time_left=" (${hrs}h ${mins}m)"
    fi
  fi
fi

# Trigger ccusage refresh if stale (OAuth handled by launchd daemon)
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
echo "$now,$five_hr,$seven_day,$sonnet" >> /tmp/claude-usage-log.csv

usage_str="📊 5h: ${five_hr}%${oauth_stale} / 7d: ${seven_day}%${oauth_stale} / son: ${sonnet}%${oauth_stale}"

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

**Note:** As of CC 2.1.0, the `/context` command displays the autocompact buffer (45k, 22.5%) as a **separate reserved space** line item, not included in the usage percentage. The statusline calculation now matches this behavior - no manual +45k addition needed.

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

**Performance:**
- Cache read: ~0.1s
- Cache refresh: ~5s (runs ccusage daily + blocks)

### /tmp/claude-usage-cache.json

Written by launchd daemon (`com.henrychong.claude-oauth-usage`) every 300 seconds (5 min):

```json
{
  "five_hour": {
    "utilization": 25.0,
    "resets_at": "2025-12-17T12:00:00.000000+00:00"
  },
  "seven_day": {
    "utilization": 21.0,
    "resets_at": "2025-12-24T02:00:00.000000+00:00"
  },
  "seven_day_sonnet": {
    "utilization": 2.0,
    "resets_at": "2025-12-18T10:00:00.000000+00:00"
  }
}
```

### /tmp/claude-usage-log.csv

Append-only log for ratio analysis (rotated >500KB → keep last 1000 lines):

```
timestamp,5h%,7d%,sonnet%
1765864379,25,20,2
1765864438,25,20,2
```

### /tmp/claude-oauth-debug.log

Debug breadcrumbs for OAuth operations. Written by launchd daemon. Rotated >50KB → keep last 20 lines. Includes HTTP status codes since 2026-03-06.

### /tmp/claude-oauth-launchd.log

Launchd stdout/stderr for the OAuth daemon process.

## Caching Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Statusline Execution                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. READ CACHE IMMEDIATELY (never blocks)                       │
│     ┌──────────────────┐      ┌──────────────────┐              │
│     │  ccusage cache   │      │   OAuth cache    │              │
│     │ (cost data)      │      │ (utilization)    │              │
│     │ (in-statusline)  │      │ (launchd daemon) │              │
│     └────────┬─────────┘      └────────┬─────────┘              │
│              │                         │                         │
│              ▼                         ▼                         │
│     read + fallback            read-only (daemon writes)         │
│     (~0.1s)                    (~0.1s)                           │
│              │                         │                         │
│              └────────┬────────────────┘                         │
│                       ▼                                          │
│  2. DISPLAY OUTPUT (instant, uses cached values)                │
│                       │                                          │
│                       ▼                                          │
│  3. TRIGGER CCUSAGE BACKGROUND REFRESH IF STALE                 │
│     ┌──────────────────┐                                        │
│     │ age > 60s?       │   OAuth: no refresh here — daemon      │
│     │ Yes → bg refresh │   handles it independently every 60s   │
│     │ (non-blocking)   │                                        │
│     └──────────────────┘                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Performance (all cases): ~0.2s (never blocks on network)
First run: Shows 0% values (daemon populates cache within 60s)
```

### ccusage Background Refresh Details

**Lock File Guard Pattern (with stale lock cleanup):**
```
1. Check lock file exists
   a. If exists AND age > 120s → remove stale lock, continue
   b. If exists AND age ≤ 120s → return early (skip refresh)
2. Write lock file: /tmp/claude-ccusage.lock
3. Set trap for cleanup on EXIT (handles crashes)
4. Run ccusage CLI, write to temp file, validate, atomic mv
5. Remove lock file
```

## Dependencies

### Statusline command
- **jq**: JSON processor (for parsing stdin JSON and cache files)
- **ccusage**: Global binary at `~/.bun/bin/ccusage` (installed via bun, for daily/block costs)

### Launchd daemon (`~/scripts/claude-oauth-usage.sh`)
- **jq**: JSON processor
- **curl**: OAuth API calls
- **security**: macOS Keychain access for OAuth token

## Error Prevention

### Statusline command
1. **Lock file guard**: Prevents concurrent ccusage process storms (`/tmp/claude-ccusage.lock`)
2. **Trap cleanup**: `trap 'rm -f lockfile' EXIT` ensures lock removal even on crash
3. **Fallback values**: All jq queries use `// 0` or `// null` to prevent errors
4. **Silent failures**: `2>/dev/null` on all external commands
5. **Cache TTL**: 60-second ccusage refresh prevents slow statusline
6. **Error/stale indicator**: `!` suffix on 5h/7d/son values when error flag exists (last API call failed) or cache > 600s old (daemon not running)
7. **Null check**: Context usage gracefully handles null current_usage
8. **Separate caches**: Fault isolation — ccusage failure doesn't break OAuth data and vice versa
9. **Usage CSV rotation**: `/tmp/claude-usage-log.csv` trimmed to 1000 lines when > 500KB

### Launchd daemon (`com.henrychong.claude-oauth-usage`)
10. **Single-instance guarantee**: launchd ensures only one daemon process runs (every 300s) — eliminates multi-session rate limit amplification
20. **Error flag signalling**: On any non-200 response, writes reason to `/tmp/claude-oauth-error`. On 200 success, removes flag. Statusline reads flag for `!` indicator — decouples failure detection from cache staleness
11. **Token extraction**: CC Keychain uses `jq` (primary) with `grep -o` + `cut` fallback to handle truncated keychain JSON
12. **HTTP status differentiation**: `curl -w '%{http_code}'` distinguishes 200/429/401/403/000 (old code logged generic "rejected")
13. **5-min polling interval**: Reduced from 60s to 300s to minimize API calls (~288/day vs ~1440/day). On any failure, error flag written and next 5-min cycle retries naturally — no separate cooldown mechanism needed
15. **Atomic writes**: `mktemp` + validate + `mv` prevents statusline from reading partial JSON
16. **Never deletes good cache**: On API failure, stale data persists (better than no data)
17. **Debug breadcrumb**: All API calls logged to `/tmp/claude-oauth-debug.log` with ISO timestamp and HTTP status
18. **curl timeout**: `--max-time 10` prevents hanging
19. **Log rotation**: Debug log (>50KB → 20 lines)

## Time Remaining Calculation

The `(Xh Ym)` time remaining is calculated from the OAuth API's `five_hour.resets_at` field:

```bash
reset_at=$(jq -r '.five_hour.resets_at // empty' "$oauth_cache")
# Example: "2025-12-17T12:00:00.215851+00:00"

# Parse ISO timestamp (first 19 chars) and convert to epoch
reset_ts="${reset_at:0:19}"
reset_epoch=$(date -j -u -f "%Y-%m-%dT%H:%M:%S" "$reset_ts" +%s)

# Calculate remaining seconds from UTC now
now_utc=$(date -u +%s)
remaining=$((reset_epoch - now_utc))

# Format as hours and minutes
hrs=$((remaining / 3600))
mins=$(((remaining % 3600) / 60))
time_left=" (${hrs}h ${mins}m)"
```

**Why this is better than ccusage:**
- **Server-authoritative**: Uses Anthropic's actual `resets_at` timestamp
- **Cross-platform accurate**: Reflects true block timing even if block started on claude.ai
- **No local calculation drift**: Not based on first CC usage timestamp

## Line Wrapping Fix (Resolved)

**Problem:** Single-line output (~130+ chars) gets clipped in narrow terminals. CC allocates row height by counting `\n` in output — no newline = 1 row reserved, so excess is invisible. See [GitHub #22115](https://github.com/anthropics/claude-code/issues/22115).

**Fix (applied 2026-03-01):** Split final `printf` into 2 lines via `\n` in format string. CC counts the `\n` and allocates 2 rows.

```
Line 1: repos │ main │ 🤖 Opus 4.6 [medium] | 🧠 146k/200k (73%)
Line 2: 💰 $0.13 today / $0.13 block (4h 25m) | 📊 5h: 25% / 7d: 21% / son: 2%
```

## Version History

- **2026-03-15**: **Added effort level display.** Reads `effortLevel` from `~/.claude/settings.json` and displays as `[effort]` after model name (e.g., `🤖 Opus 4.6 [medium]`). Shows `[auto]` when field is unset (model default). New data source: `settings.json` read via `jq` (~0.1s). Note: effort is a global setting shared across all sessions — changing `/effort` in one session affects the display in all sessions.
- **2026-03-08 (b)**: **Fix curl error code concatenation bug.** When curl failed with a network error, `-w '%{http_code}'` output "000" then `|| echo "000"` appended another "000", producing "000000" which missed the `000)` case and fell through to `*) unexpected`. Fixed by replacing `|| echo "000"` with `|| true` + empty check fallback. Now network errors correctly match `000)` and log "network/timeout error".
- **2026-03-08 (a)**: **5-min polling interval + error flag signalling.** Changed launchd daemon `StartInterval` from 60s to 300s (5 min), reducing API calls from ~1440/day to ~288/day. Replaced 429 cooldown mechanism (`/tmp/claude-oauth-cooldown`) with error flag (`/tmp/claude-oauth-error`) — on any non-200 response, daemon writes reason to error flag; on 200 success, removes it. Statusline `!` indicator now checks error flag (last call failed) OR cache age > 600s (daemon not running), replacing the old 180s staleness check. Removed: `$COOLDOWN` variable, cooldown file check/write, `$hdr` temp file and `-D` header capture from curl. Added: `$ERROR_FLAG` variable, error flag writes on all failure paths including keychain/token extraction failures.
- **2026-03-06 (d)**: **429 cooldown backoff (5 min).** On 429, daemon writes expiry timestamp to `/tmp/claude-oauth-cooldown`. Subsequent 60s launchd cycles check file and exit without API call until cooldown expires. On 200 success, cooldown file is cleared. Reduces ~60 wasted network calls and log lines per rate limit window to 1.
- **2026-03-06 (c)**: **Removed retry on 429.** OAuth daemon now logs rate limit and exits immediately — no sleep, no retry. Launchd naturally retries on next 60s cycle. Prevents compounding rate limit pressure from overlapping sleep+retry with next invocation. Removed retry-after header parsing, `curl -D` header capture, and `$hdr` temp file.
- **2026-03-06 (b)**: **Launchd daemon for OAuth polling.** Extracted all OAuth API calls from statusline into standalone launchd daemon (`com.henrychong.claude-oauth-usage`, `~/scripts/claude-oauth-usage.sh`). Daemon polls `/api/oauth/usage` every 60s and writes to `/tmp/claude-usage-cache.json`. Statusline becomes read-only consumer — removed `get_oauth_token()`, `refresh_oauth_bg()`, all OAuth lock/cooldown logic (~100 lines). Fixes chronic staleness caused by multi-session rate limit amplification (3+ CC sessions each polling independently). Retry-after bounds changed from 300s floor to 5s floor / 120s cap. Stale threshold changed from 300s to 180s. Removed: `/tmp/claude-oauth.lock`, `/tmp/claude-oauth-api-cooldown`. Added: `/tmp/claude-oauth-launchd.log`. See `~/.claude/skills/infra-hc/references/automations/macbook-automations.md` for daemon documentation.
- **2026-03-06 (a)**: **OAuth simplification — direct CC Keychain read.** Removed `attempt_token_refresh()` function and 4-step `get_oauth_token()` chain (~85 lines). Replaced with 1-step direct read from CC's Keychain entry (`Claude Code-credentials`). CC manages its own token lifecycle (refresh, rotation); statusline just reads the current access token. Eliminates stale refresh token `invalid_grant` cascades that caused rate limiting. Also implemented dynamic `retry-after` cooldown (was documented but never deployed to settings.json). Removed: `/tmp/claude-statusline-token.json`, Keychain `Claude Code-statusline-token`, `/tmp/claude-oauth-refresh-cooldown`. Token extraction now uses `jq` primary with `grep -o`/`cut` fallback.
- **2026-03-05**: Token invalidation on API rejection + dynamic retry-after cooldown. (1) When usage API returns non-200, cached token is invalidated (file cache + Keychain statusline entry deleted), forcing `get_oauth_token()` to re-resolve via CC Keychain refresh token on next cycle. Fixes revoked tokens being reused indefinitely. (2) API cooldown file changed from empty touch file (mtime-based, fixed 5-min) to epoch-in-file format. Parses `retry-after` header from 429 responses for dynamic cooldown duration (minimum 300s). (3) `curl -D` captures response headers for retry-after extraction. Root cause: token rotation by CC invalidated cached access token; `get_oauth_token()` only checked expiry not API acceptance; 277 failed calls triggered account-level rate limiting.
- **2026-03-02**: Moved 📊 usage block from Line 1 to end of Line 2. New layout: Line 1 (dir │ branch │ model | ctx), Line 2 (cost | usage).
- **2026-03-01**: Two-line layout and block reorder. Line 1: dir │ branch │ model | context | usage. Line 2: cost (daily/block + time remaining). Resolves line wrapping/cutoff issue (GitHub #22115). Added full CC JSON stdin schema documentation (all available fields including unused: cost.*, version, session_id, vim.mode, agent.name). Added block layout reference table for easy rearranging.
- **2026-02-26**: Self-healing OAuth token refresh. Added `attempt_token_refresh()` and `get_oauth_token()` with 4-step token resolution chain (file cache → statusline Keychain → CC Keychain fallback → stale fallback). Separate Keychain entry `Claude Code-statusline-token` stores refresh token (never in `/tmp`). 5-minute cooldown on failed refresh. Rotation-safe token handling. `umask 077` in background subshell. `--max-time 10` on all curl calls. Debug log rotation (>50KB) and usage CSV rotation (>500KB). `$USER` instead of `$(whoami)`.
- **2026-02-25**: Added stale OAuth data indicator (`!` suffix on 5h/7d/son values). Triggers when cache age > 300s (5 min), meaning background refresh is failing (expired token). Also logs OAuth API rejection to `/tmp/claude-oauth-debug.log` for diagnosis.
- **2026-02-24**: Fixed OAuth token extraction — replaced `jq` with `grep -o` + `cut` to handle truncated keychain JSON (2012+ byte credential blob). Added debug breadcrumb to `/tmp/claude-oauth-debug.log` on extraction failure.
- **2026-02-20**: Documented `padding: 0` setting; hardened OAuth cache validation to check for `.five_hour` field (not just valid JSON) — prevents expired-token error responses from being cached as 0% values.
- **2026-02-12**: Added stale lock cleanup (120s timeout) to prevent permanently stuck ccusage/oauth refreshes when subshell crashes bypass trap cleanup.
- **2026-02-08**: Added lock file guards to prevent concurrent ccusage/oauth process storms. Uses `/tmp/claude-ccusage.lock` and `/tmp/claude-oauth.lock` with trap cleanup.
- **2026-01-08**: Removed +45k autocompact buffer addition from context calculation. CC 2.1.0+ now displays buffer as separate reserved space in `/context`, so statusline matches this behavior.
- **2026-01-02**: Implemented background refresh pattern - read cache first, refresh in background if stale. Never blocks on network calls.
- **2026-01-02**: Added atomic write pattern for cache updates (temp file + validate + mv)
- **2026-01-02**: Changed ccusage installation from npm to bun (`~/.bun/bin/ccusage`)
- **2025-12-17**: Added ccusage caching (Option B - separate file) with 60s TTL
- **2025-12-17**: Added time remaining `(Xh Ym)` from OAuth API `five_hour.resets_at`
- **v2.0.70+**: Uses `current_usage` field for accurate context window percentage
- **Pre-v2.0.70**: Used buggy `total_input_tokens`/`total_output_tokens` (cumulative session totals)

## Related KG Entities

- "Statusline OAuth Launchd Daemon Architecture" — architectural decision: single launchd daemon for OAuth polling
- "Statusline Block Layout and Data Sources" — current block positions, variables, and data source mapping
- "Statusline CC JSON Stdin Schema" — full schema of fields available from CC's JSON input
- "Why Statusline Shows Shell CWD Not Claude Code Workspace" — design decision for pwd vs workspace.current_dir
- "Haiku 4.5 Cost Tracking Bug - Complete Context" — known ccusage cost reporting issue
- "5h/7d Usage Ratio" — ratio analysis methodology

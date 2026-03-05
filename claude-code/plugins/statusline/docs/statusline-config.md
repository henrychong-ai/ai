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
Line 1: repos │ main │ 🤖 Opus 4.6 | 🧠 146k/200k (73%)
Line 2: 💰 $21.13 today / $21.13 block (4h 25m) | 📊 5h: 25% / 7d: 21% / son: 2%
```

When OAuth data is stale (token expired, API unreachable):
```
Line 1: repos │ main │ 🤖 Opus 4.6 | 🧠 146k/200k (73%)
Line 2: 💰 $21.13 today / $21.13 block (4h 25m) | 📊 5h: 25%! / 7d: 21%! / son: 2%!
```

### Block Layout (for rearranging)

Each block is an independent `printf` argument. To reorder, swap the variable positions in the two printf statements (with-git-branch and without-git-branch).

**Line 1 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `repos` | `$(basename "$current_dir")` | **Local filesystem** (`pwd`) | Current directory name |
| 2 | `main` | `$git_branch` | **Git** (`git branch --show-current`) | Git branch (omitted if not in repo) |
| 3 | `🤖 Opus 4.6` | `$model` | **CC JSON stdin** (`.model.display_name`) | Current model |
| 4 | `🧠 146k/200k (73%)` | `$ctx_str` | **CC JSON stdin** (`.context_window.current_usage`) | Context window usage (v2.0.70+) |

**Line 2 blocks:**

| Position | Block | Variable | Source | Description |
|----------|-------|----------|--------|-------------|
| 1 | `💰 $21.13 today / $21.13 block (4h 25m)` | `$cost_str` | **ccusage** (cached) + **OAuth API** (`resets_at`) | Daily/block cost + time remaining |
| 2 | `📊 5h: 25% / 7d: 21% / son: 2%` | `$usage_str` | **OAuth API** (cached) | 5h/7d/sonnet utilization |

**Stale indicator:** `%!` suffix on usage values when OAuth cache > 300s old.

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
3. **Anthropic OAuth API** (background refresh, 60s cache at `/tmp/claude-usage-cache.json`) — utilization %, time remaining

## Data Flow

```
Claude Code JSON stdin ──┬── model.display_name ──────────────────────────────┐
                         ├── context_window.current_usage ────────────────────┤
                         │   (also available: cost.*, version, session_id)    │
                         │                                                    │
ccusage cache (/tmp/claude-ccusage-cache.json, 60s TTL) ──────────────────────┤
  └── daily/block costs (read first, background refresh)                      │
                                                                              │
OAuth API cache (/tmp/claude-usage-cache.json, 60s TTL) ──────────────────────┤
  ├── 5h/7d/son utilization (read first, background refresh)                 │
  └── five_hour.resets_at ────────────────────────────────────────────────────┤
                                                                              │
                      Line 1: dir │ branch │ model | ctx | usage  ◄───────────┘
                      Line 2: cost (daily/block + time remaining)
                                          │
                      /tmp/claude-usage-log.csv (append, rotated >500KB)
```

**Key Design Principle:** Read cache FIRST, display immediately, then trigger background refresh if stale. This ensures the statusline never blocks on network calls and always shows last-known-good values.

## Self-Healing OAuth Token Resolution

When `refresh_oauth_bg()` needs a token, `get_oauth_token()` resolves it via a 4-step chain:

```
1. /tmp/claude-statusline-token.json (file cache, ~1ms, lost on reboot)
   → contains ONLY {accessToken, expiresAt} — NO refresh token
   → if accessToken valid (expiresAt > now + 60s): USE IT

2. Keychain "Claude Code-statusline-token" (persistent, ~50ms)
   → contains {accessToken, refreshToken, expiresAt}
   → if accessToken valid: populate file cache + USE IT
   → if expired: try its refreshToken via OAuth endpoint

3. Keychain "Claude Code-credentials" (CC's own, read-only fallback)
   → extract refreshToken via grep (truncated blob)
   → try OAuth refresh endpoint

4. Stale fallback
   → use whatever's in /tmp/claude-usage-cache.json + "!" indicator
```

### Security Model

| Store | Contains | Security |
|-------|----------|----------|
| `/tmp/claude-statusline-token.json` | `{accessToken, expiresAt}` only | `chmod 600`, `umask 077` |
| Keychain `Claude Code-statusline-token` | `{accessToken, refreshToken, expiresAt}` | macOS Keychain encryption |
| Keychain `Claude Code-credentials` | CC's own blob (read-only fallback) | macOS Keychain encryption |

### Refresh Mechanics

- **OAuth endpoint**: `POST https://console.anthropic.com/v1/oauth/token` with `grant_type=refresh_token`
- **Client ID**: `9d1c250a-e61b-44d9-88ed-5944d1962f5e` (Claude Code's public client ID)
- **Cooldown**: 5-minute cooldown after failed refresh (`/tmp/claude-oauth-refresh-cooldown`)
- **Rotation-safe**: If response omits new `refresh_token`, keeps previous one
- **Bootstrap**: First run uses CC Keychain refresh token → creates statusline Keychain entry

## Complete Command

```bash
input=$(cat)
current_dir=$(pwd)
git_branch=$(git branch --show-current 2>/dev/null)

# Extract model from JSON input
model=$(echo "$input" | jq -r '.model.display_name // "?"')

# Context window from current_usage field (v2.0.70+)
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
current_usage=$(echo "$input" | jq '.context_window.current_usage // null')

if [ "$current_usage" != "null" ]; then
  # Sum all token types (no +45k - CC 2.1.0+ shows buffer separately in /context)
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

# ============================================
# SELF-HEALING OAUTH TOKEN FUNCTIONS
# ============================================

# Refresh an OAuth access token using a refresh token
# Returns new access token on success, empty on failure
# Writes to Keychain (with refresh token) and file cache (without)
attempt_token_refresh() {
  local refresh_token="$1"
  local ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local cooldown="/tmp/claude-oauth-refresh-cooldown"
  # Cooldown: skip if last failure < 300s (5 min)
  if [ -f "$cooldown" ]; then
    local cd_ts=$(stat -f %m "$cooldown" 2>/dev/null || echo 0)
    local now_s=$(date +%s)
    [ $((now_s - cd_ts)) -lt 300 ] && return 1
  fi
  # POST with --data-urlencode to safely handle special chars in token
  local resp=$(curl -s --max-time 10 -X POST "https://console.anthropic.com/v1/oauth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "grant_type=refresh_token" \
    --data-urlencode "refresh_token=${refresh_token}" \
    --data-urlencode "client_id=9d1c250a-e61b-44d9-88ed-5944d1962f5e" 2>/dev/null)
  local new_access=$(echo "$resp" | jq -r '.access_token // empty' 2>/dev/null)
  if [ -z "$new_access" ]; then
    echo "$ts refresh failed: $(echo "$resp" | jq -r '.error // "unknown"' 2>/dev/null)" >> /tmp/claude-oauth-debug.log
    touch "$cooldown" 2>/dev/null
    return 1
  fi
  # Rotation-safe: keep old refresh token if response doesn't include a new one
  local new_refresh=$(echo "$resp" | jq -r '.refresh_token // empty' 2>/dev/null)
  [ -z "$new_refresh" ] && new_refresh="$refresh_token"
  local expires_in=$(echo "$resp" | jq -r '.expires_in // 86400' 2>/dev/null)
  local now_ms=$(($(date +%s) * 1000))
  local new_expires=$((now_ms + expires_in * 1000))
  # Keychain blob (includes refresh token — encrypted at rest)
  local kc_blob="{\"accessToken\":\"${new_access}\",\"refreshToken\":\"${new_refresh}\",\"expiresAt\":${new_expires}}"
  security add-generic-password -U -s "Claude Code-statusline-token" -a "$USER" -w "$kc_blob" 2>/dev/null
  # File cache (access token + expiry ONLY — no refresh token in /tmp)
  local fc_blob="{\"accessToken\":\"${new_access}\",\"expiresAt\":${new_expires}}"
  local tmp="/tmp/claude-statusline-token.json.tmp.$$"
  echo "$fc_blob" > "$tmp"
  chmod 600 "$tmp" 2>/dev/null
  if jq -e . "$tmp" >/dev/null 2>&1; then
    mv "$tmp" /tmp/claude-statusline-token.json
  else
    rm -f "$tmp"
  fi
  rm -f "$cooldown" 2>/dev/null
  echo "$ts token refreshed successfully (expires in ${expires_in}s)" >> /tmp/claude-oauth-debug.log
  echo "$new_access"
}

# Resolve OAuth token via 4-step chain:
# 1. File cache (fastest) → 2. Statusline Keychain → 3. CC Keychain fallback → 4. Stale fallback
get_oauth_token() {
  local now_ms=$(($(date +%s) * 1000))
  # Step 1: File cache (~1ms) — access token only, no refresh token
  if [ -f /tmp/claude-statusline-token.json ]; then
    local ct=$(jq -r '.accessToken // empty' /tmp/claude-statusline-token.json 2>/dev/null)
    local ce=$(jq -r '.expiresAt // 0' /tmp/claude-statusline-token.json 2>/dev/null)
    if [ -n "$ct" ] && [ "$ce" -gt $((now_ms + 60000)) ] 2>/dev/null; then
      echo "$ct"
      return 0
    fi
  fi
  # Step 2: Statusline Keychain entry (~50ms) — has refresh token for self-healing
  local sb=$(security find-generic-password -s "Claude Code-statusline-token" -w 2>/dev/null)
  if [ -n "$sb" ]; then
    local st=$(echo "$sb" | jq -r '.accessToken // empty' 2>/dev/null)
    local se=$(echo "$sb" | jq -r '.expiresAt // 0' 2>/dev/null)
    if [ -n "$st" ] && [ "$se" -gt $((now_ms + 60000)) ] 2>/dev/null; then
      # Populate file cache (access token + expiry only)
      echo "{\"accessToken\":\"${st}\",\"expiresAt\":${se}}" > /tmp/claude-statusline-token.json
      chmod 600 /tmp/claude-statusline-token.json 2>/dev/null
      echo "$st"
      return 0
    fi
    # Token expired — try refresh using statusline's own refresh token
    local sr=$(echo "$sb" | jq -r '.refreshToken // empty' 2>/dev/null)
    if [ -n "$sr" ]; then
      local result=$(attempt_token_refresh "$sr")
      if [ -n "$result" ]; then
        echo "$result"
        return 0
      fi
    fi
  fi
  # Step 3: CC Keychain refresh token (bootstrap/fallback)
  local cb=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null)
  local cr=$(echo "$cb" | grep -o '"refreshToken":"[^"]*"' | head -1 | cut -d'"' -f4)
  if [ -n "$cr" ]; then
    local result=$(attempt_token_refresh "$cr")
    if [ -n "$result" ]; then
      echo "$result"
      return 0
    fi
  fi
  # Step 4: Stale CC access token as last resort (will likely fail but triggers ! indicator)
  local cc=$(echo "$cb" | grep -o '"accessToken":"[^"]*"' | head -1 | cut -d'"' -f4)
  if [ -n "$cc" ]; then
    echo "$cc"
    return 0
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) get_oauth_token: all paths exhausted" >> /tmp/claude-oauth-debug.log
  return 1
}

# ============================================
# BACKGROUND REFRESH FUNCTIONS (non-blocking)
# ============================================

# Background ccusage refresh with lock file guard + stale lock cleanup + atomic write
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

# Background OAuth refresh — uses get_oauth_token() for self-healing token resolution
refresh_oauth_bg() {
  # Dynamic cooldown: file contains epoch (seconds) of when retry is allowed
  if [ -f /tmp/claude-oauth-api-cooldown ]; then
    local retry_until=$(cat /tmp/claude-oauth-api-cooldown 2>/dev/null)
    [ -n "$retry_until" ] && [ "$retry_until" -gt "$now" ] 2>/dev/null && return
    rm -f /tmp/claude-oauth-api-cooldown
  fi
  if [ -f /tmp/claude-oauth.lock ]; then
    lock_ts=$(stat -f %m /tmp/claude-oauth.lock 2>/dev/null || echo 0)
    [ $((now - lock_ts)) -gt 120 ] && rm -f /tmp/claude-oauth.lock || return
  fi
  (
    umask 077
    echo $$ > /tmp/claude-oauth.lock
    trap 'rm -f /tmp/claude-oauth.lock' EXIT
    # Debug log rotation (>50KB → keep last 20 lines)
    if [ -f /tmp/claude-oauth-debug.log ]; then
      sz=$(stat -f %z /tmp/claude-oauth-debug.log 2>/dev/null || echo 0)
      [ "$sz" -gt 51200 ] && { tail -20 /tmp/claude-oauth-debug.log > /tmp/claude-oauth-debug.log.tmp && mv /tmp/claude-oauth-debug.log.tmp /tmp/claude-oauth-debug.log; }
    fi
    token=$(get_oauth_token)
    if [ -z "$token" ]; then
      rm -f /tmp/claude-oauth.lock
      return
    fi
    tmp="${oauth_cache}.tmp.$$"
    hdr_tmp="${oauth_cache}.hdr.$$"
    curl -s -D "$hdr_tmp" --max-time 10 "https://api.anthropic.com/api/oauth/usage" \
      -H "Authorization: Bearer $token" \
      -H "anthropic-beta: oauth-2025-04-20" > "$tmp" 2>/dev/null
    if jq -e '.five_hour' "$tmp" >/dev/null 2>&1; then
      mv "$tmp" "$oauth_cache"
    else
      echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) oauth API rejected — invalidating cached token" >> /tmp/claude-oauth-debug.log
      # Invalidate cached token — may be revoked, force re-resolution on next cycle
      rm -f /tmp/claude-statusline-token.json
      security delete-generic-password -s "Claude Code-statusline-token" 2>/dev/null
      # Dynamic cooldown from retry-after header (minimum 300s)
      ra=$(grep -i "retry-after" "$hdr_tmp" 2>/dev/null | tr -d "\r" | awk '{print $2}')
      ra=${ra:-300}
      [ "$ra" -lt 300 ] 2>/dev/null && ra=300
      echo "$(($(date +%s) + ra))" > /tmp/claude-oauth-api-cooldown
      rm -f "$tmp"
    fi
    rm -f "$hdr_tmp"
    rm -f /tmp/claude-oauth.lock
  ) &>/dev/null & disown 2>/dev/null
}

# ============================================
# READ CACHE VALUES FIRST (always instant)
# ============================================

daily_raw=$(jq -r '.daily // 0' "$ccusage_cache" 2>/dev/null)
daily_fmt=$(printf '%.2f' "${daily_raw:-0}" 2>/dev/null)
daily_fmt=${daily_fmt:-0.00}

block_raw=$(jq -r '.block // 0' "$ccusage_cache" 2>/dev/null)
block_fmt=$(printf '%.2f' "${block_raw:-0}" 2>/dev/null)
block_fmt=${block_fmt:-0.00}

five_hr=$(jq -r '.five_hour.utilization // 0' "$oauth_cache" 2>/dev/null | xargs printf '%.0f' 2>/dev/null)
five_hr=${five_hr:-0}

seven_day=$(jq -r '.seven_day.utilization // 0' "$oauth_cache" 2>/dev/null | xargs printf '%.0f' 2>/dev/null)
seven_day=${seven_day:-0}

sonnet=$(jq -r '.seven_day_sonnet.utilization // 0' "$oauth_cache" 2>/dev/null | xargs printf '%.0f' 2>/dev/null)
sonnet=${sonnet:-0}

# Detect stale OAuth cache (>5 min = background refresh failing)
oauth_stale=""
if [ -f "$oauth_cache" ]; then
  oauth_age=$((now - $(stat -f %m "$oauth_cache" 2>/dev/null || echo $now)))
  [ "$oauth_age" -gt 300 ] && oauth_stale="!"
fi

# Calculate time remaining from API's resets_at (server-authoritative)
reset_at=$(jq -r '.five_hour.resets_at // empty' "$oauth_cache" 2>/dev/null)
time_left=""
if [ -n "$reset_at" ]; then
  reset_ts="${reset_at:0:19}"
  reset_epoch=$(date -j -u -f "%Y-%m-%dT%H:%M:%S" "$reset_ts" +%s 2>/dev/null)
  if [ -n "$reset_epoch" ]; then
    now_utc=$(date -u +%s)
    remaining=$((reset_epoch - now_utc))
    if [ "$remaining" -gt 0 ]; then
      hrs=$((remaining / 3600))
      mins=$(((remaining % 3600) / 60))
      time_left=" (${hrs}h ${mins}m)"
    fi
  fi
fi

# ============================================
# TRIGGER BACKGROUND REFRESH IF STALE
# ============================================

if [ -f "$ccusage_cache" ]; then
  file_ts=$(stat -f %m "$ccusage_cache" 2>/dev/null || echo 0)
  age=$((now - file_ts))
  [ "$age" -gt 60 ] && refresh_ccusage_bg
else
  refresh_ccusage_bg
fi

if [ -f "$oauth_cache" ]; then
  file_ts=$(stat -f %m "$oauth_cache" 2>/dev/null || echo 0)
  age=$((now - file_ts))
  [ "$age" -gt 60 ] && refresh_oauth_bg
else
  refresh_oauth_bg
fi

# ============================================
# BUILD OUTPUT STRINGS
# ============================================

cost_str="💰 \$$daily_fmt today / \$$block_fmt block$time_left"

# Usage CSV log rotation (>500KB → keep last 1000 lines)
if [ -f /tmp/claude-usage-log.csv ]; then
  sz=$(stat -f %z /tmp/claude-usage-log.csv 2>/dev/null || echo 0)
  [ "$sz" -gt 512000 ] && { tail -1000 /tmp/claude-usage-log.csv > /tmp/claude-usage-log.csv.tmp && mv /tmp/claude-usage-log.csv.tmp /tmp/claude-usage-log.csv; }
fi

echo "$now,$five_hr,$seven_day,$sonnet" >> /tmp/claude-usage-log.csv

usage_str="📊 5h: ${five_hr}%${oauth_stale} / 7d: ${seven_day}%${oauth_stale} / son: ${sonnet}%${oauth_stale}"

if [ -n "$git_branch" ]; then
  printf "%s │ %s │ 🤖 %s | %s\n%s | %s" "$(basename "$current_dir")" "$git_branch" "$model" "$ctx_str" "$cost_str" "$usage_str"
else
  printf "%s │ 🤖 %s | %s\n%s | %s" "$(basename "$current_dir")" "$model" "$ctx_str" "$cost_str" "$usage_str"
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

OAuth API response cached for 60 seconds:

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

### /tmp/claude-statusline-token.json

File cache for OAuth access token (hot path, ~1ms read). **No refresh token stored here.**

```json
{
  "accessToken": "eyJ...",
  "expiresAt": 1740000000000
}
```

**Permissions:** `chmod 600` (owner-only), created with `umask 077`
**Lifecycle:** Lost on reboot → repopulated from Keychain on next statusline render

### Keychain: "Claude Code-statusline-token"

Persistent OAuth token store with refresh token (macOS Keychain, encrypted at rest).

```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "expiresAt": 1740000000000
}
```

**Created by:** `attempt_token_refresh()` via `security add-generic-password -U`
**Bootstrap:** First created using CC Keychain's refresh token, then self-sustaining

### /tmp/claude-usage-log.csv

Append-only log for ratio analysis (rotated >500KB → keep last 1000 lines):

```
timestamp,5h%,7d%,sonnet%
1765864379,25,20,2
1765864438,25,20,2
```

### /tmp/claude-oauth-refresh-cooldown

Empty touch file. Prevents refresh token hammering after a failed attempt. Checked by `stat -f %m` — if younger than 300s (5 min), refresh is skipped.

### /tmp/claude-oauth-api-cooldown

Contains a Unix epoch (seconds) indicating when the next API retry is allowed. Prevents OAuth usage API hammering after a failed API call. Checked at the start of `refresh_oauth_bg()` — if current time < stored epoch, refresh is skipped entirely.

**Dynamic duration:** Parses `retry-after` header from 429 responses (minimum 300s / 5 min). A rate limit with `retry-after: 3600` creates a 1-hour cooldown instead of the old fixed 5-minute cooldown.

**Format (2026-03-05):** Changed from empty touch file (mtime-based, fixed 5-min) to epoch-in-file (dynamic duration from retry-after header).

### /tmp/claude-oauth-debug.log

Debug breadcrumbs for OAuth operations (rotated >50KB → keep last 20 lines).

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
│     └────────┬─────────┘      └────────┬─────────┘              │
│              │                         │                         │
│              ▼                         ▼                         │
│     read + fallback            read + fallback                   │
│     (~0.1s)                    (~0.1s)                           │
│              │                         │                         │
│              └────────┬────────────────┘                         │
│                       ▼                                          │
│  2. DISPLAY OUTPUT (instant, uses cached values)                │
│                       │                                          │
│                       ▼                                          │
│  3. CHECK IF STALE & TRIGGER BACKGROUND REFRESH                 │
│     ┌──────────────────┐      ┌──────────────────┐              │
│     │ age > 60s?       │      │ age > 60s?       │              │
│     │ Yes → bg refresh │      │ Yes → bg refresh │              │
│     │ (non-blocking)   │      │ (non-blocking)   │              │
│     └──────────────────┘      └──────────────────┘              │
│                                                                  │
│  Background processes update cache files for NEXT call          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Performance (all cases): ~0.2s (never blocks on network)
First run: Shows 0% values, triggers background refresh
Next call after refresh: Shows updated values
```

### Background Refresh Details

**Lock File Guard Pattern (with stale lock cleanup):**
```
1. Check API cooldown file (OAuth only)
   a. If exists AND stored epoch > now → return early (skip refresh)
   b. If exists AND stored epoch ≤ now → remove cooldown, continue
2. Check lock file exists
   a. If exists AND age > 120s → remove stale lock, continue
   b. If exists AND age ≤ 120s → return early (skip refresh)
3. Write lock file: /tmp/claude-ccusage.lock (or claude-oauth.lock)
4. Set trap for cleanup on EXIT (handles crashes)
5. Do work...
6. On failure: invalidate cached token + write retry epoch to /tmp/claude-oauth-api-cooldown (OAuth only)
7. Remove lock file
```

**Atomic Write Pattern:**
```
1. Write to temp file: ${cache}.tmp.$$
2. Validate JSON: jq -e . "$tmp"
3. If valid: mv "$tmp" "$cache" (atomic)
4. If invalid: rm -f "$tmp" (keep old cache)
```

**Benefits:**
- Lock file prevents concurrent ccusage/oauth process storms
- Never blocks statusline rendering
- Failed refreshes don't corrupt cache
- Partial writes can't cause parse errors
- Last-known-good values always displayed
- Stale lock file worst case: delays refresh by one prompt cycle

## Dependencies

- **jq**: JSON processor (for parsing stdin JSON and cache files)
- **ccusage**: Global binary at `~/.bun/bin/ccusage` (installed via bun, for daily/block costs)
- **curl**: OAuth API calls
- **security**: macOS Keychain access for OAuth token

## Error Prevention

1. **Lock file guard**: Prevents concurrent ccusage/oauth process storms (`/tmp/claude-ccusage.lock`, `/tmp/claude-oauth.lock`)
2. **Trap cleanup**: `trap 'rm -f lockfile' EXIT` ensures lock removal even on crash
3. **Fallback values**: All jq queries use `// 0` or `// null` to prevent errors
4. **Silent failures**: `2>/dev/null` on all external commands
5. **Cache TTL**: 60-second refresh prevents API rate limiting and slow statusline
6. **Token extraction**: CC Keychain uses `grep -o` + `cut` instead of `jq` to handle truncated keychain JSON (credential blob exceeds `security -w` output limit)
7. **Debug breadcrumb**: Token operations logged to `/tmp/claude-oauth-debug.log` with ISO timestamp
8. **OAuth API rejection logging**: Failed API responses (expired token, error) logged to debug log
9. **Stale data indicator**: `!` suffix on 5h/7d/son values when OAuth cache > 300s old (background refresh failing)
10. **Null check**: Context usage gracefully handles null current_usage
11. **Separate caches**: Fault isolation - ccusage failure doesn't break OAuth data
12. **Self-healing tokens**: `get_oauth_token()` 4-step resolution chain auto-refreshes expired tokens
13. **Refresh cooldown**: 5-minute cooldown after failed token refresh prevents endpoint hammering (`/tmp/claude-oauth-refresh-cooldown`)
14. **API call cooldown**: Dynamic cooldown after failed OAuth usage API call prevents rate limit feedback loops (`/tmp/claude-oauth-api-cooldown`). Parses `retry-after` header for duration (minimum 300s). File contains retry epoch, not just empty touch.
15. **Token invalidation on API rejection**: When the usage API returns non-200 (429, 401, etc.), both file cache and Keychain statusline entry are deleted. Forces `get_oauth_token()` to fall through to Step 3 (CC Keychain refresh token) on next cycle, obtaining a fresh access token. Prevents revoked/rate-limited tokens from being reused indefinitely.
16. **Retry-after header parsing**: `curl -D` captures response headers; `grep -i "retry-after"` extracts the value. Cooldown duration adapts to server-specified wait time rather than using a fixed 5-minute interval.
15. **No refresh token in /tmp**: File cache stores only `{accessToken, expiresAt}` — refresh token stays in Keychain
16. **File permissions**: `chmod 600` on file cache, `umask 077` in background subshell
17. **Rotation-safe refresh**: Keeps previous refresh token if OAuth response omits new one
18. **URL-encoded POST body**: `--data-urlencode` handles special chars in tokens safely
19. **curl timeout**: `--max-time 10` on all curl calls prevents hanging
20. **Log rotation**: Debug log (>50KB → 20 lines) and usage CSV (>500KB → 1000 lines)

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
Line 1: repos │ main │ 🤖 Opus 4.6 | 🧠 146k/200k (73%)
Line 2: 💰 $0.13 today / $0.13 block (4h 25m) | 📊 5h: 25% / 7d: 21% / son: 2%
```

## Version History

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

- "Statusline Block Layout and Data Sources" — current block positions, variables, and data source mapping
- "Statusline CC JSON Stdin Schema" — full schema of fields available from CC's JSON input
- "Why Statusline Shows Shell CWD Not Claude Code Workspace" — design decision for pwd vs workspace.current_dir
- "Haiku 4.5 Cost Tracking Bug - Complete Context" — known ccusage cost reporting issue
- "5h/7d Usage Ratio" — ratio analysis methodology

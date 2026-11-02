# Statusline Plugin

A Claude Code statusline plugin that displays comprehensive session metrics including model, context usage, costs, and rate limits. The 5-hour usage segment and block cost appear only when your plan has a 5-hour usage window.

## Output Format

Two-line display:

```
Line 1: repos │ main │ 🤖 Fable 5 [xhigh] | 🧠 146k/1000k (15%)
Line 2: 💰 $21.13 today / $21.13 block (4h 25m) | 📊 5h: 25% / 7d: 21% / Fable: 6%
```

On a plan with no 5-hour usage window (for example Claude Ultra, or Max 20x since that limit was removed), line 2 becomes:

```
Line 2: 💰 $21.13 today | 📊 7d: 21% / Fable: 6%
```

| Component | Line | Description |
|-----------|------|-------------|
| `repos` | 1 | Current directory name |
| `main` | 1 | Git branch (if in repo) |
| `🤖 Fable 5` | 1 | Current model |
| `[xhigh]` | 1 | Effort level — live per-session from stdin; falls back to the model's saved `modelSettings` entry, then the top-level settings.json default (not for Opus 5.5, which ignores it), then `auto` |
| `🧠 146k/1000k (15%)` | 1 | Context window usage |
| `💰 $21.13 today` | 2 | Today's accumulated cost |
| `$21.13 block` | 2 | Current billing block cost — only when the plan has a 5-hour window |
| `(4h 25m)` | 2 | Time remaining in 5h block — only when the plan has a 5-hour window |
| `📊 5h: 25%` | 2 | 5-hour utilization — only when the plan has a 5-hour window |
| `7d: 21%` | 2 | 7-day (all models) utilization |
| `Fable: 6%` | 2 | Fable weekly (model-scoped) utilization — omitted if unavailable; `*` suffix = newest source >1h old |

### Data Sources

| Data | Source | Latency |
|------|--------|---------|
| Model, context, rate limits (5h/7d) | CC JSON stdin (piped every render) | Instant |
| Effort level | CC JSON stdin `.effort.level` (fallback: settings.json `modelSettings`, then top-level default) | Instant |
| Fable weekly utilization | `~/.claude.json` → `.cachedUsageUtilization` (CC-owned cache of `/api/oauth/usage`) | Instant read; refreshed by CC |
| Daily/block costs | ccusage CLI (cached 60s at `/tmp/claude-ccusage-cache.json`) | Background refresh |
| Account-wide 5h/7d/Fable usage, 5h-window detection (optional) | CodexBar CLI (cached at `/tmp/claude-codexbar-usage.json`, refreshed at most every 180s) | Background refresh |
| Git branch | `git branch --show-current` | Instant |

## Requirements

### Platform
- **macOS only** - Uses BSD utilities (`stat -f`); the optional CodexBar integration expects the Homebrew path `/opt/homebrew/bin/codexbar`

### Dependencies

| Dependency | Purpose | Install |
|------------|---------|---------|
| `jq` | JSON parsing | `brew install jq` |
| `ccusage` | Cost tracking | `npm install -g ccusage` |
| CodexBar (optional) | Account-wide usage reconciliation and 5h-window detection | CodexBar app with its CLI at `/opt/homebrew/bin/codexbar`; the statusline works without it |

### Authentication
- **Claude Max subscription** with OAuth login required for rate limit metrics
- API key users will see partial data (no utilization percentages)

## Installation

### Option 1: Via Plugin System (Recommended)

1. Add the plugin marketplace to your settings (one-time):
   ```json
   // ~/.claude/settings.json
   {
     "extraKnownMarketplaces": [
       "file:///path/to/plugins"
     ]
   }
   ```

2. Install the plugin:
   ```
   /plugin install statusline
   ```

3. Run the installer:
   ```
   /install-statusline
   ```

### Option 2: Direct Installation

```bash
/path/to/statusline/scripts/install.sh
```

### Option 3: Manual Installation

Copy the `statusLine` object from `configs/statusline.json` into your `~/.claude/settings.json`.

## Architecture

### Non-Blocking Design

The statusline uses a **non-blocking architecture** that never waits for network calls:

1. **Read cache first** - Always displays last-known-good values instantly
2. **Display immediately** - Statusline renders in ~0.2s regardless of network
3. **Background refresh** - If ccusage cache is stale (>60s), triggers async refresh for next call

### Rate Limits (CC v2.1.80+)

Rate limit data (`5h`, `7d`) comes directly from CC's native JSON stdin via `.rate_limits` — always fresh, no external polling or daemon required. This replaced a previous OAuth launchd daemon architecture.

### Plans Without a 5-Hour Window (1.6.0)

The statusline hides the 5h segment, the ccusage block cost and its countdown when the account has no 5-hour window. Detection, first match wins: a stdin `rate_limits.five_hour` with a future reset → show; else a fresh (<30 min) CodexBar cache → show only if it reports a 5h window; else any stdin `five_hour` → show; else hide. The usage CSV then logs an empty 5h column. Plans that still have a 5-hour limit see no change.

### CodexBar Reconciliation (optional)

stdin `rate_limits` is each session's own last API response, so parallel or idle sessions can disagree. If the CodexBar CLI is installed at `/opt/homebrew/bin/codexbar`, the statusline also reads account-wide usage from it in the background and merges: within the same window the higher value wins, across windows the later reset wins, and Fable comes from whichever source is newer. A CodexBar cache older than 30 minutes is ignored. Without CodexBar the statusline falls back to stdin and CC's cache.

Model-scoped weekly windows (e.g. **Fable**) are NOT in the stdin payload — CC hard-codes only `five_hour` and `seven_day` there (verified v2.1.211). The statusline reads them instead from CC's own on-disk cache of the `/api/oauth/usage` response (`~/.claude.json` → `.cachedUsageUtilization`): no network calls, no tokens, no keychain. A `*` suffix marks the value when the newest source (this cache or CodexBar) is older than 1h; the segment disappears entirely if the bucket is absent.

### Cache Files

| File | Purpose | TTL |
|------|---------|-----|
| `/tmp/claude-ccusage-cache.json` | Cost data from ccusage | 60s |
| `/tmp/claude-usage-log.csv` | Historical usage log (for ratio analysis) | Rotated >500KB |
| `/tmp/claude-ccusage.lock` | Prevents concurrent ccusage processes | 120s stale cleanup |
| `/tmp/claude-codexbar-usage.json` | CodexBar usage cache (optional; `{ts,h5,p,pr,s,sr,f}`) | Refreshed every 180s; ignored after 30 min |
| `/tmp/claude-codexbar-usage.stamp` | Throttles CodexBar refresh attempts | 180s |
| `~/.claude.json` → `.cachedUsageUtilization` | Fable/model-scoped weekly windows (CC-owned — read-only, never write) | Refreshed by CC |

### Atomic Write Pattern

Cache updates use atomic writes to prevent corruption:
1. Write to temp file (`cache.tmp.$$`)
2. Validate JSON with `jq -e`
3. Atomic replace with `mv` (or discard if invalid)

## Plugin Structure

```
statusline/
├── README.md                          # This file
├── commands/
│   └── install-statusline.md          # /install-statusline slash command
├── configs/
│   └── statusline.json                # Statusline settings.json config
├── docs/
│   └── statusline-config.md           # Detailed technical reference
└── scripts/
    ├── install.sh                     # Shell installer
    └── calc_usage_ratio.py            # 5h/7d consumption ratio analysis
```

## Troubleshooting

### Statusline not showing
- Restart Claude Code after installation
- Check `~/.claude/settings.json` contains the `statusLine` key

### Missing cost data
- Verify ccusage is installed: `which ccusage`
- Run `ccusage daily` manually to check for errors

### Missing usage percentages
- Requires a Claude subscription login (not an API key); check with `claude auth status`, which does not print the token
- `rate_limits` appear only after the session's first API response (Claude Code v2.1.80+)

### 5h segment or block cost missing
- Expected on plans with no 5-hour usage window — the statusline hides the 5h segment, the block cost and the countdown there
- If your plan does have a 5h window, send one message in the session (stdin `rate_limits` populate only after an API request)

### CodexBar values not updating
- CodexBar is optional; if its binary link is missing, the feed stops silently and the statusline falls back to stdin
- Check `ls -l /opt/homebrew/bin/codexbar` and the cache age: `stat -f %m /tmp/claude-codexbar-usage.json`

### Fable segment missing
- The `Fable: N%` segment only appears when CC's cached `/api/oauth/usage` response contains a model-scoped weekly window — open `/usage` once in any session to force a refresh
- Plans without a Fable weekly window never show the segment (by design — it degrades silently)

### Slow statusline refresh
- First run shows 0% values while background refresh populates cache
- Subsequent runs always instant (~0.2s) — refresh happens in background
- If consistently slow, check for shell startup issues

## Uninstallation

Remove the `statusLine` key from `~/.claude/settings.json`:

```bash
jq 'del(.statusLine)' ~/.claude/settings.json > tmp.json && mv tmp.json ~/.claude/settings.json
```

## Usage Analytics

### Calculating 5h/7d Consumption Ratio

The statusline logs usage data to `/tmp/claude-usage-log.csv`. Use the included script to analyse how much 5-hour capacity you consume per 1% of 7-day utilisation:

```bash
python3 claude-code/plugins/statusline/scripts/calc_usage_ratio.py
```

**Output:**
```
=== 5h Climb Per 7d Unit Transition ===

Transition      5h climb
------------------------------
11% → 12%       42
12% → 13%       38
------------------------------

Total transitions: 2
Total 5h climb: 80

*** RATIO: 80/2 = 40.00 5h% per 1% 7d ***

Interpretation: For every 1% of 7d consumed, ~40.0% of 5h is consumed.
```

**Options:**
- `--log-file PATH` - Use custom log file location (default: `/tmp/claude-usage-log.csv`)

## Version History

- **1.6.0** (2026-11-03): **Plans without a 5-hour window** — hides the 5h segment, the ccusage block cost and its countdown when the plan has no 5-hour usage window (e.g. Claude Ultra, Max 20x); the usage CSV logs an empty 5h column. Plans with a 5h limit see no change. Adds the optional **CodexBar reconciliation** (5h/7d max-within-window merge, Fable from the newest source, `*` = newest source >1h old), with a fixed null-safe cache writer (jq `round` on a null 5h window used to stop the cache being written). **Per-model effort fallback**: reads `modelSettings[<model.id>].effortLevel` first and shows `auto` for Opus 5.5 instead of the ignored top-level default.
- **1.5.0** (2026-07-16): **Fable weekly usage segment** (`Fable: N%`) read from CC's `cachedUsageUtilization` on-disk cache — the stdin `rate_limits` carries 5h/7d only (verified v2.1.211). Also: per-session effort now reads stdin `.effort.level` (fixes stale global-default display across windows), and ccusage v20 schema fix (`.period` + `.agent == "all"` — the old `.date` query silently returned $0.00 daily cost).
- **1.4.0** (2026-03-20): Native `rate_limits` migration. Replaced OAuth launchd daemon with CC's native `rate_limits` JSON stdin (v2.1.80+). Dropped sonnet display (not in native field). ~20 lines removed.
- **1.3.1** (2026-03-15): Added effort level display (`[medium]`, `[auto]`, etc.) after model name.
- **1.3.0** (2026-03-06): Two-line layout, OAuth simplification (direct CC Keychain read), retry-after bounds fix (5s floor / 300s cap).
- **1.2.0** (2026-01-08): Added calc_usage_ratio.py for 5h/7d consumption analysis.
- **1.1.0** (2026-01-05): Non-blocking architecture — read cache first, background refresh, atomic writes.
- **1.0.0** (2025-12-19): Initial release.

## Further Documentation

See [`docs/statusline-config.md`](docs/statusline-config.md) for the complete technical reference including the full shell command, data flow diagram, CC JSON stdin schema, and all available fields.

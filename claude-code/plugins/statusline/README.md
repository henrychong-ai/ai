# Statusline Plugin

A Claude Code statusline configuration that displays comprehensive session metrics.

## Output Format

```
repos │ main │ 🤖 Opus | 💰 $21.13 today / $21.13 block (4h 25m) | 🧠 146k/200k (73%) | 📊 5h: 25% / 7d: 21% / son: 2%
```

| Component | Description |
|-----------|-------------|
| `repos` | Current directory name |
| `main` | Git branch (if in repo) |
| `🤖 Opus` | Current model |
| `💰 $21.13 today` | Today's accumulated cost |
| `$21.13 block` | Current billing block cost |
| `(4h 25m)` | Time remaining in 5h block |
| `🧠 146k/200k (73%)` | Context window usage |
| `📊 5h: 25%` | 5-hour utilization |
| `7d: 21%` | 7-day utilization |
| `son: 2%` | Sonnet-specific utilization |

## Requirements

### Platform
- **macOS only** - Uses macOS Keychain and BSD utilities

### Dependencies

| Dependency | Purpose | Install |
|------------|---------|---------|
| `jq` | JSON parsing | `brew install jq` |
| `ccusage` | Cost tracking | `npm install -g ccusage` |
| `curl` | API calls | Pre-installed |

### Authentication
- **Claude Max subscription** with OAuth login required for usage metrics
- API key users will see partial data (no OAuth utilization metrics)

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

## Caching & Non-Blocking Design

The statusline uses a **non-blocking architecture** that never waits for network calls:

1. **Read cache first** - Always displays last-known-good values instantly
2. **Display immediately** - Statusline renders in ~0.2s regardless of network
3. **Background refresh** - If cache is stale (>60s), triggers async refresh for next call

### Cache Files

- `/tmp/claude-ccusage-cache.json` - Cost data from ccusage
- `/tmp/claude-usage-cache.json` - OAuth utilization data
- `/tmp/claude-usage-log.csv` - Historical usage log

### Atomic Write Pattern

Cache updates use atomic writes to prevent corruption:
1. Write to temp file (`cache.tmp.$$`)
2. Validate JSON with `jq -e`
3. Atomic replace with `mv` (or discard if invalid)

## Troubleshooting

### Statusline not showing
- Restart Claude Code after installation
- Check `~/.claude/settings.json` contains the `statusLine` key

### Missing cost data
- Verify ccusage is installed: `which ccusage`
- Run `ccusage daily` manually to check for errors

### Missing usage percentages
- Requires Claude Max with OAuth login (not API keys)
- Check OAuth token: `security find-generic-password -s "Claude Code-credentials" -w | jq .claudeAiOauth`

### Slow statusline refresh
- First run shows 0% values while background refresh populates cache
- Subsequent runs always instant (~0.2s) - refresh happens in background
- If consistently slow, check for shell startup issues

## Uninstallation

Remove the `statusLine` key from `~/.claude/settings.json`:

```bash
jq 'del(.statusLine)' ~/.claude/settings.json > tmp.json && mv tmp.json ~/.claude/settings.json
```

## Usage Analytics

### Calculating 5h/7d Consumption Ratio

The statusline logs usage data to `/tmp/claude-usage-log.csv`. Use the included script to analyze how much 5-hour capacity you consume per 1% of 7-day utilization:

```bash
python3 plugins/statusline/scripts/calc_usage_ratio.py
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

- **1.2.0** (2026-01-08): Added calc_usage_ratio.py for 5h/7d consumption analysis
- **1.1.0** (2026-01-05): Non-blocking architecture - read cache first, background refresh, atomic writes
- **1.0.0** (2025-12-19): Initial release

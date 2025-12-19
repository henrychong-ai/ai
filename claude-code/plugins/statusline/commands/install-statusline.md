---
description: Install statusline configuration
allowed-tools: ["Bash", "Read"]
---

# Install Statusline

Run the installation script to add the Statusline to your Claude Code configuration.

The script will:
1. Check for required dependencies (jq, ccusage, curl)
2. Backup your existing settings.json
3. Merge the statusline configuration into your settings
4. Validate the result

Execute the installer:

```bash
~/.claude/plugins/marketplaces/*/plugins/statusline/scripts/install.sh
```

After installation, restart Claude Code to see the new statusline displaying:
- Directory and git branch
- Current model
- Daily/block costs with time remaining
- Context window usage
- Rate limit utilization (5h, 7d, sonnet)

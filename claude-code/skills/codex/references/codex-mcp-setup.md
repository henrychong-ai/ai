# Codex MCP Server Setup

Setup guide for the OpenAI Codex CLI MCP server, integrating GPT-5.3 models with Claude Code and Claude Desktop.

## Prerequisites

- **macOS** (Homebrew required)
- **ChatGPT Plus/Pro subscription** (browser-based auth, no API keys)
- **Node.js** (v18+)
- **Claude Code** or **Claude Desktop**

## Installation

### 1. Install Codex CLI

```bash
brew tap openai/codex-cli
brew install codex
codex --version
```

### 2. Authenticate

Opens browser for ChatGPT login. Persists across sessions.

```bash
codex auth
```

### 3. Create Config

```bash
mkdir -p ~/.codex
cat > ~/.codex/config.toml << 'EOF'
sandbox_mode    = "workspace-write"
approval_policy = "never"
model           = "gpt-5.3-codex"
model_reasoning_effort = "high"

[features]
web_search_request = true

[sandbox_workspace_write]
network_access = true
EOF
```

### 4. Add MCP Server

**CRITICAL:** The `-c model="gpt-5.3-codex"` flag is required at startup to prevent empty responses.

#### Claude Code

```bash
claude mcp add --scope user codex codex mcp-server -c 'model="gpt-5.3-codex"'
```

Or manually add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "codex": {
      "type": "stdio",
      "command": "codex",
      "args": [
        "mcp-server",
        "-c",
        "model=\"gpt-5.3-codex\""
      ],
      "env": {},
      "autoapprove": [
        "codex",
        "codex-reply"
      ]
    }
  }
}
```

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "codex": {
      "command": "/opt/homebrew/bin/codex",
      "args": [
        "mcp-server",
        "-c",
        "model=\"gpt-5.3-codex\""
      ]
    }
  }
}
```

**Note:** Claude Desktop requires the full path to `codex`. Find yours with `which codex`.

### 5. Restart and Verify

Restart Claude Code/Desktop, then test:

```
use codex low: Return "MCP test successful"
```

## Troubleshooting

### Empty Responses

**Cause:** Model not configured at MCP server startup.

**Fix:** Ensure args include `-c model="gpt-5.3-codex"`, then restart.

### Authentication Issues

```bash
codex auth logout
codex auth
```

### Complete Reinstall

```bash
brew uninstall codex && brew untap openai/codex-cli
claude mcp remove codex
rm -rf ~/.codex
# Then restart from step 1
```

## Resources

- [Codex CLI GitHub](https://github.com/openai/codex-cli)
- [OpenAI Platform](https://platform.openai.com)

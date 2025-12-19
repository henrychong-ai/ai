# Codex MCP Server Installation Guide
*Complete Auto-Executable Installation Guide for GPT-5.2 Models*

## Mission

This document provides complete, auto-executable instructions for installing the Codex MCP server on Claude Code and Claude Desktop. Claude Code can read this file and perform the entire installation process autonomously.

**HOW TO USE THIS GUIDE**:
1. **In Claude Code**: Simply reference this file in your conversation
   - Example: "Please read and execute the setup from claude-code/mcp/codex-mcp-setup.md"
   - Claude Code will then automatically execute all the installation steps

The Codex MCP server integrates OpenAI's most advanced coding models (gpt-5.2-codex and gpt-5.2) with Claude Code, providing multi-step reasoning capabilities with configurable effort levels (none/low/medium/high/xhigh) for complex technical challenges, architectural decisions, and performance optimization.

**KEY VALUE PROPOSITIONS**:
- **Enhanced Reasoning**: Multi-step problem decomposition for complex logic and architecture
- **Second Opinion**: Validate Claude's solutions with an alternative advanced AI perspective
- **Configurable Depth**: Adjust reasoning effort based on task complexity (5 levels)
- **Dual Models**: gpt-5.2-codex for coding, gpt-5.2 for general tasks
- **Parallel Processing**: Run multiple Codex sessions concurrently for comprehensive analysis

## Prerequisites Verification

**CRITICAL**: Before installation, verify these requirements:

1. **macOS**: Required for Homebrew installation
2. **ChatGPT Account**: Plus or Pro subscription for gpt-5.2-codex access
3. **Homebrew**: Package manager for macOS
4. **Node.js & NPM**: Required for MCP server execution
5. **Claude Code**: Version 1.0+ with MCP support
6. **Claude Desktop**: Latest version (optional but recommended)

**AUTO-VERIFICATION COMMANDS**:
```bash
# Check macOS version
sw_vers -productVersion

# Check if Homebrew is installed (install if missing)
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is installed: $(brew --version)"
fi

# Check Node.js version (should be 16+ for best compatibility)
node --version

# Check NPM availability
npm --version

# Verify Claude Code MCP functionality
claude mcp list

# Check if Codex CLI is already installed
if command -v codex &> /dev/null; then
    echo "Codex CLI already installed: $(codex --version)"
else
    echo "Codex CLI not found. Will install via Homebrew."
fi
```

## Authentication Overview

**IMPORTANT: ChatGPT Browser Authentication**

The Codex CLI uses **browser-based ChatGPT authentication**, NOT API keys. This provides:
- **Security**: No API keys stored in configuration files
- **Convenience**: Uses existing ChatGPT login session
- **Team Compliance**: Each developer uses their individual ChatGPT Plus/Team account
- **Session Management**: Automatic token refresh and session handling

**AUTHENTICATION PROCESS**:
1. First run of `codex` opens your default browser
2. Log in with your ChatGPT Plus/Team account
3. Authorize the Codex CLI application
4. Authentication persists across sessions
5. Re-authentication required only when session expires

## Claude Code MCP Installation

**AUTO-EXECUTION SEQUENCE**:

### Step 1: Install Codex CLI via Homebrew
```bash
# Add OpenAI tap to Homebrew
brew tap openai/codex-cli

# Install Codex CLI
brew install codex

# Verify installation
codex --version

# Find Codex installation path (needed for Claude Desktop)
CODEX_PATH=$(which codex)
echo "Codex installed at: $CODEX_PATH"
```

### Step 2: Authenticate with ChatGPT
```bash
# Initial authentication (will open browser)
echo "Running initial Codex authentication..."
echo "Your browser will open. Please:"
echo "1. Log in with your ChatGPT Plus/Team account"
echo "2. Authorize the Codex CLI application"
echo "3. Return to terminal after successful authorization"
codex auth

# Verify authentication
codex exec "echo 'Authentication successful!'"
```

### Step 3: Create Codex Configuration
```bash
# Create Codex config directory if it doesn't exist
mkdir -p ~/.codex

# Create optimized config for GPT-5.2
cat > ~/.codex/config.toml << 'EOF'
# Codex Configuration for GPT-5.2
# Optimized for development workflows

sandbox_mode    = "workspace-write"
approval_policy = "never"
model           = "gpt-5.2-codex"
model_reasoning_effort = "high"

[features]
web_search_request = true

[sandbox_workspace_write]
network_access = true
EOF

echo "Codex configuration created at ~/.codex/config.toml"
```

### Step 4: Add MCP Server to Claude Code Configuration

**CRITICAL**: The MCP server must be configured with the model at startup to avoid empty response issues.

```bash
# Add Codex MCP server to Claude Code with model config
# NOTE: The -c model="gpt-5.2-codex" flag is REQUIRED to prevent empty responses
claude mcp add \
  --scope user \
  codex \
  codex \
  mcp-server \
  -c \
  'model="gpt-5.2-codex"'

echo "Codex MCP server added to Claude Code configuration"
echo ""
echo "IMPORTANT: Restart Claude Code to load the new MCP server"
```

**Manual Configuration Alternative**:

If the `claude mcp add` command doesn't work correctly, manually add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "codex": {
      "type": "stdio",
      "command": "codex",
      "args": [
        "mcp-server",
        "-c",
        "model=\"gpt-5.2-codex\""
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

**Why the `-c model="gpt-5.2-codex"` flag is required**:
Without this flag, the MCP server may return empty responses for gpt-5.2-codex model calls. This is a known issue where the model must be configured at server startup, not just per-request.

## Claude Desktop MCP Installation

**AUTO-EXECUTION SEQUENCE**:

### Step 1: Backup Existing Configuration
```bash
# Create backup of current Claude Desktop config
DESKTOP_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$DESKTOP_CONFIG" ]; then
    cp "$DESKTOP_CONFIG" "${DESKTOP_CONFIG}.backup"
    echo "Backed up existing Claude Desktop configuration"
else
    echo "No existing Claude Desktop configuration found"
fi
```

### Step 2: Update Claude Desktop Configuration
```bash
# Get Codex path (handles both Intel and Apple Silicon Macs)
CODEX_PATH=$(which codex)
echo "Using Codex at: $CODEX_PATH"

# Create or update Claude Desktop configuration
# NOTE: Full path required for Claude Desktop, and model config at startup
cat > "$HOME/Library/Application Support/Claude/claude_desktop_config_update.json" << EOF
{
  "mcpServers": {
    "codex": {
      "command": "$CODEX_PATH",
      "args": [
        "mcp-server",
        "-c",
        "model=\"gpt-5.2-codex\""
      ]
    }
  }
}
EOF

# Merge with existing configuration if it exists
if [ -f "$DESKTOP_CONFIG" ]; then
    echo "Merging with existing Claude Desktop configuration..."
    if command -v jq &> /dev/null; then
        jq -s '.[0] * .[1]' "$DESKTOP_CONFIG" "$HOME/Library/Application Support/Claude/claude_desktop_config_update.json" > "$HOME/Library/Application Support/Claude/claude_desktop_config_new.json"
        mv "$HOME/Library/Application Support/Claude/claude_desktop_config_new.json" "$DESKTOP_CONFIG"
    else
        echo "WARNING: jq not installed. Manual merge required for Claude Desktop config."
        echo "Please manually add the Codex server configuration to your claude_desktop_config.json"
    fi
else
    mv "$HOME/Library/Application Support/Claude/claude_desktop_config_update.json" "$DESKTOP_CONFIG"
fi

# Clean up temporary file
rm -f "$HOME/Library/Application Support/Claude/claude_desktop_config_update.json"

echo "Claude Desktop configuration updated"
echo "Please restart Claude Desktop to load the new MCP server"
```

## Verification and Testing

**AUTOMATED VERIFICATION SEQUENCE**:

### Step 1: Verify Claude Code Installation
```bash
# List MCP servers to confirm codex server is installed
claude mcp list | grep codex

# Check the configuration includes model flag
cat ~/.claude.json | grep -A 10 '"codex"'
```

### Step 2: Test Basic Codex Operations

**Basic Connectivity Test** (in Claude Code conversation):
```
use codex low: Return only the text "MCP test successful"
```

**Test Both Models**:
```
use codex low: Return "gpt-5.2-codex working"
use codex -g low: Return "gpt-5.2 working"
```

### Step 3: Test All Reasoning Levels
```
use codex none: Simple hello world
use codex low: Write a hello world function
use codex medium: Design a basic rate limiter
use codex high: Architect a distributed cache
use codex xhigh: Design a CRDT-based collaborative editor
```

## Available Models and Reasoning Levels

### Models

| Model | Trigger | Description |
|-------|---------|-------------|
| `gpt-5.2-codex` | `use codex` | Specialized coding model (DEFAULT) |
| `gpt-5.2` | `use codex -g` | General purpose model |

### Reasoning Levels

| Level | Keyword | Description |
|-------|---------|-------------|
| `none` | `use codex none` | No extended thinking (fastest) |
| `low` | `use codex low` | Lightweight reasoning |
| `medium` | `use codex medium` | Balanced speed/quality |
| `high` | `use codex` | Thorough reasoning (DEFAULT) |
| `xhigh` | `use codex xhigh` | Maximum reasoning (slowest, highest quality) |

### Usage Examples

```
# Default: gpt-5.2-codex with high reasoning
use codex: Analyze this codebase architecture

# Fastest: no reasoning
use codex none: Format this JSON

# Maximum quality
use codex xhigh: Design a fault-tolerant distributed system

# General purpose model
use codex -g: Analyze this research paper

# General purpose with specific reasoning
use codex -g medium: Summarize these meeting notes
```

## MCP Tool Syntax Reference

### Primary Session
```
mcp__codex__codex({
  prompt: "[your prompt]",
  model: "gpt-5.2-codex"  // or "gpt-5.2"
})
```

### Continue Conversation
```
mcp__codex__codex-reply({
  conversationId: "[id from previous response]",
  prompt: "[follow-up question]"
})
```

## Troubleshooting

### Empty Responses from gpt-5.2-codex

**Symptom**: MCP tool returns empty output for gpt-5.2-codex but works for other models.

**Cause**: Model not configured at MCP server startup.

**Solution**: Ensure your MCP server config includes the `-c model="gpt-5.2-codex"` args:
```json
"codex": {
  "command": "codex",
  "args": [
    "mcp-server",
    "-c",
    "model=\"gpt-5.2-codex\""
  ]
}
```

Then restart Claude Code.

### Authentication Issues
```bash
# Clear authentication cache
codex auth logout
codex auth

# Verify ChatGPT subscription
echo "Ensure you have an active ChatGPT Plus or Pro subscription"
```

### MCP Connection Failed
```bash
# Remove and re-add MCP server
claude mcp remove codex

# Re-add with correct config
claude mcp add --scope user codex codex mcp-server -c 'model="gpt-5.2-codex"'

# Restart Claude Code
```

### Complete Reinstallation
```bash
# 1. Remove Codex CLI
brew uninstall codex
brew untap openai/codex-cli

# 2. Remove MCP configuration
claude mcp remove codex

# 3. Clean configuration files
rm -rf ~/.codex

# 4. Restart from Step 1 of installation
```

## Success Checklist

- [ ] Codex CLI installed via Homebrew (`codex --version` works)
- [ ] Authentication successful with ChatGPT account
- [ ] Configuration file created at `~/.codex/config.toml`
- [ ] MCP server added with `-c model="gpt-5.2-codex"` flag
- [ ] Claude Code restarted after MCP config change
- [ ] `use codex low: test` returns a response (not empty)
- [ ] Both models work: `use codex` and `use codex -g`
- [ ] All reasoning levels work: none/low/medium/high/xhigh

## Additional Resources

- [Codex CLI Documentation](https://github.com/openai/codex-cli)
- [OpenAI Platform](https://platform.openai.com)
- [MCP Protocol Specification](https://modelcontextprotocol.org)

---

*Integrating GPT-5.2 models with Claude Code via MCP*

*Version: 2.0.0 - Updated for GPT-5.2 (December 2025)*

---
description: Install all Claude Code extensions (agents, skills, commands)
allowed-tools: ["Bash", "Read"]
---

# Install Claude Code Extensions

Install the complete set of Claude Code extensions including agents, skills, and commands.

## What Gets Installed

**Agents** (to `~/.claude/agents/`):
- codex - OpenAI Codex MCP integration
- file-converter - Intelligent file format conversion
- instruction-creator - Claude instruction file architect
- media-downloader - Video/audio download from URLs

**Skills** (to `~/.claude/skills/`):
- 1password - Secrets management and op CLI
- ffmpeg - Video/audio processing
- instruction-creator - Instruction file reference guide
- pdf - PDF manipulation toolkit

**Commands** (to `~/.claude/commands/`):
- /kg - Knowledge Graph session capture
- /push - Intelligent git push workflow

## Installation

Run the installer script:

```bash
# Find and execute the installer
~/.claude/plugins/marketplaces/*/plugins/claude-code-extensions/scripts/install.sh
```

### Options

```bash
# Install only specific components
./scripts/install.sh --agents-only
./scripts/install.sh --skills-only
./scripts/install.sh --commands-only

# Skip backing up existing files
./scripts/install.sh --no-backup
```

## Post-Installation

After installation, restart Claude Code to load the new extensions.

For MCP server setup guides, see the `mcp/` directory in the plugin folder.

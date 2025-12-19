# Claude Code Extensions

A collection of agents, skills, commands, MCP server setup guides, and plugins for [Claude Code](https://claude.ai/code) - Anthropic's official CLI for Claude.

## What's Included

### 🤖 Agents

Autonomous domain specialists that handle complex, multi-step tasks. Copy to `~/.claude/agents/`.

| Agent | Description |
|-------|-------------|
| [codex](claude-code/agents/codex.md) | OpenAI Codex MCP integration for routing requests to gpt-5.1-codex models |
| [file-converter](claude-code/agents/file-converter.md) | Intelligent file format conversion with auto-detection (PDF, Markdown, DOCX, HTML, Mermaid, images) |
| [instruction-creator](claude-code/agents/instruction-creator.md) | Master architect for creating Claude instruction files (agents, skills, commands) |
| [media-downloader](claude-code/agents/media-downloader.md) | Download videos/audio from web URLs using yt-dlp with smart tool selection |

### 📚 Skills

Bundled knowledge packages with reference materials. Copy entire folder to `~/.claude/skills/`.

| Skill | Description |
|-------|-------------|
| [1password](claude-code/skills/1password/) | 1Password CLI, secrets management, op run setup, GitHub Actions integration |
| [ffmpeg](claude-code/skills/ffmpeg/) | Video/audio processing with hardware acceleration on Apple Silicon |
| [instruction-creator](claude-code/skills/instruction-creator/) | Quick reference for instruction file formats, templates, and best practices |
| [pdf](claude-code/skills/pdf/) | PDF manipulation: extraction, merging, forms, creating fillable templates |

### ⚡ Commands

Custom slash commands for common workflows. Copy to `~/.claude/commands/`.

| Command | Description |
|---------|-------------|
| [/kg](claude-code/commands/kg.md) | Token-efficient Knowledge Graph session capture and optimization |
| [/push](claude-code/commands/push.md) | Intelligent git push workflow with auto-generated commit messages |

### 🔧 MCP Server Setup Guides

Step-by-step installation guides for MCP servers. Claude Code can read and execute these automatically.

| Guide | Description |
|-------|-------------|
| [codex-mcp-setup](claude-code/mcp/codex-mcp-setup.md) | Install OpenAI Codex MCP for gpt-5.1-codex model integration |
| [mcp-neo4j-knowledge-graph-setup](claude-code/mcp/mcp-neo4j-knowledge-graph-setup.md) | Set up Neo4j-backed Knowledge Graph with embeddings |
| [sequential-thinking-mcp-setup](claude-code/mcp/sequential-thinking-mcp-setup.md) | Install Sequential Thinking MCP for structured problem-solving |

### 🔌 Plugins

Full plugins with installers for easy distribution. See plugin-specific READMEs for installation.

| Plugin | Description |
|--------|-------------|
| [statusline](claude-code/plugins/statusline/) | Statusline showing model, costs, context usage, and rate limit metrics |

## Installation

### Option 1: Automated Installer (Recommended)

```bash
# Clone and run the installer
git clone https://github.com/henrychong-ai/ai.git
cd ai/claude-code
./scripts/install.sh
```

The installer will:
- Copy all agents to `~/.claude/agents/`
- Copy all skills to `~/.claude/skills/`
- Copy all commands to `~/.claude/commands/`
- Backup any existing files before overwriting

**Installer options:**
```bash
./scripts/install.sh --agents-only    # Install only agents
./scripts/install.sh --skills-only    # Install only skills
./scripts/install.sh --commands-only  # Install only commands
./scripts/install.sh --no-backup      # Skip backing up existing files
```

### Option 2: Plugin Marketplace

Add this repository as a plugin marketplace source, then install via Claude Code:

```bash
# In Claude Code, run:
/install-extensions
```

### Option 3: Manual Install

1. **Agents**: Copy individual `.md` files to `~/.claude/agents/`
2. **Skills**: Copy entire skill folder (with `SKILL.md` and `references/`) to `~/.claude/skills/`
3. **Commands**: Copy `.md` files to `~/.claude/commands/`
4. **MCP Guides**: Reference directly in Claude Code conversations
5. **Plugins**: Follow plugin-specific installation instructions

### Using MCP Setup Guides

In Claude Code, simply reference the guide file:

```
Please read and execute the setup from /path/to/ai/claude-code/mcp/sequential-thinking-mcp-setup.md
```

Claude Code will automatically execute all installation steps.

## Directory Structure

```
ai/
└── claude-code/
    ├── .claude-plugin/   # Plugin metadata
    │   └── plugin.json
    ├── scripts/          # Installation scripts
    │   └── install.sh
    ├── agents/           # Autonomous domain specialists
    │   ├── codex.md
    │   ├── file-converter.md
    │   ├── instruction-creator.md
    │   └── media-downloader.md
    ├── commands/         # Custom slash commands
    │   ├── kg.md
    │   └── push.md
    ├── mcp/              # MCP server setup guides
    │   ├── codex-mcp-setup.md
    │   ├── mcp-neo4j-knowledge-graph-setup.md
    │   └── sequential-thinking-mcp-setup.md
    ├── plugins/          # Nested plugins
    │   └── statusline/
    ├── plugin-commands/  # Plugin-specific commands
    │   └── install-extensions.md
    └── skills/           # Bundled knowledge packages
        ├── 1password/
        ├── ffmpeg/
        ├── instruction-creator/
        └── pdf/
```

## Requirements

- **Claude Code** v1.0+ with MCP support
- **macOS** recommended (some features use macOS-specific tools)
- **Node.js & npm** for MCP server installation

### Skill-Specific Requirements

| Skill/Plugin | Dependencies |
|--------------|--------------|
| ffmpeg | `brew install ffmpeg` |
| pdf | `uv pip install pypdf pdfplumber` |
| statusline | `brew install jq`, `npm install -g ccusage` |
| 1password | 1Password CLI (`op`) |

## Usage Examples

### Using Agents

Agents auto-activate based on triggers or can be invoked explicitly:

```
# File conversion (auto-triggers on "convert this file")
Convert this PDF to markdown

# Media download (auto-triggers on URLs)
Download this video: https://youtube.com/watch?v=...

# Codex integration (explicit trigger)
use codex to optimize this function
```

### Using Skills

Invoke skills with the "use skill" pattern:

```
use skill pdf to fill this form
use skill ffmpeg to compress this video
```

### Using Commands

Type the command name directly:

```
/push          # Smart git push with auto-commit message
/kg            # Capture session knowledge to KG
```

## Contributing

Contributions welcome! When adding new components:

1. **Agents**: Include YAML frontmatter with `name`, `description`, and `model`
2. **Skills**: Create folder with `SKILL.md` and optional `references/` subdirectory
3. **Commands**: Include YAML frontmatter with `name` and `description`
4. **MCP Guides**: Make them auto-executable by Claude Code

## License

Individual components may have their own licenses. Check component-specific files for details.

## Author

Henry Chong ([@henrychong-ai](https://github.com/henrychong-ai))

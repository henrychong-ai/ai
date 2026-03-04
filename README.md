# Claude Code Resources

A collection of agents, skills, and commands for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Installation

Copy the items you need to your Claude Code configuration:

```bash
# Copy a skill
cp -r claude-code/skills/typescript ~/.claude/skills/

# Copy an agent
cp claude-code/agents/file-converter.md ~/.claude/agents/

# Copy a command
cp commands/kg.md ~/.claude/commands/
```

Or point Claude Code at this repo and ask it to install what you need.

## Contents

### Agents

Autonomous domain specialists that handle complex, multi-step tasks. Copy to `~/.claude/agents/`.

| Agent | Description |
|-------|-------------|
| [file-converter](claude-code/agents/file-converter.md) | Intelligent file format conversion with auto-detection and validation |
| [instruction-creator](claude-code/agents/instruction-creator.md) | Create and review Claude Code instruction files (agents, skills, commands) |
| [media-downloader](claude-code/agents/media-downloader.md) | Download videos/audio from web URLs using yt-dlp |

### Skills

Bundled knowledge packages with reference materials. Copy entire folder to `~/.claude/skills/`.

| Skill | Description |
|-------|-------------|
| [1password](claude-code/skills/1password/) | 1Password CLI, secrets management, op run setup |
| [claude-code-config](claude-code/skills/claude-code-config/) | Statusline setup with real-time cost, context, and OAuth utilization metrics |
| [codex](claude-code/skills/codex/) | OpenAI Codex MCP integration for second opinions |
| [dotnet](claude-code/skills/dotnet/) | .NET development specialist for enterprise applications |
| [ffmpeg](claude-code/skills/ffmpeg/) | Video/audio processing with ffmpeg |
| [gemini-gem-creator](claude-code/skills/gemini-gem-creator/) | Create and convert Gemini Custom Gems |
| [go](claude-code/skills/go/) | Go development specialist for backends, APIs, CLI tools |
| [images](claude-code/skills/images/) | Image processing and manipulation |
| [instruction-creator](claude-code/skills/instruction-creator/) | Guide for creating Claude Code instruction files |
| [lint](claude-code/skills/lint/) | Linting and formatting setup for TypeScript/JavaScript projects |
| [pdf](claude-code/skills/pdf/) | PDF manipulation toolkit (extract, create, merge, split, forms) |
| [typescript](claude-code/skills/typescript/) | TypeScript development specialist with Cloudflare Workers, React, Node.js patterns |
| [typescript-version-upgrade](claude-code/skills/typescript-version-upgrade/) | Node.js/TypeScript version upgrade protocols |

### Commands

Custom slash commands for common workflows. Copy to `~/.claude/commands/`.

| Command | Description |
|---------|-------------|
| [/kg](claude-code/commands/kg.md) | Knowledge Graph query shortcuts |
| [/push](claude-code/commands/push.md) | Git push with validation |

## Directory Structure

```
ai/
└── claude-code/
    ├── agents/           # Autonomous domain specialists
    │   ├── file-converter.md
    │   ├── instruction-creator.md
    │   └── media-downloader.md
    ├── commands/         # Custom slash commands
    │   ├── kg.md
    │   └── push.md
    └── skills/           # Bundled knowledge packages
        ├── 1password/
        ├── claude-code-config/
        ├── codex/
        ├── dotnet/
        ├── ffmpeg/
        ├── gemini-gem-creator/
        ├── go/
        ├── images/
        ├── instruction-creator/
        ├── lint/
        ├── pdf/
        ├── typescript/
        └── typescript-version-upgrade/
```

## Usage

### Using Skills

Skills are invoked with `/skill-name` or automatically triggered based on context:

```
/typescript   # Invoke TypeScript skill
/pdf          # Invoke PDF skill
```

### Using Agents

Agents are invoked via the Agent tool or auto-triggered based on their description:

```
Use the file-converter agent to convert document.pdf to markdown
```

### Using Commands

Commands are invoked with `/command-name`:

```
/kg search "topic"
/push
```

## Requirements

- **Claude Code** v1.0+
- **macOS** recommended (some features use macOS-specific tools)

## Contributing

1. Fork this repository
2. Create your feature branch
3. Ensure all sensitive/personal information is removed
4. Submit a pull request

## License

MIT License - see individual files for specific attributions.

## Related

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [@henrychong-ai/mcp-neo4j-knowledge-graph](https://www.npmjs.com/package/@henrychong-ai/mcp-neo4j-knowledge-graph)

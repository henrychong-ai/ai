# Claude Code Resources

A collection of agents, skills, commands, and MCP server setup guides for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Directory Structure

```
claude-code/
├── agents/           # Autonomous domain specialist agents
├── commands/         # Slash command definitions
├── skills/           # Specialized knowledge packages with bundled resources
├── mcp/              # MCP server setup guides
├── plugins/          # Claude Code plugins
└── scripts/          # Utility scripts
```

## Installation

Copy the directories you need to your Claude Code configuration:

```bash
# Copy a skill
cp -r skills/typescript ~/.claude/skills/

# Copy an agent
cp agents/file-converter.md ~/.claude/agents/

# Copy a command
cp commands/kg.md ~/.claude/commands/
```

## Contents

### Skills

| Skill | Description |
|-------|-------------|
| **typescript** | TypeScript development specialist with Cloudflare Workers, React, Node.js patterns |
| **go** | Go development specialist for backends, APIs, CLI tools |
| **dotnet** | .NET development specialist for enterprise applications |
| **python** | Python development specialist (reference only) |
| **pdf** | PDF manipulation toolkit (extract, create, merge, split, forms) |
| **lint** | Linting and formatting setup for TypeScript/JavaScript projects |
| **ffmpeg** | Video/audio processing with ffmpeg |
| **images** | Image processing and manipulation |
| **codex** | OpenAI Codex MCP integration for second opinions |
| **1password** | 1Password developer configuration and secrets management |
| **instruction-creator** | Guide for creating Claude Code instruction files |
| **gemini-gem-creator** | Create and convert Gemini Custom Gems |
| **typescript-version-upgrade** | Node.js/TypeScript version upgrade protocols |

### Agents

| Agent | Description |
|-------|-------------|
| **file-converter** | Intelligent file format conversion with validation |
| **media-downloader** | Download videos/audio from web URLs |
| **instruction-creator** | Create instruction files and review existing ones |

### MCP Setup Guides

| Guide | Description |
|-------|-------------|
| **mcp-neo4j-knowledge-graph-setup** | Automated setup for Neo4j Knowledge Graph MCP |
| **sequential-thinking-mcp-setup** | Setup guide for Yggdrasil sequential thinking |
| **codex-mcp-setup** | OpenAI Codex MCP server configuration |

### Commands

| Command | Description |
|---------|-------------|
| **/kg** | Knowledge Graph query shortcuts |
| **/push** | Git push with validation |

### Plugins

| Plugin | Description |
|--------|-------------|
| **statusline** | Custom statusline configuration for Claude Code |

## Usage

### Using a Skill

Skills are invoked with `/skill-name` or automatically triggered based on context:

```
/typescript   # Invoke TypeScript skill
/pdf          # Invoke PDF skill
```

### Using an Agent

Agents are invoked via the Task tool or auto-triggered based on their description:

```
Use the file-converter agent to convert document.pdf to markdown
```

### Using a Command

Commands are invoked with `/command-name`:

```
/kg search "topic"
/push
```

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

# AI Resources

A collection of Claude Code extensions (agents, skills, commands, plugins) and Gemini Custom Gems.

## Installation

Copy the items you need to your Claude Code configuration:

```bash
# Copy a skill
cp -r claude-code/skills/typescript ~/.claude/skills/

# Copy an agent
cp claude-code/agents/file-converter.md ~/.claude/agents/

# Copy a command
cp claude-code/commands/kg.md ~/.claude/commands/

# Copy a plugin
cp -r claude-code/plugins/statusline ~/.claude/plugins/
```

Or point Claude Code at this repo and ask it to install what you need.

## Contents

### Agents

Autonomous domain specialists that handle complex, multi-step tasks. Copy to `~/.claude/agents/`.

| Agent | Description |
|-------|-------------|
| [codex-relay](claude-code/agents/codex-relay.md) | Mechanical relay to the OpenAI Codex plugin — one companion-CLI call, response returned verbatim |
| [file-converter](claude-code/agents/file-converter.md) | Intelligent file format conversion with auto-detection and validation |
| [media-downloader](claude-code/agents/media-downloader.md) | Download videos/audio from web URLs using yt-dlp |

### Skills

Bundled knowledge packages with reference materials. Copy entire folder to `~/.claude/skills/`.

| Skill | Description |
|-------|-------------|
| [1password](claude-code/skills/1password/) | 1Password CLI, secrets management, op run setup |
| [codex](claude-code/skills/codex/) | Route work to OpenAI GPT-6 (Astra/Sol/Luna) through the official Codex plugin — second opinions and code review (requires the Codex plugin and the `codex-relay` agent) |
| [ffmpeg](claude-code/skills/ffmpeg/) | Video/audio processing with ffmpeg |
| [gemini-gem-creator](claude-code/skills/gemini-gem-creator/) | Create and convert Gemini Custom Gems |
| [go](claude-code/skills/go/) | Go development specialist for backends, APIs, CLI tools |
| [images](claude-code/skills/images/) | Image processing and manipulation |
| [instruction-creator](claude-code/skills/instruction-creator/) | Create Claude instruction files (agents, skills, commands, MCP servers) and package skills for Claude Desktop upload (skill zips, linked Desktop Projects, sanitization, fork subagents, cross-platform conversion) |
| [lint](claude-code/skills/lint/) | Linting and formatting across ecosystems — TypeScript/JavaScript (Oxlint + Biome, residual ESLint), Python (Ruff), Go (golangci-lint v2), .NET (Roslyn), Solidity — with gitleaks pre-commit secret scanning and copy-ready templates |
| [typescript](claude-code/skills/typescript/) | TypeScript development — strict type patterns, Vitest testing, Hono/tRPC/`@hono/zod-openapi` single-source APIs, Cloudflare Workers, NestJS core, Astro content sites |
| [typescript-version-upgrade](claude-code/skills/typescript-version-upgrade/) | Node.js/TypeScript version upgrade protocols |

### Plugins

Reusable configuration packages. Copy entire folder to `~/.claude/plugins/`.

| Plugin | Description |
|--------|-------------|
| [statusline](claude-code/plugins/statusline/) | Real-time statusline with cost tracking, context usage, and OAuth utilization metrics |

### Commands

Custom slash commands for common workflows. Copy to `~/.claude/commands/`.

| Command | Description |
|---------|-------------|
| [/kg](claude-code/commands/kg.md) | Capture the current session into a knowledge graph with deduplication (requires a knowledge-graph MCP server, e.g. [@henrychong-ai/mcp-neo4j-knowledge-graph](https://www.npmjs.com/package/@henrychong-ai/mcp-neo4j-knowledge-graph)) |
| [/push](claude-code/commands/push.md) | Git commit and push with validation, generated commit messages, and an approval step |

### Gemini Custom Gems

Ready-to-use [Gemini Custom Gems](https://gemini.google.com/). Copy the instructions into Gemini's gem builder.

| Gem | Description |
|-----|-------------|
| [Dossier](gemini-gems/dossier/) | OSINT intelligence dossier generator with 7-pass search methodology, confidence ratings, and structured templates for individuals and companies. Best with Deep Research mode. |
| [Gemini Gem Creator](gemini-gems/gemini-gem-creator.md) | Build, optimise, and validate custom Gemini gems using the 4-component framework (Persona/Task/Context/Format) with canvas-based building and the 5-test quality framework. |

## Directory Structure

```
ai/
├── claude-code/
│   ├── agents/           # Autonomous domain specialists
│   ├── commands/         # Custom slash commands
│   ├── plugins/          # Reusable configuration packages
│   │   └── statusline/   # Cost, context, and utilization metrics
│   └── skills/           # Bundled knowledge packages
└── gemini-gems/
    ├── dossier/          # OSINT intelligence dossier generator
    │   ├── dossier.md
    │   └── attachments/  # Knowledge base files (.txt)
    └── gemini-gem-creator.md   # Gem creation methodology (build / convert / optimise gems)
```

## Usage

### Using Skills

Skills are invoked with `/skill-name` or automatically triggered based on context:

```
/typescript   # Invoke TypeScript skill
/lint         # Invoke lint skill
```

### Using Agents

Agents are invoked via the Agent tool or auto-triggered based on their description:

```
Use the file-converter agent to convert document.pdf to markdown
```

### Using Commands

Commands are invoked with `/command-name`:

```
/kg          # Capture this session into the knowledge graph
/push
```

### Using Gemini Gems

Each gem directory contains a markdown file with instructions between `---BEGIN GEM INSTRUCTIONS---` and `---END GEM INSTRUCTIONS---` markers. Copy that block into Gemini's gem builder, upload any attachments to the knowledge base, and you're ready to go.

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

**Third-party code:** `claude-code/skills/instruction-creator/scripts/init_skill.py`, `package_skill.py` and `quick_validate.py` contain portions derived from Anthropic's [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator), licensed under the Apache License 2.0 (copy in `claude-code/skills/instruction-creator/scripts/LICENSE-APACHE-2.0.txt`).

## Related

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [@henrychong-ai/mcp-neo4j-knowledge-graph](https://www.npmjs.com/package/@henrychong-ai/mcp-neo4j-knowledge-graph)

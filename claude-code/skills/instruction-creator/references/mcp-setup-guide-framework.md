# MCP Server Setup Guide Framework

Complete framework for creating MCP server setup guides for team distribution.

**Updated:** 2026-02-24

---

## MCP Installation Scope Decision Matrix

**Apply this FIRST before any MCP setup.**

### Use `--scope user` (Global/User) When:
- Individual developer accessing MCP server
- Personal productivity tools you want everywhere
- Personal authentication credentials (PAT tokens, API keys)
- Tools used across ALL projects and directories
- Stored in: `~/.claude.json` → top-level `mcpServers`
- Command: `claude mcp add --scope user <name> <command>`

### Use `--scope local` (Project) When:
- Specialised tools for specific projects (avoid context pollution)
- Experimental or development-phase MCP servers
- Directory-specific functionality
- Default behaviour when `--scope` flag omitted
- Stored in: `~/.claude.json` → `projects['/path/to/project'].mcpServers`

### Use `--scope project` (Team/.mcp.json) When:
- Multiple developers EXPLICITLY need identical MCP server configuration
- Shared team credentials and authentication (rare)
- Standardised development environment requirements
- Repository-specific tooling for collaborative projects
- CI/CD pipeline integration requirements
- Creates `.mcp.json` in project directory

**Default Recommendation:** `--scope user` for personal tools, `--scope local` for project-specific. Team scope is rare.

```bash
# User scope (appears everywhere)
claude mcp add --scope user yggdrasil "npx -y yggdrasil-mcp"

# Project-only scope (current directory only)
claude mcp add atlassian "https://mcp.atlassian.com/v1/sse"

# Team scope (creates .mcp.json)
claude mcp add --scope project docker "node /path/to/mcp-docker/dist/index.js"
```

---

## Seven-Phase Setup Guide Framework

### Phase 1: Business Value Foundation
- MCP server purpose and team benefits
- Use case documentation with specific examples
- ROI framework and productivity metrics
- **Scope Decision**: Apply installation scope matrix FIRST

### Phase 2: Technical Prerequisites Assessment
- System requirements and compatibility verification
- Dependency analysis and installation requirements
- Environment preparation and validation
- Pre-installation health checks

### Phase 3: Dual-Platform Installation Coverage
- **Claude Code Installation**: Complete installation with verification
- **Claude Desktop Configuration**: JSON config management with backup
- **Configuration Synchronisation**: Consistent setup across platforms
- **CRITICAL: Executable Path Requirements**: Full paths for Claude Desktop (sandbox), relative paths OK for Claude Code (shell environment)

### Phase 4: Configuration Management
- JSON configuration template generation
- Configuration backup and versioning
- Sync script integration for maintenance
- Environment variable and path management

### Phase 5: Verification and Testing
- Installation success verification with test procedures
- Functionality validation through practical use cases
- Performance testing and optimisation confirmation
- Integration testing with existing MCP ecosystem

### Phase 6: Troubleshooting and Recovery
- Common issue identification and resolution
- Error pattern recognition and debugging
- Recovery strategies for failed installations
- Support escalation criteria

### Phase 7: Team Integration and Workflow
- Team distribution procedures and onboarding
- Usage pattern documentation and best practices
- Integration with existing workflows
- Ongoing maintenance and update procedures

---

## Standard MCP Setup Guide Template

```markdown
---
mcp_server: [server-name]
version: 1.0
setup_type: dual_platform
last_updated: YYYY-MM-DD
token_estimate: ~6000
business_value: [specific benefits]
---

# [MCP Server Name] Setup Guide
*Auto-Executable Installation*
*Claude Code + Desktop*
*Version X.Y - YYYY-MM-DD*

## Business Value & Use Cases
[Specific business benefits and practical applications]

### Key Capabilities
- [Capability 1 with business impact]
- [Capability 2 with productivity gain]
- [Integration with existing workflows]

## Prerequisites & System Requirements
[Detailed prerequisite verification with commands]

### Environment Verification
\`\`\`bash
# System requirement checks
[specific verification commands]
\`\`\`

## Auto-Executable Installation

### Phase 1: Claude Code Installation
\`\`\`bash
# [Step-by-step installation commands with verification]
\`\`\`

**Verification:**
\`\`\`bash
# [Commands to verify success]
\`\`\`

### Phase 2: Claude Desktop Configuration

**CRITICAL PATH REQUIREMENT**: Claude Desktop requires full executable paths.

\`\`\`json
{
  "mcpServers": {
    "server-name": {
      "command": "/opt/homebrew/bin/npx",
      "args": ["-y", "package-name"],
      "env": {
        "KEY": "value"
      }
    }
  }
}
\`\`\`

**Path Discovery:**
\`\`\`bash
which npx    # /opt/homebrew/bin/npx
which uv     # /Users/user/.local/bin/uv
which node   # /opt/homebrew/bin/node
\`\`\`

## Verification & Testing Protocol

### Installation Success
\`\`\`bash
# [Comprehensive verification commands]
\`\`\`

### Functionality Testing
[Specific test procedures with expected results]

## Troubleshooting Framework

### Common Issues & Solutions
**Issue**: [Problem description]
**Symptoms**: [How to identify]
**Resolution**: [Step-by-step solution]
**Verification**: [How to confirm fix]

## Team Integration
1. [Distribution steps]
2. [Onboarding procedures]
3. [Consistency verification]
```

---

## Troubleshooting Decision Trees

### Installation Failure
```
Installation Failed?
├── Dependency Issue?
│   ├── Missing runtime → Install prerequisites
│   └── Version Conflict → Update dependencies
├── Network Issue?
│   ├── Proxy/Firewall → Configure network settings
│   └── Repository Access → Verify availability
└── Permission Issue?
    ├── File System → Update permissions
    └── Security Policy → Escalate to IT
```

### Configuration Problems
```
Configuration Not Working?
├── JSON Syntax Error?
│   ├── Invalid JSON → Validate and fix syntax
│   └── Missing Fields → Add required fields
├── Path Issues?
│   ├── Incorrect Paths → Verify and update
│   └── Permissions → Update file permissions
└── Service Integration?
    ├── Claude Code Not Recognising → Restart and verify
    └── Claude Desktop Not Loading → Check config location
```

---

## Credential Security Protocol

**MANDATORY when MCP server requires credentials.**

### Secure Configuration Pattern (1Password)

```json
{
  "mcpServers": {
    "service-name": {
      "command": "op",
      "args": ["run", "--env-file=/path/to/.env", "--", "npx", "-y", "mcp-server-package"],
      "env": {}
    }
  }
}
```

### Environment File Pattern
```bash
# 1Password secret references - NOT plaintext values
API_KEY=op://Development/ServiceName/api-key
AUTH_TOKEN=op://Development/ServiceName/token
SECRET=op://Development/ServiceName/secret
```

### Credential Decision Tree
```
MCP Server Requires Credentials?
├── YES → MANDATORY: Use 1Password integration
│   ├── Store credentials in appropriate vault
│   ├── Create .env file with op:// references
│   └── Configure MCP with op run wrapper
└── NO → Standard MCP configuration (no wrapper needed)
```

### Anti-Patterns to Avoid
- Plaintext API keys in JSON config files
- Hardcoded tokens in MCP server arguments
- Environment variables with actual secret values
- Credentials committed to version control

---

## Verification Command Library

```bash
# Claude Code MCP server verification
claude mcp list | grep [server-name]

# Claude Desktop configuration verification
jq '.mcpServers."[server-name]"' ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Functionality testing
[server-specific test commands]
```

### Success Criteria
- MCP server listed in Claude Code installations
- JSON configuration properly formatted and loaded
- Basic functionality test passes
- Integration with existing workflow confirmed

---

## QA Checklist for MCP Setup Guides

- [ ] Complete auto-executable installation procedure
- [ ] Dual-platform coverage (Claude Code + Desktop)
- [ ] Business value and use case documentation
- [ ] Comprehensive verification and testing protocols
- [ ] Troubleshooting framework with decision trees
- [ ] Configuration management and backup strategies
- [ ] Credential security (1Password if applicable)

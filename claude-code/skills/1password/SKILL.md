---
name: 1password
description: This skill should be used for 1Password developer configuration, secrets management, op CLI usage, MCP server credential injection, op run setup, wrapper scripts, the Environments .env feature, GitHub Actions CI/CD integration, and AWS Secrets Manager sync. Auto-triggers on "1password", "op run", "op://", "secret reference", "credential injection", "secrets management", "vault", "biometric unlock", "GitHub Actions secrets", "CI/CD secrets", "AWS Secrets Manager", "shell plugins". Covers service accounts, Developer Watchtower, activity logging, and troubleshooting.
---

# 1Password Developer & Secrets Management

Expert guidance for 1Password CLI, secrets management, and secure credential injection for development workflows.

## Quick Reference

### Secret Reference Syntax
```
op://<vault>/<item>[/section]/<field>
```

**Examples:**
- `op://Personal/Sunsama/password`
- `op://Work/GitHub/api-token`
- `op://${VAULT:-dev}/database/connection-string` (with default)

### Core Commands

| Command | Purpose |
|---------|---------|
| `op run --env-file=.env -- cmd` | Inject secrets as env vars, run command |
| `op read "op://vault/item/field"` | Read single secret to stdout |
| `op inject -i template -o output` | Replace op:// refs in template file |
| `op account list` | List connected accounts |
| `op vault list` | List accessible vaults |
| `op item list --vault=VaultName` | List items in vault |
| `op signin` | Authenticate to 1Password |

### Three Methods to Use Secret References

| Method | Use Case | Secrets Persist? |
|--------|----------|------------------|
| `op run` | Runtime injection to process | No (memory only) |
| `op read` | Single value to stdout/file | No |
| `op inject` | Template file substitution | Yes (writes to file) |

## Decision Matrix: op run vs Environments

| Use Case | Best Choice | Reason |
|----------|-------------|--------|
| **MCP servers** | op run | Concurrent access safe |
| **Claude Code integration** | op run | Explicit env injection |
| **CI/CD pipelines** | op run | Scriptable, automatable |
| **Local dev apps** | Environments | Always available when unlocked |
| **Team onboarding** | Environments | GUI-based, easy setup |
| **Windows development** | op run | Environments not supported |
| **Multiple concurrent processes** | op run | No single-reader limit |

## MCP Server Configuration

### Why op run for MCP Servers
- Secrets injected at process start only
- Never stored on disk (memory only)
- Cleared when process exits
- No concurrent access issues (unlike Environments)
- LLM never sees actual secret values

### Setup Pattern

**Step 1: Create .env file with op:// references**
```bash
mkdir -p ~/.config/mcp-credentials
cat > ~/.config/mcp-credentials/server-name.env << 'EOF'
API_KEY=op://Personal/ServiceName/api-key
PASSWORD=op://Personal/ServiceName/password
EOF
# This file is SAFE to commit - contains only references
```

**Step 2: Configure MCP server in ~/.claude.json**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "op",
      "args": [
        "run",
        "--env-file=/Users/USERNAME/.config/mcp-credentials/server-name.env",
        "--",
        "npx",
        "mcp-server-package"
      ]
    }
  }
}
```

### Locked Vault Behavior

| Scenario | What Happens |
|----------|--------------|
| **Biometric enabled** | Touch ID prompt appears |
| **1Password fully locked** | MCP fails to start with error |
| **After unlocking** | Must manually restart: `/mcp restart server-name` |

**Note:** Claude Code does NOT auto-retry failed MCP servers after 1Password unlock.

For wrapper scripts and advanced patterns, see `references/mcp-server-setup.md`.

## CI/CD Integration (GitHub Actions)

Use `1password/load-secrets-action` for secure secrets in GitHub Actions workflows.

### Quick Setup
```yaml
- uses: 1password/load-secrets-action/configure@v1
  with:
    service-account-token: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}

- uses: 1password/load-secrets-action@v1
  with:
    secret-API_KEY: op://vault/item/api-key
```

### Key Features
- Automatic log masking (secrets replaced with `***`)
- Service Account or Connect Server authentication
- Mac/Linux runners only (Windows unsupported)

See `references/github-actions-guide.md` for complete workflows and examples.

## AWS Secrets Manager Sync

Sync environment variables from 1Password to AWS Secrets Manager for applications running on AWS infrastructure.

### Use Cases
- Centralize secrets for AWS applications
- Share secrets without sharing AWS credentials
- Single source of truth in 1Password

### Key Points
- One-directional sync (1Password → AWS)
- Uses AWS Nitro Enclaves for secure handling
- 64KB max environment size
- Requires IAM role with SAML 2.0 federation

See `references/aws-secrets-manager.md` for complete setup guide.

## 1Password Environments (Beta)

Virtual .env file mounting - secrets delivered via UNIX pipe, never on disk.

### Best For
- Local development with apps that read .env files
- Team secret sharing (built-in GUI)
- "Always on" secret access when 1Password unlocked

### NOT For
- MCP servers (single-reader limitation causes failures)
- CI/CD pipelines (no CLI support)
- Windows (unsupported platform)
- Multiple concurrent processes

### Key Limitations
- Max 10 local .env files per device
- Single reader at a time (concurrent access fails)
- GUI-only management (no CLI commands)
- Beta status - may change

**Setup:** 1Password app → Settings → Developer → View Environments

See `references/environments-guide.md` for complete setup guide.

## Security Features

| Feature | Purpose | How to Enable |
|---------|---------|---------------|
| **Developer Watchtower** | Detect plaintext secrets on disk | Settings → Developer → Developer Watchtower |
| **Activity Logging** | Audit CLI usage | Settings → Developer → Record activity |
| **Biometric Unlock** | Touch ID for CLI | Settings → Developer → Integrate with CLI |
| **Vault Separation** | Access control | Organize items by vault |
| **Service Accounts** | CI/CD automation | 1Password.com → Developer |

## Biometric Integration Setup

```bash
# Verify CLI installed
op --version

# Check app integration status
op account list

# Test vault access (will prompt Touch ID if configured)
op vault list
```

**Enable in 1Password app:**
1. Settings → Developer → "Integrate with 1Password CLI"
2. Settings → Security → Enable Touch ID

**Environment variable control:**
```bash
# Temporarily disable biometric
export OP_BIOMETRIC_UNLOCK_ENABLED=false
```

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| "Unexpected response from 1Password" | Unlock 1Password app |
| No Touch ID prompt | Enable CLI integration in Settings → Developer |
| "Connection reset" error | System Settings → Login Items → Allow 1Password in background |
| MCP won't start after unlock | `/mcp restart server-name` or restart Claude Code |
| CLI prompts for every request | Use `op run` to batch; check biometric enabled |

See `references/troubleshooting.md` for detailed solutions.

## Common Patterns

### Shell Plugins (40+ Supported)
Automatic credential injection for CLI tools:
- **Cloud:** AWS, Azure, Google Cloud
- **DevOps:** Terraform, Kubernetes, Ansible
- **Git:** GitHub CLI, GitLab CLI
- **Databases:** PostgreSQL, MySQL, MongoDB

```bash
# Initialize plugin
op plugin init aws

# Biometric auth per command - no stored credentials
aws s3 ls
```

### Credential File Organization
```
~/.config/mcp-credentials/
├── sunsama.env      # Sunsama MCP credentials
├── github.env       # GitHub MCP credentials
├── database.env     # Database credentials
└── ...
```

### Wrapper Script (Optional, for Multiple MCPs)
```bash
#!/bin/bash
# ~/.config/1password/op-mcp-wrapper
if ! op account get &>/dev/null; then
    echo "Please sign in to 1Password" >&2
    exit 1
fi
op run --env-file="$HOME/.config/mcp-credentials/$1.env" -- "${@:2}"
```

### Service Account for CI/CD
```bash
# Set token (don't commit this!)
export OP_SERVICE_ACCOUNT_TOKEN="your-token"

# Now op commands work without biometric
op run --env-file=.env -- ./deploy.sh
```

## References

Detailed guides in `references/` subdirectory:
- **op-run-guide.md** - Complete op run usage, shell plugins, and patterns
- **mcp-server-setup.md** - MCP-specific configuration
- **environments-guide.md** - 1Password Environments feature
- **github-actions-guide.md** - CI/CD integration with GitHub Actions
- **aws-secrets-manager.md** - AWS Secrets Manager sync setup
- **troubleshooting.md** - Common issues and solutions
- **security-best-practices.md** - Hardening recommendations

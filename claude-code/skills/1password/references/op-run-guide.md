# op run Complete Guide

## Overview

`op run` is the recommended method for injecting 1Password secrets into processes at runtime. Secrets exist only in memory during process execution and are cleared when the process exits.

## Secret Reference Syntax

### Basic Format
```
op://<vault>/<item>[/section]/<field>
```

### Components
| Component | Required | Description |
|-----------|----------|-------------|
| `vault` | Yes | Vault name or ID |
| `item` | Yes | Item name or ID |
| `section` | No | Section within item (for complex items) |
| `field` | Yes | Field name (password, username, api-key, etc.) |

### Examples
```bash
# Basic reference
op://Personal/GitHub/api-token

# With section
op://Work/Database/Production/connection-string

# Using vault ID
op://abc123xyz/ServiceName/password

# With environment variable default
op://${VAULT:-Personal}/Item/field
```

## Three Methods Compared

### op run (Recommended for Processes)
```bash
op run --env-file=.env -- ./my-app
```
- Injects secrets as environment variables
- Secrets only in subprocess memory
- Cleared when process exits
- Best for: MCP servers, applications, scripts

### op read (Single Values)
```bash
# To stdout
op read "op://Personal/GitHub/api-token"

# To file
op read "op://Personal/SSH/private-key" > ~/.ssh/id_rsa

# With output format
op read "op://Personal/Certificate/cert" --out-file=cert.pem

# Pipe to remote command via SSH (e.g., docker login)
op read "op://Work/GitHub/github-pat-package-registry" | ssh root@server "docker login ghcr.io -u USERNAME --password-stdin"
```
- Reads one secret at a time
- Good for: shell scripts, one-off retrieval, remote authentication

### op inject (Template Substitution)
```bash
op inject -i config.tpl -o config.json
```
- Replaces op:// references in template files
- Writes resolved content to output file
- **Caution:** Output file contains plaintext secrets
- Good for: generating config files (use carefully)

## op run Deep Dive

### Basic Usage
```bash
# With env file
op run --env-file=.env -- command arg1 arg2

# With inline env vars
export API_KEY="op://Personal/Service/key"
op run -- ./my-script.sh

# Multiple env files
op run --env-file=base.env --env-file=secrets.env -- ./app
```

### Environment File Format
```bash
# .env file with secret references
DATABASE_URL=op://Work/Database/connection-string
API_KEY=op://Work/ServiceAPI/key
SECRET_TOKEN=op://Work/Auth/token

# Can mix with non-secret values
LOG_LEVEL=debug
ENVIRONMENT=production
```

### How op run Works

1. **Scan**: Reads environment variables and env files
2. **Identify**: Finds all `op://` references
3. **Authenticate**: Prompts for biometric/password if needed
4. **Fetch**: Retrieves secrets from 1Password
5. **Inject**: Sets secrets as environment variables
6. **Execute**: Runs the specified command as subprocess
7. **Clear**: When subprocess exits, secrets are gone

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ .env file   │────▶│   op run    │────▶│  Subprocess │
│ (op:// refs)│     │  resolves   │     │  (has real  │
│             │     │  secrets    │     │   values)   │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                    │
                          ▼                    ▼
                    ┌───────────┐        Process exits,
                    │ 1Password │        secrets cleared
                    │   Vault   │
                    └───────────┘
```

## Wrapper Script Pattern

### Generic Wrapper
```bash
#!/bin/bash
# ~/.config/1password/op-mcp-wrapper

# Pre-flight check
if ! op account get &>/dev/null; then
    echo "Error: Please sign in to 1Password first" >&2
    echo "Run: op signin" >&2
    exit 1
fi

# Run with specified env file
ENV_FILE="$HOME/.config/mcp-credentials/$1.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Credentials file not found: $ENV_FILE" >&2
    exit 1
fi

op run --env-file="$ENV_FILE" -- "${@:2}"
```

### Usage
```bash
# Make executable
chmod +x ~/.config/1password/op-mcp-wrapper

# Use with MCP config
~/.config/1password/op-mcp-wrapper sunsama npx mcp-sunsama
```

## Environment Variables

### OP_BIOMETRIC_UNLOCK_ENABLED
```bash
# Temporarily disable biometric (use password instead)
export OP_BIOMETRIC_UNLOCK_ENABLED=false
op run --env-file=.env -- ./app

# Re-enable
unset OP_BIOMETRIC_UNLOCK_ENABLED
```

### OP_SERVICE_ACCOUNT_TOKEN
```bash
# For CI/CD or automation (no biometric available)
export OP_SERVICE_ACCOUNT_TOKEN="ops_xxxxxxxxxxxx"
op run --env-file=.env -- ./deploy.sh
```

### OP_CONNECT_HOST / OP_CONNECT_TOKEN
```bash
# For 1Password Connect server
export OP_CONNECT_HOST="https://connect.example.com"
export OP_CONNECT_TOKEN="your-connect-token"
```

## Advanced Patterns

### Conditional Secrets
```bash
# .env with environment-specific vault
DATABASE_URL=op://${ENVIRONMENT:-dev}/Database/url
```

### Chaining Commands
```bash
op run --env-file=.env -- sh -c 'echo $API_KEY | base64'
```

### Piping
```bash
op run --env-file=.env -- ./generate-config.sh | tee config.json
```

### Timeout
```bash
# op run inherits from subprocess
timeout 30 op run --env-file=.env -- ./long-running-task.sh
```

## Verification Commands

### Verify Secrets Are Injected
```bash
# Check specific variable is set
op run --env-file=.env -- printenv | grep API_KEY

# Check all op:// references resolved
op run --env-file=.env -- env | grep -E "^(API|SECRET|TOKEN|KEY)"

# Verify outside subprocess (should NOT show value)
echo $API_KEY  # Empty - secrets don't leak to parent shell
```

## Shell Plugins

1Password provides 40+ shell plugins for automatic credential injection in CLI tools.

### Supported Tools
- **Cloud:** AWS CLI, Azure CLI, Google Cloud SDK
- **DevOps:** Terraform, Ansible, Kubernetes (kubectl)
- **Git:** GitHub CLI, GitLab CLI
- **Databases:** PostgreSQL, MySQL, MongoDB
- **AI/ML:** OpenAI CLI
- **Package managers:** npm, cargo, pip

### How Shell Plugins Work
1. Install plugin: `op plugin init aws`
2. Plugin wraps the CLI tool
3. Credentials injected via biometric authentication
4. No manual credential entry or storage

### Multi-Environment Switching
```bash
# Switch credential profile
op plugin configure aws --profile production

# Use specific vault for environment
export OP_VAULT=Production
aws s3 ls
```

### Custom Plugin Development
Build plugins for unsupported tools using 1Password's plugin framework. See [Shell Plugins documentation](https://developer.1password.com/docs/cli/shell-plugins/).

## Security Considerations

1. **Never log secrets**: Be careful with debug output
2. **Subprocess isolation**: Secrets only in child process
3. **No disk writes**: Secrets never touch filesystem
4. **Biometric required**: Each session needs authentication
5. **Audit trail**: Activity logged if enabled

## Common Issues

### "Could not find item"
- Check vault name spelling
- Verify item exists: `op item get "ItemName" --vault="VaultName"`
- Check account: `op account list`

### "Authentication required"
- 1Password may be locked
- Biometric may have timed out
- Run `op signin` to re-authenticate

### Slow startup
- Many secrets = many fetches
- Consider consolidating items
- Use caching strategies where safe

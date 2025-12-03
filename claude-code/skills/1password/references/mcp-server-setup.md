# MCP Server Setup with 1Password

## Why op run for MCP Servers

MCP servers require credentials at startup. Using `op run`:
- Secrets injected only when server starts
- Never written to disk
- Cleared when server process exits
- LLM never sees actual credential values
- No concurrent access issues (unlike Environments)

## Setup Methods

### Method 1: Direct op run (Recommended)

Simplest approach - configure op run directly in MCP config.

**Step 1: Create credentials file**
```bash
mkdir -p ~/.config/mcp-credentials

cat > ~/.config/mcp-credentials/sunsama.env << 'EOF'
SUNSAMA_EMAIL=op://Personal/Sunsama/email
SUNSAMA_PASSWORD=op://Personal/Sunsama/password
EOF
```

**Step 2: Configure MCP server**

For Claude Code (`~/.claude.json`):
```json
{
  "mcpServers": {
    "sunsama": {
      "command": "op",
      "args": [
        "run",
        "--env-file=/Users/USERNAME/.config/mcp-credentials/sunsama.env",
        "--",
        "npx",
        "mcp-sunsama"
      ]
    }
  }
}
```

### Method 2: Wrapper Script (For Multiple MCPs)

Better when managing many MCP servers with similar patterns.

**Step 1: Create wrapper script**
```bash
mkdir -p ~/.config/1password

cat > ~/.config/1password/op-mcp-wrapper << 'EOF'
#!/bin/bash
# Generic MCP wrapper with 1Password

# Check 1Password status
if ! op account get &>/dev/null; then
    echo "Error: 1Password not authenticated" >&2
    echo "Please unlock 1Password or run: op signin" >&2
    exit 1
fi

# First arg is the credentials file name (without .env)
CREDS_NAME="$1"
shift

ENV_FILE="$HOME/.config/mcp-credentials/${CREDS_NAME}.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Credentials file not found: $ENV_FILE" >&2
    exit 1
fi

exec op run --env-file="$ENV_FILE" -- "$@"
EOF

chmod +x ~/.config/1password/op-mcp-wrapper
```

**Step 2: Configure MCP server**
```json
{
  "mcpServers": {
    "sunsama": {
      "command": "/Users/USERNAME/.config/1password/op-mcp-wrapper",
      "args": ["sunsama", "npx", "mcp-sunsama"]
    },
    "github": {
      "command": "/Users/USERNAME/.config/1password/op-mcp-wrapper",
      "args": ["github", "npx", "@modelcontextprotocol/server-github"]
    }
  }
}
```

## Claude Code vs Claude Desktop

### Claude Code
- Can use relative commands (`op`, `npx`)
- Inherits shell PATH
- More flexible

### Claude Desktop
- Requires **full paths** to executables
- Runs in sandbox without PATH
- Must use: `/opt/homebrew/bin/op`, `/opt/homebrew/bin/npx`

**Find full paths:**
```bash
which op     # /opt/homebrew/bin/op
which npx    # /opt/homebrew/bin/npx
```

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "sunsama": {
      "command": "/opt/homebrew/bin/op",
      "args": [
        "run",
        "--env-file=/Users/USERNAME/.config/mcp-credentials/sunsama.env",
        "--",
        "/opt/homebrew/bin/npx",
        "mcp-sunsama"
      ]
    }
  }
}
```

## Credential File Organization

### Recommended Structure
```
~/.config/mcp-credentials/
├── sunsama.env       # Sunsama MCP
├── github.env        # GitHub MCP
├── linear.env        # Linear MCP
├── database.env      # Database MCP
└── ...
```

### Template for New MCP
```bash
# Create new credentials file
cat > ~/.config/mcp-credentials/NEW_SERVICE.env << 'EOF'
# NEW_SERVICE MCP credentials
# Reference: op://Vault/Item/field
SERVICE_API_KEY=op://Personal/NewService/api-key
SERVICE_SECRET=op://Personal/NewService/secret
EOF
```

## Locked Vault Behavior

### With Biometric Enabled (Recommended)

1. Claude Code starts MCP server
2. `op run` detects 1Password locked
3. **Touch ID prompt appears**
4. User authenticates
5. Secrets fetched, MCP starts

### Without Biometric / Fully Locked

1. Claude Code starts MCP server
2. `op run` fails immediately
3. Error: "unexpected response from 1Password app"
4. MCP server **does not start**
5. Tools unavailable in Claude

### Recovery After Unlock

**Important:** Claude Code does NOT auto-retry failed MCP servers.

**To recover:**
```bash
# Option 1: In Claude Code
/mcp restart sunsama

# Option 2: Restart Claude Code entirely
# Quit and reopen the application
```

## Startup Flow Diagram

```
Claude Code Launch
       │
       ▼
  Start MCP Server
       │
       ▼
  op run executes
       │
       ├── 1Password Unlocked ────────▶ ✅ Secrets fetched
       │                                       │
       │                                       ▼
       │                                 MCP Server Starts
       │
       ├── Biometric Available ───────▶ 🔐 Touch ID Prompt
       │                                       │
       │                               ┌───────┴───────┐
       │                               ▼               ▼
       │                          User Approves   User Cancels
       │                               │               │
       │                               ▼               ▼
       │                          ✅ MCP Starts   ❌ MCP Fails
       │
       └── 1Password Locked ──────────▶ ❌ Error
                                              │
                                              ▼
                                        MCP Unavailable
                                        (manual restart needed)
```

## Multiple Accounts

If you have multiple 1Password accounts:

```bash
# List accounts
op account list

# Specify account in secret reference
op://my.1password.com/Personal/Item/field
op://company.1password.com/Work/Item/field
```

## Troubleshooting MCP + 1Password

### MCP Server Won't Start

1. **Check 1Password unlocked:**
   ```bash
   op vault list  # Should list vaults without error
   ```

2. **Verify credentials file exists:**
   ```bash
   cat ~/.config/mcp-credentials/sunsama.env
   ```

3. **Test op run manually:**
   ```bash
   op run --env-file=~/.config/mcp-credentials/sunsama.env -- env | grep SUNSAMA
   ```

4. **Check MCP server logs:**
   ```bash
   # In Claude Code, check for errors in output
   ```

### Touch ID Not Prompting

1. Check CLI integration enabled:
   - 1Password → Settings → Developer → "Integrate with 1Password CLI"

2. Check Touch ID enabled:
   - 1Password → Settings → Security → Touch ID

3. Check background permissions:
   - System Settings → Login Items → Allow 1Password in background

### "Item not found" Error

1. Verify item exists:
   ```bash
   op item get "Sunsama" --vault="Personal"
   ```

2. Check field name:
   ```bash
   op item get "Sunsama" --vault="Personal" --format=json | jq '.fields[].label'
   ```

3. Correct the reference in .env file

## Security Best Practices

1. **Credentials file permissions:**
   ```bash
   chmod 600 ~/.config/mcp-credentials/*.env
   ```

2. **Directory permissions:**
   ```bash
   chmod 700 ~/.config/mcp-credentials
   ```

3. **Never commit credentials directory**

4. **Use separate vaults** for different sensitivity levels

5. **Enable activity logging** for audit trail

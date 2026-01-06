# 1Password SSH Agent Configuration

## Overview

1Password's SSH agent securely stores and provides SSH keys without exposing private keys on disk. The agent authenticates using biometric (Touch ID) when an SSH connection is attempted.

**Key Benefits:**
- Private keys never leave 1Password
- Biometric authentication for each connection
- Works across all SSH clients
- Centralized key management

## SSH Agent vs CLI/Secrets

| Feature | SSH Agent | op CLI (Secrets) |
|---------|-----------|------------------|
| Purpose | SSH key management | Secret references |
| Config file | `~/.config/1Password/ssh/agent.toml` | N/A (op:// refs) |
| Integration | SSH protocol | Environment variables |
| Use case | Git, SSH connections | API keys, passwords |

## Default Behavior

By default, the SSH agent makes available **only** keys from:
- Personal vault
- Private vault
- Employee vault

Keys in **shared or custom vaults** (e.g., "DevOps") require explicit configuration.

## Config File Location

```
~/.config/1Password/ssh/agent.toml
```

Create the directory if it doesn't exist:
```bash
mkdir -p ~/.config/1Password/ssh
```

## Enabling Keys from Non-Default Vaults

### Enable Entire Vault

Add all SSH keys from a vault:

```toml
[[ssh-keys]]
vault = "DevOps"
```

### Enable Specific Key

Add a single SSH key by item name:

```toml
[[ssh-keys]]
item = "Production-Server"
vault = "DevOps"
```

### Complete Example

```toml
# Default vaults
[[ssh-keys]]
vault = "Private"

[[ssh-keys]]
vault = "Personal"

# Custom vaults
[[ssh-keys]]
vault = "Work"

# Specific key from shared vault
[[ssh-keys]]
item = "Production-Server"
vault = "DevOps"
```

## Config File Syntax (TOML)

### Available Fields

| Field | Required | Description |
|-------|----------|-------------|
| `vault` | Yes* | Vault name containing the key |
| `item` | No | Specific item name (if omitted, all keys in vault) |
| `account` | No | Account identifier (for multi-account setups) |

*Either `vault` or `item` must be specified.

### Key Order

The order of `[[ssh-keys]]` entries determines the order keys are offered to SSH servers. Place frequently-used keys first to avoid the 6-key authentication limit.

```toml
# Offered first (most used)
[[ssh-keys]]
item = "GitHub SSH"
vault = "Personal"

# Offered second
[[ssh-keys]]
item = "Bitbucket SSH"
vault = "Personal"

# All remaining keys from vault
[[ssh-keys]]
vault = "Work"
```

## SSH Client Configuration

Configure SSH to use 1Password's agent socket:

**~/.ssh/config:**
```
Host *
    IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
```

## Verification Commands

### List Available Keys

```bash
SSH_AUTH_SOCK=~/Library/Group\ Containers/2BUA8C4S2C.com.1password/t/agent.sock ssh-add -l
```

Expected output:
```
256 SHA256:abc123... GitHub SSH (ED25519)
256 SHA256:def456... Bitbucket SSH (ED25519)
256 SHA256:ghi789... Production-Server (ED25519)
```

### Test Connection

```bash
ssh -T git@github.com
```

1Password will prompt for Touch ID, then display:
```
Hi username! You've successfully authenticated...
```

## Enabling SSH Agent (First-Time Setup)

1. Open 1Password app
2. Settings → Developer
3. Click "Set Up SSH Agent"
4. Choose display preference for key names
5. Configure `~/.ssh/config` as shown above

## Troubleshooting

### Key Not Appearing in ssh-add -l

1. **Check vault name matches exactly:**
   ```bash
   op vault list
   ```

2. **Check item name matches exactly:**
   ```bash
   op item list --vault="DevOps" | grep -i ssh
   ```

3. **Verify item is SSH Key type:**
   ```bash
   op item get "Production-Server" --vault="DevOps" --format=json | jq '.category'
   # Should return: "SSH_KEY"
   ```

4. **Restart 1Password app** after config changes

### SSH Connection Fails

1. **Verify agent socket exists:**
   ```bash
   ls -la ~/Library/Group\ Containers/2BUA8C4S2C.com.1password/t/agent.sock
   ```

2. **Check SSH config syntax:**
   ```bash
   ssh -vvv git@github.com 2>&1 | grep -i identity
   ```

3. **Ensure 1Password is unlocked**

### Touch ID Not Prompting

1. Check CLI integration:
   - 1Password → Settings → Developer → "Integrate with 1Password CLI"

2. Check SSH Agent enabled:
   - 1Password → Settings → Developer → SSH Agent settings

3. Check background permissions:
   - System Settings → Login Items → Allow 1Password in background

### Multiple 1Password Accounts

Specify account in config:

```toml
[[ssh-keys]]
account = "company.1password.com"
vault = "DevOps"
item = "Production-Server"
```

List accounts:
```bash
op account list
```

## Key Requirements

For an SSH key to be available via the agent:

1. **Item type**: Must be "SSH Key" category (not Login or Secure Note)
2. **Key type**: Ed25519 or RSA (Ed25519 recommended)
3. **Status**: Must be active (not archived or deleted)
4. **Vault access**: Vault must be in your account's accessible vaults
5. **Config**: Vault/item must be listed in agent.toml (or be in default vaults)

## Creating SSH Keys in 1Password

### Generate New Key

1. Open 1Password
2. Click + → SSH Key
3. Choose key type (Ed25519 recommended)
4. Name the key descriptively
5. Save to appropriate vault

### Import Existing Key

1. Open 1Password
2. Click + → SSH Key
3. Click "Import" or paste private key
4. Save to appropriate vault

After creating/importing, add the public key to your servers or Git hosting provider.

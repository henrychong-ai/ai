# 1Password Environments Guide

## Overview

1Password Environments (Beta) provides virtual .env file mounting. Secrets are delivered via UNIX named pipe - never stored on disk in plaintext.

**Platform Availability:** Desktop only (macOS, Linux). Not available on iOS/Android.

### Supported Libraries

Works with standard dotenv libraries - no code changes required:
- Python (`python-dotenv`)
- Node.js (`dotenv`)
- Ruby (`dotenv`)
- Go (`godotenv`)
- Java (`dotenv-java`)
- PHP (`vlucas/phpdotenv`)
- Rust (`dotenv`)
- C# (`DotNetEnv`)
- Docker Compose

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   1Password     │────▶│  Virtual .env    │────▶│   Application   │
│   Environment   │     │  (UNIX pipe)     │     │   reads .env    │
│   (in app)      │     │  at ~/path/.env  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │
         ▼
   Secrets delivered on-demand
   Never stored on disk
   Auto-remounts on 1Password restart
```

### Key Characteristics
- **Virtual file**: Mounted via UNIX named pipe
- **On-demand**: Secrets fetched when file is read
- **No persistence**: Contents never written to disk
- **Auto-mount**: Remounts when 1Password restarts
- **Single reader**: Only one process can read at a time

## Setup Process

### Prerequisites
- 1Password desktop app (Mac or Linux)
- Developer features enabled

### Step 1: Enable Developer Experience
1. Open 1Password app
2. Settings → Developer
3. Enable "Show 1Password Developer experience"

### Step 2: Create Environment
1. Navigate to Developer → View Environments
2. Click "New environment"
3. Enter name (e.g., "MyProject-Dev")
4. Select account (if multiple)
5. Save

### Step 3: Add Variables
**Option A: Manual entry**
1. Click "Add variable"
2. Enter KEY and VALUE
3. Repeat for each variable

**Option B: Import existing .env**
1. Click "Import .env file"
2. Select your existing .env
3. Variables auto-populate

### Step 4: Configure Local Destination
1. In environment settings, find "Destinations"
2. Click "Add destination" → "Local .env file"
3. Specify path (e.g., `~/projects/myapp/.env`)
4. Save

The virtual .env file is now mounted at that path.

## Permissions & Access Control

### Permission Levels

| Level | Capabilities |
|-------|--------------|
| **View** | See environment and variable values |
| **Edit** | Modify variables and destinations |
| **Manage** | Full control including sharing and deletion |

### Managing Access

1. Open environment in 1Password
2. Click **Share** or access settings
3. Add users/groups
4. Assign permission level
5. Save changes

### Multi-Account Support

Environments are account-specific. Users can work across multiple independent 1Password accounts, each with separate environments.

## Offline Access

### How It Works
- Most recently synced secrets are cached locally
- Available when device is offline
- Updates sync when reconnected

### Limitations
- Only cached content available offline
- Local changes sync on reconnection
- First-time access requires connection

## When to Use Environments

### Best Use Cases

| Scenario | Why Environments Works |
|----------|------------------------|
| Local development | Always available when 1Password unlocked |
| Apps that read .env | Standard .env file interface |
| Team onboarding | GUI-based, easy for non-technical users |
| Quick secret access | No command wrapping needed |

### When NOT to Use

| Scenario | Why NOT Environments |
|----------|---------------------|
| **MCP servers** | Single-reader causes failures with concurrent starts |
| **CI/CD pipelines** | No CLI support - can't automate |
| **Windows** | Platform not supported |
| **Multiple processes** | Concurrent access fails |
| **Scripts/automation** | GUI-only management |

## Limitations

### Critical: Single Reader
```
⚠️ "If multiple processes try to read your local .env file
    at the same time, you may encounter delays or unexpected
    behaviors. The first process to access the file will
    succeed in reading the secrets, while others may fail."
```

**Impact on MCP servers:**
- Claude Code may start multiple MCP servers simultaneously
- First server gets secrets, others fail
- Unpredictable which servers work

### Platform Support
- ✅ macOS
- ✅ Linux
- ❌ Windows (not supported)

### Other Limits
- Maximum 10 local .env files per device
- GUI-only management (no CLI commands)
- Beta status - features may change
- Cannot script environment creation/modification
- **Deletion is permanent** - deleted environments cannot be restored

### IDE Concurrent Access Warning

IDEs that actively monitor or read .env files can cause conflicts:
- VS Code with dotenv extensions
- JetBrains IDEs with env file plugins
- Any tool that watches file changes

**Solution:** Temporarily disable .env file watchers in your IDE, or close other applications accessing the file.

## Environments vs op run

| Feature | op run | Environments |
|---------|--------|--------------|
| **Secrets on disk** | Never | Never (pipe) |
| **Management** | CLI + files | GUI only |
| **Concurrent access** | ✅ Safe | ❌ Single reader |
| **Automation** | ✅ Scriptable | ❌ Manual only |
| **MCP compatible** | ✅ Yes | ❌ No |
| **Platform** | All | Mac/Linux only |
| **Setup complexity** | Medium | Low |
| **Team sharing** | Via vaults | Built-in |

## Migration: .env to Environments

### From plaintext .env
1. Open 1Password → Developer → Environments
2. Create new environment
3. Import your existing .env file
4. Delete the plaintext .env file
5. Configure local destination at same path

### From op run
Generally don't migrate MCP configs from op run to Environments due to concurrent access issues. Keep using op run for MCP servers.

## Sharing Environments

### Within Shared Account
1. Environments inherit vault permissions
2. Team members with vault access see environments
3. Can grant view/edit/manage permissions

### Cross-Account
- Environments are account-specific
- Cannot share across different 1Password accounts
- Use shared vaults instead

## Troubleshooting

### .env file not appearing
1. Check 1Password is unlocked
2. Verify destination path is correct
3. Check 1Password has disk access permissions
4. Try: unmount and remount destination

### Git Conflict with Existing .env File

**Problem:** Can't mount because a tracked .env file exists.

**Solution:**
```bash
# Remove existing .env from Git (but keep local copy)
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from tracking"

# Add to .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Ignore .env files"

# Now mount the 1Password environment at that path
```

**Note:** Mounted .env files are NOT tracked by Git - they're virtual pipes, not real files.

### App can't read .env
1. Only one process can read at a time
2. Close other apps that might be reading
3. Check file path matches app's expected location

### Variables not updating
1. Changes may require app restart
2. Or remount the destination
3. Check environment is saved

### Beta Limitations
- Some features may not work as expected
- Report issues to 1Password
- Have fallback plan (op run) ready

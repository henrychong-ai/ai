# Codex MCP Server Installation Guide
*Complete Auto-Executable Installation Guide*

## 🎯 Mission

This document provides complete, auto-executable instructions for any developer to install the Codex MCP server on their Claude Code and Claude Desktop instances. Claude Code can read this file and perform the entire installation process autonomously.

**HOW TO USE THIS GUIDE**:
1. **In Claude Code**: Simply reference this file in your conversation
   - Example: "Please read and execute the setup from claude-code/shared/mcp/codex-mcp-setup.md"
   - Claude Code will then automatically execute all the installation steps

The Codex MCP server integrates OpenAI's most advanced coding model (gpt-5-codex) with Claude Code, providing multi-step reasoning capabilities with configurable effort levels (low/medium/high) for complex technical challenges, architectural decisions, and performance optimization.

**KEY VALUE PROPOSITIONS**:
- **Enhanced Reasoning**: Multi-step problem decomposition for complex logic and architecture
- **Second Opinion**: Validate Claude's solutions with an alternative advanced AI perspective
- **Configurable Depth**: Adjust reasoning effort based on task complexity (low/medium/high)
- **Parallel Processing**: Run multiple Codex sessions concurrently for comprehensive analysis
- **Team Collaboration**: Shared configuration and usage patterns across your development team

## 📋 Prerequisites Verification

**CRITICAL**: Before installation, verify these requirements:

1. **macOS**: Required for Homebrew installation
2. **ChatGPT Account**: Plus or Pro subscription for gpt-5-codex access
3. **Homebrew**: Package manager for macOS
4. **Node.js & NPM**: Required for MCP server execution
5. **Claude Code**: Version 1.0+ with MCP support
6. **Claude Desktop**: Latest version (optional but recommended)

**AUTO-VERIFICATION COMMANDS**:
```bash
# Check macOS version
sw_vers -productVersion

# Check if Homebrew is installed (install if missing)
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is installed: $(brew --version)"
fi

# Check Node.js version (should be 16+ for best compatibility)
node --version

# Check NPM availability
npm --version

# Verify Claude Code MCP functionality
claude mcp list

# Check if Codex CLI is already installed
if command -v codex &> /dev/null; then
    echo "Codex CLI already installed: $(codex --version)"
else
    echo "Codex CLI not found. Will install via Homebrew."
fi
```

## 🔐 Authentication Overview

**IMPORTANT: ChatGPT Browser Authentication**

The Codex CLI uses **browser-based ChatGPT authentication**, NOT API keys. This provides:
- **Security**: No API keys stored in configuration files
- **Convenience**: Uses existing ChatGPT login session
- **Team Compliance**: Each developer uses their individual ChatGPT Plus/Team account
- **Session Management**: Automatic token refresh and session handling

**AUTHENTICATION PROCESS**:
1. First run of `codex` opens your default browser
2. Log in with your ChatGPT Plus/Team account
3. Authorize the Codex CLI application
4. Authentication persists across sessions
5. Re-authentication required only when session expires

## 🚀 Claude Code MCP Installation

**AUTO-EXECUTION SEQUENCE**:

### Step 1: Install Codex CLI via Homebrew
```bash
# Add OpenAI tap to Homebrew
brew tap openai/codex-cli

# Install Codex CLI
brew install codex

# Verify installation
codex --version

# Find Codex installation path (needed for Claude Desktop)
CODEX_PATH=$(which codex)
echo "Codex installed at: $CODEX_PATH"
```

### Step 2: Authenticate with ChatGPT
```bash
# Initial authentication (will open browser)
echo "Running initial Codex authentication..."
echo "Your browser will open. Please:"
echo "1. Log in with your ChatGPT Plus/Team account"
echo "2. Authorize the Codex CLI application"
echo "3. Return to terminal after successful authorization"
codex auth

# Verify authentication
codex exec "echo 'Authentication successful!'"
```

### Step 3: Create Codex Configuration
```bash
# Create Codex config directory if it doesn't exist
mkdir -p ~/.codex

# Create optimized config
cat > ~/.codex/config.toml << 'EOF'
# Codex Configuration
# Optimized for development workflows

[model]
default = "gpt-5-codex"
# Reasoning effort is dynamically set via triggers (low/medium/high)
# Default medium provides balanced performance

[sandbox]
# workspace-write allows file operations within project scope
mode = "workspace-write"

[approval]
# Never require approval for MCP automation
policy = "never"

[output]
# Optimized for technical analysis
format = "detailed"
show_thinking = true

[session]
# Maintain context across interactions
preserve_context = true
max_context_length = 128000
EOF

echo "Codex configuration created at ~/.codex/config.toml"
```

### Step 4: Add MCP Server to Claude Code Configuration
```bash
# Add Codex MCP server to Claude Code
claude mcp add \
  --name codex \
  --command codex \
  --args "-m,gpt-5-codex,mcp" \
  --scope user \
  --autoapprove "codex,codex-reply"

echo "Codex MCP server added to Claude Code configuration"
```

## 🖥️ Claude Desktop MCP Installation

**AUTO-EXECUTION SEQUENCE**:

### Step 1: Backup Existing Configuration
```bash
# Create backup of current Claude Desktop config
DESKTOP_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$DESKTOP_CONFIG" ]; then
    cp "$DESKTOP_CONFIG" "${DESKTOP_CONFIG}.backup"
    echo "Backed up existing Claude Desktop configuration"
else
    echo "No existing Claude Desktop configuration found"
fi
```

### Step 2: Update Claude Desktop Configuration
```bash
# Get Codex path (handles both Intel and Apple Silicon Macs)
CODEX_PATH=$(which codex)
echo "Using Codex at: $CODEX_PATH"

# Create or update Claude Desktop configuration
cat > "$HOME/Library/Application Support/Claude/claude_desktop_config_update.json" << EOF
{
  "mcpServers": {
    "codex": {
      "command": "$CODEX_PATH",
      "args": [
        "-m",
        "gpt-5-codex",
        "mcp"
      ]
    }
  }
}
EOF

# Merge with existing configuration if it exists
if [ -f "$DESKTOP_CONFIG" ]; then
    echo "Merging with existing Claude Desktop configuration..."
    # This requires jq for JSON merging
    if command -v jq &> /dev/null; then
        jq -s '.[0] * .[1]' "$DESKTOP_CONFIG" "$HOME/Library/Application Support/Claude/claude_desktop_config_update.json" > "$HOME/Library/Application Support/Claude/claude_desktop_config_new.json"
        mv "$HOME/Library/Application Support/Claude/claude_desktop_config_new.json" "$DESKTOP_CONFIG"
    else
        echo "WARNING: jq not installed. Manual merge required for Claude Desktop config."
        echo "Please manually add the Codex server configuration to your claude_desktop_config.json"
    fi
else
    mv "$HOME/Library/Application Support/Claude/claude_desktop_config_update.json" "$DESKTOP_CONFIG"
fi

# Clean up temporary file
rm -f "$HOME/Library/Application Support/Claude/claude_desktop_config_update.json"

echo "Claude Desktop configuration updated"
echo "Please restart Claude Desktop to load the new MCP server"
```

## ✅ Verification and Testing

**AUTOMATED VERIFICATION SEQUENCE**:

### Step 1: Verify Claude Code Installation
```bash
# List MCP servers to confirm codex server is installed
claude mcp list | grep codex

# Test codex server connectivity
claude mcp test codex
```

### Step 2: Test Basic Codex Operations

**Basic Connectivity Test**:
Test the MCP tool directly in your Claude Code conversation:
```
User: Test Codex connection with: mcp__codex__codex({"prompt": "Hello Codex, confirm you're connected and ready", "config": {"model_reasoning_effort": "low"}})
```

**Different Reasoning Levels Test**:
```
User: use codex low: Write a simple hello world function in Go
User: use codex medium: Design a rate limiting algorithm for our API gateway
User: use codex high: Architect a distributed data processing system with ACID guarantees
```

### Step 3: Test Conversation Continuity
```
User: use codex: Start a conversation about optimizing database queries
# Note the conversationId in response
User: Continue with: mcp__codex__codex-reply({"conversationId": "[id]", "prompt": "Now explain connection pooling strategies"})
```

### Step 4: Verify Trigger Detection
```
User: use codex to analyze our application architecture
User: use codex high to review this complex business logic
User: use codex medium for debugging this race condition
```

## 🎯 CLAUDE.md Integration

**AUTO-UPDATE USER PREFERENCES**:

This section will automatically update your Claude Code global user preferences (`~/.claude/CLAUDE.md`) with the Codex MCP Integration Protocol.

### Step 1: Backup Current User Preferences
```bash
# Create backup of current CLAUDE.md
if [ -f "$HOME/.claude/CLAUDE.md" ]; then
    cp "$HOME/.claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md.backup"
    echo "Backed up existing CLAUDE.md"
else
    echo "No existing CLAUDE.md found - will create new one"
fi
```

### Step 2: Add Codex Integration Protocol to CLAUDE.md

**The following section will be added to your CLAUDE.md file:**

```bash
# Check if Codex section already exists to avoid duplication
if grep -q "## 🤖 Codex MCP Integration Protocol" "$HOME/.claude/CLAUDE.md" 2>/dev/null; then
    echo "Codex Integration Protocol already exists in CLAUDE.md"
else
    # Append Codex Integration Protocol to CLAUDE.md
    cat >> "$HOME/.claude/CLAUDE.md" << 'EOF'

## 🤖 Codex MCP Integration Protocol

### Detection Mechanism
- **Triggers**: ONLY when "use codex" OR "use codex high" OR "use codex medium" OR "use codex low" detected explicitly anywhere in user input

### Prompt Processing Pipeline
```
User Input → Extract Core Request → Optimize Prompt → Execute → Return Response
```
**Processing Steps:**
When Codex trigger detected:
1. Intelligently extract the key user request
2. Apply prompt optimization (remove filler, add all necessary context for Codex)
3. Execute via MCP tool with proper config structure: `mcp__codex__codex({prompt: "...", config: {...}})`
4. Return Codex's response directly without interpretation

### gpt-5-codex Description
gpt-5-codex is OpenAI's most advanced coding model, featuring enhanced reasoning capabilities that excel at complex code analysis, generation, and debugging tasks. Unlike standard models, gpt-5-codex performs multi-step reasoning with configurable effort levels (low/medium/high), allowing it to break down complex programming challenges, trace through intricate logic, and provide comprehensive solutions with detailed explanations. Its deep understanding of programming languages, frameworks, and development patterns makes it particularly effective for architectural decisions, performance optimization, and cross-language integration tasks that benefit from systematic reasoning rather than quick responses.

### Codex MCP Tool Parameters (KEY SPECIFICATION)
**MCP Tools Available**
- `mcp__codex__codex` → Run single conversation session
- `mcp__codex__codex-reply` → Continue existing conversation

**Trigger Detection for model_reasoning_effort config parameter during Codex MCP tool call:**
- `"codex:"` → Use medium reasoning effort (DEFAULT)
- `"codex high:"` → Use high reasoning effort (for difficult tasks)
- `"codex medium:"` → Use medium reasoning effort (for most tasks, as gpt-5-codex can dynamically adjust thinking levels during the task)
- `"codex low:"` → Use low reasoning effort (for simple, fast tasks)

**Verified Tool Call Structure & Syntax - MUST use for all Codex MCP tool calls:**
1. Primary tool call syntax to use:
```
mcp__codex__codex({
  prompt: "[optimized prompt]",
  config: {
    "model_reasoning_effort": "medium",  // or "high", "low"
  }
})
```
2. Conversation Continuity tool call syntax to use:
```
mcp__codex__codex-reply({
  conversationId: "[id from previous response]",
  prompt: "[follow-up question]"
})
```

#### Configuration Parameters for Reference ONLY
1. model_reasoning_effort:
  - Valid values: "low", "medium" (default), "high"
  - Invalid values: "minimal" (returns error)
  - Can be set via config.toml, command line flags, or tool config object

2. sandbox:
  - Valid values: "read-only", "workspace-write", "danger-full-access"
  - Provides access control guidance (not hard enforcement)
  - Configurable in ~/.codex/config.toml or via command line
  - Default config is "workspace-write"

3. approval-policy:
  - Valid values: "never", "on-request", "on-failure", "untrusted"
  - Controls when user approval is required for tool invocations
  - Default config is "never" to ensure mcp tool calls work without user interaction that might cause the tool to be blocked

### Parallel Execution
- **Run multiple Codex sessions concurrently when appropriate**
- Use multiple `mcp__codex__codex` tool calls in single response
- Ideal for: analyzing multiple files, comparing approaches, batch operations
- Each session runs independently with its own connection

### Second Opinion Protocol
**Use Codex as backup when encountering issues or uncertainty:**

#### Trigger Scenarios
- Error messages you can't resolve or understand
- Ambiguous documentation or conflicting information
- Complex problems requiring validation
- Need alternative approaches or solutions
- Unfamiliar technologies or frameworks
- Performance optimization challenges

#### Implementation
When triggered:
1. Formulate clear question including context and error details
2. Query Codex via MCP tool with high reasoning effort
3. Compare Codex's response with your analysis
4. Present both perspectives to user if they differ
5. Use consensus or note disagreement

### Response Handling
- Return Codex's raw output (no double-interpretation)
- Preserve thinking/reasoning if displayed
- Include conversation ID for follow-up sessions
- Show model and configuration info when relevant
EOF
    echo "Added Codex Integration Protocol to CLAUDE.md"
fi
```

### Step 3: Verify CLAUDE.md Update
```bash
# Verify the update was successful
if grep -q "## 🤖 Codex MCP Integration Protocol" "$HOME/.claude/CLAUDE.md"; then
    echo "✅ CLAUDE.md successfully updated with Codex Integration Protocol"
else
    echo "❌ Failed to update CLAUDE.md - manual intervention required"
fi
```

## 💡 Example Usage Patterns

### System Architecture Review
```
use codex high: Review our system architecture for race conditions and suggest optimizations for high throughput
```

### Security Audit
```
use codex high: Audit this code for security vulnerabilities and suggest improvements
```

### Debugging Complex Issues
```
use codex medium: Debug this concurrency issue and identify the root cause
```

### Performance Analysis
```
use codex: Profile this database query and suggest indexing strategies
```

### Code Review
```
use codex high: Review this implementation for best practices and potential issues
```

### Parallel Analysis Example
```
Run these Codex analyses in parallel:
1. use codex: Review authentication flow
2. use codex: Analyze database schema
3. use codex: Check API rate limiting
```

## 🏗️ Team Integration Workflows

### Code Review Process
1. Developer implements feature
2. Use Codex high for architectural review
3. Use Codex medium for implementation details
4. Compare with Claude's analysis for consensus
5. Document decisions in team knowledge base

### Architecture Decisions
1. Present problem to both Claude and Codex
2. Use high reasoning for complex trade-offs
3. Document reasoning chains for team review
4. Create ADRs (Architecture Decision Records)

### Performance Optimization
1. Profile with standard tools
2. Use Codex to analyze bottlenecks
3. Implement suggested optimizations
4. Verify improvements with benchmarks

### Security Audits
1. Use Codex high for comprehensive review
2. Cross-reference with OWASP guidelines
3. Implement fixes with test coverage
4. Document security considerations

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Homebrew Installation Failed
```bash
# For Apple Silicon Macs
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# For Intel Macs
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

#### Authentication Issues
```bash
# Clear authentication cache
codex auth logout
codex auth

# Verify ChatGPT subscription
echo "Ensure you have an active ChatGPT Plus or Team subscription"
echo "Visit https://chat.openai.com/subscription to verify"
```

#### MCP Connection Failed
```bash
# Remove and re-add MCP server
claude mcp remove codex
claude mcp add --name codex --command codex --args "-m,gpt-5-codex,mcp" --scope user --autoapprove "codex,codex-reply"

# Restart Claude Code
echo "Please restart Claude Code application"
```

#### Configuration Not Loading
```bash
# Verify config file location
ls -la ~/.codex/config.toml

# Reset configuration
rm -f ~/.codex/config.toml
# Re-run Step 3 of installation
```

#### Claude Desktop Not Recognizing Codex
```bash
# Ensure full path is used
CODEX_PATH=$(which codex)
echo "Update claude_desktop_config.json with full path: $CODEX_PATH"

# Manually verify JSON syntax
python3 -m json.tool "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

### Recovery Procedures

#### Complete Reinstallation
```bash
# 1. Remove Codex CLI
brew uninstall codex
brew untap openai/codex-cli

# 2. Remove MCP configuration
claude mcp remove codex

# 3. Clean configuration files
rm -rf ~/.codex
rm -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# 4. Restart from Step 1 of installation
```

#### Restore from Backup
```bash
# Restore CLAUDE.md
cp "$HOME/.claude/CLAUDE.md.backup" "$HOME/.claude/CLAUDE.md"

# Restore Claude Desktop config
cp "$HOME/Library/Application Support/Claude/claude_desktop_config.json.backup" \
   "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

## 📊 Success Metrics

### Installation Verification Checklist
- [ ] Codex CLI installed via Homebrew
- [ ] Authentication successful with ChatGPT account
- [ ] Configuration file created at ~/.codex/config.toml
- [ ] Claude Code `claude mcp list` shows `codex` server active
- [ ] Claude Desktop configuration updated with Codex server
- [ ] CLAUDE.md updated with Codex Integration Protocol
- [ ] Basic test prompts execute successfully
- [ ] Different reasoning levels (low/medium/high) respond appropriately
- [ ] Conversation continuity works with codex-reply
- [ ] Parallel execution capabilities confirmed

## 🔗 Additional Resources

### Official Documentation
- [Codex CLI Documentation](https://github.com/openai/codex-cli)
- [OpenAI Platform](https://platform.openai.com)
- [MCP Protocol Specification](https://modelcontextprotocol.org)

### Support Channels
- **Installation Issues**: Run this setup guide via Claude Code for autonomous resolution
- **Authentication Problems**: Verify ChatGPT subscription status
- **Configuration Questions**: Reference team's shared MCP configurations

## 🎉 Installation Complete!

**Congratulations!** You now have Codex MCP fully integrated with Claude Code and Claude Desktop.

**Installation Usage Summary**:
```
# To install Codex MCP on a new machine, in Claude Code conversation:
"Please read and execute the setup from claude-code/shared/mcp/codex-mcp-setup.md"

# After installation, use these commands:
```

**Quick Start Commands**:
```
# Basic usage
use codex: [your prompt]

# With reasoning levels
use codex high: [complex analysis]
use codex medium: [standard task]
use codex low: [simple query]

# Direct tool usage
mcp__codex__codex({"prompt": "...", "config": {"model_reasoning_effort": "high"}})
```

**Next Steps**:
1. Test Codex with a real development task
2. Document useful patterns in your knowledge base
3. Optimize workflows with parallel Codex sessions

---

*Enhancing Claude Code with OpenAI's most advanced coding model*

*Version: 1.0.0*
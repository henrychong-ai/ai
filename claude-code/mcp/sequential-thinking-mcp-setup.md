# Sequential Thinking MCP Server Installation Guide
*Complete Auto-Executable Installation Guide*

## 🎯 Mission
This document provides complete, auto-executable instructions for any developer to install the Sequential Thinking MCP server on their Claude Code and Claude Desktop instances. Claude Code can read this file and perform the entire installation process autonomously.

The Sequential Thinking MCP server enables structured problem-solving, systematic analysis, and collaborative reasoning workflows essential for complex development, architecture decisions, and technical planning.

## 📋 Prerequisites Verification

**CRITICAL**: Before installation, verify these requirements:

1. **Node.js & NPM**: Required for MCP server execution
2. **Claude Code**: Version 1.0+ with MCP support
3. **Claude Desktop**: Latest version (optional but recommended)
4. **File System Access**: Write permissions to Claude configuration directories

**AUTO-VERIFICATION COMMANDS**:
```bash
# Check Node.js version (should be 16+ for best compatibility)
node --version

# Check NPM availability
npm --version

# Verify Claude Code MCP functionality
claude mcp list

# Verify sequential thinking package availability
npx -y @modelcontextprotocol/server-sequential-thinking --version
```

## 🧠 Sequential Thinking Overview

**WHAT IS SEQUENTIAL THINKING MCP?**

The Sequential Thinking MCP server provides structured, step-by-step reasoning capabilities through the `mcp__st__sequentialthinking` tool. Unlike knowledge storage systems, this is a stateless analysis tool that enhances decision-making processes.

**KEY CAPABILITIES**:
- **Structured Analysis**: Break complex problems into clear, sequential steps
- **Thought Evolution**: Ability to revise, branch, and iterate on reasoning
- **Collaborative Planning**: Share systematic thought processes across team members
- **Decision Documentation**: Record and review analytical reasoning chains
- **Integration with CLAUDE.md**: Works seamlessly with existing "think s1/s2/s3" patterns

**NO STORAGE CONFIGURATION**: Unlike Knowledge Graph MCP, Sequential Thinking requires no persistent storage path - it's designed for real-time analytical processing.

## 🚀 Claude Code MCP Installation

**AUTO-EXECUTION SEQUENCE**:

### Step 1: Test MCP Server Availability
```bash
# Verify the sequential thinking server package is accessible
npx -y @modelcontextprotocol/server-sequential-thinking --help
```

### Step 2: Add MCP Server to Claude Code Configuration
```bash
claude mcp add \
  --name st \
  --command npx \
  --args "-y,@modelcontextprotocol/server-sequential-thinking" \
  --scope user \
  --autoapprove "sequentialthinking"
```

**Configuration Details**:
- **Server Name**: `st` (short for Sequential Thinking)
- **Command**: `npx` (uses Node Package Execute for latest version)
- **Args**: Includes `-y` flag for automatic confirmation, no additional configuration needed
- **Scope**: `user` (available across all projects)
- **Auto-approve**: `sequentialthinking` function for seamless usage

## 🖥️ Claude Desktop MCP Installation

**AUTO-EXECUTION SEQUENCE**:

### Step 1: Backup Existing Configuration
```bash
# Create backup of current Claude Desktop config
cp "~/Library/Application Support/Claude/claude_desktop_config.json" "~/Library/Application Support/Claude/claude_desktop_config.json.backup"
```

### Step 2: Update Claude Desktop Configuration
Claude Code must programmatically update the Claude Desktop config file:

```json
{
  "mcpServers": {
    "st": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    }
  }
}
```

**MERGE STRATEGY**: 
- If `claude_desktop_config.json` exists, merge the `st` server into existing `mcpServers` object
- If file doesn't exist, create with the complete structure above
- Preserve all existing MCP servers during merge

## ✅ Verification and Testing

**AUTOMATED VERIFICATION SEQUENCE**:

### Step 1: Verify Claude Code Installation
```bash
# List MCP servers to confirm st server is installed
claude mcp list

# Test st server connectivity
claude mcp test st
```

### Step 2: Test Basic Sequential Thinking Operations
Execute these test commands to verify functionality:

**Basic Thinking Process Test**:
```bash
# Test simple sequential thinking process
mcp__st__sequentialthinking '{
  "thought": "Testing sequential thinking installation with a simple problem analysis.",
  "nextThoughtNeeded": false,
  "thoughtNumber": 1,
  "totalThoughts": 1
}'
```

**Multi-Step Analysis Test**:
```bash
# Test multi-step thinking process
mcp__st__sequentialthinking '{
  "thought": "Step 1 of testing: Analyzing the problem - we need to verify that sequential thinking can handle multiple steps for complex analysis.",
  "nextThoughtNeeded": true,
  "thoughtNumber": 1,
  "totalThoughts": 3
}'
```

**Advanced Features Test**:
```bash
# Test thought revision capabilities
mcp__st__sequentialthinking '{
  "thought": "Actually, let me revise my previous analysis - the installation test should focus on practical business scenarios rather than abstract testing.",
  "nextThoughtNeeded": false,
  "thoughtNumber": 2,
  "totalThoughts": 2,
  "isRevision": true,
  "revisesThought": 1
}'
```

### Step 3: Verify Integration with CLAUDE.md Patterns
Test integration with existing thinking patterns:
```bash
# Verify that "think s1", "think s2", "think s3" patterns work with MCP
echo "Testing: Can now use 'think s2' to trigger 6-10 step detailed analysis using mcp__st__sequentialthinking"
```

## 🎯 User Preference Configuration (Optional)

**OPTIONAL ENHANCEMENT**: Configure Claude Code and Claude Desktop user preferences for optimal sequential thinking experience.

**PROMPT**: Would you like to update your Claude Code and Claude Desktop user preference files to include the 's1/s2/s3' triggerwords for easy sequential thinking activation?

**BENEFITS OF CONFIGURATION**:
- Enable simple triggerword usage: "think s1", "think s2", "think s3"
- Auto-invoke sequential thinking based on keyword detection
- Seamless integration with existing workflow patterns
- Consistent experience across Claude platforms

### Claude Code User Preferences Configuration

**AUTO-EXECUTION SEQUENCE**:

#### Step 1: Backup Existing Preferences
```bash
# Create backup of current Claude Code user preferences
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup
```

#### Step 2: Add Sequential Thinking Triggerwords to CLAUDE.md

Add this section to your `~/.claude/CLAUDE.md` file (or update existing section):

```markdown
## 🧠 Sequential Thinking Triggers
- **s1**: Basic analysis (3-5 steps, ~400-800 tokens)
- **s2**: Detailed analysis (6-10 steps, ~1000-1800 tokens)
- **s3**: Comprehensive analysis (12-20 steps, ~2200-4000 tokens)
- **s_clear**: Reset thinking history
- Auto-invoke on keyword detection
- Format: "message\n\nthink s1"
```

**AUTOMATED UPDATE COMMAND**:
```bash
# Claude Code can programmatically update CLAUDE.md with the configuration
# Check if Sequential Thinking Triggers section exists, if not, add it
```

### Claude Desktop User Preferences Configuration

**AUTO-EXECUTION SEQUENCE**:

#### Step 1: Locate Claude Desktop Preferences
Claude Desktop user preferences are typically managed through the app interface:
- Open Claude Desktop application  
- Navigate to Settings/Preferences
- Look for "Custom Instructions" or "User Preferences" section

#### Step 2: Add Sequential Thinking Configuration
Add this text to your Claude Desktop custom instructions:

```
Sequential Thinking Triggers:
- s1: Basic analysis (3-5 steps, ~400-800 tokens)
- s2: Detailed analysis (6-10 steps, ~1000-1800 tokens)  
- s3: Comprehensive analysis (12-20 steps, ~2200-4000 tokens)
- s_clear: Reset thinking history
- Auto-invoke on keyword detection
- Format: "message\n\nthink s1"
```

**NOTE**: Claude Desktop preferences are managed through the GUI interface. For consistency, ensure this configuration matches your Claude Code CLAUDE.md setup.

### Verification of Triggerword Configuration

**TEST SEQUENCE**:

#### Step 1: Test Basic Triggerword Functionality
```bash
# Test s1 triggerword (should invoke sequential thinking with 3-5 steps)
echo "Test problem: Analyze the benefits of microservices architecture" | echo "think s1"

# Test s2 triggerword (should invoke sequential thinking with 6-10 steps)  
echo "Test problem: Design a scalable authentication system" | echo "think s2"

# Test s3 triggerword (should invoke comprehensive 12-20 step analysis)
echo "Test problem: Plan the migration of our monolithic application" | echo "think s3"
```

#### Step 2: Verify Auto-Invoke Functionality
```bash
# Test keyword detection (should automatically trigger sequential thinking)
echo "We need to systematically analyze this complex database performance issue"
# Should auto-detect need for structured thinking and suggest appropriate level
```

#### Step 3: Test Thinking History Management
```bash
# Test s_clear functionality
echo "s_clear"
# Should reset any ongoing sequential thinking context
```

### Integration Verification

**VALIDATE CONFIGURATION SUCCESS**:

1. **Triggerword Recognition**: 
   - "think s1" should invoke basic sequential thinking (3-5 steps)
   - "think s2" should invoke detailed analysis (6-10 steps)  
   - "think s3" should invoke comprehensive analysis (12-20 steps)

2. **Auto-Detection**:
   - Keywords like "analyze", "systematically", "complex problem" should suggest sequential thinking
   - Context-appropriate level suggestions (s1 for simple, s3 for complex)

3. **Cross-Platform Consistency**:
   - Both Claude Code and Claude Desktop should respond to triggerwords identically
   - Sequential thinking depth and approach should be consistent across platforms

4. **MCP Integration**:
   - Triggerwords should properly invoke `mcp__st__sequentialthinking` tool
   - All sequential thinking features (revision, branching) should work with triggerwords

## 🧮 Team Usage Patterns

**TEAM INTEGRATION**:

### Architecture Decision Making
Use sequential thinking for systematic technical decisions:

**Example Workflow**:
```
Message: "We need to decide on the authentication architecture for our new microservice. think s3"

Result: 12-20 step comprehensive analysis covering:
- Security requirements evaluation
- Technology stack compatibility  
- Scalability considerations
- Implementation complexity
- Integration with existing systems
- Cost-benefit analysis
- Risk assessment
- Recommendation with rationale
```

### Code Review Enhancement
Apply structured analysis to complex code changes:

**Example Process**:
1. **Initial Assessment** (s1): Basic analysis of change scope and impact
2. **Deep Dive** (s2): Detailed security, performance, and maintainability review
3. **Comprehensive Review** (s3): Full architectural impact, testing strategy, deployment considerations

### Project Planning and Retrospectives
Break down complex initiatives systematically:

**Planning Example**:
```
"Plan the implementation of our new compliance monitoring system. think s3"

Enables: Systematic breakdown of requirements, dependencies, timeline, resources, risks
```

**Retrospective Example**:
```
"Analyze what went well and what could improve in our last sprint. think s2"

Enables: Structured evaluation of processes, outcomes, team dynamics, improvement opportunities
```

### Technical Problem Solving
Apply systematic debugging and troubleshooting:

**Troubleshooting Workflow**:
1. **Symptom Analysis** (s1): Quick problem identification
2. **Root Cause Investigation** (s2): Detailed investigation with hypothesis testing  
3. **Solution Design** (s3): Comprehensive solution with alternatives and implementation plan

### Integration with Existing Tools

**Knowledge Graph Synergy**:
- Use sequential thinking to analyze complex problems
- Capture insights and decisions in KG using `/kg` command
- Build institutional memory of decision-making processes

**Documentation Enhancement**:
- Structure technical documentation using systematic analysis
- Ensure comprehensive coverage through step-by-step thinking
- Create reproducible decision frameworks

## 🛠️ Troubleshooting Guide

### Common Issues and Solutions

**Issue 1: NPX Command Not Found**
```bash
# Solution: Install Node.js and NPM
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Issue 2: Package Not Found Error**
```bash
# Solution: Clear npm cache and retry
npm cache clean --force
npx -y @modelcontextprotocol/server-sequential-thinking --version
```

**Issue 3: MCP Server Connection Timeout**
```bash
# Solution: Verify network connectivity and increase timeout
export MCP_TIMEOUT=30000
claude mcp test st
```

**Issue 4: Tool Not Appearing in Claude Interface**
```bash
# Solution: Restart Claude and verify configuration
# Check server status
claude mcp list

# Verify server is running
claude mcp test st

# Check tool permissions
claude mcp status st
```

**Issue 5: Sequential Thinking Tool Returns Errors**
```bash
# Solution: Verify JSON parameter format
# Ensure all required fields are present:
# - thought (string)
# - nextThoughtNeeded (boolean)  
# - thoughtNumber (integer)
# - totalThoughts (integer)

# Test with minimal valid parameters:
mcp__st__sequentialthinking '{
  "thought": "Simple test",
  "nextThoughtNeeded": false,
  "thoughtNumber": 1,
  "totalThoughts": 1
}'
```

### Error Recovery Procedures

**Complete Reinstallation**:
```bash
# Remove existing st server
claude mcp remove st

# Clear any cached packages
npm cache clean --force

# Restart installation process
# [Execute installation steps again]
```

**Configuration Reset**:
```bash
# Reset Claude Code MCP configuration (if needed)
# Backup first!
cp ~/.claude.json ~/.claude.json.backup

# Reset Claude Desktop configuration (if needed)
# Backup first!
cp "~/Library/Application Support/Claude/claude_desktop_config.json" \
   "~/Library/Application Support/Claude/claude_desktop_config.json.backup"

# Restore from backups if needed
```

**Network-Related Issues**:
```bash
# Test network connectivity to npm registry
curl -I https://registry.npmjs.org/

# Test with different npm registry if needed
npm config set registry https://registry.npmmirror.com/
npx -y @modelcontextprotocol/server-sequential-thinking --version
npm config set registry https://registry.npmjs.org/  # Reset to default
```

## 📈 Advanced Usage Patterns

### Thought Process Documentation
Sequential thinking processes can be saved and shared:

**Best Practices**:
1. **Start with Clear Problem Statement**: Define what you're analyzing
2. **Use Appropriate Depth**: s1 for quick analysis, s2 for detailed, s3 for comprehensive
3. **Allow for Revision**: Use revision capabilities when new information emerges
4. **Branch When Needed**: Explore alternative approaches through branching
5. **Document Outcomes**: Capture key insights in Knowledge Graph or project documentation

### Team Collaboration Patterns

**Design Reviews**:
```
Team Member A: Initiates sequential thinking analysis of proposed architecture
Team Member B: Reviews the thought chain and adds revisions/branches
Team Member C: Builds on analysis with implementation considerations
Result: Documented, collaborative decision-making process
```

**Problem Solving Sessions**:
1. **Problem Definition** (s1): Quick shared understanding
2. **Investigation** (s2): Detailed collaborative analysis  
3. **Solution Design** (s3): Comprehensive implementation planning

### Integration with Development Workflow

**Pre-Commit Analysis**:
- Analyze complex changes before committing
- Document decision rationale in commit messages
- Identify potential impacts and dependencies

**Sprint Planning Enhancement**:
- Break down user stories systematically
- Identify dependencies and risks early
- Create detailed implementation approaches

**Technical Debt Assessment**:
- Analyze technical debt systematically
- Prioritize remediation efforts
- Document architectural improvements

## 🔄 Maintenance and Updates

### Regular Maintenance Tasks

**Weekly**: Verify server functionality
```bash
# Test basic sequential thinking functionality
claude mcp test st

# Verify latest package version
npx -y @modelcontextprotocol/server-sequential-thinking --version
```

**Monthly**: Update MCP server package
```bash
# Update to latest sequential thinking server version
# (npx automatically uses latest with -y flag, but can force update cache)
npm cache clean --force
npx -y @modelcontextprotocol/server-sequential-thinking --version
```

**Quarterly**: Review usage patterns and optimization
- Analyze how team is using sequential thinking
- Identify opportunities for workflow improvements
- Update team best practices and patterns
- Review integration with other tools (KG, documentation systems)

## 🎯 Success Criteria

**INSTALLATION COMPLETE WHEN**:
1. ✅ Claude Code `claude mcp list` shows `st` server as active
2. ✅ Claude Desktop can access Sequential Thinking tools via MCP menu
3. ✅ Basic sequential thinking operations (single thought) function correctly
4. ✅ Multi-step thinking processes work with thought progression
5. ✅ Advanced features (revision, branching) operate as expected
6. ✅ Integration with CLAUDE.md "think s1/s2/s3" patterns works seamlessly
7. ✅ Both Claude Code and Claude Desktop can use Sequential Thinking tools simultaneously
8. ✅ (Optional) User preference files configured with s1/s2/s3 triggerwords
9. ✅ (Optional) Triggerword functionality verified across both platforms

**VERIFICATION CHECKLIST**:
- [ ] Node.js and NPM installed and functional
- [ ] Sequential Thinking MCP package accessible via npx
- [ ] Claude Code MCP server installed with correct configuration
- [ ] Claude Desktop MCP server installed with correct configuration
- [ ] Basic thinking process test successful
- [ ] Multi-step analysis test successful  
- [ ] Advanced features (revision/branching) test successful
- [ ] Integration with existing CLAUDE.md patterns confirmed
- [ ] Team usage patterns documented and understood
- [ ] (Optional) Claude Code CLAUDE.md updated with s1/s2/s3 triggerwords
- [ ] (Optional) Claude Desktop preferences updated with sequential thinking configuration
- [ ] (Optional) Triggerword functionality verified ("think s1", "think s2", "think s3" working)
- [ ] (Optional) Auto-invoke keyword detection confirmed
- [ ] (Optional) Cross-platform triggerword consistency verified

## 📚 Additional Resources

**Documentation Links**:
- [MCP Sequential Thinking Source](https://github.com/modelcontextprotocol/server-sequential-thinking) - Official server repository
- [Sequential Thinking NPM Package](https://www.npmjs.com/package/@modelcontextprotocol/server-sequential-thinking)
- [Claude Code MCP Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
- Your CLAUDE.md Thinking Patterns - Integration with existing s1/s2/s3 patterns

**Team Support**:
- For installation issues: Contact Claude Code setup support team
- For usage patterns: Reference your team's best practices
- For advanced workflows: Collaborate with team on sequential thinking integration patterns

**Related Tools**:
- [Knowledge Graph MCP Setup](./knowledge-graph-mcp-setup.md) - Complementary knowledge capture system
- Shared Commands - Additional workflow automation tools

## 🔧 Development Team Benefits

**FOR ARCHITECTS**:
- Systematic architecture decision documentation
- Complex system analysis with clear reasoning chains
- Collaborative design review processes
- Technology evaluation frameworks

**FOR DEVELOPERS**:
- Structured problem-solving for complex bugs
- Code review enhancement with systematic analysis
- Planning complex feature implementations
- Technical debt assessment and prioritization

**FOR TEAM LEADS**:
- Project planning with comprehensive analysis
- Risk assessment and mitigation planning
- Team decision documentation and knowledge sharing
- Process improvement through structured retrospectives

**FOR THE ORGANIZATION**:
- Institutional knowledge capture of decision-making processes
- Consistent analytical frameworks across teams
- Improved decision quality through structured thinking
- Enhanced collaboration through shared reasoning processes

---

**INSTALLATION EXECUTION PROTOCOL FOR CLAUDE CODE**:

When a developer requests "read sequential-thinking-mcp-setup.md and install the sequential thinking MCP server", Claude Code should:

1. **Read this file completely**
2. **Execute prerequisites verification**  
3. **Install MCP server for Claude Code**
4. **Install MCP server for Claude Desktop**
5. **Run verification tests** (basic, multi-step, and advanced features)
6. **Test integration with CLAUDE.md thinking patterns**
7. **Prompt for optional user preference configuration** (s1/s2/s3 triggerwords)
8. **Execute preference updates if requested** (Claude Code and Desktop)
9. **Verify triggerword functionality if configured**
10. **Confirm successful installation**
11. **Provide usage guidance specific to team workflows**
12. **Document integration with existing tools (Knowledge Graph, etc.)**

This document serves as both documentation and executable specification for autonomous installation by Claude Code instances across development teams.

**KEY COMPONENTS OF EFFECTIVE SETUP INSTRUCTIONS**:

1. **Auto-Executable Design**: Every command and configuration step can be performed programmatically by Claude Code
2. **Complete Coverage**: Both Claude Code and Claude Desktop installation with all necessary steps
3. **Comprehensive Verification**: Multiple test layers to ensure functionality at basic, intermediate, and advanced levels  
4. **Team Integration**: Clear patterns for how this tool enhances existing workflows
5. **Troubleshooting**: Anticipation of common issues with specific diagnostic and resolution steps
6. **Maintenance Guidance**: Ongoing care and optimization recommendations
7. **Success Criteria**: Unambiguous verification that installation is complete and functional
8. **Context Integration**: Clear connection to existing team tools and processes (CLAUDE.md, Knowledge Graph, etc.)
9. **Business Value**: Explanation of how this tool advances team capabilities and project outcomes
10. **Collaborative Framework**: Patterns for team usage that enhance collective intelligence and decision-making

These components ensure that the setup instructions serve both as documentation and as executable specifications for autonomous installation, while providing comprehensive guidance for successful team adoption and integration.
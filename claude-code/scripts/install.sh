#!/bin/bash
# Claude Code Extensions Installer
# Installs agents, skills, and commands to ~/.claude/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/backups/extensions-$(date +%Y%m%d_%H%M%S)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "================================================"
echo "  Claude Code Extensions Installer"
echo "================================================"
echo ""

# Parse arguments
INSTALL_AGENTS=true
INSTALL_SKILLS=true
INSTALL_COMMANDS=true
SKIP_BACKUP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --agents-only)
            INSTALL_SKILLS=false
            INSTALL_COMMANDS=false
            shift
            ;;
        --skills-only)
            INSTALL_AGENTS=false
            INSTALL_COMMANDS=false
            shift
            ;;
        --commands-only)
            INSTALL_AGENTS=false
            INSTALL_SKILLS=false
            shift
            ;;
        --no-backup)
            SKIP_BACKUP=true
            shift
            ;;
        -h|--help)
            echo "Usage: install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --agents-only    Install only agents"
            echo "  --skills-only    Install only skills"
            echo "  --commands-only  Install only commands"
            echo "  --no-backup      Skip backing up existing files"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Create directories
echo "Creating directories..."
mkdir -p "$CLAUDE_DIR/agents"
mkdir -p "$CLAUDE_DIR/skills"
mkdir -p "$CLAUDE_DIR/commands"

# Backup function
backup_if_exists() {
    local src="$1"
    local name=$(basename "$src")
    local type="$2"

    if [ "$SKIP_BACKUP" = true ]; then
        return
    fi

    local target="$CLAUDE_DIR/$type/$name"
    if [ -e "$target" ]; then
        mkdir -p "$BACKUP_DIR/$type"
        cp -r "$target" "$BACKUP_DIR/$type/"
        echo -e "  ${YELLOW}Backed up${NC} $name"
    fi
}

# Count installations
AGENTS_INSTALLED=0
SKILLS_INSTALLED=0
COMMANDS_INSTALLED=0

# Install agents
if [ "$INSTALL_AGENTS" = true ] && [ -d "$PLUGIN_DIR/agents" ]; then
    echo ""
    echo -e "${BLUE}Installing agents...${NC}"
    for agent in "$PLUGIN_DIR/agents"/*.md; do
        if [ -f "$agent" ]; then
            name=$(basename "$agent")
            backup_if_exists "$agent" "agents"
            cp "$agent" "$CLAUDE_DIR/agents/"
            echo -e "  ${GREEN}✓${NC} $name"
            ((AGENTS_INSTALLED++))
        fi
    done
fi

# Install skills
if [ "$INSTALL_SKILLS" = true ] && [ -d "$PLUGIN_DIR/skills" ]; then
    echo ""
    echo -e "${BLUE}Installing skills...${NC}"
    for skill_dir in "$PLUGIN_DIR/skills"/*/; do
        if [ -d "$skill_dir" ]; then
            name=$(basename "$skill_dir")
            backup_if_exists "$skill_dir" "skills"
            cp -r "$skill_dir" "$CLAUDE_DIR/skills/"
            echo -e "  ${GREEN}✓${NC} $name/"
            ((SKILLS_INSTALLED++))
        fi
    done
fi

# Install commands
if [ "$INSTALL_COMMANDS" = true ] && [ -d "$PLUGIN_DIR/commands" ]; then
    echo ""
    echo -e "${BLUE}Installing commands...${NC}"
    for cmd in "$PLUGIN_DIR/commands"/*.md; do
        if [ -f "$cmd" ]; then
            name=$(basename "$cmd")
            backup_if_exists "$cmd" "commands"
            cp "$cmd" "$CLAUDE_DIR/commands/"
            echo -e "  ${GREEN}✓${NC} $name"
            ((COMMANDS_INSTALLED++))
        fi
    done
fi

# Summary
echo ""
echo "================================================"
echo -e "${GREEN}Installation complete!${NC}"
echo "================================================"
echo ""
echo "Installed:"
[ "$INSTALL_AGENTS" = true ] && echo "  - $AGENTS_INSTALLED agents"
[ "$INSTALL_SKILLS" = true ] && echo "  - $SKILLS_INSTALLED skills"
[ "$INSTALL_COMMANDS" = true ] && echo "  - $COMMANDS_INSTALLED commands"

if [ "$SKIP_BACKUP" = false ] && [ -d "$BACKUP_DIR" ]; then
    echo ""
    echo "Backups saved to:"
    echo "  $BACKUP_DIR"
fi

echo ""
echo "MCP setup guides available at:"
echo "  $PLUGIN_DIR/mcp/"
echo ""
echo "To install the statusline plugin separately:"
echo "  $PLUGIN_DIR/plugins/statusline/scripts/install.sh"
echo ""

#!/bin/bash
# Statusline Installer
# Installs the statusline configuration into Claude Code settings

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PLUGIN_DIR/configs/statusline.json"
SETTINGS_FILE="$HOME/.claude/settings.json"
BACKUP_DIR="$HOME/.claude/backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "  Statusline Installer"
echo "================================================"
echo ""

# Check dependencies
echo "Checking dependencies..."

check_dep() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}ERROR: $1 is not installed${NC}"
        echo "  Install with: $2"
        return 1
    else
        echo -e "  ${GREEN}✓${NC} $1"
        return 0
    fi
}

DEPS_OK=true
check_dep "jq" "brew install jq" || DEPS_OK=false
check_dep "ccusage" "npm install -g ccusage" || DEPS_OK=false
check_dep "curl" "(should be pre-installed on macOS)" || DEPS_OK=false

if [ "$DEPS_OK" = false ]; then
    echo ""
    echo -e "${RED}Please install missing dependencies and try again.${NC}"
    exit 1
fi

echo ""

# Check for macOS (required for security command)
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${YELLOW}WARNING: This statusline is designed for macOS.${NC}"
    echo "  Some features (OAuth usage metrics) may not work on other platforms."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}ERROR: Config file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Create backup directory if needed
mkdir -p "$BACKUP_DIR"

# Backup existing settings
if [ -f "$SETTINGS_FILE" ]; then
    BACKUP_FILE="$BACKUP_DIR/settings.json.$(date +%Y%m%d_%H%M%S).backup"
    echo "Backing up existing settings to:"
    echo "  $BACKUP_FILE"
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
    echo ""
fi

# Create settings.json if it doesn't exist
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "Creating new settings.json..."
    echo '{}' > "$SETTINGS_FILE"
fi

# Validate existing settings.json
if ! jq empty "$SETTINGS_FILE" 2>/dev/null; then
    echo -e "${RED}ERROR: Existing settings.json is not valid JSON${NC}"
    echo "Please fix or remove ~/.claude/settings.json and try again."
    exit 1
fi

# Merge statusline config into settings
echo "Installing statusline configuration..."
TEMP_FILE=$(mktemp)

if jq -s '.[0] * .[1]' "$SETTINGS_FILE" "$CONFIG_FILE" > "$TEMP_FILE"; then
    # Validate merged result
    if jq empty "$TEMP_FILE" 2>/dev/null; then
        mv "$TEMP_FILE" "$SETTINGS_FILE"
        echo -e "${GREEN}✓ Statusline configuration installed successfully!${NC}"
    else
        rm -f "$TEMP_FILE"
        echo -e "${RED}ERROR: Merged config is invalid JSON${NC}"
        exit 1
    fi
else
    rm -f "$TEMP_FILE"
    echo -e "${RED}ERROR: Failed to merge configurations${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo -e "${GREEN}Installation complete!${NC}"
echo "================================================"
echo ""
echo "The statusline will display:"
echo "  - Current directory and git branch"
echo "  - Model name"
echo "  - Daily and block costs (via ccusage)"
echo "  - Time remaining in 5-hour block"
echo "  - Context window usage"
echo "  - Rate limit utilization (5h, 7d, sonnet)"
echo ""
echo "Restart Claude Code to see the new statusline."
echo ""

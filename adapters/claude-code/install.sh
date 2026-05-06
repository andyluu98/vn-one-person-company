#!/usr/bin/env bash
# Install Claude Code skill (assumes vn-business-os Python package + MCP server already installed)
set -euo pipefail

CLAUDE_AGENTS_DIR="${CLAUDE_AGENTS_DIR:-$HOME/.claude/skills}"
mkdir -p "$CLAUDE_AGENTS_DIR/vn-business-os"

cp "$(dirname "$0")/skill.md" "$CLAUDE_AGENTS_DIR/vn-business-os/SKILL.md"

echo "Installed Claude Code skill to $CLAUDE_AGENTS_DIR/vn-business-os/"
echo ""
echo "Prerequisites for skill to work:"
echo "  1. pip install vn-business-os"
echo "  2. vn-os install-mcp        # registers MCP server in Claude Desktop config"
echo "  3. Restart Claude Desktop"
echo ""
echo "Then in Claude session, type Vietnamese business request — skill auto-activates."

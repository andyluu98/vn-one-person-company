#!/usr/bin/env bash
# Install Claude Code skill + register MCP server in Claude Code global config.
set -euo pipefail

CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$CLAUDE_SKILLS_DIR/vn-business-os"

cp "$(dirname "$0")/skill.md" "$CLAUDE_SKILLS_DIR/vn-business-os/SKILL.md"
echo "✓ Skill installed to $CLAUDE_SKILLS_DIR/vn-business-os/"

# Register MCP server in Claude Code global config (~/.claude.json)
if command -v vn-os &>/dev/null; then
    vn-os install-mcp --target claude-code
    echo "✓ MCP server registered in ~/.claude.json"
else
    echo "⚠ vn-os not found. Run after installing package:"
    echo "    pip install -e ."
    echo "    vn-os install-mcp --target claude-code"
fi

echo ""
echo "Bước tiếp: restart Claude Code để load MCP server."
echo "Rồi gõ brief tiếng Việt trong Claude Code — skill tự kích hoạt."

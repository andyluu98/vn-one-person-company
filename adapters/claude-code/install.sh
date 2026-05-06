#!/usr/bin/env bash
set -euo pipefail

CLAUDE_AGENTS_DIR="${CLAUDE_AGENTS_DIR:-$HOME/.claude/skills}"
mkdir -p "$CLAUDE_AGENTS_DIR/vn-business-os"

cp "$(dirname "$0")/skill.md" "$CLAUDE_AGENTS_DIR/vn-business-os/SKILL.md"
echo "Installed Claude Code skill to $CLAUDE_AGENTS_DIR/vn-business-os/"

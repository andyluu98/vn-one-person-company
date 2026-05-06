#!/usr/bin/env bash
set -euo pipefail

DIR="$(dirname "$0")"
OUT="${1:-vn-business-os.plugin}"
TMP=$(mktemp -d)

mkdir -p "$TMP/.claude-plugin" "$TMP/skills/vn-business-os"
cp "$DIR/.claude-plugin/plugin.json" "$TMP/.claude-plugin/"
cp "$DIR/skills/vn-business-os/SKILL.md" "$TMP/skills/vn-business-os/"
cp "$DIR/README.md" "$TMP/" 2>/dev/null || true

(cd "$TMP" && zip -qr "$OUT" .)
mv "$TMP/$OUT" "./$OUT"
rm -rf "$TMP"

echo "Built $OUT"

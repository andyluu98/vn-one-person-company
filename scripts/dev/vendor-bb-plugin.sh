#!/usr/bin/env bash
# Extract bb-plugin và copy 191 template vào templates-vn/
set -euo pipefail

PLUGIN_PATH="${1:-references/business-builder.plugin}"
TARGET="templates-vn"

if [ ! -f "$PLUGIN_PATH" ]; then
  echo "❌ Không tìm thấy $PLUGIN_PATH"
  exit 1
fi

TMP=$(mktemp -d)
unzip -q "$PLUGIN_PATH" -d "$TMP"

mkdir -p "$TARGET"

# Map bb-* skills → templates-vn dept codes
declare -A MAP=(
  [bb-orchestrator]="_orchestrator"
  [bb-governance]="01-governance"
  [bb-strategy]="02-strategy"
  [bb-finance]="03-finance"
  [bb-people]="04-people"
  [bb-operations]="05-operations"
  [bb-sales]="06-sales"
  [bb-marketing]="07-marketing"
  [bb-customer]="08-customer"
  [bb-product-tech]="09-product-tech"
  [bb-training]="10-training"
  [bb-reporting]="11-reporting"
  [bb-growth]="12-growth"
)

for src in "${!MAP[@]}"; do
  dst="${MAP[$src]}"
  mkdir -p "$TARGET/$dst"
  if [ -d "$TMP/skills/$src/references" ]; then
    cp -r "$TMP/skills/$src/references/"* "$TARGET/$dst/"
    echo "✓ $src → $dst ($(ls "$TARGET/$dst" | wc -l) files)"
  fi
done

rm -rf "$TMP"
echo "✅ Vendored to $TARGET/"

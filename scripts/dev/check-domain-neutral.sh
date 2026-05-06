#!/usr/bin/env bash
# Verify RULE 2: no trade/finance leakage trong core/
# Banned terms must NOT appear in code (identifiers, strings, etc).
# Allowed: comments documenting the rule itself, or "Adapted from TradingAgents..." attribution.

set -euo pipefail

# Banned identifiers — these MUST NOT appear in core/ except in attribution comments
FORBIDDEN_PATTERNS=(
  "Bull"
  "Bear"
  "trader"
  "ticker"
  "yfinance"
  "Alpha Vantage"
  "stock"
)

FAILED=0
for pat in "${FORBIDDEN_PATTERNS[@]}"; do
  echo "Checking: $pat"
  # Use grep with word-boundary matching (case-insensitive)
  matches=$(grep -ri --include="*.py" -E "\b$pat\b" core/ 2>/dev/null || true)
  if [ -n "$matches" ]; then
    # Filter out attribution comments
    real_matches=$(echo "$matches" | grep -v -E "(# Adapted from|# was:|# RULE 2|KHONG|KHÔNG)" || true)
    if [ -n "$real_matches" ]; then
      echo "❌ Found '$pat' in core/ (non-attribution lines):"
      echo "$real_matches"
      FAILED=1
    else
      echo "  (ok — only in attribution/rule comments)"
    fi
  fi
done

if [ "$FAILED" -eq 1 ]; then
  echo ""
  echo "❌ Domain-neutral check FAILED"
  exit 1
fi
echo ""
echo "✅ Domain-neutral check passed"

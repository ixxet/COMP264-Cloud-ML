#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./assignment1_ex2_commands.sh "your test sentence here"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 \"text for comprehend\""
  exit 1
fi

TEXT="$1"
OUT_DIR="$(cd "$(dirname "$0")" && pwd)"

aws iam get-user > "$OUT_DIR/izzet_iam_get_user.json"

aws comprehend detect-entities \
  --text "$TEXT" \
  --language-code en \
  > "$OUT_DIR/izzet_comprehend_output.json"

aws comprehendmedical detect-phi \
  --text "$TEXT" \
  > "$OUT_DIR/izzet_comprehend_medical_output.json"

echo "Generated:"
echo "  $OUT_DIR/izzet_iam_get_user.json"
echo "  $OUT_DIR/izzet_comprehend_output.json"
echo "  $OUT_DIR/izzet_comprehend_medical_output.json"

#!/usr/bin/env bash
# Copy the dataset into docs/ so it is fetchable over HTTP from GitHub Pages.
# GitHub Pages does not follow symlinks, so these must be real copies.
# Run this after editing anything in dataset/.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for f in translation_watermark.json corrections.jsonl knowledge_qa.jsonl; do
  cp "$root/dataset/$f" "$root/docs/$f"
  echo "synced dataset/$f -> docs/$f"
done

# Fail loudly if the JSON is malformed — a broken file is worse than no file.
if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$root/docs/translation_watermark.json"
  python3 -c '
import json, sys
for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    raise SystemExit(f"{path}:{n}: {e}")
' "$root/docs/corrections.jsonl" "$root/docs/knowledge_qa.jsonl"
  echo "json ok"
fi

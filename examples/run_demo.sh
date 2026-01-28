#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -U pip
pip install -e .

# Copy example docs into ./docs if empty
mkdir -p docs
if [ -z "$(ls -A docs 2>/dev/null || true)" ]; then
  echo "Copying examples/docs -> docs"
  cp -n examples/docs/*.docx docs/ 2>/dev/null || true
fi

docxbrief init || true
docxbrief scan
docxbrief build

echo "Generated: summary.adoc"

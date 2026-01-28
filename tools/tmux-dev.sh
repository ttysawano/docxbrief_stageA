#!/usr/bin/env bash
set -euo pipefail

SESSION="docxbriefA"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

# Create session if not exists
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux new-session -d -s "$SESSION" -n main
fi

# Layout: 2x2 panes
tmux select-window -t "$SESSION:main"
tmux kill-pane -a -t "$SESSION:main" 2>/dev/null || true

tmux split-window -h -t "$SESSION:main"
tmux split-window -v -t "$SESSION:main.0"
tmux split-window -v -t "$SESSION:main.1"

# Pane commands
tmux send-keys -t "$SESSION:main.0" "source .venv/bin/activate 2>/dev/null || true; docxbrief shell" C-m
tmux send-keys -t "$SESSION:main.1" "mkdir -p .docxbrief; touch .docxbrief/log.txt; tail -f .docxbrief/log.txt" C-m
tmux send-keys -t "$SESSION:main.2" "watch -n 1 'ls -lh summary.adoc 2>/dev/null || true; echo; tail -n 40 summary.adoc 2>/dev/null || true'" C-m
tmux send-keys -t "$SESSION:main.3" "watch -n 2 'test -f .docxbrief/manifest.json && python -m json.tool .docxbrief/manifest.json | tail -n 80 || echo "(manifest not found yet)"'" C-m

tmux select-pane -t "$SESSION:main.0"
tmux attach -t "$SESSION"

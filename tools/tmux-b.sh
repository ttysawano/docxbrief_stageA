#!/usr/bin/env bash
set -euo pipefail

SESSION="docxbriefB"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux new-session -d -s "$SESSION" -n main
fi

tmux select-window -t "$SESSION:main"
tmux kill-pane -a -t "$SESSION:main" 2>/dev/null || true

tmux split-window -h -t "$SESSION:main"
tmux split-window -v -t "$SESSION:main.0"
tmux split-window -v -t "$SESSION:main.1"

start_codex='command -v codex >/dev/null 2>&1 && codex || { echo "codex not found; staying in shell"; exec "${SHELL:-/bin/bash}"; }'

tmux send-keys -t "$SESSION:main.0" "cd \"$ROOT_DIR\"; $start_codex" C-m
tmux send-keys -t "$SESSION:main.1" "cd \"$ROOT_DIR\"; $start_codex" C-m
tmux send-keys -t "$SESSION:main.2" "cd \"$ROOT_DIR\"; $start_codex" C-m
tmux send-keys -t "$SESSION:main.3" "cd \"$ROOT_DIR\"; $start_codex" C-m

tmux send-keys -t "$SESSION:main.0" "You are SHOGUN.\nRead task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml\nFollow constraints.\nWrite result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml\nIf you propose code changes, produce a patch file and reference it in result.\nDo NOT apply changes to repo unless write_policy=allow_edit." C-m
tmux send-keys -t "$SESSION:main.1" "You are KARO.\nRead task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml\nFollow constraints.\nWrite result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml\nIf you propose code changes, produce a patch file and reference it in result.\nDo NOT apply changes to repo unless write_policy=allow_edit." C-m
tmux send-keys -t "$SESSION:main.2" "You are ASHIGARU1.\nRead task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml\nFollow constraints.\nWrite result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml\nIf you propose code changes, produce a patch file and reference it in result.\nDo NOT apply changes to repo unless write_policy=allow_edit." C-m
tmux send-keys -t "$SESSION:main.3" "You are ASHIGARU2.\nRead task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml\nFollow constraints.\nWrite result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml\nIf you propose code changes, produce a patch file and reference it in result.\nDo NOT apply changes to repo unless write_policy=allow_edit." C-m

tmux select-pane -t "$SESSION:main.0"
tmux attach -t "$SESSION"

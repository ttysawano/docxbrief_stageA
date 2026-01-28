#!/usr/bin/env bash
set -euo pipefail

SESSION="docxbrief-b"
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

tmux select-pane -t "$SESSION:main.0"
tmux select-pane -T "shogun"
tmux select-pane -t "$SESSION:main.1"
tmux select-pane -T "karo"
tmux select-pane -t "$SESSION:main.2"
tmux select-pane -T "ashigaru1"
tmux select-pane -t "$SESSION:main.3"
tmux select-pane -T "ashigaru2"

start_codex='command -v codex >/dev/null 2>&1 && codex || { echo "codex not found; staying in shell"; exec "${SHELL:-/bin/bash}"; }'

send_and_enter() {
  # Send one line literally, then press Enter (separate tmux calls).
  local target="$1"
  local line="$2"
  tmux send-keys -t "$target" -l "$line"
  sleep 0.15
  tmux send-keys -t "$target" Enter
  sleep 0.15
}

send_lines() {
  # Send multiple lines: line-by-line + Enter each time.
  local target="$1"
  shift
  local line
  for line in "$@"; do
    send_and_enter "$target" "$line"
  done
  # Extra Enter to "unstick" UIs that buffer a final newline.
  tmux send-keys -t "$target" Enter
}

# Start Codex (or fallback shell) in each pane
send_and_enter "$SESSION:main.0" "cd \"$ROOT_DIR\"; $start_codex"
send_and_enter "$SESSION:main.1" "cd \"$ROOT_DIR\"; $start_codex"
send_and_enter "$SESSION:main.2" "cd \"$ROOT_DIR\"; $start_codex"
send_and_enter "$SESSION:main.3" "cd \"$ROOT_DIR\"; $start_codex"

# Role prompts: send one line at a time to avoid paste-mode buffering
send_lines "$SESSION:main.0" \
  "You are SHOGUN." \
  "Read task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml" \
  "Follow constraints." \
  "Write result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml" \
  "If you propose code changes, produce a patch file and reference it in result." \
  "Do NOT apply changes to repo unless write_policy=allow_edit."

send_lines "$SESSION:main.1" \
  "You are KARO." \
  "Read task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml" \
  "Follow constraints." \
  "Write result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml" \
  "If you propose code changes, produce a patch file and reference it in result." \
  "Do NOT apply changes to repo unless write_policy=allow_edit."

send_lines "$SESSION:main.2" \
  "You are ASHIGARU1." \
  "Read task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml" \
  "Follow constraints." \
  "Write result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml" \
  "If you propose code changes, produce a patch file and reference it in result." \
  "Do NOT apply changes to repo unless write_policy=allow_edit."

send_lines "$SESSION:main.3" \
  "You are ASHIGARU2." \
  "Read task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml" \
  "Follow constraints." \
  "Write result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml" \
  "If you propose code changes, produce a patch file and reference it in result." \
  "Do NOT apply changes to repo unless write_policy=allow_edit."

tmux select-pane -t "$SESSION:main.0"
tmux attach -t "$SESSION"

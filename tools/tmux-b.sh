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

# NOTE:
# For reliability (Codex CLI / shell input modes), send literal text and Enter separately.
# Some environments drop the Enter when mixed in a single send-keys invocation.
send_line() {
  local target="$1"
  local line="$2"
  tmux send-keys -t "$target" -l "$line"
  sleep 0.05
  tmux send-keys -t "$target" Enter
  sleep 0.05
  tmux send-keys -t "$target" Enter
}

send_multiline() {
  local target="$1"
  local text="$2"
  tmux send-keys -t "$target" -l "$text"
  sleep 0.05
  tmux send-keys -t "$target" Enter
  sleep 0.05
  tmux send-keys -t "$target" Enter
}

send_line "$SESSION:main.0" "cd \"$ROOT_DIR\"; $start_codex"
send_line "$SESSION:main.1" "cd \"$ROOT_DIR\"; $start_codex"
send_line "$SESSION:main.2" "cd \"$ROOT_DIR\"; $start_codex"
send_line "$SESSION:main.3" "cd \"$ROOT_DIR\"; $start_codex"

send_multiline "$SESSION:main.0" $'You are SHOGUN.\nRead task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml\nFollow constraints.\nWrite result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml\nIf you propose code changes, produce a patch file and reference it in result.\nDo NOT apply changes to repo unless write_policy=allow_edit.'
send_multiline "$SESSION:main.1" $'You are KARO.\nRead task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml\nFollow constraints.\nWrite result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml\nIf you propose code changes, produce a patch file and reference it in result.\nDo NOT apply changes to repo unless write_policy=allow_edit.'
send_multiline "$SESSION:main.2" $'You are ASHIGARU1.\nRead task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml\nFollow constraints.\nWrite result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml\nIf you propose code changes, produce a patch file and reference it in result.\nDo NOT apply changes to repo unless write_policy=allow_edit.'
send_multiline "$SESSION:main.3" $'You are ASHIGARU2.\nRead task YAML at: b/tasks/TASK-YYYYMMDD-xxxx-ROLE.yaml\nFollow constraints.\nWrite result YAML to: b/results/RESULT-YYYYMMDD-xxxx.yaml\nIf you propose code changes, produce a patch file and reference it in result.\nDo NOT apply changes to repo unless write_policy=allow_edit.'

tmux select-pane -t "$SESSION:main.0"
tmux attach -t "$SESSION"

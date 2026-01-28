#!/usr/bin/env bash
set -euo pipefail

SESSION="docxbrief-b"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

# Always start from a clean session to avoid agents continuing old context.
if tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
fi
tmux new-session -d -s "$SESSION" -n main

tmux split-window -h -t "$SESSION:main"
tmux split-window -v -t "$SESSION:main.0"
tmux split-window -v -t "$SESSION:main.1"

tmux set-option -t "$SESSION" pane-border-status top
tmux set-option -t "$SESSION" pane-border-format "#[reverse] #T #[default]"

tmux select-pane -t "$SESSION:main.0"
tmux select-pane -T "shogun"
tmux select-pane -t "$SESSION:main.1"
tmux select-pane -T "karo"
tmux select-pane -t "$SESSION:main.2"
tmux select-pane -T "ashigaru1"
tmux select-pane -t "$SESSION:main.3"
tmux select-pane -T "ashigaru2"

tmux bind-key -T prefix d display-prompt -p "task yaml:" "run-shell 'cd \"$ROOT_DIR\"; docxbrief b dispatch %%'"

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
}

# Start Codex (or fallback shell) in each pane
send_and_enter "$SESSION:main.0" "cd \"$ROOT_DIR\"; $start_codex"
send_and_enter "$SESSION:main.1" "cd \"$ROOT_DIR\"; $start_codex"
send_and_enter "$SESSION:main.2" "cd \"$ROOT_DIR\"; $start_codex"
send_and_enter "$SESSION:main.3" "cd \"$ROOT_DIR\"; $start_codex"

# Role prompts: send one line at a time to avoid paste-mode buffering
# Role prompts (IDLE mode):
# On startup, agents must NOT start working or planning.
# They should print READY and wait for a dispatch message that begins with "Read: b/tasks/".
send_lines "$SESSION:main.0" \
  "You are SHOGUN." \
  "Startup behavior: do nothing. Print 'READY (SHOGUN)' and wait." \
  "Do NOT plan, review, or propose changes unless explicitly dispatched." \
  "You must ONLY act when you receive a dispatch message that begins with:" \
  "  Read: b/tasks/" \
  "When dispatched, open the YAML at that path, follow constraints, and coordinate the workflow." \
  "You may ask the human for approvals when needed." \
  "Never apply changes unless write_policy=allow_edit."

send_lines "$SESSION:main.1" \
  "You are KARO." \
  "Startup behavior: do nothing. Print 'READY (KARO)' and wait." \
  "Do NOT plan, review, or propose changes unless explicitly dispatched." \
  "You must ONLY act when you receive a dispatch message that begins with:" \
  "  Read: b/tasks/" \
  "When dispatched, open the YAML at that path and do exactly what it requests." \
  "Create the expected result file path under outputs.expected[0] (or b/results/)." \
  "If you propose code changes, produce a patch file and reference it in the result YAML." \
  "Never apply changes unless write_policy=allow_edit."

send_lines "$SESSION:main.2" \
  "You are ASHIGARU1." \
  "Startup behavior: do nothing. Print 'READY (ASHIGARU1)' and wait." \
  "Do NOT plan, review, or propose changes unless explicitly dispatched." \
  "You must ONLY act when you receive a dispatch message that begins with:" \
  "  Read: b/tasks/" \
  "When dispatched, open the YAML at that path and do exactly what it requests." \
  "Create the expected result file path under outputs.expected[0] (or b/results/)." \
  "If you propose code changes, produce a patch file and reference it in the result YAML." \
  "Never apply changes unless write_policy=allow_edit."

send_lines "$SESSION:main.3" \
  "You are ASHIGARU2." \
  "Startup behavior: do nothing. Print 'READY (ASHIGARU2)' and wait." \
  "Do NOT plan, review, or propose changes unless explicitly dispatched." \
  "You must ONLY act when you receive a dispatch message that begins with:" \
  "  Read: b/tasks/" \
  "When dispatched, open the YAML at that path and do exactly what it requests." \
  "Create the expected result file path under outputs.expected[0] (or b/results/)." \
  "If you propose code changes, produce a patch file and reference it in the result YAML." \
  "Never apply changes unless write_policy=allow_edit."

# Trigger initial READY output (so panes are visibly idle)
send_and_enter "$SESSION:main.0" "READY (SHOGUN)"
send_and_enter "$SESSION:main.1" "READY (KARO)"
send_and_enter "$SESSION:main.2" "READY (ASHIGARU1)"
send_and_enter "$SESSION:main.3" "READY (ASHIGARU2)"

tmux select-pane -t "$SESSION:main.0"
tmux attach -t "$SESSION"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TASK_PATH="b/tasks/TASK-repro-ashigaru1.yaml"
RESULT_PATH="b/results/RESULT-repro.yaml"

cleanup() {
  rm -f "$TASK_PATH" "$RESULT_PATH"
}
trap cleanup EXIT

cat > "$TASK_PATH" <<'YAML'
version: 1
id: "TASK-repro"
issued_at: "2026-01-28T12:34:56+09:00"
issuer: "shogun"
assignee: "ashigaru1"
title: "Await repro"
objective: >
  Simple await repro with outputs.expected.
outputs:
  expected:
    - "b/results/RESULT-repro.yaml"
constraints:
  network: "disallow"
  write_policy: "no_direct_edit"
YAML

(sleep 1; cat > "$RESULT_PATH" <<'YAML'
version: 1
task_id: "TASK-repro"
assignee: "ashigaru1"
status: "done"
summary: "Repro result"
YAML
) &

docxbrief b await "$TASK_PATH" --timeout 5

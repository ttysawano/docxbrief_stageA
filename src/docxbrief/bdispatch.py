from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import datetime as _dt
import subprocess
import time
from typing import Iterable

import yaml


DEFAULT_SESSION = "docxbrief-b"
DEFAULT_WINDOW = "main"
PANE_FALLBACK = {
    "shogun": "0",
    "karo": "1",
    "ashigaru1": "2",
    "ashigaru2": "3",
}


@dataclass(frozen=True)
class TaskInfo:
    path: Path
    task_id: str
    assignee: str
    expected_results: list[Path]
    write_policy: str


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _session_name() -> str:
    session_path = Path("b/state/session.yaml")
    if session_path.exists():
        data = _load_yaml(session_path)
        name = data.get("tmux_session")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return DEFAULT_SESSION


def _list_panes(session: str) -> list[tuple[str, str, str]]:
    fmt = "#{pane_id}\t#{pane_index}\t#{pane_title}"
    cmd = ["tmux", "list-panes", "-t", session, "-F", fmt]
    try:
        out = subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"tmux session not found: {session}") from exc
    panes = []
    for line in out.strip().splitlines():
        if not line.strip():
            continue
        pane_id, pane_index, pane_title = line.split("\t", 2)
        panes.append((pane_id, pane_index, pane_title))
    return panes


def _find_pane_target(session: str, assignee: str) -> str:
    panes = _list_panes(session)
    for pane_id, _pane_index, pane_title in panes:
        if pane_title.strip() == assignee:
            return pane_id
    fallback_index = PANE_FALLBACK.get(assignee)
    if fallback_index is not None:
        return f"{session}:{DEFAULT_WINDOW}.{fallback_index}"
    raise RuntimeError(f"no pane found for assignee '{assignee}' in session '{session}'")


def _send_keys(target: str, lines: Iterable[str]) -> None:
    msg = "\n".join(lines)
    subprocess.check_call(["tmux", "send-keys", "-t", target, msg, "C-m"])


def _expected_results(task: dict) -> list[Path]:
    outputs = task.get("outputs", {})
    expected = outputs.get("expected", [])
    results: list[Path] = []
    if isinstance(expected, list):
        for item in expected:
            if isinstance(item, str) and item.strip():
                results.append(Path(item))
    if results:
        return results
    task_id = task.get("id", "")
    if isinstance(task_id, str) and task_id:
        suffix = task_id[5:] if task_id.startswith("TASK-") else task_id
        return [Path(f"b/results/RESULT-{suffix}.yaml")]
    return []


def _write_lock(assignee: str, task_id: str) -> None:
    state_dir = Path("b/state")
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = state_dir / f"lock-{assignee}"
    now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    payload = {"task_id": task_id, "started_at": now}
    lock_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _log_line(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")


def _task_info(task_path: Path) -> TaskInfo:
    task = _load_yaml(task_path)
    task_id = str(task.get("id", "")).strip()
    assignee = str(task.get("assignee", "")).strip()
    if not task_id or not assignee:
        raise ValueError("task must include id and assignee")
    expected_results = _expected_results(task)
    constraints = task.get("constraints", {})
    write_policy = str(constraints.get("write_policy", "no_direct_edit"))
    return TaskInfo(
        path=task_path,
        task_id=task_id,
        assignee=assignee,
        expected_results=expected_results,
        write_policy=write_policy,
    )


def dispatch_task(task_path: Path) -> None:
    info = _task_info(task_path)
    session = _session_name()
    target = _find_pane_target(session, info.assignee)

    lines = [
        f"Read task YAML at: {info.path.as_posix()}",
        f"Write result YAML to: {', '.join(p.as_posix() for p in info.expected_results) or 'b/results/RESULT-*.yaml'}",
        f"Follow write_policy: {info.write_policy}",
    ]

    _send_keys(target, lines)
    _write_lock(info.assignee, info.task_id)
    _log_line(Path("b/logs/dispatch.log"), f"dispatch {info.task_id} -> {info.assignee} ({session})")


def _find_latest_result_by_task_id(task_id: str) -> Path | None:
    results_dir = Path("b/results")
    if not results_dir.exists():
        return None
    latest_path: Path | None = None
    latest_mtime = -1.0
    for path in results_dir.glob("RESULT-*.yaml"):
        try:
            data = _load_yaml(path)
        except Exception:
            continue
        if str(data.get("task_id", "")).strip() == task_id:
            mtime = path.stat().st_mtime
            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_path = path
    return latest_path


def await_result(task_path: Path, timeout: float) -> tuple[Path | None, str]:
    info = _task_info(task_path)
    deadline = time.monotonic() + timeout
    if info.expected_results:
        expected = info.expected_results[0]
        description = f"expected: {expected.as_posix()}"
        while True:
            if expected.exists():
                return expected, description
            if time.monotonic() >= deadline:
                return None, description
            time.sleep(0.5)
    description = f"searched: b/results/*.yaml with task_id == {info.task_id}"
    while True:
        match = _find_latest_result_by_task_id(info.task_id)
        if match is not None:
            return match, description
        if time.monotonic() >= deadline:
            return None, description
        time.sleep(0.5)

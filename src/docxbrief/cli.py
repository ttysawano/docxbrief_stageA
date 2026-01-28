from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import load_config, init_templates
from .scan import scan_files
from .build import build_summary, update_summary
from .shell import run_shell
from .status import show_status
from .reset import reset_project
from .bdispatch import dispatch_task, await_result


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("-c", "--config", default="docxbrief.yaml", help="Path to config YAML (default: docxbrief.yaml)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docxbrief", description="Scan .docx files and generate AsciiDoc summary (Stage A).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create config/template files if missing.")
    _add_common_args(p_init)
    p_init.add_argument("--dir", dest="input_dir", default=None, help="Override project.input_dir on init")
    p_init.add_argument("--out", dest="output_adoc", default=None, help="Override project.output_adoc on init")

    p_scan = sub.add_parser("scan", help="List matched .docx files.")
    _add_common_args(p_scan)
    p_scan.add_argument("--json", action="store_true", help="Print machine-readable JSON list")
    p_scan.add_argument("--print", action="store_true", help="Print paths (default behavior)")

    p_build = sub.add_parser("build", help="Build summary for all matched files (initial build).")
    _add_common_args(p_build)
    p_build.add_argument("--force", action="store_true", help="Rebuild even if manifest exists")

    p_update = sub.add_parser("update", help="Update summary only for changed files.")
    _add_common_args(p_update)
    p_update.add_argument("--force", action="store_true", help="Force reprocess all matched files")

    p_shell = sub.add_parser("shell", help="Interactive helper (Shogun A).")
    _add_common_args(p_shell)

    p_status = sub.add_parser("status", help="Show current config and manifest overview.")
    _add_common_args(p_status)

    p_reset = sub.add_parser("reset", help="Reset state (and optionally output) to avoid stale changelog.")
    _add_common_args(p_reset)
    p_reset.add_argument("--all", action="store_true", help="Also remove output summary.adoc")
    p_reset.add_argument("--yes", action="store_true", help="Skip confirmation")

    p_b = sub.add_parser("b", help="Stage B helpers (tmux/Codex dispatcher).")
    _add_common_args(p_b)
    b_sub = p_b.add_subparsers(dest="b_cmd", required=True)

    p_dispatch = b_sub.add_parser("dispatch", help="Dispatch a task YAML to the assignee pane.")
    _add_common_args(p_dispatch)
    p_dispatch.add_argument("task_yaml", help="Path to task YAML (b/tasks/*.yaml)")

    p_await = b_sub.add_parser("await", help="Wait for result YAML for a task.")
    _add_common_args(p_await)
    p_await.add_argument("task_yaml", help="Path to task YAML (b/tasks/*.yaml)")
    p_await.add_argument("--timeout", type=float, default=600.0, help="Timeout seconds (default: 600)")

    args = parser.parse_args(argv)

    if args.cmd == "init":
        cfg_path = Path(args.config)
        init_templates(cfg_path, override_input_dir=args.input_dir, override_output_adoc=args.output_adoc)
        print(f"Initialized templates (config: {cfg_path})")
        return 0

    cfg = load_config(Path(args.config))

    if args.cmd == "scan":
        files = scan_files(cfg)
        if args.json:
            import json
            print(json.dumps([str(p) for p in files], ensure_ascii=False, indent=2))
        else:
            for p in files:
                print(p)
        return 0

    if args.cmd == "build":
        return 0 if build_summary(cfg, force=args.force) else 1

    if args.cmd == "update":
        return 0 if update_summary(cfg, force=args.force) else 1

    if args.cmd == "shell":
        return 0 if run_shell(cfg) else 1

    if args.cmd == "status":
        show_status(cfg)
        return 0

    if args.cmd == "reset":
        if not args.yes:
            print("This will delete .docxbrief/ (state)" + (" and summary.adoc" if args.all else "") + ".")
            print("Re-run with --yes to proceed.")
            return 2
        reset_project(cfg, remove_summary=bool(args.all), remove_state=True)
        print("Reset complete.")
        return 0

    if args.cmd == "b":
        if args.b_cmd == "dispatch":
            try:
                dispatch_task(Path(args.task_yaml))
            except RuntimeError as exc:
                print(str(exc))
                return 1
            return 0
        if args.b_cmd == "await":
            result = await_result(Path(args.task_yaml), timeout=float(args.timeout))
            if result is None:
                print("Result not found before timeout.")
                return 1
            print(result.read_text(encoding="utf-8"))
            return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

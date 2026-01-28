from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import load_config, init_templates
from .scan import scan_files
from .build import build_summary, update_summary
from .shell import run_shell
from .status import show_status


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

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

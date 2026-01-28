from __future__ import annotations

from pathlib import Path
import difflib
import yaml

from .config import Config


def run_shell(cfg: Config) -> bool:
    print("DocxBrief Shell (Stage A)")
    print(f"Config: {cfg.config_path}")
    print("")
    data = cfg.raw

    def show():
        proj = data.get("project", {})
        print("Current settings:")
        print(f"  input_dir   : {proj.get('input_dir')}")
        print(f"  output_adoc : {proj.get('output_adoc')}")
        print(f"  state_dir   : {proj.get('state_dir')}")
        print(f"  include_glob: {data.get('scan', {}).get('include_glob')}")
        print(f"  exclude_glob: {data.get('scan', {}).get('exclude_glob')}")
        print(f"  filename_regex: {data.get('filter', {}).get('filename_regex')}")
        print("")

    show()
    print("Choose item to edit (comma-separated):")
    print("  1) input_dir")
    print("  2) output_adoc")
    print("  3) add filename_regex")
    print("  4) done (no change)")
    choice = input("> ").strip()
    if choice == "4" or choice == "":
        return True

    if "1" in choice:
        new_dir = input("input_dir (e.g., ./docs): ").strip()
        if new_dir:
            data.setdefault("project", {})["input_dir"] = new_dir

    if "2" in choice:
        new_out = input("output_adoc (e.g., ./summary.adoc): ").strip()
        if new_out:
            data.setdefault("project", {})["output_adoc"] = new_out

    if "3" in choice:
        r = input("Add regex (e.g., (minutes|議事録)) : ").strip()
        if r:
            data.setdefault("filter", {}).setdefault("filename_regex", []).append(r)

    proposed_path = cfg.config_path.with_suffix(cfg.config_path.suffix + ".proposed")
    proposed_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    proposed_path.write_text(proposed_text, encoding="utf-8")

    original = cfg.config_path.read_text(encoding="utf-8").splitlines(keepends=True)
    proposed = proposed_text.splitlines(keepends=True)
    diff = "".join(difflib.unified_diff(original, proposed, fromfile=str(cfg.config_path), tofile=str(proposed_path)))
    print("\n--- Proposed diff ---")
    print(diff if diff.strip() else "(no diff)")
    ans = input("Apply? [y/N] ").strip().lower()
    if ans == "y":
        cfg.config_path.write_text(proposed_text, encoding="utf-8")
        print("Applied.")
    else:
        print("Not applied. Proposed file kept:", proposed_path)
    return True

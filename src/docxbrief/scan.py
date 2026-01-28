from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

from .config import Config


def _glob_paths(input_dir: Path, patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pat in patterns:
        paths.extend(input_dir.glob(pat))
    # unique + sort
    uniq = sorted({p for p in paths if p.is_file()})
    return uniq


def scan_files(cfg: Config) -> list[Path]:
    input_dir = cfg.input_dir
    scan_cfg = cfg.raw.get("scan", {})
    include = scan_cfg.get("include_glob", ["**/*.docx"])
    exclude = scan_cfg.get("exclude_glob", [])

    files = _glob_paths(input_dir, include)

    # Exclude globs
    excl_set: set[Path] = set()
    for pat in exclude:
        excl_set.update({p for p in input_dir.glob(pat) if p.is_file()})
    files = [p for p in files if p not in excl_set]

    # filename regex filters
    filt = cfg.raw.get("filter", {})
    regexes = filt.get("filename_regex", []) or []
    if regexes:
        comp = [re.compile(r) for r in regexes]
        files = [p for p in files if any(r.search(p.name) for r in comp)]

    max_files = int(filt.get("max_files", 200))
    return files[:max_files]

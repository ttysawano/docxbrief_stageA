from __future__ import annotations

from pathlib import Path
import datetime
import difflib

from .config import Config
from .scan import scan_files
from .state import load_manifest, save_manifest, ensure_state, sha256_file
from .extract import extract_docx_text
from .summarize import summarize_text
from .render import render_summary


def _now_local_date() -> str:
    # Keep it simple: local date (no timezone conversion)
    return datetime.datetime.now().strftime("%Y-%m-%d")


def _append_changelog(manifest: dict, target: str, message: str) -> None:
    manifest.setdefault("changelog", []).append(
        {"date": _now_local_date(), "target": target, "message": message}
    )


def build_summary(cfg: Config, force: bool = False) -> bool:
    """Initial build: compute summaries for all matched files and write summary.adoc."""
    ensure_state(cfg)
    files = scan_files(cfg)
    manifest = load_manifest(cfg)

    is_first_build = (not manifest.get("files"))

    for p in files:
        sp = str(p)
        sha = sha256_file(p)
        prev = manifest.get("files", {}).get(sp)
        need = force or (prev is None) or (prev.get("sha256") != sha)
        if need:
            text = extract_docx_text(cfg, p)
            bullets = summarize_text(cfg, text)
            manifest.setdefault("files", {})[sp] = {
                "sha256": sha,
                "mtime": p.stat().st_mtime,
                "summary": bullets,
            }

    # Remove entries for files no longer matched (only if not first build)
    current = {str(p) for p in files}
    to_remove = [k for k in manifest.get("files", {}).keys() if k not in current]
    for k in to_remove:
        # keep record but drop from current build view
        manifest["files"].pop(k, None)

    manifest["generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if is_first_build:
        _append_changelog(manifest, "(all)", f"Initial build: {len(files)} file(s) processed.")

    save_manifest(cfg, manifest)

    # Render from manifest summaries (stable)
    summaries = {k: v.get("summary", []) for k, v in manifest.get("files", {}).items()}
    render_summary(cfg, files, summaries, manifest)
    return True


def update_summary(cfg: Config, force: bool = False) -> bool:
    """Update: re-summarize changed/new files, keep unchanged, and append changelog."""
    ensure_state(cfg)
    files = scan_files(cfg)
    manifest = load_manifest(cfg)

    # First build fallback
    if not manifest.get("files"):
        return build_summary(cfg, force=True)

    current = {str(p) for p in files}

    # Detect removed files (no longer matched)
    removed = [k for k in list(manifest.get("files", {}).keys()) if k not in current]
    for k in removed:
        manifest["files"].pop(k, None)
        _append_changelog(manifest, k, "Removed from scan scope.")

    # Process current files
    for p in files:
        sp = str(p)
        sha = sha256_file(p)
        prev = manifest.get("files", {}).get(sp)

        if force or (prev is None) or (prev.get("sha256") != sha):
            old_summary = (prev or {}).get("summary", [])
            text = extract_docx_text(cfg, p)
            new_summary = summarize_text(cfg, text)

            # diff stats at "bullet level" (cheap, but useful)
            sm = difflib.SequenceMatcher(a=old_summary, b=new_summary)
            added = removed_n = 0
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == "insert":
                    added += (j2 - j1)
                elif tag == "delete":
                    removed_n += (i2 - i1)
                elif tag == "replace":
                    removed_n += (i2 - i1)
                    added += (j2 - j1)

            if prev is None:
                _append_changelog(manifest, sp, "Added (new file).")
            else:
                _append_changelog(manifest, sp, f"Updated summary (+{added}/-{removed_n} bullets).")

            manifest.setdefault("files", {})[sp] = {
                "sha256": sha,
                "mtime": p.stat().st_mtime,
                "summary": new_summary,
            }

    manifest["generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_manifest(cfg, manifest)

    summaries = {k: v.get("summary", []) for k, v in manifest.get("files", {}).items()}
    render_summary(cfg, files, summaries, manifest)
    return True

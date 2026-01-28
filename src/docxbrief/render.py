from __future__ import annotations

from pathlib import Path
import datetime
from .config import Config


def _iso_from_mtime(mtime: float) -> str:
    return datetime.datetime.fromtimestamp(mtime).isoformat(timespec="seconds")


def render_summary(cfg: Config, files, summaries: dict[str, list[str]], manifest: dict) -> None:
    tpl_path = Path(__file__).resolve().parent.parent.parent / "templates" / "summary.adoc"
    tpl = tpl_path.read_text(encoding="utf-8")

    # file table rows in scan order
    file_table_rows = []
    for p in files:
        sp = str(p)
        info = manifest.get("files", {}).get(sp, {})
        sha = info.get("sha256", "")
        mtime = info.get("mtime", p.stat().st_mtime)
        file_table_rows.append(f"| {sp} | {_iso_from_mtime(mtime)} | {sha}")
    file_table_rows_s = "\n".join(file_table_rows)

    # summaries section in scan order
    parts = []
    for p in files:
        sp = str(p)
        parts.append(f"=== {sp}")
        for b in summaries.get(sp, []):
            parts.append(f"* {b}")
        parts.append("")
    file_summaries = "\n".join(parts).strip()

    # changelog rows
    rows = []
    for ch in manifest.get("changelog", []):
        rows.append(f"| {ch.get('date','')} | {ch.get('target','')} | {ch.get('message','')}")
    changelog_rows = "\n".join(rows)

    out = tpl.format(
        project_name=cfg.project.get("name", "DocxBrief"),
        project_description=cfg.project.get("description", ""),
        file_table_rows=file_table_rows_s,
        file_summaries=file_summaries,
        changelog_rows=changelog_rows,
    )
    cfg.output_adoc.write_text(out, encoding="utf-8")

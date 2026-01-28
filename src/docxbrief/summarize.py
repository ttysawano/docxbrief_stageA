from __future__ import annotations

import re
from typing import List, Tuple
from .config import Config

_BULLET_RE = re.compile(r"^\s*(?:[-*•・]|\d+\.)\s+")
# Heuristic: short line, no trailing period, not too punctuated
_PUNCT_RE = re.compile(r"[。．\.,:：;；\(\)\[\]{}<>]|\d{4}/\d{2}/\d{2}")

_HEADING_STOP = {
    "Revision List", "改訂", "変更内容", "著者", "日付",
}

# Common Japanese section headings in technical docs
_KNOWN_HEADINGS = (
    "本文書について",
    "適用文書",
    "参考文書",
    "前提条件",
    "解析手法",
    "解析方法",
    "結果",
    "結論",
    "目的",
    "概要",
)


def _is_heading_candidate(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s in _HEADING_STOP:
        return False
    # known headings
    if any(k in s for k in _KNOWN_HEADINGS):
        return True
    # Short-ish, low punctuation, looks like a label
    if len(s) <= 18 and not _PUNCT_RE.search(s):
        return True
    return False


def _first_meaningful_line(lines: List[str]) -> str | None:
    for ln in lines:
        t = ln.strip()
        if not t:
            continue
        if t in _HEADING_STOP:
            continue
        return t
    return None


def _truncate(s: str, n: int = 160) -> str:
    s = s.strip()
    if len(s) <= n:
        return s
    return s[: n - 3] + "..."


def summarize_text(cfg: Config, text: str) -> list[str]:
    """Stage A: Section-aware heuristic summary.

    Goals:
    - Keep original order (no re-order surprises)
    - Prefer real section headings and first sentences under them
    - Avoid cover-page / revision-table noise
    """
    bullets_max = int(cfg.raw.get("summarize", {}).get("bullets_max", 8))

    # Preserve paragraph boundaries (extract.py joins paragraphs with \n)
    paras = [ln.strip() for ln in text.splitlines() if ln.strip()]

    if not paras:
        return []

    # 1) Pick a compact "doc header" (title-ish lines) from the beginning
    header: list[str] = []
    for ln in paras[:12]:
        if ln in _HEADING_STOP:
            continue
        if "Revision List" in ln:
            continue
        # skip table-like single-word headers
        if ln in {"改訂", "変更内容", "著者", "日付"}:
            continue
        header.append(ln)
        if len(header) >= 3:
            break

    # 2) Find first real section heading to start summarizing the body
    heading_idxs = [i for i, ln in enumerate(paras) if _is_heading_candidate(ln)]
    start_i = heading_idxs[0] if heading_idxs else 0

    # If the first heading is very early and looks like cover, push start to the first known heading if exists
    for i, ln in enumerate(paras):
        if any(k in ln for k in _KNOWN_HEADINGS):
            start_i = i
            break

    body = paras[start_i:]

    # Recompute heading indices within body
    rel_heading_idxs = [i for i, ln in enumerate(body) if _is_heading_candidate(ln)]
    if not rel_heading_idxs:
        # fallback: pick first N lines as-is
        picked = header + body[: max(0, bullets_max - len(header))]
        # de-dup preserving order
        seen = set()
        out = []
        for x in picked:
            if x in seen:
                continue
            seen.add(x)
            out.append(_truncate(x))
        return out[:bullets_max]

    # 3) Build section bullets in order: "Heading — first line / key line"
    focus = cfg.raw.get("summarize", {}).get("focus", []) or []
    out: list[str] = []

    # include header lines first (dedup later)
    out.extend(header)

    for idx_pos, hi in enumerate(rel_heading_idxs):
        heading = body[hi].strip()
        next_hi = rel_heading_idxs[idx_pos + 1] if idx_pos + 1 < len(rel_heading_idxs) else len(body)
        section_lines = body[hi + 1 : next_hi]

        # pick a key line in section: focus keyword line > first meaningful line
        key = None
        for ln in section_lines:
            if any(k in ln for k in focus):
                key = ln.strip()
                break
        if key is None:
            key = _first_meaningful_line(section_lines)

        if key:
            out.append(f"{heading} — {_truncate(key)}")
        else:
            out.append(heading)

        if len(out) >= bullets_max:
            break

    # de-dup preserving order
    seen = set()
    deduped = []
    for x in out:
        x = _truncate(x)
        if x in seen:
            continue
        seen.add(x)
        deduped.append(x)

    return deduped[:bullets_max]

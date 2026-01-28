from __future__ import annotations

import difflib
from typing import Dict


def diff_stats(old: str, new: str) -> Dict[str, int]:
    """Return simple diff stats: added/removed lines."""
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines)
    added = removed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":
            added += (j2 - j1)
        elif tag == "delete":
            removed += (i2 - i1)
        elif tag == "replace":
            removed += (i2 - i1)
            added += (j2 - j1)
    return {"added": added, "removed": removed}

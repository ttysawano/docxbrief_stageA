from __future__ import annotations

import shutil

from .config import Config


def reset_project(cfg: Config, *, remove_summary: bool = False, remove_state: bool = True) -> None:
    """Reset docxbrief project state.

    This exists to avoid "stale changelog" issues when users swap the input docs set.

    - remove_state=True: delete cfg.state_dir (manifest, caches, logs)
    - remove_summary=True: also delete cfg.output_adoc (generated output)
    """
    if remove_state and cfg.state_dir.exists():
        shutil.rmtree(cfg.state_dir)

    if remove_summary:
        out = cfg.output_adoc
        if out.exists():
            out.unlink()

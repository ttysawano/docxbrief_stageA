from __future__ import annotations

from pathlib import Path
import json
import hashlib
import datetime

from .config import Config


def ensure_state(cfg: Config) -> None:
    cfg.state_dir.mkdir(parents=True, exist_ok=True)
    (cfg.state_dir / "log.txt").touch(exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(cfg: Config) -> dict:
    ensure_state(cfg)
    p = cfg.state_dir / "manifest.json"
    if not p.exists():
        return {"version": 1, "generated_at": "", "files": {}, "changelog": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save_manifest(cfg: Config, manifest: dict) -> None:
    ensure_state(cfg)
    p = cfg.state_dir / "manifest.json"
    p.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

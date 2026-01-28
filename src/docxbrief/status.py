from __future__ import annotations

from .config import Config
from .state import load_manifest


def show_status(cfg: Config) -> None:
    print("DocxBrief Status")
    print(f"  config   : {cfg.config_path}")
    print(f"  input_dir: {cfg.input_dir}")
    print(f"  output  : {cfg.output_adoc}")
    print(f"  state   : {cfg.state_dir}")
    m = load_manifest(cfg)
    print(f"  manifest version: {m.get('version')}")
    print(f"  tracked files   : {len(m.get('files', {}))}")
    print(f"  changelog rows  : {len(m.get('changelog', []))}")

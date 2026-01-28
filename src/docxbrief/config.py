from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import shutil
import yaml

TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


@dataclass
class Config:
    raw: dict[str, Any]
    config_path: Path

    @property
    def project(self) -> dict[str, Any]:
        return self.raw.get("project", {})

    @property
    def state_dir(self) -> Path:
        return Path(self.project.get("state_dir", "./.docxbrief"))

    @property
    def input_dir(self) -> Path:
        return Path(self.project.get("input_dir", "./docs"))

    @property
    def output_adoc(self) -> Path:
        return Path(self.project.get("output_adoc", "./summary.adoc"))


def load_config(path: Path) -> Config:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Config(raw=data, config_path=path)


def init_templates(config_path: Path, override_input_dir: str | None = None, override_output_adoc: str | None = None) -> None:
    # Copy templates if missing
    config_tpl = TEMPLATE_DIR / "docxbrief.yaml"
    adoc_tpl = TEMPLATE_DIR / "summary.adoc"

    if not config_path.exists():
        shutil.copyfile(config_tpl, config_path)

    # Apply overrides if provided
    if override_input_dir or override_output_adoc:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if override_input_dir:
            data.setdefault("project", {})["input_dir"] = override_input_dir
        if override_output_adoc:
            data.setdefault("project", {})["output_adoc"] = override_output_adoc
        config_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # Ensure state dir exists
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    state_dir = Path(data.get("project", {}).get("state_dir", "./.docxbrief"))
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "log.txt").touch(exist_ok=True)

    # Create summary.adoc if missing
    out_adoc = Path(data.get("project", {}).get("output_adoc", "./summary.adoc"))
    if not out_adoc.exists():
        shutil.copyfile(adoc_tpl, out_adoc)

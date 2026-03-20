from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATABASE_NAME = "financial_warehouse.db"


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    project_root: Path
    raw_data_dir: Path
    processed_data_dir: Path
    warehouse_dir: Path
    database_url: str
    log_level: str = "INFO"

    @classmethod
    def from_project_root(
        cls,
        project_root: Path,
        *,
        raw_data_dir: Path | None = None,
        processed_data_dir: Path | None = None,
        warehouse_dir: Path | None = None,
        database_url: str | None = None,
        log_level: str = "INFO",
    ) -> PipelineConfig:
        root = project_root.resolve()
        raw_dir = _resolve_path(root, raw_data_dir, Path("data/raw"))
        processed_dir = _resolve_path(root, processed_data_dir, Path("data/processed"))
        warehouse = _resolve_path(root, warehouse_dir, Path("data/warehouse"))

        resolved_database_url = (
            database_url or f"sqlite:///{(warehouse / DEFAULT_DATABASE_NAME).as_posix()}"
        )

        return cls(
            project_root=root,
            raw_data_dir=raw_dir,
            processed_data_dir=processed_dir,
            warehouse_dir=warehouse,
            database_url=resolved_database_url,
            log_level=log_level.upper(),
        )

    def ensure_directories(self) -> None:
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        self.warehouse_dir.mkdir(parents=True, exist_ok=True)


def _resolve_path(project_root: Path, candidate: Path | None, default: Path) -> Path:
    path = candidate or default
    return path if path.is_absolute() else project_root / path

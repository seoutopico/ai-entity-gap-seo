from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def ensure_parent(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def canonicalize_entity(entity: str) -> str:
    entity = normalize_text(entity)
    entity = re.sub(r"[^\w\sáéíóúüñçàèìòùäëïöâêîôû-]", " ", entity, flags=re.IGNORECASE)
    entity = re.sub(r"\s+", " ", entity).strip(" -_")
    return entity


def slugify(value: str) -> str:
    value = canonicalize_entity(value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "untitled"


def read_optional_csv(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def require_columns(df: pd.DataFrame, columns: list[str], source_name: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source_name} is missing required columns: {missing}")


def classify_entity(entity: str, ontology: dict[str, Any]) -> str:
    patterns = (ontology or {}).get("patterns", [])
    canonical = canonicalize_entity(entity)
    for item in patterns:
        regex = item.get("regex")
        entity_type = item.get("type")
        if regex and entity_type and re.search(regex, canonical, flags=re.IGNORECASE):
            return str(entity_type)
    return "unknown"


def minmax(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    min_value = series.min()
    max_value = series.max()
    if max_value == min_value:
        return pd.Series([1.0 if max_value > 0 else 0.0] * len(series), index=series.index)
    return (series - min_value) / (max_value - min_value)

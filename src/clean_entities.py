from __future__ import annotations

"""
Limpia el crudo de la API (entities_raw.csv) y produce un entities.csv depurado.

NO llama a la API: opera sobre el resultado ya extraído, así puedes iterar los
filtros de config/config.yml -> cleaning sin gastar unidades.

Uso:
    python src/clean_entities.py --config config/config.yml
    python src/clean_entities.py --raw outputs/entities_raw.csv --out outputs/entities.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from utils import canonicalize_entity, classify_entity, ensure_parent, load_config

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def clean(raw_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    cleaning = config.get("cleaning", {})
    exclude_types = {t.lower() for t in cleaning.get("exclude_types", [])}
    min_salience = float(cleaning.get("min_salience", 0.0))
    max_words = int(cleaning.get("max_entity_words", 0))
    blocklist = {canonicalize_entity(t) for t in cleaning.get("blocklist", [])}
    ontology = config.get("ontology", {})
    # brand_terms NO viven aquí (fase objetiva): los marca el agente entity-curator
    # (fase 3) leyendo project.json -> brief.brand_terms.

    df = raw_df.copy()
    n0 = len(df)
    counts: dict[str, int] = {}

    def drop(mask: pd.Series, label: str) -> None:
        nonlocal df
        removed = int(mask.sum())
        if removed:
            counts[label] = removed
        df = df[~mask]

    df["canonical_entity"] = df["canonical_entity"].fillna("").astype(str)
    df["type"] = df["type"].fillna("unknown").astype(str)

    drop(df["canonical_entity"].str.strip() == "", "vacías")
    drop(df["type"].str.lower().isin(exclude_types), "tipo no-entidad")
    if min_salience > 0:
        drop(df["salience"].astype(float) < min_salience, "salience baja")
    if max_words > 0:
        word_count = df["canonical_entity"].str.split().map(len)
        drop(word_count > max_words, "frases largas")
    drop(df["canonical_entity"].isin(blocklist), "blocklist genéricos")

    # Reclasificar con la ontología (corrige tipados erróneos de Google).
    if not df.empty:
        df["type"] = df.apply(
            lambda r: _retype(r["canonical_entity"], r["type"], ontology),
            axis=1,
        )

    removed_total = n0 - len(df)
    print(f"Limpieza: {n0} -> {len(df)} menciones (-{removed_total})")
    for label, n in counts.items():
        print(f"  - {label}: -{n}")
    return df.reset_index(drop=True)


def _retype(canonical: str, current: str, ontology: dict) -> str:
    seo_type = classify_entity(canonical, ontology)
    if seo_type != "unknown":
        return seo_type
    return current


def clean_file(raw_csv: str | Path, out_csv: str | Path, config: dict) -> pd.DataFrame:
    raw_df = pd.read_csv(raw_csv)
    cleaned = clean(raw_df, config)
    ensure_parent(out_csv)
    cleaned.to_csv(out_csv, index=False)
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yml")
    parser.add_argument("--raw", default=None)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    output_cfg = config.get("output", {})
    raw_csv = args.raw or output_cfg.get("entities_raw_csv", "outputs/entities_raw.csv")
    out_csv = args.out or output_cfg.get("entities_csv", "outputs/entities.csv")
    cleaned = clean_file(raw_csv, out_csv, config)
    print(f"Wrote {len(cleaned)} cleaned entity mentions to {out_csv}")


if __name__ == "__main__":
    main()

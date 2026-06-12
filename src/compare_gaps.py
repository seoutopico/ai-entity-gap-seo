from __future__ import annotations

"""
Fase 5: detecta gaps de entidades (dato CUANTITATIVO -> script, determinista).

Un gap = entidad con demanda externa (external_entities.csv, ya filtrada por
territorio/anti-territorio en la fase 4) que NO está en el territorio curado
(entities_curated.csv). El cruce es matching exacto por canonical_entity.

  gap_type = "trending"    si rising == 1 (demanda al alza)
  gap_type = "consolidado" si rising == 0 (demanda establecida)

Produce projects/<id>/outputs/gaps.csv con las columnas EXACTAS del contrato
(ver projects/_template/outputs/gaps.csv). La priorización EDITORIAL de estos
gaps (cualitativa) es de la fase 6-7: agente gap-strategist.

Uso:
    python src/compare_gaps.py --project <id>
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from utils import ensure_parent, require_columns

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

GAPS_COLUMNS = ["canonical_entity", "gap_type", "rising", "score", "score_norm", "seeds", "source"]


def compare(external_csv: str | Path, curated_csv: str | Path, output_csv: str | Path) -> pd.DataFrame:
    external = pd.read_csv(external_csv)
    require_columns(external, ["canonical_entity", "score", "rising", "seeds", "source", "score_norm"], str(external_csv))
    curated = pd.read_csv(curated_csv)
    require_columns(curated, ["canonical_entity"], str(curated_csv))

    covered = set(curated["canonical_entity"].astype(str))
    gaps = external[~external["canonical_entity"].astype(str).isin(covered)].copy()
    gaps["gap_type"] = gaps["rising"].astype(int).map({1: "trending", 0: "consolidado"})
    gaps = gaps[GAPS_COLUMNS].sort_values(["rising", "score_norm"], ascending=False)

    ensure_parent(output_csv)
    gaps.to_csv(output_csv, index=False)
    return gaps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="id del proyecto (projects/<id>/)")
    args = parser.parse_args()

    out_dir = Path("projects") / args.project / "outputs"
    gaps = compare(out_dir / "external_entities.csv", out_dir / "entities_curated.csv", out_dir / "gaps.csv")
    counts = gaps["gap_type"].value_counts().to_dict()
    print(f"Gaps -> {out_dir / 'gaps.csv'} ({len(gaps)} entidades: {counts})")


if __name__ == "__main__":
    main()

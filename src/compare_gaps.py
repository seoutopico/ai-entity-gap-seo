from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from utils import canonicalize_entity, ensure_parent, load_config, minmax, read_optional_csv, require_columns


def _aggregate_internal(entities: pd.DataFrame) -> pd.DataFrame:
    return (
        entities.groupby(["canonical_entity", "type"], dropna=False)
        .agg(
            internal_posts=("url", "nunique"),
            internal_score=("score", "sum"),
            internal_mentions=("mentions", "sum"),
        )
        .reset_index()
    )


def _aggregate_external(external_entities: pd.DataFrame) -> pd.DataFrame:
    if external_entities.empty:
        return pd.DataFrame(columns=["canonical_entity", "external_posts", "external_score"])
    if "canonical_entity" not in external_entities.columns:
        if "entity" not in external_entities.columns:
            raise ValueError("external_entities must contain canonical_entity or entity")
        external_entities = external_entities.copy()
        external_entities["canonical_entity"] = external_entities["entity"].map(canonicalize_entity)
    url_col = "url" if "url" in external_entities.columns else None
    score_col = "score" if "score" in external_entities.columns else None
    grouped = external_entities.groupby("canonical_entity", dropna=False)
    result = grouped.size().reset_index(name="external_mentions")
    if url_col:
        result["external_posts"] = grouped[url_col].nunique().values
    else:
        result["external_posts"] = result["external_mentions"]
    if score_col:
        result["external_score"] = grouped[score_col].sum().values
    else:
        result["external_score"] = result["external_mentions"].astype(float)
    return result


def _entity_query_metrics(gsc_queries: pd.DataFrame, entities: pd.Series) -> pd.DataFrame:
    if gsc_queries.empty:
        return pd.DataFrame({"canonical_entity": entities, "gsc_impressions": 0.0, "gsc_clicks": 0.0, "gsc_avg_position": 0.0})
    require_columns(gsc_queries, ["query", "impressions"], "gsc_queries")
    gsc = gsc_queries.copy()
    gsc["query_norm"] = gsc["query"].map(canonicalize_entity)
    if "clicks" not in gsc.columns:
        gsc["clicks"] = 0.0
    if "position" not in gsc.columns:
        gsc["position"] = 0.0

    records = []
    for entity in entities:
        entity_norm = canonicalize_entity(entity)
        tokens = [token for token in entity_norm.split() if len(token) > 2]
        if not tokens:
            matched = gsc.iloc[0:0]
        else:
            mask = gsc["query_norm"].apply(lambda q: entity_norm in q or all(token in q for token in tokens))
            matched = gsc[mask]
        impressions = float(matched["impressions"].sum()) if not matched.empty else 0.0
        clicks = float(matched["clicks"].sum()) if not matched.empty else 0.0
        position = float(matched["position"].mean()) if not matched.empty else 0.0
        records.append({"canonical_entity": entity, "gsc_impressions": impressions, "gsc_clicks": clicks, "gsc_avg_position": position})
    return pd.DataFrame(records)


def compare(
    entities_csv: str | Path,
    output_gaps_csv: str | Path,
    output_backlog_csv: str | Path,
    config: dict,
    external_entities_csv: str | Path | None = None,
    gsc_queries_csv: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    entities = pd.read_csv(entities_csv)
    require_columns(entities, ["canonical_entity", "url", "score", "mentions", "type"], str(entities_csv))

    source_cfg = config.get("source", {})
    external_path = external_entities_csv or source_cfg.get("external_entities_csv", "data/raw/external_entities.csv")
    gsc_path = gsc_queries_csv or source_cfg.get("gsc_queries_csv", "data/raw/gsc_queries.csv")

    internal = _aggregate_internal(entities)
    external_entities = read_optional_csv(external_path)
    external = _aggregate_external(external_entities)

    all_entities = sorted(set(internal["canonical_entity"]) | set(external["canonical_entity"]))
    base = pd.DataFrame({"canonical_entity": all_entities})
    gaps = base.merge(internal, on="canonical_entity", how="left").merge(external, on="canonical_entity", how="left")
    gaps["type"] = gaps["type"].fillna("unknown")
    for col in ["internal_posts", "internal_score", "internal_mentions", "external_posts", "external_score", "external_mentions"]:
        if col not in gaps.columns:
            gaps[col] = 0.0
        gaps[col] = gaps[col].fillna(0.0)

    gsc = read_optional_csv(gsc_path)
    query_metrics = _entity_query_metrics(gsc, gaps["canonical_entity"])
    gaps = gaps.merge(query_metrics, on="canonical_entity", how="left")

    scoring_cfg = config.get("scoring", {})
    weights = scoring_cfg.get("weights", {})
    external_weight = float(weights.get("external", 0.45))
    gsc_weight = float(weights.get("search_console", 0.35))
    internal_gap_weight = float(weights.get("internal_gap", 0.20))

    gaps["external_norm"] = minmax(gaps["external_score"].astype(float))
    gaps["gsc_norm"] = minmax(gaps["gsc_impressions"].astype(float))
    gaps["internal_norm"] = minmax(gaps["internal_score"].astype(float))
    gaps["internal_gap_norm"] = 1.0 - gaps["internal_norm"]
    gaps["opportunity_score"] = (
        external_weight * gaps["external_norm"]
        + gsc_weight * gaps["gsc_norm"]
        + internal_gap_weight * gaps["internal_gap_norm"]
    ).round(4)

    shallow_threshold = int(scoring_cfg.get("shallow_post_threshold", 2))
    orphan_threshold = int(scoring_cfg.get("orphan_entity_threshold", 1))

    def gap_type(row: pd.Series) -> str:
        if row["internal_posts"] == 0 and (row["external_score"] > 0 or row["gsc_impressions"] > 0):
            return "absent_entity"
        if row["internal_posts"] <= orphan_threshold and row["external_score"] == 0 and row["gsc_impressions"] == 0:
            return "orphan_entity"
        if row["internal_posts"] < shallow_threshold and (row["external_score"] > 0 or row["gsc_impressions"] > 0):
            return "shallow_coverage"
        if row["gsc_impressions"] > 0 and row["gsc_clicks"] == 0:
            return "search_demand_no_clicks"
        return "covered_or_low_signal"

    gaps["gap_type"] = gaps.apply(gap_type, axis=1)
    high = float(scoring_cfg.get("opportunity_thresholds", {}).get("high", 0.70))
    medium = float(scoring_cfg.get("opportunity_thresholds", {}).get("medium", 0.40))

    def priority(score: float) -> str:
        if score >= high:
            return "high"
        if score >= medium:
            return "medium"
        return "low"

    gaps["priority"] = gaps["opportunity_score"].map(priority)
    gaps = gaps.sort_values(["opportunity_score", "external_score", "gsc_impressions"], ascending=False)

    backlog = gaps[gaps["gap_type"].isin(["absent_entity", "shallow_coverage", "search_demand_no_clicks"])].copy()
    backlog["recommended_action"] = backlog["gap_type"].map(
        {
            "absent_entity": "Crear pieza evergreen o sección pilar si encaja con el territorio editorial.",
            "shallow_coverage": "Actualizar posts existentes con definición, ejemplos, enlaces internos y entidad relacionada.",
            "search_demand_no_clicks": "Revisar title/intro/estructura e intención de búsqueda; crear respuesta más directa.",
        }
    )
    backlog["working_title"] = backlog["canonical_entity"].apply(lambda e: f"Guía práctica: {e}")

    ensure_parent(output_gaps_csv)
    gaps.to_csv(output_gaps_csv, index=False)
    ensure_parent(output_backlog_csv)
    backlog.to_csv(output_backlog_csv, index=False)
    return gaps, backlog


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yml")
    parser.add_argument("--entities", default=None)
    parser.add_argument("--external-entities", default=None)
    parser.add_argument("--gsc", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    output_cfg = config.get("output", {})
    entities_csv = args.entities or output_cfg.get("entities_csv", "outputs/entities.csv")
    gaps_csv = output_cfg.get("gaps_csv", "outputs/gaps.csv")
    backlog_csv = output_cfg.get("editorial_backlog_csv", "outputs/editorial_backlog.csv")
    gaps, backlog = compare(entities_csv, gaps_csv, backlog_csv, config, args.external_entities, args.gsc)
    print(f"Wrote {len(gaps)} gaps to {gaps_csv}")
    print(f"Wrote {len(backlog)} backlog items to {backlog_csv}")


if __name__ == "__main__":
    main()

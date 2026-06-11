from __future__ import annotations

"""
Descubre demanda de búsqueda alrededor de tus entidades usando Google Trends
(related_queries + related_topics) vía trendspy.

- "top"    -> términos consolidados que la gente busca alrededor de la entidad.
- "rising" -> términos en tendencia ascendente (señal de oportunidad temprana).

Produce:
  data/raw/trends_related.csv          (cache acumulativo, crudo por término)
  data/processed/external_entities.csv (demanda agregada para compare_gaps.py)

NO reconsulta semillas que ya están en el cache, para no abusar de Trends
(que rate-limita con 429). Sube `max_seeds` poco a poco entre ejecuciones.

Uso:
    python src/fetch_trends.py --config config/config.yml
    python src/fetch_trends.py --config config/config.yml --max-seeds 5
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

from utils import canonicalize_entity, ensure_parent, load_config, load_project_config, minmax, read_optional_csv

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

CACHE_COLUMNS = ["seed", "seed_type", "kind", "rank", "term", "term_norm", "value"]


def select_seeds(entities: pd.DataFrame, trends_cfg: dict) -> pd.DataFrame:
    """Elige las entidades más relevantes como semilla para Trends."""
    seed_types = set(trends_cfg.get("seed_types", []))
    min_sal = float(trends_cfg.get("seed_min_salience", 0.0))
    max_seeds = int(trends_cfg.get("max_seeds", 15))

    df = entities.copy()
    df["has_mid"] = df.get("mid", "").fillna("").astype(str).str.len() > 0

    if "salience_sum" in df.columns:
        # entities_curated.csv: ya agregado por entidad (territorio decidido por el agente).
        agg = df.copy()
        agg["sal_sum"] = agg["salience_sum"].astype(float)
        if "posts" not in agg.columns:
            agg["posts"] = 0
    else:
        # entities.csv crudo de menciones: agregar por entidad.
        df = df[df["type"].fillna("") != "brand"]
        agg = (
            df.groupby("canonical_entity")
            .agg(
                sal_sum=("salience", "sum"),
                posts=("url", "nunique"),
                type=("type", "first"),
                has_mid=("has_mid", "any"),
            )
            .reset_index()
        )

    agg = agg[agg["type"].fillna("") != "brand"]
    # Semilla = está en el Knowledge Graph (dato OBJETIVO: tiene mid) o es de un tipo
    # nombrado/estratégico. Los genéricos 'other' (contenido, datos, sistema...) sin mid
    # quedan fuera solos. El criterio cualitativo de territorio ya lo puso el agente.
    mask = (agg["has_mid"] | agg["type"].isin(seed_types)) & (agg["sal_sum"] >= min_sal)
    agg = agg[mask].sort_values(["sal_sum", "posts"], ascending=False)
    return agg.head(max_seeds)


def _extract_pairs(obj) -> list[tuple[str, float]]:
    """Normaliza el resultado de related_* (DataFrame) a [(texto, value)]."""
    if obj is None:
        return []
    if not isinstance(obj, pd.DataFrame) or obj.empty:
        return []
    text_col = next((c for c in ["query", "topic_title", "title", "term", "name"] if c in obj.columns), None)
    if text_col is None:
        text_col = obj.columns[0]
    val_col = "value" if "value" in obj.columns else None
    pairs = []
    for _, row in obj.iterrows():
        term = str(row[text_col]).strip()
        value = float(row[val_col]) if val_col and pd.notna(row[val_col]) else 0.0
        if term:
            pairs.append((term, value))
    return pairs


def fetch_for_seed(tr, seed: str, trends_cfg: dict) -> list[dict]:
    """Consulta related_queries (+topics) para una semilla y devuelve registros."""
    geo = trends_cfg.get("geo", "")
    timeframe = trends_cfg.get("timeframe", "today 12-m")
    headers = {"referer": trends_cfg.get("referer", "https://www.google.com/")}
    fetch_topics = bool(trends_cfg.get("fetch_topics", True))

    records: list[dict] = []

    def collect(result, kind: str) -> None:
        if not isinstance(result, dict):
            return
        for rank in ("top", "rising"):
            for term, value in _extract_pairs(result.get(rank)):
                records.append(
                    {
                        "seed": seed,
                        "kind": kind,
                        "rank": rank,
                        "term": term,
                        "term_norm": canonicalize_entity(term),
                        "value": value,
                    }
                )

    rq = tr.related_queries(seed, geo=geo, timeframe=timeframe, headers=headers)
    collect(rq, "query")
    if fetch_topics:
        rt = tr.related_topics(seed, geo=geo, timeframe=timeframe, headers=headers)
        collect(rt, "topic")
    return records


def _tokens(text: str) -> set[str]:
    return {t for t in canonicalize_entity(str(text)).split() if len(t) >= 2}


def _territory_tokens(curated: pd.DataFrame, brief: dict) -> set[str]:
    """Léxico del territorio: tokens de las entidades curadas + entidades_nucleo del brief."""
    toks: set[str] = set()
    for e in curated.get("canonical_entity", pd.Series(dtype=str)).astype(str):
        toks |= _tokens(e)
    for e in brief.get("entidades_nucleo", []):
        toks |= _tokens(str(e))
    return toks


def _anti_tokens(brief: dict) -> set[str]:
    """Tokens de los SENTIDOS a excluir (lado derecho de 'X = sentido'), sin paréntesis."""
    toks: set[str] = set()
    items = brief.get("anti_territorio_inicial", []) + brief.get("anti_territorio_detectado", [])
    for item in items:
        right = item.split("=", 1)[1] if "=" in item else item
        right = re.sub(r"\(.*?\)", " ", right)  # quita la explicación entre paréntesis
        toks |= {t for t in _tokens(right) if len(t) >= 3}
    return toks


def filter_relevant(df: pd.DataFrame, territory: set[str], anti: set[str]) -> pd.DataFrame:
    """Relevante = comparte vocabulario con el territorio y NO cae en el anti_territorio."""
    def keep(term: str) -> bool:
        tk = _tokens(term)
        return bool(tk & territory) and not (tk & anti)
    return df[df["canonical_entity"].map(keep)].copy()


def normalize_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza 0-1 por separado dentro de rising y de top (escalas no comparables)."""
    df = df.copy()
    df["score_norm"] = 0.0
    for flag in (0, 1):
        mask = df["rising"] == flag
        if mask.any():
            df.loc[mask, "score_norm"] = minmax(df.loc[mask, "score"].astype(float)).round(4)
    return df


def build_external_entities(cache: pd.DataFrame) -> pd.DataFrame:
    """Agrega los términos de Trends en demanda externa para compare_gaps."""
    if cache.empty:
        return pd.DataFrame(columns=["canonical_entity", "score", "source", "rising"])
    df = cache[cache["term_norm"].str.len() >= 2].copy()
    df["rising_flag"] = (df["rank"] == "rising").astype(int)
    grouped = (
        df.groupby("term_norm")
        .agg(score=("value", "max"), rising=("rising_flag", "max"), seeds=("seed", "nunique"))
        .reset_index()
        .rename(columns={"term_norm": "canonical_entity"})
    )
    grouped["source"] = "google_trends"
    return grouped.sort_values(["rising", "score"], ascending=False)


def run(config: dict, project: str | None = None, entities_csv: str | Path | None = None, max_seeds_override: int | None = None) -> pd.DataFrame:
    trends_cfg = config.get("trends", {})
    if not trends_cfg.get("enabled", True):
        print("trends.enabled=false; nada que hacer.")
        return pd.DataFrame()
    if max_seeds_override is not None:
        trends_cfg = {**trends_cfg, "max_seeds": max_seeds_override}

    output_cfg = config.get("output", {})
    if project:
        # Modo proyecto: consume el territorio curado y escribe dentro del proyecto.
        pdir = Path("projects") / project
        entities_path = entities_csv or str(pdir / "outputs/entities_curated.csv")
        cache_path = str(pdir / "outputs/trends_related.csv")
        external_path = str(pdir / "outputs/external_entities.csv")
    else:
        entities_path = entities_csv or output_cfg.get("entities_csv", "outputs/entities.csv")
        cache_path = trends_cfg.get("cache_csv", "data/raw/trends_related.csv")
        external_path = config.get("source", {}).get("external_entities_csv", "data/raw/external_entities.csv")
    delay = float(trends_cfg.get("request_delay", 4.0))

    entities = pd.read_csv(entities_path)
    seeds = select_seeds(entities, trends_cfg)
    print(f"Semillas seleccionadas: {len(seeds)} -> {', '.join(seeds['canonical_entity'].head(20))}")

    cache = read_optional_csv(cache_path)
    if cache.empty:
        cache = pd.DataFrame(columns=CACHE_COLUMNS)
    done_seeds = set(cache["seed"].unique()) if "seed" in cache.columns else set()

    from trendspy import Trends

    tr = Trends(hl=trends_cfg.get("hl", "es-ES"), tz=60, request_delay=delay)

    new_records: list[dict] = []
    pending = [s for s in seeds["canonical_entity"] if s not in done_seeds]
    print(f"{len(pending)} semillas nuevas (cache: {len(done_seeds)} ya hechas).")

    seed_type_map = dict(zip(seeds["canonical_entity"], seeds["type"]))
    for i, seed in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] Trends: '{seed}'")
        try:
            recs = fetch_for_seed(tr, seed, trends_cfg)
            for r in recs:
                r["seed_type"] = seed_type_map.get(seed, "")
            new_records.extend(recs)
            print(f"    +{len(recs)} términos")
        except Exception as e:  # rate limit u otros -> salta, reintentable luego
            print(f"    ⚠️  fallo en '{seed}': {type(e).__name__} {str(e)[:120]} (reintentable)")
        if i < len(pending):
            time.sleep(delay)

    if new_records:
        cache = pd.concat([cache, pd.DataFrame(new_records)], ignore_index=True)
        cache = cache.drop_duplicates(subset=["seed", "kind", "rank", "term"], keep="last")
        ensure_parent(cache_path)
        cache.to_csv(cache_path, index=False)
        print(f"Cache actualizado: {cache_path} ({len(cache)} filas)")

    external = build_external_entities(cache)

    # Filtro de relevancia (solo en modo proyecto): usa el territorio + anti_territorio
    # que el agente ya decidió. El script solo APLICA el matching (objetivo).
    if project:
        brief = {}
        pj = Path("projects") / project / "project.json"
        if pj.exists():
            brief = json.loads(pj.read_text(encoding="utf-8")).get("brief", {})
        curated = pd.read_csv(entities_path)
        territory = _territory_tokens(curated, brief)
        anti = _anti_tokens(brief)
        raw_path = str(Path(external_path).with_name("external_entities_raw.csv"))
        ensure_parent(raw_path)
        external.to_csv(raw_path, index=False)  # crudo, para auditar
        before = len(external)
        external = normalize_scores(filter_relevant(external, territory, anti))
        external = external.sort_values(["rising", "score_norm"], ascending=False)
        print(f"Filtro de relevancia: {before} -> {len(external)} términos (territorio {len(territory)} tokens, anti {len(anti)})")

    ensure_parent(external_path)
    external.to_csv(external_path, index=False)
    print(f"Demanda externa -> {external_path} ({len(external)} entidades)")
    return external


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yml")
    parser.add_argument("--project", default=None, help="id del proyecto (projects/<id>/)")
    parser.add_argument("--entities", default=None)
    parser.add_argument("--max-seeds", type=int, default=None)
    args = parser.parse_args()

    config = load_project_config(args.config, args.project)
    run(config, project=args.project, entities_csv=args.entities, max_seeds_override=args.max_seeds)


if __name__ == "__main__":
    main()

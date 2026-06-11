from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

# La consola de Windows usa cp1252 por defecto y rompe con emojis/acentos.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv is optional; env vars can also be set by the shell
    def load_dotenv(*_args, **_kwargs):  # type: ignore
        return False

from utils import (
    canonicalize_entity,
    classify_entity,
    ensure_parent,
    load_config,
    load_project_config,
    require_columns,
)

GCP_NL_ENDPOINT = "https://language.googleapis.com/{version}/documents:analyzeEntities"


class MissingApiKeyError(RuntimeError):
    """Raised when the Google NL API key is not available."""


def _current_month() -> str:
    return datetime.now().strftime("%Y-%m")


def _load_usage(path: str | Path) -> dict:
    """Carga el consumo acumulado; resetea si ha cambiado el mes."""
    p = Path(path)
    month = _current_month()
    default = {"month": month, "units": 0, "chars": 0, "requests": 0}
    if not p.exists():
        return default
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default
    if data.get("month") != month:  # mes nuevo -> contador a cero
        return default
    return {
        "month": month,
        "units": int(data.get("units", 0)),
        "chars": int(data.get("chars", 0)),
        "requests": int(data.get("requests", 0)),
    }


def _save_usage(path: str | Path, usage: dict) -> None:
    p = ensure_parent(path)
    p.write_text(json.dumps(usage, ensure_ascii=False, indent=2), encoding="utf-8")


def _doc_units(text: str) -> int:
    """Unidades facturables de un documento (Google redondea al alza por 1.000 chars)."""
    return max(1, math.ceil(len(text) / 1000))


def _get_api_key(config: dict) -> str:
    load_dotenv()
    extraction_cfg = config.get("extraction", {})
    env_var = extraction_cfg.get("api_key_env", "GOOGLE_NL_API_KEY")
    key = os.getenv(env_var, "").strip()
    if not key:
        raise MissingApiKeyError(
            f"No Google NL API key found. Set {env_var} in your .env file "
            f"(see .env.example)."
        )
    return key


def analyze_entities_gcp(
    text: str,
    api_key: str,
    *,
    language: str = "es",
    version: str = "v1",
    timeout: int = 30,
    max_retries: int = 3,
) -> list[dict]:
    """Call Google Cloud Natural Language analyzeEntities and return raw entities."""
    if not text.strip():
        return []

    document: dict = {"type": "PLAIN_TEXT", "content": text}
    if language:
        document["language"] = language
    payload = {"document": document, "encodingType": "UTF8"}
    url = GCP_NL_ENDPOINT.format(version=version)

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url, params={"key": api_key}, json=payload, timeout=timeout
            )
            if response.status_code == 200:
                return response.json().get("entities", [])
            # Retry on transient server / rate-limit errors; fail fast otherwise.
            if response.status_code in (429, 500, 503):
                last_error = RuntimeError(
                    f"Google NL API {response.status_code}: {response.text[:300]}"
                )
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(
                f"Google NL API error {response.status_code}: {response.text[:500]}"
            )
        except requests.RequestException as exc:  # network-level errors
            last_error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Google NL API failed after {max_retries} retries: {last_error}")


def _entities_for_posts(posts: pd.DataFrame, config: dict) -> pd.DataFrame:
    extraction_cfg = config.get("extraction", {})
    language = extraction_cfg.get("language", "es")
    version = extraction_cfg.get("api_version", "v1")
    timeout = int(extraction_cfg.get("request_timeout", 30))
    include_title = bool(extraction_cfg.get("include_title", True))
    min_salience = float(extraction_cfg.get("min_salience", 0.0))
    require_kg = bool(extraction_cfg.get("require_kg_mid", False))
    min_chars = int(extraction_cfg.get("min_entity_chars", 2))
    # Topes duros de coste por ejecución (0 = sin límite).
    max_requests = int(extraction_cfg.get("max_requests", 0))
    max_chars = int(extraction_cfg.get("max_chars", 0))
    # Tope ABSOLUTO mensual acumulado (capa gratuita = 5.000 unidades/mes).
    monthly_unit_cap = int(extraction_cfg.get("monthly_unit_cap", 5000))
    usage_file = extraction_cfg.get("usage_file", ".usage/nl_usage.json")

    api_key = _get_api_key(config)
    ontology = config.get("ontology", {})

    usage = _load_usage(usage_file)
    print(
        f"📊 Consumo del mes {usage['month']}: {usage['units']}/{monthly_unit_cap} "
        f"unidades usadas ({usage['requests']} peticiones)."
    )

    records: list[dict] = []
    requests_made = 0
    chars_sent = 0
    total = len(posts)
    for row_index, post in posts.reset_index(drop=True).iterrows():
        title = str(post.get("title", "") or "")
        body = str(post.get("text", "") or "")
        content = f"{title}. {body}".strip() if include_title else body

        doc_units = _doc_units(content)

        # --- Topes de coste: detenerse ANTES de enviar si se superaría algún límite ---
        if monthly_unit_cap and usage["units"] + doc_units > monthly_unit_cap:
            print(
                f"🛑 TOPE MENSUAL alcanzado: {usage['units']}/{monthly_unit_cap} unidades "
                f"este mes ({usage['month']}). No se envía nada más para no salir de la capa "
                f"gratuita. Procesados {row_index}/{total} posts."
            )
            break
        if max_requests and requests_made >= max_requests:
            print(
                f"⚠️  Tope de peticiones por ejecución alcanzado (max_requests={max_requests}). "
                f"Procesados {row_index}/{total} posts. Deteniendo extracción."
            )
            break
        if max_chars and chars_sent + len(content) > max_chars:
            print(
                f"⚠️  Tope de caracteres por ejecución alcanzado (max_chars={max_chars}, "
                f"acumulado={chars_sent}). Saltando el resto. Procesados {row_index}/{total} posts."
            )
            break

        print(f"[{row_index + 1}/{total}] Analyzing: {title[:60]}")
        entities = analyze_entities_gcp(
            content, api_key, language=language, version=version, timeout=timeout
        )
        requests_made += 1
        chars_sent += len(content)
        # Persistir el consumo TRAS cada petición (seguro ante cortes/crashes).
        usage["units"] += doc_units
        usage["chars"] += len(content)
        usage["requests"] += 1
        _save_usage(usage_file, usage)
        for ent in entities:
            name = str(ent.get("name", "")).strip()
            canonical = canonicalize_entity(name)
            if len(canonical) < min_chars:
                continue
            salience = float(ent.get("salience", 0.0))
            if salience < min_salience:
                continue
            metadata = ent.get("metadata", {}) or {}
            mid = metadata.get("mid", "")
            wikipedia_url = metadata.get("wikipedia_url", "")
            if require_kg and not mid:
                continue
            google_type = str(ent.get("type", "OTHER"))
            # Strategic SEO type wins via ontology, else fall back to Google's type.
            seo_type = classify_entity(canonical, ontology)
            entity_type = seo_type if seo_type != "unknown" else google_type.lower()
            mentions = len(ent.get("mentions", []) or [])

            records.append(
                {
                    "url": post.get("url", ""),
                    "title": title,
                    "published": post.get("published", ""),
                    "entity": name,
                    "canonical_entity": canonical,
                    "type": entity_type,
                    "google_type": google_type,
                    "score": round(salience, 6),
                    "salience": round(salience, 6),
                    "mentions": int(max(mentions, 1)),
                    "mid": mid,
                    "wikipedia_url": wikipedia_url,
                }
            )

    print(
        f"💰 Esta ejecución: {requests_made} peticiones, {chars_sent} caracteres. "
        f"Acumulado del mes {usage['month']}: {usage['units']}/{monthly_unit_cap} "
        f"unidades (capa gratuita)."
    )
    return pd.DataFrame(records)


def extract(input_csv: str | Path, output_csv: str | Path, config: dict) -> pd.DataFrame:
    from clean_entities import clean as clean_entities_df

    posts = pd.read_csv(input_csv)
    require_columns(posts, ["url", "title", "text"], str(input_csv))
    entities = _entities_for_posts(posts, config)

    # Guardar el crudo (cache para iterar filtros sin volver a llamar la API).
    out_path = Path(output_csv)
    raw_path = out_path.with_name(f"{out_path.stem}_raw{out_path.suffix}")
    ensure_parent(raw_path)
    entities.to_csv(raw_path, index=False)

    # Aplicar la capa de limpieza configurable -> salida final.
    cleaned = clean_entities_df(entities, config)
    ensure_parent(output_csv)
    cleaned.to_csv(output_csv, index=False)
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yml")
    parser.add_argument("--project", default=None, help="id del proyecto (projects/<id>/)")
    parser.add_argument("--input", default=None)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    config = load_project_config(args.config, args.project)
    if args.project:
        pdir = f"projects/{args.project}"
        input_csv = args.input or f"{pdir}/data/raw/posts.csv"
        output_csv = args.out or f"{pdir}/outputs/entities.csv"
    else:
        input_csv = args.input or config.get("output", {}).get("posts_csv", "data/processed/posts.csv")
        output_csv = args.out or config.get("output", {}).get("entities_csv", "outputs/entities.csv")
    entities = extract(input_csv, output_csv, config)
    print(f"Wrote {len(entities)} entity mentions to {output_csv}")


if __name__ == "__main__":
    main()

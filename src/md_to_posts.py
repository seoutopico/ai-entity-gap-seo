from __future__ import annotations

"""
Convierte notas Markdown de la newsletter (con frontmatter YAML) en data/raw/posts.csv.

Uso:
    python src/md_to_posts.py ruta/al/post.md [otro_post.md ...] --out data/raw/posts.csv
    python src/md_to_posts.py "carpeta/publicadas/*.md" --out data/raw/posts.csv
"""

import argparse
import glob
import re
from pathlib import Path

import pandas as pd
import yaml


def split_frontmatter(raw: str) -> tuple[dict, str]:
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            return meta, parts[2]
    return {}, raw


def markdown_to_text(body: str) -> str:
    # Quitar imágenes: ![alt](url) y la variante enlazada [![..](..)](..)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    # Enlaces [texto](url) -> texto
    body = re.sub(r"\[([^\]]*)\]\(<?[^)]*>?\)", r"\1", body)
    # Encabezados, énfasis, separadores, comillas de bloque
    body = re.sub(r"^#{1,6}\s*", "", body, flags=re.MULTILINE)
    body = body.replace("**", "").replace("*", "").replace("_", "")
    body = re.sub(r"^\s*\*\s*\*\s*\*\s*$", " ", body, flags=re.MULTILINE)
    body = re.sub(r"^\s*>\s?", "", body, flags=re.MULTILINE)
    # Normalizar espacios
    return " ".join(body.split())


def parse_md(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)
    return {
        "url": meta.get("url", str(path)),
        "title": meta.get("title", path.stem),
        "published": str(meta.get("date", "")),
        "text": markdown_to_text(body),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="Archivos .md o patrones glob")
    ap.add_argument("--out", default="data/raw/posts.csv")
    args = ap.parse_args()

    files: list[Path] = []
    for item in args.inputs:
        matched = glob.glob(item)
        files.extend(Path(p) for p in matched) if matched else files.append(Path(item))

    rows = [parse_md(f) for f in files if f.exists()]
    if not rows:
        raise SystemExit("No se encontraron archivos .md válidos.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=["url", "title", "published", "text"]).to_csv(out, index=False, encoding="utf-8")
    print(f"Escrito {out} con {len(rows)} post(s).")
    for r in rows:
        print(f"  - {r['title'][:60]}  ({len(r['text'])} chars)")


if __name__ == "__main__":
    main()

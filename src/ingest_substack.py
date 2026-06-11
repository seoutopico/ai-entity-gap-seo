from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from utils import ensure_parent, load_config


def html_to_text(html: str) -> str:
    if BeautifulSoup is None:
        import re
        text = re.sub(r"<[^>]+>", " ", html or "")
        return " ".join(text.split())
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return " ".join(soup.get_text(" ").split())


def entry_text(entry: object) -> tuple[str, str]:
    html_parts: list[str] = []
    if hasattr(entry, "content"):
        for content_item in getattr(entry, "content", []):
            value = content_item.get("value") if isinstance(content_item, dict) else None
            if value:
                html_parts.append(value)
    summary = getattr(entry, "summary", "")
    if summary:
        html_parts.append(summary)
    html = "\n".join(html_parts)
    return html, html_to_text(html)


def ingest(feed_url: str, out_path: str | Path, limit: int | None = None) -> pd.DataFrame:
    if not feed_url:
        raise ValueError("source.substack_feed_url is empty. Add it to config or use --skip-ingest.")
    try:
        import feedparser
    except ImportError as exc:
        raise RuntimeError("feedparser is required for RSS ingest. Install requirements.txt or run with --skip-ingest.") from exc
    parsed = feedparser.parse(feed_url)
    if parsed.bozo and not parsed.entries:
        raise RuntimeError(f"Could not parse feed: {feed_url}")

    records = []
    entries = parsed.entries[:limit] if limit else parsed.entries
    for entry in entries:
        html, text = entry_text(entry)
        records.append(
            {
                "url": getattr(entry, "link", ""),
                "title": getattr(entry, "title", ""),
                "published": getattr(entry, "published", ""),
                "html": html,
                "text": text,
            }
        )
    df = pd.DataFrame(records)
    ensure_parent(out_path)
    df.to_csv(out_path, index=False)
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yml")
    parser.add_argument("--feed-url", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    feed_url = args.feed_url or config.get("source", {}).get("substack_feed_url", "")
    out_path = args.out or config.get("output", {}).get("posts_csv", "data/processed/posts.csv")
    df = ingest(feed_url, out_path, args.limit)
    print(f"Wrote {len(df)} posts to {out_path}")


if __name__ == "__main__":
    main()

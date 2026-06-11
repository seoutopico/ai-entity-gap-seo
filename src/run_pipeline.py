from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from build_graph import build_graph, write_obsidian, write_pyvis
from compare_gaps import compare
from extract_entities import extract
from ingest_substack import ingest
from utils import ensure_parent, load_config

import networkx as nx
import pandas as pd


def copy_csv(src: str | Path, dst: str | Path) -> None:
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {src_path}")
    ensure_parent(dst)
    shutil.copyfile(src_path, dst)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yml")
    parser.add_argument("--skip-ingest", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    source_cfg = config.get("source", {})
    output_cfg = config.get("output", {})

    processed_posts = output_cfg.get("posts_csv", "data/processed/posts.csv")
    if args.skip_ingest:
        copy_csv(source_cfg.get("posts_csv", "data/raw/posts.csv"), processed_posts)
        print(f"Copied source posts to {processed_posts}")
    else:
        ingest(source_cfg.get("substack_feed_url", ""), processed_posts, limit=args.limit)

    entities_csv = output_cfg.get("entities_csv", "outputs/entities.csv")
    extract(processed_posts, entities_csv, config)

    external_entities_path = source_cfg.get("external_entities_csv", "data/raw/external_entities.csv")
    external_posts_path = Path(source_cfg.get("external_posts_csv", "data/raw/external_posts.csv"))
    if not Path(external_entities_path).exists() and external_posts_path.exists():
        external_entities_path = "data/processed/external_entities.csv"
        extract(external_posts_path, external_entities_path, config)
        print(f"Extracted external entities to {external_entities_path}")

    post_edges, entity_edges, graph = build_graph(processed_posts, entities_csv, config)
    post_edges_path = output_cfg.get("post_entity_edges_csv", "outputs/post_entity_edges.csv")
    entity_edges_path = output_cfg.get("entity_edges_csv", "outputs/entity_edges.csv")
    graphml_path = output_cfg.get("graph_graphml", "outputs/graph.graphml")

    ensure_parent(post_edges_path)
    post_edges.to_csv(post_edges_path, index=False)
    ensure_parent(entity_edges_path)
    entity_edges.to_csv(entity_edges_path, index=False)
    ensure_parent(graphml_path)
    nx.write_graphml(graph, graphml_path)
    write_obsidian(processed_posts, entities_csv, output_cfg.get("obsidian_dir", "outputs/obsidian"))
    write_pyvis(graph, str(Path(graphml_path).with_suffix(".html")))

    compare(
        entities_csv,
        output_cfg.get("gaps_csv", "outputs/gaps.csv"),
        output_cfg.get("editorial_backlog_csv", "outputs/editorial_backlog.csv"),
        config,
        external_entities_csv=external_entities_path,
        gsc_queries_csv=source_cfg.get("gsc_queries_csv", "data/raw/gsc_queries.csv"),
    )
    print("Pipeline completed")


if __name__ == "__main__":
    main()

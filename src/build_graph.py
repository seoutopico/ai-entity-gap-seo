from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx
import pandas as pd
try:
    from pyvis.network import Network
except ImportError:  # optional dependency for interactive HTML graphs
    Network = None

from utils import ensure_parent, load_config, require_columns, slugify


def build_graph(posts_csv: str | Path, entities_csv: str | Path, config: dict) -> tuple[pd.DataFrame, pd.DataFrame, nx.Graph]:
    posts = pd.read_csv(posts_csv)
    entities = pd.read_csv(entities_csv)
    require_columns(posts, ["url", "title", "text"], str(posts_csv))
    require_columns(entities, ["url", "canonical_entity", "score", "mentions", "type"], str(entities_csv))

    graph = nx.Graph()
    post_edges = []

    for _, post in posts.iterrows():
        post_id = f"post::{post['url']}"
        graph.add_node(
            post_id,
            label=post.get("title", post.get("url", "")),
            node_type="post",
            url=post.get("url", ""),
            published=post.get("published", ""),
        )

    entity_summary = (
        entities.groupby(["canonical_entity", "type"], dropna=False)
        .agg(total_score=("score", "sum"), total_mentions=("mentions", "sum"), post_count=("url", "nunique"))
        .reset_index()
    )
    for _, entity in entity_summary.iterrows():
        entity_id = f"entity::{entity['canonical_entity']}"
        graph.add_node(
            entity_id,
            label=entity["canonical_entity"],
            node_type="entity",
            entity_type=entity.get("type", "unknown"),
            total_score=float(entity.get("total_score", 0.0)),
            total_mentions=int(entity.get("total_mentions", 0)),
            post_count=int(entity.get("post_count", 0)),
        )

    for _, row in entities.iterrows():
        post_id = f"post::{row['url']}"
        entity_id = f"entity::{row['canonical_entity']}"
        graph.add_edge(post_id, entity_id, relation="mentions", weight=float(row.get("score", 0.0)))
        post_edges.append(
            {
                "source": row["url"],
                "target": row["canonical_entity"],
                "relation": "mentions",
                "weight": float(row.get("score", 0.0)),
            }
        )

    cooccurrence: Counter[tuple[str, str]] = Counter()
    for _, group in entities.groupby("url"):
        unique_entities = sorted(set(group["canonical_entity"].dropna().astype(str)))
        for left, right in combinations(unique_entities, 2):
            cooccurrence[(left, right)] += 1

    entity_edges = []
    for (left, right), weight in cooccurrence.items():
        left_id = f"entity::{left}"
        right_id = f"entity::{right}"
        graph.add_edge(left_id, right_id, relation="cooccurs", weight=int(weight))
        entity_edges.append({"source": left, "target": right, "relation": "cooccurs", "weight": int(weight)})

    return pd.DataFrame(post_edges), pd.DataFrame(entity_edges), graph


def write_obsidian(posts_csv: str | Path, entities_csv: str | Path, output_dir: str | Path) -> None:
    posts = pd.read_csv(posts_csv)
    entities = pd.read_csv(entities_csv)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for canonical, group in entities.groupby("canonical_entity"):
        entity_type = group["type"].iloc[0] if "type" in group.columns else "unknown"
        related_posts = group[["title", "url"]].drop_duplicates().to_dict("records")
        lines = [f"# {canonical}", "", f"Tipo: {entity_type}", "", "## Posts", ""]
        for post in related_posts:
            lines.append(f"- [{post['title']}]({post['url']})")
        lines.extend(["", "## Gaps a revisar", "", "- [ ] ¿Está explicada o solo mencionada?", "- [ ] ¿Tiene enlaces internos suficientes?", "- [ ] ¿Existe una pieza evergreen dedicada?", ""])
        (out_dir / f"entity-{slugify(canonical)}.md").write_text("\n".join(lines), encoding="utf-8")

    for _, post in posts.iterrows():
        post_entities = entities[entities["url"] == post["url"]]["canonical_entity"].drop_duplicates().tolist()
        lines = [f"# {post['title']}", "", f"URL: {post['url']}", f"Fecha: {post.get('published', '')}", "", "## Entidades", ""]
        for entity in post_entities:
            lines.append(f"- [[entity-{slugify(entity)}|{entity}]]")
        lines.extend(["", "## Diagnóstico", "", "- [ ] Intención de búsqueda clara", "- [ ] Entidades principales cubiertas en profundidad", "- [ ] Enlaces internos hacia piezas pilar", ""])
        (out_dir / f"post-{slugify(str(post['title']))}.md").write_text("\n".join(lines), encoding="utf-8")


def write_pyvis(graph: nx.Graph, html_path: str | Path) -> None:
    if Network is None:
        return
    net = Network(height="750px", width="100%", notebook=False)
    for node_id, data in graph.nodes(data=True):
        title = "\n".join(f"{k}: {v}" for k, v in data.items())
        group = data.get("node_type", "unknown")
        net.add_node(node_id, label=str(data.get("label", node_id))[:80], title=title, group=group)
    for source, target, data in graph.edges(data=True):
        net.add_edge(source, target, value=float(data.get("weight", 1)), title=data.get("relation", ""))
    ensure_parent(html_path)
    net.write_html(str(html_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yml")
    parser.add_argument("--posts", default=None)
    parser.add_argument("--entities", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    output_cfg = config.get("output", {})
    posts_csv = args.posts or output_cfg.get("posts_csv", "data/processed/posts.csv")
    entities_csv = args.entities or output_cfg.get("entities_csv", "outputs/entities.csv")

    post_edges, entity_edges, graph = build_graph(posts_csv, entities_csv, config)
    post_edges_path = output_cfg.get("post_entity_edges_csv", "outputs/post_entity_edges.csv")
    entity_edges_path = output_cfg.get("entity_edges_csv", "outputs/entity_edges.csv")
    graphml_path = output_cfg.get("graph_graphml", "outputs/graph.graphml")
    obsidian_dir = output_cfg.get("obsidian_dir", "outputs/obsidian")

    ensure_parent(post_edges_path)
    post_edges.to_csv(post_edges_path, index=False)
    ensure_parent(entity_edges_path)
    entity_edges.to_csv(entity_edges_path, index=False)
    ensure_parent(graphml_path)
    nx.write_graphml(graph, graphml_path)
    write_obsidian(posts_csv, entities_csv, obsidian_dir)
    write_pyvis(graph, str(Path(graphml_path).with_suffix(".html")))
    print(f"Wrote graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")


if __name__ == "__main__":
    main()

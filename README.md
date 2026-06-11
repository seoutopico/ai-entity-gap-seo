# Think & Hack Entity Gap MVP

MVP para analizar oportunidades SEO/GEO mediante entidades de contenido, grafos, scripts reproducibles y Claude Code.

## Objetivo

Convertir el archivo de una newsletter de Substack en un sistema auditable que detecta:

- Entidades cubiertas por tu contenido.
- Entidades ausentes o superficiales frente a competidores/SERPs.
- Clusters temáticos débiles.
- Posts huérfanos o mal conectados.
- Oportunidades editoriales priorizadas por impacto SEO.

## Flujo MVP

```text
Substack RSS / CSV
    -> posts.csv
    -> entities.csv
    -> graph.graphml + Obsidian notes
    -> gaps.csv
    -> editorial_backlog.csv
    -> revisión con Claude Code skills/subagents
```

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/config.example.yml config/config.yml
cp .env.example .env   # añade tu GOOGLE_NL_API_KEY
```

## Extracción de entidades

La extracción usa la **Google Cloud Natural Language API** (`analyzeEntities`), que
devuelve entidades tipadas con `salience` (relevancia 0-1) y enlace al Knowledge
Graph (`mid`, `wikipedia_url`). La clave se lee desde `.env`:

```text
GOOGLE_NL_API_KEY=tu_api_key
```

Habilita la "Cloud Natural Language API" en tu proyecto de Google Cloud y crea una
API key en *APIs & Services > Credentials*. Parámetros en `config/config.yml` bajo
`extraction` (idioma, `min_salience`, `require_kg_mid`, etc.).

## Uso rápido con Substack

Edita `config/config.yml` y añade tu feed, por ejemplo:

```yaml
source:
  substack_feed_url: "https://TU-SUBDOMINIO.substack.com/feed"
```

Ejecuta:

```bash
python src/run_pipeline.py --config config/config.yml
```

## Uso con CSV exportado

Crea `data/raw/posts.csv` con estas columnas mínimas:

```csv
url,title,published,text
```

Luego ejecuta:

```bash
python src/run_pipeline.py --config config/config.yml --skip-ingest
```

## Comparación externa

Para detectar gaps de mercado, añade uno de estos inputs:

1. `data/raw/external_posts.csv` con columnas `url,title,text`, obtenido de competidores o resultados SERP.
2. `data/raw/external_entities.csv` con columna `canonical_entity` o `entity`.
3. `data/raw/gsc_queries.csv` con columnas `query,clicks,impressions,ctr,position` exportadas de Search Console.

El script no scrapea Google directamente. Para SERPs usa una API legal como SerpAPI, DataForSEO, Semrush, Ahrefs, Sistrix o una exportación manual.

## Outputs

```text
outputs/entities.csv
outputs/entity_edges.csv
outputs/post_entity_edges.csv
outputs/gaps.csv
outputs/editorial_backlog.csv
outputs/graph.graphml
outputs/obsidian/*.md
```

## Uso con Claude Code

Este repo incluye:

```text
.claude/skills/entity-gap-audit/SKILL.md
.claude/skills/run-entity-gap-pipeline/SKILL.md
.claude/agents/entity-extractor.md
.claude/agents/gap-strategist.md
.claude/agents/seo-validator.md
.claude/settings.example.json
```

En Claude Code puedes invocar:

```text
/run-entity-gap-pipeline config/config.yml
/entity-gap-audit outputs/gaps.csv outputs/editorial_backlog.csv
```


## Ejecución programática con Claude Agent SDK

Opcionalmente puedes ejecutar una auditoría con el Agent SDK:

```bash
pip install -r requirements-agent.txt
export ANTHROPIC_API_KEY=tu_api_key
python src/claude_audit_agent.py --gaps outputs/gaps.csv --backlog outputs/editorial_backlog.csv
```

Para uso no interactivo desde Claude Code CLI:

```bash
claude -p "Usa /entity-gap-audit outputs/gaps.csv outputs/editorial_backlog.csv" --allowedTools "Read,Grep,Glob,Bash"
```

## Principio de diseño

- Scripts: ingestan, transforman, cuentan, comparan y exportan.
- Skills: encapsulan procedimientos repetibles.
- Subagentes: separan análisis especializado.
- Hooks: validan que Claude no rompa el pipeline.
- Humanos: deciden qué publicar y qué no.

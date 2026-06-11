# Entity Gap — SEO/GEO con IA

Sistema **repetible y escalable** para detectar oportunidades de contenido (gaps
de entidades) y priorizar un backlog editorial, partiendo de tu propio archivo de
contenido. Diseñado para correr bajo **Claude Code por conversación**: scripts
deterministas + skills + agentes + un arnés que verifica.

> El diseño completo está en **`ARCHITECTURE.md`**. Las mejoras pendientes, en **`BACKLOG.md`**.

## Filosofía

> Dato **cuantitativo → script** (determinista). Dato **cualitativo → IA** como
> clasificador, no como oráculo (skill/agente). Nada se da por hecho sin evidencia.

## El flujo, por fases

| Fase | Pieza | Qué hace |
|------|-------|----------|
| 0. Proyecto | skill `nuevo-proyecto` | crea `projects/<id>/` + brief autocompletado (`project.json`) |
| 1. Extracción | `src/extract_entities.py` | Google NL `analyzeEntities` (salience + Knowledge Graph) |
| 2. Limpieza objetiva | `src/clean_entities.py` | quita números, vacíos, frases-título (reglas) |
| 3. Limpieza semántica | agente `entity-curator` | decide territorio/ruido con el brief; enriquece `anti_territorio` |
| 4. Demanda | `src/fetch_trends.py` | Google Trends (related top + rising) filtrado al territorio |
| 5-7. Gaps + backlog | agente `gap-strategist` | agrupa gaps en clusters y prioriza acciones editoriales |
| Arnés | `bin/check.py` | check de salud + Default-FAIL (verifica cada fase) |

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config/config.example.yml config/config.yml
cp .env.example .env                # añade tu GOOGLE_NL_API_KEY
```

Necesitas una API key de **Google Cloud Natural Language API** (capa gratuita:
5.000 unidades/mes; el código nunca la supera, ver `extraction.monthly_unit_cap`).

## Uso (por proyecto)

```bash
# 0. Crear proyecto desde una carpeta de .md (o un CSV url,title,published,text)
python src/md_to_posts.py "ruta/a/newsletters/*.md" --out projects/<id>/data/raw/posts.csv
# (la skill /nuevo-proyecto hace esto y rellena el brief leyendo el contenido)

# 1-2. Extracción + limpieza objetiva
python src/extract_entities.py --input projects/<id>/data/raw/posts.csv --out projects/<id>/outputs/entities.csv
python src/clean_entities.py --raw projects/<id>/outputs/entities_raw.csv --out projects/<id>/outputs/entities.csv

# 3. Limpieza semántica -> agente entity-curator (lee el brief)
# 4. Demanda
python src/fetch_trends.py --project <id>

# Arnés: verificar salud y que el estado no miente
python bin/check.py <id>
```

## Estructura

```text
projects/<id>/          un proyecto = un análisis
  project.json          brief (contexto del territorio) + estado de fases
  data/raw/posts.csv    contenido ingerido
  outputs/              entities, trends, gaps, editorial_backlog, topical_map
src/                    scripts deterministas
.claude/skills/         nuevo-proyecto, entity-gap-audit
.claude/agents/         entity-curator, gap-strategist, seo-validator
bin/check.py            el arnés (Default-FAIL)
```

## Con Claude Code

```text
/nuevo-proyecto <id> <ruta-al-contenido>
/entity-gap-audit projects/<id>/outputs/gaps.csv projects/<id>/outputs/editorial_backlog.csv
```

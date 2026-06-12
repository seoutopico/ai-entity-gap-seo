# ai-entity-gap-seo — gaps de entidades para SEO/GEO con IA

Sistema **repetible** para detectar *gaps de entidades* —temas con demanda de
búsqueda que tu contenido cubre poco o nada— y convertirlos en un **backlog
editorial priorizado** y un **informe final**, partiendo de tu propio archivo de
contenido (newsletters, blog…).

Diseñado para correr bajo **Claude Code por conversación**: scripts deterministas
+ agentes + skills + un arnés que verifica cada fase contra el disco.

> 📖 **Documentación en [`docs/`](docs/README.md)** — para perfiles técnicos y no
> técnicos: [conceptos](docs/conceptos.md) · [el pipeline](docs/el-pipeline.md) ·
> [cómo se mide](docs/como-se-mide.md) · [arquitectura](docs/arquitectura.md).

## Filosofía

> Dato **cuantitativo → script** (determinista, reproducible).
> Dato **cualitativo → IA** como clasificador anclado a un brief, no como oráculo.
> Nada se da por hecho sin evidencia escrita en disco (**Default-FAIL**).

## El pipeline, por fases

| Fase | Pieza | Qué hace | Evidencia |
|------|-------|----------|-----------|
| 0. Proyecto | skill `nuevo-proyecto` | crea `projects/<id>/`, ingiere el contenido y autocompleta el brief leyéndolo | `project.json`, `posts.csv` |
| 1-2. Extracción + limpieza | `src/extract_entities.py` | Google NL `analyzeEntities` (salience + Knowledge Graph) y limpieza por reglas | `entities_raw.csv`, `entities.csv` |
| 3. Limpieza semántica | agente `entity-curator` | decide territorio/ruido/marca con el brief; resuelve polisemia y enriquece el anti-territorio | `entities_curated.csv` |
| 4. Demanda | `src/fetch_trends.py` | Google Trends (related top + rising) alrededor del territorio, filtrado por brief | `trends_related.csv`, `external_entities.csv` |
| 5. Gaps | `src/compare_gaps.py` | cruza demanda externa con cobertura interna (matching determinista) | `gaps.csv` |
| 6-7. Backlog | agente `gap-strategist` | prioriza editorialmente los gaps: qué crear, actualizar, agrupar o ignorar | `editorial_backlog.csv` |
| 8. Informe | agente `report-writer` | sintetiza todo en un informe legible para el dueño del contenido | `informe.md` |
| Arnés | `bin/check.py` | verifica evidencia, columnas exactas y orden de fases; sale con error si algo miente | — |

Los agentes no se ejecutan por terminal: los lanza la IA orquestadora (Claude
Code) con la tool `Agent`. Las instrucciones de orquestación viven en
[`CLAUDE.md`](CLAUDE.md); el contrato de columnas de cada output, en
[`projects/_template/outputs/README.md`](projects/_template/outputs/README.md).

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                # añade tu GOOGLE_NL_API_KEY (el único secreto)
```

Necesitas una API key de **Google Cloud Natural Language**. El código nunca
supera su capa gratuita (5.000 unidades/mes, tope persistido en
`.usage/nl_usage.json`). Google Trends no necesita key, pero rate-limita fuerte:
el cache evita reconsultar y `max_seeds` se sube poco a poco.

## Uso

Lo natural es abrir el repo en Claude Code y pedirle el análisis: la IA orquesta
las fases en orden y corre el arnés entre ellas.

```text
/nuevo-proyecto mi-blog ruta/a/posts/*.md
```

Las fases de script también se pueden lanzar a mano:

```bash
python bin/check.py <id>                        # SIEMPRE antes de empezar
python src/extract_entities.py --project <id>   # fases 1-2
python src/clean_entities.py --project <id>     # re-afinar filtros sin gastar API
python src/fetch_trends.py --project <id>       # fase 4
python src/compare_gaps.py --project <id>       # fase 5
```

Las fases 3, 6-7 y 8 son de agente (juicio cualitativo anclado al brief): se
lanzan desde Claude Code, nunca se sustituyen por scripts ad-hoc.

## Estructura

```text
projects/<id>/          un proyecto = un análisis
  project.json          brief (dominio: tema, entidades núcleo, anti-territorio…) + estado de fases
  data/raw/posts.csv    contenido ingerido
  outputs/              entities*, trends*, gaps, editorial_backlog, informe.md
projects/_template/     contrato de columnas (molde, no se copia)
src/                    scripts deterministas
.claude/agents/         entity-curator, gap-strategist, report-writer
.claude/skills/         nuevo-proyecto, entity-gap-audit
config/config.yml       parámetros técnicos (el dominio vive en el brief de cada proyecto)
bin/check.py            el arnés (Default-FAIL)
```

## El arnés

```bash
python bin/check.py            # valida el repo base + lista proyectos
python bin/check.py <id>       # valida además ese proyecto
```

Una fase marcada como hecha solo se da por buena si su archivo de evidencia
existe, tiene contenido, **sus columnas (o secciones) coinciden exactamente con
el molde** y ninguna fase anterior quedó sin hacer. Si algo miente, sale con
código 2: el informe nunca sustituye al disco.

## Autora

Hecho por **Aina Lluna**.

Si te interesa la IA aplicada, la gestión de proyectos con LLMs y cómo construir
sistemas personales sobre Claude Code, suscríbete a mi newsletter en
[ainalluna.substack.com](https://ainalluna.substack.com).

Si este repo te resulta útil, una estrella en GitHub o un comentario por el canal
que prefieras se agradece.

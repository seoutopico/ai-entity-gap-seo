# Arquitectura del proceso — Entity Gap (SEO/GEO con IA)

> Sistema **repetible y escalable** para detectar oportunidades de contenido
> (gaps de entidades) y priorizar un backlog editorial. Pensado para **personas
> no técnicas**: todo corre bajo **Claude Code por conversación (voz)**; nadie
> edita código ni YAML. Material de la ponencia *Mujeres en SEO 2026 — "Procesos,
> automatización y criterio para no delegar a ciegas"*.

## Filosofía (la regla que decide qué hace qué)

> **Si el dato es cuantitativo → lógica determinista (script).
> Si el dato es cualitativo → IA como clasificador, no como oráculo (skill/agente).**

| | Script | Skill | Agente |
|---|---|---|---|
| Autonomía | baja | media | alta |
| Función | ejecuta reglas | empaqueta criterio | decide pasos |
| Ideal para | datos cuantitativos | tareas cualitativas acotadas | procesos multifase |
| Riesgo | bajo | medio | alto |
| Control | validación técnica | salida restringida | supervisión y límites |

La IA **mueve datos entre pasos, deja rastro y ayuda a decidir** — no inventa ni
decide a ciegas. Cada paso deja evidencia en disco (no depende del chat):
**memoria, control, escala.**

## El concepto de "proyecto"

Cada análisis vive en su carpeta. Al dar el contenido se crea el folder y un
`project.json` con un **brief** que **la IA rellena leyendo el propio contenido**
(es un `_template`, **NO se entrevista al usuario**). Ese brief es el **contexto**
que luego usan los agentes para clasificar y desambiguar con criterio.

```
projects/
  _template/
    project.json          # plantilla del brief (campos a rellenar por la IA)
  <nombre-proyecto>/
    project.json          # brief autocompletado por la IA desde el contenido
    data/raw/posts.csv    # contenido ingerido
    outputs/              # entities, trends, gaps, backlog
```

El brief incluye un campo **`anti_territorio`** clave para la desambiguación
semántica: p.ej. *"memoria = LLM sí, memoria = RAM / canción no"*. Eso permite al
agente de limpieza decidir por **contexto**, no por umbrales frágiles.

## El método, fase a fase

| Fase | Pieza | Qué entra | Qué hace | Qué sale |
|---|---|---|---|---|
| **0. Proyecto** | Skill | contenido (.md/csv) | crea folder + rellena el brief leyendo el contenido | `project.json` |
| **1. Extracción** | Script | posts | Google NL `analyzeEntities` (salience + mid + wikipedia) | `entities_raw.csv` |
| **2. Limpieza objetiva** | Script | crudo | quita números, vacíos, frases-título (reglas) | `entities.csv` |
| **3. Limpieza semántica** | **Agente** | entidades + **brief** | descarta lo fuera de territorio, desambigua por contexto, valida semillas | entidades curadas |
| **4. Demanda** | Script | semillas curadas | Google Trends (related top + rising) | `external_entities.csv` |
| **5. Intención** | Skill | término + extracto | clasifica intención (informacional/comercial/transaccional) | términos tipados |
| **6. Gaps + prioridad** | **Agente** | entidades + demanda + **brief** | agrupa, detecta gaps, prioriza con criterio editorial | `gaps.csv` |
| **7. Resultado** | Agente | gaps | decide crear / actualizar / enlazar | `editorial_backlog.csv` |

Regla de oro aplicada: las fases 1, 2, 4 son **cuantitativas → script**; las fases
0, 3, 5, 6, 7 implican **criterio → skill/agente** (siempre con el brief como ancla).

## Control de coste (no negociable)

La extracción usa la capa gratuita de Google NL (5.000 unidades/mes). Tope **en el
código**: `monthly_unit_cap` + contador persistente `.usage/nl_usage.json` que
acumula entre ejecuciones. Nunca se envía nada que supere el límite.

## Estado actual

**Scripts** (`src/`)
- `extract_entities.py` — ✅ Google NL v1 + topes de coste.
- `clean_entities.py` — ✅ limpieza objetiva por reglas (fase 2).
- `fetch_trends.py` — ✅ Trends vía trendspy (fase 4); selección de semillas a mover a la fase 3 (agente).
- `build_graph.py`, `compare_gaps.py`, `run_pipeline.py` — ✅ existen (scoring heredado, a recalibrar).
- `md_to_posts.py` — ✅ ingesta (pendiente: capturar métricas del frontmatter).

**Skills** (`.claude/skills/`)
- `run-entity-gap-pipeline` — ⚠️ actualizar al flujo nuevo + ruta `.venv`.
- `entity-gap-audit` — ✅ válida (interpretación de outputs).
- `nuevo-proyecto` — ➕ pendiente de crear (fase 0).

**Agentes** (`.claude/agents/`)
- `entity-curator` — ✅ agente de limpieza semántica (fase 3): juzga relevancia anclado al brief, escribe `entities_curated.csv` y enriquece `anti_territorio_detectado` (loop). Sustituye al obsoleto `entity-extractor`.
- `gap-strategist` — ✅ válido (fase 6/7).
- `seo-validator` — ✅ válido (validación medible).

**Arnés** (Pilar 1 + Default-FAIL)
- ✅ `bin/check.py` — check de salud: valida repo base + proyecto, y **Default-FAIL**
  (una fase marcada hecha en `project.json` falla si no existe su evidencia CSV).
  Corre antes de trabajar; `exit 2` = parar.
- ✅ Roles (barato ejecuta / caro juzga): scripts extraen/limpian (cuantitativo);
  el agente `entity-curator` juzga la relevancia (cualitativo, lee el brief).
- ➕ pendiente (fuera del mínimo): verify-gate como hook automático; loop `/mejora`.

**Hooks**
- ✅ py_compile tras editar `src/`; bloqueo `rm -rf`.

## Orden de construcción

1. **Skill `nuevo-proyecto`** + `_template/project.json` (fase 0) — el cimiento; todo lo demás lee el brief.
2. **Reescribir `entity-extractor`** como agente de limpieza semántica (fase 3) que consume el brief.
3. Mover la **selección de semillas** de `fetch_trends.py` a la fase 3 (decisión del agente, no umbrales).
4. Actualizar `run-entity-gap-pipeline` al flujo nuevo.
5. Hook de validación de outputs.
6. Recalibrar `opportunity_score` y conectar GSC real (ver `BACKLOG.md`).

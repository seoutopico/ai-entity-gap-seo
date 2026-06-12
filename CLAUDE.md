<!--
  Notas para mantenedores humanos (NO entran en el contexto de Claude):
  - Objetivo de este archivo: que una IA que arranca sesión sepa LANZAR el pipeline
    sin re-derivar el flujo. Mantenerlo bajo ~200 líneas y en imperativo.
  - Fuente del diseño: README.md + projects/_template/outputs/README.md (contrato de columnas).
  - Si cambia un comando o el contrato de columnas, actualizar AQUÍ y en el template.
-->

# ai-entity-gap-seo — instrucciones de proyecto

Sistema **repetible** para detectar *gaps de entidades* (temas con demanda de
búsqueda que tu contenido cubre poco) y priorizar un **backlog editorial**.
Corre bajo Claude Code: scripts deterministas + agentes + un arnés que verifica.

**Filosofía (no la rompas):** dato **cuantitativo → script** (determinista);
dato **cualitativo → IA** como clasificador, no como oráculo (agente/skill).
Nada se da por hecho sin evidencia escrita en disco.

## Cómo lanzar el sistema

Entorno: **Windows + PowerShell**. Activa el venv una vez por sesión:

```powershell
.venv\Scripts\Activate.ps1
```

Requisitos previos: `.env` con `GOOGLE_NL_API_KEY` (único secreto). Verifícalo
SIEMPRE antes de empezar con el arnés (ver abajo).

El pipeline es **por proyecto** (`projects/<id>/`). Lánzalo en orden de fases.
`<id>` es el slug del proyecto (p. ej. `think-hack`).

| Fase | Quién | Comando / acción | Produce |
|---|---|---|---|
| 0. Proyecto | skill `nuevo-proyecto` | invoca la skill (no entrevista al usuario; lee el corpus y rellena el brief) | `project.json` + `data/raw/posts.csv` |
| 1. Extracción + 2. Limpieza | `src/extract_entities.py` | `python src/extract_entities.py --project <id>` | `entities_raw.csv` y `entities.csv` |
| (2 bis) Re-iterar filtros | `src/clean_entities.py` | `python src/clean_entities.py --project <id>` | `entities.csv` (sin llamar a la API) |
| 3. Limpieza semántica | agente `entity-curator` | lánzalo con la tool **Agent** (`subagent_type: entity-curator`), pásale el `<id>` | `entities_curated.csv` |
| 4. Demanda | `src/fetch_trends.py` | `python src/fetch_trends.py --project <id>` | `trends_related.csv`, `external_entities.csv` |
| 5. Gaps | `src/compare_gaps.py` | `python src/compare_gaps.py --project <id>` | `gaps.csv` |
| 6-7. Backlog | agente `gap-strategist` | lánzalo con la tool **Agent** (`subagent_type: gap-strategist`), pásale el `<id>` | `editorial_backlog.csv` |
| 8. Informe | agente `report-writer` | lánzalo con la tool **Agent** (`subagent_type: report-writer`), pásale el `<id>` | `informe.md` |
| Auditar | skill `entity-gap-audit` | invoca la skill sobre los outputs (diálogo, no escribe archivos) | diagnóstico editorial |

Notas de ejecución:

- **Fase 1 ya incluye la 2**: `extract_entities.py` escribe el crudo (`entities_raw.csv`,
  cache de la API) y aplica la limpieza por reglas → `entities.csv`. Usa
  `clean_entities.py` **solo** para re-afinar filtros sin volver a gastar API.
- Los **agentes no se ejecutan por terminal**: los lanzas tú (IA principal) con la
  tool `Agent` y el `subagent_type` correspondiente. Cada agente lee/escribe solo
  sus archivos del contrato (ver `.claude/agents/`).
- Entre fase 3 y 4 puede haber **loop**: el curador enriquece `anti_territorio_detectado`
  en `project.json`; Trends lo usa para filtrar. Re-corre Trends si el anti-territorio cambió.
- **Quién marca `estado.<fase> = true`**: los agentes marcan su propia fase
  (`limpieza_semantica`, `backlog`, `informe`) tras escribir su evidencia; las fases
  de script las marcas tú (IA principal) DESPUÉS de que el script termine y
  `check.py <id>` pase.

## El arnés — corre ANTES de trabajar y DESPUÉS de cada fase (Default-FAIL)

```powershell
python bin/check.py            # valida repo base + lista proyectos
python bin/check.py <id>       # valida además ese proyecto
```

**IMPORTANT:** el check implementa **Default-FAIL**. Una fase marcada `true` en
`project.json → estado` solo se da por buena si su CSV de evidencia existe, tiene
filas, sus columnas son EXACTAS al molde del template y ninguna fase anterior
quedó sin hacer. Sale con código 2 si algo miente. **NUNCA marques
`estado.<fase> = true` sin haber escrito su archivo de evidencia** — el check lo
comprueba contra el disco, no contra el informe. Corre el check tras CADA fase:
si falla, arregla esa fase antes de tocar la siguiente.

## Reglas críticas (no negociables)

- **YOU MUST NOT sustituir a los agentes.** `entities_curated.csv` SOLO lo escribe
  el agente `entity-curator`; `editorial_backlog.csv` SOLO el agente `gap-strategist`;
  `informe.md` SOLO el agente `report-writer`; `gaps.csv` SOLO el script
  `compare_gaps.py`. NUNCA generes estos archivos tú
  (IA principal) con scripts ad-hoc, pandas inline ni "atajos equivalentes", aunque
  parezca más rápido: el juicio cualitativo anclado al brief es EL PRODUCTO de esas
  fases, no un formalismo. Si un agente falla, reporta el fallo y para; no lo suplas.
- **YOU MUST respetar el contrato de columnas.** Cada CSV de `outputs/` tiene
  columnas EXACTAS definidas en `projects/_template/outputs/` (y su `README.md`).
  Si las columnas no coinciden, la fase siguiente se rompe. `salience_sum` ≠
  `salience_total`; `posts` ≠ `n_posts`. No inventes ni renombres columnas; el
  conjunto es el contrato (el orden no importa, todo se lee por nombre).
- **Topes de coste blindados.** `extract_entities.py` nunca supera la capa gratuita
  de Google NL (`monthly_unit_cap: 5000`, persistido en `.usage/nl_usage.json`).
  No subas ese tope ni quites los topes por ejecución (`max_requests`, `max_chars`)
  para "ir más rápido".
- **Google Trends rate-limita fuerte (429).** El cache (`trends_related.csv`) no
  reconsulta semillas ya hechas. Sube `max_seeds` poco a poco entre ejecuciones;
  no fuerces lotes grandes.
- **Separación de responsabilidades.** El dato de DOMINIO (ontología, idioma, geo,
  brand_terms, anti_territorio) vive en `project.json → brief`, NO en
  `config/config.yml` (que solo tiene parámetros técnicos). `load_project_config()`
  mergea ambos. No muevas dominio al config global.
- **No machaques proyectos existentes.** Un proyecto = un análisis en `projects/<id>/`.
  No sobrescribas outputs ajenos sin que el usuario lo pida.
- **`outputs/` solo contiene salidas del contrato.** Si un agente o tú necesitáis
  archivos de trabajo (scripts, volcados), escríbelos en `.tmp/` y bórralos.

## Cómo trabajar (principios)

Adaptado de las observaciones de Karpathy sobre fallos típicos de los LLM:

- **Piensa antes de codear.** Si hay ambigüedad sobre territorio o sobre qué fase
  toca, di tus asunciones y pregunta; no elijas una interpretación en silencio.
- **Simplicidad.** Implementa solo lo pedido. No añadas "flexibilidad" ni
  abstracciones que nadie pidió. Si 200 líneas pueden ser 50, reescríbelo.
- **Cambios quirúrgicos.** Toca solo lo que la tarea exige. No "mejores" código
  adyacente, comentarios ni formato; no refactorices lo que funciona. Respeta el
  estilo del código que rodea tu cambio.
- **Verifica con un objetivo.** Convierte tareas imperativas en objetivos
  comprobables. Tras tocar el pipeline, corre `python bin/check.py <id>` y usa su
  salida como criterio de éxito, no tu impresión.

## Mapa rápido del repo

```text
projects/<id>/        un proyecto = un análisis
  project.json        brief (dominio) + estado de fases
  data/raw/posts.csv  contenido ingerido
  outputs/            entities*, trends*, gaps, editorial_backlog, informe.md
projects/_template/   contrato de columnas (molde, no se copia)
src/                  scripts deterministas (extract, clean, fetch_trends, compare_gaps, md_to_posts, utils)
.claude/agents/       entity-curator, gap-strategist, report-writer, seo-validator
.claude/skills/       nuevo-proyecto, entity-gap-audit
config/config.yml     parámetros TÉCNICOS (no dominio)
bin/check.py          el arnés (Default-FAIL)
```

## Idioma

Responde y escribe comentarios **en español** con ortografía y acentos correctos.

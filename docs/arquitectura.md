# Arquitectura

Cómo está construido el sistema y, sobre todo, **por qué está construido así**.
Para perfiles técnicos.

## La regla de reparto

| | Script | Skill | Agente |
|---|---|---|---|
| Naturaleza | determinista | procedimiento guiado por IA | IA con rol y contrato acotados |
| Ideal para | dato cuantitativo | flujos con el usuario en el bucle | juicio cualitativo repetible |
| Ejemplos | extract, clean, fetch_trends, compare_gaps | nuevo-proyecto, entity-gap-audit | entity-curator, gap-strategist, report-writer |
| Riesgo | bajo | medio | alto → se mitiga con contrato + arnés |

El criterio para asignar una fase no es "qué puede hacer la IA" (puede hacerlo
todo) sino **qué se pierde si lo hace**: un cruce de CSVs hecho por IA es más
caro, más lento y no reproducible; una decisión de territorio hecha por regex es
frágil ante la polisemia. Cada pieza hace solo lo que le toca.

## El mapa

```text
projects/<id>/          un proyecto = un análisis aislado
  project.json          brief (DOMINIO) + estado de fases
  data/raw/posts.csv    contenido ingerido
  outputs/              solo salidas del contrato
projects/_template/     el CONTRATO: cabeceras de cada CSV + secciones del informe
src/                    scripts deterministas
.claude/agents/         contratos de los agentes (qué leen, qué escriben, qué NO)
.claude/skills/         nuevo-proyecto, entity-gap-audit
config/config.yml       parámetros TÉCNICOS globales
bin/check.py            el arnés
CLAUDE.md               instrucciones de orquestación (fuente de verdad única)
```

## Separación config / brief

- `config/config.yml` = **cómo** funciona el sistema (timeouts, topes, umbrales).
  Global, versionado, agnóstico del contenido.
- `project.json → brief` = **de qué va** el proyecto (tema, idioma, geo,
  ontología, anti-territorio, brand_terms). Por proyecto, lo genera la IA
  leyendo el corpus.
- `load_project_config()` mergea ambos en tiempo de ejecución: el brief manda en
  todo lo que depende del contenido.

Mover dominio al config global rompería la premisa "un proyecto = un análisis":
es el error de diseño contra el que más protege el repo.

## El contrato de outputs

`projects/_template/outputs/` define las columnas EXACTAS de cada CSV (y las
secciones obligatorias de `informe.md`). El conjunto de columnas es el contrato;
el orden no importa (todo se lee por nombre). `salience_sum` ≠ `salience_total`:
la fase 4 busca columnas por nombre y un rename silencioso rompe el pipeline dos
fases más tarde, donde ya no se ve la causa. Por eso el arnés valida cabeceras,
no solo existencia.

## El arnés (Default-FAIL)

`bin/check.py <id>` implementa la premisa de que **el informe de una IA no es
evidencia**. Valida contra disco:

1. **Evidencia**: cada fase marcada `true` en `project.json → estado` tiene su
   archivo con contenido real (filas en CSV, secciones en MD).
2. **Contrato**: todo output presente tiene las cabeceras exactas del template
   (o las secciones `##` del molde, para el informe).
3. **Orden**: ninguna fase hecha con una anterior pendiente — los atajos no pasan.
4. **Higiene**: CSVs ajenos al contrato en `outputs/` son fallo (scratch → `.tmp/`).

Sale con código 2 si algo miente. Se corre antes de trabajar y tras cada fase.

## Por qué los agentes no se sustituyen

La tentación natural de cualquier orquestador LLM es el atajo: "puedo generar
`entities_curated.csv` con pandas en 30 segundos en vez de lanzar el agente".
El archivo resultante existe y tiene filas — pero **el juicio anclado al brief
es el producto de esa fase**, no un formalismo. Las defensas, por capas:

1. Cada output sensible tiene **un único productor declarado** (CLAUDE.md, el
   template y el contrato del agente dicen lo mismo — sin contradicciones que
   den excusa al atajo).
2. El arnés hace el atajo **no rentable**: columnas inventadas o fases saltadas
   rompen el check.
3. La regla imperativa en CLAUDE.md: si un agente falla, se reporta; no se suple.

Lo que un check de disco no puede probar es la *procedencia* (quién escribió el
archivo); lo que sí consigue es que la ruta correcta sea la de menor resistencia.

## Costes blindados

- **Google NL**: tope mensual absoluto (5.000 unidades, capa gratuita) persistido
  en `.usage/nl_usage.json` entre ejecuciones, más topes por ejecución
  (`max_requests`, `max_chars`). El crudo (`entities_raw.csv`) actúa de cache:
  re-analizar no re-gasta.
- **Google Trends**: sin key pero con rate-limit agresivo (429). El cache
  (`trends_related.csv`) no reconsulta semillas hechas; `max_seeds` se sube
  gradualmente entre ejecuciones.

## Qué es reproducible (y qué no)

| Fase | ¿Reproducible bit a bit? | Por qué |
|---|---|---|
| 1-2, 5 (scripts) | **Sí** | deterministas + cache de API |
| 3, 6-8 (agentes) | No | son LLM: mismo contrato, salida distinta |
| 4 (Trends) | No | la demanda cambia con el tiempo |

Además hay un bucle de retroalimentación: el anti-territorio enriquecido por una
ejecución cambia el filtrado de la siguiente. Por eso "reproducir" un análisis
significa **equivalencia de contrato y de conclusiones** (mismas columnas,
solapamiento del top-N), no diffs idénticos. Lo que el arnés garantiza es que
cualquier ejecución pasó por las mismas fases, con los mismos productores y el
mismo contrato.

# _template/outputs/ — molde de las salidas (contrato de columnas)

Cada `.csv` de esta carpeta es una **plantilla de cabecera** (solo la fila de columnas):
el molde que TODO productor —script o agente— debe respetar al escribir ese fichero en
`projects/<id>/outputs/`. Aquí NO hay datos: son la **forma** que deben tener los resultados.

Esta carpeta es **referencia/contrato**, no se copia a cada proyecto: los scripts y agentes
escriben sus propios outputs ya con estas cabeceras. Si las columnas no coinciden, la fase
siguiente se rompe (p. ej. `fetch_trends.py` busca `salience_sum`, `posts`, `mid` en el curado).

> **Regla:** el conjunto de columnas es el contrato; el **orden** no importa (todo se lee por
> nombre). No inventes ni renombres columnas (`salience_sum` ≠ `salience_total`, `posts` ≠
> `n_posts`). Si necesitas una columna nueva, primero actualiza el molde aquí.

| Fichero | Lo produce | Fase | Columnas |
|---|---|---|---|
| `entities_raw.csv` | `src/extract_entities.py` | 1 | `url,title,published,entity,canonical_entity,type,google_type,score,salience,mentions,mid,wikipedia_url` |
| `entities.csv` | `src/clean_entities.py` | 2 | igual que el raw (filtrado por reglas) |
| `entities_curated.csv` | **agente `entity-curator`** | 3 | `canonical_entity,type,posts,salience_sum,mid,decision,motivo` |
| `trends_related.csv` | `src/fetch_trends.py` | 4 | `seed,seed_type,kind,rank,term,term_norm,value` |
| `external_entities_raw.csv` | `src/fetch_trends.py` | 4 | `canonical_entity,score,rising,seeds,source` |
| `external_entities.csv` | `src/fetch_trends.py` | 4 | `canonical_entity,score,rising,seeds,source,score_norm` |
| `gaps.csv` | `src/compare_gaps.py` | 5 | `canonical_entity,gap_type,rising,score,score_norm,seeds,source` |
| `editorial_backlog.csv` | **agente `gap-strategist`** | 6-7 | `prioridad,cluster,titulo_trabajo,accion,formato,intencion,gap_type,entidades,justificacion` |
| `informe.md` | **agente `report-writer`** | 8 | markdown; las secciones `##` del molde `informe.md` son obligatorias |

## El curado (fase 3) — el que más se rompía

`entities_curated.csv` es **agregado por entidad** (una fila = una `canonical_entity` que
pasa a territorio), NO por mención. Por eso NO lleva las columnas por-mención de
`entities.csv` (`url`, `salience`, `mentions`, `score`…). Las 7 columnas canónicas:

- `canonical_entity` — la entidad (clave).
- `type` — tipo del dominio (ontología del brief): `tool`/`concept`/`platform`/…
- `posts` — nº de posts distintos donde aparece (cobertura interna).
- `salience_sum` — salience **acumulada** sumando todas sus menciones.
- `mid` — Knowledge Graph id de Google (vacío si no tiene). Lo usa Trends como señal objetiva.
- `decision` — `KEEP` (el curado solo contiene KEEP).
- `motivo` — una frase anclada al brief.

Notas:
- Solo se escriben las filas `KEEP`. Las `DROP`/`BRAND` no van al curado (sí al resumen).
- `salience_sum` y `posts` salen de **agregar** `entities.csv` por `canonical_entity`
  (sumar `salience`, contar `url` únicos). `mid`/`type` se toman de la mención de mayor salience.

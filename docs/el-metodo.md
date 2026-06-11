# El método, fase a fase

Cada análisis es un **proyecto** (`projects/<id>/`). El contexto del proyecto vive en
`project.json` (el **brief**) y cada fase deja su resultado en `outputs/`.

> Regla que decide qué pieza hace qué: **cuantitativo → script** (determinista),
> **cualitativo → IA** (skill/agente). Ver [arquitectura](arquitectura.md).

| Fase | Pieza | Qué entra | Qué hace | Qué sale |
|---|---|---|---|---|
| **0. Proyecto** | skill `nuevo-proyecto` | tu contenido (.md/CSV) | crea la carpeta y **rellena el brief leyendo el contenido** (tema, idioma, geo, entidades núcleo, anti-territorio, tipado del dominio) | `project.json` |
| **1. Extracción** | `extract_entities.py` | posts | llama a **Google NL** y extrae entidades con `salience` + enlace al Knowledge Graph | `entities_raw.csv` |
| **2. Limpieza objetiva** | `clean_entities.py` | crudo | quita números, vacíos, frases-título (reglas) | `entities.csv` |
| **3. Limpieza semántica** | agente `entity-curator` | entidades + **brief** | decide territorio/ruido **con criterio**, marca marca, enriquece el anti-territorio (loop) | `entities_curated.csv` |
| **4. Demanda** | `fetch_trends.py` | semillas curadas | **Google Trends** (related top + rising), filtrado al territorio del brief | `external_entities.csv` |
| **5-7. Gaps + backlog** | agente `gap-strategist` | territorio + demanda + **brief** | cruza, agrupa en clusters, prioriza acciones editoriales | `gaps.csv`, `editorial_backlog.csv`, `topical_map.md` |
| **Arnés** | `bin/check.py` | el proyecto | verifica salud y que el estado no miente (**Default-FAIL**) | `exit 0/2` |

## El detalle de cada fase

**0 · Proyecto.** No se entrevista al usuario: la IA lee el contenido y rellena el
brief. El brief es el **contexto** que usan los agentes después (sobre todo el
`anti_territorio`, que desambigua: *"memoria" aquí es de IA, no RAM ni la canción*).

**1 · Extracción.** Google NL no devuelve palabras frecuentes, devuelve **entidades
reales tipadas** con dos señales clave: `salience` (cuán central es al texto) y `mid`
(si está en el Knowledge Graph de Google). Tope de coste para no salir de la capa
gratuita.

**2 · Limpieza objetiva.** Reglas puras, sin criterio: fuera números, fechas,
precios, frases-título largas y genéricos vacíos.

**3 · Limpieza semántica.** Aquí entra el **criterio**: el agente lee el brief y
decide, entidad por entidad, si es **territorio** (KEEP), **ruido/fuera** (DROP) o
**marca** (BRAND). Y aprende sentidos polisémicos nuevos → los apunta en el brief.

**4 · Demanda.** Para cada entidad de territorio con presencia en el Knowledge Graph,
pregunta a Trends qué busca la gente alrededor (`top` = consolidado, `rising` =
tendencia). Filtra lo que no pertenece a tu territorio.

**5-7 · Gaps y backlog.** Lo que la gente busca y tú **no** cubres = gap. El agente
los agrupa en clusters (Claude Code, Deep Research…) y los convierte en piezas con
acción, formato y prioridad.

## El bucle de aprendizaje

El `anti_territorio` del brief **crece** con cada vuelta: la fase 3 y la 4 detectan
ruido nuevo y lo registran, así la próxima ejecución es más limpia. El sistema deja
rastro de cómo aprendió.

➡️ Para los números, ver [cómo se mide](como-se-mide.md). Para ejecutarlo, [uso](uso.md).

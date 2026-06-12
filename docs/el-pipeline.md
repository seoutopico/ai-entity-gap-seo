# El pipeline, fase a fase

Cada análisis es un **proyecto** (`projects/<id>/`): su contexto vive en
`project.json` (el [brief](conceptos.md#brief)) y cada fase deja su resultado en
`outputs/`. La regla que decide **quién** hace cada fase:

> Si el dato es **cuantitativo** → script determinista (mismo input, mismo output).
> Si el dato es **cualitativo** → agente de IA anclado al brief (clasifica, no inventa).

| Fase | Quién | Qué hace | Evidencia |
|---|---|---|---|
| 0. Proyecto | skill `nuevo-proyecto` | crea el proyecto y rellena el brief **leyendo tu contenido** | `project.json`, `posts.csv` |
| 1-2. Extracción + limpieza | script | extrae entidades con Google NL y filtra por reglas | `entities_raw.csv`, `entities.csv` |
| 3. Limpieza semántica | **agente** `entity-curator` | decide territorio / ruido / marca, con el brief | `entities_curated.csv` |
| 4. Demanda | script | pregunta a Google Trends qué se busca alrededor del territorio | `trends_related.csv`, `external_entities.csv` |
| 5. Gaps | script | cruza demanda externa con cobertura interna | `gaps.csv` |
| 6-7. Backlog | **agente** `gap-strategist` | prioriza editorialmente: qué crear, actualizar o ignorar | `editorial_backlog.csv` |
| 8. Informe | **agente** `report-writer` | sintetiza todo en un documento legible | `informe.md` |
| Arnés | `bin/check.py` | verifica cada fase contra el disco | exit 0 / 2 |

## El detalle

**0 · Proyecto.** No hay formulario: la IA lee una muestra de tus posts y rellena
el brief (tema, audiencia, entidades núcleo, anti-territorio inicial, tono,
ontología del dominio). Tú lo validas hablando. El brief es el contexto que toda
decisión posterior citará.

**1-2 · Extracción y limpieza objetiva.** Google Natural Language lee cada post y
devuelve entidades reales con [salience](como-se-mide.md#salience) y enlace al
Knowledge Graph. Después, reglas puras (sin criterio): fuera números, fechas,
pronombres, frases-título. Topes de coste blindados: nunca sale de la capa
gratuita de la API.

**3 · Limpieza semántica.** Aquí entra el criterio. El agente lee el brief y
decide entidad por entidad: `KEEP` (territorio), `DROP` (ruido o fuera), `BRAND`
(tu propia marca — no puede ser un gap). Resuelve la polisemia que ninguna regla
puede: *¿"memoria" aquí es de IA, RAM o la canción?* Cada decisión lleva un
motivo de una frase anclado al brief. Y los sentidos nuevos a excluir los apunta
en el `anti_territorio_detectado` del brief.

**4 · Demanda.** Para las entidades más fuertes del territorio (las que tienen
`mid` o tipo estratégico), pregunta a Trends qué busca la gente alrededor:
términos consolidados (top) y en tendencia (rising). Filtra el resultado con el
territorio y el anti-territorio que el agente ya decidió — el script solo
**aplica** ese criterio, no lo inventa.

**5 · Gaps.** Cruce determinista: demanda externa que **no** está en el
territorio curado = gap. `trending` si la demanda va al alza, `consolidado` si
es estable. Esto es aritmética, no juicio: por eso es un script y su resultado
es reproducible.

**6-7 · Backlog.** Segundo momento de criterio: de los gaps (354 en think-hack),
¿cuáles merecen contenido? El agente prioriza autoridad temática sobre volumen
suelto, descarta lo indefendible (términos genéricos donde no tienes autoridad,
modas contrarias a tu marca) y entrega piezas con prioridad, formato, intención
y justificación (26 piezas en think-hack).

**8 · Informe.** Un agente redactor convierte todos los outputs en un informe
markdown para el dueño del contenido, con una regla dura: **todo número sale de
los CSV** y las recomendaciones vienen del backlog — no añade opinión nueva.

## El bucle de aprendizaje (fases 3 ↔ 4)

El anti-territorio crece con el uso: el curador detecta sentidos a excluir, los
escribe en el brief, y Trends los usa para filtrar. Si el anti-territorio cambió,
se re-corre la fase 4. El sistema deja rastro escrito de cómo aprendió — en
think-hack el brief pasó de 3 exclusiones iniciales a más de 25 detectadas.

## El arnés (por qué te puedes fiar)

`python bin/check.py <id>` se corre **antes de empezar y después de cada fase**.
Una fase solo se da por hecha si:

1. Su archivo de evidencia **existe y tiene contenido**.
2. Sus columnas (o secciones, en el informe) **coinciden exactamente** con el
   contrato (`projects/_template/outputs/`).
3. **Ninguna fase anterior quedó sin hacer** (no hay atajos).

Si algo no cuadra, sale con error y el proceso se para. El principio se llama
**Default-FAIL**: el informe de la IA nunca sustituye a la evidencia en disco.

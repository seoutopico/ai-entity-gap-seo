---
description: Audita outputs de análisis de entidades de contenido, gaps SEO/GEO y backlog editorial, y valida críticamente las recomendaciones (medibles, realistas, sin suposiciones sin datos). Úsalo cuando el usuario quiera interpretar o auditar outputs/gaps.csv, outputs/editorial_backlog.csv, informe.md o entities.csv.
allowed-tools: Read Grep Glob Bash
---

## Objetivo

Analiza los outputs del pipeline de entity gaps y entrega un diagnóstico editorial
accionable. Y, si ya existen backlog y/o informe, **valídalos críticamente**: el
que produce no se valida a sí mismo, así que aquí se desconfía de lo que los
agentes produjeron y se comprueba contra los CSV.

## Inputs esperados

- `projects/<id>/outputs/entities_curated.csv` (el territorio)
- `projects/<id>/outputs/external_entities.csv` (demanda de Trends)
- `projects/<id>/outputs/gaps.csv`
- `projects/<id>/outputs/editorial_backlog.csv`
- `projects/<id>/outputs/informe.md` (si existe, valídalo también)

Si el usuario pasa rutas concretas, usa esas rutas. Esquema de cada CSV en
`projects/_template/outputs/`.

## Procedimiento

1. Lee los CSV disponibles.
2. Identifica las 10 entidades con mayor `score_norm` en `gaps.csv` (prioriza las `rising`).
3. Separa gaps por `gap_type` (en el flujo actual: `trending` = demanda al alza,
   `consolidado` = demanda establecida) y crúzalos con la cobertura interna del curado
   (`posts`/`salience_sum`) para distinguir lo ausente de lo poco cubierto.
4. Para cada oportunidad prioritaria, decide si conviene:
   - Crear artículo nuevo.
   - Actualizar un post existente.
   - Crear pieza pilar.
   - Añadir enlaces internos.
   - Cambiar title/intro/estructura.
5. No recomiendes publicar sobre entidades que no encajen con el territorio editorial del proyecto.
6. Distingue entre demanda SEO, moda de IA y autoridad real de la newsletter.
7. **Validación crítica** (si hay backlog y/o informe): verifica todo número del
   informe contra su CSV y emite veredicto por pieza del backlog
   (`aprobada / con reparos / rechazada` + motivo + dato que lo sustenta). Marca:
   - Suposiciones no verificadas (afirmaciones sin dato en los CSV).
   - Piezas ancladas a gaps sin demanda externa ni señal interna.
   - Propuestas demasiado genéricas (sin entidad, URL, intención y acción).
   - Acciones no medibles (ver indicadores en Criterios).
   - Confusión entre tráfico de newsletter, tráfico orgánico y visibilidad en
     buscadores generativos.

## Output

Entrega:

```text
1. Diagnóstico breve
2. Top oportunidades
3. Gaps que NO merece la pena perseguir
4. Backlog editorial priorizado
5. Enlaces internos recomendados
6. Experimentos para medir en Search Console
7. Validación crítica (si hay backlog/informe): veredicto por pieza
```

## Criterios

Prioriza temas que cumplan:

- Alta relación con IA generativa, SEO, newsletters, Substack, creación de contenido o automatización editorial.
- Cobertura interna débil.
- Señal externa o Search Console.
- Capacidad de producir una pieza evergreen con utilidad práctica.

Evita recomendaciones genéricas como “mejorar SEO” sin indicar entidad, URL, intención y acción.

Toda recomendación (tuya o del backlog que validas) debe poder medirse con alguno
de estos indicadores:

- Impresiones en Search Console.
- Clicks orgánicos.
- CTR.
- Posición media.
- Nuevas queries por URL.
- Enlaces internos añadidos.
- Número de entidades cubiertas por cluster.

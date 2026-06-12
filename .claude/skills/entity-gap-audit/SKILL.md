---
description: Audita outputs de análisis de entidades de contenido, gaps SEO/GEO y backlog editorial. Úsalo cuando el usuario quiera interpretar outputs/gaps.csv, outputs/editorial_backlog.csv, entities.csv o el grafo de contenido.
allowed-tools: Read Grep Glob Bash
---

## Objetivo

Analiza los outputs del pipeline de entity gaps y entrega un diagnóstico editorial accionable para ganar visibilidad en buscadores.

## Inputs esperados

- `projects/<id>/outputs/entities_curated.csv` (el territorio)
- `projects/<id>/outputs/external_entities.csv` (demanda de Trends)
- `projects/<id>/outputs/gaps.csv`
- `projects/<id>/outputs/editorial_backlog.csv`

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

## Output

Entrega:

```text
1. Diagnóstico breve
2. Top oportunidades
3. Gaps que NO merece la pena perseguir
4. Backlog editorial priorizado
5. Enlaces internos recomendados
6. Experimentos para medir en Search Console
```

## Criterios

Prioriza temas que cumplan:

- Alta relación con IA generativa, SEO, newsletters, Substack, creación de contenido o automatización editorial.
- Cobertura interna débil.
- Señal externa o Search Console.
- Capacidad de producir una pieza evergreen con utilidad práctica.

Evita recomendaciones genéricas como “mejorar SEO” sin indicar entidad, URL, intención y acción.

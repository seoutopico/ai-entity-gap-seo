---
description: Audita outputs de análisis de entidades de contenido, gaps SEO/GEO y backlog editorial. Úsalo cuando el usuario quiera interpretar outputs/gaps.csv, outputs/editorial_backlog.csv, entities.csv o el grafo de contenido.
allowed-tools: Read Grep Glob Bash
---

## Objetivo

Analiza los outputs del pipeline de entity gaps y entrega un diagnóstico editorial accionable para ganar visibilidad en buscadores.

## Inputs esperados

- `outputs/entities.csv`
- `outputs/gaps.csv`
- `outputs/editorial_backlog.csv`
- `outputs/entity_edges.csv`
- `outputs/post_entity_edges.csv`

Si el usuario pasa rutas concretas, usa esas rutas.

## Procedimiento

1. Lee los CSV disponibles.
2. Identifica las 10 entidades con mayor `opportunity_score`.
3. Separa gaps en:
   - `absent_entity`
   - `shallow_coverage`
   - `search_demand_no_clicks`
   - `orphan_entity`
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

# Informe de gaps de entidades — think-hack

## Resumen ejecutivo

Se analizaron las **37 newsletters publicadas** de Think&Hack para mapear de qué
hablas realmente (tu "territorio") y compararlo con lo que la gente busca en
Google (España) alrededor de esos mismos temas. El territorio está claro: IA
generativa, ChatGPT, prompting, contexto y newsletter dominan tu contenido. El
hallazgo principal es que **Claude Code es tu mayor oportunidad**: lo has tocado
en 4 posts (autoridad real), y a su alrededor hay un cluster entero de búsquedas
en crecimiento (qué es, documentación, skills, agents, MCP, precios) que casi
nadie cubre bien en español para perfiles no desarrolladores. La recomendación de
mayor impacto: ejecutar primero las 6 piezas del cluster `claude-code` del
backlog, empezando por la guía práctica para no desarrolladores (top gap del
análisis), seguidas del pilar de prompt engineering y la comparativa de Deep
Research (ChatGPT vs Gemini vs Perplexity), que concentra los gaps consolidados
de puntuación máxima.

## Datos del análisis

| Métrica | Valor |
|---|---|
| Posts analizados (newsletters) | 37 |
| Menciones de entidades extraídas (crudo) | 10.068 (2.858 entidades únicas) |
| Tras limpieza por reglas (`entities.csv`) | 1.791 menciones (839 entidades únicas) |
| Territorio curado (`entities_curated.csv`) | 66 entidades (todas con decisión KEEP) |
| Semillas consultadas en Google Trends | 17 |
| Términos relacionados devueltos por Trends | 1.003 |
| Demanda externa filtrada (`external_entities.csv`) | 370 entidades |
| Gaps detectados (`gaps.csv`) | 354 → 172 *trending* (en crecimiento) + 182 *consolidado* (volumen estable) |
| Piezas en el backlog editorial | 26 → 10 alta · 12 media · 4 baja |
| Acciones del backlog | 21 crear · 3 actualizar · 1 pilar · 1 cluster |

*Gap = tema con demanda de búsqueda alrededor de tu territorio que tu contenido
no cubre (o cubre poco). "Trending" = búsqueda en crecimiento; "consolidado" =
búsqueda con volumen estable.*

## Territorio (lo que ya cubres)

Las entidades curadas con más presencia en tus 37 newsletters (posts en los que
aparecen y suma de relevancia, `salience_sum`):

| Entidad | Posts | Salience acumulada | Lectura |
|---|---|---|---|
| ia | 31 | 4,93 | El eje de todo el corpus: IA aplicada con criterio. |
| chatgpt | 16 | 1,22 | Tu herramienta más tratada; autoridad clara. |
| prompt | 13 | 0,49 | El prompting atraviesa casi la mitad del corpus. |
| contexto | 12 | 0,16 | Memoria/contexto: tema recurrente pero con poca profundidad por pieza. |
| newsletter | 11 | 0,19 | El canal en sí como tema. |
| gemini | 5 | 0,14 | Cobertura incipiente. |
| claude code | 4 | 0,52 | Pocas piezas pero con mucho peso cuando aparece. |
| agentes | 4 | 0,26 | Núcleo del brief, cobertura aún parcial. |
| deep research | 1 | 0,88 | Una sola pieza, pero muy centrada en el tema. |

Qué dice esto de tu posicionamiento: eres fuerte en el discurso general (IA con
criterio, ChatGPT, prompting), pero las entidades donde tienes peso *y* la
demanda está creciendo —**claude code, agentes, deep research**— tienen pocas
piezas (1-4 posts). Ahí es donde un puñado de contenidos nuevos puede convertir
menciones sueltas en autoridad temática.

## Demanda externa y gaps

Google Trends, consultado a partir de 17 semillas de tu territorio, devolvió
370 entidades con demanda real; **354 de ellas son gaps** (no las cubres o las
cubres poco).

**Gaps trending (en crecimiento), los de mayor puntuación:** casi todo el top es
el universo Claude Code — `what is claude code` (0,17), `claude code
documentation` (0,17), `claude code cli` (0,15), `claude code skills` (0,14),
`claude code agents` (0,08), `claude code usage` (0,08) — más `ai agent` (0,06)
y `banana prompt` (0,08, relacionado con Nano Banana). La gente está buscando
ahora mismo lo que tú ya tocas de pasada.

**Gaps consolidados (volumen estable), los de mayor puntuación:** `gemini deep
research` (1,0), `deep research ai` (0,98), `chatgpt deep research` (0,92),
`claude code vs code` (0,98), `claude code mcp` y `claude mcp` (0,33),
`system prompt` (0,18), `prompt injection` (0,18). Demanda madura donde una
buena guía en español puede rankear de forma duradera.

Ojo: en el top consolidado también hay ruido que Trends arrastra y que no es
territorio (ver "Gaps descartados").

## Top oportunidades

Las 10 piezas de **prioridad alta** del backlog, tal cual están priorizadas:

| # | Pieza (título de trabajo) | Cluster | Acción / Formato | Intención | Por qué |
|---|---|---|---|---|---|
| 1 | Claude Code: guía práctica para no desarrolladores | claude-code | crear / guía | informacional | Top gap del corpus (0,17 trending); entidad núcleo con solo 4 posts. Ángulo: criterio, no IDE de programador. |
| 2 | Claude Code agents: automatizar tareas con subagentes | claude-code | crear / tutorial | informacional | Gap `claude code agents` (0,08 trending); cruza dos entidades núcleo (Claude Code + agentes/subagentes). |
| 3 | Claude Code y memoria de contexto: cómo gestionar proyectos largos | claude-code | crear / guía | informacional | Gap `claude code memory` (0,05 trending); conecta con memoria de contexto, núcleo del brief. |
| 4 | Claude Code vs Codex: cuál usar y para qué | claude-code | crear / comparativa | informacional | Gap `codex vs claude code` (0,06 trending); comparativas con criterio son territorio defendible. |
| 5 | MCP y Claude Code: conectar herramientas externas sin código | claude-code | crear / tutorial | informacional | Gaps `claude code mcp` y `claude mcp` (0,33 consolidado); tecnología nueva con demanda creciente. |
| 6 | Agentes de IA: qué son y cómo usarlos sin delegar a ciegas | agentes-ia | crear / guía | informacional | Gap `ai agent` (0,06 trending) + `agentes ia` consolidado; ángulo anti-hype con autoridad real (4+1 posts). |
| 7 | Deep Research comparado: ChatGPT vs Gemini vs Perplexity | deep-research | crear / comparativa | informacional | Gaps consolidados de score máximo (`gemini deep research` 1,0; `deep research ai` 0,98; `chatgpt deep research` 0,92). |
| 8 | Cómo usar Deep Research de Gemini para crear contenido con criterio | deep-research | crear / tutorial | informacional | Gap `gemini deep research` (1,0 consolidado); cobertura actual de 1 post. |
| 9 | Prompt engineering: guía con sistemas reales, no trucos | prompting | **pilar** / guía | informacional | Gap `prompt engineering` (0,04 trending, 2 semillas) + cluster de queries consolidadas; pieza que vertebra todo el prompting. |
| 10 | System prompt: qué es y cómo construir uno que realmente funcione | prompting | crear / guía | informacional | Gap `system prompt` (0,18 consolidado); poca competencia en español con ángulo práctico; enlaza al pilar. |

## Gaps descartados (y por qué)

No todo lo que tiene volumen merece una pieza. Descartes anclados al brief y al
anti-territorio:

- **Ruido de Trends fuera del territorio**, aunque tenga puntuación máxima:
  `maps google` (1,0), `youtube video` (1,0), `mp3 youtube` (0,89), `youtube
  music` (0,82), `chatgpt gratis` (1,0). Son búsquedas genéricas o de consumo
  que el brief no cubre; perseguirlas no construye autoridad en tu tema.
- **Polisemias del anti-territorio**: `la memoria` (1,0 consolidado) es la
  acepción genérica/RAM/canción, no la "memoria de contexto" del brief; lo
  mismo aplica a `nano banana` como fruta. El anti-territorio del proyecto ya
  documenta estas confusiones.
- **Score residual**: `grok ai` (0,0001 trending) — el backlog lo deja en
  prioridad baja, "crear solo si el cluster de herramientas necesita
  completarse".
- **Periférico al brief**: `prompt para fotos profesionales` (0,006 trending) —
  el brief no cubre imágenes como disciplina; solo tiene sentido con un
  experimento real detrás (así lo recoge la pieza de prioridad baja).
- **Sin gap directo de demanda**: n8n es entidad núcleo (1 post) pero no tiene
  gap de alta demanda en español en este corpus; el backlog lo pospone hasta
  que el cluster de automatización tenga piezas ancla.

## Backlog editorial priorizado

Resumen del backlog completo (26 piezas) por cluster:

| Cluster | Piezas | Prioridades | Qué contiene |
|---|---|---|---|
| claude-code | 6 | 5 alta · 1 media | Guía para no developers, agents, memoria, vs Codex, MCP, precios. |
| prompting | 5 | 2 alta · 2 media · 1 baja | Pilar de prompt engineering, system prompt, prompt injection, generadores de prompts, prompts de imagen. |
| herramientas-ia | 5 | 4 media · 1 baja | Google AI Studio, ChatGPT Business vs Claude Pro, NotebookLM+RAG (actualizar), Gemini CLI, Grok. |
| deep-research | 2 | 2 alta | Comparativa ChatGPT/Gemini/Perplexity y tutorial de Gemini Deep Research. |
| agentes-ia | 2 | 1 alta · 1 media | Guía de agentes sin delegar a ciegas; IA agéntica. |
| automatizacion | 2 | 1 media · 1 baja | WordPress + MCP; n8n primer flujo. |
| seo-geo | 2 | 2 media/baja | AI Overviews y SEO 2026 (actualizar); CTR y AI Overviews (actualizar). |
| cluster-claude-code | 1 | 1 media | Acción estructural: arquitectura de enlaces internos entre las guías de Claude Code. |
| nano-banana | 1 | 1 media | Prompts para Nano Banana Pro. |

De las 26 piezas, 21 son contenido nuevo, 3 son actualizaciones de posts que ya
existen (NotebookLM, AI Overviews, CTR), 1 es la pieza pilar de prompting y 1 es
trabajo de arquitectura de enlaces (no contenido).

## Próximos pasos y medición

1. **Publica primero el cluster `claude-code`** en este orden: la guía práctica
   para no desarrolladores (pieza ancla), luego agents, memoria de contexto,
   vs Codex y MCP. Cierra con la pieza de precios (intención comercial) cuando
   las informacionales ya enlacen entre sí.
2. **Ejecuta la acción de cluster** (`cluster-claude-code`): cada pieza nueva de
   Claude Code debe enlazar a la guía ancla y la ancla a todas; añade enlaces
   desde tus 4 posts existentes que ya mencionan Claude Code.
3. **En paralelo o justo después**, el pilar de prompt engineering + system
   prompt (se enlazan entre sí) y la comparativa de Deep Research, que ataca
   los gaps consolidados de puntuación máxima.
4. **Las 3 actualizaciones** (NotebookLM+RAG, AI Overviews 2026, CTR) son
   victorias rápidas: contenido ya indexado al que solo añades el ángulo con
   demanda.
5. **Medición en Search Console** (experimento por pieza, 6-8 semanas tras
   publicar): impresiones y posición media para las queries del gap que motivó
   cada pieza (p. ej. "claude code", "system prompt", "gemini deep research");
   CTR de las piezas actualizadas antes vs después; y qué piezas empiezan a
   aparecer citadas en AI Overviews para sus queries objetivo.
6. **Re-corre el análisis** cuando hayas publicado el primer cluster: los gaps
   trending caducan rápido y conviene verificar si el territorio nuevo ya
   absorbe demanda antes de atacar las prioridades medias.

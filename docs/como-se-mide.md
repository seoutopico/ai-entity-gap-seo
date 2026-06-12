# Cómo se mide

Qué significa cada número del sistema, de dónde sale y cómo leerlo. Ninguno es
magia: cada uno tiene una fuente concreta y un archivo donde verlo.

## Lo primero: tres advertencias honestas

1. **Google Trends da interés relativo, no volumen.** Un score de 100 no son
   100 búsquedas: es el máximo de esa consulta. Sirve para **comparar y
   ordenar**, no para prometer tráfico.
2. **Salience no es tráfico.** Mide cuánto cubres tú un tema, no cuánto se busca.
   Son los dos ejes del análisis y no deben confundirse.
3. **Rising y top no son comparables entre sí** (uno es % de crecimiento, el
   otro una escala 0-100). Por eso se normalizan por separado.

## Señales de tu contenido (Google Natural Language)

En `entities_raw.csv` / `entities.csv` — una fila por mención:

| Señal | Qué es | Cómo se lee |
|---|---|---|
| `salience` | Centralidad de la entidad en ese post (0-1) | 0.4 = el post va de eso; 0.003 = mención de pasada |
| `mid` | ID en el Knowledge Graph de Google | Si existe, Google reconoce la entidad. Las que más pesan para SEO/GEO |
| `wikipedia_url` | Página de Wikipedia enlazada | Confirma a qué entidad concreta se refiere |
| `mentions` | Veces que aparece en el post | Frecuencia bruta; menos informativa que salience |
| `type` / `google_type` | Tipo del dominio (brief) / tipo de Google | `tool`, `concept`, `platform`… vs `PERSON`, `ORG`… |

En `entities_curated.csv` — una fila por entidad del territorio (agregado):

| Señal | Cómo se calcula | Qué mide |
|---|---|---|
| `posts` | nº de posts distintos donde aparece | **Amplitud** de tu cobertura |
| `salience_sum` | suma de la salience de todas sus menciones | **Profundidad** de tu cobertura |

*Lectura conjunta:* "ia" con 31 posts y salience_sum 4.93 = tema dominante.
"claude code" con 4 posts y salience_sum 0.52 = cobertura débil — y como además
tiene demanda alta, ahí hay oportunidad.

## Señales de demanda (Google Trends)

En `external_entities.csv` — una fila por término con demanda:

| Señal | Qué es | Cómo se lee |
|---|---|---|
| `score` | Valor máximo que dio Trends al término | Magnitud bruta (escalas distintas según rising/top) |
| `rising` | 1 = tendencia ascendente · 0 = consolidado | `rising=1` con score alto = oportunidad temprana |
| `seeds` | nº de entidades tuyas alrededor de las cuales apareció | 2+ = el término orbita tu territorio por varios lados |
| `score_norm` | `score` normalizado 0-1 **dentro de su grupo** (rising o top, por separado) | **El número para priorizar.** Hace comparables las dos escalas |

## Los gaps (`gaps.csv`)

Un gap = término de `external_entities.csv` que **no** está en
`entities_curated.csv` (matching exacto por entidad canónica). Hereda las señales
de demanda y añade:

| Señal | Valores | Significado |
|---|---|---|
| `gap_type` | `trending` | demanda al alza que no cubres — atácala pronto |
| | `consolidado` | demanda estable que no cubres — pieza evergreen |

El cálculo es determinista (script): con los mismos CSV de entrada salen
exactamente los mismos gaps. El **juicio** sobre qué hacer con ellos es de la
fase siguiente.

## El backlog (`editorial_backlog.csv`)

Aquí los números se convierten en decisiones. Cada pieza lleva:

| Campo | Valores | Qué decide |
|---|---|---|
| `prioridad` | alta / media / baja | orden de ataque — pesa autoridad temática, no solo volumen |
| `accion` | crear / actualizar / cluster / pilar / enlazar | qué hacer exactamente |
| `intencion` | informacional / comercial / transaccional | para qué busca eso la gente |
| `formato` | guía, tutorial, comparativa… | la forma que pide esa intención |
| `entidades` | lista | qué gaps cubre la pieza (varias por pieza) |
| `justificacion` | texto | el porqué, **citando datos reales** (posts, score_norm) y el brief |

*Regla de oro de la priorización:* un gap genérico con score enorme ("ai",
score_norm alto) puede valer menos que uno modesto y defendible ("claude code
mcp"): en el primero no tienes autoridad ni ángulo; en el segundo, sí. Por eso
esta fase es de un agente con el brief, no de una fórmula.

## Qué número mirar según tu pregunta

| Pregunta | Mira |
|---|---|
| ¿De qué hablo yo de verdad? | `entities_curated.csv` ordenado por `salience_sum` |
| ¿Qué busca la gente cerca de mí? | `external_entities.csv` por `score_norm` |
| ¿Qué me falta cubrir? | `gaps.csv` (los `trending` primero) |
| ¿Qué escribo y en qué orden? | `editorial_backlog.csv` por `prioridad` |
| ¿El resumen de todo? | `informe.md` |

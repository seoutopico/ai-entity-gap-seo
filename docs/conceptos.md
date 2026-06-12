# Conceptos

Cada término del sistema, en cristiano y con un ejemplo real del proyecto
[think-hack](../projects/think-hack/) (37 newsletters sobre IA aplicada).

## Entidad

Una "cosa" con nombre de la que habla tu contenido: una herramienta (ChatGPT), un
concepto (deep research), una plataforma (Substack). No es una palabra frecuente —
es algo que un buscador entiende como **una cosa concreta del mundo**.

La diferencia importa: el SEO clásico contaba keywords; los buscadores de hoy (y
los buscadores con IA) entienden entidades y **relaciones entre ellas**. "Claude
Code" no son dos palabras: es una entidad con su ficha en el grafo de Google.

## Salience

Cuán **central** es una entidad dentro de un texto, de 0 a 1. La calcula Google
Natural Language al leer cada post.

- `salience 0.4` → el post **va de eso**.
- `salience 0.003` → se nombró de pasada.

*Ejemplo real:* en think-hack, "ia" acumula salience 4.93 repartida en 31 posts
(tema central del proyecto); "archigram" aparece una vez con salience mínima
(una referencia puntual, no territorio).

## Knowledge Graph y `mid`

El Knowledge Graph es la base de datos de entidades de Google. Si una entidad
tiene `mid` (un identificador tipo `/m/0mkz`), Google **la reconoce y la tiene
desambiguada**. Para SEO/GEO son las que más pesan: son las que Google puede
conectar con tu contenido sin ambigüedad.

## Territorio

El conjunto de temas que **son tuyos**: aquello de lo que hablas con autoridad
real. No lo decide una fórmula — lo decide un agente de IA leyendo tu contenido
contra el **brief** del proyecto. En think-hack: IA generativa, prompting,
agentes, SEO/GEO, newsletters.

## Anti-territorio

Los **sentidos a excluir** para que la polisemia no meta ruido. Es la pieza más
importante para la calidad del análisis:

- *"memoria"* en think-hack es memoria de contexto de un LLM — **no** la RAM, ni
  la canción de Rosalía, ni el videojuego.
- *"agentes"* son agentes de IA — **no** agentes forestales ni de Hacienda
  (ambos aparecían de verdad en los datos de Google Trends).

El anti-territorio **crece solo**: cada ejecución detecta sentidos nuevos a
excluir y los apunta en el brief, así la siguiente vuelta es más limpia.

## Brief

La ficha de contexto del proyecto (`project.json`): tema, audiencia, idioma,
entidades núcleo, anti-territorio, tono de marca. **La rellena la IA leyendo tu
contenido** (no te entrevista); tú solo la validas. Es el ancla de todas las
decisiones cualitativas: ningún agente decide "porque sí", decide "porque el
brief dice".

## Demanda externa

Lo que la gente **busca de verdad** alrededor de tu territorio, según Google
Trends. Dos sabores:

- **Consolidado** (top): demanda estable. Ej.: *"gemini deep research"*.
- **Rising**: demanda en tendencia ascendente. Oportunidad temprana, antes de
  que el hueco se llene. Ej.: *"what is claude code"*.

## Gap

**El concepto central del sistema**: un término con demanda (aparece en Trends
alrededor de tu territorio) que **no está cubierto** en tu contenido. La gente lo
busca; tú no lo tienes. En think-hack salieron 354 gaps; el mayor cluster fue
Claude Code (la gente busca "what is claude code", "claude code tutorial",
"claude code mcp"… y la newsletter solo lo tocaba de pasada en 4 posts).

## Cluster y pilar

Un **cluster** es el grupo de contenidos sobre un mismo subtema (todo lo de
"Claude Code"). El **pilar** es la pieza grande y central del cluster (la guía
completa); los demás artículos cuelgan de ella y la enlazan. Los buscadores
premian cubrir el árbol entero, no piezas sueltas.

## SEO y GEO

- **SEO**: posicionar en buscadores clásicos (Google).
- **GEO**: que los buscadores con IA (AI Overviews, ChatGPT, Perplexity) te
  **citen** en sus respuestas. Las entidades importan aún más aquí: los modelos
  razonan sobre cosas, no sobre keywords.

## Backlog editorial

El entregable: una lista priorizada de piezas con **qué** escribir (entidades),
**cómo** (formato e intención de búsqueda), **qué hacer** (crear, actualizar,
pilar, cluster) y **por qué** (justificación anclada al brief y a los datos).
En think-hack: 26 piezas (10 de prioridad alta).

## Arnés

El verificador (`bin/check.py`). Comprueba contra el disco que cada fase
realmente hizo lo que dice haber hecho: que su archivo de evidencia existe,
tiene contenido y respeta el formato pactado. Si algo miente, el sistema se
para. Es lo que hace al pipeline fiable aunque lo ejecute una IA.

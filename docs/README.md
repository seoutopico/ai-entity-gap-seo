# Documentación

Sistema que lee tu archivo de contenido, detecta **qué busca la gente que tú no
cubres** (gaps de entidades) y lo convierte en un **backlog editorial priorizado**
con un **informe final**. Repetible, auditable y manejable por conversación bajo
Claude Code.

> La idea en una frase: dato **cuantitativo → script** (determinista); dato
> **cualitativo → IA** como clasificador anclado a un brief, no como oráculo.
> Y nada se da por hecho sin evidencia en disco.

## Por dónde empezar

**Si no eres técnico**, lee en este orden:

1. [Conceptos](conceptos.md) — qué significa cada cosa (entidad, salience, gap…), con ejemplos reales.
2. [El pipeline](el-pipeline.md) — qué hace el sistema, fase a fase, y quién decide qué.
3. [Cómo se mide](como-se-mide.md) — qué significan los números (puedes saltarte las fórmulas).

**Si eres técnico**, añade:

4. [Arquitectura](arquitectura.md) — cómo está construido, los contratos, el arnés y por qué.

## Mapa

| Documento | Para quién | Responde a |
|---|---|---|
| [conceptos.md](conceptos.md) | todos | ¿qué significa esa palabra? |
| [el-pipeline.md](el-pipeline.md) | todos | ¿qué hace, paso a paso, y quién lo hace? |
| [como-se-mide.md](como-se-mide.md) | todos (detalle técnico opcional) | ¿de dónde sale cada número y cómo lo leo? |
| [arquitectura.md](arquitectura.md) | técnicos | ¿cómo se sostiene y por qué está diseñado así? |

Los ejemplos de toda la documentación salen de un proyecto real incluido en el
repo: [`projects/think-hack/`](../projects/think-hack/), el análisis de 37
newsletters de Think&Hack, ejecutado de la fase 0 a la 8.

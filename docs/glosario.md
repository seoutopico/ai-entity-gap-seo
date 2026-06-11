# Glosario

Términos que aparecen en el sistema, en cristiano.

**Entidad.** Una "cosa" con nombre de la que habla tu contenido: una herramienta
(ChatGPT), un concepto (deep research), una plataforma (YouTube). No es una palabra
suelta ("contenido") sino algo que un buscador entiende como una cosa concreta.

**Salience.** Cuán **central** es una entidad en un texto (0 a 1). Alta = el post va
de eso; baja = se nombró de pasada.

**Knowledge Graph / `mid`.** La base de datos de entidades de Google. Si una entidad
tiene `mid`, Google "la entiende" como entidad real. Son las que más importan para
salir en búsquedas e IA.

**SEO.** Salir bien posicionado en los buscadores clásicos (Google).

**GEO.** Lo mismo pero para los **buscadores con IA** (AI Overviews de Google,
ChatGPT…): que te **citen** en sus respuestas.

**Gap (hueco).** Un tema que la gente **busca** y tú **no cubres**. La oportunidad.

**Territorio.** El conjunto de temas que **son tuyos** (de lo que hablas con
autoridad). Vive en el brief del proyecto.

**Anti-territorio.** Sentidos que hay que **excluir** para no confundir. Ej: "memoria"
en tu contenido es memoria de IA, no la RAM ni una canción. Evita traer ruido.

**Brief.** La ficha de contexto de tu proyecto (`project.json`): tema, audiencia,
idioma, entidades núcleo, anti-territorio, tono. La **rellena la IA leyendo tu
contenido**, no tú a mano.

**Topical map (mapa temático).** Dibujo de tu territorio: tema central → clusters →
piezas. Sirve para ver de un vistazo qué cubrir.

**Cluster.** Un grupo de contenidos sobre el mismo subtema (p.ej. todo lo de "Claude
Code"). Es el **árbol entero**: pilar + satélites.

**Pilar.** La pieza **grande y central** de un cluster (una guía completa). El tronco
del árbol. Los demás artículos (satélites) cuelgan de ella y la enlazan.

**Rising vs Top (Google Trends).** `rising` = en **tendencia ascendente** (oportunidad
temprana). `top` = demanda **consolidada** (estable).

**Skill.** Un procedimiento que la IA ejecuta cuando se lo pides (ej.
`/nuevo-proyecto`). Empaqueta una receta repetible.

**Agente / subagente.** Una IA especializada con un rol acotado y su propio criterio
(ej. el que decide qué entidades son territorio). Trabaja aislado y devuelve un
resultado.

**Script.** Código que hace una tarea mecánica y determinista (siempre igual): contar,
filtrar, llamar a una API.

**Arnés (harness).** La infraestructura que rodea a la IA y la mantiene a raya:
verifica, pone límites, deja rastro. Aquí, `bin/check.py`.

**Default-FAIL.** Principio del arnés: **nada se da por hecho** hasta que se demuestra.
Si dices "extracción hecha" pero no existe el archivo, el check **falla**.

**Salience acumulada.** La suma de salience de una entidad en todo tu archivo = cuánto
la cubres en total.

**Unidad (coste).** 1.000 caracteres enviados a Google NL. Gratis hasta 5.000/mes.

➡️ Volver al [índice](README.md).

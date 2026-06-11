---
name: nuevo-proyecto
description: |
  Crea un proyecto de análisis de entidades a partir de un contenido (carpeta de
  .md, un CSV o un feed). Crea projects/<nombre>/, ingiere el contenido y rellena
  el brief (project.json) LEYENDO el contenido, sin entrevistar al usuario.
  Úsalo cuando el usuario diga "crea un proyecto con este contenido", "analiza
  estas newsletters", "nuevo proyecto sobre ...".
argument-hint: [nombre-proyecto] [ruta-al-contenido]
allowed-tools: Read Write Bash Glob Grep
---

## Objetivo

Dejar listo un proyecto con su contenido ingerido y su **brief autocompletado**,
para que las fases siguientes (extracción → limpieza → trends → gaps) tengan
contexto. El brief lo rellenas **tú (la IA)** leyendo el contenido. **No
entrevistes al usuario**: rellenas y luego le muestras el brief para que lo valide
o corrija hablando.

## Procedimiento

1. **Nombre y fuente.** Del `$ARGUMENTS`: primer término = nombre del proyecto
   (pásalo a slug kebab-case), segundo = ruta del contenido. Si falta el nombre,
   dedúcelo del contenido.

2. **Estructura.** Crea:
   ```
   projects/<slug>/
     data/raw/
     outputs/
   ```

3. **Ingesta del contenido → `projects/<slug>/data/raw/posts.csv`:**
   - Si es una carpeta o glob de `.md`:
     ```bash
     python src/md_to_posts.py "<ruta>/*.md" --out projects/<slug>/data/raw/posts.csv
     ```
   - Si ya es un CSV con columnas `url,title,published,text`: cópialo a esa ruta.

4. **Brief.** Copia `projects/_template/project.json` a
   `projects/<slug>/project.json`. Lee una muestra representativa del contenido
   (títulos + extractos de varios posts) y **rellena el `brief`**:
   - `tema`: territorio editorial en 1-2 frases.
   - `audiencia`, `objetivo` (seo|geo|ambos), `idioma`, `geo`.
   - `entidades_nucleo`: lo que SÍ es el terreno (marcas, herramientas, conceptos recurrentes).
   - `anti_territorio`: **sentidos a EXCLUIR** para desambiguar después. Detecta
     términos polisémicos del corpus y anota el sentido NO deseado (p.ej.
     `"memoria = RAM"`, `"memoria = canción"`, `"nano banana = fruta"`).
   - `tono_marca`: voz y estilo.
   - Rellena `nombre_proyecto`, `fecha_creacion` (fecha de hoy), `fuente_contenido`.
   - En `estado`, deja todo en `false` (aún no se ha procesado nada).
   - Quita las claves `_template`, `_instrucciones`.

5. **Validación.** Muestra al usuario el brief generado en lenguaje natural y
   pídele que confirme o ajuste por voz. Aplica los cambios que pida.

## Límites

- No ejecutes la extracción ni Trends aquí: este skill solo prepara el proyecto.
- No inventes datos del brief que no estén soportados por el contenido leído.
- No pidas al usuario que rellene campos: los rellenas tú y él valida.

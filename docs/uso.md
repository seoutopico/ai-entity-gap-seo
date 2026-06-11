# Cómo se usa

Dos formas: **hablando con Claude Code** (no técnico) o **por línea de comandos**
(técnico). Hacen lo mismo por debajo.

## Preparación (una vez)

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # pega tu GOOGLE_NL_API_KEY (único secreto)
```

Necesitas una API key gratuita de **Google Cloud Natural Language API**. El sistema
nunca sale de la capa gratuita (tope en el código).

## Modo conversación (no técnico)

En Claude Code, hablando:

1. **Crear el proyecto** — *"Crea un proyecto con las newsletters de esta carpeta: …"*
   → la IA crea `projects/<id>/`, ingiere el contenido y **rellena el brief** leyéndolo.
   Te lo muestra para que lo valides ("¿el tema y las entidades núcleo son correctas?").
2. **Extraer y limpiar** — *"Extrae las entidades y límpialas."*
3. **Curar** — *"Haz la limpieza semántica con el brief."* (decide territorio/ruido)
4. **Demanda** — *"Busca la demanda en Trends."*
5. **Backlog** — *"Genérame el backlog editorial."* → tu plan de contenidos.
6. **Mapa** — *"Hazme el topical map."* → diagrama del territorio (Mermaid).

En cualquier momento: *"¿está todo bien?"* → corre el arnés (`bin/check.py`).

## Modo CLI (técnico)

```bash
# 0. Proyecto (la skill lo hace; manual con md_to_posts):
python src/md_to_posts.py "ruta/*.md" --out projects/<id>/data/raw/posts.csv

# 1-2. Extracción + limpieza objetiva (lee idioma/ontología del brief con --project)
python src/extract_entities.py --project <id>
python src/clean_entities.py   --project <id>

# 3. Limpieza semántica -> agente entity-curator (lee el brief)

# 4. Demanda (geo/idioma del brief; filtro de relevancia)
python src/fetch_trends.py --project <id>

# Arnés: salud + Default-FAIL
python bin/check.py <id>
```

## El resultado (dónde mirar)

Todo en `projects/<id>/outputs/`:

| Archivo | Qué es |
|---|---|
| `editorial_backlog.csv` | **el entregable**: piezas priorizadas (ábrelo en Excel) |
| `topical_map.md` | el mapa del territorio (Mermaid → Obsidian / mermaid.live) |
| `gaps.csv` | demanda no cubierta (rising/consolidado, score) |
| `entities_curated.csv` | tu territorio (137 entidades, en el caso think-hack) |
| `external_entities.csv` | demanda de Trends filtrada |

## Caso de ejemplo incluido

`projects/think-hack/` es un análisis real de 37 newsletters, completo de la fase 0 a
la 7. Úsalo como referencia de cómo se ve cada output.

> Nota: tras crear skills/agentes nuevos, **reinicia Claude Code** para que aparezcan
> en `/` y en la lista de agentes.

➡️ Cómo está construido por dentro: [arquitectura](arquitectura.md).

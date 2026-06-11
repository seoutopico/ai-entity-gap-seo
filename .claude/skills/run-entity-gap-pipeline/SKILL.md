---
description: Ejecuta y valida el pipeline local de análisis de entidades y gaps de contenido. Úsalo cuando el usuario quiera correr el MVP, regenerar outputs o comprobar si el sistema funciona.
argument-hint: [config-path]
allowed-tools: Read Bash Glob Grep
---

## Instrucciones

Usa `$0` como ruta de configuración si el usuario la proporciona. Si no, usa `config/config.yml`.

1. Comprueba que existen:
   - `src/run_pipeline.py`
   - `src/extract_entities.py`
   - `src/compare_gaps.py`
   - archivo de configuración
2. Si no existe `config/config.yml`, copia `config/config.example.yml` y avisa de que falta configurar `source.substack_feed_url` o `source.posts_csv`.
3. Ejecuta:

```bash
python src/run_pipeline.py --config $0
```

Si el feed de Substack no está configurado, usa:

```bash
python src/run_pipeline.py --config $0 --skip-ingest
```

4. Verifica que se han creado:
   - `outputs/entities.csv`
   - `outputs/gaps.csv`
   - `outputs/editorial_backlog.csv`
   - `outputs/graph.graphml`
5. Resume errores concretos. No digas que el pipeline funciona si faltan outputs.

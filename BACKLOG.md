# Backlog — Entity Gap MVP

Mejoras y cambios pendientes, ordenados por impacto hacia el objetivo: **ganar
visibilidad en buscadores y motores generativos (SEO/GEO)**.

Estado: `[ ]` pendiente · `[~]` parcial · `[x]` hecho.

---

## ✅ Hecho en esta iteración (2026-06)

- [x] Sustituir extracción TF-IDF por **Google NL API** (`analyzeEntities` v1: salience + mid + wikipedia_url).
- [x] Key vía `.env`; topes de coste por ejecución y **tope mensual persistente** (5.000 unidades = capa gratuita).
- [x] Capa de **limpieza configurable** (`clean_entities.py`) sobre cache crudo, sin re-llamar a la API.
- [x] Módulo **`fetch_trends.py`** (trendspy) con `related_queries`/`related_topics`, cache acumulativo y delay.
- [x] Ingesta real de las 37 newsletters publicadas (`md_to_posts.py`).

---

## P0 — Desbloquea el objetivo (gaps creíbles)

- [ ] **Afinar selección de semillas de Trends.** Excluir genéricas ambiguas
  (`memoria`, `ia` → traen Rosalía, RAM, videojuegos) y priorizar entidades con
  `mid` (Knowledge Graph). Añadir `seed_blocklist` + `prefer_mid` en `config.yml`.
  *(src/fetch_trends.py, config: trends)*
- [x] **Normalizar `rising` vs `top` por separado.** Hecho: `normalize_scores` escala
  0-1 dentro de cada grupo (`score_norm`). *(src/fetch_trends.py)*
- [ ] **Conectar el GSC real.** Exportar Search Console de `ainalluna.substack.com`
  y sustituir `data/raw/gsc_queries.csv` (hoy de juguete). Es la señal de demanda
  propia más fiable (impresiones sin clics = oportunidad inmediata).
  *(data/raw, compare_gaps.py)*
- [ ] **Cerrar el loop.** Correr `build_graph` + `compare_gaps` con entidades limpias
  + demanda de Trends → generar `gaps.csv` y `editorial_backlog.csv` reales.
  *(run_pipeline.py)*
- [ ] **Revisar pesos del `opportunity_score`.** Hoy: external 0.45 / GSC 0.35 /
  internal_gap 0.20, heredados del mundo TF-IDF. Recalibrar con las fuentes nuevas
  (Trends + GSC real). *(config: scoring)*

## P1 — Calidad de datos

- [x] **Filtro de relevancia en términos de Trends.** Hecho: `filter_relevant` usa el
  territorio (entidades curadas + entidades_nucleo) y el `anti_territorio` del brief.
  Pendiente menor: semillas demasiado amplias (`google`/`youtube`) aún cuelan ruido
  tangencial (`product`, `mp3 youtube`). *(src/fetch_trends.py)*
- [ ] **Limpieza residual de entidades internas:**
  - [ ] Bajar `max_entity_words` a 4-5 (aún pasan títulos: "gpt-5 prompting guide").
  - [ ] Añadir genéricos mal tipados como `person` a la blocklist (`terapeuta`,
    `creador`, `generador`).
  - [ ] Decidir qué hacer con conceptos genéricos `other` (`texto`, `datos`,
    `sistema`, `método`): ¿temas útiles o ruido? *(config: cleaning)*
- [ ] **Aprovechar métricas propias del frontmatter.** Cada `.md` trae `views`,
  `open_rate`, `click_through_rate`, `engagement_rate`. El conversor las ignora.
  Capturarlas para priorizar: entidades que viven en posts de alto rendimiento.
  *(src/md_to_posts.py, scoring)*
- [ ] **Regenerar grafo + notas Obsidian** con las entidades limpias (las antiguas
  se borraron por ruido). *(build_graph.py)*

## P2 — Robustez y mantenimiento

- [ ] **Tests** para `clean_entities` y `fetch_trends` (con mocks de la API/Trends).
  Hoy solo existe `tests/test_utils.py`. *(tests/)*
- [ ] **Actualizar el subagente `entity-extractor.md`** — describe el mundo TF-IDF;
  reescribir para salience + mid + tipos de Google. *(.claude/agents/)*
- [ ] **Documentar el flujo nuevo en el README** (`clean_entities`, `fetch_trends`).
- [ ] **Tipado por Knowledge Graph.** Usar `mid`/`wikipedia_url` para tipar en vez de
  la ontología regex manual (que hay que mantener a mano). *(clean_entities.py)*
- [ ] **Consultar Trends por topic (`mid`) en vez de keyword** para desambiguar
  semillas (ej. resolvería el problema de "memoria"). *(fetch_trends.py)*
- [ ] **Forzar Wikipedia en español** en el linking donde exista (hoy casi todo
  resuelve a `en.wikipedia.org`). *(extract_entities.py)*

## Backlog futuro (descartado por ahora)

- [ ] **Competidores / SERP reales** como fuente de gaps de cobertura (external_posts
  reales vía SerpAPI/DataForSEO o export manual). Es un *update* posterior.
- [ ] **Volumen de búsqueda absoluto** (Trends solo da relativo). Requiere API de
  pago; solo si hace falta magnitud exacta para priorizar.
- [ ] **`interest_over_time`** de Trends (da 429 con frecuencia). No crítico: el
  `rising` de related_queries ya aporta señal de tendencia.

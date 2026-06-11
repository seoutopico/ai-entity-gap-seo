# Cómo se mide todo

Qué significan los números que produce el sistema y cómo leerlos. Ninguno es magia:
cada uno viene de una fuente concreta.

## Señales de extracción (Google NL API)

| Señal | Qué es | Cómo se lee | Dónde |
|---|---|---|---|
| **`salience`** | Relevancia de la entidad **dentro de ese texto**, 0–1 | 0.4 = núcleo del post · 0.001 = mención de pasada. Es lo que distingue "tema central" de "lo nombré una vez". | `entities*.csv` |
| **`mid`** | ID de la entidad en el **Knowledge Graph de Google** (`/m/...`) | Si lo tiene, Google **la reconoce como entidad** (está desambiguada). Oro para SEO/GEO. Si está vacío, es un concepto común sin enlazar. | `entities*.csv`, `mid` |
| **`wikipedia_url`** | Página de Wikipedia enlazada | Confirma a qué entidad concreta se refiere. | `entities*.csv` |
| **`mentions`** | Nº de veces que aparece en el documento | Frecuencia bruta (menos importante que salience). | `entities*.csv` |
| **`type` / `google_type`** | Tipo de la entidad | `type` = el de tu dominio (del brief: tool/concept/platform…). `google_type` = el que dio Google (PERSON, ORG…). | `entities*.csv` |

**Salience acumulada** (`salience_sum`): al juntar todas las menciones de una entidad
en el corpus, se **suman** sus salience. Es la medida de **cuánto cubres** ese tema.

## Señales de demanda (Google Trends)

Trends da interés **relativo**, no volumen absoluto. Hay dos tipos y **no son
comparables entre sí**, por eso se normalizan por separado:

| Señal | Qué es | Cómo se lee |
|---|---|---|
| **`top`** | Términos consolidados que la gente busca alrededor de la semilla | Escala 0–100 dentro de la consulta. Demanda estable. |
| **`rising`** | Términos en **tendencia ascendente** | Valores enormes (% de crecimiento, "Breakout"). Oportunidad **temprana**. |
| **`score_norm`** | El valor anterior **normalizado 0–1 dentro de su grupo** (rising o top) | Permite ordenar de forma justa sin mezclar las dos escalas. **Úsalo para priorizar.** |
| **`rising` (flag)** | 1 = tendencia · 0 = consolidado | Un gap `rising=1` con score alto = atácalo ya. |

## Qué es un "gap" y cómo se prioriza

Un **gap** = un término con **demanda** (aparece en Trends) que **no está en tu
territorio** (no está en `entities_curated.csv`).

- `gap_type = trending` → tendencia ascendente (rising). Oportunidad temprana.
- `gap_type = consolidado` → demanda estable (top).

El **backlog** ordena los gaps en piezas con **prioridad**:
- 🔴 **alta** — entidad núcleo del brief + demanda alta + cobertura baja.
- 🟠 **media** — relacionada con el territorio, demanda media.
- 🔵 **baja** — variantes secundarias (se agrupan en un "recopilatorio").

> La prioridad NO es solo volumen: pesa la **autoridad temática** (¿es tu terreno?)
> sobre el volumen aislado. Eso lo decide el agente `gap-strategist` con el brief.

## `opportunity_score` (scoring formal, en revisión)

`compare_gaps.py` calcula un score combinando señales con pesos (`config: scoring`):

```
opportunity_score = 0.45·externo + 0.35·search_console + 0.20·gap_interno
```

⚠️ Estos pesos son **heredados** y están **pendientes de recalibrar** con las fuentes
nuevas (Trends + GSC real). Ver el backlog en [arquitectura](arquitectura.md).

## Coste (Google NL API)

| Métrica | Valor |
|---|---|
| Unidad de facturación | 1 unidad = 1.000 caracteres |
| Capa gratuita | 5.000 unidades/mes |
| Tope en el código | `monthly_unit_cap: 5000` — **nunca lo supera** |
| Contador persistente | `.usage/nl_usage.json` (acumula entre ejecuciones, resetea cada mes) |

Ejemplo real: 37 newsletters = **288 unidades** (5,8% de la capa gratuita) = **0 €**.

## Cómo verificar que un resultado es real

El arnés (`bin/check.py`) aplica **Default-FAIL**: una fase marcada como "hecha" en
`project.json` **falla** si no existe su archivo de evidencia. No te fías del informe;
compruebas el archivo. `exit 0` = sano · `exit 2` = algo miente, para.

➡️ Glosario de términos en [glosario.md](glosario.md).

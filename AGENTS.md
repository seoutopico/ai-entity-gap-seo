# Instrucciones para agentes de IA

La fuente de verdad única de este repo es **[`CLAUDE.md`](CLAUDE.md)**: léelo
entero y obedécelo antes de tocar nada. No se duplica aquí para que no diverja.

Lo mínimo que debes saber antes de leerlo:

- Hay un pipeline por fases con productores fijos (scripts deterministas y
  agentes). **No te saltes fases ni sustituyas a un agente con un script ad-hoc.**
- Corre `python bin/check.py <id>` antes de trabajar y después de cada fase.
  Implementa Default-FAIL: si sale con código 2, para y arregla; no continúes.
- Cada output tiene columnas EXACTAS (contrato en `projects/_template/outputs/`).
- Topes de coste de API blindados: no los subas ni los quites.

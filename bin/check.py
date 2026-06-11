#!/usr/bin/env python
"""
Check de salud del arnés (Pilar 1 + Default-FAIL).

Corre ANTES de trabajar. Si algo está roto, sale con código 2 y el proceso debe
parar. Implementa Default-FAIL: una fase marcada `true` en project.json -> estado
solo se da por buena si su evidencia (el CSV de salida) existe y no está vacía.
El check no se fía del informe; comprueba el archivo real.

Uso:
    python bin/check.py                # valida el repo base y lista proyectos
    python bin/check.py think-hack     # valida además ese proyecto
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

ROOT = Path(__file__).resolve().parent.parent

# Fase del estado -> archivo de evidencia (dentro de projects/<id>/outputs/).
PHASE_EVIDENCE = {
    "extraccion": "entities_raw.csv",
    "limpieza_objetiva": "entities.csv",
    "limpieza_semantica": "entities_curated.csv",
    "demanda_trends": "trends_related.csv",
    "gaps": "gaps.csv",
    "backlog": "editorial_backlog.csv",
}

_fail = False


def ok(msg: str) -> None:
    print(f"[ok]   {msg}")


def fail(msg: str) -> None:
    global _fail
    _fail = True
    print(f"[FALLO] {msg}")


def warn(msg: str) -> None:
    print(f"[warn] {msg}")


def _csv_has_rows(path: Path, min_rows: int = 1) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # cabecera
        return sum(1 for _ in zip(range(min_rows), reader)) >= min_rows


def check_base() -> None:
    print("== Repo base ==")
    if (ROOT / "config/config.yml").exists():
        ok("config/config.yml presente")
    else:
        fail("falta config/config.yml (copia config.example.yml)")

    for script in ("extract_entities.py", "clean_entities.py", "fetch_trends.py"):
        if (ROOT / "src" / script).exists():
            ok(f"src/{script} presente")
        else:
            fail(f"falta src/{script}")

    env = ROOT / ".env"
    if not env.exists():
        fail(".env no existe (copia .env.example y añade GOOGLE_NL_API_KEY)")
    else:
        content = env.read_text(encoding="utf-8", errors="ignore")
        has_key = any(
            line.strip().startswith("GOOGLE_NL_API_KEY=") and line.split("=", 1)[1].strip()
            for line in content.splitlines()
        )
        ok("GOOGLE_NL_API_KEY configurada en .env") if has_key else fail(
            "GOOGLE_NL_API_KEY vacía o ausente en .env"
        )

    usage = ROOT / ".usage/nl_usage.json"
    if usage.exists():
        try:
            u = json.loads(usage.read_text(encoding="utf-8"))
            print(f"       consumo mes {u.get('month','?')}: {u.get('units',0)}/5000 unidades")
        except (json.JSONDecodeError, OSError):
            warn(".usage/nl_usage.json ilegible")


def check_project(project_id: str) -> None:
    print(f"\n== Proyecto: {project_id} ==")
    pdir = ROOT / "projects" / project_id
    if not pdir.exists():
        fail(f"projects/{project_id}/ no existe")
        return

    # project.json + brief mínimo
    pj = pdir / "project.json"
    brief = {}
    if not pj.exists():
        fail("falta project.json")
    else:
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
            brief = data.get("brief", {})
            if brief.get("tema") and brief.get("entidades_nucleo"):
                ok("project.json con brief (tema + entidades_nucleo)")
            else:
                fail("brief incompleto (falta tema o entidades_nucleo)")
        except json.JSONDecodeError:
            fail("project.json no es JSON válido")
            data = {}

    # contenido ingerido
    posts = pdir / "data/raw/posts.csv"
    if _csv_has_rows(posts):
        ok("data/raw/posts.csv con contenido")
    else:
        fail("data/raw/posts.csv ausente o vacío")

    # Default-FAIL: estado vs evidencia real
    estado = data.get("estado", {}) if pj.exists() else {}
    out_dir = pdir / "outputs"
    any_true = False
    for phase, done in estado.items():
        if not done:
            continue
        any_true = True
        evidence = PHASE_EVIDENCE.get(phase)
        if evidence and _csv_has_rows(out_dir / evidence):
            ok(f"fase '{phase}' = hecha y verificada ({evidence})")
        else:
            fail(f"Default-FAIL: '{phase}' marcada hecha pero falta evidencia ({evidence})")
    if not any_true:
        print("       (ninguna fase ejecutada todavía; proyecto recién creado)")


def main() -> int:
    check_base()
    args = sys.argv[1:]
    if args:
        check_project(args[0])
    else:
        projects = sorted(p.name for p in (ROOT / "projects").glob("*") if p.is_dir() and p.name != "_template")
        if projects:
            print(f"\nProyectos disponibles: {', '.join(projects)}")
            print("Ejecuta 'python bin/check.py <id>' para validar uno.")

    print()
    if _fail:
        print("RESULTADO: FALLO — corrige lo de arriba antes de continuar.")
        return 2
    print("RESULTADO: OK — sistema sano.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

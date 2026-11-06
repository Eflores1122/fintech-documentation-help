"""Clone a catalog year and leave a checklist for counsel."""

from __future__ import annotations

import shutil
from pathlib import Path

from fdh.catalog import CatalogError, locate_rules_dir

CHECKLIST = """# Checklist del catálogo {year}

Este archivo lo abre `fdh rules new-year`. No es asesoría legal.

Copiado desde {previous}. Revise cada punto antes de dar el año por cerrado:

- [ ] RMF {year} y sus modificaciones en el hub del SAT. Actualice la ficha de publicación y deje UNVERIFIED lo que no se haya leído.
- [ ] Ley de Ingresos de la Federación {year}, en especial retenciones de IFC si siguen.
- [ ] DOF: LRITF, LFPIORPI, LFPDPPP, disposiciones CNBV, Banxico y CONDUSEF publicados desde el cierre del año anterior.
- [ ] Criterios contables y reportes regulatorios (anexos) si la CNBV publicó resolución nueva.
- [ ] Cada regla nueva trae `source_url` https, `effective_date`, `last_verified` y `verified: false` (`unverified: true` más `unverified_detail`) si el artículo no se leyó.
- [ ] `fdh rules validate` y `fdh rules diff {previous} {year}`.
- [ ] No hay datos de una entidad real.

Quien no programa puede copiar un bloque `rules:` de un YAML vecino y cambiar los campos. El validador rechaza el archivo si falta la fuente o el disclaimer.
"""


def start_new_year(year: int, rules_dir: Path | None = None) -> Path:
    if year < 2025:
        raise CatalogError([f"Año no soportado: {year}"])
    root = locate_rules_dir(rules_dir)
    previous = root / str(year - 1)
    target = root / str(year)
    if not previous.is_dir():
        raise CatalogError([f"No existe el catálogo {year - 1} para clonarlo."])
    if target.exists():
        raise CatalogError([f"Ya existe {target}. No se sobreescribe."])
    shutil.copytree(previous, target)
    for path in target.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        text = text.replace(f"catalog_year: {year - 1}", f"catalog_year: {year}", 1)
        path.write_text(text, encoding="utf-8")
    checklist = target / "CHECKLIST.md"
    checklist.write_text(
        CHECKLIST.format(year=year, previous=year - 1),
        encoding="utf-8",
    )
    return target

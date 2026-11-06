"""Export the YAML catalog to JSON for the browser demo. No network."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from fdh.catalog import available_years, load_catalog
from fdh.parameters import load_parameters

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data"
SAMPLES = SITE / "samples"


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)
    versions = []
    for year in available_years():
        for rule in load_catalog(year):
            versions.append(
                {
                    "catalog_year": year,
                    "id": rule.id,
                    "domain": rule.domain,
                    "area": rule.area,
                    "title": rule.title,
                    "requirement": rule.requirement,
                    "severity": rule.severity,
                    "entity_types": rule.entity_types,
                    "documents": rule.documents,
                    "source_url": rule.source_url,
                    "source_name": rule.source_name,
                    "effective_from": rule.effective_from.isoformat(),
                    "effective_to": rule.effective_to.isoformat() if rule.effective_to else None,
                    "supersedes": rule.supersedes,
                    "superseded_by": rule.superseded_by,
                    "applies_if": rule.applies_if,
                    "min_strictness": rule.min_strictness,
                    "binding": rule.binding,
                    "unverified": rule.unverified,
                    "fix_suggestion": rule.fix_suggestion,
                    "owner_role": rule.owner_role,
                    "remediation_days": rule.remediation_days,
                    "matcher": rule.matcher.model_dump(),
                }
            )
    parameters = []
    for item in load_parameters():
        parameters.append(
            {
                "id": item.id,
                "title": item.title,
                "unit": item.unit,
                "verified": item.verified,
                "unverified_detail": item.unverified_detail,
                "source_url": item.source_url,
                "source_name": item.source_name,
                "used_by": item.used_by,
                "values": [
                    {
                        "effective_from": value.effective_from.isoformat(),
                        "effective_to": value.effective_to.isoformat()
                        if value.effective_to
                        else None,
                        "value": value.value,
                    }
                    for value in item.values
                ],
            }
        )
    (DATA / "catalog.json").write_text(
        json.dumps({"rules": versions, "parameters": parameters}, ensure_ascii=False),
        encoding="utf-8",
    )
    packs = {}
    for name, folder in (
        ("nube_pago", ROOT / "samples" / "nube_pago" / "docs"),
        ("ladrillo_comun", ROOT / "samples" / "ladrillo_comun" / "docs"),
    ):
        files = []
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in {".md", ".txt"}:
                continue
            files.append({"name": path.name, "text": path.read_text(encoding="utf-8")})
        packs[name] = files
    (DATA / "samples.json").write_text(json.dumps(packs, ensure_ascii=False), encoding="utf-8")
    scan = ROOT / "samples" / "nube_pago" / "docs" / "aviso_escaneado.png"
    if scan.is_file():
        shutil.copy(scan, SAMPLES / "aviso_escaneado.png")
    print(f"reglas exportadas: {len(versions)}")


if __name__ == "__main__":
    main()

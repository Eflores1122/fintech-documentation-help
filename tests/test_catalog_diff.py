import json
from pathlib import Path

import pytest
import yaml

from fdh.catalog import (
    CatalogError,
    available_years,
    load_catalog,
    locate_rules_dir,
    validate_catalogs,
)
from fdh.cli import main
from fdh.diff import diff_catalogs, render_diff_json, render_diff_markdown

SEED_2026 = {
    "privacy-aviso-art15-elementos",
    "privacy-no-citar-inai",
    "privacy-consentimiento-datos-financieros",
    "privacy-arco-plazos",
    "privacy-departamento-datos",
    "privacy-medidas-seguridad",
    "privacy-aviso-vulneraciones",
    "lritf-no-garantia-gobierno",
    "lritf-politicas-segregacion",
    "lritf-divulgacion-riesgos-comisiones",
    "lritf-seguridad-informacion",
    "lritf-conflictos-interes",
    "lritf-prevencion-fraude",
    "lritf-continuidad-controles",
    "lritf-conservacion-10-anos",
    "lritf-av-divulgacion-riesgos",
    "banxico-ifpe-continuidad-seguridad",
    "cnbv-normatividad-index",
    "pld-manual-art58",
    "pld-metodologia-riesgos",
    "pld-reportes-roi-ror-rop",
    "pld-kyc-identificacion",
    "pld-oficial-cumplimiento-certificado",
    "pld-auditoria-anual",
    "pld-lista-bloqueados",
    "pld-retencion-10-anos",
    "pld-dcg-art58-fuente",
    "lfpiorpi-2025-manual-rba-av",
    "condusef-reca-inscripcion-previa",
    "condusef-consentimiento-expreso",
    "condusef-caratula-leyendas",
    "condusef-une",
    "condusef-reus-publicidad",
    "condusef-terminos-plataforma",
    "condusef-comisiones-plataforma",
    "sat-rmf-calendario-anual",
    "sat-rmf2026-publicacion",
    "sat-cfdi40-emision",
    "sat-complemento-pagos-rep",
    "sat-carta-porte",
    "sat-plataformas-tecnologicas",
    "sat-lif2026-ifc-retencion-isr-iva",
    "sat-cff-32b-informacion",
    "sat-iva-servicios-digitales",
    "meta-disclaimer-no-legal-advice",
    "meta-what-changed-2026",
}


def _rule(rule_id: str = "demo-regla", **extra) -> dict:
    rule = {
        "id": rule_id,
        "domain": "sat",
        "title": "Regla de prueba",
        "requirement": "Requisito de prueba suficientemente descriptivo.",
        "check_hint": "Pista de prueba.",
        "fix_suggestion": "Corrija el documento de prueba con una cita real.",
        "entity_types": ["fintech_general"],
        "documents": ["politica_cfdi"],
        "source_url": "https://www.sat.gob.mx/ejemplo",
        "source_name": "Fuente de prueba",
        "effective_date": "2026-01-01",
        "last_verified": "2026-11-05",
        "severity": "low",
        "matcher": {
            "require_document": True,
            "checks": [{"type": "contains_any", "any": ["cfdi"], "label": "cfdi"}],
        },
    }
    rule.update(extra)
    return rule


def _write(root: Path, year: int, rules: list[dict], name: str = "demo.yaml") -> None:
    folder = root / str(year)
    folder.mkdir(parents=True, exist_ok=True)
    payload = {
        "catalog_year": year,
        "disclaimer": "No constituyen asesoría legal ni fiscal.",
        "rules": rules,
    }
    (folder / name).write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def test_seed_catalog_2026_and_2025():
    rules = load_catalog(2026)
    ids = {rule.id for rule in rules}
    assert ids >= SEED_2026
    assert len(rules) == 134
    areas = {rule.area for rule in rules}
    assert {
        "legal",
        "regulatorio",
        "financiero",
        "fiscal",
        "pld",
        "ciberseguridad",
        "privacidad",
        "condusef",
        "riesgos",
        "operacion",
        "laboral",
    } <= areas
    for rule in rules:
        assert rule.source_url.startswith("https://")
        assert rule.fix_suggestion
        assert rule.verified is (not rule.unverified)
        if rule.unverified:
            assert rule.unverified_detail
    unverified = {rule.id for rule in rules if rule.unverified}
    assert {
        "sat-cfdi40-emision",
        "sat-complemento-pagos-rep",
        "sat-cff-32b-informacion",
        "legal-oficio-autorizacion",
        "ciber-incidentes-ifpe",
    } <= unverified
    older = load_catalog(2025)
    assert len(older) == 130
    assert "sat-rmf2025-publicacion" in {rule.id for rule in older}
    assert "sat-lif2026-ifc-retencion-isr-iva" not in {rule.id for rule in older}
    assert "financiero-criterios-nif-2026" not in {rule.id for rule in older}
    notes = validate_catalogs()
    assert any(line.startswith("UNVERIFIED 2026/sat-cfdi40-emision") for line in notes)


def test_diff_explains_annual_update():
    payload = diff_catalogs(2025, 2026)
    assert payload["summary"] == {
        "added": 5,
        "removed": 1,
        "modified": 3,
        "revalidated": 0,
        "unchanged": 126,
        "rules_before": 130,
        "rules_after": 134,
    }
    added = {item["id"] for item in payload["added"]}
    assert added == {
        "sat-lif2026-ifc-retencion-isr-iva",
        "sat-rmf2026-publicacion",
        "meta-what-changed-2026",
        "financiero-criterios-nif-2026",
        "regulatorio-anexos-contables-2026",
    }
    lif = next(item for item in payload["added"] if item["id"].startswith("sat-lif"))
    assert "IFPE" in lif["explanation"] or "financiamiento colectivo" in lif["explanation"]
    assert payload["removed"][0]["id"] == "sat-rmf2025-publicacion"
    assert payload["removed"][0]["replaced_by"] == "sat-rmf2026-publicacion"
    modified = {item["id"] for item in payload["modified"]}
    assert modified == {
        "sat-rmf-calendario-anual",
        "sat-cfdi40-emision",
        "sat-complemento-pagos-rep",
    }
    markdown = render_diff_markdown(payload)
    assert "LIF" in markdown or "financiamiento colectivo" in markdown
    assert markdown.count("Sustituye a sat-rmf2025-publicacion") == 1
    assert "UNVERIFIED" in markdown
    decoded = json.loads(render_diff_json(payload))
    assert decoded["from_year"] == 2025
    same = render_diff_markdown(diff_catalogs(2026, 2026))
    assert "No hay cambios materiales" in same


def test_diff_revalidation_only(tmp_path: Path):
    first = _rule(last_verified="2025-01-01")
    second = _rule(last_verified="2026-11-05")
    _write(tmp_path, 2025, [first])
    _write(tmp_path, 2026, [second])
    payload = diff_catalogs(2025, 2026, tmp_path)
    assert payload["summary"]["revalidated"] == 1
    assert payload["summary"]["modified"] == 0
    text = render_diff_markdown(payload)
    assert "Solo cambió la fecha de verificación" in text


def test_catalog_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(CatalogError):
        load_catalog(2030)
    with pytest.raises(CatalogError):
        locate_rules_dir(tmp_path / "no-existe")
    monkeypatch.setenv("FDH_RULES_DIR", str(tmp_path / "tampoco"))
    found = locate_rules_dir()
    assert (found / "2026").is_dir()
    monkeypatch.delenv("FDH_RULES_DIR")

    empty = tmp_path / "vacio"
    (empty / "2026").mkdir(parents=True)
    with pytest.raises(CatalogError, match="no contiene"):
        load_catalog(2026, empty)

    broken = tmp_path / "roto"
    (broken / "2026").mkdir(parents=True)
    (broken / "2026" / "x.yaml").write_text(":\n  :\n", encoding="utf-8")
    with pytest.raises(CatalogError, match="YAML"):
        load_catalog(2026, broken)

    not_map = tmp_path / "lista"
    (not_map / "2026").mkdir(parents=True)
    (not_map / "2026" / "x.yaml").write_text("- 1\n", encoding="utf-8")
    with pytest.raises(CatalogError, match="mapa"):
        load_catalog(2026, not_map)

    mismatch = tmp_path / "anio"
    _write(mismatch, 2026, [_rule()])
    text = (mismatch / "2026" / "demo.yaml").read_text(encoding="utf-8")
    (mismatch / "2026" / "demo.yaml").write_text(text.replace("2026", "2024", 1), encoding="utf-8")
    with pytest.raises(CatalogError, match="catalog_year"):
        load_catalog(2026, mismatch)

    dup = tmp_path / "dup"
    _write(dup, 2026, [_rule()], name="a.yaml")
    _write(dup, 2026, [_rule()], name="b.yaml")
    with pytest.raises(CatalogError, match="duplicado"):
        load_catalog(2026, dup)

    bad_regex = tmp_path / "regex"
    _write(
        bad_regex,
        2026,
        [_rule(matcher={"require_document": True, "checks": [{"type": "regex", "pattern": "["}]})],
    )
    with pytest.raises(CatalogError):
        load_catalog(2026, bad_regex)

    ghost = tmp_path / "ghost"
    _write(ghost, 2026, [_rule(supersedes="no-existe")])
    problems = validate_catalogs(ghost)
    assert any("supersedes" in line for line in problems)

    assert 2026 in available_years()


def test_cli_rules(capsys: pytest.CaptureFixture[str]):
    assert main(["rules", "validate"]) == 0
    out = capsys.readouterr().out
    assert "UNVERIFIED" in out
    assert "Catálogo válido" in out

    assert main(["rules", "list", "--year", "2026", "--domain", "privacy"]) == 0
    listed = capsys.readouterr().out
    assert "privacy-no-citar-inai" in listed
    assert "sat-lif2026" not in listed
    assert "privacy:" in listed

    assert main(["rules", "diff", "2025", "2026"]) == 0
    diff_out = capsys.readouterr().out
    assert "sat-lif2026-ifc-retencion-isr-iva" in diff_out

    assert main(["what-changed", "--year", "2026", "--format", "json"]) == 0
    body = json.loads(capsys.readouterr().out)
    assert body["to_year"] == 2026
    assert body["from_year"] == 2025

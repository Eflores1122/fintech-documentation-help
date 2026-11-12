"""Official source and date checks. Missing citations are reported, not invented."""

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from pydantic import ValidationError

from fdh.calendar_data import OBLIGATIONS
from fdh.citations import citation_problem, render_citation_report, source_url_problem
from fdh.cli import main
from fdh.models import Rule
from fdh.parameters import Parameter, load_parameters


def _rule(**extra: object) -> dict:
    rule: dict = {
        "id": "demo-regla",
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


def _write_catalog(root: Path, rules: list[dict]) -> None:
    folder = root / "2026"
    folder.mkdir(parents=True)
    payload = {
        "catalog_year": 2026,
        "disclaimer": "No constituyen asesoría legal ni fiscal.",
        "rules": rules,
    }
    (folder / "demo.yaml").write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def test_source_url_problem_rejects_missing_and_unknown_hosts():
    assert source_url_problem("http://www.sat.gob.mx/a") is not None
    assert "example.com" in (source_url_problem("https://example.com/law") or "")
    assert source_url_problem("https://www.sat.gob.mx/a") is None
    assert source_url_problem("https://www.iso.org/standard/27001") is None
    assert citation_problem("https://www.sat.gob.mx/a", "  ", "2026/demo") is not None
    assert citation_problem("https://dof.gob.mx/nota", "DOF", "2026/demo") is None


def test_rule_model_rejects_invented_host_and_blank_name():
    with pytest.raises(ValidationError, match="example.com"):
        Rule.model_validate(_rule(source_url="https://example.com/law"))
    with pytest.raises(ValidationError, match="source_name"):
        Rule.model_validate(_rule(source_name="   "))
    with pytest.raises(ValidationError, match="source_name"):
        Parameter.model_validate(
            {
                "id": "demo",
                "title": "Demo",
                "unit": "UDI",
                "source_url": "https://www.sat.gob.mx/ejemplo",
                "source_name": "  ",
                "values": [],
            }
        )
    with pytest.raises(ValidationError, match="example.com"):
        Parameter.model_validate(
            {
                "id": "demo",
                "title": "Demo",
                "unit": "UDI",
                "source_url": "https://example.com/law",
                "source_name": "No oficial",
                "values": [],
            }
        )


def test_render_lists_missing_dates_and_keeps_unverified_rows():
    unverified = SimpleNamespace(
        id="sat-abierta",
        source_url="https://www.sat.gob.mx/rmf",
        source_name="RMF",
        effective_date=date(2026, 1, 1),
        last_verified=date(2026, 11, 5),
        unverified=True,
    )
    undated = SimpleNamespace(
        id="sin-fecha",
        source_url="https://www.sat.gob.mx/rmf",
        source_name="RMF",
        effective_date=None,
        last_verified=date(2026, 11, 5),
        unverified=False,
    )
    bad_param = SimpleNamespace(
        id="tasa",
        source_url="https://example.com/tasa",
        source_name="Blog",
        verified=False,
    )
    text, missing = render_citation_report({2026: [unverified, undated]}, [bad_param])
    assert missing == 2
    assert "2026/sat-abierta" in text
    assert "falta effective_date" in text
    assert "example.com" in text
    assert "not legal or tax advice" in text
    assert "no es asesoría legal ni fiscal" in text

    empty, count = render_citation_report({}, [])
    assert count == 0
    assert empty.count("(none)") == 3


def test_shipped_catalog_has_no_missing_source(capsys: pytest.CaptureFixture[str]):
    assert main(["rules", "citations"]) == 0
    out = capsys.readouterr().out
    missing, _, rest = out.partition("MISSING SOURCE")
    section, _, _ = rest.partition("UNVERIFIED")
    assert "(none)" in section
    assert "not legal or tax advice" in missing
    assert "no es asesoría legal ni fiscal" in out
    for item in OBLIGATIONS:
        assert citation_problem(item.source_url, item.summary, item.uid) is None
    for param in load_parameters():
        assert citation_problem(param.source_url, param.source_name, param.id) is None


def test_citations_command_flags_unknown_host(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    _write_catalog(tmp_path, [_rule(source_url="https://example.com/invented")])
    assert main(["rules", "citations", "--rules-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "MISSING SOURCE" in out
    assert "example.com" in out
    assert "No se inventó una URL." in out
    assert "not legal or tax advice" in out


def test_citations_command_flags_bad_parameter(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    _write_catalog(tmp_path, [_rule()])
    (tmp_path / "parameters.yaml").write_text(
        "disclaimer: No constituyen asesoría legal ni fiscal.\n"
        "parameters:\n"
        "  - id: demo\n"
        "    title: Demo\n"
        "    unit: UDI\n"
        "    source_url: https://example.com/tasa\n"
        "    source_name: Blog\n"
        "    values: []\n",
        encoding="utf-8",
    )
    assert main(["rules", "citations", "--rules-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "example.com" in out
    assert "No se inventó una URL." in out

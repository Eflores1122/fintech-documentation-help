"""Coverage for the v2 audit workflow, exports and local helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fdh.calendar_data import obligations_for, render_ics
from fdh.cli import main
from fdh.diagrams import DIAGRAMS, render_svg, write_diagrams
from fdh.engine.audit import run_audit
from fdh.llm.rag import answer_question, search_rules
from fdh.llm.reviewer import SUGGESTED_MODELS, build_client
from fdh.models import Profile
from fdh.report.exports import render_csv, write_pdf, write_xlsx
from fdh.rules_admin import start_new_year
from fdh.templates_lib import write_templates
from fdh.watch import run_watch


def test_strictness_standard_skips_methodology(samples: Path):
    report = run_audit(
        [samples],
        Profile(entity_type="IFPE", year=2026, strictness="standard"),
        generated_at=datetime(2026, 11, 6, tzinfo=UTC),
    )
    ids = {item.rule_id for item in report.findings}
    assert "metodo-fecha-aprobacion" not in ids
    assert any(item["id"] == "metodo-ambiguedad" for item in report.omitted_rules)
    assert report.strictness == "standard"


def test_evidence_checklist_and_compare(samples: Path, tmp_path: Path):
    first = run_audit(
        [samples],
        Profile(entity_type="IFPE", year=2026),
        generated_at=datetime(2026, 11, 6, tzinfo=UTC),
    )
    marks = {"lritf-conflictos-interes": "ausente", "privacy-no-citar-inai": "presente"}
    second = run_audit(
        [samples],
        Profile(entity_type="IFPE", year=2026),
        evidence=marks,
        previous=json.loads(first.model_dump_json()),
        generated_at=datetime(2026, 11, 6, tzinfo=UTC),
    )
    by = {item.rule_id: item for item in second.findings}
    assert by["lritf-conflictos-interes"].status == "fail"
    assert "evidence_checklist" in by["lritf-conflictos-interes"].origin
    assert by["privacy-no-citar-inai"].status == "fail"
    assert second.comparison
    assert second.remediation
    assert second.opinion["label"] == "adverso"
    assert second.heatmap["pld"]["fail"] >= 1
    assert second.inventory
    partial = run_audit(
        [samples],
        Profile(entity_type="IFPE", year=2026),
        evidence={"lritf-conflictos-interes": "parcial"},
    )
    partial_item = next(
        item for item in partial.findings if item.rule_id == "lritf-conflictos-interes"
    )
    assert partial_item.status == "unclear"


def test_exports_and_assets(samples: Path, tmp_path: Path):
    report = run_audit([samples], Profile(entity_type="IFPE", year=2026))
    csv_text = render_csv(report)
    assert "rule_id" in csv_text and "privacy-no-citar-inai" in csv_text
    xlsx = tmp_path / "h.xlsx"
    write_xlsx(report, xlsx)
    assert xlsx.read_bytes().startswith(b"PK")
    pdf = tmp_path / "r.pdf"
    write_pdf(report, pdf)
    assert pdf.read_bytes().startswith(b"%PDF")
    written = write_diagrams(tmp_path / "d")
    assert any(path.suffix == ".svg" for path in written)
    assert "mapa-areas" in DIAGRAMS
    assert "<svg" in render_svg("flujo-pld")
    templates = write_templates(tmp_path / "t", only="pld")
    assert templates and "BORRADOR" in templates[0].read_text(encoding="utf-8")
    ics = render_ics("IFPE", 2026)
    assert "BEGIN:VCALENDAR" in ics and "A-0111" not in ics
    assert "R01" in ics
    assert obligations_for("SOFOM_ENR")
    assert obligations_for("IFC")


def test_new_year_and_watch(tmp_path: Path):
    import shutil

    from fdh.catalog import CatalogError, locate_rules_dir

    root = tmp_path / "rules"
    shutil.copytree(locate_rules_dir() / "2026", root / "2026")
    target = start_new_year(2027, root)
    assert (target / "CHECKLIST.md").is_file()
    assert "catalog_year: 2027" in (target / "meta" / "meta.yaml").read_text(encoding="utf-8")
    with pytest.raises(CatalogError):
        start_new_year(2027, root)

    def fetch(url: str) -> bytes:
        return f"cuerpo {url}".encode()

    code, text = run_watch(root, fetch=fetch)
    assert code == 0
    assert "Candado inicial" in text
    code, text = run_watch(root, fetch=lambda url: b"otro")
    assert code == 3
    assert "cambió" in text

    def boom(_url: str) -> bytes:
        raise RuntimeError("caido")

    code, text = run_watch(root, fetch=boom)
    assert code == 0
    assert "no respondieron" in text


def test_rag_and_local_llm(monkeypatch: pytest.MonkeyPatch):
    from fdh.catalog import load_catalog

    rules = load_catalog(2026)
    hits = search_rules("aviso de privacidad INAI", rules, limit=3)
    assert hits
    text = answer_question("capital mínimo UDI", rules)
    assert "Reglas más cercanas" in text
    assert "No es asesoría" in text
    empty = answer_question("xyzqwertyuiop", rules)
    assert "Ninguna regla" in empty

    monkeypatch.setenv("FDH_LLM_PROVIDER", "ollama")
    monkeypatch.delenv("FDH_LLM_API_KEY", raising=False)
    monkeypatch.delenv("FDH_LLM_ALLOW_REMOTE", raising=False)
    client, note = build_client()
    assert client is not None
    assert "127.0.0.1" in note
    assert "qwen2.5:7b" in SUGGESTED_MODELS

    monkeypatch.setenv("FDH_LLM_BASE_URL", "https://llm.example/v1")
    monkeypatch.delenv("FDH_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("FDH_LLM_API_KEY", "sk")
    monkeypatch.delenv("FDH_LLM_ALLOW_REMOTE", raising=False)
    blocked, reason = build_client()
    assert blocked is None
    assert "FDH_LLM_ALLOW_REMOTE" in reason

    monkeypatch.setenv("FDH_LLM_EMBEDDINGS", "1")
    monkeypatch.setenv("FDH_LLM_EMBED_URL", "https://embeddings.example/api")
    remote = answer_question("capital mínimo", rules)
    assert "no sale de la máquina" in remote


def test_cli_v2(samples: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    diagrams = tmp_path / "diagramas"
    assert main(["diagrams", "--out", str(diagrams)]) == 0
    assert (diagrams / "diagramas.md").is_file()
    templates = tmp_path / "plantillas"
    assert main(["templates", "--out", str(templates), "--only", "privacidad"]) == 0
    assert list(templates.glob("*.md"))
    ics = tmp_path / "cal.ics"
    assert main(["calendar", "--entity", "ifc", "--year", "2026", "--out", str(ics)]) == 0
    assert "BEGIN:VCALENDAR" in ics.read_text(encoding="utf-8")
    assert main(["ask", "RECA"]) == 0
    assert "RECA" in capsys.readouterr().out or "reca" in capsys.readouterr().out.casefold()
    assert main(["llm", "doctor"]) == 0
    assert "Ollama" in capsys.readouterr().out or "ollama" in capsys.readouterr().out.casefold()
    out = tmp_path / "audit"
    code = main(
        [
            "audit",
            str(samples),
            "--entity",
            "IFPE",
            "--strictness",
            "high",
            "--format",
            "md,csv,pdf",
            "--out",
            str(out),
            "--fail-on",
            "info",
        ]
    )
    assert code == 1
    assert (out / "hallazgos.csv").is_file()
    assert (out / "report.pdf").is_file()

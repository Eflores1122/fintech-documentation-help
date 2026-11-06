import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fdh.engine.audit import run_audit
from fdh.engine.matchers import _run_check
from fdh.engine.scoring import score_findings
from fdh.ingest.classify import classify_heuristic, classify_with_llm, parse_llm_types
from fdh.ingest.loaders import html_to_text, load_documents
from fdh.ingest.pdfutil import write_simple_pdf
from fdh.models import Finding, Profile
from fdh.report.render import render_html, render_json, render_markdown

PASS = {
    "privacy-departamento-datos",
    "pld-kyc-identificacion",
    "lritf-conflictos-interes",
}
NA = {
    "lritf-av-divulgacion-riesgos",
    "sat-complemento-pagos-rep",
    "sat-carta-porte",
    "sat-plataformas-tecnologicas",
    "sat-iva-servicios-digitales",
}
OMITTED = {
    "meta-disclaimer-no-legal-advice",
    "meta-what-changed-2026",
    "sat-lif2026-ifc-retencion-isr-iva",
}


def _audit(samples: Path, **kwargs):
    profile = Profile(entity_type="IFPE", year=2026, **kwargs)
    return run_audit([samples], profile, generated_at=datetime(2026, 11, 5, 18, 0, tzinfo=UTC))


def test_sample_partition(samples: Path):
    report = _audit(samples)
    by = {item.rule_id: item for item in report.findings}
    assert len(by) == len(report.findings) == 43
    assert {item.rule_id for item in report.findings if item.status == "pass"} == PASS
    assert {item.rule_id for item in report.findings if item.status == "not_applicable"} == NA
    assert {item["id"] for item in report.omitted_rules} == OMITTED
    assert report.summary["fail"] == 35
    assert report.summary["fail_critical"] == 13
    assert report.scores.overall == 7.6
    assert report.scores.by_domain["privacy"] == 9.5
    assert report.scores.by_domain["cnbv"] is None
    assert {item.rule_id for item in report.findings if item.unverified} == {
        "sat-cfdi40-emision",
        "sat-complemento-pagos-rep",
        "sat-cff-32b-informacion",
    }

    aviso = by["privacy-aviso-art15-elementos"]
    assert "III." in aviso.message and "VI." in aviso.message
    inai = by["privacy-no-citar-inai"]
    assert inai.evidence and "INAI" in inai.evidence
    assert "Secretaría Anticorrupción" in inai.fix_suggestion
    reca = by["condusef-reca-inscripcion-previa"]
    assert "pendiente" in (reca.evidence or "").lower() or "pendiente" in reca.message.lower()
    assert "continuar navegando" in (by["condusef-consentimiento-expreso"].evidence or "")
    assert "vacante" in (by["pld-oficial-cumplimiento-certificado"].evidence or "")
    assert by["sat-rmf2026-publicacion"].status == "fail"
    for item in report.findings:
        assert item.source_url.startswith("https://")
        assert len(item.fix_suggestion) > 15
        if item.status == "fail" and item.document:
            assert item.evidence

    markdown = render_markdown(report)
    html = render_html(report)
    payload = json.loads(render_json(report))
    assert "no es asesoría legal ni fiscal" in markdown
    assert "not legal or tax advice" in markdown
    assert "UNVERIFIED" in markdown and "UNVERIFIED" in html
    assert payload["disclaimer"].startswith("AVISO:")
    assert payload["llm_used"] is False


def test_golden_report(samples: Path, repo: Path):
    fresh = _audit(samples)
    golden = json.loads(
        (repo / "examples" / "nube_pago" / "report.json").read_text(encoding="utf-8")
    )

    def signature(findings: list[dict]) -> list[tuple]:
        return [
            (
                item["rule_id"],
                item["status"],
                item["severity"],
                item["unverified"],
                item["source_url"],
            )
            for item in findings
        ]

    assert signature(json.loads(render_json(fresh))["findings"]) == signature(golden["findings"])
    assert fresh.scores.model_dump() == golden["scores"]
    assert "Nube Pago" in (repo / "examples" / "nube_pago" / "report.md").read_text(
        encoding="utf-8"
    )


def test_entity_and_profile_flags(samples: Path, tmp_path: Path):
    ifc = run_audit([tmp_path], Profile(entity_type="IFC", year=2026))
    lif = next(item for item in ifc.findings if item.rule_id == "sat-lif2026-ifc-retencion-isr-iva")
    assert lif.status == "fail"
    ifpe_ids = {item.rule_id for item in _audit(samples).findings}
    assert "sat-lif2026-ifc-retencion-isr-iva" not in ifpe_ids

    with_assets = _audit(samples, operates_virtual_assets=True)
    asset = next(
        item for item in with_assets.findings if item.rule_id == "lritf-av-divulgacion-riesgos"
    )
    assert asset.status == "fail"
    payments = _audit(samples, has_partial_or_deferred_payments=True)
    rep = next(item for item in payments.findings if item.rule_id == "sat-complemento-pagos-rep")
    assert rep.status == "fail"
    assert rep.unverified is True


def test_ingest_formats(tmp_path: Path, samples: Path, monkeypatch: pytest.MonkeyPatch):
    (tmp_path / "nota.md").write_text(
        "# Aviso de privacidad\nResponsable y domicilio.\n", encoding="utf-8"
    )
    (tmp_path / "vacio.txt").write_text("   \n", encoding="utf-8")
    (tmp_path / ".oculto.txt").write_text("no debe leerse", encoding="utf-8")
    (tmp_path / "tabla.bin").write_bytes(b"abc")
    (tmp_path / "latin.txt").write_bytes(b"\xffaviso de privacidad del responsable")
    (tmp_path / "pagina.html").write_text(
        "<html><script>secreto-interno</script><p>Aviso de privacidad del responsable.</p></html>",
        encoding="utf-8",
    )
    write_simple_pdf(tmp_path / "publicidad_campana.pdf", "MATERIAL PUBLICITARIO\nCampana ficticia")
    (tmp_path / "roto.pdf").write_bytes(b"%PDF-1.4\nesto no es un pdf")

    import docx

    document = docx.Document()
    document.add_paragraph("Nombramiento del oficial de cumplimiento")
    table = document.add_table(rows=1, cols=1)
    table.rows[0].cells[0].text = "Puesto vacante"
    document.save(tmp_path / "nombramiento_oficial.docx")

    (tmp_path / "grande.txt").write_text("demasiado texto para el limite", encoding="utf-8")
    monkeypatch.setattr("fdh.ingest.loaders.MAX_BYTES", 8)
    huge = load_documents([tmp_path / "grande.txt"])
    assert any("mayor" in warning for warning in huge[0].warnings)
    monkeypatch.setattr("fdh.ingest.loaders.MAX_BYTES", 20 * 1024 * 1024)

    docs = {item.filename: item for item in load_documents([tmp_path])}
    assert ".oculto.txt" not in docs
    assert "aviso_privacidad" in docs["nota.md"].types
    assert docs["vacio.txt"].warnings
    assert docs["tabla.bin"].warnings
    assert "aviso" in docs["latin.txt"].text
    assert "secreto-interno" not in docs["pagina.html"].text
    assert "Campana" in docs["publicidad_campana.pdf"].text
    assert docs["roto.pdf"].warnings
    assert "Puesto vacante" in docs["nombramiento_oficial.docx"].text

    stripped = html_to_text("<style>body{}</style><p>visible</p>")
    assert "visible" in stripped and "body" not in stripped

    sample_docs = {item.filename: item.types for item in load_documents([samples])}
    assert sample_docs["aviso_de_privacidad.md"] == ["aviso_privacidad"]
    assert "politica_kyc" in sample_docs["procedimiento_kyc.txt"]
    assert classify_heuristic("privacidad.txt", "aviso de privacidad") == ["aviso_privacidad"]


def test_llm_classifier_rejects_unknown_types():
    assert parse_llm_types("no json", {"aviso_privacidad"}) == []
    assert parse_llm_types('{"types": "aviso_privacidad"}', {"aviso_privacidad"}) == []
    assert parse_llm_types(
        'nota {"types": ["contrato_adhesion", "inventada", "contrato_adhesion"]}',
        {"contrato_adhesion"},
    ) == ["contrato_adhesion"]

    def boom(_messages):
        raise RuntimeError("caido")

    assert classify_with_llm("a.txt", "texto", boom, {"aviso_privacidad"}) == []

    def ok(messages):
        assert "contrato_adhesion" in messages[-1]["content"]
        return '{"types": ["contrato_adhesion", "no-existe"]}'

    chosen = classify_with_llm(
        "notas.txt", "texto largo", ok, {"contrato_adhesion", "aviso_privacidad"}
    )
    assert chosen == ["contrato_adhesion"]


def test_scoring_weights():
    def make(status: str, severity: str, domain: str = "sat", rule_id: str = "r") -> Finding:
        return Finding(
            rule_id=rule_id,
            status=status,  # type: ignore[arg-type]
            severity=severity,  # type: ignore[arg-type]
            domain=domain,
            title="t",
            requirement="r",
            message="m",
            fix_suggestion="Corrija el documento de prueba.",
            source_name="s",
            source_url="https://www.sat.gob.mx/",
            effective_date="2026-01-01",
            last_verified="2026-11-05",
        )

    card = score_findings(
        [
            make("pass", "critical", rule_id="a"),
            make("fail", "high", rule_id="b"),
            make("fail", "info", "cnbv", rule_id="c"),
            make("not_applicable", "critical", rule_id="d"),
            make("unclear", "medium", rule_id="e"),
        ]
    )
    # critical pass 5, high fail 0, medium unclear 1, info weight 0. Total weight 10, got 6.
    assert card.overall == 60.0
    assert card.by_domain["cnbv"] is None


def test_unknown_matcher_type():
    class Dummy:
        type = "desconocido"
        label = None
        groups: list = []
        any: list = []
        pattern = None
        expect = "match"

    outcome = _run_check(Dummy(), [])  # type: ignore[arg-type]
    assert outcome.ok is False

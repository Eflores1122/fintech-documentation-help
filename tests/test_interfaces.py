import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

import fdh.__main__ as entrypoint
from fdh.cli import main
from fdh.engine.audit import run_audit
from fdh.ingest.loaders import load_documents
from fdh.llm.reviewer import OpenAICompatibleClient, build_client, review_documents
from fdh.models import Profile
from fdh.web import app


def test_llm_review_grounds_and_rejects(samples: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("FDH_LLM_API_KEY", raising=False)
    client, note = build_client()
    assert client is None
    assert "FDH_LLM_API_KEY" in note

    monkeypatch.setenv("FDH_LLM_API_KEY", "sk-test")
    monkeypatch.setenv("FDH_LLM_ENABLED", "0")
    client, note = build_client()
    assert client is None
    assert "FDH_LLM_ENABLED" in note

    class Fake:
        def complete(self, messages):
            blob = messages[-1]["content"]
            if "Etiquetas permitidas" in blob:
                return '{"types": ["aviso_privacidad", "tipo-falso"]}'
            return json.dumps(
                {
                    "findings": [
                        {
                            "rule_id": "no-existe",
                            "status": "fail",
                            "evidence_quote": "texto inventado que no está en el expediente",
                            "fix": "inventar una ley",
                        },
                        {
                            "rule_id": "privacy-departamento-datos",
                            "status": "fail",
                            "evidence_quote": (
                                "Departamento de datos personales: privacidad@nubepago.example"
                            ),
                            "fix": "el modelo no puede reescribir la obligación",
                        },
                        {
                            "rule_id": "privacy-no-citar-inai",
                            "status": "pass",
                            "evidence_quote": "La autoridad competente para la protección de datos es el INAI",
                            "fix": "no debe bajar una falla determinística",
                        },
                        {
                            "rule_id": "sat-carta-porte",
                            "status": "fail",
                            "evidence_quote": "Nos regimos únicamente por la Resolución Miscelánea Fiscal 2025",
                            "fix": "no aplica al perfil",
                        },
                        {
                            "rule_id": "privacy-arco-plazos",
                            "status": "fail",
                            "evidence_quote": "cita que el modelo se inventó y no está en el archivo",
                            "fix": "x",
                        },
                    ]
                }
            )

    monkeypatch.setattr("fdh.llm.reviewer.build_client", lambda: (Fake(), "revisor de prueba"))
    report = run_audit([samples], Profile(entity_type="IFPE", year=2026), use_llm=True)
    assert report.llm_used is True
    by = {item.rule_id: item for item in report.findings}
    assert by["privacy-departamento-datos"].status == "fail"
    assert "llm" in by["privacy-departamento-datos"].origin
    assert by["privacy-no-citar-inai"].status == "fail"
    reasons = {item["rule_id"]: item["reason"] for item in report.rejected_llm_findings}
    assert "no-existe" in reasons
    assert "catálogo" in reasons["no-existe"]
    assert "privacy-no-citar-inai" in reasons
    assert "sat-carta-porte" in reasons
    assert "privacy-arco-plazos" in reasons
    assert all(doc.types.count("tipo-falso") == 0 for doc in report.documents)

    class Boom:
        def complete(self, _messages):
            raise RuntimeError("timeout")

    rules_docs = load_documents([samples])
    from fdh.catalog import load_catalog

    unchanged, rejected = review_documents(Boom(), load_catalog(2026), rules_docs, report.findings)
    assert unchanged
    assert rejected == []

    empty_docs = load_documents([samples])
    for doc in empty_docs:
        doc.text = ""
    same, rejected = review_documents(Fake(), load_catalog(2026), empty_docs, report.findings)
    assert rejected == []
    assert same[0].status == report.findings[0].status


def test_openai_compatible_client(monkeypatch: pytest.MonkeyPatch):
    captured: dict = {}

    def fake_post(url, headers, json, timeout):  # noqa: A002
        captured["url"] = url
        captured["model"] = json["model"]
        captured["auth"] = headers["Authorization"]

        class Response:
            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {"content": '{"findings": []}'}}]}

        return Response()

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("FDH_LLM_API_KEY", "sk-test")
    monkeypatch.setenv("FDH_LLM_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("FDH_LLM_MODEL", "demo-model")
    monkeypatch.delenv("FDH_LLM_ENABLED", raising=False)
    client, note = build_client()
    assert client is not None
    assert "demo-model" in note
    assert client.complete([{"role": "user", "content": "hola"}]) == '{"findings": []}'
    assert captured["url"] == "https://llm.example/v1/chat/completions"
    assert captured["model"] == "demo-model"
    assert captured["auth"] == "Bearer sk-test"

    def failing_post(url, headers, json, timeout):  # noqa: A002
        class Response:
            def raise_for_status(self):
                raise RuntimeError("500")

        return Response()

    monkeypatch.setattr(httpx, "post", failing_post)
    with pytest.raises(RuntimeError):
        OpenAICompatibleClient("https://llm.example/v1", "sk-test", "demo").complete([])


def test_module_entrypoint():
    assert entrypoint.main is main


def test_cli_audit(samples: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch):
    monkeypatch.delenv("FDH_LLM_API_KEY", raising=False)
    out = tmp_path / "out"
    code = main(
        [
            "audit",
            str(samples),
            "--year",
            "2026",
            "--entity",
            "ifpe",
            "--out",
            str(out),
            "--format",
            "md,html,json",
            "--llm",
            "--fail-on",
            "critical",
        ]
    )
    assert code == 1
    text = capsys.readouterr().out
    assert "no es asesoría legal ni fiscal" in text
    assert "FDH_LLM_API_KEY" in text
    assert (out / "report.md").exists()
    assert (out / "report.html").exists()
    assert (out / "report.json").exists()
    assert main(["audit", str(tmp_path / "no-existe")]) == 2
    assert main(["audit", str(samples), "--entity", "banco-inexistente"]) == 2

    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_cli_serve(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    called: dict = {}

    def fake_run(target, host, port, reload):  # noqa: A002
        called["target"] = target
        called["host"] = host
        called["port"] = port

    monkeypatch.setattr("uvicorn.run", fake_run)
    assert main(["serve", "--host", "127.0.0.1", "--port", "9"]) == 0
    assert called == {"target": "fdh.web:app", "host": "127.0.0.1", "port": 9}
    assert "no es asesoría" in capsys.readouterr().out


def test_web_upload(samples: Path):
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    index = client.get("/")
    assert index.status_code == 200
    assert "no es asesoría legal ni fiscal" in index.text
    assert "confidenciales" in index.text

    aviso = (samples / "aviso_de_privacidad.md").read_bytes()
    response = client.post(
        "/audit",
        data={"year": "2026", "entity": "IFPE"},
        files=[("files", ("aviso_de_privacidad.md", aviso, "text/markdown"))],
    )
    assert response.status_code == 200
    assert "UNVERIFIED" in response.text or "INAI" in response.text
    assert "no es asesoría legal ni fiscal" in response.text

    payload = client.post(
        "/audit.json",
        data={"year": "2026", "entity": "IFPE", "use_llm": "true"},
        files=[("files", ("aviso_de_privacidad.md", aviso, "text/markdown"))],
    )
    assert payload.status_code == 200
    body = payload.json()
    assert body["disclaimer"].startswith("AVISO:")
    assert body["llm_used"] is False
    assert any(item["rule_id"] == "privacy-no-citar-inai" for item in body["findings"])

    bad = client.post(
        "/audit",
        data={"year": "2026", "entity": "no-es-una-entidad"},
        files=[("files", ("aviso_de_privacidad.md", aviso, "text/markdown"))],
    )
    assert bad.status_code == 400
    assert "no es asesoría" in bad.text

    missing_year = client.post(
        "/audit.json",
        data={"year": "1999", "entity": "IFPE"},
        files=[("files", ("aviso_de_privacidad.md", b"aviso de privacidad", "text/markdown"))],
    )
    assert missing_year.status_code == 400
    assert "disclaimer" in missing_year.json()

    unnamed = client.post(
        "/audit",
        data={"year": "2026", "entity": "IFPE"},
        files=[("files", ("..", b"aviso", "text/plain"))],
    )
    assert unnamed.status_code == 400


def test_web_rejects_oversized():
    client = TestClient(app)
    response = client.post(
        "/audit.json",
        data={"year": "2026", "entity": "IFPE"},
        files=[("files", ("aviso.txt", b"x" * (20 * 1024 * 1024 + 1), "text/plain"))],
    )
    assert response.status_code == 400
    assert "20 MB" in response.json()["error"]


def test_readme_mentions_domains(repo: Path):
    readme = (repo / "README.md").read_text(encoding="utf-8")
    for domain in ("privacy", "lritf", "banxico", "cnbv", "pld", "condusef", "sat"):
        assert domain in readme
    assert "no es asesoría legal ni fiscal" in readme
    assert "fdh audit" in readme
    assert "fdh rules diff" in readme

"""Provider-agnostic reviewer.

The client speaks the OpenAI chat-completions protocol (any compatible base URL).
Findings are kept only when ``rule_id`` exists in the loaded catalog and the
evidence quote is a verbatim span of an ingested document. The model cannot
invent a regulation: title, requirement, severity and source URL always come
from the catalog.
"""

from __future__ import annotations

import json
import os
import re
from typing import Protocol
from urllib.parse import urlparse

import httpx

from fdh.models import Document, Finding, Rule
from fdh.textutil import quote_grounded

LOCAL_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "host.docker.internal",
    "ollama",
}
LOCAL_PROVIDERS = {"ollama", "llamacpp", "llama.cpp", "lmstudio", "vllm", "local"}
SUGGESTED_MODELS = (
    "qwen2.5:7b",
    "qwen2.5:14b",
    "llama3.1:8b",
    "llama3.2:3b",
    "mistral:7b",
)

LLM_SEVERITIES = {"critical", "high", "medium"}
_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


class ChatClient(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


class OpenAICompatibleClient:
    """POST {base_url}/chat/completions with a bearer token."""

    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def complete(self, messages: list[dict[str, str]]) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "temperature": 0, "messages": messages},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload["choices"][0]["message"]["content"])


def _local_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in LOCAL_HOSTS


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def build_client() -> tuple[ChatClient | None, str]:
    """Return a local or explicitly allowed client. Documents stay on the machine by default."""
    if os.environ.get("FDH_LLM_ENABLED", "1").strip().lower() in {"0", "false", "no", "off"}:
        return None, "LLM desactivado con FDH_LLM_ENABLED=0. Solo revisión determinística."
    provider = os.environ.get("FDH_LLM_PROVIDER", "").strip().lower()
    api_key = os.environ.get("FDH_LLM_API_KEY", "").strip()
    if provider in LOCAL_PROVIDERS:
        default = (
            "http://127.0.0.1:11434/v1" if provider == "ollama" else "http://127.0.0.1:8080/v1"
        )
        base = os.environ.get("FDH_LLM_BASE_URL", default).strip()
        model = os.environ.get("FDH_LLM_MODEL", SUGGESTED_MODELS[0]).strip()
        key = api_key or "local"
    else:
        if not api_key:
            return (
                None,
                "No hay FDH_LLM_API_KEY ni FDH_LLM_PROVIDER local. La auditoría quedó solo con "
                "reglas determinísticas y ningún documento salió de este equipo.",
            )
        base = os.environ.get("FDH_LLM_BASE_URL", "https://api.openai.com/v1").strip()
        model = os.environ.get("FDH_LLM_MODEL", "gpt-4o-mini").strip()
        key = api_key
    if not _local_host(base) and not _truthy("FDH_LLM_ALLOW_REMOTE"):
        return (
            None,
            "El endpoint no es local. Defina FDH_LLM_ALLOW_REMOTE=1 para enviar texto fuera de "
            "esta máquina. Por defecto los documentos no salen.",
        )
    return OpenAICompatibleClient(base, key, model), f"Revisor LLM activo ({model} @ {base})."


_SYSTEM = (
    "Eres un revisor de documentación de una fintech mexicana. "
    "SOLO puedes citar rule_id que aparezcan en el catálogo proporcionado. "
    "No inventes leyes, artículos, tasas, fechas ni obligaciones que no estén en ese catálogo. "
    "evidence_quote debe ser un fragmento COPIADO del documento, no una paráfrasis. "
    "Si el texto no alcanza para decidir, usa status unclear. "
    'Responde únicamente JSON: {"findings": [{"rule_id": "...", "status": "pass|fail|unclear", '
    '"evidence_quote": "...", "fix": "..."}]}.'
)


def review_documents(
    client: ChatClient,
    rules: list[Rule],
    documents: list[Document],
    findings: list[Finding],
    adversarial: bool = False,
) -> tuple[list[Finding], list[dict[str, str]]]:
    catalog = {rule.id: rule for rule in rules}
    by_id = {item.rule_id: item for item in findings}
    considered = [rule for rule in rules if rule.severity in LLM_SEVERITIES and rule.id in by_id]
    if not considered or not any(doc.text for doc in documents):
        return findings, []
    raw = _safe_complete(client, considered, documents, adversarial=adversarial)
    parsed, rejected = _parse(raw, catalog, documents)
    merged = list(findings)
    index = {item.rule_id: position for position, item in enumerate(merged)}
    for item in parsed:
        current = merged[index[item["rule_id"]]]
        if current.status == "not_applicable":
            rejected.append(
                {
                    "rule_id": item["rule_id"],
                    "reason": "La regla no aplica al perfil; el modelo no puede reactivarla.",
                }
            )
            continue
        # A deterministic failure is never downgraded by the model.
        if current.status == "fail" and item["status"] == "pass":
            rejected.append(
                {
                    "rule_id": item["rule_id"],
                    "reason": "El modelo marcó pass pero el chequeo determinístico ya falló.",
                }
            )
            continue
        if current.status == "pass" and item["status"] == "fail":
            current.status = "fail"
            current.message += (
                " El revisor LLM, citando esta regla del catálogo, marcó incumplimiento."
            )
            current.cause = (
                "Hallazgo agregado por el modelo sobre una regla del catálogo. "
                "No sustituye el chequeo determinístico ni baja ninguna severidad."
            )
        if item["status"] == "unclear" and current.status == "pass":
            current.status = "unclear"
            current.message += " El revisor LLM no pudo confirmar el cumplimiento."
        if "llm" not in current.origin:
            current.origin.append("llm")
        current.source = "mixed"
        if item.get("confidence"):
            current.confidence = float(item["confidence"])
        if item.get("evidence_quote") and not current.evidence:
            current.evidence = item["evidence_quote"]
        # The catalog severity stays. A model cannot lower it.
    return merged, rejected


def _safe_complete(
    client: ChatClient,
    rules: list[Rule],
    documents: list[Document],
    adversarial: bool = False,
) -> str:
    system = _SYSTEM
    if adversarial:
        system += (
            " Modo auditor adversarial: busca fallas adicionales. "
            "No marques pass si hay duda. No inventes rule_id. "
            "Incluye confidence entre 0 y 1. No pidas bajar la severidad."
        )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": _user_prompt(rules, documents)},
    ]
    try:
        return client.complete(messages)
    except Exception as exc:
        return json.dumps({"findings": [], "error": f"No se pudo consultar al modelo: {exc}"})


def _user_prompt(rules: list[Rule], documents: list[Document]) -> str:
    catalog = [
        {
            "rule_id": rule.id,
            "severity": rule.severity,
            "requirement": rule.requirement,
            "check_hint": rule.check_hint,
            "documents": rule.documents,
        }
        for rule in rules
    ]
    docs = [
        {"filename": doc.path, "types": doc.types, "text": doc.text[:12_000]}
        for doc in documents
        if doc.text
    ][:8]
    return (
        "Catálogo cerrado (no cites nada fuera de estos rule_id):\n"
        + json.dumps(catalog, ensure_ascii=False)
        + "\n\nDocumentos:\n"
        + json.dumps(docs, ensure_ascii=False)
    )


def _parse(
    raw: str, catalog: dict[str, Rule], documents: list[Document]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rejected: list[dict[str, str]] = []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        match = _JSON_OBJECT.search(raw)
        if match is None:
            return [], [{"rule_id": "", "reason": "La respuesta del modelo no es JSON."}]
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return [], [{"rule_id": "", "reason": "La respuesta del modelo no es JSON."}]
    rows = payload.get("findings", []) if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return [], [{"rule_id": "", "reason": "El JSON no trae una lista findings."}]
    texts = [doc.text for doc in documents]
    accepted: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            rejected.append({"rule_id": "", "reason": "Hallazgo mal formado."})
            continue
        rule_id = str(row.get("rule_id", "")).strip()
        status = str(row.get("status", "")).strip()
        quote = str(row.get("evidence_quote", "") or "").strip()
        if rule_id not in catalog:
            rejected.append(
                {
                    "rule_id": rule_id or "(vacío)",
                    "reason": "rule_id fuera del catálogo; no se inventa regulación.",
                }
            )
            continue
        if status not in {"pass", "fail", "unclear"}:
            rejected.append({"rule_id": rule_id, "reason": f"status no permitido: {status}"})
            continue
        if status in {"fail", "unclear"} and not quote_grounded(quote, texts):
            rejected.append(
                {
                    "rule_id": rule_id,
                    "reason": "evidence_quote no es un fragmento literal del documento.",
                }
            )
            continue
        confidence = row.get("confidence", 0.5)
        try:
            confidence_value = max(0.0, min(1.0, float(confidence)))
        except (TypeError, ValueError):
            confidence_value = 0.5
        accepted.append(
            {
                "rule_id": rule_id,
                "status": status,
                "evidence_quote": quote,
                "confidence": str(confidence_value),
            }
        )
    return accepted, rejected

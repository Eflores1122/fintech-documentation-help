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

import httpx

from fdh.models import Document, Finding, Rule
from fdh.textutil import quote_grounded

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


def build_client() -> tuple[ChatClient | None, str]:
    """Return a client when FDH_LLM_API_KEY is set, otherwise a reason it is off."""
    api_key = os.environ.get("FDH_LLM_API_KEY", "").strip()
    if os.environ.get("FDH_LLM_ENABLED", "1").strip() in {"0", "false", "False", "no"}:
        return None, "LLM desactivado con FDH_LLM_ENABLED=0. Solo revisión determinística."
    if not api_key:
        return (
            None,
            "No hay FDH_LLM_API_KEY. La auditoría se completó solo con reglas determinísticas "
            "y ningún documento salió de este equipo.",
        )
    base = os.environ.get("FDH_LLM_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.environ.get("FDH_LLM_MODEL", "gpt-4o-mini").strip()
    return OpenAICompatibleClient(base, api_key, model), f"Revisor LLM activo ({model})."


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
) -> tuple[list[Finding], list[dict[str, str]]]:
    catalog = {rule.id: rule for rule in rules}
    by_id = {item.rule_id: item for item in findings}
    considered = [rule for rule in rules if rule.severity in LLM_SEVERITIES and rule.id in by_id]
    if not considered or not any(doc.text for doc in documents):
        return findings, []
    raw = _safe_complete(client, considered, documents)
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
        if "llm" not in current.origin:
            current.origin.append("llm")
        if item.get("evidence_quote") and not current.evidence:
            current.evidence = item["evidence_quote"]
        if item["status"] == "unclear" and current.status == "pass":
            current.status = "unclear"
            current.message += " El revisor LLM no pudo confirmar el cumplimiento."
    return merged, rejected


def _safe_complete(client: ChatClient, rules: list[Rule], documents: list[Document]) -> str:
    messages = [
        {"role": "system", "content": _SYSTEM},
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
        accepted.append({"rule_id": rule_id, "status": status, "evidence_quote": quote})
    return accepted, rejected

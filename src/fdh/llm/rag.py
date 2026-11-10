"""Local answers over the rule catalog.

Lexical search always works. Embeddings are attempted only against a local Ollama
endpoint and never against a remote host.
"""

from __future__ import annotations

import math
import os
import re
from collections import Counter

import httpx

from fdh.llm.reviewer import SUGGESTED_MODELS, _local_host
from fdh.models import Rule

_TOKEN = re.compile(r"[a-záéíóúñ0-9]{3,}", re.IGNORECASE)


def _tokens(text: str) -> list[str]:
    return [item.casefold() for item in _TOKEN.findall(text)]


def _score(query: list[str], text: str) -> float:
    if not query:
        return 0.0
    bag = Counter(_tokens(text))
    if not bag:
        return 0.0
    overlap = sum(bag[token] for token in query)
    return overlap / math.sqrt(len(bag))


def search_rules(question: str, rules: list[Rule], limit: int = 5) -> list[Rule]:
    query = _tokens(question)
    ranked = sorted(rules, key=lambda rule: _score(query, _blob(rule)), reverse=True)
    return [rule for rule in ranked if _score(query, _blob(rule)) > 0][:limit]


def _blob(rule: Rule) -> str:
    return " ".join(
        [
            rule.id,
            rule.title,
            rule.requirement,
            rule.source_name,
            rule.notes or "",
            " ".join(rule.frameworks),
        ]
    )


def answer_question(question: str, rules: list[Rule], limit: int = 5) -> str:
    hits = search_rules(question, rules, limit=limit)
    lines = [
        "Respuesta apoyada solo en el catálogo cargado. No es asesoría legal ni fiscal.",
        "",
    ]
    if not hits:
        lines.append("Ninguna regla del catálogo coincide con la pregunta.")
        return "\n".join(lines)
    lines.append("Reglas más cercanas:")
    for rule in hits:
        flag = " UNVERIFIED" if rule.unverified else ""
        binding = "" if rule.binding else " (referencia, no obligatoria en México)"
        lines.append(f"- `{rule.id}`{flag}{binding}: {rule.title}")
        lines.append(f"  - {rule.requirement}")
        lines.append(f"  - Fuente: {rule.source_name} — {rule.source_url}")
        if rule.unverified_detail:
            lines.append(f"  - UNVERIFIED: {rule.unverified_detail}")
    embed_note = _embedding_note(question, hits)
    if embed_note:
        lines.extend(["", embed_note])
    lines.append("")
    lines.append("Modelos locales sugeridos, si usa Ollama: " + ", ".join(SUGGESTED_MODELS) + ".")
    return "\n".join(lines)


def _embedding_note(question: str, hits: list[Rule]) -> str:
    """Optional local embedding check. Failure falls back silently to lexical order."""
    if os.environ.get("FDH_LLM_EMBEDDINGS", "").strip().lower() not in {"1", "true", "yes"}:
        return ""
    base = os.environ.get("FDH_LLM_EMBED_URL", "http://127.0.0.1:11434/api/embeddings")
    if not _local_host(base):
        return "Embeddings remotos desactivados: el texto del catálogo no sale de la máquina."
    model = os.environ.get("FDH_LLM_EMBED_MODEL", "nomic-embed-text")
    try:
        response = httpx.post(
            base,
            json={"model": model, "prompt": question[:1000]},
            timeout=3.0,
        )
        response.raise_for_status()
        vector = response.json().get("embedding")
    except (httpx.HTTPError, ValueError, KeyError):
        return "Ollama no respondió embeddings. Se usó solo la búsqueda léxica."
    if not isinstance(vector, list) or not vector:
        return "Ollama no devolvió un vector. Se usó solo la búsqueda léxica."
    return (
        f"Embeddings locales respondieron ({len(vector)} dimensiones, modelo {model}). "
        f"El orden mostrado sigue siendo el léxico sobre {len(hits)} reglas, para no "
        "depender de un modelo que no está en las pruebas."
    )

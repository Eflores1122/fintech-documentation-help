"""Evaluate a rule's matcher against the documents that belong to it."""

from __future__ import annotations

import re

from fdh.models import Check, Document, Rule
from fdh.textutil import locate_phrase, snippet


class MatchOutcome:
    def __init__(
        self,
        ok: bool,
        message: str,
        evidence: str | None = None,
        document: str | None = None,
    ) -> None:
        self.ok = ok
        self.message = message
        self.evidence = evidence
        self.document = document


def documents_for(rule: Rule, documents: list[Document]) -> list[Document]:
    expected = set(rule.documents)
    return [doc for doc in documents if expected & set(doc.types)]


def evaluate_rule(rule: Rule, documents: list[Document]) -> MatchOutcome:
    candidates = documents_for(rule, documents)
    if rule.matcher.require_document and not candidates:
        expected = ", ".join(rule.documents)
        return MatchOutcome(
            ok=False,
            message=(
                "No se encontró ningún documento clasificado como: "
                f"{expected}. La obligación queda sin soporte documental."
            ),
        )
    if not candidates:
        return MatchOutcome(ok=True, message="Sin documentos en alcance y la regla no los exige.")

    failures: list[str] = []
    evidence: str | None = None
    source: str | None = None
    for check in rule.matcher.checks:
        outcome = _run_check(check, candidates)
        if not outcome.ok:
            failures.append(outcome.message)
            if evidence is None and outcome.evidence:
                evidence = outcome.evidence
                source = outcome.document
    reviewed = ", ".join(doc.path for doc in candidates)
    if failures:
        if evidence is None and candidates[0].text:
            preview = candidates[0].text[:180]
            evidence = preview + ("…" if len(candidates[0].text) > 180 else "")
            source = candidates[0].path
        return MatchOutcome(
            ok=False,
            message=f"Se revisó {reviewed}. " + " ".join(failures),
            evidence=evidence,
            document=source or candidates[0].path,
        )
    return MatchOutcome(
        ok=True,
        message=f"Los documentos revisados cubren el criterio: {reviewed}.",
        document=candidates[0].path,
    )


def _run_check(check: Check, documents: list[Document]) -> MatchOutcome:
    if check.type == "contains_all_groups":
        return _groups(check, documents)
    if check.type == "contains_any":
        return _contains_any(check, documents)
    if check.type == "forbidden_phrases":
        return _forbidden(check, documents)
    if check.type == "regex":
        return _regex(check, documents)
    if check.type == "each_document_contains_any":
        return _each_contains(check, documents)
    if check.type == "each_document_forbidden":
        return _each_forbidden(check, documents)
    return MatchOutcome(ok=False, message=f"Tipo de chequeo no soportado: {check.type}")


def _groups(check: Check, documents: list[Document]) -> MatchOutcome:
    missing: list[str] = []
    for group in check.groups:
        if not _group_ok(group.all, group.any, documents):
            missing.append(group.name)
    if missing:
        listed = "; ".join(missing)
        return MatchOutcome(ok=False, message=f"Faltan elementos: {listed}.")
    return MatchOutcome(ok=True, message="Grupos presentes.")


def _group_ok(required_all: list[str], required_any: list[str], documents: list[Document]) -> bool:
    all_ok = all(_any_doc_has(phrase, documents) for phrase in required_all)
    any_ok = any(_any_doc_has(phrase, documents) for phrase in required_any) or not required_any
    return all_ok and any_ok


def _contains_any(check: Check, documents: list[Document]) -> MatchOutcome:
    for phrase in check.any:
        found = _first_hit(phrase, documents)
        if found is not None:
            return MatchOutcome(ok=True, message="Término presente.", document=found.path)
    label = check.label or "el término exigido"
    options = ", ".join(f"«{phrase}»" for phrase in check.any)
    return MatchOutcome(
        ok=False,
        message=f"No aparece {label}. Se buscó alguna de: {options}.",
    )


def _forbidden(check: Check, documents: list[Document]) -> MatchOutcome:
    for phrase in check.any:
        found = _first_hit(phrase, documents)
        if found is not None:
            span = locate_phrase(found.text, phrase)
            evidence = snippet(found.text, span[0], span[1]) if span else None
            label = check.label or "una expresión desactualizada o prohibida"
            return MatchOutcome(
                ok=False,
                message=f"Se encontró {label}: «{phrase}».",
                evidence=evidence,
                document=found.path,
            )
    return MatchOutcome(ok=True, message="Sin expresiones prohibidas.")


def _regex(check: Check, documents: list[Document]) -> MatchOutcome:
    assert check.pattern is not None
    pattern = re.compile(check.pattern)
    label = check.label or "el patrón exigido"
    for doc in documents:
        match = pattern.search(doc.text)
        if match and check.expect == "match":
            return MatchOutcome(
                ok=True,
                message=f"Coincide {label}.",
                evidence=snippet(doc.text, match.start(), match.end()),
                document=doc.path,
            )
        if match and check.expect == "no_match":
            return MatchOutcome(
                ok=False,
                message=f"Se encontró {label}.",
                evidence=snippet(doc.text, match.start(), match.end()),
                document=doc.path,
            )
    if check.expect == "match":
        return MatchOutcome(ok=False, message=f"No coincide {label}.")
    return MatchOutcome(ok=True, message=f"No aparece {label}.")


def _each_contains(check: Check, documents: list[Document]) -> MatchOutcome:
    missing: list[str] = []
    for doc in documents:
        if not any(locate_phrase(doc.text, phrase) is not None for phrase in check.any):
            missing.append(doc.path)
    if missing:
        label = check.label or "el elemento exigido en cada documento"
        listed = ", ".join(missing)
        return MatchOutcome(
            ok=False,
            message=f"No aparece {label} en: {listed}.",
            document=missing[0],
        )
    return MatchOutcome(ok=True, message="Cada documento trae el elemento.")


def _each_forbidden(check: Check, documents: list[Document]) -> MatchOutcome:
    for doc in documents:
        for phrase in check.any:
            span = locate_phrase(doc.text, phrase)
            if span is not None:
                label = check.label or "una expresión que el modo estricto no acepta"
                return MatchOutcome(
                    ok=False,
                    message=f"Se encontró {label}: «{phrase}» en {doc.path}.",
                    evidence=snippet(doc.text, span[0], span[1]),
                    document=doc.path,
                )
    return MatchOutcome(ok=True, message="Sin expresiones rechazadas por el modo estricto.")


def _any_doc_has(phrase: str, documents: list[Document]) -> bool:
    return _first_hit(phrase, documents) is not None


def _first_hit(phrase: str, documents: list[Document]) -> Document | None:
    for doc in documents:
        if locate_phrase(doc.text, phrase) is not None:
            return doc
    return None

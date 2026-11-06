"""Orchestrate ingestion, deterministic checks and the optional LLM review."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fdh import __version__
from fdh.catalog import load_catalog
from fdh.disclaimer import DISCLAIMER_EN, DISCLAIMER_ES
from fdh.engine.matchers import evaluate_rule
from fdh.engine.scoring import score_findings
from fdh.ingest.loaders import load_documents
from fdh.models import (
    SEVERITY_RANK,
    AuditReport,
    Document,
    Finding,
    Profile,
    Rule,
)


def run_audit(
    paths: list[Path],
    profile: Profile,
    rules_dir: Path | None = None,
    use_llm: bool = False,
    generated_at: datetime | None = None,
) -> AuditReport:
    rules = load_catalog(profile.year, rules_dir)
    llm_client = None
    llm_note = None
    llm_used = False
    rejected: list[dict[str, str]] = []
    if use_llm:
        from fdh.llm.reviewer import build_client

        llm_client, llm_note = build_client()
        llm_used = llm_client is not None
    extra = {doc_type for rule in rules for doc_type in rule.documents}
    documents = load_documents(
        paths,
        llm_complete=llm_client.complete if llm_client else None,
        extra_types=extra,
    )
    findings, omitted = _deterministic(rules, documents, profile)
    if llm_client is not None:
        from fdh.llm.reviewer import review_documents

        findings, rejected = review_documents(llm_client, rules, documents, findings)
    findings.sort(key=lambda item: (SEVERITY_RANK[item.severity], item.domain, item.rule_id))
    summary = _summary(findings)
    summary["omitted"] = len(omitted)
    summary["unverified"] = sum(1 for item in findings if item.unverified)
    summary["documents"] = len(documents)
    return AuditReport(
        tool="fintech-documentation-help",
        version=__version__,
        disclaimer=DISCLAIMER_ES,
        disclaimer_en=DISCLAIMER_EN,
        generated_at=generated_at or datetime.now(UTC),
        entity_type=profile.entity_type,
        catalog_year=profile.year,
        llm_used=llm_used,
        llm_note=llm_note,
        profile=profile.model_dump(mode="json"),
        documents=documents,
        scores=score_findings(findings),
        summary=summary,
        findings=findings,
        rejected_llm_findings=rejected,
        omitted_rules=omitted,
    )


def _deterministic(
    rules: list[Rule], documents: list[Document], profile: Profile
) -> tuple[list[Finding], list[dict[str, str]]]:
    findings: list[Finding] = []
    omitted: list[dict[str, str]] = []
    for rule in rules:
        if "tool" in rule.entity_types and not rule.applies_to_entity(profile.entity_type):
            omitted.append(
                {
                    "id": rule.id,
                    "reason": "Regla interna de la herramienta; no se audita al cliente.",
                }
            )
            continue
        if not rule.applies_to_entity(profile.entity_type):
            omitted.append(
                {
                    "id": rule.id,
                    "reason": (
                        f"No aplica a {profile.entity_type}; la regla está dirigida a "
                        + ", ".join(rule.entity_types)
                        + "."
                    ),
                }
            )
            continue
        if rule.applies_if and not profile.flag(rule.applies_if):
            findings.append(_finding(rule, "not_applicable", _na_message(rule), None, None))
            continue
        outcome = evaluate_rule(rule, documents)
        status = "pass" if outcome.ok else "fail"
        findings.append(_finding(rule, status, outcome.message, outcome.evidence, outcome.document))
    return findings, omitted


def _na_message(rule: Rule) -> str:
    return (
        f"No aplica con el perfil actual: no se declaró `{rule.applies_if}`. "
        "Actívelo en la CLI o en la interfaz si el modelo de negocio entra en el supuesto."
    )


def _finding(
    rule: Rule,
    status: str,
    message: str,
    evidence: str | None,
    document: str | None,
) -> Finding:
    return Finding(
        rule_id=rule.id,
        status=status,  # type: ignore[arg-type]
        severity=rule.severity,
        domain=rule.domain,
        title=rule.title,
        requirement=rule.requirement,
        message=message,
        evidence=evidence,
        document=document,
        fix_suggestion=rule.fix_suggestion,
        source_name=rule.source_name,
        source_url=rule.source_url,
        effective_date=rule.effective_date,
        last_verified=rule.last_verified,
        unverified=rule.unverified,
        unverified_detail=rule.unverified_detail,
        notes=rule.notes,
    )


def _summary(findings: list[Finding]) -> dict[str, int]:
    counts = {"pass": 0, "fail": 0, "not_applicable": 0, "unclear": 0}
    for finding in findings:
        counts[finding.status] += 1
    for severity in ("critical", "high", "medium", "low", "info"):
        counts[f"fail_{severity}"] = sum(
            1 for item in findings if item.status == "fail" and item.severity == severity
        )
    return counts

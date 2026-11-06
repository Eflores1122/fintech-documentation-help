"""Orchestrate ingestion, deterministic checks and the optional LLM review."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from fdh import __version__
from fdh.business import infer_business
from fdh.catalog import load_catalog
from fdh.disclaimer import DISCLAIMER_EN, DISCLAIMER_ES
from fdh.engine.matchers import evaluate_rule
from fdh.engine.scoring import score_findings
from fdh.engine.workflow import (
    apply_evidence,
    build_heatmap,
    build_inventory,
    build_opinion,
    build_phases,
    build_remediation,
    compare_with,
    decorate,
    summary_extras,
)
from fdh.ingest.loaders import load_documents
from fdh.models import (
    SEVERITY_RANK,
    AuditReport,
    Document,
    Finding,
    Profile,
    Rule,
)
from fdh.parameters import resolve_parameters
from fdh.temporal import explain_applicability, rules_as_of


def run_audit(
    paths: list[Path],
    profile: Profile,
    rules_dir: Path | None = None,
    use_llm: bool = False,
    generated_at: datetime | None = None,
    evidence: dict[str, str] | None = None,
    previous: dict | None = None,
    adversarial: bool = False,
    questionnaire: dict[str, object] | None = None,
) -> AuditReport:
    temporal_notes: list[str] = []
    if profile.as_of is not None:
        rules, temporal_notes = rules_as_of(profile.as_of, rules_dir)
    else:
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
    if evidence:
        apply_evidence(findings, evidence)
    if llm_client is not None:
        from fdh.llm.reviewer import review_documents

        findings, rejected = review_documents(
            llm_client, rules, documents, findings, adversarial=adversarial
        )
    findings.sort(key=lambda item: (SEVERITY_RANK[item.severity], item.domain, item.rule_id))
    summary = summary_extras(findings, _summary(findings))
    summary["omitted"] = len(omitted)
    summary["unverified"] = sum(1 for item in findings if item.unverified)
    summary["documents"] = len(documents)
    scores = score_findings(findings)
    inventory = build_inventory(rules, documents, profile)
    remediation = build_remediation(findings)
    opinion = build_opinion(summary, scores.overall)
    phases = build_phases(profile, inventory, summary)
    heatmap = build_heatmap(findings, scores.by_area)
    comparison = compare_with(previous, findings) if previous else []
    on = profile.as_of or date(profile.year, 12, 31)
    parameter_values, parameter_gaps = resolve_parameters(
        on, {rule.id for rule in rules}, rules_dir
    )
    business = infer_business(documents, profile.entity_type, questionnaire)
    if temporal_notes:
        business["temporal_notes"] = temporal_notes
    applicability = explain_applicability(
        rules,
        {item.rule_id: item.status for item in findings},
        omitted,
        profile.entity_type,
        profile.as_of,
    )
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
        scores=scores,
        summary=summary,
        findings=findings,
        rejected_llm_findings=rejected,
        omitted_rules=omitted,
        strictness=profile.strictness,
        phases=phases,
        inventory=inventory,
        remediation=remediation,
        opinion=opinion,
        comparison=comparison,
        heatmap=heatmap,
        as_of=profile.as_of.isoformat() if profile.as_of else None,
        business_profile=business,
        coherence=_as_rows(business.get("coherence")),
        applicability=applicability,
        parameter_gaps=parameter_gaps,
        parameter_values=parameter_values,
    )


def _as_rows(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


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
        if not rule.enabled_at(profile.strictness):
            omitted.append(
                {
                    "id": rule.id,
                    "reason": (
                        f"La regla pide estrictez {rule.min_strictness} y el perfil está en "
                        f"{profile.strictness}."
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
    finding = Finding(
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
        area=rule.area or "",
        binding=rule.binding,
        verified=not rule.unverified,
    )
    decorate(rule, finding)
    return finding


def _summary(findings: list[Finding]) -> dict[str, int]:
    counts = {"pass": 0, "fail": 0, "not_applicable": 0, "unclear": 0}
    for finding in findings:
        counts[finding.status] += 1
    for severity in ("critical", "high", "medium", "low", "info"):
        counts[f"fail_{severity}"] = sum(
            1 for item in findings if item.status == "fail" and item.severity == severity
        )
    return counts

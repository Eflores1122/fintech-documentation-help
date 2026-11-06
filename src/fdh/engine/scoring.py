"""Domain and overall scores. Informational rules do not move the number."""

from __future__ import annotations

from fdh.models import SEVERITY_WEIGHT, Finding, ScoreCard

_CREDIT = {"pass": 1.0, "unclear": 0.5, "fail": 0.0}


def score_findings(findings: list[Finding]) -> ScoreCard:
    by_domain: dict[str, list[Finding]] = {}
    for finding in findings:
        if finding.status == "not_applicable":
            continue
        by_domain.setdefault(finding.domain, []).append(finding)
    domain_scores = {domain: _ratio(items) for domain, items in sorted(by_domain.items())}
    return ScoreCard(
        overall=_ratio([item for items in by_domain.values() for item in items]),
        by_domain=domain_scores,
        weights=dict(SEVERITY_WEIGHT),
    )


def _ratio(findings: list[Finding]) -> float | None:
    weight_total = 0
    weight_got = 0.0
    for finding in findings:
        weight = SEVERITY_WEIGHT[finding.severity]
        if weight == 0:
            continue
        weight_total += weight
        weight_got += weight * _CREDIT[finding.status]
    if weight_total == 0:
        return None
    return round(100.0 * weight_got / weight_total, 1)

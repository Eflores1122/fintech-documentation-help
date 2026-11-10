# fintech-documentation-help

In-browser demo, nothing to install and no file upload to a server: [GitHub Pages](https://eflores1122.github.io/fintech-documentation-help/). If the link is not live yet, the remaining step is in [docs/demo.md](docs/demo.md).

> **This is not legal or tax advice.** It is an assisted checklist with public citations and a verification date. Rules flagged **UNVERIFIED** (`verified: false`) still need a full read of the official instrument. Compliance decisions belong to a qualified lawyer or accountant and to the current text on the Diario Oficial and the SAT, CNBV, Banxico, CONDUSEF, UIF and Congress portals. It does not replace a certified audit.

Open-source documentation auditor for Mexican fintechs: payment institutions (IFPE), crowdfunding institutions (IFC), unregulated SOFOMEs, money transmitters, investment advisers and sandbox ("modelo novedoso") filings. The default mode is the strictest auditor (`--strictness max`).

Samples are fictional: **Nube Pago** (an imaginary IFPE) and **Ladrillo Común** (an imaginary real-estate crowdfunding IFC).

Spanish documentation: [README.md](README.md).

## Three commands

```bash
python3.12 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
fdh audit samples/nube_pago/docs --year 2026 --entity IFPE --out fdh-report
fdh serve
```

## What you get

A phased review (planning, inventory, document checks, control evidence, findings, remediation, follow-up, opinion), a score by area and overall, and exports in Markdown, HTML, JSON, CSV, XLSX, a plain-text PDF and an `.ics` calendar. Findings use a formal observation: condition, criterion, cause, effect, recommendation, required evidence, suggested owner and deadline, plus the official URL.

Deterministic rules are the baseline. A local OpenAI-compatible model (Ollama, llama.cpp, LM Studio, vLLM) may only add findings tied to an existing rule id and a verbatim quote. It never lowers severity. Documents stay on the machine unless `FDH_LLM_ALLOW_REMOTE=1`.

```bash
export FDH_LLM_PROVIDER=ollama
export FDH_LLM_MODEL=qwen2.5:7b
fdh llm doctor
fdh audit samples/nube_pago/docs --llm --adversarial
```

Suggested local models: Qwen2.5, Llama 3.1 / 3.2, Mistral.

International frameworks (ISO/IEC 27001:2022, NIST CSF 2.0, PCI DSS 4.0 only if the profile processes cards, SOC 2, COSO, FATF 40) are reference mappings. The report says they are not Mexican law.

## Each year

```bash
fdh rules new-year 2027
fdh rules diff 2026 2027
```

A weekly GitHub Action hashes official SAT, Banxico, Congress and DOF pages and opens an issue when a hash changes. It does not draft rules. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Samples (strict mode, no model)

| Fictional entity | Overall | Opinion |
|---|---:|---|
| Nube Pago, IFPE | 8.8 | adverse |
| Ladrillo Común, IFC | 22.2 | adverse |

Reports live in `examples/`. Methodology: [docs/metodologia.md](docs/metodologia.md). Sources: [docs/fuentes.md](docs/fuentes.md).

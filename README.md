# Multi-AI, Multi-Cloud SRE Agent Research

## Working local prototype

The [initial multi-cloud agent](docs/implementation.md) adds a reproducible synthetic demonstration alongside this research survey. It reads fake AWS, Azure and Google Cloud SDK responses, records evidence and uncertainty, proposes a typed synthetic action, and keeps execution off by default. No credentials, LLM key, network service or paid resources are needed. Python 3.11+ is sufficient.

```powershell
$env:PYTHONPATH = "src"
python -m sre_agent.cli demo
python -m unittest discover -s tests -v
# Optional: only in-memory state changes with synthetic approval
python -m sre_agent.cli demo --simulate-approved
```

For POSIX shells, use `PYTHONPATH=src python -m sre_agent.cli demo`. The demo's three providers are **fake-client tests**, not live cloud validation. It does not diagnose root causes, run cloud changes, or prove recovery after an incident. See [ADR-001](docs/ADR-001-local-agent.md) for the requirement map and [operating gates](docs/implementation.md) for permissions, limitations and roadmap.

**English** | [日本語](README.ja.md)

A source-linked survey of existing SRE agents, cloud practitioners' talks and implementations, and academic research, followed by a staged evaluation proposal for AWS, Azure, and Google Cloud.

**Research snapshot: 2026-10-11. Status: literature and public-code review with an architecture proposal. No experiments, installations, cloud operations, or paid API calls have been performed for this repository.**

## Reading guide

Each report is available in English and Japanese; use the switcher at the top of each page.

| Order | Report | Coverage |
| --- | --- | --- |
| 1 | [Products and practitioner evidence](docs/survey-products-and-practice.md) | OpenAI's official sample, Azure SRE Agent, AWS DevOps Agent, Gemini Cloud Assist, HolmesGPT, and related candidates. Availability, access, pricing, licenses, and selection rationale |
| 2 | [Academic survey](docs/survey-academic.md) | 15 core papers and 2 supporting studies on RCA, replay benchmarks, live repair, multi-agent designs, safety, and reproducibility |
| 3 | [Architecture and minimal validation plan](docs/architecture-and-validation-plan.md) | Shared evidence, comparisons using existing AI tools, approval and execution boundaries, a one-case first experiment, and gates for live cloud tests |

## Future study: Fault injection and recovery verification

The [unimplemented proposal based on the publisher PDF](docs/chaos-resilience-future-study.md) separates the end of fault injection from verified service recovery. The paper's Section 8 proposes future evaluation, not measured effects. No cloud action or permission change has occurred.

## Main findings

- Establish a single-agent diagnostic baseline before deploying autonomous agents across three clouds.
- Compare another AI independently using the same evidence and total time/cost budget; test additional roles separately.
- Score a correct root-cause answer and sufficient supporting evidence as different outcomes.
- Separate investigation, proposed repair, human approval, scoped execution, and independent recovery checks.
- Do not treat open-source licensing, free trials, or a read-only label as proof of zero total cost or zero side effects.

The survey contrasts Microsoft's experience simplifying specialist-agent handoffs, Mary Kay's AWS-and-Azure implementation, Google SRE's controlled action workflow, and Datadog's replay-based evaluations. Product claims, customer reports, demonstrations, peer-reviewed papers, and preprints are identified separately.

## Recommended first experiment

**Diagnose one public Cloud-OpsBench snapshot with one existing MCP-compatible AI client.**

| Item | Proposed scope |
| --- | --- |
| Case | Online Boutique runtime/1, used as an integration smoke test because it is a public example |
| Components | Existing MCP server and AI client; no live Kubernetes cluster or cloud credentials |
| Limits | One run, five minutes of diagnosis, at most 20 admitted tool requests; an inference spending cap must be set before execution |
| Isolation | Keep answer labels, golden trajectories, prior runs, and live cloud tools outside the agent's access |
| Evaluation | Connectivity, faulty component, fault type, citations, handling missing evidence, action boundaries, stopping, and reproducibility |
| Alternative | Consider HolmesGPT CLI with synthetic files if the replay integration is unsuitable |

The reference is commit [`ea05dafb`](https://github.com/LLM4Ops/Cloud-OpsBench/tree/ea05dafbc87b5985df8721622d63d4229c2b4224). This proposal is based on the [published MCP interface](https://github.com/LLM4Ops/Cloud-OpsBench/blob/ea05dafbc87b5985df8721622d63d4229c2b4224/cloudopsbench_mcp/README.md), not a successful run performed here. The server needs no LLM key, but client inference may still incur charges.

## Logical architecture

```text
Public snapshots / cloud-specific read-only collection
                         |
Shared evidence: source, time, scope, missing observations
                         |
Single diagnostic AI -- independent comparison with another AI
                         |
Evidence review -> human approval -> scoped execution
                         |
Independent SLI/state checks -> cleanup and billing reconciliation
```

These are logical responsibilities, not a requirement to build a separate service for every box. Mutations use a single writer per resource. Stale approvals, API timeouts, retries, and irreversible actions require explicit handling.

## What this repository does not establish

- An overall product/model ranking, production safety certification, or SLA
- Successful live remediation based only on a diagnostic response
- Generalization from Kubernetes tasks to every cloud management API
- Equivalence between process termination, resource absence, stopped recurring charges, and reconciled billing
- Eligibility, trial availability, or final pricing for a particular account

The proposed evaluation distinguishes PASS, FAIL, INCONCLUSIVE, and NOT_RUN. An unexecuted test is not a success, and awaiting authorization is not a technical failure.

## Sources and publication scope

Each report links to official documentation, public repositories, authors' and speakers' materials, or research papers. The repository contains summaries and analysis, not full-paper reproductions, third-party source code, private telemetry, credentials, personal machine paths, or non-public operational records.

Third-party copyrights and licenses remain with their respective owners; see [Third-party materials](THIRD_PARTY_NOTICES.md). Product availability, prices, and repositories may change after the research date and must be checked again before execution.

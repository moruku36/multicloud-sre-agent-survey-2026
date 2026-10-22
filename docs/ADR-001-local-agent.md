# ADR-001: Local-first, read-only multi-cloud SRE prototype

**Status:** Accepted for this prototype
**Date:** 2026-10-22
**Decider:** implementation team; live-operation decisions remain with the repository owner

## Context

The [survey](architecture-and-validation-plan.md) recommends first evaluating one public snapshot with an existing AI client, then independently comparing another AI. It separates evidence, diagnosis, proposal, human approval, scoped execution, and independent recovery observation. The owner subsequently requested a working AWS/Azure/Google Cloud agent with a local demonstration. No cloud connection, inference charge, or resource change is authorized for this iteration.

## Decision

Use Python 3.11 and its standard library for the common model, rule-based single diagnosis, policy gate, simulation and tests. Use small read-only adapters shaped around official SDK calls. SDK clients are injected explicitly; package import and tests never construct credentials or invoke instance metadata. The default command uses synthetic fake clients. There is no live-action implementation. A future caller can supply reviewed SDK clients for read collection only after separate authorization.

The initial signal is **one scoped capacity metric per cloud**, not general incident diagnosis. A below-minimum metric is a symptom, so the diagnosis says the root cause and user impact are unconfirmed. A plan can request only `simulate_restore_capacity`, with exact target and observation hash. The synthetic executor requires matching human approval, an allowlisted target, an action and cost cap, expiry, fresh state, and one writer. It records uncertain results and never automatically retries a possibly applied change. Recovery is checked from six separate synthetic observations over 300 seconds; an executor return is not treated as recovery proof.

![Architecture rendered with Pele](agent-architecture.svg)

Mermaid source: [agent-architecture.mmd](agent-architecture.mmd).

## Requirement to acceptance mapping

| Survey requirement | This design | Acceptance test |
| --- | --- | --- |
| Shared evidence with time, scope and gaps | `Target` + `Observation`, deterministic evidence ID | AWS missing data and all three adapter tests |
| Single diagnosis, separate evidence sufficiency | Deterministic threshold diagnosis with explicit uncertainty | Missing metric is INCONCLUSIVE; below minimum cites evidence |
| Treat telemetry as untrusted | No prose to command or API-operation parser; errors do not echo SDK text | Injection and secret-suppression tests |
| Separate proposal, approval and change | Typed plan; simulation-only policy gate | No approval, wrong scope, expiry and stale state denied |
| Limit cost, retries and parallel writes | One action/unit budget, no read retry, duplicate ledger, one writer | Bounded failure and uncertain duplicate tests |
| Independently verify recovery | Six observations spanning 300 seconds | Stability, missing coverage and insufficient samples tests |
| Compare across three clouds without assuming live equivalence | Injected SDK read adapters; synthetic three-cloud demo | Three fake-client contracts and default-off demo |

## Options considered

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Existing Cloud-OpsBench MCP + AI, as survey's first experiment | Closest to survey's preferred initial evaluation | Does not itself deliver the requested cross-cloud implementation; inference path and budget not approved |
| Multi-agent framework and three cloud deployments | Broad surface | Adds cost, credentials, infrastructure and handoffs before a baseline exists |
| Chosen small deterministic core with injected SDK reads | Reproducible without keys or cloud calls; makes authority boundary testable | Cannot claim root-cause quality, live operation, or successful remediation |

## Consequences and next gates

1. Keep REPLAY01/FILE01 as separate experiments. This prototype does not score Cloud-OpsBench or HolmesGPT.
2. Before any live read: choose account, resource, metric/dimensions, explicit identity, billing cap, read permission and destination; review SDK retry and telemetry behavior. Current tests use fakes only.
3. Before any real change: implement a separate scoped executor with durable idempotency and reconciliation, obtain exact human approval, verify resource state and SLI independently, and test cleanup and cost. Do not repurpose the simulation executor for cloud writes.
4. Evaluate the rule baseline on public snapshots, then compare an independent AI under equal evidence and budget. An LLM connector is absent and unvalidated.

## Sources checked for SDK shape

- [AWS CloudWatch GetMetricData](https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_GetMetricData.html)
- [Azure MetricsQueryClient.query_resource](https://learn.microsoft.com/en-us/python/api/azure-monitor-query/azure.monitor.query.metricsqueryclient?view=azure-python-preview#query-resource)
- [Azure Application Gateway HealthyHostCount](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-network-applicationgateways-metrics)
- [Google Cloud MetricServiceClient.list_time_series](https://docs.cloud.google.com/python/docs/reference/monitoring/latest/google.cloud.monitoring_v3.services.metric_service.MetricServiceClient)
- [Google Cloud instance group size metric and resource label](https://docs.cloud.google.com/compute/docs/autoscaler/scaling-cloud-monitoring-metrics)

These API references establish call shapes and metric names. They do not establish permissions, availability or correctness in a particular account.

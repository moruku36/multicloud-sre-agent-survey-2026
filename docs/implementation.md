# Initial implementation and operating gates

The synthetic demo is a small implementation of the boundaries in [ADR-001](ADR-001-local-agent.md). It is **not** REPLAY01, FILE01, a three-cloud live test, an LLM evaluation, or proof of recovery after a security incident. The repository's [original validation plan](architecture-and-validation-plan.md) remains the guide for those later experiments.

## What runs now

1. A fake SDK response for each cloud is normalized into a target, observed value, time, source and evidence ID. Missing or stale metrics are marked inconclusive.
2. A single deterministic check compares that metric with a configured minimum. It never claims a root cause from this one signal.
3. A typed proposal names one synthetic operation and the observed evidence ID. It is not permission to execute.
4. `--simulate-approved` constructs a **synthetic** approval for demonstration, then checks target allowlist, operation, expiry, budget, fresh state and duplicate ledger before modifying in-memory state.
5. A separate synthetic probe supplies six observations over 300 seconds. Verification can fail or remain inconclusive despite an action response.

There is no shell tool, free-text-to-command conversion, LLM call, outbound network path, credential discovery, cloud mutation or cloud SDK client constructor in the demo. Only fake clients are instantiated. SDK-compatible adapters exist for read operations, but their behavior is verified only with fake clients.

## Official read interfaces and scope

| Cloud | Injected client operation | Synthetic signal | Read scope requirement |
| --- | --- | --- | --- |
| AWS | `boto3` CloudWatch client `get_metric_data` | ALB `HealthyHostCount` | Explicit account/region context and TargetGroup dimension matching the target ARN |
| Azure | `azure.monitor.query.MetricsQueryClient.query_resource` | Application Gateway `HealthyHostCount` | Resource ID under the explicit subscription; reject multiple time series until a backend dimension is chosen |
| Google Cloud | `google.cloud.monitoring_v3.MetricServiceClient.list_time_series` | `compute.googleapis.com/instance_group/size` | Explicit project and instance group name filter; reject out-of-scope or multiple time series |

The signals are not semantically identical: an AWS ALB target's health, an Azure gateway backend's health, and a GCP instance group's size answer different questions. The common model normalizes evidence and control flow; it does not equate the health claims. A GCP size of two does not establish two serving healthy instances. Threshold and metric selection are lab settings, not a universal production SLO.

## Permissions and approval checklist for any later live run

- [ ] Specify one cloud, identity, account/subscription/project, region, exact resource and metric/dimensions. Review whether the metric is available and how missing data appears.
- [ ] Approve connection and credential method separately. Inject a client explicitly. Never use default credential chains, IMDS, local CLI profiles or ambient secrets in tests. Review SDK retry and telemetry options.
- [ ] Grant only the exact read API needed for collection; confirm effective role and cross-account scope. Record API and telemetry-query costs and a stop budget.
- [ ] Use a validation environment and agree on evidence retention, redaction, audit access and deletion. Keep untrusted logs out of policy and command decisions.
- [ ] For a real change, define an allowlisted typed operation, target, impact/cost/time limits, approval identity and expiry, fresh-state check, durable operation ID, timeout reconciliation, single writer, rollback conditions and independent SLI/resource verification. Implement and test this separate executor first.
- [ ] Approve fault injection, cloud writes, isolation or rebuilds explicitly. A broad approval for diagnosis does not authorize them.
- [ ] Check cleanup and billing separately from resource state. Record PASS, FAIL, INCONCLUSIVE and NOT_RUN distinctly.

## Remaining roadmap

1. Execute the survey's pinned Cloud-OpsBench REPLAY01 under its own isolation and inference budget; record cause and evidence sufficiency separately. No model or API key is configured here.
2. Compare an independent AI on the same evidence and budget. Consider an optional LLM interface only after evaluating whether it adds value; provider calls remain unimplemented and unverified.
3. Expand each cloud's scoped signals and incident cases, preserving distinct semantics and required dimensions. Add real SDK contract tests in an authorized isolated sandbox.
4. Design a durable, separately deployed change executor only after exact operations and approvals are selected. Test partial failure, retries, concurrent writers, compensation limits and recovery observations against a disposable environment.
5. Gate any production candidate on security review, operator runbooks, SLO evidence, cost reconciliation and a limited live trial. No production-safety or complete-recovery claim follows from this synthetic demo.

## Diagram regeneration

Source: [agent-architecture.mmd](agent-architecture.mmd). Rendered artifact: [agent-architecture.svg](agent-architecture.svg).

The renderer is [Pele 1.8.0 official GitHub release](https://github.com/obsidianmd/pele/releases/tag/1.8.0), source commit `8fad23bd51783e4df1204e177a7fb0d2a30dcd13`. Official asset: `pele-1.8.0.tgz`, SHA-256 `f6fd9389d167d7fb3bd9a6fb16a9e02bdbbbee708dae7faa48769f67d38eb314` (verified before use). The committed SVG SHA-256 after generation is `dca586f243c8b00cdbbadc39c70a28c587e2b179b634474e5bc62dc8c33823a7`.

With Node 20 or later, run from the repository root in PowerShell:

```powershell
$asset = "pele-1.8.0.tgz"
curl.exe -L --fail --output $asset https://github.com/obsidianmd/pele/releases/download/1.8.0/pele-1.8.0.tgz
$expected = "f6fd9389d167d7fb3bd9a6fb16a9e02bdbbbee708dae7faa48769f67d38eb314"
if ((Get-FileHash $asset -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw "Pele hash mismatch" }
New-Item -ItemType Directory -Force node_modules/pele | Out-Null
tar -xzf $asset -C node_modules/pele --strip-components=1
node scripts/render_diagram.mjs
```

Do not disable TLS verification. The runtime demo and tests do not depend on Node or Pele.

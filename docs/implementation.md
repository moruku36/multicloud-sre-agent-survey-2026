# Initial implementation and operating gates

The synthetic demo is a small implementation of the boundaries in [ADR-001](ADR-001-local-agent.md). It is **not** REPLAY01, FILE01, a three-cloud live test, an LLM evaluation, or proof of recovery after a security incident. The repository's [original validation plan](architecture-and-validation-plan.md) remains the guide for those later experiments.

## What runs now

1. A fake SDK response for each cloud is normalized into a target, observed value, time, source and evidence ID. Missing or stale metrics are marked inconclusive.
2. A single deterministic check compares that metric with a configured minimum. It never claims a root cause from this one signal.
3. A typed proposal binds the full target, operation, evidence ID, expiry and cost in a recomputed SHA-256 digest. It is not permission to execute. The demo rejects observations older than five minutes or from the future when proposing and executing; this is a demo policy, not a production SLO.
4. `--simulate-approved` constructs a **synthetic** approval for demonstration, then checks the exact plan digest and expiry, target allowlist, operation, budget, fresh state and duplicate ledger before modifying in-memory state.
5. The demonstration reads six synthetic samples from the **same in-memory state** over 300 seconds. It checks the run and target, 60–75-second spacing, post-change timing and recency. This is not an independent real probe or evidence of continuous recovery.

There is no shell tool, free-text-to-command conversion, LLM call, outbound network path, credential discovery, cloud mutation or cloud SDK client constructor in the demo. Only fake clients are instantiated. SDK-compatible adapters exist for read operations. They are verified with fake clients and with an offline [SDK type contract check](#sdk-type-contract-check); no live API response has been observed.

## Official read interfaces and scope

| Cloud | Injected client operation | Synthetic signal | Read scope requirement |
| --- | --- | --- | --- |
| AWS | `boto3` CloudWatch client `get_metric_data` | ALB `HealthyHostCount` | Exact account/region plus `LoadBalancer` and `TargetGroup` ARN-derived dimensions |
| Azure | `azure.monitor.query.MetricsQueryClient.query_resource` (azure-monitor-query 1.x only; see the contract section) | Application Gateway `HealthyHostCount` | Resource ID under the explicit subscription; reject multiple time series until a backend dimension is chosen |
| Google Cloud | `google.cloud.monitoring_v3.MetricServiceClient.list_time_series` | `compute.googleapis.com/instance_group/size` | Filter and validate metric type, resource type, project ID, location and group name; reject out-of-scope or multiple time series |

The signals are not semantically identical: an AWS ALB target's health, an Azure gateway backend's health, and a GCP instance group's size answer different questions. The common model normalizes evidence and control flow; it does not equate the health claims. A GCP size of two does not establish two serving healthy instances. Threshold and metric selection are lab settings, not a universal production SLO. [AWS publishes ALB HealthyHostCount with LoadBalancer and TargetGroup dimensions](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html); [Google Cloud monitoring scopes can include another project's instance group metrics](https://docs.cloud.google.com/compute/docs/autoscaler/scaling-cloud-monitoring-metrics#autoscale-based-on-a-metric-from-a-different-project).

The fixture is bundled in the Python package, and CI runs the built package from outside the source checkout. The synthetic duplicate ledger and writer guard are process-local; SDK request timeouts/retry configuration, durable idempotency, cross-process writer coordination and a real independent probe are unimplemented and unverified.

## SDK type contract check

`tests/test_sdk_contract.py` passes each case in the packaged fixture through the real adapter as objects built from the public SDKs' own model classes, then asserts the resulting evidence ID equals the fake-client demo's. It also validates each request: AWS against the botocore CloudWatch `GetMetricData` input/output shapes, Azure against the real `query_resource` keyword names, and Google Cloud against `ListTimeSeriesRequest` and `MetricServiceClient.list_time_series`. It creates no client, session, credential or network connection. Run it with `python -m pip install -r requirements-sdk-contract.txt` and `SRE_REQUIRE_SDK_CONTRACT=1 python -m unittest discover -s tests -p "test_sdk_contract.py"`. Without the flag, a missing SDK skips the tests; CI's `sdk-contract` job sets it so a skip cannot pass silently.

What it found: the Azure adapter read `MetricValue.time_stamp`, but every checked `azure-monitor-query` 1.x release (1.0.0 to 1.4.1) exposes `timestamp`. With real objects the adapter failed closed with `CollectionError`; the earlier fakes shared the wrong name, so the unit tests and demo passed. Fixed; the adapter also now requests `aggregations=["Average"]` because it reads `.average`.

Limits, stated plainly:

- Responses are constructed from SDK classes, not deserialized from real service output. Field semantics, permissions, metric availability, dimensions, aggregation defaults and pagination are unverified.
- Azure: verified only against `azure-monitor-query` 1.4.1. Version 2.0.0 has no `MetricsQueryClient`; metrics moved to `azure-monitor-querymetrics`, whose `MetricsClient.query_resources(resource_ids=..., metric_namespace=..., metric_names=...)` returns a list and has a different signature. That client is **not supported**; it would need its own adapter and contract test. The test fails under 2.x when `SRE_REQUIRE_SDK_CONTRACT=1`.
- AWS: botocore validates structure but not enum membership (the test checks `ScanBy` explicitly). The adapter rejects a paginated `NextToken` result as incomplete; it does not fetch later pages or exercise signing.
- Direct SDK versions are pinned; transitive dependencies are not. Checked with Python 3.11 and 3.13 against the pins in `requirements-sdk-contract.txt`; other versions are untested.

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
3. Expand each cloud's scoped signals and incident cases, preserving distinct semantics and required dimensions. Offline SDK type contracts exist (above); add live SDK contract tests in an authorized isolated sandbox and, if Azure 2.x is needed, a separate `azure-monitor-querymetrics` adapter.
4. Design a durable, separately deployed change executor only after exact operations and approvals are selected. Test partial failure, retries, concurrent writers, compensation limits and recovery observations against a disposable environment.
5. Gate any production candidate on security review, operator runbooks, SLO evidence, cost reconciliation and a limited live trial. No production-safety or complete-recovery claim follows from this synthetic demo.

## Diagram regeneration

Source: [agent-architecture.mmd](agent-architecture.mmd). Rendered artifact: [agent-architecture.svg](agent-architecture.svg).

The renderer is [Pele 1.8.0 official GitHub release](https://github.com/obsidianmd/pele/releases/tag/1.8.0), source commit `8fad23bd51783e4df1204e177a7fb0d2a30dcd13`. Official asset: `pele-1.8.0.tgz`, SHA-256 `f6fd9389d167d7fb3bd9a6fb16a9e02bdbbbee708dae7faa48769f67d38eb314` (verified before use). The committed SVG SHA-256 after generation is `d5436c50e2afb18a5f21872a1c9c183f64a29f35e9894d87959de92d12a395f0`.

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

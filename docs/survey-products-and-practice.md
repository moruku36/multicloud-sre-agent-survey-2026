# SRE Agent Survey: Products, Practitioner Talks, and Implementation Cases

**English** | [日本語](survey-products-and-practice.ja.md) · [Overview](../README.md)

Research date: 2026-10-11
Status: findings from public primary sources. No installation or measurement has been run.
Purpose: cross-check products, talks, implementation cases, and academic research to choose candidate configurations for a multi-AI, multi-cloud setup.

## 1 Conclusion

**The recommendation is to start with the diagnosis of one existing agent, compare another AI on shared evidence, and add only the role splits that show an effect.** The first experiment is replay-style diagnosis with Cloud-OpsBench and an existing AI; synthetic-file diagnosis with the HolmesGPT CLI is the alternative. Start real cloud work with the one provider that is actually needed, and choose between AWS DevOps Agent and Azure SRE Agent by use case. This survey found no basis for building autonomous agents on all three clouds first.

OpenAI's official "Build an SRE agent for incident response" was published on 2026-09-10. It is an implementation example that investigates a bundled synthetic incident and records a rollback approval in Slack; it does not perform a real rollback. From public information alone, we do not conclude it is a finished, standalone operational service. [OpenAI official sample](https://developers.openai.com/cookbook/examples/agents_api/apps/sev_bot/readme)

Four main points where the survey changes the design:

- A first evaluation that only reads logs does not need new Kubernetes or load balancers and VMs on three clouds.
- Check the scope behind "read-only," "Review," and "free trial." Bash, external notifications, monitoring settings, and log-query charges do not automatically become safe or free.
- Evaluate root-cause inference, the approval flow, real data collection, and real repair as separate stages. Do not stretch a working demo into proof of SLOs, recovery, or stopped billing.
- Microsoft's experience with failed handoffs between specialist agents and AWS's and Google's examples of role splitting coexist. Treat multi-AI as a variable to compare, not a goal, and measure the difference from a single agent with matched evidence and budget.

This round only read public primary sources and public code. No installation, API execution, account operation, outside inquiry, billing, or cloud operation was done.

## 2 Where each candidate stands

| Candidate | Availability and version checked | Coverage | Role in the first round |
| --- | --- | --- | --- |
| OpenAI sev_bot | Official Cookbook example published 2026-09-10. The underlying Agents API went public beta the same day | The sample covers GitHub, AWS, and Slack. External evidence can be swapped | Official implementation example. Suited to checking the approval flow |
| HolmesGPT | 0.43.0, 2026-10-07, prerelease=false, CNCF Sandbox | Local files, Kubernetes, observability, toolsets/MCP for each cloud | Alternative candidate for file-only diagnosis |
| Robusta Platform | Commercial managed / enterprise self-hosted product. A single GA date and pinned version were not settled this round | UI, notifications, alert triage, and continuing investigation built around HolmesGPT | A stage for trying team operations. Not needed for the initial CLI run |
| Azure SRE Agent | Preview 2025-05-19, GA 2026-03-10 | Azure-centric. MCP and AWS DevOps Agent integration officially announced | Comparison candidate for Azure-native operations |
| AWS DevOps Agent | Preview 2025-12-02, GA 2026-03-31 | AWS, Azure, on-prem. Depends on the connection source and permissions | Main managed candidate for multi-cloud investigation |
| CloudWatch investigations | Preview 2024-12-03, GA 2025-06-24 | AWS metrics, logs, traces, and change events | One-shot diagnosis baseline for existing AWS environments |
| Gemini Cloud Assist | Preview in docs updated 2026-10-07. Proactive investigations are in private preview | GCP. An investigation covers a single project / App Hub application | Later candidate once eligibility is checked. Not used for free local tests |
| K8sGPT | v0.4.40, 2026-10-09, prerelease=false | Kubernetes analyzers and optional LLM explanation | Excluded from the first round that uses arbitrary logs only |

GA is not a guarantee of availability for every feature, region, and account. AWS DevOps Agent's release management is a separate feature in preview; do not mix it with the GA base service. That a model can use AWS Bedrock / Azure / Vertex is also separate from being able to investigate that cloud's resources.

Primary sources: [Agents API changelog](https://developers.openai.com/api/docs/changelog), [HolmesGPT release](https://github.com/HolmesGPT/holmesgpt/releases/tag/0.43.0), [Robusta architecture](https://docs.robusta.dev/master/how-it-works/oss-vs-saas.html), [Azure GA](https://techcommunity.microsoft.com/blog/appsonazureblog/whats-new-in-azure-sre-agent-in-the-ga-release/4500779), [AWS GA](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/), [CloudWatch GA](https://aws.amazon.com/about-aws/whats-new/2025/06/ga-accelerate-troubleshooting-amazon-cloudwatch-investigations/), [K8sGPT release](https://github.com/k8sgpt-ai/k8sgpt/releases/tag/v0.4.40).

## 3 Permissions, cost, and adoption decision per candidate

### OpenAI sev_bot

- **What it is**: a code example in the official OpenAI Cookbook. It combines Agents API sessions, tools, memory, webhooks, and approvals. The reference code is openai-cookbook commit 5bd6cb40b6b84b69b2032d810610aa85064102df. Nothing in this example implies GA of a separate managed "SRE Agent" product.
- **Permissions**: the bundled evidence tools are read-only. Rollback stops at proposing and recording an approval; it does not call a deployment system. Live GitHub/AWS connections are optional. Installing only the AWS skills does not grant AWS access.
- **Preparation**: Python 3.14 or later, uv, a sandbox such as Docker, an OpenAI API key plus a separate executor key, and a Slack app. Two-way approval needs a public HTTPS callback and signature verification.
- **Local trial**: data can be the bundled fixtures. But run as in the sample, OpenAI API calls and Slack posts are real. It is not fully offline.
- **Pricing and license**: the Cookbook code is MIT. OpenAI service terms are separate. Models are billed at the chosen API price, tools at their listed prices, and OpenAI-hosted sandboxes at container prices. Using your own Docker does not make model API calls free. Total run cost and free-tier eligibility are unconfirmed.
- **This round**: adopted as a candidate for evaluating the official example's approval boundary. It needs more setup than the first replay diagnosis, so it is a separate track for evaluating the approval flow. Set priority by purpose and the integrations needed.

Basis: [sample text](https://developers.openai.com/cookbook/examples/agents_api/apps/sev_bot/readme), [read-only tools and optional MCP implementation](https://github.com/openai/openai-cookbook/blob/5bd6cb40b6b84b69b2032d810610aa85064102df/examples/agents_api/apps/sev_bot/tools.py), [approval and cleanup implementation](https://github.com/openai/openai-cookbook/blob/5bd6cb40b6b84b69b2032d810610aa85064102df/examples/agents_api/apps/sev_bot/agent.py), [MIT](https://github.com/openai/openai-cookbook/blob/5bd6cb40b6b84b69b2032d810610aa85064102df/LICENSE), [Agents API pricing treatment](https://developers.openai.com/api/docs/guides/agents-api/overview), [usage notes](https://developers.openai.com/api/docs/guides/agents-api/observability).

### HolmesGPT

- **Input**: the CLI's file input accepts logs and public runbooks. Multiple files, prompt files, one-shot non-interactive runs, and saving JSON responses were confirmed in the source. Saving JSON is not a guarantee of conformance to any particular diagnostic schema.
- **Coverage**: beyond Kubernetes, there are toolsets/MCP for VMs and observability on AWS, Azure, and GCP. Coverage depends on the tools connected and their permissions.
- **Safety notes**: it auto-detects available toolsets, and the CLI may use existing credentials or kubeconfig. Bash is enabled by default. Adding a Kubernetes remediation MCP enables restart, scale, patch, and similar. Do not use these in the first round.
- **Authentication needed**: file diagnosis alone needs no cloud authentication. An external LLM needs that provider's API authentication. Adding live connections needs AWS IAM/CLI, Azure RBAC/CLI, GCP IAM/gcloud or ADC, and so on.
- **Pricing and license**: 0.43.0 is Apache-2.0. There is no OSS usage fee, but external LLM, GPU/runtime environment, and target API charges are separate. Use the LICENSE at the adopted tag, not the MIT notation in older material.
- **This round**: the alternative if the Cloud-OpsBench / existing-AI connection does not fit. Confirm effective tool disabling and isolation, then diagnose one synthetic log. Live collection and repair capability are out of scope.

Basis: [CLI implementation](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/holmes/main.py), [file addition](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/holmes/core/prompt.py), [Apache-2.0](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/LICENSE), [Bash](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/bash.md), [Remediation MCP](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/kubernetes-remediation-mcp.md), [AWS](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/aws.md), [Azure](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/azure-mcp.md), [GCP](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/data-sources/builtin-toolsets/gcp.md).

### Conditions for running HolmesGPT fully locally

There is an official Ollama path, and local Ollama needs no API key. But it is experimental, and tool calling can be unstable. The model's license, RAM/VRAM, and the fetch and runtime environment must be checked separately. [Ollama integration](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/docs/ai-providers/ollama.md)

An empty toolsets setting does not mean "all tools disabled." No single switch that disables everything was found; you must override each toolset of the pinned version with enabled:false and check the list of enabled ones. bash-always-deny also denies what is outside an allowlist and does not mean all Bash is denied. [Toolset management](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/holmes/core/toolset_manager.py)

Setting max-steps to 1 has a code path that runs without tools from the first model call, but it does not suppress initialization or precondition checks. So it cannot be a safety boundary by itself. [Call implementation](https://github.com/HolmesGPT/holmesgpt/blob/0.43.0/holmes/core/tool_calling_llm.py)

The minimal test requires an isolated environment with no existing home directory or credentials, egress blocked except local inference, toolsets disabled, and no fallback. So far this rests on documents and code, not on a guarantee that it works on real hardware. If the conditions cannot be met, hold off running it.

### Robusta Platform

A management layer built around HolmesGPT, providing a web UI, Slack/Teams, background investigation, and management of multiple agents. Do not count it twice as an inference engine independent of HolmesGPT.

The commercial Platform is advertised as free to start, but current pricing is quote-based and firm numbers for free counts and periods could not be obtained. The self-hosted Platform is an enterprise plan. It requires the standard in-cluster install and a Platform account, so a first round with only synthetic files would need extra setup. Once connected, confirm the read and repair boundaries, including HolmesGPT's tools, RBAC, and added integrations.

The public repo robusta-dev/robusta is **Robusta Classic**, a rule-based alert enrichment engine, MIT, 0.51.0. Do not infer from this that the whole commercial Platform is MIT, free, or locally distributable. This round treats it as a team-operations candidate after the CLI shows diagnostic value.

Basis: [OSS vs. SaaS distinction](https://docs.robusta.dev/master/how-it-works/oss-vs-saas.html), [pricing](https://home.robusta.dev/pricing), [Classic](https://github.com/robusta-dev/robusta/blob/master/README.md), [Classic release](https://github.com/robusta-dev/robusta/releases/tag/0.51.0).

### Azure SRE Agent

A managed product that monitors, investigates, and responds, centered on Azure. MCP and AWS DevOps Agent integration have also been officially announced, but we do not conclude from that alone that it has the same repair capability across all clouds including GCP. [GA](https://techcommunity.microsoft.com/blog/appsonazureblog/whats-new-in-azure-sre-agent-in-the-ga-release/4500779), [AWS integration](https://techcommunity.microsoft.com/blog/appsonazureblog/announcing-aws-with-azure-sre-agent-cross-cloud-investigation-using-the-brand-ne/4507413)

- An active Azure subscription is required. The creator needs Owner, or Contributor plus User Access Administrator, etc. The agent uses a managed identity.
- Even when Reader is selected, the description includes Monitoring Contributor, so alert ack/close and monitoring configuration changes may not be out of reach. Check the effective role assignments.
- Review covers change approval for Azure infrastructure. External operations such as email and Teams are not behind the same gate. Response plans and scheduled tasks are described as Autonomous by default, so check Review and the tool policy for each unit.

Basis: [creation requirements](https://learn.microsoft.com/en-us/azure/sre-agent/create-and-set-up), [permissions](https://learn.microsoft.com/en-us/azure/sre-agent/permissions), [run modes](https://learn.microsoft.com/en-us/azure/sre-agent/run-modes).

Pricing is a fixed 4 AAU per agent-hour plus model-specific token AAU. The new trial is up to 30 days and 3 agents, mainly waiving the fixed part, and active use is paid. The fixed charge continues until the agent is deleted. A currency unit price could not be settled from the public pricing page, and unit prices from older articles should not be carried into current estimates. [Pricing structure](https://learn.microsoft.com/en-us/azure/sre-agent/pricing-billing), [trial](https://learn.microsoft.com/en-us/azure/sre-agent/evaluate), [pricing page](https://azure.microsoft.com/en-us/pricing/details/sre-agent/)

The public microsoft/sre-agent is an MIT collection of labs and templates and is not a local distribution of the managed product runtime. Even though synthetic knowledge files can be provided, a running Azure agent is required. This round treats it as a candidate only for Azure-specific operational evaluation and does not use it in the first local experiment. [Official repo](https://github.com/microsoft/sre-agent), [knowledge files](https://learn.microsoft.com/en-us/azure/sre-agent/tutorial-upload-knowledge-document)

### AWS DevOps Agent

A managed product that added Azure support at GA. A candidate for investigating multiple sources across AWS, Azure, and on-prem. For the first round, one Agent Space and a limited AWS scope are enough, and Azure need not be connected at the same time. [GA announcement](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)

- Read-only by default. Directed actions are currently OFF by default; enabling them needs an elevated IAM role and operator approval at run time. Do not rule out current repair features on the strength of older "read-only only" descriptions.
- Requires an AWS account, an IAM role for investigation, and operator access. Start from AWS standard policies and limit the scope.
- Azure integration needs Entra consent or your own app / federated identity. A Reader connection on the Azure side is not permission for Azure write access.

Basis: [directed actions](https://docs.aws.amazon.com/devopsagent/latest/userguide/working-with-devops-agent-working-with-directed-actions.html), [limiting AWS access](https://docs.aws.amazon.com/devopsagent/latest/userguide/aws-devops-agent-security-limiting-agent-access-in-an-aws-account.html), [Azure authentication](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-integrations-and-knowledge-connecting-azure-index.html).

Current pricing is 0.0083 USD per agent-second for investigation, evaluation, and on-demand SRE, with no charge while idle. An agent-second is the cumulative time of activity within a task and is not necessarily the same as simple human waiting time. The new trial is two months from the first operational task, with per month up to 10 Agent Spaces, 20 hours of investigation, 15 hours of evaluation, and 20 hours of chat. Beyond that it is pay-as-you-go, and charges such as CloudWatch queries are separate. This confirms the pricing structure only, not any user's trial eligibility or this round's total. [AWS pricing](https://aws.amazon.com/devops-agent/pricing/)

The service itself cannot run locally. Items such as the MIT-0 sample plugin are examples of integrating with the service and do not make the service itself open source. Even with synthetic evidence, an Agent Space is needed. This round adopts it as the next managed candidate and looks only at diagnosis with directed actions OFF. [assets](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-managing-assets.html), [MIT-0 sample](https://github.com/aws-samples/sample-aws-devops-agent-claude-plugin)

### CloudWatch investigations

The shortest baseline candidate for existing AWS environments. Current one-shot investigations have a path that starts with no additional configuration and investigates metrics, logs, and so on with the read-only permissions of the signed-in console session. Permission to start an investigation is needed separately. A one-shot investigation is visible only to the person who ran it and is deleted after 24 hours, so save needed evidence before then. [One-shot investigations](https://docs.aws.amazon.com/en_en/AmazonCloudWatch/latest/monitoring/Investigations-Ephemeral.html), [security](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Investigations-Security.html)

Proposing or launching a Systems Manager Automation runbook is treated as a separate repair operation and is not launched in the first round. The feature has no additional charge, but telemetry, API, and similar costs are separate. We found no way to evaluate this product using only local synthetic files. [Features](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Investigations.html), [costs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/investigations-costs.html)

An adoption candidate for AWS one-shot diagnosis. We do not go as far as treating it as a replacement for multi-cloud investigation or repair agents.

### Why K8sGPT and CloudWatch Omni are left out of the first round

K8sGPT is Apache-2.0, inspects Kubernetes read-only, and explains with an LLM. It needs a kubeconfig, and we found no standard analyze path that takes an arbitrary log file. That does not fit this round's no-cluster condition. Being able to handle Kubernetes on AWS/Azure/GCP is separate from investigating general cloud services across clouds. [README](https://github.com/k8sgpt-ai/k8sgpt/blob/main/README.md), [security](https://github.com/k8sgpt-ai/k8sgpt/blob/main/SECURITY_SELF_ASSESSMENT.md), [CLI](https://github.com/k8sgpt-ai/k8sgpt/blob/v0.4.40/cmd/analyze/analyze.go)

CloudWatch Omni, announced GA on 2026-09-22, is related, but its focus is AI agent telemetry, quality, and observability. It works with AWS DevOps Agent for RCA, so it is not counted separately as an independent competitor. A free local IDE feature does not mean it can demonstrate VM incident response offline. [GA announcement](https://aws.amazon.com/blogs/aws/introducing-amazon-cloudwatch-omni-ai-powered-observability-for-generative-ai-and-agentic-workloads/), [Omni agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/omni-ask-the-omni-agent.html)

### Conditions for keeping Gemini Cloud Assist as a GCP candidate

A commercial service, not a locally distributed SRE runtime. The docs updated 2026-10-07 state Preview. Since April 10, existing investigations require access through a Premium Support contract or the account team. Proactive alert investigation and cost optimization are private preview and for Premium Support. Do not judge general availability from older introductory articles.

Ordinary investigations use the user's OAuth credentials and read permissions on the target, and the docs state the token is not used to modify data. On the other hand, changes in general chat require the user's explicit consent, and the background agent uses a dedicated service account, which are separate paths. A broad user IAM widens the investigation scope. Limit the target project/application and confirm the needed audit log types are enabled.

The pricing table states no additional charge for Enterprise-covered features during Preview, but eligibility, Support contracts, and charges for surrounding services are separate. Contracts, quotas, and log charges for the target environment are unconfirmed, so the total is undetermined. It is not the first choice for free local use. No outside inquiry or contract addition was made this round.

[Availability and scope](https://docs.cloud.google.com/cloud-assist/investigations), [creation permissions](https://docs.cloud.google.com/cloud-assist/create-investigation), [identity and approval](https://docs.cloud.google.com/cloud-assist/proactive-agents-concepts), [pricing](https://cloud.google.com/products/gemini/pricing), [availability changes](https://docs.cloud.google.com/cloud-assist/deprecations/features).

## 4 What to borrow from research and benchmarks

### ITBench

An ICML 2025 study covering SRE, CISO, and FinOps tasks. The code is Apache-2.0. The self-hosted SRE tests need Kubernetes, Helm, kubectl, Ansible, and so on, plus applications, observability, and fault injection. Building this from the first round would make the main work building a test platform rather than evaluating products.

What we borrow is the framing of "verify the resolution separately, not just the root cause." Choose it after live repair needs evaluating. The hosted leaderboard also needs repo registration, GitHub App permissions, and so on, so do not treat it as unconditionally free and immediately runnable.

[Paper](https://arxiv.org/abs/2502.05352), [official repo](https://github.com/itbench-hub/ITBench), [run requirements](https://github.com/itbench-hub/ITBench/blob/main/documentation/getting-started/scenarios.md), [hosted procedure](https://github.com/itbench-hub/ITBench/blob/main/documentation/getting-started/leaderboard.md)

### ITBench-AA

Published 2026-05-27. A method that reads an incident snapshot and outputs the root-cause entity and evidence in structured form; it does not measure repair. 40 public and 19 private cases, each evaluated three times. It emphasizes precision when the cause is named without missing it, and also discourages mixing downstream symptoms into the cause.

The public data is CC-BY-4.0. No cluster is needed, which fits this round, but the whole dataset is about 31.1 GB and Scenario-1 alone, as checked, is about 1.18 GB. That is heavy for a first test with a few files. In the next stage, pick a few snapshots and keep ground_truth.yaml and answer-bearing data.jsonl isolated from the agent's input.

The official harness, 100 turns, and judge differ from this round's one or two runs and scoring. Do not compare this round's results directly with official leaderboard scores or ranks.

[Evaluation method](https://artificialanalysis.ai/evaluations/itbench-aa), [methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking#itbench-aa), [public dataset](https://huggingface.co/datasets/ArtificialAnalysis/ITBench-AA)

### AIOpsLab

An MLSys 2025 study from the Microsoft Research family, released under MIT. It evaluates detection, localization, analysis, and mitigation with real applications, load generation, fault injection, and telemetry. It needs Python 3.11 or later, Helm, Kubernetes, and so on, and even the Kind path needs Docker and the like.

A candidate for a later stage to confirm "whether the proposed response really recovered the system." Not introduced in the first round of local synthetic logs. [Research introduction](https://microsoft.github.io/AIOpsLab/), [paper](https://arxiv.org/abs/2501.06706), [official repo](https://github.com/microsoft/AIOpsLab), [Kind requirements](https://github.com/microsoft/AIOpsLab/blob/main/kind/README.md)

### Integration with the academic survey

The [academic survey](survey-academic.md) covers 15 core papers and 2 supporting ones. This document sorts out only what bears directly on adoption decisions.

| Stage | Candidate and venue | What it gives / limits |
| --- | --- | --- |
| First same-evidence comparison | Cloud-OpsBench, first version 2026-02 / v2 08-22, preprint | Replay of a diagnosis tool's snapshot. Scores correctness and evidence sufficiency separately. Does not measure real repair |
| Large-scale data analysis | OpenRCA, ICLR 2025 | Analysis of logs, metrics, and traces. Check capacity, RAM, and time systems. Not a repair evaluation |
| Live environments | AIOpsLab, MLSys 2025 / ITBench, ICML 2025 | Evaluate diagnosis and actual recovery separately. Build and operation burden |
| Noise and compound failures | SREGym, first version 2026-05 / v3 07-30, preprint | A later, harder evaluation. All problems require SSH/root on Linux nodes, so it does not apply as is to EKS/AKS/GKE |
| Off-the-shelf research agent | STRATUS, NeurIPS 2025 | A state machine of diagnosis, mitigation, and Undo. It assumes a single writer, exact Undo, etc., and cannot generally prevent mid-course worsening or irreversible APIs |
| Safety | AIOpsDoom, USENIX Security 2026 | Instructions hidden in telemetry can induce wrong responses. Do not treat observed data as approval; keep authorization decisions outside the model |
| Comparing role splits | mABC, Findings of EMNLP 2024 / LATS-RCA, SEAA 2026 / RCLAgent, 2026 preprint | Options of voting, hypothesis search, and dependency-based division of labor. Do not treat more agents as better quality as is |

Primary sources: [Cloud-OpsBench](https://arxiv.org/html/2603.00468v2), [OpenRCA](https://microsoft.github.io/OpenRCA/), [SREGym](https://arxiv.org/html/2605.07161v3), [STRATUS](https://arxiv.org/html/2506.02009v2), [AIOpsDoom](https://www.usenix.org/conference/usenixsecurity26/presentation/pasquini), [mABC](https://aclanthology.org/2024.findings-emnlp.232/), [LATS-RCA](https://arxiv.org/abs/2605.03505), [RCLAgent](https://arxiv.org/abs/2605.14866).

In particular, Cloud-OpsBench is a public MIT implementation, and MCP was added in commit `ea05dafbc87b5985df8721622d63d4229c2b4224` on 2026-10-06. The server itself needs no LLM key or live cluster. There are Codex / OpenCode connection examples, making it an entry point to try without rebuilding an existing AI. But client inference cost is separate, native Windows operation is unconfirmed, and MCP itself does not isolate the client's filesystem. The current JSONL trace is not directly the evaluation format for the bundled agent. [MCP spec](https://github.com/LLM4Ops/Cloud-OpsBench/blob/ea05dafbc87b5985df8721622d63d4229c2b4224/cloudopsbench_mcp/README.md), [license](https://github.com/LLM4Ops/Cloud-OpsBench/blob/ea05dafbc87b5985df8721622d63d4229c2b4224/LICENSE).

## 5 Practitioner talks, development experience, and implementation cases

Do not conflate product specifications, developers' self-reports, demos, and peer-reviewed research. The reflections on our design below are this round's judgments, not a claim that the vendors guarantee this multi-cloud configuration.

### Microsoft: a talk on SRE Agent anti-patterns

**Toru Makabe, "Azure SRE Agent anti-patterns you should know to use it well."** The public slides were published 2026-10-07, and the title page lists him as Senior Cloud Solution Architect at Microsoft Japan. We used the parts of the public transcript we could confirm and do not claim to have checked every slide image.

| Caution confirmed | How we avoid it this round |
| --- | --- |
| Wasting cost by routing every alert to the AI | Narrow the target by SLO, severity, and duplicate suppression, and use known routine handling first |
| Accepting the AI's answer without understanding it | Review evidence IDs, counter-evidence, and unconfirmed points; do not pass on self-assessment alone |
| Reports that do not lead to decisions | Specify the reader, the decision, and the next action, and leave a short accept/reject per incident |
| Expecting resolution without the needed code or telemetry | Keep a ledger of connection and observation gaps, and do not misjudge missing information as lack of ability or as normal |

The material covers not just incident response but success criteria, understanding, improvement, operations, and spreading learning. We likewise do not make the number of deployments or the level of autonomy the goal; we measure whether it helps operational decisions. [The author's slides](https://speakerdeck.com/torumakabe/tsukaikonasu-tame-ni-shi-te-okitai-azure-sre-agent-anchipatan)

### Microsoft: from fragmented multi-agent to a few generalists

**Sanchit Mehta et al., 2025-12-26, on developing Azure SRE Agent.** They report that handoffs between many Azure-service-specific agents caused undiscoverability, context pollution, repetition, and narrowed vision, and that they reorganized into a few generalists plus knowledge read on demand. This is one product's experience and not a demonstration that "all multi-agent designs are bad." The description of using broad tools is also no basis for granting broad IAM.

What we adopt is the policy of a single-agent baseline first, additional AIs in limited roles such as independent diagnosis or evidence checking, and recording handoff counts and cost. Do not design many per-service agents first. [Developer article](https://techcommunity.microsoft.com/blog/appsonazureblog/context-engineering-lessons-from-building-azure-sre-agent/4481200)

**Dalibor Kovacevic, 2026-03-10, an implementation example of GA onboarding.** He connected the code, logs, deployment, and knowledge of a real sample app and separated insufficient RBAC from a missing telemetry exporter. A design reference: do not count merely creating an agent resource as ready. This is insight from internal operations and experiments on a sample app, not an independent product comparison. [Process article](https://techcommunity.microsoft.com/blog/appsonazureblog/what-it-takes-to-give-sre-agent-a-useful-starting-point/4500343)

### AWS: a customer implementation close to ours (AWS plus Azure)

**James Ickes (Mary Kay Technical Architect) / Emmanuel Isimah (AWS Senior Solutions Architect), 2026-08-25.** AWS DevOps Agent investigation results are passed along as JSON and branched to triage / specialist agents through events, queues, and workflows. A customer co-authored production example describing the Sonnet and Haiku role split, AgentCore's isolated environment, and PR creation in Azure DevOps.

What we adopt are the boundaries of "separate investigation from change by artifacts," "suppress duplicates," and "turn fix proposals into PRs." The numbers are customer self-reports, and details of least-privilege IAM, human approval, merge, and rollback are unclear from the article alone. Do not copy a large AWS event platform into the first round. [Official customer implementation](https://aws.amazon.com/blogs/industries/how-mary-kay-built-self-triaging-operations-with-amazon-bedrock-2/)

**Amit Arora / Dheeraj Oruganty, 2025-09-26.** A public demo using a LangGraph supervisor and four agents (Kubernetes, logs, metrics, runbook), with AgentCore identity/runtime/gateway. The text says it uses synthetic data and stub backends, so it does not count as a production repair record. Do not reuse the sample's broad permission settings as production least privilege. [Technical article](https://aws.amazon.com/blogs/machine-learning/build-multi-agent-site-reliability-engineering-assistants-with-amazon-bedrock-agentcore/), [public implementation](https://github.com/awslabs/agentcore-samples/tree/main/02-use-cases/01-conversational-agents/SRE-agent)

### Google: separate freedom in diagnosis from control over changes

**Riccardo Carlesso / Ramón Medrano Llamas, 2026-01-22.** A process article by Google SREs on Gemini CLI / ProdAgent. The incidents shown are simulations. It describes typed MCP operations, risk levels, context-dependent policy, human approval in the CLI, and auditing of proposals and approvals. The internal ProdAgent itself is not a public product that can be reused.

What we adopt: include verification and recovery conditions in the runbook, and hand off to scoped execution instead of calling APIs directly from the diagnosis result. Do not treat a simulation or an internal-use description as a guarantee of autonomous repair for general users. [Google process article](https://cloud.google.com/blog/topics/developers-practitioners/how-google-sres-use-gemini-cli-to-solve-real-world-outages/)

### Datadog: evaluate the investigation process, not just the final answer

**Daniel Shan / Tristan Ratchford, 2026-01-12.** A development explanation of Bits AI SRE, which forms hypotheses, refutes them with telemetry, and digs deeper. It shows an example where summarizing messy data in one pass led the root-cause estimate astray. [Development article](https://www.datadoghq.com/blog/building-bits-ai-sre/)

**Benjamin Barton, 2026-04-07.** Covers offline replay that preserves the observed state of real incidents, and root cause, investigation process, and regression detection. The key point is that tests of the model or tools alone cannot guarantee overall quality. It is a self-report using non-public internal evaluations and customer data and cannot be compared directly with public benchmarks. We adopt the policy of fixing snapshots and scoring root-cause correctness, evidence reached, and wrong operations separately. [Evaluation platform article](https://www.datadoghq.com/blog/engineering/bits-ai-eval-platform/)

### References on multi-AI connection and observation

- **PayPal, 2026-10-08, official implementation article.** Connects multiple AI clients to a common MCP Hub, explaining permissions at tool discovery, re-authorization at invoke, and separation of downstream credentials. It is not an SRE agent product itself. We adopt only the principle that "even for what looks like the same tool, check the person, agent, and target scope on every execution." [MCP Hub](https://developer.paypal.com/community/blog/One_connection_2000_tools/)
- **Vipul Rajendra Gargav / Rajesh Kumar Ravi, 2026-08-13, AWS official implementation example.** Connects an agent on GCP Cloud Shell to AgentCore Observability via OpenTelemetry and tracks model calls, tokens, latency, and sessions. It is not a demonstration of cross-cloud repair or multi-AI collaboration. It is a reference that the observation destination can be separated from the cloud where it runs; for the first round, local traces suffice. [Observability implementation](https://aws.amazon.com/blogs/machine-learning/monitor-on-premises-and-multi-cloud-ai-agents-with-agentcore-observability/)

### How to read related talks

| Talk | Date and scope checked | Use and reservations |
| --- | --- | --- |
| Arik Alon, HolmesGPT, KubeCon Europe 2026 | Conference 2026-03-23 to 26, author's slides checked | Read the stages of root-cause commit, PR, and rollback. Do not treat demo success as production assurance |
| David Yanacek / Bill Fine, AWS re:Invent 2025 COP362 | Official video published 2025-12-05. The speaker says it includes a recorded demo | Distinguish the internal multi-agent from the user-side execution permissions. The 2026-05-27 technical article supplements parallel hypotheses and refutation |
| Afrina M / Mir Islam / Cedric Yao, Google Cloud Next ’26 BRK2-013 | Official video published 2026-07-07, checked through the description, captions not checked | Covers PayPal's observability, multi-agent, and governance. Specific IAM and approval settings are not treated as confirmed |

[HolmesGPT slides](https://hosted-files.sched.co/kccnceu2026/9f/holmesgpt%20auto%20remediation.pdf), [AWS official video](https://www.youtube.com/watch?v=JajBEYle67I), [AWS technical article](https://aws.amazon.com/blogs/devops/how-aws-devops-agent-uses-multi-agent-reasoning-to-find-root-causes/), [Google official video](https://www.youtube.com/watch?v=8tB01DYGMAs).

## 6 Configuration chosen from the survey

1. **Shared evidence plus single diagnosis**: pass one snapshot to an existing AI through Cloud-OpsBench's existing MCP. No new cloud. HolmesGPT file-only is the alternative.
2. **Compare first, then collaborate**: evaluate another AI independently on the same evidence and total budget. Only after that, try investigation plus evidence checking. Do not substitute a majority vote for correctness or approval.
3. **Add cloud-native as needed**: choose AWS DevOps / Azure SRE by permissions, cost, and target. GCP's eligibility is unclear, so do not make it a prerequisite.
4. **Changes go through a separate path**: separate human approval, scoped execution, independent recovery observation, and cleanup from the diagnostic agent. Do not build a new platform if existing workflows can do it.

This configuration is a proposal from the literature and implementation cases. There is no measurement yet that confirms adoption. Whether multiple AIs beat a single one, and whether a managed product is needed, will be decided by the next small tests.

## 7 Unconfirmed items

For the actual adoption and staged tests, see the [architecture and validation plan](architecture-and-validation-plan.md).

- Available local models, device performance, required isolation settings, and existing installations
- Per-service contracts, trial eligibility, regions, SKUs, billing currency, and cost caps for the target environment
- Azure's current currency unit prices and Robusta Platform's specific free tier and quotes
- Real-environment connection, diagnostic quality, prevention of wrong operations, recovery, and cleanup for each candidate

These are not filled in by guesswork. Distinguish between a product existing or an official path being confirmed, being usable in the target environment, and having succeeded in measurement.

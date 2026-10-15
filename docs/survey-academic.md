# SRE Agent / AIOps Academic Survey

**English** | [日本語](survey-academic.ja.md) · [Overview](../README.md)

Research date: 2026-10-11. Scope: selecting research for staged SRE validation on AWS, Azure, and GCP using existing AI tools.

## Conclusion

What to compare first is not "which model is strongest" but how to align diagnostic data, tools, role split, change authority, and success criteria.

- **Read-centered comparison**: Cloud-OpsBench, OpenRCA. Easy to compare existing agents on the same evidence and budget.
- **Repair comparison in live environments**: AIOpsLab, ITBench, SREGym. Score the diagnostic text and the actual recovery separately.
- **Off-the-shelf research agent candidates**: STRATUS, each benchmark's reference agent, and existing general-purpose coding agents. There is no need to develop a custom framework from the start.
- **Must-read on safety**: STRATUS's assumptions about reversible operations, AIOpsDoom's telemetry attack, and the 2026 paper analyzing failure processes. A human approval screen alone is not enough.
- **Extrapolation to multi-cloud is unverified**: success on Kubernetes does not prove the ability to handle AWS/Azure/GCP-specific IAM, billing, management APIs, and managed databases.

The "implications" and "recommendations" below are this survey's judgments, not a claim that the papers guarantee commercial production operation. No software, clusters, fault injection, or billing APIs were run this time.

## 1. An evaluation map for reading apart

| Kind of evaluation | Main papers / assets | What it can confirm | What it cannot confirm alone |
|---|---|---|---|
| Offline diagnosis of incident records and telemetry | OpenRCA, RCAgent, RCACopilot | Evidence extraction, root-cause candidates, explanation, analysis code | Recovery after a change, side effects of operations |
| Interaction with a fixed snapshot | Cloud-OpsBench | Compares tool choice and evidence gathering under fixed conditions | Dynamic environment changes, real repair |
| Fault injection into live environments | AIOpsLab, ITBench | The read-operate-recover loop | Generalization to all clouds and all failures |
| Execution environments with noise and compound failures | SREGym | Handling of misleading signals, low-layer failures, recurring failures | All operational constraints of real companies |
| Comparing agent structures | mABC, STRATUS, LATS-RCA, RCLAgent | Effects of role split, search, and recovery mechanisms | Quality assurance from agent count alone |
| Verifying safety and failure processes | AI Oops, Why Do AI Agents…, Between Promise and Pain | Misinterpretation, information loss, attacks and side effects | A guarantee against all unknown attacks and side effects |

Success rates differ across studies in tasks, model generation, data, tools, time limits, and scoring. Do not make a side-by-side ranking.

## 2. Core papers

### 2.1 AIOpsLab: a platform for testing the failure lifecycle

**Chen et al., AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds**

- Published: 2025-01-12. MLSys 2025. The predecessor design paper is 2024-07-16.
- Method: integrates application deployment, load generation, fault injection, telemetry, and agent evaluation through an Agent-Cloud Interface.
- Evaluation: DeathStarBench HotelReservation / SocialNetwork, 48 problems. Separates detection, localization, root-cause analysis, and mitigation.
- Limitations: a small set of known applications and faults. Do not read per-task success as the success rate of continuous production response.
- Implication: suited as a test bed for comparing tool connections of existing AI teams. Add cloud-specific failures separately.

Primary sources: [paper](https://arxiv.org/abs/2501.06706), [MLSys version](https://proceedings.mlsys.org/paper_files/paper/2025/file/d1f9e4a9f109b6e8b75ed362736f22ec-Paper-Conference.pdf), [official implementation](https://github.com/microsoft/AIOpsLab), [predecessor paper](https://arxiv.org/abs/2407.12165).

### 2.2 ITBench: evaluating SRE, security, and cost separately

**Jha et al., ITBench: Evaluating AI Agents across Diverse Real-World IT Automation Tasks**

- Published: 2025-02-07. ICML 2025.
- Method: practice-derived scenarios on Kubernetes, reference agents, scoring of diagnosis and mitigation.
- Evaluation: the initial 94 scenarios total SRE, CISO, and FinOps. The SRE experiment in the text uses 42 scenarios. GPT-4o's diagnosis pass@1 is 13.81% and mitigation 11.43%.
- Limitations: the publicly released subset at the time of the paper differs from the full evaluation set. Do not call the abstract's 13.8% a repair success rate. Also distinguish it from the current repository and ITBench-AA results.
- Implication: usable as a baseline for comparing against off-the-shelf SRE agents. Record success, wrong changes, time, and cost separately.

Primary sources: [paper, Table 4 / Appendix C](https://arxiv.org/html/2502.05352v1), [IBM publication info](https://research.ibm.com/publications/itbench-evaluating-ai-agents-across-diverse-real-world-it-automation-tasks), [official implementation](https://github.com/itbench-hub/ITBench).

### 2.3 OpenRCA: analysis ability over large telemetry

**Xu et al., OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?**

- Published: ICLR 2025 paper. The official project's acceptance notice is 2025-01-23. The exact date of first posting was not confirmed this time.
- Method: for natural-language tasks, analyzes logs, metrics, and traces with Python and similar. Provides the reference implementation RCA-agent.
- Evaluation: 3 systems, 335 failures, over 68 GB of telemetry. Even the best model at the time of the paper, Claude 3.5, fully resolves only 11.34%.
- Limitations: offline tasks of identifying cause, time, and so on. Not a live-repair benchmark.
- Implication: makes it easy to check, with several existing AI tools, the handoff between an analysis role and a code-execution role. Fixing the analysis environment and input conditions matters more than the model name.

Primary sources: [ICLR paper page](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d29b8d53678015079e1d245c023e49d2-Abstract-Conference.html), [official implementation](https://github.com/microsoft/OpenRCA), [official project](https://microsoft.github.io/OpenRCA/).

### 2.4 Cloud-OpsBench: separating correctness from evidence sufficiency

**Wang et al., Cloud-OpsBench: A Reproducible Benchmark for Agentic Root Cause Analysis in Cloud Systems**

- First version: 2026-02-28. Reference version: v2, 2026-08-22. Preprint.
- Method: confirms failures on real clusters and turns them into snapshots. Replays identical responses to diagnostic tools and also scores how far the evidence reached.
- Evaluation: Online Boutique / Train-Ticket, 57 fault types, 754 cases. The best Joint RCA Accuracy is 0.76 / 0.68, but the corresponding Evidence Closure Rate is 0.38 / 0.15.
- Limitations: supports only the finite set of recorded queries. Does not evaluate state changes or live repair.
- Implication: the first candidate for this project. By giving different off-the-shelf AIs the same evidence, you can catch answers that merely name the cause.

Primary sources: [paper v2](https://arxiv.org/html/2603.00468v2), [publication history](https://arxiv.org/abs/2603.00468), [official implementation and artifacts](https://github.com/LLM4Ops/Cloud-OpsBench).

### 2.5 SREGym: complex failures and comparing general-purpose agents

**Clark et al., SREGym: A Live Benchmark for AI SRE Agents with High-Fidelity Failure Scenarios**

- First version: 2026-05-08. Reference version: v3, 2026-07-30. Preprint.
- Method: configures failures at different layers, unrelated noise, correlated failures, and metastable failures in a real cloud-native environment.
- Evaluation: 90 problems. Compares STRATUS with Claude Code, Codex, and others, verifying diagnosis and actual mitigation.
- Limitations: an LLM judge is also used on the diagnosis side. You must separate the influence of the grading model from verification of real state.
- Implication: easy to evaluate a whole existing AI team. Start with the Lite version, then compound failures. Do not equate the paper's full 90 problems with the current code; pin the version.

Primary sources: [paper v3](https://arxiv.org/html/2605.07161v3), [publication history](https://arxiv.org/abs/2605.07161), [official implementation](https://github.com/SREGym/SREGym).

### 2.6 STRATUS: a research agent with role separation and Undo

**Chen et al., STRATUS: A Multi-agent System for Autonomous Reliability Engineering of Modern Clouds**

- First version: 2025-05-27. NeurIPS 2025. Reference version: 2026-03-19, v2.
- Method: controls detection, diagnosis, mitigation, and Undo with a state machine. Formalizes Transactional Non-Regression (TNR).
- Evaluation: compares mitigation success on AIOpsLab / ITBench. Reports improvement over existing methods.
- Limitations: TNR assumes exclusive writes, exact Undo, and an upper bound on operation-sequence length. What is guaranteed is the state at transaction boundaries, and temporary worsening in between is allowed. It does not prove that arbitrary external APIs can be unconditionally restored.
- Implication: a strong candidate to try before building your own. In multi-AI, restrict concurrent writes and treat operations that cannot be undone separately.

Primary sources: [paper v2, §3–4](https://arxiv.org/html/2506.02009v2), [NeurIPS version](https://papers.nips.cc/paper_files/paper/2025/file/47a6e9e2c3019f13ad94a0f259fe4970-Paper-Conference.pdf), [official implementation](https://github.com/xlab-uiuc/stratus).

### 2.7 RCAgent: internal models, tools, and context management

**Wang et al., RCAgent: Cloud Root Cause Analysis by Autonomous Agents with Tool-Augmented Large Language Models**

- First version: 2023-10-25. Reference version: 2024-08-02, v3. Accepted at CIKM 2024.
- Method: internally deployed models, information-gathering and analysis tools, reference keys for observations, and self-consistency aggregation of action trajectories.
- Evaluation: diagnosis and problem discovery on Alibaba Cloud's Flink platform. Evaluates cause, proposed solution, evidence, and area of responsibility, and reports outperforming ReAct.
- Limitations: depends heavily on industry-specific tools and non-public data. The quality of the proposed solutions and the safety of automatic execution are separate matters.
- Implication: a reference for designs that make use of local/internal models. Rather than repeatedly passing full-text logs to multiple agents, share evidence identifiers and the needed excerpts.

Primary sources: [paper v3](https://arxiv.org/html/2310.16340v3), [bibliography and history](https://arxiv.org/abs/2310.16340).

### 2.8 mABC: specialist roles and voting

**Zhang et al., mABC: Multi-Agent Blockchain-inspired Collaboration for Root Cause Analysis in Micro-Services Architecture**

- First version: 2024-04-18. Findings of EMNLP 2024, 2024-11.
- Method: seven specialist agents, an Agent Workflow that fixes the process, and blockchain-inspired voting. Limits endless search caused by circular dependencies.
- Evaluation: data from the AIOps challenge and Train-Ticket. Also runs ablations on components.
- Limitations: voting is not equivalent to independent external verification. Agents that share the same wrong evidence may agree and be wrong.
- Implication: a candidate for comparing role splits. Measure with matched vote counts, token cost, and the difference from a single agent.

Primary sources: [ACL paper and software](https://aclanthology.org/2024.findings-emnlp.232/), [full text](https://arxiv.org/html/2404.12135), [authors' code](https://github.com/zwpride/mABC).

### 2.9 LATS-RCA: tree search over hypotheses and the gap to production

**Naakka, Wang, Mäntylä, LATS-RCA: Language Agent Tree Search for Root Cause Analysis in Microservices**

- First version: 2026-05-05. Reference version: 2026-06-12, v2. Accepted at SEAA 2026.
- Method: multiple agents inspect logs and metrics and search a tree of root-cause hypotheses with reflective evaluation.
- Evaluation: 91.3% on public LO2. In a production case at Zoner Oy, the multi-trial average is 65.1%.
- Limitations: a gap between the simple public setup and production's multiple factors and missing observations. Not a success rate across products.
- Implication: use multi-AI to widen the range of hypotheses. Limit search depth, time, and cost, and make it possible to hold when evidence is insufficient.

Primary sources: [paper v2](https://arxiv.org/html/2605.03505v2), [publication date and acceptance info](https://arxiv.org/abs/2605.03505), [reproduction package](https://github.com/kottinov/lats-rca).

### 2.10 RCLAgent: parallel diagnosis following trace structure

**Zhang et al., Towards In-Depth Root Cause Localization for Microservices with Multi-Agent Recursion-of-Thought**

- Published: 2026-05-14. Preprint. A related 2025 version was published 2025-08-28.
- Method: assigns a dedicated agent to each trace span, diagnoses recursively and in parallel, and synthesizes a global evidence graph.
- Evaluation: compares localization accuracy and inference efficiency on AIOPS 2022, Augmented-TrainTicket, and RCAEval.
- Limitations: the subject is cause localization. These results cannot judge the effectiveness of independent change authority, approval, or rollback.
- Implication: consider divisions of labor that follow real service dependencies, not only a fixed AWS-owner / Azure-owner split. Keep the diagnostic structure separate from the execution-permission structure.

Primary sources: [2026 paper full text](https://arxiv.org/html/2605.14866v1), [related 2025 paper](https://arxiv.org/abs/2508.20370), [code listed in the paper](https://github.com/LLM4AIOps/RCLAgent-V2).

### 2.11 Between Promise and Pain: turning failures into design material

**Cornacchia et al., Between Promise and Pain: The Reality of Automating Failure Analysis in Microservices with LLMs**

- Published: APSys 2025, 2025-10 (conference 2025-10-12 to 13).
- Method: compares ReAct alone with AutoGen's reasoner / executor / critic, and tests the effect of specialized tools.
- Evaluation: SocialNetwork / HotelReservation extended from AIOpsLab, including performance faults and healthy states.
- Limitations and findings: observed false detections, overconfidence, repetition of wrong APIs, and unnecessary changes. The effect of going multi-agent depends on conditions.
- Implication: make "no failure" and "already recovered naturally" required negative cases. Measure whether the agent can stop, correct itself, and hand off to a human on failure.

Primary sources: [authors' public PDF](https://mcanini.github.io/papers/kashef2.apsys25.pdf), [DOI](https://doi.org/10.1145/3725783.3764388).

### 2.12 Why Do AI Agents Systematically Fail…: the effect of handoff quality

**Kim et al., Why Do AI Agents Systematically Fail at Cloud Root Cause Analysis?**

- First version: 2026-02-10. Reference version: 2026-03-04, v2. Preprint.
- Method and evaluation: analyzes 1,675 runs of 5 models on OpenRCA. Classifies 12 failure types across reasoning, inter-agent communication, and environment operation.
- Findings: misinterpreting data and insufficient exploration are common. Improving communication to share generated code, execution results, and exceptions reduced communication-related failures by up to 15 points.
- Limitations: the improvement experiments center on the Bank subset. It does not guarantee the same effect for every agent structure.
- Implication: do not pass only summaries between roles; attach execution results and evidence references. Also include independent verifiers and memory limits as comparison targets.

Primary sources: [paper v2](https://arxiv.org/html/2602.09937v2), [publication history](https://arxiv.org/abs/2602.09937).

### 2.13 OpenRCA 2.0: scoring causal paths

**Fang et al., OpenRCA 2.0: From Outcome Labels to Causal Process Supervision**

- First version: 2026-06-25. Reference version: 2026-06-30, v2. Marked as work in progress.
- Method: attaches causal propagation paths using PAVE, which forward-verifies impact from known fault injections.
- Evaluation: 3 application systems, 500 cases, 11 models. Exact match of the root-cause set averages 20.7%, very different from evaluations that credit naming some causes.
- Limitations: data selected from synthetic faults. The paper's appendix says release is planned after acceptance, while the project site already has 2.0 results. Confirming how the full data and versions correspond is a precondition before reproduction.
- Implication: useful for designs that require an evidence-backed explanation of cause → intermediate anomaly → user symptom, not just the cause name.

Primary sources: [paper v2, Appendix A](https://arxiv.org/html/2606.27154v2), [publication history](https://arxiv.org/abs/2606.27154), [project site](https://microsoft.github.io/OpenRCA/).

### 2.14 When AIOps Become "AI Oops": observed data is also outside the trust boundary

**Pasquini et al., When AIOps Become "AI Oops": Subverting LLM-driven IT Operations via Telemetry Manipulation**

- First version: 2025-08-08. USENIX Security 2026, 2026-08.
- Method: evaluates telemetry-derived steering with AIOpsDoom, and proposes AIOpsShield, which sanitizes input by exploiting its structure.
- Evaluation: an isolated AIOpsLab environment, ReAct / Flash, GPT-4o / GPT-4.1, and others. Shows the agent can be steered toward plausible but wrong repair proposals.
- Limitations: the defense's experimental results hold within the evaluation conditions. It is not a guarantee of blocking all unknown attacks.
- Implication: do not treat externally derived strings in logs and traces as operating instructions. Check proposals against read evidence, and do permission checks outside the LLM. Human-facing summaries also need references to evidence.

Primary sources: [USENIX conference page](https://www.usenix.org/conference/usenixsecurity26/presentation/pasquini), [final PDF](https://www.usenix.org/system/files/usenixsecurity26-pasquini.pdf), [first-version history](https://arxiv.org/abs/2508.06394), [authors' implementation](https://github.com/RSAC-Labs/AIOpsDoom).

### 2.15 Declarative multi-agent: measuring value even when read-only

**Adatiya & Kariya, A Declarative Multi-Agent Framework for Reducing On-Call Operational Burden**

- Published: listed by Google Research in 2026. The exact month and day and the peer-reviewed venue could not be confirmed from the listing.
- Method: manager/worker agents execute investigation procedures written by experts. The tool layer validates the procedures, combining read-only access, audit records, and RAG.
- Evaluation: multiple services and regions in a single organization. Reports cutting median high-severity triage from about 30 minutes to under 5.
- Limitations: no controlled user experiment. Sample size and public reproduction materials are not sufficiently shown, so avoid strong generalization. Repair is left to humans.
- Implication: a reference for the comparison plan that starts initial production connections as diagnostic support. Treat it as a design example, and do not turn its effect size into a target value.

Primary sources: [Google Research listing](https://research.google/pubs/a-declarative-multi-agent-framework-for-reducing-on-call-operational-burden/), [authors' PDF](https://storage.googleapis.com/gweb-research2023-media/pubtools/1046157.pdf).

## 3. Historically important supporting material

### RCACopilot

Chen et al., **Automatic Root Cause Analysis via Large Language Models for Cloud Incidents**. First version 2023-05-25, EuroSys 2024 published 2024-04-22. Gathers information with existing per-alert handlers and estimates the cause category using similar incidents. Reports up to 0.766 on a year of Microsoft incidents. Making use of existing operational knowledge is important, but the data is non-public and organization-specific, and that value does not apply to arbitrary clouds. Distinguish "the information-collection part has run for over four years" from "the whole LLM has done production repair for over four years." [Paper](https://arxiv.org/abs/2305.15778), [authors' PDF](https://tianyin.github.io/pub/rca-copilot.pdf), [university publication record](https://experts.illinois.edu/en/publications/automatic-root-cause-analysis-via-large-language-models-for-cloud/).

### Early large-scale recommendation of causes and mitigations

Ahmed et al., **Recommending Root-Cause and Mitigation Steps for Cloud Incidents using Large Language Models**. First version 2023-01-10, ICSE 2023. On over 40,000 Microsoft incidents, compares zero-shot / fine-tuning / multi-task and also had on-call owners evaluate. A way in to understanding the difference between the usefulness of recommended text and the ability to safely repair real systems. [Paper](https://arxiv.org/abs/2301.03797), [Microsoft research introduction](https://www.microsoft.com/en-us/research/blog/large-language-models-for-automatic-cloud-incident-management/).

## 4. Reproducibility and choosing off-the-shelf assets

The following is based on official READMEs checked on 2026-10-11. Repositories change, so at execution time pin the commit, dependency lockfile, and container digest. That something is public is separate from it being safe to run as is.

| Asset | Conditions confirmed | Treatment in this project |
|---|---|---|
| [Cloud-OpsBench](https://github.com/LLM4Ops/Cloud-OpsBench) | 754-case snapshots, reference agent, process labels. No live Kubernetes needed. Streamable HTTP MCP, with Codex / OpenCode connection examples | First read-only comparison candidate. Connection and scoring not yet confirmed to work |
| [OpenRCA](https://github.com/microsoft/OpenRCA) | Python 3.10 or later. Officially recommended RAM 32 GB, 80 GB free. Data distributed separately. Timestamps in UTC+8 | After checking device capacity. Remove the answer files from the agent's readable range |
| [AIOpsLab](https://github.com/microsoft/AIOpsLab/blob/main/README.md) | Python 3.11 or later, Helm, Poetry/pip. kind or remote K8s. Deployment steps for Azure VMs | Separate the control client from the Linux execution surface. OS compatibility unverified |
| [SREGym](https://github.com/SREGym/SREGym) | Python 3.12 or later, Docker, Helm 4 or later, kubectl, uv. Lite is 17 problems, about 8 vCPU / 16 GB on kind | Candidate for an early live environment. All problems need SSH/root on Linux nodes. Managed K8s as is does not work |
| [STRATUS](https://github.com/xlab-uiuc/stratus/blob/main/README.md) | Python 3.12, CrewAI, K8s, model connection. Procedures with AIOpsLab / ITBench | Research reference implementation. Check consistency before adoption, including the README's old names and submodule references |
| [ITBench](https://github.com/itbench-hub/ITBench) | Distinguishes self-hosted assets from hosted evaluation. Not all 94 cases in the paper are in the initial public code | Start with the local public subset. Decide separately on registration and sending results |
| [ITBench old SRE Agent](https://github.com/itbench-hub/ITBench-SRE-Agent) | Archived, with guidance to migrate to the unified agent | Do not pin the old name. Check the migration target and the matching scenario version |

SREGym's node-permission requirement is a big difference. Normal managed environments including the EKS / AKS / GKE management plane and self-managed Kubernetes on cloud VMs should be separate experiment lanes. When trying OS-level faults, give root only to dedicated validation VMs/clusters.

Cloud-OpsBench's replay material does not require building a full cluster first, which suits comparing existing AIs from a local environment. Whether to run on Linux / WSL2 / a VM is decided after checking device resources and the target assets' dependencies. These are recommended configurations, not results of verification on a particular device.

## 5. Bringing this into multi-AI, multi-cloud validation

### 5.1 Minimal comparison before deciding the design

Below is a general experiment plan for separating the effects of structure. For the concrete order for this round, prefer the [architecture and validation plan](architecture-and-validation-plan.md), and judge necessity in the order: confirm connection of a single existing AI, independent comparison with another AI, then adding roles to the same model. There is no need to run all combinations from the start.

1. Measure a single configuration with **the same existing AI, same model, same tools**.
2. Add "investigator + evidence checker" under the same conditions.
3. Measure the existing reference agent with the same time limit and model budget.
4. For only the structures that showed an effect, swap in a different model / provider.
5. For those that pass read-only, try approved repair on a validation cluster.

Treat using multiple models, using multiple agents, and operating multiple clouds as separate variables. Changing everything at once leaves no way to explain the cause of success or failure.

### 5.2 Metrics to record

| Axis | What to record |
|---|---|
| Diagnosis | Root-cause component, failure mechanism, impact scope, time, match of multi-cause sets |
| Evidence | The data ID, query, and time each claim references. Search for counter-evidence, unconfirmed items, wrong citations |
| Repair | Actual SLO recovery, config diffs, sustained recovery, worsening of other services, recurrence |
| Safety | Requests / executions of forbidden operations, unapproved operations, mix-ups of cloud/account, permission overreach |
| Restoration | Whether rollback completed, match with the original state, size and duration of mid-course worsening |
| Operational burden | Human review time, approval wait, rework, duplicated investigation, quality of escalation |
| Cost | Model input/output, tool calls, retries, cloud resource cost, total elapsed time |
| Reproducibility | Variance across trials, model version, judge version, noise seed, differences in initial state |

Do not make any one of "the alert disappeared," "the LLM judge said it was correct," or "the agent reported completion" the sole success condition. Also exclude from success any behavior that gets around evaluation by accessing the benchmark infrastructure or ground-truth data.

### 5.3 Required failure and safety scenarios

- No failure, a stale alert, already recovered naturally
- Insufficient logs, missing traces, clock skew, contradictory observations
- Multiple alerts from the same cause, and unrelated simultaneous failures
- Cases where the first plausible anomaly found is not the cause
- Cases where another SLO worsens after a change
- Cases where state changes while awaiting approval and the proposal goes stale
- Conflicting changes to the same cluster by two AIs
- Mix-ups of account / subscription / project / region / namespace
- Cases where external strings in telemetry push toward approval or change
- Tool errors, partial success, API timeouts, retries of the same operation

Attack resistance is first confirmed with read-only tests on safe synthetic data. Attacks on public systems, fault injection in third parties' environments, and running attack code are not part of this plan's early stages.

### 5.4 Proposed approval and safety boundaries

The following are operating proposals for this project, not research claims.

- Run the investigation agent under a read-only identity. Do not give the diagnostic text execution authority.
- Output change candidates as proposals carrying target, evidence, diff, impact scope, restoration steps, verification conditions, and expiry.
- Pass to the execution layer only approved operations and targets. Reconfirm if the diff changes after approval.
- Make changes exclusive per resource. Even with multiple AI owners, do not run writes to the same resource at the same time.
- Classify rollback feasibility per operation. Do not assume that external sending, billing, credentials, or destructive data operations are "Undo-able."
- Judge recovery by independent state verification. Do not let the original proposer grade itself.
- Do not make stops, time and cost caps, or audit records depend on the model's prompt alone.

### 5.5 Additional tests needed across clouds

In addition to the shared Kubernetes tests in the literature, evaluate in separate tables each cloud's own ID and permission model, API latency / partial failure, quotas, managed services, network boundaries, and audit logs. Do not assume features with similar names on the three clouds are equivalent.

At first, reproduce the same failure of the same app one cloud at a time and convert tool return values to a shared evidence format. Then add "dependencies between clouds." Consider simultaneous automatic repair across all three clouds only after approval, restoration, and auditing work on a single cloud.

## 6. Points left unsettled in this survey

- For the support scope, pricing, and general availability of current commercial SRE products, see the [products, practitioner talks, and implementation survey](survey-products-and-practice.md).
- Native Windows compatibility, end-to-end runs, and API cost of public research implementations are unmeasured.
- The full correspondence between the OpenRCA 2.0 paper version and the distributed data is unverified. Do not make it a required dependency for early adoption.
- Some papers' production data and internal tools are non-public and cannot be fully reproduced.
- Numbers at the time of a paper are results of the configuration then. Do not reinterpret them as results of other 2026 models or the current README.
- Gains in accuracy or time are not legal responsibility, SLAs, security certification, or a safety guarantee for commercial production.

## Recommended reading order

1. AIOpsLab, ITBench: what is being evaluated
2. Cloud-OpsBench, OpenRCA: how to compare on the same evidence
3. STRATUS: the boundary between change and restoration
4. AI Oops, Why Do AI Agents…: how it breaks and defenses
5. SREGym: extension to realistic complexity
6. mABC, LATS-RCA, RCLAgent: design options when the existing configuration is not enough

This order lets you build on the broad survey while avoiding building a huge multi-agent platform of your own first.

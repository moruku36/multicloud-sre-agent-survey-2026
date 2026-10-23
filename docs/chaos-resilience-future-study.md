[日本語](chaos-resilience-future-study.ja.md) | **English**

# Future study: Fault injection and recovery verification

**Status: documented proposal; no implementation or experiment.** No cloud connection, fault injection, permission change or recovery action has been performed.

The [publisher PDF for Adaptive Ephemeral Chaos Infrastructure for Resilience Validation in AWS Multi-Account Environments](https://ijetcsit.org/index.php/ijetcsit/article/view/654/593) was checked by a separate research contributor. It describes seven experiment phases, recovery checks, collision detection and coordination across AWS accounts. Its design uses a 15-minute prior baseline, values within two standard deviations for three consecutive minutes, and an UNRESOLVED/SNS/stop decision after 15 minutes without convergence. These are design parameters, not universal safety guarantees. Section 8 proposes future evaluation and supplies no measured results or demonstrated real-world effect. Code and reproducibility remain unverified. See the companion survey in the research repository. Multiple AWS accounts are distinct from multiple cloud providers; experiment control is distinct from autonomous LLM diagnosis.

The existing [architecture and validation plan](architecture-and-validation-plan.md) separates diagnosis from execution. Preserve that boundary while recording **fault injection ended** and **service recovered** as different states.

## Proposed design and checks

1. Separate a cloud-neutral experiment state model from provider-specific fault-injection adapters. Porting beyond AWS would require additional design and evaluation.
2. Start agents with plans and result summaries. Consider execution only for isolated, approved targets with explicit authorization, stop conditions and an identified rollback owner.
3. Do not infer recovery from one successful API call. Observe user-facing SLIs, dependencies, configuration differences and residual resources over time; missing data is not healthy data.
4. First test collisions, partial failures, missing observations and timeouts using simulated event streams. Later comparison dimensions would include false recovery declarations, recovery time, residual resources, collision prevention and cost.
5. Review the full-text design and check reproducible configuration and measured logs before an implementation decision. Do not list the paper's future concepts or this proposal as implemented features.

The free initial check is a tabletop test of transitions, interruption and recovery decisions. Cloud fault injection is outside the scope of this documentation.

[README](../README.md) | [Architecture and validation plan](architecture-and-validation-plan.md)

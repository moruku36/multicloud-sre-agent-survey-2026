"""Deterministic diagnosis and a synthetic-only execution boundary."""
from __future__ import annotations

from datetime import datetime, timedelta

from .model import Approval, Diagnosis, Observation, Plan, Result, utc


class PolicyDenied(RuntimeError):
    pass


MAX_OBSERVATION_AGE = timedelta(minutes=5)  # Synthetic demo policy, not a production SLO.
MAX_VERIFICATION_GAP = timedelta(seconds=75)


def _fresh(observation: Observation, now: datetime) -> bool:
    age = utc(now) - utc(observation.observed_at)
    return timedelta(0) <= age <= MAX_OBSERVATION_AGE


def diagnose(observation: Observation) -> Diagnosis:
    if observation.value is None:
        return Diagnosis("INCONCLUSIVE", "Metric unavailable; cause and health unconfirmed",
                         (observation.evidence_id,), observation.gaps)
    if observation.value < observation.target.minimum:
        return Diagnosis("FAIL", "Observed metric is below its configured minimum; cause unconfirmed",
                         (observation.evidence_id,), ("root cause", "user impact"))
    return Diagnosis("PASS", "Observed metric meets its configured minimum; wider health unconfirmed",
                     (observation.evidence_id,), ("other resources", "user impact"))


def propose(observation: Observation, now: datetime) -> Plan | None:
    if (not _fresh(observation, now) or observation.value is None
            or observation.value >= observation.target.minimum):
        return None
    return Plan(observation.target, "simulate_restore_capacity",
                observation.evidence_id, utc(now) + timedelta(minutes=5))


class SimulationState:
    """Synthetic state only. No SDK reference or cloud write operation exists here."""

    def __init__(self, observation: Observation):
        self.observation = observation
        self.writes = 0

    def read(self) -> Observation:
        return self.observation

    def set_capacity(self, value: float, now: datetime) -> None:
        self.observation = Observation(self.observation.target, utc(now), value,
                                       "synthetic state after simulated action",
                                       run_id=self.observation.run_id)
        self.writes += 1


class SimulationExecutor:
    def __init__(self, allowed: set[tuple[str, str, str]], max_actions: int,
                 max_cost_units: int, deadline: datetime):
        self.allowed = allowed
        self.max_actions = max_actions
        self.max_cost_units = max_cost_units
        self.deadline = utc(deadline)
        self.used_actions = 0
        self.used_cost_units = 0
        self.ledger: dict[str, Result] = {}
        self.busy: set[tuple[str, str, str]] = set()

    def execute(self, plan: Plan, approval: Approval | None,
                state: SimulationState, now: datetime, fail_after_change: bool = False) -> Result:
        now = utc(now)
        plan_digest = plan.plan_id
        key = (plan.target.cloud, plan.target.scope, plan.target.resource)
        if approval is None or (approval.plan_id, approval.scope, approval.resource,
                                approval.operation, utc(approval.expires_at)) != (plan_digest, plan.target.scope,
                                                        plan.target.resource, plan.operation,
                                                        utc(plan.expires_at)):
            raise PolicyDenied("exact human approval required")
        if not approval.approver or approval.approver == "agent":
            raise PolicyDenied("synthetic non-agent approver label required")
        if now >= self.deadline or now >= utc(plan.expires_at) or now >= utc(approval.expires_at):
            raise PolicyDenied("approval, plan or budget expired")
        if key not in self.allowed or plan.operation != "simulate_restore_capacity":
            raise PolicyDenied("target or operation not allowed")
        if plan_digest in self.ledger:
            return self.ledger[plan_digest]
        if self.used_actions >= self.max_actions or self.used_cost_units + plan.cost_units > self.max_cost_units:
            raise PolicyDenied("action or cost budget exhausted")
        if key in self.busy:
            raise PolicyDenied("resource already has a writer")
        current = state.read()
        if not _fresh(current, now):
            raise PolicyDenied("observation too old or in the future")
        if current.target != plan.target or current.evidence_id != plan.expected_evidence_id:
            raise PolicyDenied("state changed since diagnosis")
        if current.value is None or current.value >= current.target.minimum:
            raise PolicyDenied("change no longer indicated")
        self.busy.add(key)
        self.used_actions += 1
        self.used_cost_units += plan.cost_units
        try:
            state.set_capacity(plan.target.minimum, now + timedelta(seconds=1))
            if fail_after_change:
                result = Result("INCONCLUSIVE", "simulated response lost; reconcile before retry", plan.plan_id)
            else:
                result = Result("INCONCLUSIVE", "simulated action returned; independent verification pending",
                                plan.plan_id)
            self.ledger[plan.plan_id] = result
            return result
        finally:
            self.busy.remove(key)


def verify_recovery(before: Observation, after: list[Observation], as_of: datetime,
                    changed_at: datetime) -> Result:
    """Synthetic sampled-capacity check; it cannot prove continuous real recovery."""
    if len(after) != 6:
        return Result("INCONCLUSIVE", "exactly six synthetic observations required", "", ())
    first = utc(after[0].observed_at)
    previous = first
    for index, item in enumerate(after):
        stamp = utc(item.observed_at)
        if item.target != before.target or item.run_id != before.run_id:
            return Result("INCONCLUSIVE", "target or run mismatch", "")
        if item.value is None or item.value < before.target.minimum:
            return Result("FAIL", "coverage or capacity check failed", "",
                          tuple(o.evidence_id for o in after))
        if index and not timedelta(seconds=60) <= stamp - previous <= MAX_VERIFICATION_GAP:
            return Result("INCONCLUSIVE", "observation spacing is insufficient", "")
        previous = stamp
    if (utc(changed_at) <= utc(before.observed_at) or first <= utc(changed_at)
            or previous - first < timedelta(seconds=300)):
        return Result("INCONCLUSIVE", "300-second post-change window not observed", "")
    if not timedelta(0) <= utc(as_of) - previous <= MAX_VERIFICATION_GAP:
        return Result("INCONCLUSIVE", "verification observations are stale or future", "")
    return Result("PASS", "six recent synthetic samples met capacity threshold", "",
                  tuple(o.evidence_id for o in after))

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Literal


Cloud = Literal["aws", "azure", "gcp"]
Status = Literal["PASS", "FAIL", "INCONCLUSIVE", "NOT_RUN"]


def utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("observation time must include a timezone")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class Target:
    cloud: Cloud
    scope: str
    resource: str
    metric: str
    minimum: float

    def __post_init__(self) -> None:
        if self.cloud not in ("aws", "azure", "gcp"):
            raise ValueError("unsupported cloud")
        if not self.scope or not self.resource or not self.metric or self.minimum <= 0:
            raise ValueError("target requires explicit scope, resource, metric and positive minimum")
        if not math.isfinite(self.minimum):
            raise ValueError("minimum must be finite")


@dataclass(frozen=True)
class Observation:
    target: Target
    observed_at: datetime
    value: float | None
    source: str
    gaps: tuple[str, ...] = ()
    run_id: str = "synthetic-local-demo"

    def __post_init__(self) -> None:
        utc(self.observed_at)
        if not self.run_id:
            raise ValueError("run ID required")
        if self.value is None and not self.gaps:
            raise ValueError("missing value requires a gap")
        if self.value is not None and not math.isfinite(self.value):
            raise ValueError("metric value must be finite")

    @property
    def evidence_id(self) -> str:
        payload = [self.run_id, self.target.cloud, self.target.scope, self.target.resource,
                   self.target.metric, utc(self.observed_at).isoformat(), self.value,
                   self.source, self.gaps]
        return sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()[:16]


@dataclass(frozen=True)
class Diagnosis:
    status: Status
    summary: str
    evidence_ids: tuple[str, ...]
    uncertainty: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    plan_id: str
    target: Target
    operation: Literal["simulate_restore_capacity"]
    expected_evidence_id: str
    expires_at: datetime
    cost_units: int = 1


@dataclass(frozen=True)
class Approval:
    plan_id: str
    scope: str
    resource: str
    operation: str
    expires_at: datetime
    approver: str


@dataclass(frozen=True)
class Result:
    status: Status
    detail: str
    plan_id: str
    evidence_ids: tuple[str, ...] = ()

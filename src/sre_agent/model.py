from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Literal


Cloud = Literal["aws", "azure", "gcp"]
Status = Literal["PASS", "FAIL", "INCONCLUSIVE", "NOT_RUN"]


def digest(payload: dict) -> str:
    """Hash a complete, normalized approval/evidence payload."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return sha256(encoded).hexdigest()


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
    location: str = ""
    load_balancer: str = ""

    def __post_init__(self) -> None:
        if self.cloud not in ("aws", "azure", "gcp"):
            raise ValueError("unsupported cloud")
        if not self.scope or not self.resource or not self.metric or self.minimum <= 0:
            raise ValueError("target requires explicit scope, resource, metric and positive minimum")
        if not math.isfinite(self.minimum):
            raise ValueError("minimum must be finite")

    def binding_payload(self) -> dict:
        payload = asdict(self)
        payload["minimum"] = float(self.minimum)
        return payload


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
        return digest({"run_id": self.run_id, "target": self.target.binding_payload(),
                       "observed_at": utc(self.observed_at).isoformat(),
                       "value": None if self.value is None else float(self.value),
                       "source": self.source, "gaps": list(self.gaps)})


@dataclass(frozen=True)
class Diagnosis:
    status: Status
    summary: str
    evidence_ids: tuple[str, ...]
    uncertainty: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    target: Target
    operation: Literal["simulate_restore_capacity"]
    expected_evidence_id: str
    expires_at: datetime
    cost_units: int = 1

    def __post_init__(self) -> None:
        utc(self.expires_at)
        if not self.expected_evidence_id or self.cost_units <= 0:
            raise ValueError("plan requires evidence and positive cost")

    @property
    def plan_id(self) -> str:
        """Recomputed on every use; any changed execution field changes approval identity."""
        return digest({"target": self.target.binding_payload(),
                       "operation": self.operation,
                       "expected_evidence_id": self.expected_evidence_id,
                       "expires_at": utc(self.expires_at).isoformat(),
                       "cost_units": self.cost_units})


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

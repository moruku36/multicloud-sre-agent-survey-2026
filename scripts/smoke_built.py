"""Verify the packaged three-cloud path stops before synthetic execution."""
from datetime import datetime, timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
BUILT = ROOT / "build" / "lib"
FIXTURE = Path("sre_agent") / "fixtures" / "three_clouds.json"
SOURCE_NAMES = {
    "aws": "AWS CloudWatch GetMetricData",
    "azure": "Azure Monitor MetricsQueryClient.query_resource",
    "gcp": "Google Cloud Monitoring MetricServiceClient.list_time_series",
}


def digest(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return sha256(encoded).hexdigest()


def verify(report: list[dict], cases: list[dict]) -> None:
    if len(report) != len(cases) or {item["cloud"] for item in report} != {
            "aws", "azure", "gcp"}:
        raise AssertionError("one observation per cloud is required")
    for row, case in zip(report, cases):
        cloud = case["cloud"]
        stamp = datetime.fromisoformat(case["observed_at"])
        target = {"cloud": cloud, "scope": case["scope"],
                  "resource": case["resource"], "metric": case["metric"],
                  "minimum": float(case["minimum"]),
                  "location": case.get("location", ""),
                  "load_balancer": case.get("load_balancer", "")}
        evidence_id = digest({"run_id": "synthetic-local-demo", "target": target,
                              "observed_at": stamp.isoformat(),
                              "value": float(case["value"]),
                              "source": SOURCE_NAMES[cloud], "gaps": []})
        plan_id = digest({"target": target, "operation": "simulate_restore_capacity",
                          "expected_evidence_id": evidence_id,
                          "expires_at": (stamp + timedelta(seconds=302)).isoformat(),
                          "cost_units": 1})
        if not case["value"] < case["minimum"]:
            raise AssertionError(f"{cloud}: fixture must exercise a below-minimum signal")
        expected = {"cloud": cloud, "run_id": "synthetic-local-demo",
                    "scope": case["scope"], "resource": case["resource"],
                    "metric": case["metric"], "minimum": case["minimum"],
                    "location": target["location"], "load_balancer": target["load_balancer"],
                    "value": float(case["value"]), "observed_at": stamp.isoformat(),
                    "diagnosis": "FAIL", "evidence_id": evidence_id,
                    "uncertainty": ["root cause", "user impact"],
                    "proposal": plan_id, "execution": "NOT_RUN",
                    "execution_detail": "synthetic approval required before execution",
                    "verification": "NOT_RUN"}
        for field, value in expected.items():
            if row.get(field) != value:
                raise AssertionError(f"{cloud}: {field} did not match the fixture contract")
        if "cause unconfirmed" not in row["summary"]:
            raise AssertionError(f"{cloud}: diagnosis lost its uncertainty")


def main() -> None:
    packaged_fixture = BUILT / FIXTURE
    source_fixture = ROOT / "src" / FIXTURE
    if not packaged_fixture.is_file() or packaged_fixture.read_bytes() != source_fixture.read_bytes():
        raise SystemExit("built package lacks the current synthetic fixture")
    cases = json.loads(source_fixture.read_text(encoding="utf-8"))
    # Run outside the checkout. Any network attempt or synthetic state write fails.
    harness = """import json
from unittest.mock import patch
with (patch('socket.socket', side_effect=AssertionError('network attempted')),
      patch('socket.getaddrinfo', side_effect=AssertionError('DNS attempted'))):
    from sre_agent.cli import run_demo
    from sre_agent.engine import SimulationExecutor, SimulationState
    with patch.object(SimulationExecutor, 'execute', side_effect=AssertionError('execution attempted')):
        with patch.object(SimulationState, 'set_capacity', side_effect=AssertionError('state changed')):
            first = run_demo()
            if first != run_demo():
                raise AssertionError('demo is not deterministic')
print(json.dumps(first))
"""
    environment = {"PYTHONPATH": str(BUILT), "PYTHONNOUSERSITE": "1"}
    if os.name == "nt":
        environment["SystemRoot"] = os.environ.get("SystemRoot", r"C:\Windows")
    with TemporaryDirectory() as isolated:
        completed = subprocess.run([sys.executable, "-c", harness], cwd=isolated,
                                   env=environment, capture_output=True, text=True, check=True)
    report = json.loads(completed.stdout)
    verify(report, cases)
    for item in report:
        print(f"{item['cloud']}: {item['diagnosis']} -> proposal bound -> "
              f"execution {item['execution']}; verification {item['verification']}")
    print("packaged offline three-cloud end-to-end check: PASS")


if __name__ == "__main__":
    main()

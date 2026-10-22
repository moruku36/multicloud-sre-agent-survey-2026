"""Offline three-cloud demonstration. No SDK construction or network calls."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
from types import SimpleNamespace

from .adapters import AWSCloudWatch, AzureMonitor, GCPMonitoring
from .engine import SimulationExecutor, SimulationState, diagnose, propose, verify_recovery
from .model import Approval, Observation, Target


class FakeAWS:
    def __init__(self, value: float, stamp: datetime):
        self.value, self.stamp = value, stamp

    def get_metric_data(self, **kwargs):
        return {"MetricDataResults": [{"Id": "signal", "StatusCode": "Complete",
                                        "Timestamps": [self.stamp], "Values": [self.value]}]}


class FakeAzure:
    def __init__(self, value: float, stamp: datetime, metric: str):
        self.value, self.stamp, self.metric = value, stamp, metric

    def query_resource(self, *args, **kwargs):
        point = SimpleNamespace(time_stamp=self.stamp, average=self.value)
        metric = SimpleNamespace(name=self.metric, timeseries=[SimpleNamespace(data=[point])])
        return SimpleNamespace(metrics=[metric])


class FakeGCP:
    def __init__(self, value: float, stamp: datetime):
        self.value, self.stamp = value, stamp

    def list_time_series(self, *, request):
        point = SimpleNamespace(interval=SimpleNamespace(end_time=self.stamp),
                                value=SimpleNamespace(int64_value=self.value, double_value=0))
        group = request["filter"].split('instance_group_name = "')[1].split('"')[0]
        return [SimpleNamespace(points=[point],
                                resource=SimpleNamespace(labels={"instance_group_name": group}))]


def run_demo(simulate_approved: bool = False) -> list[dict]:
    fixture = Path(__file__).resolve().parents[2] / "fixtures" / "three_clouds.json"
    cases = json.loads(fixture.read_text(encoding="utf-8"))
    output = []
    for case in cases:
        target = Target(case["cloud"], case["scope"], case["resource"],
                        case["metric"], case["minimum"])
        stamp = datetime.fromisoformat(case["observed_at"])
        if target.cloud == "aws":
            adapter = AWSCloudWatch(FakeAWS(case["value"], stamp), target,
                                    case["namespace"], [{"Name": "TargetGroup",
                                                         "Value": target.resource.rsplit(":", 1)[-1]}])
        elif target.cloud == "azure":
            adapter = AzureMonitor(FakeAzure(case["value"], stamp, target.metric), target)
        else:
            adapter = GCPMonitoring(FakeGCP(case["value"], stamp), target)
        observation = adapter.collect(stamp + timedelta(seconds=1))
        diagnosis = diagnose(observation)
        plan = propose(observation, stamp + timedelta(seconds=2))
        item = {"cloud": target.cloud, "diagnosis": diagnosis.status,
                "run_id": observation.run_id, "scope": target.scope,
                "resource": target.resource, "metric": target.metric,
                "value": observation.value, "minimum": target.minimum,
                "observed_at": observation.observed_at.isoformat(),
                "summary": diagnosis.summary, "evidence_id": observation.evidence_id,
                "uncertainty": diagnosis.uncertainty, "proposal": plan.plan_id if plan else None,
                "execution": "NOT_RUN", "verification": "NOT_RUN"}
        if simulate_approved and plan:
            state = SimulationState(observation)
            executor = SimulationExecutor({(target.cloud, target.scope, target.resource)},
                                          max_actions=1, max_cost_units=1,
                                          deadline=stamp + timedelta(minutes=4))
            approval = Approval(plan.plan_id, target.scope, target.resource, plan.operation,
                                stamp + timedelta(minutes=3), "synthetic-human")
            outcome = executor.execute(plan, approval, state, stamp + timedelta(seconds=3))
            after = [Observation(target, stamp + timedelta(seconds=4 + n * 60),
                                 state.read().value, "independent synthetic probe",
                                 run_id=observation.run_id) for n in range(6)]
            verified = verify_recovery(observation, after)
            item["execution"] = outcome.status
            item["verification"] = verified.status
            item["verification_evidence_ids"] = verified.evidence_ids
        output.append(item)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="offline, synthetic SRE demonstration")
    parser.add_argument("demo", nargs="?", choices=["demo"], default="demo")
    parser.add_argument("--simulate-approved", action="store_true",
                        help="run a synthetic-only, explicitly approved state change")
    args = parser.parse_args()
    print(json.dumps(run_demo(args.simulate_approved), indent=2))


if __name__ == "__main__":
    main()

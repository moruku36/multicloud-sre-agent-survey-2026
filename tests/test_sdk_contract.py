"""Offline SDK-type contract checks for the three read adapters.

The adapters are normally exercised with hand-written fakes, which cannot reveal a
mismatch with the real SDK types. These tests feed the packaged synthetic fixture
through the adapters as objects built from the real public SDK model classes and
validate each request against the SDK's own request model or signature.

Nothing here creates a cloud client, session, credential or network connection.
Responses are constructed offline from SDK classes; they are not deserialized from
real service output, so field semantics and permissions stay unverified.

If an SDK is not installed the tests skip, unless SRE_REQUIRE_SDK_CONTRACT=1, in
which case a missing SDK is a failure (CI sets it; see requirements-sdk-contract.txt).
"""
import importlib
import inspect
import json
import os
import sys
import unittest
from datetime import datetime, timedelta
from importlib.resources import files
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sre_agent.adapters import AWSCloudWatch, AzureMonitor, GCPMonitoring
from sre_agent.cli import run_demo
from sre_agent.model import Target

REQUIRED = os.environ.get("SRE_REQUIRE_SDK_CONTRACT") == "1"


def _cases() -> dict:
    fixture = files("sre_agent").joinpath("fixtures").joinpath("three_clouds.json")
    return {case["cloud"]: case for case in json.loads(fixture.read_text(encoding="utf-8"))}


def _target(case: dict) -> Target:
    return Target(case["cloud"], case["scope"], case["resource"], case["metric"],
                  case["minimum"], case.get("location", ""), case.get("load_balancer", ""))


def _declared_keywords(function, kwargs: dict) -> list[str]:
    """Keyword names the real SDK signature does not declare (a **kwargs sink hides typos)."""
    parameters = inspect.signature(function).parameters
    return [name for name in kwargs
            if name not in parameters or parameters[name].kind is inspect.Parameter.VAR_KEYWORD]


class ContractBase(unittest.TestCase):
    cloud = ""
    modules: tuple[str, ...] = ()

    def sdk(self, name: str):
        try:
            return importlib.import_module(name)
        except ImportError as error:
            message = f"{name} is not installed ({error})"
            if REQUIRED:
                self.fail(message)
            self.skipTest(message)

    def case(self) -> tuple[dict, Target, datetime, datetime]:
        case = _cases()[self.cloud]
        stamp = datetime.fromisoformat(case["observed_at"])
        return case, _target(case), stamp, stamp + timedelta(seconds=1)  # now, as in the demo

    def assert_matches_demo(self, observation, case: dict, stamp: datetime) -> None:
        try:
            demo = next(item for item in run_demo() if item["cloud"] == self.cloud)
        except Exception as error:  # the demo runs all three clouds; name the real cause
            self.fail(f"fake-client demo failed ({type(error).__name__}: {error}); "
                      "the real-type comparison could not run")
        self.assertEqual(observation.value, case["value"])
        self.assertEqual(observation.observed_at, stamp)
        # Same evidence ID as the fake-client demo: real-typed and fake responses
        # normalize identically.
        self.assertEqual(observation.evidence_id, demo["evidence_id"])


class AWSContract(ContractBase):
    cloud = "aws"

    def test_request_and_response_match_botocore_cloudwatch_model(self):
        loaders = self.sdk("botocore.loaders")
        model_module = self.sdk("botocore.model")
        validate = self.sdk("botocore.validate").validate_parameters
        operation = model_module.ServiceModel(
            loaders.Loader().load_service_model("cloudwatch", "service-2")
        ).operation_model("GetMetricData")
        case, target, stamp, now = self.case()
        seen = []

        class Client:
            def get_metric_data(self, **kwargs):
                validate(kwargs, operation.input_shape)  # raises ParamValidationError
                # botocore does not check enum membership client-side.
                if kwargs["ScanBy"] not in operation.input_shape.members["ScanBy"].enum:
                    raise AssertionError("ScanBy is not a CloudWatch enum value")
                seen.append(kwargs)
                response = {"MetricDataResults": [{
                    "Id": "signal", "Label": target.metric, "Timestamps": [stamp],
                    "Values": [float(case["value"])], "StatusCode": "Complete"}]}
                validate(response, operation.output_shape)
                return response

        observation = AWSCloudWatch(Client(), target, case["namespace"]).collect(now)
        self.assertEqual(len(seen), 1)
        self.assert_matches_demo(observation, case, stamp)


class AzureContract(ContractBase):
    cloud = "azure"

    def test_request_and_response_match_azure_monitor_query_1x(self):
        query = self.sdk("azure.monitor.query")
        if not hasattr(query, "MetricsQueryClient"):
            message = ("azure-monitor-query has no MetricsQueryClient (2.x moved metrics to "
                       "azure-monitor-querymetrics); this adapter targets 1.x")
            if REQUIRED:
                self.fail(message)
            self.skipTest(message)
        case, target, stamp, now = self.case()
        seen = []

        class Client:
            def query_resource(self, resource_uri, metric_names, **kwargs):
                seen.append((resource_uri, metric_names, kwargs))
                undeclared = _declared_keywords(query.MetricsQueryClient.query_resource, kwargs)
                if undeclared:
                    raise AssertionError(f"not declared by the real signature: {undeclared}")
                point = query.MetricValue(timestamp=stamp, average=float(case["value"]))
                series = query.TimeSeriesElement(metadata_values={}, data=[point])
                metric = query.Metric(id="metric", type="Microsoft.Insights/metrics",
                                      name=target.metric, unit="Count", timeseries=[series],
                                      display_description="")
                return query.MetricsQueryResult(timespan="synthetic", metrics=[metric])

        observation = AzureMonitor(Client(), target).collect(now)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][2].get("aggregations"), ["Average"])  # adapter reads .average
        self.assert_matches_demo(observation, case, stamp)


class GCPContract(ContractBase):
    cloud = "gcp"

    def test_request_and_response_match_monitoring_v3_types(self):
        monitoring = self.sdk("google.cloud.monitoring_v3")
        resource_types = self.sdk("google.api.monitored_resource_pb2")
        case, target, stamp, now = self.case()
        seen = []

        class Client:
            def list_time_series(self, *, request):
                undeclared = _declared_keywords(monitoring.MetricServiceClient.list_time_series,
                                                {"request": request})
                if undeclared:
                    raise AssertionError(f"not declared by the real signature: {undeclared}")
                monitoring.ListTimeSeriesRequest(request)  # proto-plus rejects unknown fields/enums
                seen.append(request)
                labels = {"project_id": target.scope.split("/", 1)[1],
                          "location": target.location, "instance_group_name": target.resource}
                resource = resource_types.MonitoredResource(type="instance_group", labels=labels)
                point = monitoring.Point(
                    interval=monitoring.TimeInterval(end_time=stamp),
                    value=monitoring.TypedValue(int64_value=int(case["value"])))
                return iter([monitoring.TimeSeries(
                    metric={"type": target.metric}, resource=resource, points=[point])])

        observation = GCPMonitoring(Client(), target).collect(now)
        self.assertEqual(len(seen), 1)
        self.assert_matches_demo(observation, case, stamp)


if __name__ == "__main__":
    unittest.main()

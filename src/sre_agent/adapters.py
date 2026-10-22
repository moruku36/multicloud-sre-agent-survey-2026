"""Read-only SDK adapters. Clients are supplied explicitly by the caller.

No adapter constructs a credential, session or SDK client. Production callers must
perform a separate connection review before supplying one. Tests use fake clients.
"""
from __future__ import annotations

from datetime import datetime, timedelta
import re

from .model import Observation, Target, utc


class CollectionError(RuntimeError):
    pass


def _latest(points: list[tuple[datetime, float]], target: Target, source: str,
            now: datetime) -> Observation:
    if not points:
        return Observation(target, utc(now), None, source, ("no data points",))
    stamp, value = max(points, key=lambda point: utc(point[0]))
    age = utc(now) - utc(stamp)
    if age < timedelta(0) or age > timedelta(minutes=5):
        return Observation(target, utc(now), None, source, ("stale or future data point",))
    return Observation(target, utc(stamp), float(value), source)


class AWSCloudWatch:
    def __init__(self, client: object, target: Target, namespace: str):
        if target.cloud != "aws" or namespace != "AWS/ApplicationELB" or target.metric != "HealthyHostCount":
            raise ValueError("invalid AWS target")
        arn = target.resource.split(":", 5)
        balancer_arn = target.load_balancer.split(":", 5)
        if (len(arn) != 6 or len(balancer_arn) != 6
                or arn[:3] != ["arn", "aws", "elasticloadbalancing"]
                or balancer_arn[:5] != arn[:5]
                or not re.fullmatch(r"[0-9]{12}", arn[4])
                or not re.fullmatch(r"[a-z0-9-]+", arn[3])
                or target.scope != f"{arn[4]}/{arn[3]}"):
            raise ValueError("AWS ARN and account/region scope mismatch")
        group, balancer = arn[5], balancer_arn[5]
        if (not re.fullmatch(r"targetgroup/[A-Za-z0-9-]+/[0-9a-f]{16}", group)
                or not re.fullmatch(r"loadbalancer/app/[A-Za-z0-9-]+/[0-9a-f]{16}", balancer)):
            raise ValueError("AWS TargetGroup and LoadBalancer ARN suffixes required")
        self.client, self.target, self.namespace = client, target, namespace
        self.dimensions = [{"Name": "LoadBalancer", "Value": balancer.removeprefix("loadbalancer/")},
                           {"Name": "TargetGroup", "Value": group}]

    def collect(self, now: datetime) -> Observation:
        end = utc(now)
        try:
            response = self.client.get_metric_data(
                MetricDataQueries=[{"Id": "signal", "MetricStat": {"Metric": {
                    "Namespace": self.namespace, "MetricName": self.target.metric,
                    "Dimensions": self.dimensions}, "Period": 60, "Stat": "Average"}}],
                StartTime=end - timedelta(minutes=5), EndTime=end, ScanBy="TimestampDescending")
            results = response["MetricDataResults"]
            if len(results) != 1 or results[0]["Id"] != "signal" or results[0].get("StatusCode") != "Complete":
                raise CollectionError("CloudWatch result incomplete")
            item = results[0]
            if len(item["Timestamps"]) != len(item["Values"]):
                raise CollectionError("CloudWatch point mismatch")
            return _latest(list(zip(item["Timestamps"], item["Values"])), self.target,
                           "AWS CloudWatch GetMetricData", end)
        except CollectionError:
            raise
        except Exception:
            raise CollectionError("CloudWatch collection failed") from None


class AzureMonitor:
    def __init__(self, client: object, target: Target):
        if (target.cloud != "azure" or target.metric != "HealthyHostCount"
                or not target.resource.startswith("/subscriptions/")
                or "/providers/Microsoft.Network/applicationGateways/" not in target.resource):
            raise ValueError("invalid Azure resource ID")
        if target.resource.split("/")[2].lower() != target.scope.split("/")[0].lower():
            raise ValueError("Azure subscription scope mismatch")
        self.client, self.target = client, target

    def collect(self, now: datetime) -> Observation:
        try:
            response = self.client.query_resource(self.target.resource,
                metric_names=[self.target.metric],
                timespan=(utc(now) - timedelta(minutes=5), utc(now)))
            points = []
            series_count = 0
            for metric in response.metrics:
                if metric.name != self.target.metric:
                    continue
                for series in metric.timeseries:
                    series_count += 1
                    for point in series.data:
                        if point.average is not None:
                            points.append((point.time_stamp, point.average))
            if series_count > 1:
                raise CollectionError("Azure metric has multiple unscoped time series")
            return _latest(points, self.target, "Azure Monitor MetricsQueryClient.query_resource", now)
        except CollectionError:
            raise
        except Exception:
            raise CollectionError("Azure Monitor collection failed") from None


class GCPMonitoring:
    def __init__(self, client: object, target: Target):
        if target.cloud != "gcp" or target.metric != "compute.googleapis.com/instance_group/size":
            raise ValueError("invalid GCP metric type")
        if not re.fullmatch(r"projects/[a-zA-Z0-9-]+", target.scope):
            raise ValueError("invalid GCP project scope")
        if not re.fullmatch(r"[a-zA-Z0-9-]+", target.resource):
            raise ValueError("invalid GCP instance group name")
        if not re.fullmatch(r"[a-z0-9-]+", target.location):
            raise ValueError("GCP instance group location required")
        self.client, self.target = client, target

    def collect(self, now: datetime) -> Observation:
        end = utc(now)
        try:
            project = self.target.scope.split("/", 1)[1]
            request = {"name": self.target.scope,
                       "filter": (f'metric.type = "{self.target.metric}" AND '
                                  f'resource.type = "instance_group" AND '
                                  f'resource.labels.project_id = "{project}" AND '
                                  f'resource.labels.location = "{self.target.location}" AND '
                                  f'resource.labels.instance_group_name = "{self.target.resource}"'),
                       "interval": {"start_time": end - timedelta(minutes=5), "end_time": end},
                       "view": "FULL"}
            points = []
            series_count = 0
            for series in self.client.list_time_series(request=request):
                series_count += 1
                labels = series.resource.labels
                if (series.resource.type != "instance_group"
                        or labels.get("project_id") != project
                        or labels.get("location") != self.target.location
                        or labels.get("instance_group_name") != self.target.resource):
                    raise CollectionError("GCP response contains out-of-scope series")
                for point in series.points:
                    points.append((point.interval.end_time,
                                   point.value.int64_value or point.value.double_value))
            if series_count > 1:
                raise CollectionError("GCP metric has multiple unscoped time series")
            return _latest(points, self.target, "Google Cloud Monitoring MetricServiceClient.list_time_series", end)
        except CollectionError:
            raise
        except Exception:
            raise CollectionError("Google Cloud Monitoring collection failed") from None

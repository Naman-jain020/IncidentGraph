from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import boto3

from config import Config


class ObservabilityClient:
    """
    AWS CloudWatch-based observability adapter.

    Logs are retrieved from CloudWatch Logs.
    Metrics are retrieved from CloudWatch Metrics.
    Traces are represented by the trace source available to the
    deployment. X-Ray integration can be added when tracing is enabled.
    """

    def __init__(self):
        self.session = boto3.Session(
            region_name=Config.AWS_REGION,
        )

        self.logs = self.session.client(
            "logs"
        )

        self.cloudwatch = self.session.client(
            "cloudwatch"
        )

        self.xray = self.session.client(
            "xray"
        )

    @staticmethod
    def _parse_time(
        timestamp: str,
    ) -> datetime:
        return datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

    def query_logs(
        self,
        service: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        if not Config.CLOUDWATCH_LOG_GROUP:
            return []

        start_ms = int(
            start_time.timestamp() * 1000
        )

        end_ms = int(
            end_time.timestamp() * 1000
        )

        response = self.logs.filter_log_events(
            logGroupName=Config.CLOUDWATCH_LOG_GROUP,
            startTime=start_ms,
            endTime=end_ms,
            filterPattern=service,
        )

        return [
            {
                "timestamp": event.get(
                    "timestamp"
                ),
                "message": event.get(
                    "message"
                ),
                "log_stream": event.get(
                    "logStreamName"
                ),
            }
            for event in response.get(
                "events",
                [],
            )
        ]

    def query_metrics(
        self,
        service: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """
        Retrieve metrics from the configured namespace.

        Metric names/dimensions should be configured to match the
        application's actual CloudWatch instrumentation.
        """
        response = self.cloudwatch.list_metrics(
            Namespace=Config.CLOUDWATCH_METRIC_NAMESPACE,
        )

        metrics = []

        for metric in response.get(
            "Metrics",
            [],
        ):
            dimensions = {
                dimension["Name"]: dimension["Value"]
                for dimension in metric.get(
                    "Dimensions",
                    [],
                )
            }

            if service.lower() not in (
                str(dimensions).lower()
            ):
                continue

            metrics.append({
                "namespace": metric.get(
                    "Namespace"
                ),
                "metric_name": metric.get(
                    "MetricName"
                ),
                "dimensions": dimensions,
            })

        return metrics

    def query_traces(
        self,
        service: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """
        Query AWS X-Ray traces.

        This requires X-Ray tracing to be enabled and indexed.
        """
        try:
            response = self.xray.get_trace_summaries(
                StartTime=start_time,
                EndTime=end_time,
                FilterExpression=(
                    f'responsetime > 1 OR '
                    f'error = true'
                ),
            )
        except Exception:
            return []

        return [
            {
                "id": item.get(
                    "Id"
                ),
                "duration": item.get(
                    "Duration"
                ),
                "response_time": item.get(
                    "ResponseTime"
                ),
                "has_error": item.get(
                    "HasError"
                ),
                "has_fault": item.get(
                    "HasFault"
                ),
                "http": item.get(
                    "Http"
                ),
                "service_ids": item.get(
                    "ServiceIds"
                ),
            }
            for item in response.get(
                "TraceSummaries",
                [],
            )
        ]

    def investigate(
        self,
        service: str,
        incident_time: str,
        code_context: dict[str, Any],
    ) -> dict[str, Any]:
        incident_dt = self._parse_time(
            incident_time
        )

        start_time = incident_dt - timedelta(
            minutes=Config.DEFAULT_INCIDENT_LOOKBACK_MINUTES
        )

        end_time = datetime.now(
            timezone.utc
        )

        logs = self.query_logs(
            service,
            start_time,
            end_time,
        )

        metrics = self.query_metrics(
            service,
            start_time,
            end_time,
        )

        traces = self.query_traces(
            service,
            start_time,
            end_time,
        )

        return {
            "service": service,
            "window": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "logs": logs,
            "metrics": metrics,
            "traces": traces,
        }
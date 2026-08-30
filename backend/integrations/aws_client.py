from __future__ import annotations

from typing import Any

import boto3

from config import Config


class AWSClient:
    def __init__(
        self,
        aws_role_arn: str | None = None,
        region_name: str | None = None,
    ):
        region = region_name or Config.AWS_REGION

        # Base session using static credentials or default AWS provider chain
        session_kwargs: dict[str, Any] = {
            "region_name": region,
        }

        if Config.AWS_ACCESS_KEY_ID:
            session_kwargs["aws_access_key_id"] = Config.AWS_ACCESS_KEY_ID

        if Config.AWS_SECRET_ACCESS_KEY:
            session_kwargs["aws_secret_access_key"] = Config.AWS_SECRET_ACCESS_KEY

        if Config.AWS_SESSION_TOKEN:
            session_kwargs["aws_session_token"] = Config.AWS_SESSION_TOKEN

        base_session = boto3.Session(**session_kwargs)

        # If a user provided an IAM Role ARN, assume it dynamically via STS
        if aws_role_arn:
            sts_client = base_session.client("sts")
            assumed_role = sts_client.assume_role(
                RoleArn=aws_role_arn,
                RoleSessionName="IncidentGraphSession",
            )
            credentials = assumed_role["Credentials"]

            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=region,
            )
        else:
            session = base_session

        self.ecs = session.client("ecs")
        self.sqs = session.client("sqs")
        self.rds = session.client("rds")

    def find_ecs_services(
        self,
        service_name: str,
    ) -> list[dict[str, Any]]:
        clusters = self.ecs.list_clusters().get(
            "clusterArns",
            [],
        )

        results = []

        for cluster in clusters:
            services = self.ecs.list_services(
                cluster=cluster,
            ).get(
                "serviceArns",
                [],
            )

            matching = [
                arn
                for arn in services
                if service_name.lower()
                in arn.lower()
            ]

            if not matching:
                continue

            details = self.ecs.describe_services(
                cluster=cluster,
                services=matching,
            )

            for service in details.get(
                "services",
                [],
            ):
                results.append({
                    "cluster": cluster,
                    "service_arn": service.get(
                        "serviceArn"
                    ),
                    "service_name": service.get(
                        "serviceName"
                    ),
                    "status": service.get(
                        "status"
                    ),
                    "desired_count": service.get(
                        "desiredCount"
                    ),
                    "running_count": service.get(
                        "runningCount"
                    ),
                    "pending_count": service.get(
                        "pendingCount"
                    ),
                    "deployments": service.get(
                        "deployments",
                        [],
                    ),
                })

        return results

    def list_queues(self) -> list[str]:
        return self.sqs.list_queues().get(
            "QueueUrls",
            [],
        )

    def get_queue_attributes(
        self,
        queue_url: str,
    ) -> dict[str, Any]:
        response = self.sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=[
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
                "ApproximateNumberOfMessagesDelayed",
            ],
        )

        return {
            "queue_url": queue_url,
            "attributes": response.get(
                "Attributes",
                {},
            ),
        }

    def get_rds_instances(self) -> list[dict[str, Any]]:
        response = self.rds.describe_db_instances()

        return [
            {
                "identifier": item.get(
                    "DBInstanceIdentifier"
                ),
                "status": item.get(
                    "DBInstanceStatus"
                ),
                "engine": item.get(
                    "Engine"
                ),
                "engine_version": item.get(
                    "EngineVersion"
                ),
                "endpoint": (
                    item.get("Endpoint") or {}
                ).get("Address"),
                "port": (
                    item.get("Endpoint") or {}
                ).get("Port"),
                "connections": item.get(
                    "DatabaseInsightsMode"
                ),
            }
            for item in response.get(
                "DBInstances",
                [],
            )
        ]

    def investigate(
        self,
        service: str,
        code_context: dict[str, Any],
        observability: dict[str, Any],
    ) -> dict[str, Any]:
        ecs_services = self.find_ecs_services(
            service
        )

        queues = self.list_queues()

        queue_data = [
            self.get_queue_attributes(url)
            for url in queues
        ]

        rds_instances = self.get_rds_instances()

        return {
            "service": service,
            "ecs": ecs_services,
            "sqs": queue_data,
            "rds": rds_instances,
        }
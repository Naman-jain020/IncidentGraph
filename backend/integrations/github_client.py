from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from config import Config


class GitHubClient:
    def __init__(self):
        self.base_url = Config.GITHUB_API_URL.rstrip("/")
        self.session = requests.Session()

        if Config.GITHUB_TOKEN:
            self.session.headers.update({
                "Authorization": (
                    f"Bearer {Config.GITHUB_TOKEN}"
                )
            })

        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            timeout=20,
            **kwargs,
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def _split_repository(
        repository: str,
    ) -> tuple[str, str]:
        repository = repository.rstrip("/")

        if repository.startswith(
            "https://github.com/"
        ):
            repository = repository.removeprefix(
                "https://github.com/"
            )

        parts = repository.split("/")

        if len(parts) != 2:
            raise ValueError(
                "Repository must be in 'owner/name' format."
            )

        return parts[0], parts[1]

    def get_recent_commits(
        self,
        repository: str,
        since: datetime | None = None,
    ) -> list[dict[str, Any]]:
        owner, repo = self._split_repository(repository)

        params = {
            "per_page": 30,
        }

        if since:
            params["since"] = since.astimezone(
                timezone.utc
            ).isoformat()

        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/commits",
            params=params,
        )

    def get_commit(
        self,
        repository: str,
        sha: str,
    ) -> dict[str, Any]:
        owner, repo = self._split_repository(repository)

        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/commits/{sha}",
        )

    def get_pull_requests(
        self,
        repository: str,
    ) -> list[dict[str, Any]]:
        owner, repo = self._split_repository(repository)

        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={
                "state": "closed",
                "sort": "updated",
                "direction": "desc",
                "per_page": 20,
            },
        )

    def get_deployments(
        self,
        repository: str,
    ) -> list[dict[str, Any]]:
        owner, repo = self._split_repository(repository)

        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/deployments",
            params={
                "per_page": 20,
            },
        )

    def get_deployment_statuses(
        self,
        repository: str,
        deployment_id: int,
    ) -> list[dict[str, Any]]:
        owner, repo = self._split_repository(repository)

        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/deployments/"
            f"{deployment_id}/statuses",
        )

    def investigate(
        self,
        repository: str,
        service: str,
        incident_time: str,
        code_context: dict[str, Any],
    ) -> dict[str, Any]:
        if not repository:
            return {
                "warning": "No GitHub repository supplied.",
                "commits": [],
                "pull_requests": [],
                "deployments": [],
            }

        incident_dt = datetime.fromisoformat(
            incident_time.replace("Z", "+00:00")
        )

        since = incident_dt - timedelta(days=3)

        commits = self.get_recent_commits(
            repository,
            since=since,
        )

        deployments = self.get_deployments(
            repository,
        )

        pull_requests = self.get_pull_requests(
            repository,
        )

        relevant_files = self._extract_files(
            code_context
        )

        relevant_commits = []

        for commit in commits:
            sha = commit.get("sha")

            if not sha:
                continue

            try:
                details = self.get_commit(
                    repository,
                    sha,
                )
            except requests.RequestException:
                continue

            changed_files = [
                file.get("filename")
                for file in details.get("files", [])
            ]

            if (
                not relevant_files
                or any(
                    self._file_matches(
                        changed,
                        relevant_files,
                    )
                    for changed in changed_files
                )
            ):
                relevant_commits.append({
                    "sha": sha,
                    "message": (
                        commit.get("commit", {})
                        .get("message", "")
                    ),
                    "author": (
                        commit.get("commit", {})
                        .get("author", {})
                    ),
                    "changed_files": changed_files,
                    "url": commit.get("html_url"),
                })

        deployment_results = []

        for deployment in deployments[:10]:
            deployment_id = deployment.get("id")

            if not deployment_id:
                continue

            try:
                statuses = self.get_deployment_statuses(
                    repository,
                    deployment_id,
                )
            except requests.RequestException:
                statuses = []

            deployment_results.append({
                "id": deployment_id,
                "sha": deployment.get("sha"),
                "ref": deployment.get("ref"),
                "environment": deployment.get(
                    "environment"
                ),
                "created_at": deployment.get(
                    "created_at"
                ),
                "updated_at": deployment.get(
                    "updated_at"
                ),
                "statuses": statuses,
            })

        return {
            "service": service,
            "incident_time": incident_time,
            "commits": relevant_commits,
            "pull_requests": pull_requests,
            "deployments": deployment_results,
        }

    @staticmethod
    def _extract_files(
        code_context: dict[str, Any],
    ) -> list[str]:
        files: list[str] = []

        raw_files = code_context.get("files", [])

        if isinstance(raw_files, list):
            files.extend(
                str(item)
                for item in raw_files
            )

        answer = code_context.get(
            "codebase_answer",
            {},
        )

        if isinstance(answer, dict):
            citations = answer.get(
                "citations",
                [],
            )

            if isinstance(citations, list):
                for citation in citations:
                    if isinstance(citation, str):
                        files.append(citation)

        return list(dict.fromkeys(files))

    @staticmethod
    def _file_matches(
        changed_file: str,
        relevant_files: list[str],
    ) -> bool:
        changed = changed_file.strip()

        return any(
            changed == relevant.strip()
            or changed.endswith(
                relevant.strip()
            )
            or relevant.strip().endswith(changed)
            for relevant in relevant_files
        )
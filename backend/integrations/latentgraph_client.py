from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from config import Config


class LatentGraphClient:
    """
    Adapter for the LatentGraph MCP server.

    LatentGraph exposes its code-intelligence capabilities through MCP.
    This client launches the official `lgraph mcp` server over stdio and
    invokes its read-only tools.
    """

    def __init__(
        self,
        repository: str = "",
        project_id: str | None = None,
        branch: str | None = None,
    ):
        self.repository = repository
        self.project_id = project_id or os.getenv(
            "LGRAPH_PROJECT_ID"
        )
        self.branch = branch or os.getenv(
            "LGRAPH_BRANCH"
        )

    def _server_environment(self) -> dict[str, str]:
        env = os.environ.copy()

        if Config.LATENTGRAPH_API_KEY:
            env["LGRAPH_API_KEY"] = (
                Config.LATENTGRAPH_API_KEY
            )

        if self.project_id:
            env["LGRAPH_PROJECT_ID"] = self.project_id

        if self.branch:
            env["LGRAPH_BRANCH"] = self.branch

        return env

    def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        Invoke a LatentGraph MCP tool.

        This method expects the `lgraph` CLI to be installed and
        available on PATH.
        """
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError as exc:
            raise RuntimeError(
                "The 'mcp' Python package is required for "
                "LatentGraph integration."
            ) from exc

        server = StdioServerParameters(
            command="lgraph",
            args=["mcp"],
            env=self._server_environment(),
        )

        async def _run():
            async with stdio_client(server) as (
                read_stream,
                write_stream,
            ):
                async with ClientSession(
                    read_stream,
                    write_stream,
                ) as session:
                    await session.initialize()

                    result = await session.call_tool(
                        tool_name,
                        arguments or {},
                    )

                    return self._parse_result(result)

        import asyncio

        return asyncio.run(_run())

    @staticmethod
    def _parse_result(result: Any) -> Any:
        """
        MCP read tools return structured content. Preserve structured
        values where possible and parse JSON/TOON-like text when possible.
        """
        if hasattr(result, "structuredContent"):
            return result.structuredContent

        content = getattr(result, "content", None)

        if not content:
            return result

        text_parts = []

        for item in content:
            text = getattr(item, "text", None)

            if text:
                text_parts.append(text)

        if not text_parts:
            return result

        text = "\n".join(text_parts).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "raw": text,
            }

    def _common_arguments(self) -> dict[str, Any]:
        arguments: dict[str, Any] = {}

        if self.project_id:
            arguments["project_id"] = self.project_id

        if self.branch:
            arguments["branch"] = self.branch

        return arguments

    def get_project_overview(self) -> Any:
        return self._call_mcp_tool(
            "get_project_overview",
            self._common_arguments(),
        )

    def get_module_info(self, module_id: str) -> Any:
        args = self._common_arguments()
        args["module_id"] = module_id

        return self._call_mcp_tool(
            "get_module_info",
            args,
        )

    def get_file(self, file_path: str) -> Any:
        args = self._common_arguments()
        args["file_path"] = file_path

        return self._call_mcp_tool(
            "get_file",
            args,
        )

    def get_dependencies(self, file_path: str) -> Any:
        args = self._common_arguments()
        args["file_path"] = file_path

        return self._call_mcp_tool(
            "get_dependencies",
            args,
        )

    def get_call_chain(self, symbol: str) -> Any:
        args = self._common_arguments()
        args["symbol"] = symbol

        return self._call_mcp_tool(
            "get_call_chain",
            args,
        )

    def get_symbol(
        self,
        name: str,
        file_path: str | None = None,
        kind: str | None = None,
    ) -> Any:
        args = self._common_arguments()
        args["name"] = name

        if file_path:
            args["file_path"] = file_path

        if kind:
            args["kind"] = kind

        return self._call_mcp_tool(
            "get_symbol",
            args,
        )

    def get_pr_insights(
        self,
        file_path: str | None = None,
        module_id: str | None = None,
    ) -> Any:
        args = self._common_arguments()

        if file_path:
            args["file_path"] = file_path

        if module_id:
            args["module_id"] = module_id

        return self._call_mcp_tool(
            "get_pr_insights",
            args,
        )

    def ask_codebase(self, question: str) -> Any:
        args = self._common_arguments()
        args["question"] = question

        return self._call_mcp_tool(
            "ask_codebase",
            args,
        )

    def investigate(
        self,
        service: str,
        query: str,
    ) -> dict[str, Any]:
        """
        Perform a compact investigation using the actual LatentGraph
        read tools.

        We first orient the agent with the project overview and then
        use semantic codebase Q&A for the incident-specific question.
        """
        overview = self.get_project_overview()

        answer = self.ask_codebase(
            f"""
Investigate the production incident involving service/component:
{service}

Question:
{query}

Identify relevant files, modules, symbols, dependencies,
call chains and architectural relationships.
"""
        )

        return {
            "project_overview": overview,
            "codebase_answer": answer,
        }
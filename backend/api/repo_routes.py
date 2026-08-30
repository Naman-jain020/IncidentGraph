from flask import Blueprint, request, jsonify
from integrations.github_client import GitHubClient

repo_bp = Blueprint("repos", __name__)

@repo_bp.post("/analyze")
def analyze_repository():
    """
    Analyzes a GitHub repo to detect infrastructure & third-party tools.
    Returns detected services and required user configurations.
    """
    payload = request.get_json(silent=True) or {}
    repo = payload.get("repository") # e.g. "owner/repo"

    if not repo:
        return jsonify({"error": "missing_repository", "message": "Repository name is required."}), 400

    try:
        github_client = GitHubClient()
        # Scan repo file structure or tree
        files = github_client.list_repo_files(repo)
        
        detected_configs = []
        required_user_inputs = []

        # 1. AWS Detection
        has_aws = any(f.endswith((".tf", "serverless.yml", "template.yaml", "cdk.json")) or "aws" in f.lower() for f in files)
        if has_aws:
            detected_configs.append({"type": "aws", "name": "AWS Cloud Infrastructure"})
            required_user_inputs.append({
                "type": "aws",
                "title": "AWS Credentials / IAM Role (Required)",
                "fields": [
                    {"name": "aws_role_arn", "label": "IAM Role ARN", "placeholder": "arn:aws:iam::123456789012:role/IncidentGraphRole", "required": True},
                    {"name": "aws_region", "label": "AWS Region", "default": "us-east-1", "required": True}
                ]
            })

        # 2. Observability Detection
        has_cw = any("cloudwatch" in f.lower() or "datadog" in f.lower() for f in files)
        if has_cw:
            detected_configs.append({"type": "observability", "name": "CloudWatch / Datadog Logs"})
            required_user_inputs.append({
                "type": "observability",
                "title": "Observability / CloudWatch Log Group (Required)",
                "fields": [
                    {"name": "log_group_name", "label": "CloudWatch Log Group Name", "placeholder": "/aws/ecs/production-logs", "required": True}
                ]
            })

        # 3. Third-party MCP Integration Option
        required_user_inputs.append({
            "type": "mcp",
            "title": "Third-Party MCP Integration (Optional)",
            "fields": [
                {"name": "mcp_url", "label": "MCP Server URL", "placeholder": "https://mcp.yourdomain.com/v1"},
                {"name": "mcp_api_key", "label": "MCP API Key", "placeholder": "mcp_sec_..."}
            ]
        })

        return jsonify({
            "repository": repo,
            "detected_configs": detected_configs,
            "required_user_inputs": required_user_inputs,
            "graph_status": "ready_for_indexing"
        }), 200

    except Exception as exc:
        return jsonify({"error": "analysis_failed", "message": str(exc)}), 500
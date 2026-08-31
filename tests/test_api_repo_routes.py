from unittest.mock import patch, Mock
import pytest
from flask import Flask
from api.repo_routes import repo_bp
import requests


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(repo_bp, url_prefix="/api/repos")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_analyze_repository_missing_repo(client):
    res = client.post("/api/repos/analyze", json={})
    assert res.status_code == 400
    assert res.json["error"] == "missing_repository"


def test_analyze_repository_success(client):
    mock_files = ["main.tf", "app.py", "cloudwatch.log"]

    with patch("api.repo_routes.GitHubClient") as mock_github_cls:
        mock_instance = Mock()
        mock_instance.list_repo_files.return_value = mock_files
        mock_github_cls.return_value = mock_instance

        res = client.post("/api/repos/analyze", json={"repository": "owner/repo"})

        assert res.status_code == 200
        data = res.json
        assert data["repository"] == "owner/repo"
        assert len(data["detected_configs"]) == 2
        assert data["detected_configs"][0]["type"] == "aws"
        assert data["detected_configs"][1]["type"] == "observability"


def test_analyze_repository_github_http_error(client):
    mock_resp = Mock()
    mock_resp.status_code = 404
    mock_resp.content = b'{"message": "Not Found"}'
    mock_resp.json.return_value = {"message": "Not Found"}

    http_err = requests.exceptions.HTTPError(response=mock_resp)

    with patch("api.repo_routes.GitHubClient") as mock_github_cls:
        mock_instance = Mock()
        mock_instance.list_repo_files.side_effect = http_err
        mock_github_cls.return_value = mock_instance

        res = client.post("/api/repos/analyze", json={"repository": "owner/nonexistent"})

        assert res.status_code == 404
        assert res.json["error"] == "github_api_error"
        assert "Not Found" in res.json["message"]


def test_analyze_repository_github_forbidden_error(client):
    mock_resp = Mock()
    mock_resp.status_code = 403
    mock_resp.content = b'{"message": "Bad credentials"}'
    mock_resp.json.return_value = {"message": "Bad credentials"}

    http_err = requests.exceptions.HTTPError(response=mock_resp)

    with patch("api.repo_routes.GitHubClient") as mock_github_cls:
        mock_instance = Mock()
        mock_instance.list_repo_files.side_effect = http_err
        mock_github_cls.return_value = mock_instance

        res = client.post("/api/repos/analyze", json={"repository": "owner/forbidden"})

        assert res.status_code == 403
        assert res.json["error"] == "github_api_error"
        assert "Bad credentials" in res.json["message"]

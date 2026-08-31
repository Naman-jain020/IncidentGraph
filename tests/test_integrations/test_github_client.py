from unittest.mock import Mock, patch

from integrations.github_client import GitHubClient


def test_split_repository():
    owner, repo = GitHubClient._split_repository(
        "https://github.com/acme/payment-service.git "
    )

    assert owner == "acme"
    assert repo == "payment-service"


def test_github_client_token_header_format():
    with patch("integrations.github_client.Config.GITHUB_TOKEN", "ghp_123456"):
        client = GitHubClient()
        assert client.session.headers["Authorization"] == "token ghp_123456"

    with patch("integrations.github_client.Config.GITHUB_TOKEN", "github_pat_789"):
        client = GitHubClient()
        assert client.session.headers["Authorization"] == "Bearer github_pat_789"


def test_get_recent_commits():
    client = GitHubClient()

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        {
            "sha": "abc123",
            "commit": {
                "message": "Fix payment timeout"
            },
        }
    ]

    with patch.object(
        client.session,
        "request",
        return_value=mock_response,
    ):
        result = client.get_recent_commits(
            "acme/payment-service"
        )

    assert len(result) == 1
    assert result[0]["sha"] == "abc123"
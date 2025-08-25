"""
GitHub MCP Server integration tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from ..core.github_mcp_server import app, GithubMCPServer
from ..core.models import Repository, Issue, PullRequest

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def mock_gh_api():
    """Mock GitHub API fixture"""
    with patch("ghapi.all.GhApi") as mock:
        yield mock

def test_search_files(client, mock_gh_api):
    """Test file search endpoint"""
    # Setup mock response
    mock_gh_api.search.code.return_value = {
        "items": [
            {
                "path": "test.py",
                "html_url": "https://github.com/test/test/blob/main/test.py",
                "sha": "abc123"
            }
        ]
    }
    
    # Make request
    response = client.get(
        "/api/repos/test/test/files",
        params={"query": "test"},
        headers={"Authorization": "Bearer test-token"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["path"] == "test.py"

def test_create_issue(client, mock_gh_api):
    """Test issue creation endpoint"""
    # Setup mock response
    mock_issue = {
        "number": 1,
        "title": "Test Issue",
        "body": "Test description",
        "state": "open",
        "created_at": "2025-08-25T00:00:00Z",
        "updated_at": "2025-08-25T00:00:00Z"
    }
    mock_gh_api.issues.create.return_value = mock_issue
    
    # Make request
    response = client.post(
        "/api/repos/test/test/issues",
        json={
            "title": "Test Issue",
            "body": "Test description"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Issue"
    assert data["number"] == 1

def test_security_findings(client, mock_gh_api):
    """Test security findings endpoint"""
    # Setup mock response
    mock_findings = {
        "vulnerabilities": [
            {
                "severity": "HIGH",
                "package": "test-package",
                "description": "Test vulnerability"
            }
        ],
        "timestamp": "2025-08-25T00:00:00Z"
    }
    mock_gh_api.security.return_value = mock_findings
    
    # Make request
    response = client.get(
        "/api/repos/test/test/security",
        headers={"Authorization": "Bearer test-token"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data["vulnerabilities"]) == 1
    assert data["vulnerabilities"][0]["severity"] == "HIGH"

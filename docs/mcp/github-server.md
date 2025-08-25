# GitHub MCP Server

The GitHub Model Context Protocol (MCP) Server provides a standardized interface for AI agents to interact with GitHub repositories, issues, pull requests, and other GitHub features.

## Features

- **Repository Intelligence**
  - File browsing and search
  - Code analysis and insights
  - Commit history analysis
  - Security vulnerability scanning
  
- **Workflow Automation**
  - Issue management
  - Pull request automation
  - CI/CD monitoring
  - Dependabot alert processing
  
- **Team Collaboration**
  - Discussion management
  - Notification handling
  - Project board integration
  - Wiki management

## Installation

1. Configure environment variables:
```bash
# Create .env file (do not commit this file)
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY=your_private_key
GITHUB_INSTALLATION_ID=your_installation_id
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python -m mcp.github_server
```

## Configuration

The server can be configured through environment variables or a config file:

```yaml
# config.yml
github:
  app_id: your_app_id
  installation_id: your_installation_id
  private_key_path: path/to/private-key.pem
  webhook_secret: your_webhook_secret

server:
  host: 0.0.0.0
  port: 3000
  log_level: INFO

security:
  rate_limit: true
  rate_limit_window: 3600
  max_requests: 1000
```

## API Reference

### Repository Operations

```typescript
interface RepositoryAPI {
  // File operations
  searchFiles(query: string): Promise<File[]>
  getFileContent(path: string): Promise<string>
  
  // Code analysis
  analyzeCode(path: string): Promise<CodeAnalysis>
  getSecurity(path: string): Promise<SecurityFindings>
  
  // Git operations
  listCommits(params: CommitParams): Promise<Commit[]>
  getBranches(): Promise<Branch[]>
}
```

### Issue Management

```typescript
interface IssueAPI {
  create(params: IssueParams): Promise<Issue>
  update(number: number, params: IssueUpdate): Promise<Issue>
  list(params: IssueQuery): Promise<Issue[]>
  addLabels(number: number, labels: string[]): Promise<void>
}
```

### Pull Request Automation

```typescript
interface PullRequestAPI {
  create(params: PRParams): Promise<PullRequest>
  update(number: number, params: PRUpdate): Promise<PullRequest>
  merge(number: number, method: MergeMethod): Promise<void>
  review(number: number, review: Review): Promise<void>
}
```

## Security

The server implements several security measures:

1. **Authentication**
   - GitHub App authentication
   - JWT token verification
   - Webhook signature validation

2. **Authorization**
   - Repository permission checks
   - User access control
   - Rate limiting

3. **Data Protection**
   - Sensitive data encryption
   - Secure credential storage
   - Audit logging

## Error Handling

The server provides detailed error responses:

```typescript
interface ErrorResponse {
  error: {
    code: string
    message: string
    details?: object
    requestId?: string
  }
}
```

Common error codes:
- `AUTH_ERROR`: Authentication failed
- `PERMISSION_DENIED`: Insufficient permissions
- `RATE_LIMITED`: Too many requests
- `INVALID_REQUEST`: Malformed request
- `NOT_FOUND`: Resource not found
- `INTERNAL_ERROR`: Server error

## Testing

Run the test suite:

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# E2E tests
pytest tests/e2e
```

## Monitoring

The server exposes metrics for monitoring:

- **Prometheus metrics**: `/metrics`
- **Health check**: `/health`
- **Status page**: `/status`

## Troubleshooting

Common issues and solutions:

1. **Authentication Failures**
   - Check GitHub App credentials
   - Verify private key format
   - Validate installation ID

2. **Rate Limiting**
   - Check rate limit status
   - Implement request batching
   - Use conditional requests

3. **Permission Issues**
   - Review GitHub App permissions
   - Check repository access
   - Verify user authorization

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Code style
- Pull request process
- Testing requirements
- Documentation updates

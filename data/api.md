# DeployHub API Reference

## Authentication

All API requests require a bearer token. Generate tokens in Account Settings > API Tokens. Include in the Authorization header:

```
Authorization: Bearer dhk_xxxxxxxxxxxxxxxx
```

## Rate Limits

- Free: 50 requests/minute
- Pro: 200 requests/minute
- Team: 500 requests/minute
- Enterprise: Custom

Rate limit headers are included in every response: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset.

## Endpoints

### Deployments

| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/deployments | List all deployments |
| POST | /v1/deployments | Create a new deployment |
| GET | /v1/deployments/:id | Get deployment details |
| POST | /v1/deployments/:id/rollback | Roll back to a previous version |
| DELETE | /v1/deployments/:id | Cancel or remove a deployment |

### Projects

| Method | Path | RAM Options |
|--------|------|-------------|
| GET | /v1/projects | List projects |
| POST | /v1/projects | Create project |
| PATCH | /v1/projects/:id | Update project settings |
| DELETE | /v1/deployments/:id | Delete project |

### Webhooks

Register webhooks to receive deployment events. Events: deployment.created, deployment.success, deployment.failed, deployment.rolled_back. Webhooks include an HMAC signature in the X-DeployHub-Signature header for verification.

## Errors

All errors return standard HTTP status codes with a JSON body:

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit of 50 requests/minute exceeded",
    "request_id": "req_abc123"
  }
}
```

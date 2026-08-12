# DeployHub Security and Privacy

## Data Encryption

All data is encrypted at rest using AES-256. Data in transit uses TLS 1.3. Environment secrets are encrypted separately with envelope encryption.

## Compliance

DeployHub is SOC 2 Type II certified. GDPR compliant. HIPAA-ready for Enterprise customers with a signed BAA.

## Access Control

- Free and Pro: Single user
- Team: Role-based access control (Admin, Developer, Viewer)
- Enterprise: SSO via SAML, SCIM provisioning, custom roles

## Data Retention

Deployment logs are retained for 30 days (Free and Pro), 90 days (Team), and 1 year (Enterprise). Customer application data follows your plan's retention policy.

## Incident Response

Security incidents are classified by severity (P1 through P4). P1 incidents trigger immediate response with status page updates within 15 minutes. Post-incident reports are published within 7 days.

## Responsible Disclosure

Report vulnerabilities to security@deployhub.io. We respond within 48 hours. Critical vulnerabilities receive a bounty of $500-$5000 depending on impact.

## Subprocessors

- Google Cloud Platform: Infrastructure
- Stripe: Payment processing
- Cloudflare: CDN and DDoS protection
- Sentry: Error monitoring

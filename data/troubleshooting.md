# DeployHub Troubleshooting

## Common Issues

### Deployment Fails During Build
**Cause:** Missing dependencies or incorrect build command.
**Fix:** Check the build log in the Deployments tab. Ensure package.json (Node.js), requirements.txt (Python), or go.mod (Go) lists all dependencies. Verify the build command in Project Settings.

### Application Returns 502 Bad Gateway
**Cause:** The application crashed after starting or did not bind to the correct port.
**Fix:** DeployHub exposes port 8080 by default. Ensure your app listens on the PORT environment variable. Check runtime logs under Logs > Runtime for crash traces.

### Custom Domain Shows "Pending" Status
**Cause:** DNS records not configured or not yet propagated.
**Fix:** Add a CNAME record pointing to the address shown in Project Settings > Domains. Wait for DNS propagation. If still pending after 48 hours, contact support.

### High Latency After Deployment
**Cause:** Wrong region selected or resource limit hit.
**Fix:** Deploy to the region closest to your users. Options: US-East, US-West, EU-West, AP-Southeast. Check if memory usage exceeds plan limits in the Metrics tab.

### SSL Certificate Not Provisioned
**Cause:** Let's Encrypt rate limit or domain ownership not verified.
**Fix:** Verify domain ownership via the DNS challenge. If you have provisioned more than 5 certificates in a week, wait 7 days for the rate limit to reset.

## Support Escalation

- Free tier: Community forum only
- Pro: Email support@deployhub.io (24h SLA)
- Team: Priority email (4h SLA)
- Enterprise: 24/7 phone and email

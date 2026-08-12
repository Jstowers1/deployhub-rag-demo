# DeployHub Deployment Guide

## Creating Your First Deployment

1. Connect your Git repository from GitHub, GitLab, or Bitbucket.
2. Select the environment (Node.js, Python, Go, Docker, or Static).
3. Configure build settings if needed. DeployHub auto-detects most frameworks.
4. Click Deploy. Average deployment time is 45 seconds.

## Environment Variables

Set environment variables in Project Settings > Environment. Changes require a redeployment to take effect. Secret variables are encrypted at rest and never logged.

## Rollbacks

Every deployment creates a version snapshot. Roll back from the Deployments tab by selecting a previous version and clicking Roll Back. Rollback time is under 10 seconds.

## Custom Domains

Available on Pro plan and above. Add your domain in Project Settings > Domains. DeployHub provisions SSL certificates automatically via Let's Encrypt. DNS propagation can take up to 48 hours but typically completes in 15 minutes.

## Deployment Limits

- Free tier: 100 deployments/month
- Pro and above: unlimited
- Maximum build time: 15 minutes
- Maximum artifact size: 500MB

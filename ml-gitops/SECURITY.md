# Security Policy

## Reporting a Vulnerability
Please report security issues privately to the platform security team.

## Secrets Management
- No plaintext secrets in the repository
- Prefer External Secrets Operator or Sealed Secrets for secret delivery
- Rotate secrets regularly; track ownership and TTLs

## Access Control
- Enforce CODEOWNERS and branch protection on `main`
- Restrict write access to platform teams
- Use least-privilege IAM roles; verify IRSA annotations

## Supply Chain
- Only immutable image tags (branch-latest or SHA/digest)
- Consider ArgoCD Image Updater with write-back via PR
- Verify images come from trusted registries (ECR)

## Runtime Policies
- Namespaces: separate per environment
- Apply ResourceQuota and LimitRange where appropriate
- Enable monitoring and alerting for critical apps

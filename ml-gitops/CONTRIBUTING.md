# Contributing Guidelines

Thank you for contributing to the ML Fashion Recommender GitOps repository.

## Scope
- Declarative Kubernetes manifests only (ArgoCD Applications, Kustomize overlays, platform manifests)
- No application source code or Docker build logic

## Branching Strategy
- main: production-ready state, reconciled by ArgoCD
- feature/*: short-lived branches for changes; rebase frequently

## Commit Convention
Use Conventional Commits:
- feat(scope): summary
- fix(scope): summary
- docs(scope): summary
- refactor(scope): summary
- chore(scope): summary
- ci(scope): summary

## Pull Requests
- Keep PRs small and focused
- Include context in description (what/why, risk, rollout plan)
- All PRs must pass CI (validate-gitops)
- Include screenshots or `kustomize build` outputs when relevant

## Reviews & CODEOWNERS
- CODEOWNERS define mandatory reviewers; approvals required before merge
- Address review comments promptly; prefer follow-up PRs for non-blockers

## Merge Policy
- Squash merge with meaningful summary title
- No direct pushes to main

## Testing & Validation
- Run `kustomize build` on all modified overlays
- Avoid breaking ApplicationSets: ensure paths and generators remain valid

## Security
- No plaintext secrets; use Sealed Secrets or External Secrets
- Ensure IRSA annotations and roles are correct per environment

## Rollouts & Backouts
- Prefer progressive changes; use ArgoCD sync waves if ordering is required
- Backout via revert PR when necessary; keep revert changes isolated

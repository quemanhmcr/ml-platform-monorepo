# Change Management

## Governance
- All changes via Pull Requests
- Require CODEOWNERS approval and passing CI
- Protect `main` branch (no direct pushes)

## Release & Versioning
- This is a config repo; releases are represented by Git tags on `main`
- Tag format: `gitops-YYYYMMDD.N` or semver if coordinated with platform releases
- Optionally encode environment windows (e.g., freeze periods) in PR templates

## Approvals & Rollouts
- Changes affecting production overlays require platform-admin approval
- Staging soak period recommended before production rollout
- Use ArgoCD sync options and waves to control ordering

## Auditing
- PRs must describe: scope, impact, rollback plan
- Keep changes small; single-responsibility PRs
- Use GitHub protected branches and required status checks

## Backout
- Revert PRs cleanly; avoid mixing revert with new changes
- Monitor ArgoCD health after revert

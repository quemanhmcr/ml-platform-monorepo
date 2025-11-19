# CI/CD: Build and Push to ECR (ML Platform)

This document explains how the GitHub Actions workflow builds and pushes Docker images for ML components to AWS ECR using immutable tags.

## Overview
- Monorepo with components: `data_ingestion`, `data_processing`, `data_eda`, `train`, `inference`.
- Only changed components are built and pushed to minimize CI time and cost.
- Standardized ECR namespace: `ml-fashion-recommender/<component>`.
- Immutable tagging strategy with branch + SHA variants.

## Triggers
- push: branches `main`, `develop` with path filters `components/**`, `config/aws.json`, and the workflow file.
- pull_request: branches `main`, `develop` with the same path filters.

## Job Order
1) detect-changes
   - Detects changed components between the current commit and base (for PR) or parent (for push).
   - Special cases: first commit (build all), `config/aws.json` changes (build all).
   - Output: `components` (JSON array) used by the matrix in the next job.

2) build-and-push (matrix over `components`)
   - Loads AWS config (ENV/secrets-first), config file fallback as needed.
   - Auth via OIDC using `aws-actions/configure-aws-credentials`.
   - Generates immutable image tags (branch + short SHA, full SHA, branch-latest for main/develop).
   - Builds images and pushes to ECR at `ml-fashion-recommender/<component>`.
   - Produces a human-readable summary with image URLs and tags.

## ECR Namespace
- All images are pushed under a fixed namespace per account/region:
  - `<account>.dkr.ecr.<region>.amazonaws.com/ml-fashion-recommender/<component>:<tag>`
- Repositories are expected to be pre-provisioned in ECR for each component.

## Tagging Policy (Immutable)
- Primary tag depends on event/branch:
  - main: `main-<short-sha>`
  - develop: `develop-<short-sha>`
  - PR: `pr-<number>-<short-sha>`
  - other branches: `<sanitized-branch>-<short-sha>`
- Additional tags: `<full-sha>`, `main-latest` or `develop-latest` where applicable, and `pr-<number>`.

## Secrets and OIDC
- OIDC is used to assume an IAM role securely (no long-lived keys).
- Required job permissions: `id-token: write`, `contents: read`.
- AWS config values (ECR-only) resolve with priority:
  1. Environment (from GitHub secrets)
  2. `config/aws.json` (fallback)
  3. Defaults where appropriate (e.g., region)

## Adding a New Component
1. Create `components/<new_component>/Dockerfile` and source code.
2. Ensure the component name is included in the detect list in workflow (regex).
3. Ensure the ECR repo exists: `ml-fashion-recommender/<new_component>`.
4. Push a change touching the component folder; CI will detect and build.

## Troubleshooting
- Repository not found during push:
  - Ensure ECR repo exists with name `ml-fashion-recommender/<component>` in the configured region/account.
  - Verify IAM role permissions: `ecr:BatchCheckLayerAvailability`, `ecr:PutImage`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:DescribeRepositories`.
- OIDC warnings:
  - Make sure job `permissions` includes `id-token: write` and the workflow is allowed to request the role.
- Tag collisions:
  - Tags are immutable; re-pushing same `<full-sha>` fails by design. Use new commits for new images.

## Conventions / Hardening
- Immutable tags only; no generic `latest` except controlled branch-latest.
- Least-privilege job permissions.
- Optional enhancements: pin action SHAs, set `concurrency` by ref, `timeout-minutes`, and prefer explicit Docker CLI args (avoid `eval`).



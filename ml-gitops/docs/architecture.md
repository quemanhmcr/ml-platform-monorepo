# GitOps Architecture

## Overview

This GitOps repository implements a multi-tier architecture for managing ML workloads on Kubernetes using ArgoCD and Argo Workflows.

## Architecture Layers

### 1. Application Layer (`apps/`)
Contains application definitions using Kustomize base/overlays pattern:
- **Base**: Common configuration shared across environments
- **Overlays**: Environment-specific customizations (production, staging)

### 2. Bootstrap Layer (`bootstrap/`)
Manages the orchestration of applications:
- **ApplicationSets**: Automatically creates ArgoCD Applications
- **Platform Apps**: Manages infrastructure components

### 3. Manifest Layer (`manifests/`)
Contains platform infrastructure components:
- Monitoring stack (Prometheus, Grafana)
- Logging stack (ELK, Fluentd)

### 4. Root Layer (`argocd-root/`)
Single entry point - the "mother application" that manages everything.

## Data Flow

```
Developer Push → GitHub → CI/CD Pipeline → ECR
                                         ↓
Git Commit → ArgoCD Root App → Bootstrap Apps → ApplicationSets → Applications → Kubernetes
```

## Sync Flow

1. Developer commits changes to Git
2. ArgoCD detects changes (polling or webhook)
3. Root Application syncs bootstrap directory
4. ApplicationSets create/update Applications
5. Applications sync their respective Kubernetes resources
6. Kubernetes applies resources to cluster

## Environment Strategy

- **Production**: Stable, tested code from `main` branch
- **Staging**: Latest code from `develop` branch for testing
- **Development**: Feature branches for experimentation


# H&M ML Platform - GitOps Configuration

> Enterprise GitOps repository for declarative Kubernetes deployment of ML workloads

[![ArgoCD](https://img.shields.io/badge/ArgoCD-2.8+-blue.svg)](https://argo-cd.readthedocs.io/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.24+-green.svg)](https://kubernetes.io/)
[![Kustomize](https://img.shields.io/badge/Kustomize-4.5+-orange.svg)](https://kustomize.io/)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Applications](#applications)
- [Environments](#environments)
- [Deployment Workflow](#deployment-workflow)
- [Configuration](#configuration)
- [Development](#development)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This repository implements a production-ready GitOps setup for deploying and managing ML workloads on Kubernetes using **ArgoCD** and **Argo Workflows**. It follows enterprise GitOps patterns with multi-environment support, automated sync policies, and declarative configuration management.

### Key Features

- 🔄 **Declarative GitOps**: Single source of truth in Git
- 🌍 **Multi-Environment**: Production and staging environments
- 🔀 **ApplicationSets**: Automated application management
- 📦 **Kustomize**: Base/overlay pattern for DRY configuration
- 🔒 **Security**: IRSA (IAM Roles for Service Accounts), sealed secrets
- 📊 **Observability**: Integrated monitoring and logging
- ⚡ **Auto-Sync**: Automated deployment with self-healing
- 🚀 **CI/CD Integration**: Seamless integration with ML platform CI/CD

## 🏛️ Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    GitOps Repository                        │
│                    (This Repository)                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Git Commit
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ArgoCD Root Application                        │
│           (argocd-root/root-application.yaml)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Manages
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Bootstrap Layer                            │
│            (bootstrap/apps/*.yaml)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ApplicationSets                                     │  │
│  │  - ml-recommendation-inference                       │  │
│  │  - ml-training-workflow-circle                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Creates
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Application Layer                           │
│              (apps/*/overlays/*/)                           │
│  ┌──────────────────────┐  ┌───────────────────────────┐  │
│  │  Inference Service   │  │  Training Workflows       │  │
│  │  - Production        │  │  - Production             │  │
│  │  - Staging           │  │  - Staging                │  │
│  └──────────────────────┘  └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Deploys to
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (EKS)                       │
│  ┌──────────────────────┐  ┌───────────────────────────┐  │
│  │  ml-inference-prod   │  │  ml-training-prod         │  │
│  │  Namespace           │  │  Namespace                │  │
│  └──────────────────────┘  └───────────────────────────┘  │
│  ┌──────────────────────┐  ┌───────────────────────────┐  │
│  │  ml-inference-stag   │  │  ml-training-stag         │  │
│  │  Namespace           │  │  Namespace                │  │
│  └──────────────────────┘  └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Developer Push → CI/CD Pipeline → ECR (Docker Images)
                                        │
                                        │ Updates Image Tag
                                        ▼
                        Git Commit → GitOps Repo
                                        │
                                        │ ArgoCD Detects
                                        ▼
                        ArgoCD Root → ApplicationSets
                                        │
                                        │ Syncs
                                        ▼
                        Kubernetes Resources → Cluster
```

### Component Layers

1. **Root Layer** (`argocd-root/`): Single entry point, manages all applications
2. **Bootstrap Layer** (`bootstrap/`): ApplicationSets and platform apps
3. **Application Layer** (`apps/`): Application definitions with Kustomize
4. **Manifest Layer** (`manifests/`): Platform infrastructure components

## 🚀 Quick Start

### Prerequisites

- **Kubernetes Cluster**: EKS 1.24+ with ArgoCD installed
- **ArgoCD**: 2.8+ installed and configured
- **Argo Workflows**: Controller installed (for training workflows)
- **AWS Access**: ECR access configured via IRSA
- **kubectl**: Configured to access your cluster
- **Kustomize**: 4.5+ (for local validation)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/hm-mlops-gitops.git
   cd hm-mlops-gitops
   ```

2. **Update repository URL**:
   Edit `argocd-root/root-application.yaml`:
   ```yaml
   source:
     repoURL: https://github.com/your-org/hm-mlops-gitops.git
   ```

3. **Configure image registry**:
   Update ECR registry URLs in:
   - `apps/ml-recommendation-inference/overlays/production/kustomization.yaml`
   - `apps/ml-recommendation-inference/overlays/staging/kustomization.yaml`

4. **Apply root application**:
   ```bash
   kubectl apply -f argocd-root/root-application.yaml
   ```

5. **Verify deployment**:
   ```bash
   # Check ArgoCD applications
   kubectl get applications -n argocd
   
   # Check inference service
   kubectl get pods -n ml-inference-prod
   kubectl get pods -n ml-inference-staging
   ```

6. **Access ArgoCD UI**:
   ```bash
   # Port forward to ArgoCD server
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   
   # Access at https://localhost:8080
   # Default username: admin
   # Get password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```

## 📁 Repository Structure

```
.
├── argocd-root/                    # Root application (apply manually)
│   └── root-application.yaml      # Mother application
│
├── bootstrap/                      # Application orchestration
│   ├── apps/                      # ApplicationSets
│   │   ├── ml-recommendation-inference.yaml
│   │   └── ml-training-workflow-circle.yaml
│   ├── platform/                  # Platform components
│   │   ├── logging-app.yaml
│   │   └── monitoring-app.yaml
│   └── kustomization.yaml
│
├── apps/                          # Application definitions
│   ├── ml-recommendation-inference/
│   │   ├── base/                  # Base configuration
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   ├── serviceaccount.yaml
│   │   │   └── kustomization.yaml
│   │   └── overlays/              # Environment overlays
│   │       ├── production/
│   │       └── staging/
│   └── ml-training-workflow-circle/
│       ├── base/
│       │   ├── workflow-template.yaml
│       │   ├── cron-workflow.yaml
│       │   └── kustomization.yaml
│       └── overlays/
│           ├── production/
│           └── staging/
│
├── config/                        # Global configuration
│   ├── defaults/
│   │   └── image-registry.yaml
│   └── environments/
│       ├── production.yaml
│       └── staging.yaml
│
├── manifests/                     # Platform infrastructure
│   ├── monitoring/
│   └── logging/
│
├── policy/                        # ArgoCD policies
│   └── sync-policy.yaml
│
└── docs/                          # Documentation
    ├── architecture.md
    ├── change-management.md
    └── ...
```

## 📦 Applications

### 1. ML Recommendation Inference

**Purpose**: Deploy inference service for real-time model predictions.

**Components**:
- Deployment with configurable replicas
- Service (ClusterIP)
- ConfigMap for configuration
- ServiceAccount with IRSA for AWS access

**Environments**:
- **Production**: Optimized for t3.micro, 1 replica, production IAM role
- **Staging**: 1 replica, staging IAM role

**Configuration**:
```yaml
# Production overlay
apps/ml-recommendation-inference/overlays/production/kustomization.yaml
```

**Endpoints**:
- Health: `GET /healthz`
- Predict: `POST /predict`

### 2. ML Training Workflow Circle

**Purpose**: Orchestrate ML training pipeline using Argo Workflows.

**Components**:
- WorkflowTemplate: Reusable training pipeline
- CronWorkflow: Scheduled training runs
- ServiceAccount: IRSA for S3 and ECR access

**Pipeline Steps**:
1. Data Ingestion
2. Data Processing
3. Data EDA
4. Model Training

**Environments**:
- **Production**: Daily training schedule, production resources
- **Staging**: On-demand or weekly schedule, staging resources

**Configuration**:
```yaml
# Production overlay
apps/ml-training-workflow-circle/overlays/production/kustomization.yaml
```

## 🌍 Environments

### Production

- **Namespace**: `ml-inference-prod`, `ml-training-prod`
- **Replicas**: Optimized for cost (1 replica for inference)
- **Resources**: Resource limits tuned for t3.micro
- **IAM Roles**: Production IAM roles with least privilege
- **Image Tags**: `main-<sha>` (immutable tags)
- **Sync Policy**: Auto-sync with self-healing

### Staging

- **Namespace**: `ml-inference-staging`, `ml-training-staging`
- **Replicas**: 1 replica
- **Resources**: Similar to production for parity testing
- **IAM Roles**: Staging IAM roles
- **Image Tags**: `develop-<sha>` or `main-<sha>`
- **Sync Policy**: Auto-sync with self-healing

## 🔄 Deployment Workflow

### Manual Deployment

1. **Update image tag** in overlay:
   ```yaml
   # apps/ml-recommendation-inference/overlays/production/kustomization.yaml
   images:
     - name: inference
       newTag: main-ff798d6377ad24fce677ea3e9337bd0e168147af
   ```

2. **Commit and push**:
   ```bash
   git add apps/ml-recommendation-inference/overlays/production/kustomization.yaml
   git commit -m "chore: update inference image to main-ff798d6"
   git push origin main
   ```

3. **ArgoCD auto-syncs** (if enabled):
   - ArgoCD detects Git change
   - Automatically syncs application
   - Rolling update in Kubernetes

### Automated Deployment (CI/CD)

The ML platform CI/CD pipeline automatically:

1. **Builds Docker image** and pushes to ECR
2. **Updates GitOps repo** with new image tag
3. **Commits and pushes** to GitOps repository
4. **ArgoCD detects** change and syncs
5. **Kubernetes rolling update** with zero downtime

See [ML Platform Repository](../h&m_deeplearning) for CI/CD details.

### Sync Policies

**Auto-Sync** (Default):
- **Prune**: Delete resources removed from Git
- **Self-Heal**: Automatically correct drift
- **AllowEmpty**: Prevent empty applications

**Manual Sync** (if needed):
```bash
# Sync specific application
argocd app sync ml-recommendation-production-inference

# Sync all applications
argocd app sync --all
```

## ⚙️ Configuration

### Image Registry Configuration

Update ECR registry in overlays:

```yaml
# apps/ml-recommendation-inference/overlays/production/kustomization.yaml
images:
  - name: inference
    newName: 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/inference
    newTag: main-ff798d6377ad24fce677ea3e9337bd0e168147af
```

### Resource Configuration

Customize resources per environment:

```yaml
# Production overlay patches
patches:
  - patch: |-
      - op: replace
        path: /spec/replicas
        value: 1
      - op: replace
        path: /spec/template/spec/containers/0/resources/limits/cpu
        value: "1500m"
```

### IAM Roles (IRSA)

Configure AWS IAM roles for service accounts:

```yaml
# ServiceAccount annotation
metadata:
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/ml-inference-prod-role"
```

### Environment Variables

Configure via ConfigMap:

```yaml
# base/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-inference-config
data:
  LOG_LEVEL: "INFO"
  API_HOST: "0.0.0.0"
  API_PORT: "8080"
```

## 💻 Development

### Local Validation

1. **Validate YAML syntax**:
   ```bash
   # Install yamllint
   pip install yamllint
   
   # Validate all YAML files
   yamllint apps/ bootstrap/ argocd-root/
   ```

2. **Validate Kustomize builds**:
   ```bash
   # Build production overlay
   kustomize build apps/ml-recommendation-inference/overlays/production
   
   # Validate all overlays
   for overlay in apps/*/overlays/*/; do
     echo "Validating $overlay"
     kustomize build "$overlay" > /dev/null
   done
   ```

3. **Validate ArgoCD Applications**:
   ```bash
   # Dry-run apply
   kubectl apply --dry-run=client -f argocd-root/root-application.yaml
   ```

### Adding a New Application

1. **Create application structure**:
   ```bash
   mkdir -p apps/new-app/{base,overlays/{production,staging}}
   ```

2. **Create base resources**:
   - `base/deployment.yaml`
   - `base/service.yaml`
   - `base/kustomization.yaml`
   - Other resources as needed

3. **Create overlays**:
   - Environment-specific patches
   - Image overrides
   - Resource patches

4. **Create ApplicationSet**:
   ```yaml
   # bootstrap/apps/new-app.yaml
   apiVersion: argoproj.io/v1alpha1
   kind: ApplicationSet
   # ... application set definition
   ```

5. **Update bootstrap kustomization**:
   ```yaml
   # bootstrap/kustomization.yaml
   resources:
     - apps/new-app.yaml
   ```

### CI Pipeline

The `.github/workflows/validate-gitops.yaml` workflow:

- ✅ Validates YAML syntax
- ✅ Validates ArgoCD Application schemas
- ✅ Validates Kustomize builds
- ✅ Validates repository structure
- ✅ Checks for common issues

## 📝 Best Practices

### GitOps Principles

1. **Declarative Configuration**: All desired state in Git
2. **Single Source of Truth**: Git is the authoritative source
3. **Automated Sync**: ArgoCD handles deployment automatically
4. **Version Control**: All changes tracked in Git

### Configuration Management

1. **Use Kustomize Overlays**: DRY principle, separate base from environment
2. **Immutable Image Tags**: Use SHA-based tags, never `latest`
3. **Environment Parity**: Keep staging similar to production
4. **Resource Limits**: Always define requests and limits

### Security

1. **IRSA**: Use IAM Roles for Service Accounts, not access keys
2. **Least Privilege**: Minimum required permissions
3. **Secrets Management**: Use Sealed Secrets or External Secrets Operator
4. **Network Policies**: Implement network segmentation

### Sync Policies

1. **Auto-Sync**: Enable for non-critical applications
2. **Manual Sync**: Use for critical production deployments
3. **Self-Heal**: Enable to maintain desired state
4. **Prune**: Enable to clean up deleted resources

### Monitoring

1. **Health Checks**: Implement liveness and readiness probes
2. **Metrics**: Expose Prometheus metrics
3. **Logging**: Structured logging with correlation IDs
4. **Alerts**: Set up alerts for sync failures

## 🐛 Troubleshooting

### Application Not Syncing

1. **Check ArgoCD application status**:
   ```bash
   kubectl get application ml-recommendation-production-inference -n argocd -o yaml
   ```

2. **Check sync status**:
   ```bash
   argocd app get ml-recommendation-production-inference
   ```

3. **Check logs**:
   ```bash
   kubectl logs -n argocd deployment/argocd-application-controller
   ```

### Image Pull Errors

1. **Verify image exists in ECR**:
   ```bash
   aws ecr describe-images \
     --repository-name ml-fashion-recommender/inference \
     --image-ids imageTag=main-ff798d6
   ```

2. **Check IRSA configuration**:
   ```bash
   kubectl get serviceaccount ml-inference-sa -n ml-inference-prod -o yaml
   ```

3. **Verify ECR permissions**:
   - Service account IAM role needs `ecr:GetAuthorizationToken` and `ecr:BatchGetImage`

### Resource Quota Issues

1. **Check namespace quotas**:
   ```bash
   kubectl get resourcequota -n ml-inference-prod
   ```

2. **Check pod status**:
   ```bash
   kubectl describe pod <pod-name> -n ml-inference-prod
   ```

### Kustomize Build Failures

1. **Validate base**:
   ```bash
   kustomize build apps/ml-recommendation-inference/base
   ```

2. **Validate overlay**:
   ```bash
   kustomize build apps/ml-recommendation-inference/overlays/production
   ```

3. **Check for missing resources**:
   - Verify all referenced resources exist
   - Check image names match exactly

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Change Management](docs/change-management.md)
- [ECR Configuration](docs/ECR_CONFIGURATION.md)
- [Pod Optimization](docs/POD_OPTIMIZATION.md)
- [ArgoCD Sync Testing](docs/ARGOCD_SYNC_TEST.md)

## 🤝 Contributing

### Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** and validate:
   ```bash
   kustomize build apps/your-app/overlays/production
   ```

3. **Commit and push**:
   ```bash
   git commit -m "feat: add new application"
   git push origin feature/your-feature-name
   ```

4. **Create PR**: CI will validate changes automatically

### Code Review Process

1. All PRs require at least one approval
2. CI validation must pass
3. Kustomize builds must succeed
4. Documentation must be updated

## 🔗 Related Repositories

- [ML Platform](../h&m_deeplearning) - ML components and CI/CD
- [Infrastructure](../hm-infra-live) - Terraform infrastructure

## 📞 Support

For issues and questions:
- Create an issue in this repository
- Contact the Platform Engineering team
- Check documentation in `docs/` directory

---

**Built with ❤️ by the H&M Platform Engineering Team**

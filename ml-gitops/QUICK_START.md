# 🚀 Quick Start Guide

## Prerequisites

- Kubernetes cluster with ArgoCD installed
- Argo Workflows controller installed
- `kubectl` configured
- AWS ECR access (if using AWS)

## Step 1: Configure Repository

1. **Update Git Repository URL**:
   ```bash
   # Edit argocd-root/root-application.yaml
   # Replace: https://github.com/your-org/hm-mlops-gitops.git
   # With your actual repository URL
   ```

2. **Update Image Registry**:
   ```bash
   # Edit config/defaults/image-registry.yaml
   # Update baseURL and repoPrefix to match your ECR registry
   ```

3. **Update AWS Configuration**:
   ```bash
   # Edit config/environments/production.yaml
   # Edit config/environments/staging.yaml
   # Update accountId, region, and IAM role ARNs
   ```

## Step 2: Apply Root Application

```bash
kubectl apply -f argocd-root/root-application.yaml
```

## Step 3: Verify Deployment

1. **Check ArgoCD UI**:
   ```bash
   # Port forward ArgoCD server
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   
   # Access https://localhost:8080
   # Login with admin password:
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```

2. **Verify Applications**:
   - You should see `gitops-root` application
   - It should sync and create child applications:
     - `ml-recommendation-production-inference`
     - `ml-recommendation-staging-inference`
     - `ml-training-workflow-production-circle`
     - `ml-training-workflow-staging-circle`
     - `monitoring-platform`
     - `logging-platform`

## Step 4: Check Pods

```bash
# Production inference
kubectl get pods -n ml-inference-prod

# Staging inference
kubectl get pods -n ml-inference-staging

# Training workflows
kubectl get workflows -n ml-training-prod
```

## Step 5: Trigger Training Workflow

```bash
# Manual trigger
kubectl create -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: ml-training-manual-$(date +%s)
  namespace: ml-training-prod
spec:
  entrypoint: ml-training-pipeline
  workflowTemplateRef:
    name: ml-training-pipeline
EOF

# Or wait for scheduled cron (Monday 2 AM UTC)
```

## Troubleshooting

### Applications not syncing

```bash
# Check ArgoCD logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller --tail=100

# Check application status
kubectl get applications -n argocd
kubectl describe application <app-name> -n argocd
```

### Images not found

```bash
# Verify image exists in ECR
aws ecr describe-images --repository-name ml-fashion-recommender/inference --region ap-southeast-2

# Check image pull secrets
kubectl get secrets -n ml-inference-prod
```

### Workflows not running

```bash
# Check Argo Workflows controller
kubectl get pods -n argo

# Check workflow logs
kubectl logs <workflow-pod> -n ml-training-prod
```

## Next Steps

1. **Configure Monitoring**: Add Prometheus and Grafana manifests to `manifests/monitoring/`
2. **Setup Secrets**: Configure External Secrets Operator or Sealed Secrets
3. **Enable Image Updater**: Install ArgoCD Image Updater for automatic image updates
4. **Add More Environments**: Create development overlay if needed


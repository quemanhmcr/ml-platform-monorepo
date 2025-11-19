# 🔄 ArgoCD Sync Test - Monitoring Auto-Sync

**Test Started:** 2025-11-07  
**Code Change:** Inference v1.0.1 → v1.0.2  
**Change:** Added `sync_test` field to healthz endpoint

---

## 📋 Test Plan

1. ✅ **Code Change:** Updated inference service version to 1.0.2
2. ✅ **Commit & Push:** Pushed to main branch
3. ⏳ **GitHub Actions:** Build and push image to ECR
4. ⏳ **GitOps Update:** Workflow updates GitOps repo with new image tag
5. ⏳ **ArgoCD Sync:** ArgoCD detects change and syncs deployment
6. ⏳ **Pod Rollout:** New pod with updated image starts
7. ⏳ **API Test:** Verify new version is running

---

## ⏱️ Timeline Tracking

### Step 1: Code Push
- **Time:** [Will be filled after push]
- **Status:** ⏳ Pending

### Step 2: GitHub Actions Build
- **Expected Duration:** ~5-10 minutes
- **Status:** ⏳ Pending
- **Monitor:** GitHub Actions tab

### Step 3: GitOps Update
- **Expected Duration:** ~1-2 minutes after build
- **Status:** ⏳ Pending
- **Monitor:** GitOps repo commit history

### Step 4: ArgoCD Detection
- **Expected Duration:** ~1-3 minutes (ArgoCD refresh interval)
- **Status:** ⏳ Pending
- **Monitor:** ArgoCD Application status

### Step 5: ArgoCD Sync
- **Expected Duration:** ~1-2 minutes
- **Status:** ⏳ Pending
- **Monitor:** ArgoCD sync status

### Step 6: Pod Rollout
- **Expected Duration:** ~2-5 minutes (image pull + startup)
- **Status:** ⏳ Pending
- **Monitor:** Pod status

### Step 7: API Verification
- **Expected Duration:** ~1 minute
- **Status:** ⏳ Pending
- **Test:** Healthz endpoint should show v1.0.2

**Total Expected Time:** ~10-20 minutes end-to-end

---

## 🔍 Monitoring Commands

### Check GitHub Actions Status
```bash
# Check workflow runs (via GitHub CLI or web UI)
gh run list --workflow=build-inference-gitops.yml
```

### Check GitOps Repo Update
```bash
# Check latest commit in GitOps repo
cd e:\project\hm-mlops-gitops
git pull
git log --oneline -5
```

### Check ArgoCD Application Status
```bash
# Current sync status
kubectl get application ml-recommendation-production-inference -n argocd

# Detailed status
kubectl get application ml-recommendation-production-inference -n argocd -o yaml | grep -A 10 "sync:"

# Watch for changes
kubectl get application ml-recommendation-production-inference -n argocd -w
```

### Check Pod Status
```bash
# Current pods
kubectl get pods -n ml-inference-prod -o wide

# Watch pod changes
kubectl get pods -n ml-inference-prod -w

# Check pod image
kubectl get pod <pod-name> -n ml-inference-prod -o jsonpath='{.spec.containers[0].image}'
```

### Check Deployment Status
```bash
# Deployment status
kubectl get deployment ml-recommendation-inference -n ml-inference-prod

# Deployment events
kubectl describe deployment ml-recommendation-inference -n ml-inference-prod
```

### Test API
```bash
# Port forward
kubectl port-forward -n ml-inference-prod svc/ml-recommendation-inference 8081:80

# Test healthz (should show v1.0.2 and sync_test field)
curl http://localhost:8081/healthz

# Expected response:
# {
#   "status": "ok",
#   "service": "inference",
#   "version": "1.0.2",
#   "timestamp": "...",
#   "deployed": true,
#   "sync_test": "ArgoCD auto-sync verified"
# }
```

---

## 📊 Expected Results

### ArgoCD Application
- **Sync Status:** Should change from "Synced" → "OutOfSync" → "Synced"
- **Health Status:** Should remain "Healthy" (or briefly "Degraded" during rollout)
- **Revision:** Should update to new GitOps commit SHA

### Pods
- **Old Pod:** Should be terminated
- **New Pod:** Should start with new image tag
- **Image Tag:** Should contain new SHA from main branch

### API Response
- **Version:** Should be "1.0.2"
- **sync_test field:** Should be present with value "ArgoCD auto-sync verified"

---

## ⚠️ Troubleshooting

### If ArgoCD doesn't detect changes:
1. Check ArgoCD refresh interval (default: 3 minutes)
2. Manually refresh: `kubectl patch application ml-recommendation-production-inference -n argocd --type merge -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{"revision":"HEAD"}}}'`

### If sync fails:
1. Check ArgoCD logs: `kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller`
2. Check GitOps repo: Ensure image tag was updated correctly
3. Check image exists in ECR: `aws ecr describe-images --repository-name ml-fashion-recommender/inference --region ap-southeast-2`

### If pod doesn't start:
1. Check image pull: `kubectl describe pod <pod-name> -n ml-inference-prod`
2. Check ECR permissions: Verify node group role has ECR read access
3. Check resources: Ensure pod slots are available

---

## 📝 Notes

- ArgoCD sync policy is set to `automated: true` with `selfHeal: true`
- Sync should happen automatically within 3-5 minutes of GitOps repo update
- Image tag format: `main-{full-sha}` (immutable)
- GitOps overlay uses this tag format in production

---

**Last Updated:** 2025-11-07  
**Test Status:** ⏳ In Progress


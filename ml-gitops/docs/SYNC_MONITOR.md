# 🔄 ArgoCD Sync Monitor - Real-time Tracking

**Test Started:** 2025-11-07  
**Code Change:** Inference v1.0.1 → v1.0.2  
**Commit:** ff798d6 - "test: Update inference to v1.0.2 - Testing ArgoCD auto-sync"

---

## ⏱️ Timeline

### ✅ Step 1: Code Push
- **Time:** ~09:58 (local time)
- **Commit:** ff798d6
- **Status:** ✅ Completed
- **Branch:** main

### ⏳ Step 2: GitHub Actions Build
- **Expected Duration:** 5-10 minutes
- **Status:** ⏳ Running (check GitHub Actions)
- **Monitor:** https://github.com/manhque-lab/ml-fashion-recommender/actions

### ⏳ Step 3: GitOps Update
- **Expected Duration:** 1-2 minutes after build completes
- **Status:** ⏳ Pending
- **Monitor:** GitOps repo commit history

### ⏳ Step 4: ArgoCD Detection
- **Current Revision:** `4bbcb6ce0e96e8f0493ed4f3938e5ef263221c53`
- **Expected:** ArgoCD refresh interval ~3 minutes
- **Status:** ⏳ Waiting for GitOps update

### ⏳ Step 5: ArgoCD Sync
- **Current Status:** Synced (with old revision)
- **Expected:** Will change to OutOfSync → Synced
- **Status:** ⏳ Pending

### ⏳ Step 6: Pod Rollout
- **Current Pod:** `ml-recommendation-inference-6fc55c6f9d-wz5mt`
- **Current Image:** `main-a0f13477eca7bfd3c908afdfff2fa18d1b6be5c0`
- **Expected Image:** `main-ff798d6...` (new SHA)
- **Status:** ⏳ Pending

---

## 🔍 Current Status

### ArgoCD Application
```bash
# Current sync status
kubectl get application ml-recommendation-production-inference -n argocd

# Current revision
kubectl get application ml-recommendation-production-inference -n argocd -o jsonpath='{.status.sync.revision}'
# Output: 4bbcb6ce0e96e8f0493ed4f3938e5ef263221c53 (OLD)

# Sync status
kubectl get application ml-recommendation-production-inference -n argocd -o jsonpath='{.status.sync.status}'
# Output: Synced (with old revision)
```

### Pod Status
```bash
# Current pods
kubectl get pods -n ml-inference-prod

# Current image
kubectl get pod ml-recommendation-inference-6fc55c6f9d-wz5mt -n ml-inference-prod -o jsonpath='{.spec.containers[0].image}'
# Output: 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/inference:main-a0f13477eca7bfd3c908afdfff2fa18d1b6be5c0
```

---

## 📊 Monitoring Commands

### Quick Status Check
```bash
# All-in-one status
echo "=== ArgoCD Application ==="
kubectl get application ml-recommendation-production-inference -n argocd -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,REVISION:.status.sync.revision,HEALTH:.status.health.status

echo "=== Pods ==="
kubectl get pods -n ml-inference-prod -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,IMAGE:.spec.containers[0].image

echo "=== Current Image Tag ==="
kubectl get pod -n ml-inference-prod -l app=ml-recommendation-inference -o jsonpath='{.items[0].spec.containers[0].image}' | grep -o 'main-[a-f0-9]*'
```

### Watch for Changes
```bash
# Watch ArgoCD application
kubectl get application ml-recommendation-production-inference -n argocd -w

# Watch pods
kubectl get pods -n ml-inference-prod -w

# Watch deployment
kubectl get deployment ml-recommendation-inference -n ml-inference-prod -w
```

### Check GitOps Repo
```bash
cd e:\project\hm-mlops-gitops
git pull
git log --oneline -5

# Check if image tag was updated
grep -r "main-ff798d6" apps/ml-recommendation-inference/overlays/production/
```

---

## ⚠️ Known Issues

### Issue 1: Health Check Path Mismatch
**Problem:** Deployment has `/ready` and `/health` but code only has `/healthz`

**Current State:**
- Deployment config: `/ready` (readiness), `/health` (liveness)
- Code: Only `/healthz` endpoint exists
- Result: Pod crashes due to failed health checks

**Fix Needed:** Update deployment.yaml to use `/healthz` for both probes

**Impact:** Pod cannot become Ready, causing CrashLoopBackOff

---

## 🎯 Expected Flow

1. **GitHub Actions** builds new image with tag `main-ff798d6...`
2. **GitHub Actions** updates GitOps repo with new image tag
3. **ArgoCD** detects change (within 3 minutes)
4. **ArgoCD** syncs deployment (1-2 minutes)
5. **Kubernetes** pulls new image and starts new pod
6. **New pod** should have image tag `main-ff798d6...`
7. **API test** should show version `1.0.2` and `sync_test` field

**Total Expected Time:** 10-20 minutes from code push

---

## ✅ Verification Steps

### After Sync Completes:

1. **Check ArgoCD Revision:**
   ```bash
   kubectl get application ml-recommendation-production-inference -n argocd -o jsonpath='{.status.sync.revision}'
   # Should be new GitOps commit SHA
   ```

2. **Check Pod Image:**
   ```bash
   kubectl get pod -n ml-inference-prod -l app=ml-recommendation-inference -o jsonpath='{.items[0].spec.containers[0].image}'
   # Should contain: main-ff798d6...
   ```

3. **Test API:**
   ```bash
   kubectl port-forward -n ml-inference-prod svc/ml-recommendation-inference 8081:80
   curl http://localhost:8081/healthz
   # Should show: "version": "1.0.2" and "sync_test": "ArgoCD auto-sync verified"
   ```

---

## 📝 Notes

- ArgoCD sync policy: `automated: true` with `selfHeal: true`
- ArgoCD refresh interval: ~3 minutes (default)
- Image tag format: `main-{full-sha}` (immutable)
- Health check issue needs to be fixed for pod to become Ready

---

**Last Check:** 2025-11-07 ~10:00  
**Next Check:** Monitor every 2-3 minutes


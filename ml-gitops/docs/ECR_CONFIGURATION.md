# 🔐 ECR Image Pull Configuration Analysis

**Ngày kiểm tra:** 2025-11-07  
**ECR Registry:** 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com

---

## 📋 Tổng Quan

Các deployment và workflow trong GitOps đang sử dụng images từ AWS ECR. File này phân tích cấu hình hiện tại và các vấn đề cần lưu ý.

---

## ✅ Cấu Hình Hiện Tại

### 1. Infrastructure (Terraform) - ✅ Đã Config Đúng

**File:** `hm-infra-live/main.tf`

```hcl
# ECR Repository Access Policy
data "aws_iam_policy_document" "ecr_read_only" {
  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
    ]
    resources = ["*"]
  }
}

# Attach ECR read policy to node group role
resource "aws_iam_role_policy" "node_group_ecr_access" {
  name   = "${var.project_name}-${var.environment}-ecr-read-only"
  role   = local.node_role_name
  policy = data.aws_iam_policy_document.ecr_read_only.json
}
```

**Phân tích:**
- ✅ Node group role đã có ECR read permissions
- ✅ Policy bao gồm tất cả actions cần thiết để pull images
- ✅ Resources = "*" cho phép access tất cả ECR repositories

**Kết luận:** Nodes có thể pull images từ ECR thông qua node group IAM role.

---

### 2. Deployment Configuration

#### ml-recommendation-inference

**Base Deployment:**
```yaml
spec:
  template:
    spec:
      serviceAccountName: ml-inference-sa
      containers:
        - name: inference
          image: inference:latest  # Overridden by overlay
          imagePullPolicy: Always
```

**Production Overlay:**
```yaml
images:
  - name: inference
    newName: 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/inference
    newTag: main-a0f13477eca7bfd3c908afdfff2fa18d1b6be5c0
```

**ServiceAccount:**
```yaml
metadata:
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/ml-inference-prod-role"
```

**Phân tích:**
- ✅ Image được override đúng với ECR registry
- ✅ Image tag cụ thể (immutable)
- ⚠️ **Vấn đề:** IRSA role ARN có account ID sai (123456789012 thay vì 465002806239)
- ✅ Không có `imagePullSecrets` - đúng vì dùng node role

#### ml-training-workflow-circle

**WorkflowTemplate:**
```yaml
templates:
  - name: data-ingestion
    container:
      image: # Will be overridden by overlays
```

**Production Overlay:**
```yaml
images:
  - name: data-ingestion
    newName: 123456789012.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/data_ingestion
    newTag: main-latest
```

**Phân tích:**
- ⚠️ **Vấn đề:** ECR registry có account ID sai (123456789012 thay vì 465002806239)
- ⚠️ **Vấn đề:** Image tag là "main-latest" (mutable) thay vì immutable tag

---

## ⚠️ Vấn Đề Phát Hiện

### 1. Account ID Không Khớp

**Vấn đề:**
- ECR registry thực tế: `465002806239.dkr.ecr.ap-southeast-2.amazonaws.com`
- Config trong overlays: `123456789012.dkr.ecr.ap-southeast-2.amazonaws.com` (placeholder)

**Files bị ảnh hưởng:**
- `apps/ml-recommendation-inference/overlays/production/kustomization.yaml` - IRSA role ARN
- `apps/ml-training-workflow-circle/overlays/production/kustomization.yaml` - Image registry
- `apps/ml-training-workflow-circle/overlays/staging/kustomization.yaml` - Image registry

**Impact:**
- ⚠️ IRSA role ARN sai → IRSA không hoạt động (nhưng không ảnh hưởng image pull vì dùng node role)
- ⚠️ Image registry sai → Pods sẽ không thể pull images nếu dùng account ID sai

**Giải pháp:**
Cần cập nhật tất cả account IDs từ `123456789012` → `465002806239`

---

### 2. Image Pull Mechanism

**Hiện tại:**
- ✅ **Node Group Role:** Có ECR permissions → Nodes có thể pull images
- ⚠️ **IRSA Role:** Account ID sai → IRSA không hoạt động (nhưng không cần cho image pull)

**Cơ chế hoạt động:**
1. Kubelet trên nodes sử dụng node group IAM role để authenticate với ECR
2. AWS ECR plugin tự động refresh token mỗi 12 giờ
3. Không cần `imagePullSecrets` khi dùng node role

**Kết luận:** Image pull sẽ hoạt động với node role, nhưng cần fix account ID trong image URLs.

---

### 3. Image Tags

**Vấn đề:**
- Production inference: ✅ Dùng immutable tag (SHA-based)
- Training workflows: ⚠️ Dùng mutable tag "main-latest"

**Khuyến nghị:**
- Nên dùng immutable tags (SHA hoặc commit hash) cho production
- Mutable tags có thể gây ra inconsistency giữa các environments

---

## 🔧 Cấu Hình Cần Kiểm Tra

### 1. ECR Repository Tồn Tại

**Cần verify:**
```bash
# Kiểm tra ECR repositories
aws ecr describe-repositories --region ap-southeast-2

# Kiểm tra images trong repository
aws ecr list-images --repository-name ml-fashion-recommender/inference --region ap-southeast-2
aws ecr list-images --repository-name ml-fashion-recommender/data_ingestion --region ap-southeast-2
aws ecr list-images --repository-name ml-fashion-recommender/data_processing --region ap-southeast-2
aws ecr list-images --repository-name ml-fashion-recommender/data_eda --region ap-southeast-2
aws ecr list-images --repository-name ml-fashion-recommender/train --region ap-southeast-2
```

### 2. Node Group Role Permissions

**Đã config trong Terraform:**
- ✅ ECR read permissions đã được attach
- ✅ Policy đúng với các actions cần thiết

**Verify:**
```bash
# Kiểm tra IAM role policies
aws iam list-role-policies --role-name ml-fashion-recommender-infra-live-role-iam
aws iam get-role-policy --role-name ml-fashion-recommender-infra-live-role-iam --policy-name ml-fashion-recommender-production-ecr-read-only
```

### 3. IRSA Configuration (Optional)

**Nếu muốn dùng IRSA thay vì node role:**

1. **Tạo IAM role cho ServiceAccount:**
   ```bash
   # Role cần có trust relationship với EKS OIDC provider
   # Và ECR read permissions
   ```

2. **Update ServiceAccount với đúng role ARN:**
   ```yaml
   metadata:
     annotations:
       eks.amazonaws.com/role-arn: "arn:aws:iam::465002806239:role/ml-inference-prod-role"
   ```

3. **Lợi ích:**
   - Fine-grained permissions per workload
   - Better security isolation
   - Không cần node role có ECR permissions

**Hiện tại:** Không cần thiết vì node role đã có ECR permissions.

---

## ✅ Checklist ECR Configuration

### Infrastructure (Terraform)
- [x] Node group role có ECR read permissions
- [x] Policy bao gồm đầy đủ actions
- [x] Policy được attach vào node role

### GitOps Configuration
- [ ] **Cần fix:** Account ID trong image URLs (123456789012 → 465002806239)
- [ ] **Cần fix:** Account ID trong IRSA role ARNs (nếu muốn dùng IRSA)
- [x] Image tags được override đúng trong overlays
- [x] Không có imagePullSecrets (đúng vì dùng node role)

### ECR Repositories
- [ ] Verify repositories tồn tại
- [ ] Verify images có trong repositories
- [ ] Verify image tags tồn tại

---

## 🔧 Actions Cần Thực Hiện

### Priority 1: Fix Account IDs

**1. Update Production Inference Overlay:**
```yaml
# apps/ml-recommendation-inference/overlays/production/kustomization.yaml
images:
  - name: inference
    newName: 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/inference
    # ✅ Đã đúng

patches:
  - patch: |-
      - op: replace
        path: /metadata/annotations/eks.amazonaws.com~1role-arn
        value: "arn:aws:iam::465002806239:role/ml-inference-prod-role"  # Fix account ID
```

**2. Update Training Workflow Overlays:**
```yaml
# apps/ml-training-workflow-circle/overlays/production/kustomization.yaml
images:
  - name: data-ingestion
    newName: 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/data_ingestion
    # Fix account ID từ 123456789012 → 465002806239
  
  - name: data-processing
    newName: 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/data_processing
  
  - name: data-eda
    newName: 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/data_eda
  
  - name: train-model
    newName: 465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/train
```

**3. Update Staging Overlays (nếu cần):**
- Tương tự như production

### Priority 2: Verify ECR Repositories

```bash
# List all repositories
aws ecr describe-repositories --region ap-southeast-2

# Check specific repository
aws ecr describe-images \
  --repository-name ml-fashion-recommender/inference \
  --region ap-southeast-2 \
  --image-ids imageTag=main-a0f13477eca7bfd3c908afdfff2fa18d1b6be5c0
```

### Priority 3: Test Image Pull

```bash
# Test pull image từ một node
kubectl run test-ecr-pull --image=465002806239.dkr.ecr.ap-southeast-2.amazonaws.com/ml-fashion-recommender/inference:main-a0f13477eca7bfd3c908afdfff2fa18d1b6be5c0 --rm -it --restart=Never -- /bin/sh

# Hoặc check events khi pod được tạo
kubectl get events --field-selector involvedObject.name=test-ecr-pull
```

---

## 📝 Notes

1. **Image Pull không phải nguyên nhân của lỗi hiện tại:**
   - Pods đang Pending do scheduling issues (không đủ resources)
   - Không có ImagePullBackOff errors
   - Vấn đề là pod density và memory constraints

2. **IRSA Role ARN sai không ảnh hưởng image pull:**
   - Image pull dùng node group role (đã có ECR permissions)
   - IRSA chỉ cần cho application access AWS services (S3, Secrets Manager, etc.)

3. **Cần fix account IDs để:**
   - Đảm bảo consistency
   - Tránh lỗi khi pods thực sự được schedule
   - Đảm bảo IRSA hoạt động đúng (nếu cần)

---

## 🔗 Related Documentation

- [AWS ECR Authentication](https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html)
- [EKS IAM Roles for Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [Kubernetes Image Pull Secrets](https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod)

---

**Last Updated:** 2025-11-07  
**Status:** ⚠️ Cần fix account IDs trong GitOps configs


# 🔧 Pod Optimization Analysis - Giải Phóng Chỗ Cho ArgoCD Deployments

**Ngày phân tích:** 2025-11-07  
**Mục tiêu:** Tối ưu system pods để giải phóng pod slots cho application deployments

---

## 📊 Hiện Trạng Pod Distribution

### Pod Count per Node

| Node | System Pods | ArgoCD Pods | Total | Status |
|------|-------------|-------------|-------|--------|
| ip-10-0-1-82 | 4 (aws-node, kube-proxy, ebs-csi-node, coredns) | 1 (applicationset-controller) | **5** | ⚠️ **Vượt giới hạn** |
| ip-10-0-1-122 | 3 (aws-node, kube-proxy, ebs-csi-node) | 1 (applicationset-controller) | 4 | ✅ At limit |
| ip-10-0-2-117 | 3 (aws-node, kube-proxy, ebs-csi-node) | 1 (repo-server) | 4 | ✅ At limit |
| ip-10-0-2-231 | 3 (aws-node, kube-proxy, ebs-csi-node) | 1 (application-controller) | 4 | ✅ At limit |
| ip-10-0-3-13 | 3 (aws-node, kube-proxy, ebs-csi-node) | 1 (redis) | 4 | ✅ At limit |
| ip-10-0-3-87 | 3 (aws-node, kube-proxy, ebs-csi-node) | 1 (server) | 4 | ✅ At limit |

**Tổng kết:**
- **Total System Pods:** 19 pods
- **Total ArgoCD Pods:** 5 pods
- **Total Running:** 24 pods
- **Pending Application Pods:** 4 pods (không thể schedule)

### Chi Tiết System Pods

#### DaemonSets (Required trên mỗi node)

| Component | Pods | Containers/Pod | CPU Request | Memory Request | Status |
|-----------|------|----------------|-------------|----------------|--------|
| **aws-node** | 6 | 2 | 25m x 2 = 50m | - | ✅ **Required** |
| **kube-proxy** | 6 | 1 | 100m | - | ✅ **Required** |
| **ebs-csi-node** | 6 | 3 | 10m x 3 = 30m | 40Mi x 3 = 120Mi | ⚠️ **Có thể tối ưu** |

#### Deployments

| Component | Replicas | CPU Request | Memory Request | Status |
|-----------|----------|-------------|----------------|--------|
| **coredns** | 1 | 100m | 70Mi | ✅ Đã scale down |
| **ebs-csi-controller** | 0 | - | - | ✅ Đã scale down |

---

## ⚠️ Vấn Đề Phát Hiện

### 1. Node ip-10-0-1-82 Vượt Giới Hạn Pods

**Vấn đề:**
- Node này có **5 pods** trong khi t3.micro chỉ hỗ trợ tối đa **4 pods/node**
- Pods trên node này:
  1. aws-node-7fmjh (daemonset)
  2. kube-proxy-r9kn7 (daemonset)
  3. ebs-csi-node-sp7rk (daemonset)
  4. coredns-58d7b66669-xllnv (deployment)
  5. argocd-applicationset-controller (deployment)

**Nguyên nhân:**
- Coredns pod được schedule vào node này
- ArgoCD applicationset-controller cũng được schedule vào node này
- Cả hai đều là deployment pods (có thể di chuyển)

### 2. ebs-csi-node Chiếm Nhiều Resources

**Vấn đề:**
- Mỗi ebs-csi-node pod có **3 containers** (driver, registrar, liveness-probe)
- Chiếm **30m CPU** và **120Mi memory** mỗi node
- Tổng cộng: **180m CPU** và **720Mi memory** trên 6 nodes

**Phân tích:**
- ebs-csi-node là daemonset → chạy trên tất cả nodes
- Cần thiết nếu sử dụng EBS volumes
- Nhưng có thể tối ưu bằng cách chỉ chạy trên một số nodes nhất định

---

## 💡 Giải Pháp Đề Xuất

### Priority 1: Di Chuyển Coredns Pod (Immediate)

**Vấn đề:** Coredns pod đang ở node ip-10-0-1-82 (đã có 5 pods)

**Giải pháp:** Sử dụng node affinity để di chuyển coredns sang node khác

```bash
# Kiểm tra node có ít pods nhất
kubectl get pods --all-namespaces -o wide | findstr "ip-10-0-1-122"

# Patch coredns deployment với node affinity
kubectl patch deployment coredns -n kube-system -p '{"spec":{"template":{"spec":{"affinity":{"nodeAffinity":{"preferredDuringSchedulingIgnoredDuringExecution":[{"preference":{"matchExpressions":[{"key":"kubernetes.io/hostname","operator":"NotIn","values":["ip-10-0-1-82.ap-southeast-2.compute.internal"]}]},"weight":100}]}}}}}}'
```

**Hoặc scale down và scale up lại:**
```bash
kubectl scale deployment coredns -n kube-system --replicas=0
kubectl scale deployment coredns -n kube-system --replicas=1
```

**Impact:** Giải phóng 1 pod slot trên node ip-10-0-1-82

---

### Priority 2: Tối Ưu ebs-csi-node DaemonSet (High Impact)

**Option A: Giảm số lượng ebs-csi-node pods bằng node selector**

**Phân tích:**
- EBS CSI driver cần chạy trên nodes có EBS volumes
- Với t3.micro và không có persistent volumes, có thể chỉ cần 2-3 pods thay vì 6

**Giải pháp:** Sử dụng node selector để chỉ chạy trên một số nodes

```bash
# Patch ebs-csi-node daemonset với node selector
kubectl patch daemonset ebs-csi-node -n kube-system -p '{"spec":{"template":{"spec":{"nodeSelector":{"ebs-csi":"enabled"}}}}}'

# Label chỉ 2-3 nodes để chạy ebs-csi-node
kubectl label nodes ip-10-0-1-122.ap-southeast-2.compute.internal ebs-csi=enabled
kubectl label nodes ip-10-0-2-117.ap-southeast-2.compute.internal ebs-csi=enabled
kubectl label nodes ip-10-0-3-13.ap-southeast-2.compute.internal ebs-csi=enabled

# Unlabel các nodes khác
kubectl label nodes ip-10-0-1-82.ap-southeast-2.compute.internal ebs-csi-
kubectl label nodes ip-10-0-2-231.ap-southeast-2.compute.internal ebs-csi-
kubectl label nodes ip-10-0-3-87.ap-southeast-2.compute.internal ebs-csi-
```

**Impact:** 
- Giảm từ 6 pods → 3 pods
- Giải phóng **3 pod slots** trên 3 nodes
- Giải phóng **180m CPU** và **360Mi memory**

**Lưu ý:** 
- Chỉ làm nếu không sử dụng EBS volumes trên tất cả nodes
- Nếu cần EBS volumes, phải đảm bảo nodes có label `ebs-csi=enabled`

---

**Option B: Giảm số containers trong ebs-csi-node (Không khuyến nghị)**

- Phức tạp và có thể ảnh hưởng đến functionality
- Không nên làm trừ khi thực sự cần thiết

---

### Priority 3: Tối Ưu ArgoCD Pod Distribution

**Hiện tại:** ArgoCD pods được phân bổ đều trên các nodes

**Đề xuất:** Sử dụng pod anti-affinity để tránh tập trung trên một node

```yaml
# Thêm vào ArgoCD Helm values
controller:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app.kubernetes.io/name
              operator: In
              values:
              - argocd-application-controller
          topologyKey: kubernetes.io/hostname
```

**Impact:** Đảm bảo ArgoCD pods không tập trung trên một node

---

### Priority 4: Scale Down Staging Deployments

**Hiện tại:** Staging deployments đang Pending

**Giải pháp:** Xóa staging deployments để giải phóng resources

```bash
# Xóa staging deployments (đã disabled trong ApplicationSet)
kubectl delete deployment ml-recommendation-inference -n ml-inference-staging
```

**Impact:** Giải phóng 2 pending pods (không chiếm slot nhưng đang chờ)

---

## 📋 Action Plan

### Immediate Actions (Làm ngay)

1. ✅ **Di chuyển coredns pod**
   ```bash
   kubectl scale deployment coredns -n kube-system --replicas=0
   kubectl scale deployment coredns -n kube-system --replicas=1
   ```
   **Expected:** Giải phóng 1 pod slot trên node ip-10-0-1-82

2. ✅ **Xóa staging deployments**
   ```bash
   kubectl delete deployment ml-recommendation-inference -n ml-inference-staging
   ```
   **Expected:** Xóa 2 pending pods

### Short-term Actions (Trong tuần này)

3. ✅ **Tối ưu ebs-csi-node (Option A)**
   - Label 3 nodes với `ebs-csi=enabled`
   - Patch daemonset với node selector
   - **Expected:** Giải phóng 3 pod slots

4. ✅ **Verify và test**
   - Kiểm tra application pods có thể schedule không
   - Monitor node resources

### Long-term Actions (Trong tháng này)

5. ✅ **Upgrade node instance type**
   - Từ t3.micro → t3.small hoặc t3.medium
   - **Expected:** Tăng pod capacity từ 4 → 11 hoặc 17 pods/node

---

## 🎯 Expected Results

### Sau khi áp dụng Immediate + Short-term Actions:

**Pod Distribution:**
- **ebs-csi-node:** 6 pods → 3 pods (-3 pods)
- **coredns:** Di chuyển sang node khác (giải phóng 1 slot)
- **Staging:** Xóa 2 pending pods

**Total Pod Slots Freed:** ~4-5 pod slots

**Nodes có thể schedule thêm pods:**
- ip-10-0-1-82: 5 pods → 4 pods (sau khi di chuyển coredns)
- ip-10-0-1-122: 4 pods → 3 pods (sau khi giảm ebs-csi-node)
- ip-10-0-2-117: 4 pods → 3 pods (sau khi giảm ebs-csi-node)
- ip-10-0-3-13: 4 pods → 3 pods (sau khi giảm ebs-csi-node)

**Kết quả:** Có thể schedule ít nhất **1 production inference pod**

---

## ⚠️ Lưu Ý Quan Trọng

### ebs-csi-node Optimization

**Trước khi giảm ebs-csi-node pods:**

1. **Kiểm tra EBS volumes:**
   ```bash
   kubectl get pv
   kubectl get pvc --all-namespaces
   ```

2. **Kiểm tra workloads sử dụng EBS:**
   ```bash
   kubectl get pods --all-namespaces -o json | ConvertFrom-Json | 
     ForEach-Object { $_.items | Where-Object { $_.spec.volumes -match "persistentVolumeClaim" } }
   ```

3. **Nếu có EBS volumes:**
   - Đảm bảo nodes có label `ebs-csi=enabled` có thể access volumes
   - Hoặc không giảm ebs-csi-node pods

### Coredns Relocation

**Sau khi di chuyển coredns:**
- Verify DNS resolution vẫn hoạt động
- Monitor coredns metrics

---

## 🔧 Commands Reference

### Check Current Pod Distribution
```bash
# Pods per node
kubectl get pods --all-namespaces -o wide | Group-Object { $_.NODE } | 
  Select-Object Name, Count

# Detailed view
kubectl get pods --all-namespaces -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,NAMESPACE:.metadata.namespace
```

### Optimize ebs-csi-node
```bash
# Label nodes
kubectl label nodes <node-name> ebs-csi=enabled

# Patch daemonset
kubectl patch daemonset ebs-csi-node -n kube-system -p '{"spec":{"template":{"spec":{"nodeSelector":{"ebs-csi":"enabled"}}}}}'

# Verify
kubectl get pods -n kube-system -l app=ebs-csi-node -o wide
```

### Relocate Coredns
```bash
# Scale down and up
kubectl scale deployment coredns -n kube-system --replicas=0
kubectl scale deployment coredns -n kube-system --replicas=1

# Check new location
kubectl get pods -n kube-system -l k8s-app=kube-dns -o wide
```

---

## 📊 Monitoring

### After Optimization

```bash
# Check pod distribution
kubectl get pods --all-namespaces -o wide | Group-Object { $_.NODE }

# Check pending pods
kubectl get pods --all-namespaces --field-selector=status.phase=Pending

# Check node resources
kubectl describe nodes | Select-String -Pattern "Allocated resources" -Context 5
```

---

**Last Updated:** 2025-11-07  
**Status:** ⚠️ Cần thực hiện optimization để giải phóng pod slots


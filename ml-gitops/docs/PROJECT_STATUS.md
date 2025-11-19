# 📊 Trạng Thái Dự Án ML Fashion Recommender

**Ngày cập nhật:** 2025-11-07  
**Cluster:** ml-fashion-recommender-cluster  
**Region:** ap-southeast-2

---

## 🏗️ Infrastructure Overview

### EKS Cluster
- **Cluster Name:** ml-fashion-recommender-cluster
- **Kubernetes Version:** v1.28.15-eks-113cf36
- **Endpoint:** `https://AA30EB9CB7C3DA0CF5D718B57BF5BD9A.gr7.ap-southeast-2.eks.amazonaws.com`
- **Status:** ✅ Running

### Node Groups
- **Instance Type:** t3.micro
- **Node Count:** 6 nodes
- **Node Group:** general
- **Capacity Type:** ON_DEMAND
- **OS:** Amazon Linux 2
- **Kernel:** 5.10.245-241.976.amzn2.x86_64
- **Container Runtime:** containerd://1.7.27

#### Node Details
| Node Name | Status | Internal IP | Age |
|-----------|--------|-------------|-----|
| ip-10-0-1-122.ap-southeast-2.compute.internal | Ready | 10.0.1.122 | 56m |
| ip-10-0-1-82.ap-southeast-2.compute.internal | Ready | 10.0.1.82 | 56m |
| ip-10-0-2-117.ap-southeast-2.compute.internal | Ready | 10.0.2.117 | 56m |
| ip-10-0-2-231.ap-southeast-2.compute.internal | Ready | 10.0.2.231 | 56m |
| ip-10-0-3-13.ap-southeast-2.compute.internal | Ready | 10.0.3.13 | 56m |
| ip-10-0-3-87.ap-southeast-2.compute.internal | Ready | 10.0.3.87 | 56m |

#### Node Resources
- **CPU Allocatable:** ~1930m per node (2 vCPU total)
- **Memory Allocatable:** ~541MB per node (very limited)
- **Ephemeral Storage:** ~18GB per node

### VPC & Networking
- **VPC CIDR:** 10.0.0.0/16
- **Private Subnets:** 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24
- **Public Subnets:** 10.0.101.0/24, 10.0.102.0/24, 10.0.103.0/24
- **Availability Zones:** 3 AZs
- **NAT Gateway:** Single (staging optimization)

### EKS Addons
- ✅ CoreDNS (scaled to 1 replica)
- ✅ kube-proxy
- ✅ vpc-cni (AWS VPC CNI)
- ✅ aws-ebs-csi-driver (scaled to 1 replica controller)

---

## 🔄 ArgoCD Status

### ArgoCD Installation
- **Namespace:** argocd
- **Version:** 7.6.0 (Helm chart)
- **Status:** ✅ Running
- **Service Type:** LoadBalancer
- **Insecure Mode:** Enabled

### ArgoCD Components
| Component | Pods | Status | Age |
|-----------|------|--------|-----|
| argocd-application-controller | 1/1 | Running | 55m |
| argocd-applicationset-controller | 1/1 | Running | 55m |
| argocd-redis | 1/1 | Running | 55m |
| argocd-repo-server | 1/1 | Running | 55m |
| argocd-server | 1/1 | Running | 55m |

### Root Application
- **Name:** gitops-root
- **Namespace:** argocd
- **Sync Status:** ✅ Synced
- **Health Status:** ✅ Healthy
- **Repository:** https://github.com/manhque-lab/ml-fashion-recommender-gitops
- **Path:** bootstrap
- **Revision:** 4bbcb6ce0e96e8f0493ed4f3938e5ef263221c53

---

## 📦 ApplicationSets

### 1. ml-recommendation-inference
- **Name:** ml-recommendation-inference
- **Namespace:** argocd
- **Age:** 29m
- **Status:** ✅ Active

**Generated Applications:**
- `ml-recommendation-production-inference` (production)
- `ml-recommendation-staging-inference` (staging) - Currently disabled in ApplicationSet

### 2. ml-training-workflow-circle
- **Name:** ml-training-workflow-circle
- **Namespace:** argocd
- **Age:** 29m
- **Status:** ✅ Active

**Generated Applications:**
- `ml-training-workflow-production-circle` (production)
- `ml-training-workflow-staging-circle` (staging) - Currently disabled in ApplicationSet

---

## 🚀 Applications Status

| Application Name | Sync Status | Health Status | Namespace | Age |
|------------------|-------------|---------------|-----------|-----|
| gitops-root | ✅ Synced | ✅ Healthy | argocd | - |
| logging-platform | ✅ Synced | ✅ Healthy | - | - |
| monitoring-platform | ✅ Synced | ✅ Healthy | - | - |
| ml-recommendation-production-inference | ✅ Synced | ⚠️ Degraded | ml-inference-prod | 33m |
| ml-recommendation-staging-inference | ✅ Synced | ⚠️ Degraded | ml-inference-staging | 33m |
| ml-training-workflow-production-circle | ⚠️ OutOfSync | ✅ Healthy | ml-training-prod | - |
| ml-training-workflow-staging-circle | ⚠️ OutOfSync | ✅ Healthy | ml-training-staging | - |

---

## 🐳 Pods Status

### System Pods (kube-system)
| Component | Pods Running | Status |
|-----------|--------------|--------|
| aws-node | 6/6 | ✅ Running (1 per node) |
| kube-proxy | 6/6 | ✅ Running (1 per node) |
| ebs-csi-node | 6/6 | ✅ Running (1 per node) |
| coredns | 1/1 | ✅ Running |
| ebs-csi-controller | 0/0 | ⚠️ Scaled down |

**Total System Pods:** 19 pods running

### Application Pods

#### ml-inference-prod Namespace
| Pod Name | Status | Ready | Age | Issue |
|----------|--------|-------|-----|-------|
| ml-recommendation-inference-574446886b-xvlh2 | ⚠️ Pending | 0/1 | 27m | Cannot schedule |
| ml-recommendation-inference-6fc55c6f9d-zdbpz | ⚠️ Pending | 0/1 | 17m | Cannot schedule |

**Deployment Status:**
- **Desired:** 1
- **Available:** 0
- **Ready:** 0/1

#### ml-inference-staging Namespace
| Pod Name | Status | Ready | Age | Issue |
|----------|--------|-------|-----|-------|
| ml-recommendation-inference-68877c9d78-89dqr | ⚠️ Pending | 0/1 | 33m | Cannot schedule |
| ml-recommendation-inference-68877c9d78-xhsqn | ⚠️ Pending | 0/1 | 33m | Cannot schedule |

**Deployment Status:**
- **Desired:** 2
- **Available:** 0
- **Ready:** 0/2

---
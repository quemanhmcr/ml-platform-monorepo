# H&M ML Platform - Infrastructure as Code

> Enterprise-grade Terraform infrastructure for ML Fashion Recommender platform on AWS EKS

[![Terraform](https://img.shields.io/badge/Terraform-1.5+-blue.svg)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-EKS-orange.svg)](https://aws.amazon.com/eks/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-green.svg)](https://kubernetes.io/)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Infrastructure Components](#infrastructure-components)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Security](#security)
- [Operations](#operations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This repository contains Terraform code to provision and manage AWS infrastructure for the ML Fashion Recommender platform. It implements a production-ready EKS cluster with GitOps integration, following infrastructure-as-code best practices.

### Key Features

- 🏗️ **EKS Cluster**: Managed Kubernetes cluster with latest features
- 🌐 **VPC Networking**: Highly available VPC with public/private subnets
- 🔒 **Security**: KMS encryption, IRSA (IAM Roles for Service Accounts), private subnets
- 📦 **GitOps Ready**: Automatic ArgoCD installation and configuration
- 🔄 **Modular Design**: Reusable Terraform modules
- 📊 **Observability**: CloudWatch logging, cluster monitoring
- ⚡ **Auto-scaling**: Configurable node groups with auto-scaling
- 🛡️ **Network Security**: Security groups, NAT gateways, VPC endpoints

## 🏛️ Architecture

### Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Account                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                            VPC                                  │
│                      (10.0.0.0/16)                              │
│                                                                 │
│  ┌────────────────────┐          ┌────────────────────┐       │
│  │  Public Subnets    │          │  Private Subnets   │       │
│  │  (10.0.101.0/24)   │          │  (10.0.1.0/24)     │       │
│  │  - NAT Gateway     │◄─────────│  - EKS Nodes       │       │
│  │  - Load Balancers  │          │  - Pods            │       │
│  └────────────────────┘          └────────────────────┘       │
│           │                                │                    │
│           └────────────────┬───────────────┘                   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              EKS Cluster                                │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Control Plane (Managed by AWS)                  │  │   │
│  │  │  - API Server                                    │  │   │
│  │  │  - etcd                                          │  │   │
│  │  │  - Scheduler                                     │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Node Groups                                     │  │   │
│  │  │  - Managed Node Group (t3.medium)                │  │   │
│  │  │  - Auto-scaling (1-5 nodes)                      │  │   │
│  │  │  - IRSA enabled                                  │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Cluster Addons                                  │  │   │
│  │  │  - CoreDNS                                       │  │   │
│  │  │  - kube-proxy                                    │  │   │
│  │  │  - VPC CNI                                       │  │   │
│  │  │  - EBS CSI Driver                                │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ArgoCD (GitOps)                                        │   │
│  │  - Automatic installation via Helm                      │   │
│  │  - Root Application configured                          │   │
│  │  - GitOps repository integration                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Component Overview

1. **VPC**: Isolated network environment with public/private subnets
2. **EKS Cluster**: Managed Kubernetes control plane
3. **Node Groups**: Managed worker nodes with auto-scaling
4. **ArgoCD**: GitOps operator for declarative deployments
5. **IRSA**: IAM Roles for Service Accounts (no access keys)
6. **Security**: KMS encryption, security groups, network policies

## 📋 Prerequisites

### Required Tools

- **Terraform**: >= 1.5.0
- **AWS CLI**: 2.0+ configured with credentials
- **kubectl**: For cluster access
- **Helm**: 3.0+ (for ArgoCD, managed by Terraform)

### AWS Requirements

- **AWS Account**: Active AWS account with appropriate permissions
- **IAM Permissions**: 
  - EKS cluster creation
  - VPC management
  - IAM role creation
  - EC2 instance management
  - CloudWatch logging

### Pre-existing Resources

- **IAM Role for Node Group**: `ml-fashion-recommender-infra-live-role-iam`
  - Must have: `AmazonEKSWorkerNodePolicy`, `AmazonEKS_CNI_Policy`, `AmazonEC2ContainerRegistryReadOnly`, `AmazonEBSCSIDriverPolicy`
- **S3 Bucket** (optional): For Terraform remote state
- **KMS Key** (optional): For Terraform state encryption

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/hm-infra-live.git
cd hm-infra-live
```

### 2. Configure AWS Credentials

```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="ap-southeast-2"

# Option 3: AWS SSO
aws sso login --profile your-profile
export AWS_PROFILE="your-profile"
```

### 3. Create Terraform Variables File

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region   = "ap-southeast-2"
environment  = "staging"
project_name = "ml-fashion-recommender"

# Node Group IAM Role (must exist)
node_group_role_arn = "arn:aws:iam::465002806239:role/ml-fashion-recommender-infra-live-role-iam"

# Optional: Cluster Service Role
# cluster_service_role_arn = "arn:aws:iam::465002806239:role/eks-cluster-role"

# Optional: Terraform Backend (S3)
# terraform {
#   backend "s3" {
#     bucket = "your-terraform-state-bucket"
#     key    = "ml-fashion-recommender/terraform.tfstate"
#     region = "ap-southeast-2"
#     encrypt = true
#   }
# }
```

### 4. Initialize Terraform

```bash
terraform init
```

### 5. Plan Infrastructure

```bash
terraform plan
```

Review the plan to ensure all resources are correct.

### 6. Apply Infrastructure

```bash
terraform apply
```

Type `yes` to confirm. This will create:
- VPC with subnets
- EKS cluster
- Node groups
- ArgoCD (if enabled)
- Security groups and IAM roles

**⚠️ Note**: This takes approximately 15-20 minutes.

### 7. Configure kubectl

```bash
# Get kubectl config command from Terraform output
terraform output -raw kubectl_config_command | bash

# Or manually
aws eks update-kubeconfig \
  --name ml-fashion-recommender-cluster \
  --region ap-southeast-2
```

### 8. Verify Cluster

```bash
# Check nodes
kubectl get nodes

# Check ArgoCD (if enabled)
kubectl get pods -n argocd

# Get ArgoCD admin password
terraform output -raw argocd_initial_admin_password
```

## 📦 Infrastructure Components

### VPC Module (`modules/vpc/`)

**Purpose**: Creates isolated network environment

**Components**:
- VPC with DNS support
- Public subnets (3 AZs)
- Private subnets (3 AZs)
- Internet Gateway
- NAT Gateways (1 for staging, 3 for production)
- Route tables
- Security groups

**Configuration**:
```hcl
vpc_cidr         = "10.0.0.0/16"
private_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnets   = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
```

### EKS Cluster Module (`modules/eks/`)

**Purpose**: Creates managed Kubernetes cluster

**Components**:
- EKS cluster control plane
- Cluster addons (CoreDNS, kube-proxy, VPC CNI, EBS CSI)
- OIDC provider for IRSA
- Security groups
- CloudWatch logging
- KMS encryption

**Configuration**:
```hcl
cluster_name    = "ml-fashion-recommender-cluster"
cluster_version = "1.28"
```

**Addons**:
- **CoreDNS**: DNS resolution
- **kube-proxy**: Network proxy
- **VPC CNI**: AWS networking
- **EBS CSI**: Persistent volumes

### EKS Node Group Module (`modules/eks-node-group/`)

**Purpose**: Manages worker nodes

**Components**:
- Managed node groups
- Auto-scaling configuration
- Instance type configuration
- Capacity type (ON_DEMAND or SPOT)

**Configuration**:
```hcl
node_groups = {
  general = {
    desired_size = 2
    min_size     = 1
    max_size     = 5
    instance_types = ["t3.medium"]
    capacity_type  = "ON_DEMAND"
  }
}
```

### ArgoCD (`argocd.tf`)

**Purpose**: GitOps operator for declarative deployments

**Components**:
- Helm release for ArgoCD
- Root Application configuration
- GitOps repository integration
- LoadBalancer service

**Configuration**:
```hcl
argocd_enabled = true
gitops_repo_url = "https://github.com/your-org/hm-mlops-gitops"
```

## ⚙️ Configuration

### Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region | `ap-southeast-2` | No |
| `environment` | Environment name | - | Yes |
| `project_name` | Project name | `ml-fashion-recommender` | No |
| `eks_cluster_name` | EKS cluster name | `ml-fashion-recommender-cluster` | No |
| `kubernetes_version` | Kubernetes version | `1.28` | No |
| `vpc_cidr` | VPC CIDR block | `10.0.0.0/16` | No |
| `node_group_role_arn` | IAM role ARN for nodes | - | Yes |
| `node_group_desired_size` | Desired node count | `2` | No |
| `node_group_min_size` | Minimum node count | `1` | No |
| `node_group_max_size` | Maximum node count | `5` | No |
| `node_instance_types` | EC2 instance types | `["t3.medium"]` | No |
| `argocd_enabled` | Enable ArgoCD | `true` | No |

### Environment-Specific Configuration

**Staging**:
- Single NAT gateway (cost optimization)
- Smaller node groups
- Development-friendly settings

**Production**:
- Multiple NAT gateways (high availability)
- Larger node groups
- Production-hardened settings

### Terraform Backend

**Local State** (default):
- State stored locally in `terraform.tfstate`
- Suitable for development

**S3 Backend** (recommended for production):
```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "ml-fashion-recommender/terraform.tfstate"
    region         = "ap-southeast-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock" # Optional: state locking
  }
}
```

## 🚀 Deployment

### Initial Deployment

1. **Review configuration**:
   ```bash
   terraform plan
   ```

2. **Apply infrastructure**:
   ```bash
   terraform apply
   ```

3. **Configure kubectl**:
   ```bash
   terraform output -raw kubectl_config_command | bash
   ```

4. **Verify deployment**:
   ```bash
   kubectl get nodes
   kubectl get pods -n argocd
   ```

### Updating Infrastructure

1. **Modify configuration** in `*.tf` files

2. **Plan changes**:
   ```bash
   terraform plan
   ```

3. **Apply changes**:
   ```bash
   terraform apply
   ```

### Destroying Infrastructure

**⚠️ Warning**: This will delete all infrastructure!

```bash
terraform destroy
```

## 🔒 Security

### Network Security

- **Private Subnets**: Nodes run in private subnets
- **NAT Gateways**: Outbound internet access via NAT
- **Security Groups**: Restrictive ingress/egress rules
- **VPC Endpoints**: AWS service access without internet

### Access Control

- **IRSA**: IAM Roles for Service Accounts (no access keys)
- **RBAC**: Kubernetes role-based access control
- **OIDC Provider**: Secure token-based authentication

### Encryption

- **KMS Encryption**: EKS secrets encrypted at rest
- **TLS**: All API communication encrypted
- **State Encryption**: Terraform state encrypted in S3

### Best Practices

1. **Least Privilege**: Minimum required IAM permissions
2. **Secret Management**: Use AWS Secrets Manager or Sealed Secrets
3. **Network Policies**: Implement Kubernetes network policies
4. **Audit Logging**: Enable CloudWatch and audit logs
5. **Regular Updates**: Keep EKS and addons updated

## 🔧 Operations

### Accessing the Cluster

```bash
# Configure kubectl
aws eks update-kubeconfig --name ml-fashion-recommender-cluster --region ap-southeast-2

# Verify access
kubectl get nodes
```

### Scaling Node Groups

**Manual Scaling**:
```bash
# Update terraform.tfvars
node_group_desired_size = 3

# Apply changes
terraform apply
```

**Auto-Scaling**:
- Configured via `node_group_min_size` and `node_group_max_size`
- EKS automatically scales based on pod scheduling requirements

### Updating Cluster

```bash
# Update Kubernetes version in terraform.tfvars
kubernetes_version = "1.29"

# Plan and apply
terraform plan
terraform apply
```

### Monitoring

**CloudWatch Logs**:
- Cluster control plane logs
- Node logs
- Application logs

**Access Logs**:
```bash
# View cluster logs
aws logs tail /aws/eks/ml-fashion-recommender-cluster/cluster --follow
```

### ArgoCD Access

**Get ArgoCD URL**:
```bash
terraform output argocd_server_url
```

**Get Admin Password**:
```bash
terraform output -raw argocd_initial_admin_password
```

**Port Forward** (alternative):
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

## 🐛 Troubleshooting

### Cluster Creation Fails

**Check IAM permissions**:
```bash
aws iam get-user
aws sts get-caller-identity
```

**Check VPC limits**:
```bash
aws ec2 describe-vpcs
```

### Nodes Not Joining Cluster

**Check node group role**:
```bash
aws iam get-role --role-name ml-fashion-recommender-infra-live-role-iam
```

**Check node security group**:
```bash
kubectl describe node <node-name>
```

### ArgoCD Not Accessible

**Check ArgoCD pods**:
```bash
kubectl get pods -n argocd
kubectl logs -n argocd deployment/argocd-server
```

**Check LoadBalancer**:
```bash
kubectl get svc -n argocd argocd-server
```

### Network Issues

**Check security groups**:
```bash
aws ec2 describe-security-groups --filters "Name=tag:Name,Values=*eks*"
```

**Check route tables**:
```bash
aws ec2 describe-route-tables
```

## 📚 Documentation

- [Quick Reference](QUICK_REFERENCE.md)
- [IRSA Examples](examples/irsa-examples.tf)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## 🤝 Contributing

### Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** and validate:
   ```bash
   terraform fmt
   terraform validate
   terraform plan
   ```

3. **Test in staging**:
   ```bash
   terraform workspace select staging
   terraform apply
   ```

4. **Commit and push**:
   ```bash
   git commit -m "feat: add new feature"
   git push origin feature/your-feature-name
   ```

5. **Create PR**: Ensure CI validation passes

### Code Standards

- **Format**: Run `terraform fmt` before committing
- **Validate**: Run `terraform validate` before committing
- **Documentation**: Update README for significant changes
- **Variables**: Add descriptions to all variables

## 🔗 Related Repositories

- [ML Platform](../h&m_deeplearning) - ML components and CI/CD
- [GitOps Configuration](../hm-mlops-gitops) - Kubernetes manifests and ArgoCD

## 📞 Support

For issues and questions:
- Create an issue in this repository
- Contact the Platform Engineering team
- Check AWS EKS documentation

## 📝 Notes

- **Infrastructure Only**: This repo manages infrastructure, not applications
- **Application Deployments**: Managed via GitOps repository
- **State Management**: Use S3 backend for production
- **Cost Optimization**: Staging uses single NAT gateway

---

**Built with ❤️ by the H&M Platform Engineering Team**

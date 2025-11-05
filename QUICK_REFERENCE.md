# ML Fashion Recommender Infrastructure - Quick Reference

## 📁 Cấu Trúc Repository

```
hm-infra-live/
├── main.tf                      # Main Terraform configuration
├── variables.tf                  # Variable definitions
├── outputs.tf                    # Output values
├── argocd.tf                     # ArgoCD installation và Root Application
├── terraform.tfvars.example      # Example variables file
├── .gitignore                    # Git ignore rules
├── README.md                     # Main documentation
├── modules/
│   ├── vpc/                      # VPC module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eks/                      # EKS cluster module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── eks-node-group/           # EKS node group module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── examples/
    ├── irsa-examples.tf          # IRSA setup examples
    └── README.md                 # Examples documentation
```

## 🚀 Quick Start Commands

```bash
# 1. Initialize Terraform
terraform init

# 2. Copy và chỉnh sửa variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars với các giá trị phù hợp

# 3. Plan changes
terraform plan

# 4. Apply infrastructure
terraform apply

# 5. Configure kubectl
aws eks update-kubeconfig --name ml-fashion-recommender-cluster --region ap-southeast-2

# 6. Verify cluster
kubectl get nodes
kubectl get pods -n argocd
```

## 🔑 Key Configuration

### Node Group IAM Role
```
arn:aws:iam::465002806239:role/ml-fashion-recommender-infra-live-role-iam
```

### AWS Account & Region
- **Account ID**: 465002806239
- **Region**: ap-southeast-2 (default)

### EKS Cluster
- **Name**: ml-fashion-recommender-cluster
- **Version**: 1.28 (default)
- **IRSA**: Enabled

### ArgoCD
- **Namespace**: argocd
- **GitOps Repo**: https://github.com/manhque-lab/ml-fashion-recommender-gitops
- **Bootstrap Path**: bootstrap

## 📊 Important Outputs

Sau khi apply thành công, các outputs quan trọng:

```bash
# EKS Cluster Info
terraform output eks_cluster_id
terraform output eks_cluster_endpoint
terraform output oidc_provider_arn

# VPC Info
terraform output vpc_id
terraform output private_subnet_ids

# ArgoCD Info
terraform output argocd_server_url
terraform output argocd_initial_admin_password
```

## 🔗 Related Repositories

- **Application Code**: `h&m_deeplearning` - ML components và Docker images
- **GitOps Config**: `hm-mlops-gitops` - Kubernetes manifests và ArgoCD configs
- **Infrastructure**: `hm-infra-live` (this repo) - Terraform infrastructure code

## ⚠️ Important Notes

1. **Terraform State**: Nên sử dụng S3 backend với encryption
2. **Secrets**: Không commit `terraform.tfvars` vào git
3. **Node Role**: Đảm bảo IAM role đã có đủ policies:
   - AmazonEKSWorkerNodePolicy
   - AmazonEKS_CNI_Policy
   - AmazonEC2ContainerRegistryReadOnly
   - AmazonEBSCSIDriverPolicy
4. **IRSA**: OIDC provider được tạo tự động để enable IRSA

## 🆘 Troubleshooting

### EKS Cluster không tạo được
- Kiểm tra IAM permissions
- Kiểm tra VPC và subnets
- Kiểm tra security groups

### Node group không join được cluster
- Kiểm tra node role ARN
- Kiểm tra security group rules
- Kiểm tra subnets có đủ IP addresses

### ArgoCD không sync được
- Kiểm tra GitOps repo URL
- Kiểm tra ArgoCD pods đang chạy
- Kiểm tra network connectivity

### IRSA không hoạt động
- Kiểm tra OIDC provider được tạo
- Kiểm tra ServiceAccount annotation
- Kiểm tra IAM role trust policy


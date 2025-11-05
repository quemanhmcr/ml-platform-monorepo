# ML Fashion Recommender - Infrastructure Live Repository

Repository này chứa Terraform code để khởi tạo và quản lý hạ tầng AWS cho ML Fashion Recommender platform, bao gồm:

- **EKS Cluster**: Kubernetes cluster trên AWS
- **EKS Node Groups**: Worker nodes với IAM role được chỉ định
- **VPC và Networking**: VPC, subnets, NAT gateways, security groups
- **ArgoCD**: GitOps operator để quản lý Kubernetes deployments
- **IRSA Setup**: IAM Roles for Service Accounts cho workloads

## 📋 Yêu Cầu

- Terraform >= 1.5.0
- AWS CLI đã được cấu hình với credentials
- kubectl
- Helm CLI (để cài ArgoCD)

## 🏗️ Cấu Trúc Dự Án

```
.
├── main.tf                    # Main Terraform configuration
├── variables.tf               # Variable definitions
├── outputs.tf                # Output values
├── argocd.tf                  # ArgoCD installation và Root Application
├── terraform.tfvars.example   # Example variables file
├── modules/
│   ├── vpc/                   # VPC module
│   ├── eks/                   # EKS cluster module
│   └── eks-node-group/        # EKS node group module
└── README.md
```

## 🚀 Quick Start

### 1. Cấu hình AWS Credentials

Đảm bảo AWS CLI đã được cấu hình:

```bash
aws configure
```

Hoặc sử dụng environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="ap-southeast-2"
```

### 2. Tạo Terraform Variables File

Copy file example và cập nhật các giá trị:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Chỉnh sửa `terraform.tfvars` với các giá trị phù hợp:

```hcl
aws_region   = "ap-southeast-2"
environment  = "staging"
project_name = "ml-fashion-recommender"

# Node Group IAM Role
node_group_role_arn = "arn:aws:iam::465002806239:role/ml-fashion-recommender-infra-live-role-iam"
```

### 3. Cấu hình Terraform Backend (Optional)

Nếu bạn muốn sử dụng remote state (S3), cập nhật `main.tf`:

```hcl
terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "ml-fashion-recommender/terraform.tfstate"
    region = "ap-southeast-2"
    encrypt = true
  }
}
```

### 4. Khởi tạo và Apply Terraform

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan

# Apply infrastructure
terraform apply
```

### 5. Cấu hình kubectl

Sau khi EKS cluster được tạo, cấu hình kubectl:

```bash
aws eks update-kubeconfig --name ml-fashion-recommender-cluster --region ap-southeast-2
```

Hoặc sử dụng output từ Terraform:

```bash
terraform output -raw kubectl_config_command | bash
```

### 6. Xác minh Cluster

```bash
# Kiểm tra nodes
kubectl get nodes

# Kiểm tra ArgoCD (nếu enabled)
kubectl get pods -n argocd

# Lấy ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## 🔧 Cấu Hình Chi Tiết

### EKS Node Group Role

Repository này sử dụng IAM role có sẵn cho node group:

```
arn:aws:iam::465002806239:role/ml-fashion-recommender-infra-live-role-iam
```

Role này phải có các policies sau:
- `AmazonEKSWorkerNodePolicy`
- `AmazonEKS_CNI_Policy`
- `AmazonEC2ContainerRegistryReadOnly`
- `AmazonEBSCSIDriverPolicy`

### VPC Configuration

Default VPC configuration:
- **CIDR**: `10.0.0.0/16`
- **Private Subnets**: `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24`
- **Public Subnets**: `10.0.101.0/24`, `10.0.102.0/24`, `10.0.103.0/24`
- **NAT Gateways**: 1 cho staging, 3 cho production

### ArgoCD Configuration

ArgoCD được cài đặt tự động và root application sẽ trỏ đến GitOps repository:

- **Repository**: `https://github.com/manhque-lab/ml-fashion-recommender-gitops`
- **Path**: `bootstrap`
- **Namespace**: `argocd`

## 📊 Outputs

Sau khi apply thành công, Terraform sẽ output các thông tin quan trọng:

```bash
# Xem tất cả outputs
terraform output

# Xem từng output cụ thể
terraform output eks_cluster_id
terraform output eks_cluster_endpoint
terraform output vpc_id
terraform output oidc_provider_arn
```

## 🔐 Security Best Practices

1. **Terraform State**: Sử dụng S3 backend với encryption enabled
2. **Secrets**: Không commit `terraform.tfvars` vào git
3. **IAM Roles**: Sử dụng IRSA cho workloads thay vì hardcode credentials
4. **Network Security**: Nodes chạy trong private subnets
5. **EKS Encryption**: Cluster secrets được encrypt bằng KMS

## 🧹 Cleanup

Để xóa toàn bộ infrastructure:

```bash
terraform destroy
```

**⚠️ Cảnh báo**: Lệnh này sẽ xóa toàn bộ EKS cluster, VPC, và các resources liên quan!

## 📚 Tài Liệu Tham Khảo

- [EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitOps Repository](../hm-mlops-gitops/README.md)

## 🤝 Contributing

Khi thay đổi infrastructure:

1. Tạo branch mới từ `main`
2. Thực hiện thay đổi và test với `terraform plan`
3. Tạo Pull Request với description chi tiết
4. Yêu cầu review từ team
5. Merge sau khi approved

## 📝 Notes

- Repository này quản lý **infrastructure**, không phải application code
- Application deployments được quản lý bởi GitOps repository (`hm-mlops-gitops`)
- ArgoCD tự động sync các changes từ GitOps repository vào cluster


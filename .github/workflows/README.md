# GitHub Actions Workflow - Setup Guide

## Required GitHub Secrets

Để workflow có thể chạy, bạn cần setup secret sau trong GitHub repository:

### 1. AWS IAM Role ARN (for GitHub Actions) - REQUIRED
- **Secret Name**: `AWS_IAM_ROLE_ARN`
- **Value**: ARN của IAM role để GitHub Actions assume role
- **Example**: `arn:aws:iam::465002806239:role/github-actions-role`

### 2. Node Group Role ARN (optional - đã có trong terraform.tfvars)
- **Secret Name**: `NODE_GROUP_ROLE_ARN`
- **Value**: `arn:aws:iam::465002806239:role/ml-fashion-recommender-infra-live-role-iam`
- **Note**: Đã có trong terraform.tfvars, không cần secret này nữa

### 3. Cluster Service Role ARN (optional - đã có trong terraform.tfvars)
- **Secret Name**: `CLUSTER_SERVICE_ROLE_ARN`
- **Value**: ARN của cluster service role (hoặc để empty để auto-create)
- **Note**: Đã có trong terraform.tfvars, không cần secret này nữa

## Cách Setup Secrets

1. Vào GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Thêm các secrets trên

## Cách Sử Dụng Workflow

1. Vào tab "Actions" trong GitHub repository
2. Chọn workflow "Terraform Apply"
3. Click "Run workflow"
4. Chọn:
   - **Environment**: staging hoặc production
   - **Terraform action**: plan hoặc apply
   - **Auto approve**: true/false (chỉ dùng khi chắc chắn)
5. Click "Run workflow"

## Workflow Steps

1. ✅ Checkout code
2. ✅ Configure AWS credentials (từ IAM role)
3. ✅ Setup Terraform
4. ✅ Terraform Init
5. ✅ Terraform Validate
6. ✅ Terraform Format Check
7. ✅ Terraform Plan (nếu chọn plan hoặc apply)
8. ✅ Terraform Apply (nếu chọn apply)

## Lưu Ý

- **terraform.tfvars**: File này được commit vào git (personal project)
  - Tất cả values được lưu trong terraform.tfvars
  - Workflow sẽ tự động sử dụng file này
- **Environment**: Workflow sẽ override environment từ input (staging/production)
- **Approval**: Production deployments nên có manual approval
- **State**: Nên setup S3 backend để quản lý state tốt hơn

## Workflow sẽ:
- ✅ Tự động sử dụng terraform.tfvars
- ✅ Override environment từ workflow input
- ✅ Chỉ cần AWS_IAM_ROLE_ARN secret để authenticate với AWS


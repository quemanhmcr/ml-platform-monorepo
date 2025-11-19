# =============================================================================
# IRSA (IAM Roles for Service Accounts) Setup Examples
# =============================================================================
#
# IRSA cho phép Kubernetes ServiceAccounts sử dụng AWS IAM roles thay vì 
# hardcode credentials. File này chứa các ví dụ về cách setup IRSA cho
# các workloads trong ML Fashion Recommender.
#
# =============================================================================

# Example 1: IRSA Policy cho S3 Access
# Tạo IAM policy cho ServiceAccount để truy cập S3
data "aws_iam_policy_document" "ml_inference_s3_access" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::ml-fashion-data-lake-*",
      "arn:aws:s3:::ml-fashion-data-lake-*/*"
    ]
  }
}

# Example 2: Tạo IAM Role cho ServiceAccount
resource "aws_iam_role" "ml_inference_sa_role" {
  name = "ml-inference-sa-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = module.eks.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(module.eks.oidc_provider.url, "https://", "")}:sub" = "system:serviceaccount:ml-inference-${var.environment}:ml-inference-sa"
            "${replace(module.eks.oidc_provider.url, "https://", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Example 3: Attach Policy to Role
resource "aws_iam_role_policy" "ml_inference_s3_access" {
  name   = "ml-inference-s3-access-${var.environment}"
  role   = aws_iam_role.ml_inference_sa_role.id
  policy = data.aws_iam_policy_document.ml_inference_s3_access.json
}

# Example 4: Kubernetes ServiceAccount với IRSA annotation
# File này sẽ được quản lý bởi GitOps repo, nhưng đây là ví dụ:
#
# apiVersion: v1
# kind: ServiceAccount
# metadata:
#   name: ml-inference-sa
#   namespace: ml-inference-prod
#   annotations:
#     eks.amazonaws.com/role-arn: arn:aws:iam::465002806239:role/ml-inference-sa-role-production
#
# =============================================================================
# Usage trong GitOps Repository
# =============================================================================
#
# Trong GitOps repository (hm-mlops-gitops), bạn sẽ cập nhật ServiceAccount
# với IRSA role ARN từ outputs của Terraform:
#
# 1. Sau khi apply Terraform, lấy OIDC provider ARN:
#    terraform output oidc_provider_arn
#
# 2. Tạo IAM role với trust policy cho ServiceAccount (như ví dụ trên)
#
# 3. Cập nhật ServiceAccount trong GitOps repo với annotation:
#    eks.amazonaws.com/role-arn: <role-arn>
#
# 4. ArgoCD sẽ tự động sync và workload sẽ có quyền truy cập AWS services
#
# =============================================================================


# =============================================================================
# Terraform Variables - Production Configuration
# =============================================================================
# This file contains actual values for deployment
# DO NOT commit sensitive values - use GitHub Secrets instead
# =============================================================================

aws_region   = "ap-southeast-2"
environment  = "production"  # Change to "production" for production deployment

project_name = "ml-fashion-recommender"

# EKS Configuration
eks_cluster_name  = "ml-fashion-recommender-cluster"
kubernetes_version = "1.28"

# VPC Configuration
vpc_cidr        = "10.0.0.0/16"
private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

# Node Group Configuration
node_group_role_arn   = "arn:aws:iam::465002806239:role/ml-fashion-recommender-infra-live-role-iam"
cluster_service_role_arn = ""  # Leave empty to auto-create

node_group_desired_size = 2
node_group_min_size     = 1
node_group_max_size     = 5
node_instance_types     = ["t3.medium"]
node_capacity_type      = "ON_DEMAND"

# ArgoCD Configuration
argocd_enabled     = true
argocd_namespace   = "argocd"
gitops_repo_url    = "https://github.com/manhque-lab/ml-fashion-recommender-gitops"
gitops_repo_path   = "bootstrap"

# Terraform Backend Configuration
# Uncomment and configure these if using S3 backend for state
# terraform {
#   backend "s3" {
#     bucket = "your-terraform-state-bucket"
#     key    = "ml-fashion-recommender/terraform.tfstate"
#     region = "ap-southeast-2"
#     encrypt = true
#     dynamodb_table = "terraform-state-lock"
#   }
# }


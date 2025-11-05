# =============================================================================
# Terraform Variables
# =============================================================================

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-southeast-2"
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ml-fashion-recommender"
}

variable "eks_cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "ml-fashion-recommender-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# EKS Node Group Configuration
variable "node_group_role_arn" {
  description = "IAM role ARN for EKS node group"
  type        = string
  default     = "arn:aws:iam::465002806239:role/ml-fashion-recommender-infra-live-role-iam"
}

variable "cluster_service_role_arn" {
  description = "IAM role ARN for EKS cluster service"
  type        = string
  default     = ""
}

variable "node_group_desired_size" {
  description = "Desired number of nodes in node group"
  type        = number
  default     = 2
}

variable "node_group_min_size" {
  description = "Minimum number of nodes in node group"
  type        = number
  default     = 1
}

variable "node_group_max_size" {
  description = "Maximum number of nodes in node group"
  type        = number
  default     = 5
}

variable "node_instance_types" {
  description = "EC2 instance types for node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_capacity_type" {
  description = "Capacity type for node group (ON_DEMAND or SPOT)"
  type        = string
  default     = "ON_DEMAND"
  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.node_capacity_type)
    error_message = "Node capacity type must be either 'ON_DEMAND' or 'SPOT'."
  }
}

# ArgoCD Configuration
variable "argocd_enabled" {
  description = "Enable ArgoCD installation"
  type        = bool
  default     = true
}

variable "argocd_namespace" {
  description = "Namespace for ArgoCD"
  type        = string
  default     = "argocd"
}

variable "gitops_repo_url" {
  description = "GitOps repository URL"
  type        = string
  default     = "https://github.com/manhque-lab/ml-fashion-recommender-gitops"
}

variable "gitops_repo_path" {
  description = "Path in GitOps repo for bootstrap"
  type        = string
  default     = "bootstrap"
}


# =============================================================================
# Main Terraform Configuration for ML Fashion Recommender Infrastructure
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "~> 1.14"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  backend "s3" {
    # Configure backend in terraform.tfvars or via environment variables
    # bucket = "your-terraform-state-bucket"
    # key    = "ml-fashion-recommender/terraform.tfstate"
    # region = "ap-southeast-2"
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ml-fashion-recommender"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  name                 = "${var.project_name}-${var.environment}"
  cidr                 = var.vpc_cidr
  azs                  = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets      = var.private_subnets
  public_subnets       = var.public_subnets
  enable_nat_gateway   = true
  single_nat_gateway   = var.environment == "staging" ? true : false
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    "kubernetes.io/role/internal-elb" = "1"
    "kubernetes.io/cluster/${var.eks_cluster_name}" = "shared"
  }
}

# EKS Cluster Module
module "eks" {
  source = "./modules/eks"

  cluster_name    = var.eks_cluster_name
  cluster_version = var.kubernetes_version
  vpc_id          = module.vpc.vpc_id
  vpc_cidr        = var.vpc_cidr
  subnet_ids      = module.vpc.private_subnets

  # EKS Cluster Service Role
  cluster_service_role_arn = var.cluster_service_role_arn

  # Cluster addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  # Enable IRSA
  enable_irsa = true

  # Node Security Group
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }
    ingress_cluster_to_node_all_tcp = {
      description                   = "Cluster to node all TCP traffic"
      protocol                      = "tcp"
      from_port                     = 0
      to_port                       = 65535
      type                          = "ingress"
      source_cluster_security_group = true
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [module.vpc]
}

# EKS Node Group Module
module "eks_node_group" {
  source = "./modules/eks-node-group"

  cluster_name   = module.eks.cluster_name
  cluster_version = var.kubernetes_version
  node_role_arn  = var.node_group_role_arn # ml-fashion-recommender-infra-live-role-iam

  # Node Group Configuration
  node_groups = {
    general = {
      desired_size = var.node_group_desired_size
      min_size     = var.node_group_min_size
      max_size     = var.node_group_max_size
      instance_types = var.node_instance_types
      capacity_type  = var.node_capacity_type

      labels = {
        Environment = var.environment
        NodeGroup   = "general"
      }

      taints = []

      tags = {
        Environment = var.environment
        NodeGroup   = "general"
      }
    }
  }

  subnet_ids = module.vpc.private_subnets

  cluster_depends_on = [module.eks]

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }

  depends_on = [module.eks]
}

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

# Get IAM role name from ARN
locals {
  node_role_name = var.node_group_role_arn != "" ? split("/", var.node_group_role_arn)[1] : ""
}

# Attach ECR read policy to node group role
resource "aws_iam_role_policy" "node_group_ecr_access" {
  count = var.node_group_role_arn != "" ? 1 : 0

  name   = "${var.project_name}-${var.environment}-ecr-read-only"
  role   = local.node_role_name
  policy = data.aws_iam_policy_document.ecr_read_only.json
}

# Kubernetes Provider Configuration
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks.cluster_name
    ]
  }
}

# Helm Provider Configuration
provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        module.eks.cluster_name
      ]
    }
  }
}

# Kubectl Provider Configuration
provider "kubectl" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks.cluster_name
    ]
  }
}


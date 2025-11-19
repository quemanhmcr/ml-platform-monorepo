# =============================================================================
# EKS Cluster Module
# =============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = var.cluster_service_role_arn != "" ? var.cluster_service_role_arn : aws_iam_role.cluster[0].arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access   = true
    security_group_ids      = [aws_security_group.cluster.id]
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks.arn
    }
    resources = ["secrets"]
  }

  # Addons are managed via separate aws_eks_addon resources

  depends_on = [
    aws_iam_role_policy_attachment.cluster_AmazonEKSClusterPolicy,
    aws_cloudwatch_log_group.cluster,
  ]

  tags = var.tags
}

# EKS Addons
resource "aws_eks_addon" "this" {
  for_each = var.cluster_addons

  cluster_name             = aws_eks_cluster.main.name
  addon_name               = each.key
  addon_version            = try(each.value.addon_version, null)
  service_account_role_arn = try(each.value.service_account_role_arn, null)
  resolve_conflicts        = try(each.value.resolve_conflicts, "OVERWRITE")
  preserve                 = try(each.value.preserve, false)

  depends_on = [aws_eks_cluster.main]
}

# EKS Cluster IAM Role (if not provided)
resource "aws_iam_role" "cluster" {
  count = var.cluster_service_role_arn == "" ? 1 : 0

  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "cluster_AmazonEKSClusterPolicy" {
  count = var.cluster_service_role_arn == "" ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.cluster[0].name
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "cluster" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = 7

  tags = var.tags
}

# KMS Key for EKS Encryption
resource "aws_kms_key" "eks" {
  description             = "EKS cluster encryption key"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(
    {
      Name = "${var.cluster_name}-eks-key"
    },
    var.tags
  )
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.cluster_name}-eks"
  target_key_id = aws_kms_key.eks.key_id
}

# Security Group for EKS Cluster
resource "aws_security_group" "cluster" {
  name        = "${var.cluster_name}-cluster-sg"
  description = "Security group for EKS cluster"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr != "" ? var.vpc_cidr : "10.0.0.0/16"]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    {
      Name = "${var.cluster_name}-cluster-sg"
    },
    var.tags
  )
}

# OIDC Identity Provider for IRSA
data "tls_certificate" "eks" {
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  count = var.enable_irsa ? 1 : 0

  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer

  tags = var.tags
}

# Node Security Group
resource "aws_security_group" "node" {
  name        = "${var.cluster_name}-node-sg"
  description = "Security group for EKS nodes"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow ingress from cluster"
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.cluster.id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  dynamic "ingress" {
    for_each = var.node_security_group_additional_rules
    content {
      description                   = ingress.value.description
      from_port                     = ingress.value.from_port
      to_port                       = ingress.value.to_port
      protocol                      = ingress.value.protocol
      cidr_blocks                   = lookup(ingress.value, "cidr_blocks", null)
      security_groups               = lookup(ingress.value, "security_groups", null)
      self                          = lookup(ingress.value, "self", null)
    }
  }

  tags = merge(
    {
      Name = "${var.cluster_name}-node-sg"
    },
    var.tags
  )
}

# Additional ingress rules sourced from cluster security group
resource "aws_security_group_rule" "node_additional_ingress_from_cluster_sg" {
  for_each = {
    for k, v in var.node_security_group_additional_rules : k => v
    if try(v.source_cluster_security_group, false)
  }

  type                     = "ingress"
  description              = try(each.value.description, null)
  from_port                = each.value.from_port
  to_port                  = each.value.to_port
  protocol                 = each.value.protocol
  security_group_id        = aws_security_group.node.id
  source_security_group_id = aws_security_group.cluster.id
}


# =============================================================================
# EKS Node Group Module
# =============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# EKS Node Groups
resource "aws_eks_node_group" "main" {
  for_each = var.node_groups

  cluster_name    = var.cluster_name
  node_group_name = "${var.cluster_name}-${each.key}"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.subnet_ids
  version         = var.cluster_version

  ami_type       = try(each.value.ami_type, "AL2_x86_64")
  capacity_type  = try(each.value.capacity_type, "ON_DEMAND")
  instance_types = try(each.value.instance_types, ["t3.medium"])
  disk_size      = try(each.value.disk_size, 20)

  scaling_config {
    desired_size = try(each.value.desired_size, 2)
    min_size     = try(each.value.min_size, 1)
    max_size     = try(each.value.max_size, 5)
  }

  remote_access {
    ec2_ssh_key               = try(each.value.remote_access_key, null)
    source_security_group_ids = try(each.value.remote_access_security_group_ids, [])
  }

  dynamic "taint" {
    for_each = try(each.value.taints, [])
    content {
      key    = taint.value.key
      value  = try(taint.value.value, null)
      effect = taint.value.effect
    }
  }

  labels = merge(
    {
      NodeGroup = each.key
    },
    try(each.value.labels, {})
  )

  tags = merge(
    {
      Name                                        = "${var.cluster_name}-${each.key}"
      "k8s.io/cluster-autoscaler/enabled"        = "true"
      "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
    },
    try(each.value.tags, {}),
    var.tags
  )

  depends_on = [var.cluster_depends_on]
}


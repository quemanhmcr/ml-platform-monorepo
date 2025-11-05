output "node_group_arns" {
  description = "Map of node group ARNs"
  value       = { for k, v in aws_eks_node_group.main : k => v.arn }
}

output "node_group_ids" {
  description = "Map of node group IDs"
  value       = { for k, v in aws_eks_node_group.main : k => v.id }
}

output "node_group_statuses" {
  description = "Map of node group statuses"
  value       = { for k, v in aws_eks_node_group.main : k => v.status }
}


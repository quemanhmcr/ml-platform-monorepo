# =============================================================================
# Terraform Outputs
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

output "eks_cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_name
}

output "eks_cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.eks.cluster_arn
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = false
}

output "eks_cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "eks_cluster_version" {
  description = "EKS cluster Kubernetes version"
  value       = module.eks.cluster_version
}

output "eks_node_security_group_id" {
  description = "Security group ID attached to the EKS nodes"
  value       = module.eks.node_security_group_id
}

output "eks_oidc_provider_arn" {
  description = "OIDC provider ARN for IRSA"
  value       = module.eks.oidc_provider_arn
}

output "eks_oidc_provider" {
  description = "OIDC provider for IRSA"
  value       = module.eks.oidc_provider
}

output "eks_cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data for EKS cluster"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.aws_region}"
}

output "argocd_server_url" {
  description = "ArgoCD server URL (if enabled)"
  value       = var.argocd_enabled && length(data.kubernetes_service.argocd_server) > 0 && length(data.kubernetes_service.argocd_server[0].status[0].load_balancer[0].ingress) > 0 ? "https://${data.kubernetes_service.argocd_server[0].status[0].load_balancer[0].ingress[0].hostname}" : null
}

output "argocd_initial_admin_password" {
  description = "ArgoCD initial admin password"
  value       = var.argocd_enabled ? random_password.argocd_admin_password[0].result : null
  sensitive   = true
}

output "aws_account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "AWS Region"
  value       = var.aws_region
}


variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version for node groups"
  type        = string
  default     = "1.28"
}

variable "node_role_arn" {
  description = "IAM role ARN for EKS node group"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for node groups"
  type        = list(string)
}

variable "node_groups" {
  description = "Map of node group configurations"
  type = map(object({
    desired_size    = number
    min_size        = number
    max_size        = number
    instance_types  = list(string)
    capacity_type   = optional(string, "ON_DEMAND")
    ami_type        = optional(string, "AL2_x86_64")
    disk_size       = optional(number, 20)
    labels          = optional(map(string), {})
    taints          = optional(list(object({
      key    = string
      value  = optional(string)
      effect = string
    })), [])
    tags = optional(map(string), {})
    remote_access_key = optional(string)
    remote_access_security_group_ids = optional(list(string), [])
  }))
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

variable "cluster_depends_on" {
  description = "Dependencies for cluster creation"
  type        = any
  default     = []
}


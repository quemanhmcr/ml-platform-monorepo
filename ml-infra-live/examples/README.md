# =============================================================================
# Module README - IRSA Examples
# =============================================================================

Repository này cung cấp infrastructure cho ML Fashion Recommender với IRSA (IAM Roles for Service Accounts) được enable.

## IRSA Setup

IRSA cho phép Kubernetes ServiceAccounts sử dụng AWS IAM roles mà không cần hardcode credentials.

### Steps để setup IRSA cho workload:

1. **Lấy OIDC Provider ARN từ Terraform output:**
   ```bash
   terraform output oidc_provider_arn
   ```

2. **Tạo IAM Role với trust policy:**
   Xem ví dụ trong `examples/irsa-examples.tf`

3. **Cập nhật ServiceAccount trong GitOps repo:**
   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: ml-inference-sa
     namespace: ml-inference-prod
     annotations:
       eks.amazonaws.com/role-arn: arn:aws:iam::465002806239:role/ml-inference-sa-role-production
   ```

4. **ArgoCD sẽ tự động sync và workload có quyền truy cập AWS services**

### Common IAM Policies Needed:

- **S3 Access**: Cho data ingestion và model artifacts
- **ECR Access**: Đã được attach vào node group role
- **Secrets Manager**: Cho application secrets
- **CloudWatch Logs**: Cho logging

Xem `examples/irsa-examples.tf` để biết cách tạo các policies này.


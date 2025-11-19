# Configuration Management

## 🔒 Security Best Practices (BigTech Approach)

### Zero-Trust in CI/CD
**CI/CD workflows use GitHub Secrets EXCLUSIVELY** - no config file fallback for maximum security.

This follows BigTech security principles:
- ✅ **Secrets-only in production** - No config files in CI/CD
- ✅ **Zero-trust approach** - Assume config files are compromised
- ✅ **Fail-fast validation** - Missing secrets cause immediate failure
- ✅ **Clear separation** - CI/CD (secrets) vs Local Development (files)

### ✅ Safe to Commit (Non-Sensitive)
- Configuration structure (`aws.schema.json`)
- Documentation files

### 🔒 Never Commit (Sensitive - Use Secrets Only)
- **AWS Account IDs** - Must use GitHub Secrets
- **IAM Role ARNs** - Must use GitHub Secrets  
- **ECR Registry URLs** - Must use GitHub Secrets
- **Any real credentials** - Must use GitHub Secrets

**Note:** CI/CD has ECR-only permissions. S3 config is not used by CI/CD.

### 🔐 Logging & Masking in CI/CD
- All sensitive values are masked in GitHub Actions logs
- Only `region` is displayed (non-sensitive)
- Config source shows "GitHub Secrets (zero-trust)"
- No account IDs or ARNs appear in public logs

## Configuration Strategy

### 🚀 CI/CD (Production): GitHub Secrets ONLY
Workflow **requires** all secrets to be set. No fallback to config files.

### 💻 Local Development: Config Files
Use `config/aws.json` for local development only (not used in CI/CD).

## Setup Instructions

### 🚀 CI/CD Setup (Required for GitHub Actions)

**GitHub Secrets are MANDATORY** - Workflow will fail if secrets are missing.

1. Go to **Repository Settings → Secrets and variables → Actions**
2. Click **"New repository secret"** and add:

   | Secret Name | Description | Example |
   |------------|-------------|---------|
   | `AWS_ACCOUNT_ID` | AWS Account ID (12 digits) | `123456789012` |
   | `AWS_REGION` | AWS Region | `ap-southeast-2` |
   | `AWS_IAM_ROLE_ARN` | IAM Role ARN for OIDC | `arn:aws:iam::123456789012:role/github-actions-ecr-role` |
   | `AWS_ECR_REGISTRY` | ECR Registry URL | `123456789012.dkr.ecr.ap-southeast-2.amazonaws.com` |

3. **Security Note**: These secrets are encrypted by GitHub and only accessible during workflow runs.
4. Workflow validates all secrets are present and fails fast with clear error messages if missing.

### 💻 Local Development Setup

Use Environment Variables (recommended):

```bash
export AWS_ACCOUNT_ID="123456789012"
export AWS_REGION="ap-southeast-2"
export AWS_IAM_ROLE_ARN="arn:aws:iam::123456789012:role/github-actions-role"
export AWS_ECR_REGISTRY="123456789012.dkr.ecr.ap-southeast-2.amazonaws.com"
```

**⚠️ Important**: Config files are not provided. Use env vars locally; GitHub Secrets in CI/CD.

## Files

- `aws.json`: Actual configuration (should not be committed if contains real values)
- `aws.example.json`: Example configuration (safe to commit)
- `aws.json.template`: Template with environment variable placeholders
- `aws.schema.json`: JSON schema for validation

## BigTech Security Principles Applied

### 1. Zero-Trust Architecture
- CI/CD workflows **never** read config files
- All production configs come from GitHub Secrets
- Fail-fast if secrets are missing (no silent fallbacks)

### 2. Separation of Concerns
- **CI/CD**: Uses GitHub Secrets only (encrypted, access-controlled)
- **Local Dev**: Uses environment variables

### 3. Defense in Depth
- Config files in `.gitignore` (prevent accidental commits)
- GitHub Secret scanning (detect leaked secrets)
- Masked logging (sensitive values never appear in logs)
- OIDC authentication (no long-lived credentials)

### 4. Clear Error Messages
If secrets are missing, workflow shows:
- ❌ List of missing secrets
- 📋 Step-by-step setup instructions
- 🔒 Security rationale

## Validation

### Local Development
Validate environment is set correctly:
```bash
env | rg "^AWS_(ACCOUNT_ID|REGION|IAM_ROLE_ARN|ECR_REGISTRY)="
```

### CI/CD
- ✅ Secrets format validation (regex patterns)
- ✅ All secrets presence check
- ✅ No config file validation (files not used)

## Troubleshooting

### Workflow fails with "Missing required GitHub Secrets"
1. Go to Repository Settings → Secrets and variables → Actions
2. Verify all 4 secrets are added with correct names
3. Check secret values are not empty
4. Re-run the workflow

### Local scripts can't find AWS settings
1. Verify env vars are exported in your shell/profile
2. Print vars: `echo $AWS_ACCOUNT_ID $AWS_REGION`
3. For Windows PowerShell, use: `$env:AWS_REGION = "ap-southeast-2"`


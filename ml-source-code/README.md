# H&M Fashion Recommendation - ML Platform

> Enterprise-grade Machine Learning Monorepo for Fashion Recommendation System

[![CI/CD](https://github.com/your-org/h&m_deeplearning/actions/workflows/build-inference-gitops.yml/badge.svg)](https://github.com/your-org/h&m_deeplearning/actions)
[![Python](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Getting Started](#getting-started)
- [Development](#development)
- [CI/CD](#cicd)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Contributing](#contributing)

## 🎯 Overview

This repository implements a production-ready Machine Learning platform for fashion recommendation, following enterprise monorepo patterns and BigTech ML platform standards. The system orchestrates a complete ML pipeline from data ingestion to model serving, with automated CI/CD, GitOps integration, and immutable deployment strategies.

### Key Features

- 🏗️ **Monorepo Architecture**: Unified codebase for all ML components with shared tooling
- 🔒 **Security-First**: OIDC authentication, zero-trust config management, encrypted secrets
- 🚀 **Immutable Deployments**: SHA-based tagging, reproducible builds, zero-downtime updates
- 🔄 **GitOps Integration**: Automated ArgoCD sync, declarative infrastructure
- 📦 **Container-First**: All components containerized with optimized Docker images
- ⚡ **Smart CI/CD**: Change detection, parallel builds, incremental deployments
- 📊 **ML Pipeline**: End-to-end pipeline from raw data to production inference

## 🏛️ Architecture

### ML Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ML Platform Pipeline                         │
│                   (End-to-End ML Workflow)                      │
└─────────────────────────────────────────────────────────────────┘

    External Data Sources
            │
            ▼
┌──────────────────────┐
│   Data Ingestion     │
│   (Raw S3 Storage)   │
│   S3: raw/           │
└──────────────────────┘
            │
            ▼
┌──────────────────────┐
│  Data Processing     │
│  (Clean & Transform) │
│  S3: processed/      │
└──────────────────────┘
            │
            ├─────────────────┐
            ▼                 ▼
┌──────────────────────┐  ┌──────────────────────┐
│    Data EDA          │  │    Model Training    │
│  (Exploratory        │  │  (ML Model Training) │
│   Analysis)          │  │  S3: artifacts/      │
│  (Reports)           │  └──────────────────────┘
└──────────────────────┘            │
                                    │
                                    ▼
                          ┌──────────────────────┐
                          │  Model Artifacts     │
                          │  (Stored in S3)      │
                          └──────────────────────┘
                                    │
                                    ▼
                          ┌──────────────────────┐
                          │   Inference Service  │
                          │   (FastAPI / REST)   │
                          │   (Real-time Predict)│
                          └──────────────────────┘
                                    │
                                    ▼
                          Production API Endpoints
```

### Component Flow

1. **Data Ingestion** → Collect raw data from multiple sources → Store in S3 `raw/`
2. **Data Processing** → Clean, transform, and normalize data → Store in S3 `processed/`
3. **Data EDA** → Perform exploratory data analysis on processed data → Generate reports
4. **Model Training** → Train ML models on processed data → Generate model artifacts → Store in S3 `artifacts/`
5. **Inference Service** → Load trained models from artifacts → Serve predictions via REST API

## 📦 Components

### 1. Data Ingestion (`components/data_ingestion/`)

**Purpose**: Collect raw data from multiple sources and store in S3 raw bucket.

**Features**:
- Multi-source data collection
- S3 raw bucket storage
- Configurable ingestion schedules
- Data validation and schema enforcement

**Input**: External data sources  
**Output**: S3 `raw/` prefix

### 2. Data Processing (`components/data_processing/`)

**Purpose**: Transform raw data into processed format for ML training.

**Features**:
- Data cleaning and normalization
- Feature engineering
- Schema validation
- Incremental processing support

**Input**: S3 `raw/` prefix  
**Output**: S3 `processed/` prefix

### 3. Data EDA (`components/data_eda/`)

**Purpose**: Exploratory Data Analysis and statistical insights.

**Features**:
- Automated statistical analysis
- Visualization generation
- Data quality reports
- Distribution analysis

**Input**: S3 `processed/` prefix  
**Output**: EDA reports and visualizations

### 4. Training (`components/train/`)

**Purpose**: Train machine learning models on processed data.

**Features**:
- Model training orchestration
- Hyperparameter tuning
- Model versioning
- Artifact management

**Input**: S3 `processed/` prefix  
**Output**: Model artifacts in S3 `artifacts/` prefix

### 5. Inference (`components/inference/`)

**Purpose**: Serve trained models via REST API for real-time predictions.

**Features**:
- FastAPI-based REST API
- Health check endpoints
- Model loading from S3
- Request/response validation
- Horizontal scaling support

**API Endpoints**:
- `GET /healthz` - Health check and service status
- `POST /predict` - Prediction endpoint

**Input**: Model artifacts from S3  
**Output**: REST API predictions

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.10+
- **Docker**: 20.10+
- **AWS CLI**: 2.0+ (for local development)
- **Make**: (optional, for convenience commands)

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/h&m_deeplearning.git
   cd h&m_deeplearning
   ```

2. **Configure AWS credentials** (for local development):
   ```bash
   export AWS_ACCOUNT_ID="123456789012"
   export AWS_REGION="ap-southeast-2"
   export AWS_IAM_ROLE_ARN="arn:aws:iam::123456789012:role/dev-role"
   export AWS_ECR_REGISTRY="123456789012.dkr.ecr.ap-southeast-2.amazonaws.com"
   ```

3. **Build a component locally**:
   ```bash
   # Using Makefile
   make build-component COMPONENT=inference
   
   # Or directly with Docker
   cd components/inference
   docker build -t inference:local .
   ```

4. **Run a component**:
   ```bash
   docker run -p 8080:8080 \
     -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
     -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
     -e AWS_REGION=$AWS_REGION \
     inference:local
   ```

5. **Test the inference API**:
   ```bash
   curl http://localhost:8080/healthz
   ```

## 💻 Development

### Project Structure

```
.
├── components/              # ML components
│   ├── data_ingestion/     # Data collection component
│   │   ├── src/           # Source code
│   │   ├── Dockerfile     # Container definition
│   │   ├── requirements.txt
│   │   └── config.yaml    # Component config
│   ├── data_processing/    # Data transformation
│   ├── data_eda/           # Exploratory analysis
│   ├── train/              # Model training
│   └── inference/          # Model serving
├── config/                 # Configuration files
│   ├── aws.schema.json    # AWS config schema
│   └── README.md          # Config documentation
├── docs/                   # Documentation
│   └── workflows/         # CI/CD documentation
├── .github/workflows/      # GitHub Actions
├── Makefile               # Build automation
├── pyproject.toml         # Python project config
└── README.md
```

### Adding a New Component

1. **Create component directory**:
   ```bash
   mkdir -p components/new_component/src
   ```

2. **Add component files**:
   - `Dockerfile` - Container definition
   - `requirements.txt` - Python dependencies
   - `config.yaml` - Component configuration
   - `src/main.py` - Component entry point

3. **Update Makefile** (optional):
   Add component to `COMPONENTS` variable

4. **Update CI/CD workflow**:
   Add component name to detection regex in `.github/workflows/build-and-push-ecr.yml`

5. **Create ECR repository**:
   ```bash
   aws ecr create-repository \
     --repository-name ml-fashion-recommender/new_component \
     --region ap-southeast-2
   ```

### Code Quality

The project uses standard Python tooling:

- **Black**: Code formatting (`line-length=100`)
- **isort**: Import sorting (Black-compatible)
- **pylint**: Static analysis
- **mypy**: Type checking
- **pytest**: Testing framework

Format code:
```bash
black components/
isort components/
```

## 🔄 CI/CD

### Workflow Overview

The CI/CD pipeline implements enterprise-grade practices:

- **Change Detection**: Only builds components that changed
- **Parallel Builds**: Matrix strategy for concurrent builds
- **Immutable Tags**: SHA-based tagging for reproducibility
- **GitOps Integration**: Automated ArgoCD sync
- **Security**: OIDC authentication, encrypted secrets

### Workflow: Build and Push to ECR

**Trigger**: Push/PR to `main` or `develop` branches

**Jobs**:
1. **detect-changes**: Identifies changed components via git diff
2. **build-and-push**: Builds and pushes Docker images to ECR

**Image Tagging Strategy** (Immutable BigTech Standard):

| Branch/Event | Primary Tag | Additional Tags |
|-------------|-------------|-----------------|
| `main` | `main-<full-sha>` | `main-<short-sha>`, `main-latest` |
| `develop` | `develop-<full-sha>` | `develop-<short-sha>`, `develop-latest` |
| Pull Request | `pr-<number>-<full-sha>` | `pr-<number>-<short-sha>`, `pr-<number>` |
| Feature Branch | `<branch>-<full-sha>` | `<branch>-<short-sha>` |

**Why Immutable Tags?**
- ✅ Reproducibility: Exact version tracking
- ✅ Rollback: Instant version reversion
- ✅ Auditability: Clear deployment history
- ✅ No race conditions: Unique tags prevent conflicts

### Workflow: Build Inference and Update GitOps

**Trigger**: Changes to `components/inference/` or workflow file

**Jobs**:
1. **build-push-and-update-gitops**:
   - Builds inference Docker image
   - Pushes to ECR with immutable tags
   - Updates GitOps repository with new image tag
   - Triggers ArgoCD auto-sync

**GitOps Integration**:
- Automatically updates `apps/ml-recommendation-inference/overlays/{production|staging}/kustomization.yaml`
- ArgoCD detects changes and syncs deployment
- Zero-downtime rolling updates

### GitHub Secrets Setup

**Required Secrets** (Repository Settings → Secrets and variables → Actions):

| Secret Name | Description | Example |
|------------|-------------|---------|
| `AWS_ACCOUNT_ID` | AWS Account ID (12 digits) | `123456789012` |
| `AWS_REGION` | AWS Region | `ap-southeast-2` |
| `AWS_IAM_ROLE_ARN` | IAM Role ARN for OIDC | `arn:aws:iam::123456789012:role/github-actions-ecr-role` |
| `AWS_ECR_REGISTRY` | ECR Registry URL | `123456789012.dkr.ecr.ap-southeast-2.amazonaws.com` |
| `GITOPS_REPO_TOKEN` | GitOps repo access token | `ghp_xxxxxxxxxxxx` |

## 📊 Deployment

### ECR Registry

All images are stored in ECR under the namespace:
```
<account>.dkr.ecr.<region>.amazonaws.com/ml-fashion-recommender/<component>:<tag>
```

### GitOps Deployment (Production)

The inference service is deployed via GitOps using ArgoCD:

1. **CI/CD builds and pushes image** to ECR
2. **CI/CD updates GitOps repo** with new image tag
3. **ArgoCD detects change** and syncs deployment
4. **Kubernetes rolling update** with zero downtime

See [`hm-mlops-gitops`](../hm-mlops-gitops) repository for GitOps configuration.

## ⚙️ Configuration

### Security-First Configuration

**Priority Order** (Highest to Lowest):
1. **GitHub Secrets** (CI/CD) - Recommended for production 🔐
2. **Environment Variables** (Local development)
3. **Config Files** (Local fallback only)

**CI/CD**: Uses GitHub Secrets exclusively (zero-trust approach)  
**Local Dev**: Uses environment variables or `config/aws.json`

### Configuration Files

- `config/aws.schema.json`: JSON schema for validation
- `config/README.md`: Detailed configuration documentation

**⚠️ Important**: Never commit sensitive values. Use GitHub Secrets for production.

### Component Configuration

Each component has its own `config.yaml`:
```yaml
component:
  name: inference
  version: "1.0.0"

aws:
  s3_bucket: "${S3_DATA_LAKE_BUCKET}"
  artifacts_prefix: "${S3_ARTIFACTS_PREFIX}"

inference:
  api_host: "0.0.0.0"
  api_port: 8080

logging:
  level: "INFO"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests for specific component
pytest components/inference/tests/

# Run with coverage
pytest --cov=components/inference/src
```

### Component Testing

Each component should include:
- Unit tests (`tests/test_*.py`)
- Integration tests (if applicable)
- API tests (for inference service)

## 📚 Documentation

- [Configuration Guide](config/README.md)
- [CI/CD Workflows](docs/workflows/build-and-push-ecr.md)
- [Component Development Guide](docs/COMPONENT_DEVELOPMENT.md) (TODO)

## 🤝 Contributing

### Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** and commit:
   ```bash
   git commit -m "feat: add new feature"
   ```

3. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **CI/CD automatically**:
   - Builds changed components
   - Runs tests
   - Updates preview environment (if configured)

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### Code Review Process

1. All PRs require at least one approval
2. CI/CD must pass before merge
3. Code must follow style guidelines
4. Tests must be added for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **ML Engineering**: Model development and training
- **Platform Engineering**: Infrastructure and CI/CD
- **DevOps**: Deployment and operations

## 🔗 Related Repositories

- [GitOps Configuration](../hm-mlops-gitops) - ArgoCD and Kubernetes manifests
- [Infrastructure as Code](../hm-infra-live) - Terraform infrastructure

## 📞 Support

For issues and questions:
- Create an issue in this repository
- Contact the ML Platform team
- Check documentation in `docs/` directory

---

**Built with ❤️ by the H&M ML Platform Team**

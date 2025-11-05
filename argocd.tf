# =============================================================================
# ArgoCD Installation and Configuration
# =============================================================================

# Random password for ArgoCD admin
resource "random_password" "argocd_admin_password" {
  count   = var.argocd_enabled ? 1 : 0
  length  = 16
  special = true
}

# Kubernetes Namespace for ArgoCD
resource "kubernetes_namespace" "argocd" {
  count = var.argocd_enabled ? 1 : 0

  metadata {
    name = var.argocd_namespace
    labels = {
      name = var.argocd_namespace
    }
  }

  depends_on = [module.eks]
}

# Helm Release for ArgoCD
resource "helm_release" "argocd" {
  count = var.argocd_enabled ? 1 : 0

  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  version    = "7.6.0"
  namespace  = kubernetes_namespace.argocd[0].metadata[0].name

  values = [
    yamlencode({
      server = {
        service = {
          type = "LoadBalancer"
        }
        ingress = {
          enabled = false
        }
        extraArgs = ["--insecure"]
        resources = {
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
          limits = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
      }
      controller = {
        resources = {
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
          limits = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
      }
      repoServer = {
        resources = {
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
          limits = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
      }
      applicationSet = {
        enabled = true
        resources = {
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
          limits = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
      }
      configs = {
        params = {
          "server.insecure" = true
        }
        secret = {
          argocdServerAdminPassword = random_password.argocd_admin_password[0].result
        }
      }
    })
  ]

  depends_on = [
    kubernetes_namespace.argocd,
    module.eks
  ]
}

# Data source for ArgoCD Server Service (to get LoadBalancer endpoint)
data "kubernetes_service" "argocd_server" {
  count = var.argocd_enabled ? 1 : 0

  metadata {
    name      = "argocd-server"
    namespace = var.argocd_namespace
  }

  depends_on = [helm_release.argocd]
}

# ArgoCD Root Application - Bootstrap GitOps
resource "kubectl_manifest" "argocd_root_application" {
  count = var.argocd_enabled ? 1 : 0

  yaml_body = yamlencode({
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "Application"
    metadata = {
      name      = "gitops-root"
      namespace = var.argocd_namespace
      finalizers = [
        "resources-finalizer.argocd.argoproj.io"
      ]
      labels = {
        "app.kubernetes.io/name"      = "gitops-root"
        "app.kubernetes.io/part-of"   = "gitops-platform"
      }
    }
    spec = {
      project = "default"
      source = {
        repoURL        = var.gitops_repo_url
        targetRevision = "HEAD"
        path           = var.gitops_repo_path
      }
      destination = {
        server    = "https://kubernetes.default.svc"
        namespace = var.argocd_namespace
      }
      syncPolicy = {
        automated = {
          prune      = true
          selfHeal   = true
          allowEmpty = false
        }
        syncOptions = [
          "CreateNamespace=true",
          "PrunePropagationPolicy=foreground",
          "PruneLast=true"
        ]
        retry = {
          limit = 5
          backoff = {
            duration    = "5s"
            factor      = 2
            maxDuration = "3m"
          }
        }
      }
      ignoreDifferences = [
        {
          group         = "argoproj.io"
          kind          = "Application"
          jsonPointers  = ["/status"]
        }
      ]
    }
  })

  depends_on = [
    helm_release.argocd,
    module.eks
  ]
}


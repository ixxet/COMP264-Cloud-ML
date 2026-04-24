# SafeView Kubernetes And GitOps Notes

This directory is the Kustomize deployment entry point for SafeView. It can be
rendered locally with `kubectl kustomize`, applied manually with
`kubectl apply -k`, or reconciled by Flux from the GitHub repository.

## What This Path Deploys

| Resource | Purpose |
|---|---|
| `namespace.yaml` | Creates the `safeview` namespace. |
| `api-deployment.yaml` | Runs the Chalice API container with AWS/vLLM configuration, health probes, resource limits, and Secret-based credentials. |
| `api-service.yaml` | Provides an internal ClusterIP service for the API. |
| `web-deployment.yaml` | Runs the nginx frontend container and configures the internal API upstream. |
| `web-service.yaml` | Exposes the frontend through a LoadBalancer service. |
| `kustomization.yaml` | Assembles the resources and rewrites local image names to GHCR image references. |

## Required External Secrets

Secrets are intentionally not committed.

| Secret | Required keys | Purpose |
|---|---|---|
| `safeview-aws-credentials` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Allows the API pod to call S3, Rekognition, and Comprehend. |
| `safeview-ghcr-pull` | Docker registry auth JSON | Allows Kubernetes to pull private GHCR images. |

`aws-credentials.secret.example.yaml` documents the expected Secret shape with
placeholder values only.

## Images

`kustomization.yaml` expects these images:

```text
ghcr.io/ixxet/safeview-api:ai-review-20260424
ghcr.io/ixxet/safeview-web:ai-review-20260424
```

For a stronger production GitOps flow, replace the demonstration tag with
release tags or image digests after the build process is finalized.

## vLLM Review Configuration

The API Deployment enables the optional local AI review layer with:

```text
SAFEVIEW_LLM_ENABLED=true
SAFEVIEW_LLM_BASE_URL=http://vllm.ai.svc.cluster.local:8000/v1
SAFEVIEW_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.3
```

The LLM receives only the structured SafeView report. Rekognition and Comprehend
remain the authoritative moderation services.

## Manual Verification

Render manifests:

```bash
kubectl kustomize k8s
```

Apply manifests:

```bash
kubectl apply -k k8s
```

Check runtime state:

```bash
kubectl -n safeview get pods,svc
kubectl -n safeview logs deploy/safeview-api
```

## Flux Wiring

Flux should reconcile this directory from the repository path:

```text
Assignments/Final_Project/SafeView/k8s
```

The platform repository can define a Flux `GitRepository` and `Kustomization`
that points at this path. Flux then handles ongoing reconciliation, while Talos
provides the Kubernetes host OS and Kubernetes runs the SafeView workloads.

Recommended GitOps gates:

| Gate | Check |
|---|---|
| Image gate | GHCR images exist and the pull Secret works before reconciliation. |
| Secret gate | AWS runtime Secret exists before the API Deployment is applied. |
| Manifest gate | `kubectl kustomize k8s` renders successfully before commit. |
| Health gate | API `/health` and frontend `/` probes pass after rollout. |

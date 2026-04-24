# Final Project - SafeView

SafeView is the COMP 264 final project: a content moderation web application
that combines a static browser frontend with a Python Chalice backend, Amazon
S3 storage, Amazon Rekognition image analysis, Amazon Comprehend sentiment
analysis, and an optional vLLM AI review layer for Kubernetes deployment.

The maintained project source is in [SafeView/](SafeView/).

| Path | Purpose |
|---|---|
| [SafeView/README.md](SafeView/README.md) | Main academic/recruiter-facing landing page with architecture, storage, framework, file inventory, and deployment strategy. |
| [SafeView/safeview/](SafeView/safeview/) | Chalice backend source for AWS Lambda/API Gateway and containerized API execution. |
| [SafeView/SafeView_Frontend_Code/](SafeView/SafeView_Frontend_Code/) | Static frontend source and nginx container packaging. |
| [SafeView/k8s/](SafeView/k8s/) | Kustomize-ready Kubernetes manifests for manual deployment or Flux reconciliation. |
| [SafeView/compose.yaml](SafeView/compose.yaml) | Local Docker Compose stack for frontend/API verification. |
| [SafeView/diagrams/](SafeView/diagrams/) | Mermaid diagram sources for infrastructure, request sequence, and deployment topology. |
| [SafeView/SafeView_Project_Report.docx](SafeView/SafeView_Project_Report.docx) | Final written report. |
| [SafeView/SafeView_Presentation.pptx](SafeView/SafeView_Presentation.pptx) | Final presentation deck. |

## Deployment Summary

SafeView supports three deployment paths without changing the core AWS ML
integration:

| Path | Description |
|---|---|
| AWS-native Chalice | Deploys the backend to API Gateway and Lambda while using S3, Rekognition, and Comprehend. |
| Docker Compose | Runs the nginx frontend and Chalice API container together for local verification. |
| Kubernetes / Flux | Runs the frontend and API as Kubernetes Deployments from GHCR images, enables vLLM review, and can be reconciled from the `k8s/` path in Git. |

The Kubernetes manifests expect runtime credentials to be created separately as
a `safeview-aws-credentials` Secret. If GHCR images remain private, the cluster
also needs a `safeview-ghcr-pull` image pull Secret. Real credentials are not
stored in this repository.

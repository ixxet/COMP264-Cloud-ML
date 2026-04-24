# Final Project – SafeView

SafeView is a content moderation web application for COMP 264. It combines a
static browser frontend with a Python Chalice backend that stores uploads in S3
and calls AWS Rekognition and Comprehend.

Project location:

- `SafeView/safeview/` – Chalice backend
- `SafeView/SafeView_Frontend_Code/` – static frontend and nginx container
- `SafeView/k8s/` – Kubernetes manifests for Flux
- `SafeView/compose.yaml` – local Docker Compose stack
- `SafeView/README.md` – detailed architecture, storage, framework, and deployment notes

The Kubernetes manifests expect a `safeview-aws-credentials` Secret to be
created separately. Do not commit real AWS credentials.

For local Docker Compose, the stack mounts `~/.aws` read-only and defaults to
`AWS_PROFILE=safeview`, so no access keys need to be written into the project.

Current runtime: SafeView is running locally on macOS through Docker Compose at
`http://127.0.0.1:8080`. It is not currently deployed as a pod on the Talos
cluster.

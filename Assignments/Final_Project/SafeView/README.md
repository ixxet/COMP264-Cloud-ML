# SafeView Final Project

SafeView is a full-stack content moderation application for COMP 264. It lets a
user upload an image, stores the image in S3, runs AWS Rekognition moderation
and OCR, runs AWS Comprehend sentiment analysis on detected text, and returns a
downloadable moderation report.

## Current Runtime Status

| Target | Status | What this means |
|---|---|---|
| macOS Docker Compose | Optional local mode | The app can run on this Mac through Docker Desktop/Compose at `http://127.0.0.1:8080`, but this is no longer the primary runtime. |
| AWS serverless | Deployed | The Chalice backend was also deployed to AWS Lambda/API Gateway for the assignment-compatible path. |
| Talos Kubernetes | Running now | The app is deployed in the `safeview` namespace on `admin@talos-tower` and exposed through LoadBalancer IP `192.168.50.206`. |
| Flux GitOps | Manifests ready | The `k8s/` folder is ready for Flux, but the current Talos deployment was applied directly with `kubectl apply -k`. |

Talos does not pull YAML from GitHub by itself. Talos runs the Kubernetes node.
Flux runs inside Kubernetes and reconciles YAML from GitHub into the cluster.
Kubernetes then pulls the referenced container images from the registry.

## What We Changed

| Area | Work completed |
|---|---|
| Project structure | Moved the final project into `Assignments/Final_Project/SafeView` so it sits beside Assignments 1 and 2 in the course repo. |
| Frontend structure | Unburied the frontend and split the one-file app into `index.html`, `styles.css`, `app.js`, and runtime `config.js`. |
| Frontend polish | Added responsive layout fixes, safer API configuration, better error handling, threshold re-run behavior, and nginx container support. |
| Backend validation | Added stricter input checks for threshold values, base64 image payloads, filenames, and cached moderation labels. |
| Backend comments | Added detailed comments/docstrings across the Chalice backend modules so the orchestration, validation, storage, and reporting logic are easier to explain. |
| AWS migration | Updated the app to use bucket `safeview-images-izzet-225989375368-dev` in `us-east-1`. |
| AWS deployment | Deployed the backend as `safeview-dev` on Lambda with API Gateway URL `https://si7yjdzgq8.execute-api.us-east-1.amazonaws.com/api/`. |
| Packaging fix | Removed runtime dependencies from Lambda `requirements.txt` so Chalice deploys a small package instead of timing out while uploading vendored libraries. |
| Docker packaging | Added API and frontend Dockerfiles plus `compose.yaml` for local containerized execution. |
| Kubernetes packaging | Added Flux/Kustomize-ready manifests under `k8s/`. |
| Repo landing page | Updated the course root `README.md` so SafeView appears as the final project beside Assignments 1 and 2. |

## Application Architecture

```text
Browser
  |
  | static HTML/CSS/JS
  v
safeview-web (nginx)
  |
  | /api reverse proxy
  v
safeview-api (Python Chalice local server in container)
  |
  | boto3
  v
AWS S3 + Rekognition + Comprehend
```

The same backend can also run in AWS-native mode:

```text
Browser or static frontend
  |
  v
API Gateway
  |
  v
AWS Lambda running Chalice app
  |
  v
S3 + Rekognition + Comprehend
```

## Frontend Framework Options

| Option | Fit | Notes |
|---|---|---|
| Current: static HTML/CSS/JS | Best for this assignment | No build step, easy to submit, easy to serve from nginx, S3 static hosting, or any web server. |
| Vite + React | Good future upgrade | Better component structure if the app grows, but adds build tooling and dependency management. |
| Next.js | Too heavy for this project | Useful for larger apps with routing, auth, server rendering, or API routes, but unnecessary here. |
| Open WebUI integration | Not needed now | Your platform has Open WebUI for LLM chat, but SafeView is an image moderation workflow, not a chat UI. |

Current choice: keep the frontend static and containerize it with nginx. This is
the lowest-risk option for the assignment and for Flux deployment.

## Backend Framework Options

| Option | Fit | Notes |
|---|---|---|
| Current: AWS Chalice | Best for assignment compatibility | Matches the project instructions and deploys cleanly to API Gateway/Lambda. |
| Chalice local in Docker | Good bridge to Kubernetes | Lets the same backend code run as a container on macOS or Talos. |
| FastAPI | Best future Kubernetes-native backend | Better if SafeView becomes a long-lived platform service with OpenAPI docs, async endpoints, auth, and observability. |
| Flask | Acceptable but less useful | Simple, but FastAPI is a better modern choice for a container-first API. |

Current choice: keep Chalice so the AWS implementation stays intact, while
Docker lets the same app run on your local or Talos platform.

## Storage Options

| Storage option | Current status | Recommendation |
|---|---|---|
| AWS S3 | Used now | Best current option. Required by the assignment and already integrated. |
| S3 audit logs | Used now | SafeView writes lightweight audit JSON records under `logs/<session>/audit.json`. |
| Browser memory | Used now | The frontend keeps the latest report in memory for threshold re-filtering. |
| Local filesystem | Not recommended | Fine for temporary development only; not durable or portable across pods. |
| Kubernetes PVC | Optional | Useful only if you want local cluster storage, but it does not replace Rekognition/Comprehend. |
| MinIO on Talos | Optional future path | Could replace S3-compatible object storage, but would require code/config changes and would move away from the AWS assignment design. |
| Postgres | Optional future metadata store | Your platform already has Postgres; it could store report metadata, users, or analysis history later. |
| Qdrant/TEI/Mem0 | Not needed now | Useful for semantic memory/RAG, not for image upload storage. Could be added later for policy retrieval or report search. |

Current choice: keep images and audit logs in AWS S3.

## Deployment Strategies

### 1. macOS Docker Compose - current running mode

Use this when developing or demoing locally on the Mac.

```bash
cd Assignments/Final_Project/SafeView
AWS_PROFILE=safeview docker compose up --build
```

Frontend:

```text
http://127.0.0.1:8080
```

The API container is not exposed directly to the host. The web container proxies
`/api` to the API container over the internal Compose network.

### 2. AWS-native Chalice deployment - assignment-compatible mode

Use this when showing the professor the serverless AWS implementation.

```bash
cd Assignments/Final_Project/SafeView/safeview
AWS_PROFILE=safeview chalice deploy --stage dev
```

Current deployed API:

```text
https://si7yjdzgq8.execute-api.us-east-1.amazonaws.com/api/
```

This path uses Lambda, API Gateway, S3, Rekognition, and Comprehend.

### 3. Talos Kubernetes + Flux - platform mode

Use this when hosting SafeView on your tower platform.

Required first:

1. Push images to GHCR.
2. Create a `safeview-aws-credentials` Secret in the cluster.
3. Create a `safeview-ghcr-pull` image pull Secret if the GHCR packages are private.
4. Add the `k8s/` path to the Flux repo or create a Flux Kustomization that points to it.
5. Expose `safeview-web` through your existing Cilium load-balancer pattern.

Images expected by `k8s/kustomization.yaml`:

```text
ghcr.io/ixxet/safeview-api:latest
ghcr.io/ixxet/safeview-web:latest
```

Push commands:

```bash
docker login ghcr.io
docker push ghcr.io/ixxet/safeview-api:latest
docker push ghcr.io/ixxet/safeview-web:latest
```

Render manifests locally:

```bash
kubectl kustomize k8s
```

Apply manually for a quick test:

```bash
kubectl apply -k k8s
```

Current Talos URL:

```text
http://192.168.50.206
```

Flux version: point a Flux `Kustomization` at
`Assignments/Final_Project/SafeView/k8s` in the GitHub repo.

## Platform Fit

| Platform component | How SafeView would use it |
|---|---|
| Talos | Hosts the Kubernetes node. It does not run SafeView directly; Kubernetes pods do. |
| Kubernetes | Runs `safeview-web` and `safeview-api` as Deployments. |
| Flux | Pulls the SafeView manifests from GitHub and reconciles them into the cluster. |
| Cilium | Exposes `safeview-web` through a `LoadBalancer` Service, matching the pattern already used by Open WebUI, Grafana, and Fraud Sentinel. |
| Grafana/Prometheus | Can monitor pod health, CPU, memory, and nginx/API availability. |
| Postgres | Optional future database for durable report metadata/history. |
| vLLM/Open WebUI/LangGraph | Not required for current SafeView. Useful only if you later add LLM explanations, agent workflows, or moderation policy assistance. |

## Current Answer: Mac or Talos?

Right now SafeView is running on the Talos tower in Kubernetes.

It is deployed in namespace `safeview` with two pods:

- `safeview-web`
- `safeview-api`

The public LAN endpoint is:

```text
http://192.168.50.206
```

The Mac Docker Compose path remains useful for local development, but it is not
the primary runtime after the Talos deployment.

## Verification Performed

- `docker compose build` completed for `safeview-api` and `safeview-web`.
- `docker compose ps` showed both containers running locally during local testing.
- `curl http://192.168.50.206/` returned the frontend from Talos.
- `curl http://192.168.50.206/api/health` returned `{"status":"ok","service":"safeview"}` from Talos.
- `curl http://192.168.50.206/api/analyze/threshold` returned a valid SafeView report from Talos.
- `kubectl kustomize k8s` rendered valid Kubernetes YAML.
- Secret scans found no copied AWS access key or secret in the final project path.

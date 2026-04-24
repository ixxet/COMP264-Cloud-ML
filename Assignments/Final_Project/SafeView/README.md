# SafeView - COMP 264 Final Project

SafeView is a full-stack image moderation application built for COMP 264 Cloud
Machine Learning. The application accepts a JPEG or PNG image, stores the image
privately in Amazon S3, runs Amazon Rekognition moderation and OCR, applies
Amazon Comprehend sentiment analysis to detected text, and returns a structured
JSON moderation report through a browser interface.

The project demonstrates managed cloud ML orchestration rather than custom model
training. Its main engineering goal is to show how a small application can bind
cloud storage, AI service calls, API validation, report generation, container
packaging, and Kubernetes deployment assets into one reproducible system.

## Academic Positioning

| Requirement area | SafeView implementation |
|---|---|
| Managed AI services | Amazon Rekognition provides moderation labels and text detection; Amazon Comprehend scores sentiment for detected text. |
| Cloud storage | Amazon S3 stores uploaded images and lightweight audit records under UUID-scoped keys. |
| Serverless backend | AWS Chalice provides the API source used for Lambda/API Gateway deployment and local/container execution. |
| Web interface | Static HTML, CSS, and JavaScript provide upload, preview, threshold control, report display, and report download. |
| Deployment packaging | Docker, Docker Compose, Kubernetes manifests, and Kustomize support repeatable local and cluster deployments. |
| Documentation | Design documents, architecture diagrams, interaction diagrams, report, presentation, and source README files explain the system. |

## Architecture Diagrams

Mermaid source files are stored in [diagrams/](diagrams/):

| Diagram | Purpose |
|---|---|
| [application-infrastructure.mmd](diagrams/application-infrastructure.mmd) | End-to-end application infrastructure and AWS service boundaries. |
| [request-sequence.mmd](diagrams/request-sequence.mmd) | Request flow for full analysis and threshold re-filtering. |
| [deployment-topology.mmd](diagrams/deployment-topology.mmd) | Packaging and deployment path from GitHub/GHCR to Kubernetes and AWS. |

## How SafeView Works

1. The browser validates the selected image type and size before upload. The
   client accepts JPEG and PNG files up to 5 MB.
2. The frontend converts the image to base64 and sends `POST /analyze` with the
   filename and confidence threshold.
3. The Chalice API validates the request body, threshold value, base64 payload,
   filename, extension, file size, and file signature.
4. The backend stores the validated image in S3 under
   `uploads/<session_uuid>/<sanitised_filename>`.
5. Amazon Rekognition runs `DetectModerationLabels` and `DetectText` against the
   S3 object.
6. If OCR text exists, Amazon Comprehend runs `DetectSentiment` on the detected
   text.
7. The backend filters moderation labels using the selected confidence threshold
   and builds a structured report with verdict, summary, labels, OCR text, and
   sentiment scores.
8. The backend writes an audit record to S3 under
   `logs/<session_uuid>/audit.json`. The audit record excludes image content,
   detected text, user identifiers, and IP addresses.
9. The frontend renders the report and can download it as JSON.
10. Threshold re-runs call `POST /analyze/threshold` using cached label data, so
    threshold changes do not trigger new Rekognition or Comprehend calls.

## Technology Stack

| Layer | Technology | Role in SafeView |
|---|---|---|
| Browser UI | HTML5, CSS3, JavaScript | Static frontend for upload, image preview, threshold control, result rendering, and report download. |
| Frontend runtime | nginx | Serves static assets and reverse-proxies `/api` to the backend container in Docker/Kubernetes deployments. |
| API framework | AWS Chalice | Defines the REST API and keeps the AWS Lambda/API Gateway deployment path compatible with the assignment. |
| Backend language | Python 3.12 | Implements validation, orchestration, S3 storage, report construction, and error handling. |
| AWS SDK | boto3 / botocore | Calls S3, Rekognition, and Comprehend from the backend. |
| Object storage | Amazon S3 | Stores uploaded images and audit JSON records. |
| Vision ML | Amazon Rekognition | Detects visual moderation labels and OCR text in images. |
| NLP ML | Amazon Comprehend | Classifies sentiment for text detected inside images. |
| Serverless deployment | Lambda + API Gateway | AWS-native deployment target for the Chalice application. |
| Container packaging | Docker | Builds separate images for the API and frontend. |
| Local orchestration | Docker Compose | Runs the API and web containers together for local verification. |
| Cluster orchestration | Kubernetes | Runs `safeview-api` and `safeview-web` as Deployments with Services and probes. |
| GitOps path | Flux + Kustomize | Reconciles the `k8s/` manifest path from GitHub into a Kubernetes cluster. |
| Container registry | GitHub Container Registry | Stores `ghcr.io/ixxet/safeview-api` and `ghcr.io/ixxet/safeview-web` images. |
| Network exposure | Cilium LoadBalancer pattern | Exposes the web service in the Kubernetes lab environment. |
| External hosting path | Cloudflare DNS / Tunnel / Pages | Planned public presentation layer for a stable course/recruiter URL. |

## Framework Choices

| Area | Current choice | Reason |
|---|---|---|
| Frontend framework | Static HTML/CSS/JavaScript | Best fit for a focused assignment submission: no build step, easy to inspect, easy to host on nginx, S3 static hosting, Cloudflare Pages, or any web server. |
| Backend framework | AWS Chalice | Preserves the AWS serverless implementation while still allowing the same code to run locally or in a container. |
| Future frontend option | Vite + React | Useful if the UI grows into multiple screens, reusable components, auth, or persistent history. |
| Future backend option | FastAPI | Useful for a long-lived Kubernetes-native API with OpenAPI docs, richer middleware, auth, and observability. |

The current framework choice is intentionally conservative. Chalice keeps the
assignment-aligned AWS implementation intact, while Docker and Kubernetes add a
portable deployment option without rewriting the backend.

## Storage And State

| Storage location | Used for | Notes |
|---|---|---|
| Amazon S3 bucket | Uploaded images and audit logs | Configured bucket: `safeview-images-izzet-225989375368-dev`. |
| `uploads/<session_uuid>/...` | Private uploaded image object | The UUID groups each upload with its audit log. |
| `logs/<session_uuid>/audit.json` | Request audit metadata | Stores session id, timestamp, S3 key, verdict, and threshold only. |
| Browser memory | Latest moderation report | Enables threshold re-filtering without another AI service call. |
| JSON download | Portable report artifact | The browser can export the current report for submission evidence. |

SafeView does not currently require a relational database. A database such as
Postgres would become useful if the project later adds users, saved moderation
history, report search, analytics, or instructor-facing dashboards. MinIO or a
Kubernetes persistent volume could replace S3-like storage in a fully local
variant, but that would move away from the AWS managed-service assignment path.

## Quality Gates

The project uses explicit gates to keep the workflow predictable. A gate is a
decision point that allows valid work to continue and blocks unsafe or invalid
work before it reaches the next system boundary.

| Gate | Location | Purpose |
|---|---|---|
| Client file gate | `SafeView_Frontend_Code/app.js` | Blocks unsupported MIME types and oversized files before network upload. |
| API request gate | `safeview/app.py` | Rejects malformed JSON, missing fields, invalid base64, invalid thresholds, and bad cached label data. |
| Image validation gate | `safeview/chalicelib/validator.py` | Verifies extension, file size, and magic bytes before S3 upload. |
| Storage gate | `safeview/chalicelib/s3_handler.py` | Stores objects under controlled prefixes and uses private ACLs. |
| AI orchestration gate | `safeview/chalicelib/orchestrator.py` | Centralizes all Rekognition and Comprehend calls and normalizes their output. |
| Threshold gate | `safeview/app.py` and `safeview/chalicelib/orchestrator.py` | Constrains confidence thresholds to 50-99 and applies filtering consistently. |
| Deployment gate | `k8s/*.yaml` | Uses health probes, resource requests/limits, Secrets, and image pull credentials for cluster readiness. |

## Deployment Models

| Model | Purpose | Entry point |
|---|---|---|
| AWS-native serverless | Assignment-compatible cloud deployment with API Gateway and Lambda. | `safeview/.chalice/config.json` and `chalice deploy --stage dev`. |
| Local containers | Developer verification with both services running in Docker. | `compose.yaml`. |
| Kubernetes lab deployment | Self-hosted cluster deployment using container images and Kubernetes Services. | `k8s/kustomization.yaml`. |
| Flux GitOps deployment | Declarative reconciliation from GitHub into Kubernetes. | Flux Kustomization pointing at `Assignments/Final_Project/SafeView/k8s`. |
| Cloudflare public hosting | Planned public presentation URL for course and recruiter review. | Cloudflare DNS/Pages/Tunnel path selected during the hosting pass. |

### AWS-Native Deployment

```bash
cd Assignments/Final_Project/SafeView/safeview
AWS_PROFILE=safeview chalice deploy --stage dev
```

This path uses API Gateway, Lambda, S3, Rekognition, Comprehend, IAM, and
CloudWatch. It is the most direct match for an AWS-focused assignment review.

### Local Container Verification

```bash
cd Assignments/Final_Project/SafeView
AWS_PROFILE=safeview docker compose up --build
```

The web container exposes the frontend and proxies `/api` to the internal API
container. AWS credentials come from the local AWS profile mounted read-only by
Compose; no credentials are stored in the repository.

### Kubernetes And GitOps Deployment

The Kubernetes path uses two images:

```text
ghcr.io/ixxet/safeview-api:latest
ghcr.io/ixxet/safeview-web:latest
```

The cluster requires two externally managed Secrets:

| Secret | Purpose |
|---|---|
| `safeview-aws-credentials` | Provides AWS runtime credentials to the API pod. |
| `safeview-ghcr-pull` | Allows Kubernetes to pull private GHCR images. |

Manual rendering check:

```bash
kubectl kustomize k8s
```

Manual deployment check:

```bash
kubectl apply -k k8s
```

GitOps deployment uses the same `k8s/` folder. A Flux Kustomization in the
platform repository should point at this path after the images and Secrets are
available. Flux performs the cluster reconciliation; Talos provides the
immutable Kubernetes host OS, and Kubernetes runs the SafeView pods.

### Cloudflare Hosting Path

Cloudflare can provide the stable public URL after the internal cluster route is
validated. Two practical patterns are available:

| Pattern | Description |
|---|---|
| Cloudflare Tunnel to Kubernetes | Keeps the app running in Kubernetes and publishes the web service through a Cloudflare-managed tunnel and DNS record. |
| Cloudflare Pages plus API origin | Hosts the static frontend on Cloudflare Pages and points API traffic to either the AWS API Gateway URL or a tunnel-backed Kubernetes API route. |

The cleanest public demo path is usually Cloudflare Tunnel to the Kubernetes web
service because the current nginx frontend already proxies `/api` to the
backend inside the cluster.

## Meaningful File Inventory

### Project And Submission Files

| File | Purpose |
|---|---|
| `README.md` | Reviewer-facing landing page with architecture, workflow, technologies, storage, and deployment strategy. |
| `.env.example` | Documents runtime environment variables without storing secrets. |
| `SafeView_Project_Report.docx` | Final written report for the COMP 264 submission. |
| `SafeView_Presentation.pptx` | Slide deck for the final presentation. |
| `Docs/SafeView_Design_Document.docx` | Design specification and system rationale. |
| `Docs/SafeView_Rationale_Scope.docx` | Scope boundaries, assumptions, and design justification. |
| `Docs/SafeView_Research.docx` | Research notes supporting technology and service choices. |
| `Docs/SafeView_Architecture_Diagrams.pdf` | Original rendered architecture evidence. |
| `Docs/SafeView_Interaction_Diagrams.pdf` | Original rendered interaction-flow evidence. |
| `Docs/SafeView_Backend_Code.zip` | Archived backend code artifact from the assignment package; source files under `safeview/` are the maintained source of truth. |
| `diagrams/application-infrastructure.mmd` | Mermaid source for the infrastructure diagram. |
| `diagrams/request-sequence.mmd` | Mermaid source for the request and threshold re-run sequence. |
| `diagrams/deployment-topology.mmd` | Mermaid source for the deployment topology. |

### Frontend Files

| File | Purpose |
|---|---|
| `SafeView_Frontend_Code/index.html` | Defines the SafeView browser UI: header, upload panel, result panel, threshold controls, report sections, and script/style loading. |
| `SafeView_Frontend_Code/styles.css` | Controls responsive layout, typography, panels, upload states, confidence bars, verdict badges, and report presentation. |
| `SafeView_Frontend_Code/app.js` | Implements file validation, drag-and-drop, image preview, API calls, threshold re-filtering, report rendering, JSON download, and UI error handling. |
| `SafeView_Frontend_Code/config.js` | Provides runtime API base configuration for static hosting and containerized deployments. |
| `SafeView_Frontend_Code/Dockerfile` | Builds the nginx image that serves the frontend and applies runtime API proxy configuration. |
| `SafeView_Frontend_Code/.dockerignore` | Keeps unnecessary files out of the frontend image build context. |
| `SafeView_Frontend_Code/nginx/default.conf.template` | nginx template that serves static assets and proxies `/api/` to the backend service. |
| `SafeView_Frontend_Code/docker-entrypoint.d/40-safeview-config.sh` | Writes runtime frontend configuration when the nginx container starts. |

### Backend Files

| File | Purpose |
|---|---|
| `safeview/app.py` | Chalice application entry point. Defines `/health`, `/analyze`, `/analyze/threshold`, CORS responses, threshold parsing, cached-label validation, and orchestration calls. |
| `safeview/chalicelib/validator.py` | Validates uploaded images by size, extension, and magic bytes before storage or AI calls. |
| `safeview/chalicelib/s3_handler.py` | Owns S3 upload and audit-log writing, including UUID session folders and sanitized filenames. |
| `safeview/chalicelib/orchestrator.py` | Coordinates Rekognition moderation, Rekognition OCR, conditional Comprehend sentiment analysis, and threshold filtering. |
| `safeview/chalicelib/report.py` | Converts normalized AI results into the final report schema, verdict, and human-readable summary. |
| `safeview/chalicelib/__init__.py` | Marks `chalicelib` as a Python package for Chalice imports. |
| `safeview/.chalice/config.json` | Chalice stage configuration, including environment variables for bucket, region, debug mode, and default threshold. |
| `safeview/.chalice/dev-policy.json` | IAM policy used by Chalice for S3, Rekognition, and Comprehend permissions. |
| `safeview/requirements.txt` | Lambda deployment requirements kept minimal for Chalice packaging. |
| `safeview/requirements-container.txt` | Container runtime dependencies for running the Chalice app inside Docker/Kubernetes. |
| `safeview/Dockerfile` | Builds the Python API container and runs `chalice local` on port 8000. |
| `safeview/.dockerignore` | Keeps unnecessary backend files out of the API image build context. |

### Deployment Files

| File | Purpose |
|---|---|
| `compose.yaml` | Runs the API and web containers together for local verification, with `/api` proxied through nginx. |
| `k8s/kustomization.yaml` | Kustomize entry point that assembles namespace, Deployments, Services, and GHCR image references. |
| `k8s/namespace.yaml` | Creates the `safeview` namespace. |
| `k8s/api-deployment.yaml` | Runs the API pod, injects AWS credentials from a Secret, configures environment variables, health probes, and resource limits. |
| `k8s/api-service.yaml` | Provides an internal ClusterIP service for the API. |
| `k8s/web-deployment.yaml` | Runs the nginx frontend pod, injects API proxy environment variables, health probes, resource limits, and GHCR pull credentials. |
| `k8s/web-service.yaml` | Exposes the frontend with a LoadBalancer service. |
| `k8s/aws-credentials.secret.example.yaml` | Example Secret shape with placeholder values only. Real credentials must be created outside Git. |
| `k8s/README.md` | Operational notes for Kubernetes, Secrets, GHCR image pulls, and Flux reconciliation. |

## Verification Evidence

The implementation has been verified through these checks:

| Check | Result |
|---|---|
| Docker image build | API and frontend images built successfully. |
| Docker Compose smoke test | Frontend and API containers ran together with nginx proxying `/api`. |
| Kubernetes manifest render | `kubectl kustomize k8s` rendered valid YAML. |
| Kubernetes health endpoint | `/api/health` returned `{"status":"ok","service":"safeview"}` in the cluster deployment. |
| Threshold endpoint | `/api/analyze/threshold` returned a valid SafeView report without calling AWS AI services. |
| Secret scan | No pasted AWS access key or secret was found in the project path. |

## Presentation Talking Points

SafeView is best presented as a managed cloud ML integration project:

- Rekognition and Comprehend are used as production-style managed ML APIs.
- S3 is the durable storage boundary for images and audit records.
- Chalice keeps the serverless implementation close to AWS assignment
  requirements.
- Docker and Kubernetes demonstrate that the same service can be packaged for a
  self-hosted platform without replacing the AWS ML services.
- Flux is the natural next step because the Kubernetes manifests are already
  declarative and stored in Git.
- Cloudflare is the planned public access layer for a stable course/recruiter
  URL while preserving the internal Kubernetes service layout.

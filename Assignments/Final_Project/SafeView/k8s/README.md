# SafeView Kubernetes Notes

Flux can apply this directory with Kustomize after the two images are pushed to
GHCR.

Create the `safeview-aws-credentials` Secret separately with SOPS, External
Secrets, Sealed Secrets, or a one-off `kubectl create secret generic` command.
Do not commit real AWS credentials.

Create the `safeview-ghcr-pull` image pull Secret separately if the GHCR
packages are private. The deployments reference that Secret by name.

`safeview-web` is exposed with a `LoadBalancer` Service to match the existing
Cilium load-balancer pattern on the Talos tower. The frontend proxies browser
calls from `/api` to the internal `safeview-api` Service, so the backend does
not need to be public.

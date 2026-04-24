# SafeView Kubernetes Notes

Flux can apply this directory with Kustomize after the two images are pushed to
your registry and the image names in `kustomization.yaml` are changed.

Create the `safeview-aws-credentials` Secret separately with SOPS, External
Secrets, Sealed Secrets, or a one-off `kubectl create secret generic` command.
Do not commit real AWS credentials.

Expose `safeview-web` through your platform's existing Cilium Gateway, Ingress,
or load-balancer pattern. The frontend proxies browser calls from `/api` to the
internal `safeview-api` Service, so the backend does not need to be public.

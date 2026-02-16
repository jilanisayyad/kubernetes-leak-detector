# Remediation Guide

This guide provides production-ready fixes for each check reported by kube-leak-detector.

## Missing CPU/memory requests

- Define `resources.requests` for every container. A common baseline:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
```

## Missing CPU/memory limits

- Define `resources.limits` for every container. A common baseline:

```yaml
resources:
  limits:
    cpu: "500m"
    memory: "512Mi"
```

## Pods in CrashLoopBackOff

- Inspect logs: `kubectl logs <pod> -n <ns>`
- Inspect events: `kubectl describe pod <pod> -n <ns>`
- Common fixes: missing config/secret, bad command/args, probe misconfiguration.

## Containers using the latest tag

- Pin to a versioned tag (preferred) or digest (stronger):

```yaml
image: ghcr.io/org/app:v1.2.3
# or
image: ghcr.io/org/app@sha256:...
```

## Images not pinned by digest

- Use a SHA256 digest for immutable deployments:

```yaml
image: ghcr.io/org/app@sha256:...
```

## runAsNonRoot missing

- Set `runAsNonRoot: true` at pod or container level:

```yaml
securityContext:
  runAsNonRoot: true
```

## readOnlyRootFilesystem off

- Enable read-only root filesystem and mount writable paths explicitly:

```yaml
securityContext:
  readOnlyRootFilesystem: true
```

## Privilege escalation enabled

- Disable escalation explicitly:

```yaml
securityContext:
  allowPrivilegeEscalation: false
```

## Capabilities not dropped

- Drop all by default; add only what is required:

```yaml
securityContext:
  capabilities:
    drop: ["ALL"]
```

## Seccomp not RuntimeDefault

- Set seccomp at pod or container level:

```yaml
securityContext:
  seccompProfile:
    type: RuntimeDefault
```

## Missing liveness/readiness/startup probes

- Add probes for all long-running containers:

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  failureThreshold: 30
  periodSeconds: 5
```

## PodDisruptionBudget missing

- Add a PDB for critical workloads:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: my-app
```

## NetworkPolicy missing

- Add a default-deny policy and explicit allows:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

## Secret env usage

- Prefer mounted secrets or external secret providers. If env is required, scope it:

```yaml
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: api-key
        key: key
```

## Manual review items

These checks cannot be fully validated from cluster state and should be reviewed with your security and platform teams:

- Pod Security Standards alignment (baseline/restricted)
- Image signing and vulnerability scan status
- RBAC least privilege review (avoid cluster-admin, scope to namespaces)
- Secrets management posture (CSI/External Secrets, rotation)
- Scheduling safety (anti-affinity / topology spread)
- Networking posture (default-deny + explicit allow)
- Disruption strategy for critical workloads (PDBs/SLOs)

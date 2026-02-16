# Kubernetes Resource Leak Detector

A production-ready CLI that scans Kubernetes namespaces and reports resource hygiene risks. It prints a clean console report and can notify Slack and Microsoft Teams (Adaptive Card).

## What it detects

Current checks:

- Missing CPU/memory requests
- Missing CPU/memory limits
- Pods in `CrashLoopBackOff`
- Containers using the `latest` tag
- Images not pinned by digest
- Security context: `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation=false`
- Capabilities: must drop `ALL`
- Seccomp profile: `RuntimeDefault`
- Health probes: liveness/readiness/startup
- PodDisruptionBudget missing for Deployments/StatefulSets
- NetworkPolicies missing per namespace
- Secret env usage (`secretKeyRef` / `secretRef`)

Manual review (recommended/roadmap):

- Pod security standards alignment (baseline/restricted)
- Image signing and vulnerability scan status
- RBAC least privilege review (avoid cluster-admin, scope to namespaces)
- Secrets management posture (CSI/External Secrets, rotation)
- Scheduling safety: anti-affinity / topology spread where needed
- Networking posture: default-deny + explicit allow where required
- Disruption strategy for critical workloads (PDBs/SLOs)
- RBAC: least-privilege service accounts, no cluster-admin
- Secrets: avoid env var secrets, use CSI/External Secrets where possible

Workload coverage includes Deployments, StatefulSets, DaemonSets, Jobs, CronJobs, and standalone Pods.

See the remediation guide: [docs/solutions.md](docs/solutions.md).

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

kube-leak-detector
```

## Installation

From source (developer install):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

From a built wheel:

```bash
make build
pip install dist/*.whl
```

Container image:

```bash
podman build -t kube-leak-detector:local .
```

## Usage

```bash
kube-leak-detector \
  --slack-webhook https://hooks.slack.com/services/... \
  --teams-webhook https://outlook.office.com/webhook/... \
  --color
```

Environment variables:

- `SLACK_WEBHOOK_URL`
- `TEAMS_WEBHOOK_URL`

## Exit codes

- `0` - no issues detected
- `2` - issues detected

This behavior makes it CI-friendly. For local convenience, `make run` ignores non-zero exit codes.

## Makefile shortcuts

- `make install` - create venv and install the CLI in editable mode
- `make run` - run with colored output (ignores non-zero exit code)
- `make run-ci` - run with colored output (keeps exit code)

## Release (PyPI)

1. Bump the version in `pyproject.toml`.
2. Build the dist:

```bash
make build
```

3. Publish:

```bash
make publish
```

`make publish` uses `twine` and uploads to the default PyPI repository. Ensure credentials are configured in your environment.

## Authentication

The CLI auto-detects auth:

- In-cluster: uses the service account when `KUBERNETES_SERVICE_HOST` is set
- Local: falls back to kubeconfig (`~/.kube/config`)

## Notifications

- Slack: simple text payload
- Teams: Adaptive Card payload (suitable for Teams incoming webhook)

## Output example

```
==============================
Kube Leak Detector Report
==============================

Summary
-------
- Missing requests..... 5
- Missing limits....... 8
- CrashLoopBackOff..... 0
- Uses latest tag...... 0

[Missing requests] (5)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  kube-system/kube-apiserver-kind-control-plane kube-apiserver        registry.k8s.io/kube-apiserver:v1.35.0
```

## Full sample report

```
==============================
Kube Leak Detector Report
==============================

Summary
-------
- Missing requests.... 2
- Missing limits...... 3
- CrashLoopBackOff.... 0
- Uses latest tag..... 0
- Image not pinned.... 4
- runAsNonRoot missing 4
- readOnlyRootFS off.. 3
- Privilege escalation 3
- Caps not dropped.... 3
- Seccomp not default. 4
- Missing liveness.... 3
- Missing readiness... 3
- Missing startup..... 4
- PDB missing......... 2
- NetworkPolicy missing 2
- Secret env usage.... 0
- Manual review....... 3

[Missing requests] (2)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[Missing limits] (3)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  kube-system/Deployment/coredns               coredns                registry.k8s.io/coredns/coredns:v1.13.1
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[CrashLoopBackOff] (0)
  No issues found

[Uses latest tag] (0)
  No issues found

[Image not pinned] (4)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  kube-system/Deployment/coredns               coredns                registry.k8s.io/coredns/coredns:v1.13.1
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[runAsNonRoot missing] (4)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  kube-system/Deployment/coredns               coredns                registry.k8s.io/coredns/coredns:v1.13.1
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[readOnlyRootFS off] (3)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[Privilege escalation] (3)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[Caps not dropped] (3)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[Seccomp not default] (4)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  kube-system/Deployment/coredns               coredns                registry.k8s.io/coredns/coredns:v1.13.1
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[Missing liveness] (3)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[Missing readiness] (3)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[Missing startup] (4)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  kube-system/Deployment/coredns               coredns                registry.k8s.io/coredns/coredns:v1.13.1
  local-path-storage/Deployment/local-path-... local-path-provisioner docker.io/kindest/local-path-provisioner:v20251212-v0...
  kube-system/DaemonSet/kindnet                kindnet-cni            docker.io/kindest/kindnetd:v20251212-v0.29.0-alpha-10...
  kube-system/DaemonSet/kube-proxy             kube-proxy             registry.k8s.io/kube-proxy:v1.35.0

[PDB missing] (2)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  kube-system/Deployment/coredns               -                      -
  local-path-storage/Deployment/local-path-... -                      -

[NetworkPolicy missing] (2)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  kube-system/Namespace/kube-system            -                      -
  local-path-storage/Namespace/local-path-s... -                      -

[Secret env usage] (0)
  No issues found

[Manual review] (3)
  Namespace/Kind/Name                          Container             Image
  ------------------------------------------------------------------------------
  -/Manual/PodSecurityStandards                -                      -
  -/Manual/ImageSigningAndVulnScan             -                      -
  -/Manual/RBACLeastPrivilege                  -                      -

Total issues: 40
Advisories: 3 (not counted)
```

## Docker

```bash
docker build -t kube-leak-detector:local .
docker run --rm \
  -e KUBECONFIG=/root/.kube/config \
  -v $HOME/.kube:/root/.kube \
  kube-leak-detector:local
```

## Kubernetes CronJob

Deploy the CronJob and RBAC, then configure webhook secrets.

```bash
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/cronjob.yaml
```

The CronJob references a `leak-detector-webhooks` secret with `slack` and `teams` keys. Adjust namespaces and schedules as needed.

## Security and permissions

The tool only reads pod metadata. The sample RBAC grants list/watch/get on pods across namespaces.

## Troubleshooting

- `Forbidden` errors: ensure the service account has cluster-wide read on pods.
- Empty report: verify kubeconfig context or in-cluster service account.
- Teams webhook fails: confirm the incoming webhook is enabled and uses the correct URL.

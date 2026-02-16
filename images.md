```ß
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
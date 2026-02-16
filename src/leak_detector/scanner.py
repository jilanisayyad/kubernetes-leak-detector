from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Iterable, Optional

from kubernetes import client, config


@dataclass
class ContainerIssue:
    namespace: str
    kind: str
    name: str
    container: str
    image: str
    issue: str


@dataclass
class ScanResult:
    missing_requests: list[ContainerIssue] = field(default_factory=list)
    missing_limits: list[ContainerIssue] = field(default_factory=list)
    crash_looping: list[ContainerIssue] = field(default_factory=list)
    latest_tag: list[ContainerIssue] = field(default_factory=list)
    image_not_pinned_digest: list[ContainerIssue] = field(default_factory=list)
    missing_run_as_non_root: list[ContainerIssue] = field(default_factory=list)
    read_only_root_fs_disabled: list[ContainerIssue] = field(default_factory=list)
    allow_privilege_escalation: list[ContainerIssue] = field(default_factory=list)
    capabilities_not_dropped: list[ContainerIssue] = field(default_factory=list)
    seccomp_not_runtime_default: list[ContainerIssue] = field(default_factory=list)
    missing_liveness_probe: list[ContainerIssue] = field(default_factory=list)
    missing_readiness_probe: list[ContainerIssue] = field(default_factory=list)
    missing_startup_probe: list[ContainerIssue] = field(default_factory=list)
    pdb_missing: list[ContainerIssue] = field(default_factory=list)
    network_policy_missing: list[ContainerIssue] = field(default_factory=list)
    secret_env_usage: list[ContainerIssue] = field(default_factory=list)
    advisories: list[ContainerIssue] = field(default_factory=list)

    def total_issues(self) -> int:
        return (
            len(self.missing_requests)
            + len(self.missing_limits)
            + len(self.crash_looping)
            + len(self.latest_tag)
            + len(self.image_not_pinned_digest)
            + len(self.missing_run_as_non_root)
            + len(self.read_only_root_fs_disabled)
            + len(self.allow_privilege_escalation)
            + len(self.capabilities_not_dropped)
            + len(self.seccomp_not_runtime_default)
            + len(self.missing_liveness_probe)
            + len(self.missing_readiness_probe)
            + len(self.missing_startup_probe)
            + len(self.pdb_missing)
            + len(self.network_policy_missing)
            + len(self.secret_env_usage)
        )


def _load_kube_config() -> None:
    if "KUBERNETES_SERVICE_HOST" in os.environ:
        config.load_incluster_config()
        return
    config.load_kube_config()


def _image_uses_latest(image: str) -> bool:
    if "@" in image:
        return False
    if ":" not in image:
        return True
    tag = image.rsplit(":", 1)[-1]
    return tag == "latest"


def _image_pinned_digest(image: str) -> bool:
    return "@sha256:" in image


def _container_has_requests(container: client.V1Container) -> bool:
    resources = container.resources
    if not resources or not resources.requests:
        return False
    return "cpu" in resources.requests and "memory" in resources.requests


def _container_has_limits(container: client.V1Container) -> bool:
    resources = container.resources
    if not resources or not resources.limits:
        return False
    return "cpu" in resources.limits and "memory" in resources.limits


def _iter_container_statuses(
    statuses: Optional[Iterable[client.V1ContainerStatus]],
) -> Iterable[client.V1ContainerStatus]:
    return statuses or []


def _make_issue(
    namespace: str,
    kind: str,
    name: str,
    container_name: str,
    image: str,
    issue: str,
) -> ContainerIssue:
    return ContainerIssue(
        namespace=namespace,
        kind=kind,
        name=name,
        container=container_name,
        image=image,
        issue=issue,
    )


def _has_run_as_non_root(
    container_sc: Optional[client.V1SecurityContext],
    pod_sc: Optional[client.V1PodSecurityContext],
) -> bool:
    if container_sc and container_sc.run_as_non_root is not None:
        return bool(container_sc.run_as_non_root)
    if pod_sc and pod_sc.run_as_non_root is not None:
        return bool(pod_sc.run_as_non_root)
    return False


def _has_read_only_root_fs(container_sc: Optional[client.V1SecurityContext]) -> bool:
    if container_sc and container_sc.read_only_root_filesystem is not None:
        return bool(container_sc.read_only_root_filesystem)
    return False


def _has_allow_privilege_escalation_disabled(
    container_sc: Optional[client.V1SecurityContext],
) -> bool:
    if container_sc and container_sc.allow_privilege_escalation is not None:
        return not bool(container_sc.allow_privilege_escalation)
    return False


def _has_capabilities_drop_all(
    container_sc: Optional[client.V1SecurityContext],
) -> bool:
    if not container_sc or not container_sc.capabilities:
        return False
    drops = container_sc.capabilities.drop or []
    return any(value.upper() == "ALL" for value in drops)


def _has_seccomp_runtime_default(
    container_sc: Optional[client.V1SecurityContext],
    pod_sc: Optional[client.V1PodSecurityContext],
) -> bool:
    if container_sc and container_sc.seccomp_profile:
        return container_sc.seccomp_profile.type == "RuntimeDefault"
    if pod_sc and pod_sc.seccomp_profile:
        return pod_sc.seccomp_profile.type == "RuntimeDefault"
    return False


def _uses_secret_env(container: client.V1Container) -> bool:
    for env in container.env or []:
        if env.value_from and env.value_from.secret_key_ref:
            return True
    for env_from in container.env_from or []:
        if env_from.secret_ref:
            return True
    return False


def _scan_containers(
    result: ScanResult,
    namespace: str,
    kind: str,
    name: str,
    containers: Iterable[client.V1Container],
    pod_security_context: Optional[client.V1PodSecurityContext],
    is_init: bool,
) -> None:
    for container in containers:
        image = container.image or ""
        container_sc = container.security_context

        if not _container_has_requests(container):
            result.missing_requests.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "missing_requests",
                )
            )

        if not _container_has_limits(container):
            result.missing_limits.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "missing_limits",
                )
            )

        if _image_uses_latest(image):
            result.latest_tag.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "latest_tag",
                )
            )

        if not _image_pinned_digest(image):
            result.image_not_pinned_digest.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "image_not_pinned_digest",
                )
            )

        if not _has_run_as_non_root(container_sc, pod_security_context):
            result.missing_run_as_non_root.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "missing_run_as_non_root",
                )
            )

        if not _has_read_only_root_fs(container_sc):
            result.read_only_root_fs_disabled.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "read_only_root_fs_disabled",
                )
            )

        if not _has_allow_privilege_escalation_disabled(container_sc):
            result.allow_privilege_escalation.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "allow_privilege_escalation",
                )
            )

        if not _has_capabilities_drop_all(container_sc):
            result.capabilities_not_dropped.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "capabilities_not_dropped",
                )
            )

        if not _has_seccomp_runtime_default(container_sc, pod_security_context):
            result.seccomp_not_runtime_default.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "seccomp_not_runtime_default",
                )
            )

        if _uses_secret_env(container):
            result.secret_env_usage.append(
                _make_issue(
                    namespace,
                    kind,
                    name,
                    container.name,
                    image,
                    "secret_env_usage",
                )
            )

        if not is_init:
            if not container.liveness_probe:
                result.missing_liveness_probe.append(
                    _make_issue(
                        namespace,
                        kind,
                        name,
                        container.name,
                        image,
                        "missing_liveness_probe",
                    )
                )
            if not container.readiness_probe:
                result.missing_readiness_probe.append(
                    _make_issue(
                        namespace,
                        kind,
                        name,
                        container.name,
                        image,
                        "missing_readiness_probe",
                    )
                )
            if not container.startup_probe:
                result.missing_startup_probe.append(
                    _make_issue(
                        namespace,
                        kind,
                        name,
                        container.name,
                        image,
                        "missing_startup_probe",
                    )
                )


def _scan_pod_templates(
    result: ScanResult,
    namespace: str,
    kind: str,
    name: str,
    template: client.V1PodTemplateSpec,
) -> None:
    spec = template.spec
    if not spec:
        return
    containers = spec.containers or []
    init_containers = spec.init_containers or []
    pod_security_context = spec.security_context
    _scan_containers(
        result,
        namespace,
        kind,
        name,
        containers,
        pod_security_context,
        is_init=False,
    )
    _scan_containers(
        result,
        namespace,
        kind,
        name,
        init_containers,
        pod_security_context,
        is_init=True,
    )


def _scan_pod_for_crashloops(result: ScanResult, pod: client.V1Pod) -> None:
    pod_namespace = pod.metadata.namespace or "default"
    pod_name = pod.metadata.name or "unknown"
    containers = pod.spec.containers or []
    statuses = list(_iter_container_statuses(pod.status.container_statuses))
    status_by_name = {status.name: status for status in statuses}

    for container in containers:
        status = status_by_name.get(container.name)
        if status and status.state and status.state.waiting:
            if status.state.waiting.reason == "CrashLoopBackOff":
                result.crash_looping.append(
                    _make_issue(
                        pod_namespace,
                        "Pod",
                        pod_name,
                        container.name,
                        container.image or "",
                        "CrashLoopBackOff",
                    )
                )


def _is_standalone_pod(pod: client.V1Pod) -> bool:
    refs = pod.metadata.owner_references or []
    return len(refs) == 0


def _selector_matches(
    selector: Optional[client.V1LabelSelector],
    labels: dict[str, str],
) -> bool:
    if not selector:
        return False
    for key, value in (selector.match_labels or {}).items():
        if labels.get(key) != value:
            return False
    for expr in selector.match_expressions or []:
        key = expr.key
        op = expr.operator
        values = expr.values or []
        if op == "In" and labels.get(key) not in values:
            return False
        if op == "NotIn" and labels.get(key) in values:
            return False
        if op == "Exists" and key not in labels:
            return False
        if op == "DoesNotExist" and key in labels:
            return False
    return True


def scan_cluster(namespace: Optional[str] = None) -> ScanResult:
    _load_kube_config()
    core_api = client.CoreV1Api()
    apps_api = client.AppsV1Api()
    batch_api = client.BatchV1Api()
    policy_api = client.PolicyV1Api()
    networking_api = client.NetworkingV1Api()

    if namespace:
        pods = core_api.list_namespaced_pod(namespace=namespace).items
        deployments = apps_api.list_namespaced_deployment(namespace=namespace).items
        statefulsets = apps_api.list_namespaced_stateful_set(namespace=namespace).items
        daemonsets = apps_api.list_namespaced_daemon_set(namespace=namespace).items
        jobs = batch_api.list_namespaced_job(namespace=namespace).items
        cronjobs = batch_api.list_namespaced_cron_job(namespace=namespace).items
        pdbs = policy_api.list_namespaced_pod_disruption_budget(
            namespace=namespace
        ).items
        network_policies = networking_api.list_namespaced_network_policy(
            namespace=namespace
        ).items
    else:
        pods = core_api.list_pod_for_all_namespaces().items
        deployments = apps_api.list_deployment_for_all_namespaces().items
        statefulsets = apps_api.list_stateful_set_for_all_namespaces().items
        daemonsets = apps_api.list_daemon_set_for_all_namespaces().items
        jobs = batch_api.list_job_for_all_namespaces().items
        cronjobs = batch_api.list_cron_job_for_all_namespaces().items
        pdbs = policy_api.list_pod_disruption_budget_for_all_namespaces().items
        network_policies = networking_api.list_network_policy_for_all_namespaces().items

    result = ScanResult()

    pdbs_by_namespace: dict[str, list[client.V1PodDisruptionBudget]] = {}
    for pdb in pdbs:
        ns = pdb.metadata.namespace or "default"
        pdbs_by_namespace.setdefault(ns, []).append(pdb)

    np_by_namespace: dict[str, list[client.V1NetworkPolicy]] = {}
    for policy in network_policies:
        ns = policy.metadata.namespace or "default"
        np_by_namespace.setdefault(ns, []).append(policy)

    reported_np_missing: set[str] = set()

    def _namespace_has_network_policy(ns: str) -> bool:
        return len(np_by_namespace.get(ns, [])) > 0

    def _record_network_policy_missing(ns: str) -> None:
        if ns in reported_np_missing:
            return
        if _namespace_has_network_policy(ns):
            return
        reported_np_missing.add(ns)
        result.network_policy_missing.append(
            _make_issue(ns, "Namespace", ns, "-", "-", "network_policy_missing")
        )

    def _pdb_applies(ns: str, labels: dict[str, str]) -> bool:
        for pdb in pdbs_by_namespace.get(ns, []):
            if _selector_matches(pdb.spec.selector, labels):
                return True
        return False

    for deployment in deployments:
        ns = deployment.metadata.namespace or "default"
        name = deployment.metadata.name or "unknown"
        _scan_pod_templates(result, ns, "Deployment", name, deployment.spec.template)
        labels = deployment.spec.selector.match_labels or {}
        if not _pdb_applies(ns, labels):
            result.pdb_missing.append(
                _make_issue(ns, "Deployment", name, "-", "-", "pdb_missing")
            )
        _record_network_policy_missing(ns)

    for statefulset in statefulsets:
        ns = statefulset.metadata.namespace or "default"
        name = statefulset.metadata.name or "unknown"
        _scan_pod_templates(result, ns, "StatefulSet", name, statefulset.spec.template)
        labels = statefulset.spec.selector.match_labels or {}
        if not _pdb_applies(ns, labels):
            result.pdb_missing.append(
                _make_issue(ns, "StatefulSet", name, "-", "-", "pdb_missing")
            )
        _record_network_policy_missing(ns)

    for daemonset in daemonsets:
        ns = daemonset.metadata.namespace or "default"
        name = daemonset.metadata.name or "unknown"
        _scan_pod_templates(result, ns, "DaemonSet", name, daemonset.spec.template)
        _record_network_policy_missing(ns)

    for job in jobs:
        ns = job.metadata.namespace or "default"
        name = job.metadata.name or "unknown"
        _scan_pod_templates(result, ns, "Job", name, job.spec.template)
        _record_network_policy_missing(ns)

    for cronjob in cronjobs:
        ns = cronjob.metadata.namespace or "default"
        name = cronjob.metadata.name or "unknown"
        template = cronjob.spec.job_template.spec.template
        _scan_pod_templates(result, ns, "CronJob", name, template)
        _record_network_policy_missing(ns)

    for pod in pods:
        _scan_pod_for_crashloops(result, pod)
        if _is_standalone_pod(pod):
            ns = pod.metadata.namespace or "default"
            name = pod.metadata.name or "unknown"
            containers = pod.spec.containers or []
            init_containers = pod.spec.init_containers or []
            pod_security_context = pod.spec.security_context
            _scan_containers(
                result,
                ns,
                "Pod",
                name,
                containers,
                pod_security_context,
                is_init=False,
            )
            _scan_containers(
                result,
                ns,
                "Pod",
                name,
                init_containers,
                pod_security_context,
                is_init=True,
            )
            _record_network_policy_missing(ns)

    result.advisories.extend(
        [
            _make_issue(
                "-",
                "Manual",
                "PodSecurityStandards",
                "-",
                "-",
                "manual_pod_security_standards",
            ),
            _make_issue(
                "-",
                "Manual",
                "ImageSigningAndVulnScan",
                "-",
                "-",
                "manual_image_signing_vuln_scan",
            ),
            _make_issue(
                "-",
                "Manual",
                "RBACLeastPrivilege",
                "-",
                "-",
                "manual_rbac_least_privilege",
            ),
        ]
    )

    return result

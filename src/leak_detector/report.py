from __future__ import annotations

from leak_detector.scanner import ScanResult


class _Color:
    def __init__(self, enabled: bool) -> None:
        self._enabled = enabled

    def apply(self, text: str, code: str) -> str:
        if not self._enabled:
            return text
        return f"\033[{code}m{text}\033[0m"


def _truncate(value: str, width: int) -> str:
    if len(value) <= width:
        return value.ljust(width)
    return value[: max(0, width - 3)] + "..."


def _format_issue_line(issue) -> str:
    workload = f"{issue.namespace}/{issue.kind}/{issue.name}"
    workload_col = _truncate(workload, 44)
    container_col = _truncate(issue.container, 22)
    image_col = _truncate(issue.image, 56)
    return f"{workload_col} {container_col} {image_col}"


def format_console_report(result: ScanResult, *, color: bool = False) -> str:
    palette = _Color(color)
    lines: list[str] = []
    lines.append(palette.apply("==============================", "36"))
    lines.append(palette.apply("Kube Leak Detector Report", "1;36"))
    lines.append(palette.apply("==============================", "36"))
    lines.append("")

    summary = [
        ("Missing requests", result.missing_requests),
        ("Missing limits", result.missing_limits),
        ("CrashLoopBackOff", result.crash_looping),
        ("Uses latest tag", result.latest_tag),
        ("Image not pinned", result.image_not_pinned_digest),
        ("runAsNonRoot missing", result.missing_run_as_non_root),
        ("readOnlyRootFS off", result.read_only_root_fs_disabled),
        ("Privilege escalation", result.allow_privilege_escalation),
        ("Caps not dropped", result.capabilities_not_dropped),
        ("Seccomp not default", result.seccomp_not_runtime_default),
        ("Missing liveness", result.missing_liveness_probe),
        ("Missing readiness", result.missing_readiness_probe),
        ("Missing startup", result.missing_startup_probe),
        ("PDB missing", result.pdb_missing),
        ("NetworkPolicy missing", result.network_policy_missing),
        ("Secret env usage", result.secret_env_usage),
        ("Manual review", result.advisories),
    ]

    lines.append(palette.apply("Summary", "1"))
    lines.append(palette.apply("-------", "1"))
    for title, items in summary:
        count = len(items)
        count_text = palette.apply(str(count), "31" if count else "32")
        lines.append(f"- {title.ljust(20, '.')} {count_text}")
    lines.append("")

    for title, items in summary:
        header = f"[{title}] ({len(items)})"
        lines.append(palette.apply(header, "1;33" if items else "1;32"))
        if not items:
            lines.append(palette.apply("  No issues found", "32"))
            lines.append("")
            continue
        lines.append(
            "  Namespace/Kind/Name                          Container             Image"
        )
        lines.append(
            "  ------------------------------------------------------------------------------"
        )
        for issue in items[:50]:
            lines.append("  " + _format_issue_line(issue))
        if len(items) > 50:
            lines.append(f"  ... and {len(items) - 50} more")
        lines.append("")

    total_text = palette.apply(
        str(result.total_issues()),
        "31" if result.total_issues() else "32",
    )
    lines.append(f"Total issues: {total_text}")
    if result.advisories:
        lines.append(
            f"Advisories: {palette.apply(str(len(result.advisories)), '33')} (not counted)"
        )
    return "\n".join(lines)

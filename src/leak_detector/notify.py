from __future__ import annotations

import json
from typing import Optional

import requests

from leak_detector.scanner import ScanResult


def _summaries(result: ScanResult) -> list[tuple[str, int]]:
    return [
        ("Missing requests", len(result.missing_requests)),
        ("Missing limits", len(result.missing_limits)),
        ("CrashLoopBackOff", len(result.crash_looping)),
        ("Uses latest tag", len(result.latest_tag)),
        ("Image not pinned", len(result.image_not_pinned_digest)),
        ("runAsNonRoot missing", len(result.missing_run_as_non_root)),
        ("readOnlyRootFS off", len(result.read_only_root_fs_disabled)),
        ("Privilege escalation", len(result.allow_privilege_escalation)),
        ("Caps not dropped", len(result.capabilities_not_dropped)),
        ("Seccomp not default", len(result.seccomp_not_runtime_default)),
        ("Missing liveness", len(result.missing_liveness_probe)),
        ("Missing readiness", len(result.missing_readiness_probe)),
        ("Missing startup", len(result.missing_startup_probe)),
        ("PDB missing", len(result.pdb_missing)),
        ("NetworkPolicy missing", len(result.network_policy_missing)),
        ("Secret env usage", len(result.secret_env_usage)),
        ("Manual review", len(result.advisories)),
    ]


def _build_plain_text(result: ScanResult) -> str:
    lines = ["Kubernetes Resource Hygiene Report"]
    for title, count in _summaries(result):
        lines.append(f"- {title}: {count}")
    lines.append(f"Total issues: {result.total_issues()}")
    if result.advisories:
        lines.append(f"Advisories: {len(result.advisories)} (not counted)")
    return "\n".join(lines)


def _build_teams_card(result: ScanResult) -> dict:
    facts = [
        {"title": title, "value": str(count)} for title, count in _summaries(result)
    ]
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.5",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Large",
                            "weight": "Bolder",
                            "text": "Kubernetes Resource Hygiene Report",
                        },
                        {"type": "FactSet", "facts": facts},
                        {
                            "type": "TextBlock",
                            "text": f"Total issues: {result.total_issues()}",
                            "wrap": True,
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Advisories: {len(result.advisories)} (not counted)",
                            "wrap": True,
                            "isVisible": bool(result.advisories),
                        },
                    ],
                },
            }
        ],
    }


def _post_json(url: str, payload: dict) -> None:
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()


def send_notifications(
    result: ScanResult,
    slack_webhook: Optional[str] = None,
    teams_webhook: Optional[str] = None,
) -> None:
    if slack_webhook:
        _post_json(slack_webhook, {"text": _build_plain_text(result)})

    if teams_webhook:
        _post_json(teams_webhook, _build_teams_card(result))

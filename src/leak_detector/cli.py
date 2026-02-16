import argparse
import os
import sys
from typing import Optional

from leak_detector.notify import send_notifications
from leak_detector.report import format_console_report
from leak_detector.scanner import ScanResult, scan_cluster


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan Kubernetes clusters for resource hygiene issues."
    )
    parser.add_argument(
        "--namespace",
        help="Scan a single namespace (default: all namespaces)",
        default=None,
    )
    parser.add_argument(
        "--slack-webhook",
        help="Slack incoming webhook URL",
        default=os.getenv("SLACK_WEBHOOK_URL"),
    )
    parser.add_argument(
        "--teams-webhook",
        help="Microsoft Teams incoming webhook URL",
        default=os.getenv("TEAMS_WEBHOOK_URL"),
    )
    parser.add_argument(
        "--notify-only",
        action="store_true",
        help="Skip console output, send notifications only",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help="Enable ANSI colors in console output",
    )
    return parser.parse_args(argv)


def _exit_code(result: ScanResult) -> int:
    if result.total_issues() > 0:
        return 2
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    result = scan_cluster(namespace=args.namespace)

    if not args.notify_only:
        print(format_console_report(result, color=args.color))

    send_notifications(
        result,
        slack_webhook=args.slack_webhook,
        teams_webhook=args.teams_webhook,
    )

    return _exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

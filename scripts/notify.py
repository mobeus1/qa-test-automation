#!/usr/bin/env python3
"""Send notifications for test results via webhook."""

import argparse
import json
import sys
import urllib.request


def parse_args():
    parser = argparse.ArgumentParser(description="Send test result notifications")
    parser.add_argument("--webhook", required=True, help="Webhook URL")
    parser.add_argument("--app", required=True, help="Application name")
    parser.add_argument("--env", required=True, help="Environment")
    parser.add_argument("--status", required=True, choices=["passed", "failed", "error"])
    parser.add_argument("--run-url", default="", help="GitHub Actions run URL")
    return parser.parse_args()


def send_notification(webhook_url, payload):
    """Send notification to webhook endpoint."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Notification sent: {response.status}")
    except Exception as e:
        print(f"Failed to send notification: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    args = parse_args()

    status_emoji = {"passed": "OK", "failed": "FAIL", "error": "WARN"}

    payload = {
        "text": f"{status_emoji.get(args.status, '?')} QA Tests {args.status.upper()}: {args.app} ({args.env})",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"QA Test Results: {args.app}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Application:*\n{args.app}"},
                    {"type": "mrkdwn", "text": f"*Environment:*\n{args.env}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{args.status.upper()}"},
                    {"type": "mrkdwn", "text": f"*Run URL:*\n<{args.run_url}|View Run>"}
                ]
            }
        ]
    }

    send_notification(args.webhook, payload)


if __name__ == "__main__":
    main()

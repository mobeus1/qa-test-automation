#!/usr/bin/env python3
"""Parse TestComplete test results and generate GitHub-compatible output."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Parse TestComplete results")
    parser.add_argument("--app", required=True, help="Application name")
    parser.add_argument("--env", required=True, help="Environment name")
    parser.add_argument("--results-dir", default="test-results", help="Results directory")
    return parser.parse_args()


def find_latest_results(results_dir):
    """Find the most recent results directory."""
    results_path = Path(results_dir)
    if not results_path.exists():
        return None
    subdirs = sorted(results_path.iterdir(), reverse=True)
    return subdirs[0] if subdirs else None


def generate_summary(app_name, environment, results_dir):
    """Generate a test summary report."""
    latest = find_latest_results(results_dir)

    summary = {
        "app_name": app_name,
        "environment": environment,
        "timestamp": datetime.utcnow().isoformat(),
        "results_path": str(latest) if latest else "No results found",
        "status": "completed"
    }

    os.makedirs("test-results", exist_ok=True)
    summary_path = f"test-results/{app_name}-{environment}-summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Summary written to {summary_path}")
    return summary


def main():
    args = parse_args()
    summary = generate_summary(args.app, args.env, args.results_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Parse JMeter test results and validate against thresholds."""

import argparse
import csv
import json
import os
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Parse JMeter results")
    parser.add_argument("--app", required=True, help="Application name")
    parser.add_argument("--env", required=True, help="Environment name")
    parser.add_argument("--test-plan", default="health-check", help="JMeter test plan name")
    parser.add_argument("--results-dir", default="test-results/jmeter")
    parser.add_argument("--max-response-time", type=int, default=5000, help="Max response time in ms")
    parser.add_argument("--max-error-rate", type=float, default=1.0, help="Max error rate percent")
    return parser.parse_args()


def parse_jtl(jtl_path):
    """Parse JMeter JTL results file."""
    results = []
    if not os.path.exists(jtl_path):
        return results
    with open(jtl_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                "timestamp": int(row.get("timeStamp", 0)),
                "elapsed": int(row.get("elapsed", 0)),
                "label": row.get("label", ""),
                "response_code": row.get("responseCode", ""),
                "success": row.get("success", "").lower() == "true",
                "bytes": int(row.get("bytes", 0)),
                "thread_name": row.get("threadName", ""),
            })
    return results


def analyze_results(results):
    """Compute summary statistics from JTL results."""
    if not results:
        return {"total": 0, "error_rate": 100.0, "avg_response_time": 0}

    total = len(results)
    errors = sum(1 for r in results if not r["success"])
    response_times = [r["elapsed"] for r in results]

    summary = {
        "total_requests": total,
        "successful": total - errors,
        "failed": errors,
        "error_rate": round((errors / total) * 100, 2) if total > 0 else 0,
        "avg_response_time_ms": round(sum(response_times) / total) if total else 0,
        "min_response_time_ms": min(response_times) if response_times else 0,
        "max_response_time_ms": max(response_times) if response_times else 0,
        "p90_response_time_ms": sorted(response_times)[int(total * 0.9)] if total else 0,
        "p95_response_time_ms": sorted(response_times)[int(total * 0.95)] if total else 0,
    }

    # Per-endpoint breakdown
    endpoints = {}
    for r in results:
        label = r["label"]
        if label not in endpoints:
            endpoints[label] = {"total": 0, "errors": 0, "times": []}
        endpoints[label]["total"] += 1
        if not r["success"]:
            endpoints[label]["errors"] += 1
        endpoints[label]["times"].append(r["elapsed"])

    summary["endpoints"] = {}
    for label, data in endpoints.items():
        summary["endpoints"][label] = {
            "total": data["total"],
            "errors": data["errors"],
            "avg_ms": round(sum(data["times"]) / len(data["times"])) if data["times"] else 0,
        }

    return summary


def generate_markdown_summary(summary, app_name, env, test_plan, max_rt, max_err):
    """Generate a markdown summary for GitHub Actions."""
    passed_rt = summary["avg_response_time_ms"] <= max_rt
    passed_err = summary["error_rate"] <= max_err
    overall = "PASSED" if (passed_rt and passed_err) else "FAILED"

    lines = [
        f"### JMeter Results ({test_plan}): {overall}",
        f"| Metric | Value | Threshold | Status |",
        f"|--------|-------|-----------|--------|",
        f"| Avg Response Time | {summary['avg_response_time_ms']}ms | <{max_rt}ms | {'PASS' if passed_rt else 'FAIL'} |",
        f"| Error Rate | {summary['error_rate']}% | <{max_err}% | {'PASS' if passed_err else 'FAIL'} |",
        f"| Total Requests | {summary['total_requests']} | - | - |",
        f"| P90 Response Time | {summary['p90_response_time_ms']}ms | - | - |",
        f"| P95 Response Time | {summary['p95_response_time_ms']}ms | - | - |",
        "",
        "#### Endpoint Breakdown",
        "| Endpoint | Requests | Errors | Avg Response |",
        "|----------|----------|--------|-------------|",
    ]
    for label, data in summary.get("endpoints", {}).items():
        lines.append(f"| {label} | {data['total']} | {data['errors']} | {data['avg_ms']}ms |")

    return "\n".join(lines)


def main():
    args = parse_args()
    jtl_path = os.path.join(args.results_dir, "results.jtl")

    results = parse_jtl(jtl_path)
    summary = analyze_results(results)

    # Write JSON summary
    os.makedirs(args.results_dir, exist_ok=True)
    with open(os.path.join(args.results_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    # Write markdown summary
    md = generate_markdown_summary(
        summary,
        args.app,
        args.env,
        args.test_plan,
        args.max_response_time,
        args.max_error_rate,
    )
    with open(os.path.join(args.results_dir, "summary.md"), "w") as f:
        f.write(md)

    print(json.dumps(summary, indent=2))

    # Exit with error if thresholds exceeded
    if summary["error_rate"] > args.max_error_rate:
        print(f"ERROR: Error rate {summary['error_rate']}% exceeds threshold {args.max_error_rate}%")
        sys.exit(1)
    if summary["avg_response_time_ms"] > args.max_response_time:
        print(f"ERROR: Avg response time {summary['avg_response_time_ms']}ms exceeds {args.max_response_time}ms")
        sys.exit(1)


if __name__ == "__main__":
    main()

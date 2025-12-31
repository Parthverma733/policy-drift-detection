"""Turns drift results into readable text."""

from typing import List
from drift_detector import DriftResult


def explain_drift(drift: DriftResult) -> str:
    """Writes a simple explanation of what went wrong."""
    constraint_type = drift.constraint["type"]
    metric_name = drift.constraint["metric"]
    
    if constraint_type == "minimum_coverage":
        explanation = (
            f"District {drift.district_name} ({drift.district_id}) in {drift.month}: "
            f"Coverage percentage is {drift.actual_value:.1f}%, "
            f"below required minimum of {drift.expected_threshold:.1f}% "
            f"for priority districts. "
            f"Severity: {drift.severity}."
        )
    
    elif constraint_type == "resource_allocation":
        explanation = (
            f"District {drift.district_name} ({drift.district_id}) in {drift.month}: "
            f"Fund utilization is {drift.actual_value:.1f}%, "
            f"below required minimum of {drift.expected_threshold:.1f}% "
            f"for priority districts. "
            f"Severity: {drift.severity}."
        )
    
    elif constraint_type == "temporal_consistency":
        explanation = (
            f"District {drift.district_name} ({drift.district_id}) "
            f"shows high variance in {metric_name}: "
            f"observed variance of {drift.actual_value:.1f}% "
            f"exceeds threshold of {drift.expected_threshold:.1f}%. "
            f"This indicates inconsistent implementation across months. "
            f"Severity: {drift.severity}."
        )
    
    else:
        explanation = (
            f"District {drift.district_name} ({drift.district_id}) in {drift.month}: "
            f"{metric_name} value {drift.actual_value:.1f} "
            f"violates policy constraint (threshold: {drift.expected_threshold:.1f}). "
            f"Severity: {drift.severity}."
        )
    
    return explanation


def generate_summary(drifts: List[DriftResult]) -> str:
    """Creates a summary of all violations found."""
    if not drifts:
        return "No policy drift detected. Implementation aligns with policy intent."
    
    total = len(drifts)
    by_type = {}
    by_severity = {"low": 0, "medium": 0, "high": 0}
    by_district = {}
    
    for drift in drifts:
        by_type[drift.drift_type] = by_type.get(drift.drift_type, 0) + 1
        by_severity[drift.severity] = by_severity.get(drift.severity, 0) + 1
        district_key = f"{drift.district_name} ({drift.district_id})"
        by_district[district_key] = by_district.get(district_key, 0) + 1
    
    summary_lines = [
        f"Policy Drift Detection Summary",
        f"=" * 50,
        f"Total drift instances detected: {total}",
        f"",
        f"By type:",
    ]
    
    for drift_type, count in sorted(by_type.items()):
        summary_lines.append(f"  {drift_type}: {count}")
    
    summary_lines.extend([
        f"",
        f"By severity:",
        f"  High: {by_severity['high']}",
        f"  Medium: {by_severity['medium']}",
        f"  Low: {by_severity['low']}",
        f"",
        f"Districts with drift: {len(by_district)}",
    ])
    
    return "\n".join(summary_lines)


def format_drift_report(drifts: List[DriftResult]) -> str:
    """Builds the full report with summary and details."""
    report_lines = [generate_summary(drifts), "", "Detailed Findings:", "=" * 50, ""]
    
    if drifts:
        for i, drift in enumerate(drifts, 1):
            report_lines.append(f"{i}. {explain_drift(drift)}")
            report_lines.append("")
    
    return "\n".join(report_lines)


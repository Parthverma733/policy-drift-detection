"""Finds where implementation doesn't match policy rules."""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
from intent_parser import PolicyIntent, matches_target_group


class DriftResult:
    """Stores information about a policy violation."""
    
    def __init__(self, drift_type: str, district_id: str, district_name: str,
                 constraint: Dict, actual_value: float, expected_threshold: float,
                 month: str, severity: str):
        self.drift_type = drift_type
        self.district_id = district_id
        self.district_name = district_name
        self.constraint = constraint
        self.actual_value = actual_value
        self.expected_threshold = expected_threshold
        self.month = month
        self.severity = severity


def classify_district(district_data: Dict[str, Any], policy_intent: PolicyIntent) -> str:
    """Figures out which group a district belongs to."""
    for target_group in policy_intent.target_groups:
        if matches_target_group(district_data, target_group):
            return target_group["name"]
    return "unclassified"


def check_metric_constraint(value: float, constraint: Dict, 
                           target_metrics: Dict) -> Tuple[bool, float]:
    """Checks if a value breaks a policy rule."""
    constraint_type = constraint["type"]
    metric_name = constraint["metric"]
    
    if constraint_type == "minimum_coverage":
        threshold = constraint.get("threshold")
        return (value < threshold, threshold)
    
    elif constraint_type == "temporal_consistency":
        threshold = constraint.get("threshold")
        return (value > threshold, threshold)
    
    elif constraint_type == "resource_allocation":
        threshold = constraint.get("threshold")
        return (value < threshold, threshold)
    
    elif metric_name in target_metrics:
        metric_def = target_metrics[metric_name]
        if "min" in metric_def and value < metric_def["min"]:
            return (True, metric_def["min"])
        if "max" in metric_def and value > metric_def["max"]:
            return (True, metric_def["max"])
    
    return (False, 0.0)


def calculate_severity(actual: float, threshold: float, constraint_type: str) -> str:
    """Decides how serious a violation is."""
    if constraint_type in ["minimum_coverage", "resource_allocation"]:
        deviation = (threshold - actual) / threshold * 100
    else:
        deviation = (actual - threshold) / threshold * 100
    
    if deviation > 30:
        return "high"
    elif deviation > 15:
        return "medium"
    else:
        return "low"


def detect_metric_drift(district_data: Dict[str, Any], policy_intent: PolicyIntent,
                        month: str) -> List[DriftResult]:
    """Checks if a district's metrics violate policy rules."""
    drifts = []
    district_group = classify_district(district_data, policy_intent)
    constraints = policy_intent.get_constraints_for_group(district_group)
    
    for constraint in constraints:
        if constraint["type"] == "temporal_consistency":
            continue
        
        metric_name = constraint["metric"]
        actual_value = district_data.get(metric_name)
        
        if actual_value is None:
            continue
        
        is_violated, threshold = check_metric_constraint(
            actual_value, constraint, policy_intent.target_metrics
        )
        
        if is_violated:
            severity = calculate_severity(
                actual_value, threshold, constraint["type"]
            )
            
            drift = DriftResult(
                drift_type="metric",
                district_id=district_data["district_id"],
                district_name=district_data["district_name"],
                constraint=constraint,
                actual_value=actual_value,
                expected_threshold=threshold,
                month=month,
                severity=severity
            )
            drifts.append(drift)
    
    return drifts


def detect_temporal_drift(district_history: List[Dict[str, Any]], 
                         policy_intent: PolicyIntent) -> List[DriftResult]:
    """Checks if a district's metrics vary too much over time."""
    drifts = []
    
    if len(district_history) < 2:
        return drifts
    
    temporal_constraints = [
        c for c in policy_intent.constraints 
        if c["type"] == "temporal_consistency"
    ]
    
    for constraint in temporal_constraints:
        metric_name = constraint["metric"]
        threshold = constraint.get("threshold")
        
        for record in district_history:
            value = record.get(metric_name)
            if value is None:
                continue
            
            if value > threshold:
                month = record.get("month", "unknown")
                severity = calculate_severity(value, threshold, "temporal_consistency")
                
                drift = DriftResult(
                    drift_type="temporal",
                    district_id=record["district_id"],
                    district_name=record["district_name"],
                    constraint=constraint,
                    actual_value=value,
                    expected_threshold=threshold,
                    month=month,
                    severity=severity
                )
                drifts.append(drift)
    
    return drifts


def detect_all_drift(implementation_data: List[Dict[str, Any]], 
                    policy_intent: PolicyIntent) -> List[DriftResult]:
    """Finds all policy violations across all districts and months."""
    all_drifts = []
    
    district_groups = defaultdict(list)
    for record in implementation_data:
        district_id = record["district_id"]
        district_groups[district_id].append(record)
    
    for district_id, history in district_groups.items():
        for record in history:
            month = record.get("month", "unknown")
            metric_drifts = detect_metric_drift(record, policy_intent, month)
            all_drifts.extend(metric_drifts)
        
        temporal_drifts = detect_temporal_drift(history, policy_intent)
        all_drifts.extend(temporal_drifts)
    
    return all_drifts


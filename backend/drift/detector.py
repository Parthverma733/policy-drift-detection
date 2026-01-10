"""Drift detection engine with MongoDB persistence."""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime
from bson import ObjectId
import csv
import io


class DriftResult:
    """Represents a detected policy drift."""
    
    def __init__(self, drift_type: str, district_id: str, district_name: str,
                 constraint: Dict, actual_value: float, expected_threshold: float,
                 month: str, severity: str, policy_id: str, dataset_id: str):
        self.drift_type = drift_type
        self.district_id = district_id
        self.district_name = district_name
        self.constraint = constraint
        self.actual_value = actual_value
        self.expected_threshold = expected_threshold
        self.month = month
        self.severity = severity
        self.policy_id = policy_id
        self.dataset_id = dataset_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            "policy_id": ObjectId(self.policy_id) if isinstance(self.policy_id, str) else self.policy_id,
            "dataset_id": ObjectId(self.dataset_id) if isinstance(self.dataset_id, str) else self.dataset_id,
            "district_id": self.district_id,
            "district_name": self.district_name,
            "month": self.month,
            "drift_type": self.drift_type,
            "severity": self.severity,
            "constraint_type": self.constraint.get("type"),
            "metric": self.constraint.get("metric"),
            "actual_value": self.actual_value,
            "expected_threshold": self.expected_threshold,
            "detected_at": datetime.utcnow()
        }


def matches_target_group(district_data: Dict[str, Any], target_group: Dict) -> bool:
    """Check if district matches target group criteria."""
    criteria = target_group.get("criteria", {})
    
    for field, conditions in criteria.items():
        value = district_data.get(field)
        if value is None:
            return False
        
        if isinstance(conditions, dict):
            if "min" in conditions and value < conditions["min"]:
                return False
            if "max" in conditions and value > conditions["max"]:
                return False
        elif isinstance(conditions, (int, float)):
            if value != conditions:
                return False
    
    return True


def classify_district(district_data: Dict[str, Any], target_groups: List[Dict]) -> str:
    """Classify district into a target group."""
    for target_group in target_groups:
        if matches_target_group(district_data, target_group):
            return target_group["name"]
    return "unclassified"


def check_metric_constraint(value: float, constraint: Dict, 
                           target_metrics: Dict) -> Tuple[bool, float]:
    """Check if value violates constraint."""
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
    """Calculate severity of violation."""
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


def detect_metric_drift(district_data: Dict[str, Any], policy_intent: Dict,
                        month: str, policy_id: str, dataset_id: str) -> List[DriftResult]:
    """Detect metric-based drift."""
    drifts = []
    target_groups = policy_intent.get("target_groups", [])
    constraints = policy_intent.get("constraints", [])
    target_metrics = policy_intent.get("target_metrics", {})
    
    district_group = classify_district(district_data, target_groups)
    applicable_constraints = [
        c for c in constraints 
        if c.get("applies_to") == district_group or c.get("applies_to") == "all"
    ]
    
    for constraint in applicable_constraints:
        if constraint["type"] == "temporal_consistency":
            continue
        
        metric_name = constraint["metric"]
        actual_value = district_data.get(metric_name)
        
        if actual_value is None:
            continue
        
        is_violated, threshold = check_metric_constraint(
            actual_value, constraint, target_metrics
        )
        
        if is_violated:
            severity = calculate_severity(
                actual_value, threshold, constraint["type"]
            )
            
            drift = DriftResult(
                drift_type="metric",
                district_id=district_data["district_id"],
                district_name=district_data.get("district_name", "Unknown"),
                constraint=constraint,
                actual_value=actual_value,
                expected_threshold=threshold,
                month=month,
                severity=severity,
                policy_id=policy_id,
                dataset_id=dataset_id
            )
            drifts.append(drift)
    
    return drifts


def detect_temporal_drift(district_history: List[Dict[str, Any]], 
                         policy_intent: Dict, policy_id: str, 
                         dataset_id: str) -> List[DriftResult]:
    """Detect temporal drift."""
    drifts = []
    
    if len(district_history) < 2:
        return drifts
    
    constraints = policy_intent.get("constraints", [])
    temporal_constraints = [
        c for c in constraints 
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
                    district_name=record.get("district_name", "Unknown"),
                    constraint=constraint,
                    actual_value=value,
                    expected_threshold=threshold,
                    month=month,
                    severity=severity,
                    policy_id=policy_id,
                    dataset_id=dataset_id
                )
                drifts.append(drift)
    
    return drifts


def parse_csv_content(content: str) -> List[Dict[str, Any]]:
    """Parse CSV content into list of dictionaries."""
    records = []
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        processed_row = {}
        for key, value in row.items():
            if key in ["literacy_rate", "population", "coverage_percentage", 
                      "fund_utilization", "monthly_variance"]:
                try:
                    processed_row[key] = float(value)
                except ValueError:
                    processed_row[key] = value
            else:
                processed_row[key] = value
        records.append(processed_row)
    return records


async def detect_all_drift(implementation_data: List[Dict[str, Any]], 
                          policy_intent: Dict, policy_id: str, 
                          dataset_id: str, db) -> List[DriftResult]:
    """Detect all drift instances and persist to MongoDB."""
    all_drifts = []
    
    district_groups = defaultdict(list)
    for record in implementation_data:
        district_id = record["district_id"]
        district_groups[district_id].append(record)
    
    for district_id, history in district_groups.items():
        for record in history:
            month = record.get("month", "unknown")
            metric_drifts = detect_metric_drift(
                record, policy_intent, month, policy_id, dataset_id
            )
            all_drifts.extend(metric_drifts)
        
        temporal_drifts = detect_temporal_drift(
            history, policy_intent, policy_id, dataset_id
        )
        all_drifts.extend(temporal_drifts)
    
    if db is not None and all_drifts:
        drift_collection = db["drift_results"]
        drift_docs = [drift.to_dict() for drift in all_drifts]
        await drift_collection.insert_many(drift_docs)
    
    return all_drifts

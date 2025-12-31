"""Main program that runs drift detection."""

import sys
import os
import csv
from pathlib import Path
from typing import List, Dict, Any

from intent_parser import load_policy_intent
from drift_detector import detect_all_drift
from explain import format_drift_report


def load_implementation_data(file_path: str) -> List[Dict[str, Any]]:
    """Reads district data from CSV file."""
    records = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
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


def main():
    """Runs the drift detection and prints results."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    policy_path = project_root / "data" / "policy_intent.json"
    data_path = project_root / "data" / "implementation_data.csv"
    
    if not policy_path.exists():
        print(f"Error: Policy intent file not found at {policy_path}")
        sys.exit(1)
    
    if not data_path.exists():
        print(f"Error: Implementation data file not found at {data_path}")
        sys.exit(1)
    
    try:
        policy_intent = load_policy_intent(str(policy_path))
        implementation_data = load_implementation_data(str(data_path))
        
        print(f"Policy Scheme: {policy_intent.scheme_name}")
        print(f"Loaded {len(implementation_data)} implementation records")
        print("")
        
        drifts = detect_all_drift(implementation_data, policy_intent)
        report = format_drift_report(drifts)
        
        print(report)
        
    except Exception as e:
        print(f"Error during drift detection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


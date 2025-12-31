"""Reads policy rules from JSON file."""

import json
from typing import Dict, List, Any


class PolicyIntent:
    """Stores policy rules and constraints."""
    
    def __init__(self, scheme_name: str, target_groups: List[Dict], 
                 constraints: List[Dict], target_metrics: Dict):
        self.scheme_name = scheme_name
        self.target_groups = target_groups
        self.constraints = constraints
        self.target_metrics = target_metrics
    
    def get_priority_districts(self) -> List[Dict]:
        """Gets districts marked as priority."""
        return [tg for tg in self.target_groups if tg.get("allocation_priority") == 1]
    
    def get_constraints_for_group(self, group_name: str) -> List[Dict]:
        """Gets rules that apply to a district group."""
        return [c for c in self.constraints 
                if c.get("applies_to") == group_name or c.get("applies_to") == "all"]


def load_policy_intent(file_path: str) -> PolicyIntent:
    """Reads policy rules from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return PolicyIntent(
        scheme_name=data["scheme_name"],
        target_groups=data["target_groups"],
        constraints=data["constraints"],
        target_metrics=data["target_metrics"]
    )


def matches_target_group(district_data: Dict[str, Any], target_group: Dict) -> bool:
    """Checks if a district fits a target group's criteria."""
    criteria = target_group.get("criteria", {})
    
    for field, conditions in criteria.items():
        value = district_data.get(field)
        if value is None:
            return False
        
        if "min" in conditions and value < conditions["min"]:
            return False
        if "max" in conditions and value > conditions["max"]:
            return False
    
    return True


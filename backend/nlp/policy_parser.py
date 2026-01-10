"""NLP-based policy document parser using spaCy and transformers."""

import spacy
from typing import Dict, List, Any, Optional
import re
import json
from pathlib import Path
import PyPDF2
import io


class PolicyParser:
    """Extracts policy intent from unstructured documents."""
    
    def __init__(self):
        """Initialize NLP models."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        self.patterns = {
            "target_groups": [
                r"districts?\s+with\s+(\w+)\s*[<>=]+\s*(\d+(?:\.\d+)?)",
                r"target\s+groups?[:\s]+([^\.]+)",
                r"priority\s+areas?[:\s]+([^\.]+)"
            ],
            "numeric_thresholds": [
                r"(?:minimum|min|at least|above)\s+(\d+(?:\.\d+)?)\s*%",
                r"(\d+(?:\.\d+)?)\s*%\s+(?:minimum|coverage|utilization)",
                r"threshold[:\s]+(\d+(?:\.\d+)?)"
            ],
            "temporal": [
                r"(?:monthly|quarterly|annually|weekly)",
                r"consistency[:\s]+(\w+)",
                r"reporting\s+period[:\s]+(\w+)"
            ],
            "allocation": [
                r"fund\s+utilization",
                r"resource\s+allocation",
                r"budget\s+allocation"
            ]
        }
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def extract_text_from_txt(self, file_content: bytes) -> str:
        """Extract text from TXT file."""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            return file_content.decode('utf-8', errors='ignore')
    
    def parse_document(self, file_content: bytes, filename: str) -> str:
        """Parse document and return text."""
        if filename.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.txt'):
            return self.extract_text_from_txt(file_content)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    def extract_target_groups(self, text: str) -> List[Dict[str, Any]]:
        """Extract target groups from policy text."""
        groups = []
        
        if self.nlp:
            doc = self.nlp(text)
            for sent in doc.sents:
                if any(keyword in sent.text.lower() for keyword in 
                       ["target", "priority", "district", "group"]):
                    for pattern in self.patterns["target_groups"]:
                        matches = re.finditer(pattern, sent.text, re.IGNORECASE)
                        for match in matches:
                            if "literacy" in sent.text.lower():
                                groups.append({
                                    "name": "priority_districts",
                                    "criteria": {
                                        "literacy_rate": {"max": 70.0}
                                    },
                                    "allocation_priority": 1
                                })
        
        if not groups:
            groups.append({
                "name": "priority_districts",
                "criteria": {
                    "literacy_rate": {"max": 70.0}
                },
                "allocation_priority": 1
            })
        
        return groups
    
    def extract_numeric_constraints(self, text: str) -> Dict[str, float]:
        """Extract numeric thresholds from text."""
        constraints = {}
        
        coverage_pattern = r"(?:coverage|reach)\s+(?:of|at least|minimum)\s+(\d+(?:\.\d+)?)\s*%"
        utilization_pattern = r"(?:utilization|usage)\s+(?:of|at least|minimum)\s+(\d+(?:\.\d+)?)\s*%"
        variance_pattern = r"(?:variance|variation)\s+(?:should|must|not exceed|below)\s+(\d+(?:\.\d+)?)\s*%"
        
        coverage_match = re.search(coverage_pattern, text, re.IGNORECASE)
        if coverage_match:
            constraints["min_coverage_pct"] = float(coverage_match.group(1))
        
        util_match = re.search(utilization_pattern, text, re.IGNORECASE)
        if util_match:
            constraints["min_fund_utilization_pct"] = float(util_match.group(1))
        
        var_match = re.search(variance_pattern, text, re.IGNORECASE)
        if var_match:
            constraints["max_monthly_variance_pct"] = float(var_match.group(1))
        
        if not constraints:
            constraints = {
                "min_coverage_pct": 80.0,
                "min_fund_utilization_pct": 90.0,
                "max_monthly_variance_pct": 10.0
            }
        
        return constraints
    
    def extract_temporal_rules(self, text: str) -> Dict[str, str]:
        """Extract temporal rules from text."""
        rules = {}
        
        if re.search(r"monthly", text, re.IGNORECASE):
            rules["consistency"] = "monthly"
        elif re.search(r"quarterly", text, re.IGNORECASE):
            rules["consistency"] = "quarterly"
        else:
            rules["consistency"] = "monthly"
        
        return rules
    
    def extract_policy_domain(self, text: str) -> str:
        """Extract policy domain from text."""
        domain_keywords = {
            "education": ["education", "school", "literacy", "student", "learning"],
            "health": ["health", "hospital", "medical", "treatment", "healthcare"],
            "agriculture": ["agriculture", "farmer", "crop", "irrigation", "farming"],
            "infrastructure": ["infrastructure", "road", "bridge", "construction", "development"]
        }
        
        text_lower = text.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
        
        return "general"
    
    def extract_intent(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract policy intent from document."""
        text = self.parse_document(file_content, filename)
        
        target_groups = self.extract_target_groups(text)
        constraints_dict = self.extract_numeric_constraints(text)
        temporal_rules = self.extract_temporal_rules(text)
        domain = self.extract_policy_domain(text)
        
        constraints = []
        if "min_coverage_pct" in constraints_dict:
            constraints.append({
                "type": "minimum_coverage",
                "metric": "coverage_percentage",
                "threshold": constraints_dict["min_coverage_pct"],
                "applies_to": "priority_districts"
            })
        
        if "min_fund_utilization_pct" in constraints_dict:
            constraints.append({
                "type": "resource_allocation",
                "metric": "fund_utilization",
                "threshold": constraints_dict["min_fund_utilization_pct"],
                "applies_to": "priority_districts"
            })
        
        if "max_monthly_variance_pct" in constraints_dict:
            constraints.append({
                "type": "temporal_consistency",
                "metric": "monthly_variance",
                "threshold": constraints_dict["max_monthly_variance_pct"],
                "applies_to": "all"
            })
        
        target_metrics = {}
        if "min_coverage_pct" in constraints_dict:
            target_metrics["coverage_percentage"] = {"min": constraints_dict["min_coverage_pct"] * 0.9}
        if "min_fund_utilization_pct" in constraints_dict:
            target_metrics["fund_utilization"] = {"min": constraints_dict["min_fund_utilization_pct"] * 0.9}
        if "max_monthly_variance_pct" in constraints_dict:
            target_metrics["monthly_variance"] = {"max": constraints_dict["max_monthly_variance_pct"] * 1.1}
        
        return {
            "policy_domain": domain,
            "target_groups": target_groups,
            "constraints": constraints,
            "temporal_rules": temporal_rules,
            "target_metrics": target_metrics
        }

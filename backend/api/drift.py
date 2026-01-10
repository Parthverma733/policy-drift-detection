"""Drift detection API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from bson import ObjectId
from pathlib import Path

from db.mongodb import get_db
from drift.detector import detect_all_drift, parse_csv_content, DriftResult
from explain.generator import explain_drift, generate_summary

router = APIRouter(prefix="/drift", tags=["drift"])


@router.post("/run")
async def run_drift_detection(
    policy_id: str,
    dataset_id: str,
    db = Depends(get_db)
):
    """Run drift detection for a policy and dataset."""
    try:
        policies_collection = db["policies"]
        datasets_collection = db["implementation_datasets"]
        
        policy = await policies_collection.find_one({"_id": ObjectId(policy_id)})
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        dataset = await datasets_collection.find_one({"_id": ObjectId(dataset_id)})
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        file_path = Path(dataset["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        implementation_data = parse_csv_content(csv_content)
        policy_intent = policy.get("extracted_intent", {})
        
        drifts = await detect_all_drift(
            implementation_data,
            policy_intent,
            policy_id,
            dataset_id,
            db
        )
        
        drift_list = []
        for drift in drifts:
            drift_list.append({
                "drift_type": drift.drift_type,
                "district_id": drift.district_id,
                "district_name": drift.district_name,
                "constraint_type": drift.constraint.get("type"),
                "metric": drift.constraint.get("metric"),
                "actual_value": drift.actual_value,
                "expected_threshold": drift.expected_threshold,
                "month": drift.month,
                "severity": drift.severity,
                "explanation": explain_drift(drift)
            })
        
        summary = generate_summary(drifts)
        
        return {
            "policy_id": policy_id,
            "dataset_id": dataset_id,
            "policy_title": policy.get("title"),
            "summary": summary,
            "total_drifts": len(drifts),
            "drifts": drift_list
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running drift detection: {str(e)}")


@router.get("/results")
async def get_drift_results(
    policy_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    district_id: Optional[str] = None,
    drift_type: Optional[str] = None,
    severity: Optional[str] = None,
    month: Optional[str] = None,
    db = Depends(get_db)
):
    """Get drift results with filters."""
    try:
        drift_collection = db["drift_results"]
        
        query = {}
        if policy_id:
            query["policy_id"] = ObjectId(policy_id)
        if dataset_id:
            query["dataset_id"] = ObjectId(dataset_id)
        if district_id:
            query["district_id"] = district_id
        if drift_type:
            query["drift_type"] = drift_type
        if severity:
            query["severity"] = severity
        if month:
            query["month"] = month
        
        cursor = drift_collection.find(query).sort("detected_at", -1)
        drifts = await cursor.to_list(length=1000)
        
        result = []
        for drift in drifts:
            result.append({
                "_id": str(drift["_id"]),
                "policy_id": str(drift["policy_id"]),
                "dataset_id": str(drift["dataset_id"]),
                "district_id": drift.get("district_id"),
                "district_name": drift.get("district_name"),
                "month": drift.get("month"),
                "drift_type": drift.get("drift_type"),
                "severity": drift.get("severity"),
                "constraint_type": drift.get("constraint_type"),
                "metric": drift.get("metric"),
                "actual_value": drift.get("actual_value"),
                "expected_threshold": drift.get("expected_threshold"),
                "detected_at": drift.get("detected_at").isoformat() if drift.get("detected_at") else None
            })
        
        return {"drifts": result, "count": len(result)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching drift results: {str(e)}")

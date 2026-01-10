"""Dataset management API endpoints."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from pathlib import Path

from db.mongodb import get_db

router = APIRouter(prefix="/datasets", tags=["datasets"])

UPLOAD_DIR = Path("uploads/datasets")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    policy_id: str = Form(...),
    region_level: str = Form("district"),
    time_range_start: Optional[str] = Form(None),
    time_range_end: Optional[str] = Form(None),
    db = Depends(get_db)
):
    """Upload implementation dataset."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    if not policy_id:
        raise HTTPException(status_code=400, detail="policy_id is required")
    
    try:
        file_content = await file.read()
        
        file_path = UPLOAD_DIR / f"{datetime.utcnow().timestamp()}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        dataset_doc = {
            "policy_id": ObjectId(policy_id),
            "region_level": region_level,
            "time_range": {
                "start": time_range_start or datetime.utcnow().strftime("%Y-%m"),
                "end": time_range_end or datetime.utcnow().strftime("%Y-%m")
            },
            "file_path": str(file_path),
            "uploaded_at": datetime.utcnow()
        }
        
        datasets_collection = db["implementation_datasets"]
        result = await datasets_collection.insert_one(dataset_doc)
        
        return {
            "dataset_id": str(result.inserted_id),
            "policy_id": policy_id,
            "file_path": str(file_path),
            "message": "Dataset uploaded successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading dataset: {str(e)}")


@router.get("/policy/{policy_id}")
async def get_datasets_by_policy(policy_id: str, db = Depends(get_db)):
    """Get all datasets for a policy."""
    try:
        datasets_collection = db["implementation_datasets"]
        cursor = datasets_collection.find({"policy_id": ObjectId(policy_id)})
        datasets = await cursor.to_list(length=100)
        
        result = []
        for dataset in datasets:
            result.append({
                "_id": str(dataset["_id"]),
                "policy_id": str(dataset["policy_id"]),
                "region_level": dataset.get("region_level"),
                "time_range": dataset.get("time_range"),
                "file_path": dataset.get("file_path"),
                "uploaded_at": dataset.get("uploaded_at").isoformat() if dataset.get("uploaded_at") else None
            })
        
        return {"datasets": result, "count": len(result)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching datasets: {str(e)}")

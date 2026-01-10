"""Policy management API endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId
import os
from pathlib import Path

from db.mongodb import get_db
from nlp.policy_parser import PolicyParser

router = APIRouter(prefix="/policies", tags=["policies"])
policy_parser = PolicyParser()

UPLOAD_DIR = Path("uploads/policies")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_policy(
    file: UploadFile = File(...),
    title: str = None,
    ministry: str = None,
    db = Depends(get_db)
):
    """Upload and parse a policy document."""
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    try:
        file_content = await file.read()
        
        file_path = UPLOAD_DIR / f"{datetime.utcnow().timestamp()}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        extracted_intent = policy_parser.extract_intent(file_content, file.filename)
        
        policy_doc = {
            "title": title or file.filename.replace('.pdf', '').replace('.txt', ''),
            "ministry": ministry or "General",
            "effective_period": {
                "from": datetime.utcnow().strftime("%Y-%m"),
                "to": None
            },
            "raw_document_path": str(file_path),
            "extracted_intent": extracted_intent,
            "version": 1,
            "created_at": datetime.utcnow()
        }
        
        policies_collection = db["policies"]
        result = await policies_collection.insert_one(policy_doc)
        
        policy_doc["_id"] = str(result.inserted_id)
        policy_doc["raw_document_path"] = str(file_path)
        
        return {
            "policy_id": str(result.inserted_id),
            "title": policy_doc["title"],
            "extracted_intent": extracted_intent,
            "message": "Policy uploaded and parsed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing policy: {str(e)}")


@router.get("")
async def list_policies(db = Depends(get_db)):
    """List all policies."""
    try:
        policies_collection = db["policies"]
        cursor = policies_collection.find({}).sort("created_at", -1)
        policies = await cursor.to_list(length=100)
        
        result = []
        for policy in policies:
            result.append({
                "_id": str(policy["_id"]),
                "title": policy.get("title"),
                "ministry": policy.get("ministry"),
                "effective_period": policy.get("effective_period"),
                "version": policy.get("version", 1),
                "created_at": policy.get("created_at").isoformat() if policy.get("created_at") else None,
                "extracted_intent": policy.get("extracted_intent", {})
            })
        
        return {"policies": result, "count": len(result)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching policies: {str(e)}")


@router.get("/{policy_id}")
async def get_policy(policy_id: str, db = Depends(get_db)):
    """Get policy details by ID."""
    try:
        policies_collection = db["policies"]
        policy = await policies_collection.find_one({"_id": ObjectId(policy_id)})
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return {
            "_id": str(policy["_id"]),
            "title": policy.get("title"),
            "ministry": policy.get("ministry"),
            "effective_period": policy.get("effective_period"),
            "raw_document_path": policy.get("raw_document_path"),
            "extracted_intent": policy.get("extracted_intent", {}),
            "version": policy.get("version", 1),
            "created_at": policy.get("created_at").isoformat() if policy.get("created_at") else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching policy: {str(e)}")


@router.delete("/{policy_id}")
async def delete_policy(policy_id: str, db = Depends(get_db)):
    """Delete a policy and all associated data."""
    try:
        policies_collection = db["policies"]
        datasets_collection = db["implementation_datasets"]
        drift_collection = db["drift_results"]
        chat_sessions_collection = db["chat_sessions"]
        chat_messages_collection = db["chat_messages"]
        
        policy_obj_id = ObjectId(policy_id)
        
        # Check if policy exists
        policy = await policies_collection.find_one({"_id": policy_obj_id})
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Delete associated datasets
        datasets_result = await datasets_collection.delete_many({"policy_id": policy_obj_id})
        
        # Delete associated drift results
        drift_result = await drift_collection.delete_many({"policy_id": policy_obj_id})
        
        # Delete associated chat sessions and messages
        chat_sessions = await chat_sessions_collection.find({"policy_id": policy_obj_id}).to_list(length=1000)
        session_ids = [ObjectId(str(session["_id"])) for session in chat_sessions]
        if session_ids:
            await chat_messages_collection.delete_many({"session_id": {"$in": session_ids}})
        await chat_sessions_collection.delete_many({"policy_id": policy_obj_id})
        
        # Delete the policy itself
        await policies_collection.delete_one({"_id": policy_obj_id})
        
        # Optionally delete the uploaded file
        import os
        file_path = policy.get("raw_document_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Ignore file deletion errors
        
        return {
            "message": "Policy and all associated data deleted successfully",
            "policy_id": policy_id,
            "deleted_datasets": datasets_result.deleted_count,
            "deleted_drifts": drift_result.deleted_count,
            "deleted_chat_sessions": len(session_ids)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting policy: {str(e)}")

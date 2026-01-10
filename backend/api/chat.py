"""Chat API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

from db.mongodb import get_db
from chat.rag_engine import chatbot

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/start")
async def start_chat_session(
    policy_id: str,
    db = Depends(get_db)
):
    """Start a new chat session."""
    try:
        policies_collection = db["policies"]
        policy = await policies_collection.find_one({"_id": ObjectId(policy_id)})
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        session_doc = {
            "policy_id": ObjectId(policy_id),
            "created_at": datetime.utcnow()
        }
        
        sessions_collection = db["chat_sessions"]
        result = await sessions_collection.insert_one(session_doc)
        
        return {
            "session_id": str(result.inserted_id),
            "policy_id": policy_id,
            "created_at": session_doc["created_at"].isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting chat session: {str(e)}")


@router.post("/message")
async def send_message(
    session_id: str,
    message: str,
    db = Depends(get_db)
):
    """Send a message in a chat session."""
    try:
        sessions_collection = db["chat_sessions"]
        messages_collection = db["chat_messages"]
        
        session = await sessions_collection.find_one({"_id": ObjectId(session_id)})
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        policy_id = str(session["policy_id"])
        
        user_message_doc = {
            "session_id": ObjectId(session_id),
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow()
        }
        await messages_collection.insert_one(user_message_doc)
        
        context = await chatbot.retrieve_context(message, policy_id, db)
        response_text = chatbot.generate_response(message, context)
        
        assistant_message_doc = {
            "session_id": ObjectId(session_id),
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow()
        }
        await messages_collection.insert_one(assistant_message_doc)
        
        return {
            "session_id": session_id,
            "response": response_text,
            "timestamp": assistant_message_doc["timestamp"].isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/sessions/{session_id}/messages")
async def get_chat_messages(
    session_id: str,
    db = Depends(get_db)
):
    """Get all messages for a chat session."""
    try:
        messages_collection = db["chat_messages"]
        cursor = messages_collection.find(
            {"session_id": ObjectId(session_id)}
        ).sort("timestamp", 1)
        messages = await cursor.to_list(length=100)
        
        result = []
        for msg in messages:
            result.append({
                "_id": str(msg["_id"]),
                "role": msg.get("role"),
                "content": msg.get("content"),
                "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") else None
            })
        
        return {"messages": result, "count": len(result)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")

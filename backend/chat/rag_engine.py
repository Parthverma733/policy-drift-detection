"""RAG-based chatbot engine for policy-aware queries using Gemini API (new SDK)."""

from typing import Dict, Any
from bson import ObjectId
import re
import os
import asyncio
import PyPDF2
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv(override=False)

# Load API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
print(f"DEBUG: GEMINI_API_KEY loaded: {'Yes' if GEMINI_API_KEY else 'No'}")

# Initialize Gemini client (new SDK)
gemini_client = None
if GEMINI_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("✓ Gemini client initialized (google-genai)")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        gemini_client = None
else:
    print("⚠️ No GEMINI_API_KEY found, using fallback mode")


class PolicyChatbot:
    """Policy-aware chatbot using RAG with Gemini API."""

    def __init__(self):
        self.client = gemini_client
        self.model_name = "models/gemini-pro"
        print(f"DEBUG: Chatbot initialized, Gemini enabled: {bool(self.client)}")

    # ------------------------------------------------------------------
    # Document reading
    # ------------------------------------------------------------------
    def read_policy_document(self, file_path: str) -> str:
        if not file_path or not os.path.exists(file_path):
            return ""

        try:
            if file_path.lower().endswith(".pdf"):
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    return "\n".join(page.extract_text() or "" for page in reader.pages)

            if file_path.lower().endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()

        except Exception as e:
            print(f"❌ Error reading policy document: {e}")

        return ""

    # ------------------------------------------------------------------
    # Context retrieval (MongoDB)
    # ------------------------------------------------------------------
    async def retrieve_context(self, query: str, policy_id: str, db) -> Dict[str, Any]:
        context = {
            "policy": None,
            "policy_text": "",
            "drift_results": [],
            "summaries": {}
        }

        policy_obj_id = ObjectId(policy_id)
        policy = await db["policies"].find_one({"_id": policy_obj_id})

        if policy:
            context["policy"] = {
                "title": policy.get("title"),
                "ministry": policy.get("ministry"),
                "extracted_intent": policy.get("extracted_intent", {})
            }

            file_path = policy.get("raw_document_path")
            if file_path:
                context["policy_text"] = self.read_policy_document(file_path)

        query_lower = query.lower()
        drift_collection = db["drift_results"]

        if any(w in query_lower for w in ["drift", "violation", "flag", "district", "issue"]):
            drifts = await drift_collection.find(
                {"policy_id": policy_obj_id}
            ).limit(30).to_list(length=30)

            district_match = re.search(r"district\s+(\w+)", query_lower)
            if district_match:
                name = district_match.group(1)
                drifts = [
                    d for d in drifts
                    if name.lower() in d.get("district_name", "").lower()
                ]

            context["drift_results"] = drifts

        return context

    # ------------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------------
    def build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        policy = context.get("policy") or {}
        policy_text = context.get("policy_text", "")
        drifts = context.get("drift_results", [])

        if len(policy_text) > 15000:
            policy_text = policy_text[:15000] + "\n...(truncated)"

        prompt = f"""
You are a government policy analysis assistant.

Answer strictly using the provided policy document and drift data.
If information is missing, say so clearly.

## Policy
Title: {policy.get("title", "N/A")}
Ministry: {policy.get("ministry", "N/A")}

## Policy Document
{policy_text}

## Drift Results
"""

        for i, d in enumerate(drifts[:15], 1):
            prompt += (
                f"{i}. District: {d.get('district_name')}\n"
                f"   Metric: {d.get('metric')}\n"
                f"   Actual: {d.get('actual_value')}\n"
                f"   Expected: {d.get('expected_threshold')}\n"
                f"   Severity: {d.get('severity')}\n"
                f"   Explanation: {d.get('explanation')}\n\n"
            )

        prompt += f"""
## User Question
{query}

Provide a clear, structured answer.
"""

        return prompt

    # ------------------------------------------------------------------
    # Gemini response
    # ------------------------------------------------------------------
    async def generate_response(self, query: str, context: Dict[str, Any]) -> str:
        if not context.get("policy"):
            return "Policy not found."

        if not self.client:
            return self.generate_fallback_response(query, context)

        prompt = self.build_prompt(query, context)
        print(f"DEBUG: Prompt length = {len(prompt)}")

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )
            return response.text or "No response generated."

        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self.generate_fallback_response(query, context)

    # ------------------------------------------------------------------
    # Fallback logic
    # ------------------------------------------------------------------
    def generate_fallback_response(self, query: str, context: Dict[str, Any]) -> str:
        drifts = context.get("drift_results", [])
        policy = context.get("policy", {})
        title = policy.get("title", "the policy")

        if "why" in query.lower() and drifts:
            d = drifts[0]
            return (
                f"District {d.get('district_name')} was flagged due to "
                f"{d.get('drift_type')} drift. "
                f"Actual value {d.get('actual_value')} exceeded "
                f"threshold {d.get('expected_threshold')}."
            )

        return (
            f"I can help analyze '{title}', but advanced AI reasoning "
            f"is unavailable right now."
        )


chatbot = PolicyChatbot()

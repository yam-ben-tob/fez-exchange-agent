from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from fastapi.staticfiles import StaticFiles
from outputs.agent_info_examples import load_formatted_snapshot
import uvicorn
import os
import json
from pathlib import Path

from orchestration.supervisor import Supervisor

app = FastAPI()
agent = Supervisor()

# --- STRICT SCHEMA DEFINITIONS ---
class ExecuteRequest(BaseModel):
    prompt: str

class StepLog(BaseModel):
    module: str
    prompt: Dict[str, Any]
    response: Dict[str, Any]

class ExecuteResponse(BaseModel):
    status: str
    error: Optional[str] = None
    response: Optional[str] = None
    steps: List[StepLog] = []

# --- THE 4 REQUIRED ENDPOINTS ---

@app.get("/api/team_info")
def get_team_info():
    return {
        "group_batch_order_number": "03_10", 
        "team_name": "Fez Exchange Agent",
        "students": [
            { "name": "Yam Ben Tov", "email": "yam.b@campus.technion.ac.il" },
            { "name": "Asaf Greenstein", "email": "asaf.g@campus.technion.ac.il" },
            { "name": "Anna Sakoun", "email": "anna.sakoun@campus.technion.ac.il"}
        ]
    }

@app.get("/api/agent_info")
def get_agent_info():
    return {
        "description": "Multi-agent orchestration system for global university exchange placement. Uses Filter (Supabase), Ranker (LLM), and Analyzer (Pinecone RAG + LLM) to recommend universities.",
        "purpose": "Filters universities by academic/language/availability criteria, ranks by preferences, and analyzes top matches for logistics and fit.",
        "prompt_template": {
            "template": {
                "academic_profile": {
                    "gpa": "float (grade in GPA format: e.g., 3.2, 4.0)",
                    "major": "string (e.g., 'Computer Science', 'Physics')",
                    "study_level": "string ('bsc' or 'msc')",
                    "semesters_completed": "integer (e.g., 2, 4, 6)"
                },
                "language_profile": {
                    "non_english_languages": ["array of strings"],
                    "english_test_type": ["array of strings (e.g., 'TOEFL', 'IELTS', 'Duolingo', 'CET', 'IGCSE')"],
                    "english_test_level": "string (CEFR levels: e.g., 'B1', 'B2', 'C1')"
                },
                "availability": {
                    "start_month": "integer (1-12) or null",
                    "start_day": "integer (1-31) or null",
                    "end_month": "integer (1-12) or null",
                    "end_day": "integer (1-31) or null"
                },
                "preferences": {
                    "must_be_erasmus": "boolean (scholarship program flag: e.g., true, false)",
                    "free_language_preferences": "string (vibe, budget, and location)"
                }
            },
        },
        "prompt_examples": [
            load_formatted_snapshot("snapshot_test_default_turn_1.json"),
            load_formatted_snapshot("snapshot_test_high_gpa_turn_1.json"),
            load_formatted_snapshot("snapshot_test_asia_tech_specialist_turn_1.json")
        ]
    }

@app.get("/api/model_architecture")
def get_architecture():
    # os.getcwd() points to /opt/render/project/src/ on Render
    base_dir = Path(os.getcwd()) 
    
    # Point directly to the file in the root
    file_path = base_dir / "system_architechture.png"
    
    if file_path.exists():
        return FileResponse(file_path, media_type="image/png")
    
    raise HTTPException(
        status_code=404, 
        detail=f"Architecture diagram not found at {file_path}"
    )

@app.post("/api/execute", response_model=ExecuteResponse)
def execute_agent(request: ExecuteRequest):
    try:
        try:
            user_profile = json.loads(request.prompt)
            chat_msg = ""
        # If it fails, it's a plain text chat message
        except json.JSONDecodeError:
            user_profile = {}         
            chat_msg = request.prompt  
            
        result = agent.run(new_chat_message=chat_msg, user_profile_dict=user_profile)

        return {
            "status": "ok",
            "error": None,
            "response": json.dumps(result.get("analysis", [])),
            "steps": result.get("steps", [])
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e), 
            "response": None, 
            "steps": []
        }

# This tells FastAPI: "If the route isn't an /api/ route, look in the 'static' folder for an index.html file"
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

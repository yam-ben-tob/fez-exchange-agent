from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import json

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
    response: Any = None
    steps: List[StepLog] = []

# --- THE 4 REQUIRED ENDPOINTS ---

@app.get("/api/team_info")
def get_team_info():
    return {
        "group_batch_order_number": "01_01", # Update this later
        "team_name": "Fez Exchange Agent",
        "students": [
            { "name": "Yam Ben Tob", "email": "yam.b@campus.technion.ac.il" },
            { "name": "Asaf Greenstein", "email": "asaf.g@campus.technion.ac.il" }
        ]
    }

@app.get("/api/agent_info")
def get_agent_info():
    return {
        "description": "Conversation-aware multi-agent orchestration system for global university exchange placement. Uses Filter (Supabase), Ranker (LLM), CourseFinder (ReAct + RAG + Web), and Analyzer (Pinecone RAG + LLM) to recommend universities and matched courses.",
        "purpose": "Filters universities by academic/language/availability criteria, ranks by preferences, finds courses, and analyzes top matches for logistics and fit. Supports follow-up prompts (e.g. 'show more', 'find courses', 'something cheaper').",
        "prompt_template": {
            "template": '{"academic_profile": {"gpa": 85, "major": "Computer Science"}, "preferences": {"free_language_preferences": "social scene, party vibe"}, "language_profile": {}, "availability": {}}'
        },
        "prompt_examples": [
            {
                "prompt": '{"academic_profile": {"gpa": 85}, "preferences": {"free_language_preferences": "party vibe, easy to make friends"}}',
                "full_response": "**1. CTU (Prague)**\n   Fit: Strong social scene, Erasmus presence...\n   Academic: 30 ECTS min...\n   Logistics: Housing lottery, ~$3.5k/semester.\n   Courses: Introduction to Algorithms, Data Structures...",
                "steps": [
                    {"module": "Filter", "prompt": {"action": "Query Supabase", "criteria": {}}, "response": {"found_universities": 12}},
                    {"module": "Ranker", "prompt": {"llm_prompt": "..."}, "response": {"top_universities": ["CTU (Prague)", "DTU", "Politecnico di Milano"]}},
                    {"module": "CourseFinder", "prompt": {"universities": ["CTU (Prague)"], "major": "CS"}, "response": {"courses_found": 5, "courses": [...]}},
                    {"module": "Analyzer", "prompt": {"target_university": "CTU (Prague)"}, "response": {"logistics": {...}}}
                ]
            }
        ],
        "full_response": "Structured JSON with analysis (university_name, general_fit_reasoning, requirements, logistics, matched_courses) per university.",
        "steps": [
            {
                "module": "Filter",
                "prompt": {"action": "Query Supabase", "criteria": "user profile"},
                "response": {
                    "found_universities": 12,
                    "traced_steps": [
                        "filtered by GPA >= 3.0",
                        "filtered by English test level >= B2"
                    ]
                }
            },
            {
                "module": "Ranker",
                "prompt": {"llm_prompt": "Example ranking prompt..."},
                "response": {
                    "scored_universities": [
                        {"university_name": "CTU (Prague)", "total_score": 92},
                        {"university_name": "DTU", "total_score": 88}
                    ],
                    "top_universities": ["CTU (Prague)", "DTU"]
                }
            },
            {
                "module": "CourseFinder",
                "prompt": {"universities": ["CTU (Prague)"], "major": "Computer Science", "languages": ["English"]},
                "response": {
                    "courses_found": 3,
                    "courses": [
                        {
                            "university_name": "CTU (Prague)",
                            "matched_courses": [
                                {"course_name": "Algorithms", "language": "English", "relevance": "Core CS requirement"},
                                {"course_name": "Data Structures", "language": "English", "relevance": "Highly relevant to major"}
                            ]
                        }
                    ]
                }
            },
            {
                "module": "Analyzer",
                "prompt": {"target_university": "CTU (Prague)"},
                "response": {
                    "logistics": {
                        "academic": {
                            "min_credits_required": 24,
                            "max_credits_allowed": 36,
                            "instruction_languages": "English",
                            "grading_system_summary": "Local grading scale mapped to ECTS.",
                            "academic_summary_notes": "Balanced workload with strong CS focus."
                        },
                        "housing_and_logistics": {
                            "campus_housing_guaranteed": False,
                            "housing_details": "Student dorms allocated on a first-come, first-served basis; private rentals available.",
                            "university_sponsors_visa": False,
                            "estimated_visa_processing_weeks": 10,
                            "mandatory_insurance_required": True,
                            "medical_and_insurance_details": "Exchange students must show proof of health insurance.",
                            "currency": "EUR",
                            "estimated_housing_cost_per_month": "400-600",
                            "estimated_living_cost_per_month": "800-1000",
                            "logistics_summary_notes": "Affordable housing and living costs compared to Western Europe."
                        },
                        "student_integration": {
                            "buddy_program_available": True,
                            "orientation_program_provided": True,
                            "orientation_is_mandatory": False,
                            "pre_semester_language_course_available": True,
                            "language_course_details": "Optional pre-semester Czech language course.",
                            "integration_summary_notes": "Active ESN chapter and strong Erasmus community."
                        }
                    }
                }
            }
        ]
    }

@app.get("/api/model_architecture")
def get_architecture():
    base = os.path.dirname(os.path.abspath(__file__))
    for name in ("architecture.png", "architecture_placeholder.png"):
        file_path = os.path.join(base, "..", name)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Image not found")

@app.post("/api/execute", response_model=ExecuteResponse)
def execute_agent(request: ExecuteRequest):
    try:
        try:
            user_profile = json.loads(request.prompt)
            chat_msg = ""
        # 2. If it fails, it's a plain text chat message
        except json.JSONDecodeError:
            user_profile = {}         
            chat_msg = request.prompt  
            
        result = agent.run(new_chat_message=chat_msg, user_profile_dict=user_profile)

        response_payload = json.dumps({
            "analysis": result.get("analysis", []),
            "courses": result.get("courses", []),
        })

        return {
            "status": "ok",
            "error": None,
            "response": response_payload,
            "steps": result.get("steps", []),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "response": None,
            "steps": [],
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

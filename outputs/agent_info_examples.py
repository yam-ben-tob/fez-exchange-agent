import json
from pathlib import Path

def load_formatted_snapshot(filename):
    """Parses a raw snapshot into the 'Readable' API format."""
    # Path to your root/outputs/ folder
    file_path = Path(__file__).resolve().parent.parent / "outputs" / filename
    
    if not file_path.exists():
        return {"prompt": "File not found", "full_response": "", "steps": []}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return {
        "prompt": data.get("user_iformation", {}), # Returns a dict {}
        "full_response": data.get("analysis", []), # Returns a list []
        "steps": data.get("steps", [])              # Returns a list []
    }

    # # Format Prompt (User Info) as a clean JSON string
    # prompt_str = json.dumps(data.get("user_iformation", {}), indent=2)

    # # Format Full Response as Markdown for the reader
    # analysis_list = data.get("analysis", [])
    # full_response_str = json.dumps(analysis_list, indent=2)
    
    # return {
    #     "prompt": prompt_str,
    #     "full_response": full_response_str,
    #     "steps": data.get("steps", [])
    # }
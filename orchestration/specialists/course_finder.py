import json
from crawl4ai import AsyncWebCrawler
from utils.llmod_client import llmod_chat
import asyncio

def get_catalog_url(university: str, country: str) -> str:
    """
    Retrieves the official English course catalog URL via LLM.
    """
    system_prompt = (
        "You are a technical assistant. Provide the direct official URL for the "
        "English-language course catalog for the specified university. "
        "Return ONLY a JSON object with the key 'url'."
    )
    
    user_prompt = f"University: {university}\nCountry: {country}"
    
    print(f"[LOG] Requesting catalog URL for: {university}")
    try:
        raw_response = llmod_chat(system_prompt, user_prompt, use_json=True)
        data = json.loads(raw_response)
        url = data.get("url")
        return url
    except Exception as e:
        print(f"[ERROR] Failed to retrieve URL: {e}")
        return None

async def courses_finder(university: str, country: str, major: str, semester: str):
    """
    Navigates through catalog pages to extract specific courses.
    """
    current_url = get_catalog_url(university, country)
    
    if not current_url:
        return {"error": "Initialization failed: No starting URL found."}
        
    found_courses = []
    
    async with AsyncWebCrawler() as crawler:
        for page_num in range(1, 4): # Limit to 3 pages for safety
            print(f"[LOG] Scraping Page {page_num}: {current_url}")
            
            result = await crawler.arun(url=current_url)
            
            agent_prompt = (
                f"Extract {major} courses in English for {semester} semester. "
                f"Identify the 'Next' page URL if present.\n"
                f"Return JSON: {{'courses': [{{'course_name': '', 'description': ''}}], 'next_page_url': ''}}"
            )
            
            # Context management: cap at 12k chars
            llm_response = llmod_chat(agent_prompt, result.markdown[:12000], use_json=True)
            page_data = json.loads(llm_response)
            
            extracted = page_data.get("courses", [])
            print(f"[DATA] Extracted {len(extracted)} courses from current page.")
            found_courses.extend(extracted)
            
            if len(found_courses) >= 5:
                print("[STATUS] Threshold reached. Stopping.")
                break
                
            next_url = page_data.get("next_page_url")
            if not next_url:
                print("[STATUS] End of pagination.")
                break
            
            current_url = next_url 

    return found_courses[:5]
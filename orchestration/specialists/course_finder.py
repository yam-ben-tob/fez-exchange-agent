import json
import asyncio
from crawl4ai import AsyncWebCrawler
from utils.llmod_client import llmod_chat

import json

def get_catalog_url(university: str, country: str) -> str:
    """
    Helper function to find the official English course catalog URL 
    for a given university using LLMOD.
    """
    system_prompt = (
        "You are an expert academic web navigator helping international exchange students. "
        "Your task is to provide the most accurate, direct official URL for the English-language "
        "course catalog, course search portal, or international exchange module list for the given university. "
        "Do not provide explanations. Return ONLY a valid JSON object."
    )
    
    user_prompt = (
        f"University: {university}\n"
        f"Country: {country}\n"
        f"Target: Find the direct URL to search or browse courses taught in English."
    )
    
    try:
        # Call your existing LLM wrapper
        raw_response = llmod_chat(system_prompt, user_prompt, use_json=True)
        data = json.loads(raw_response)
        
        # Extract the URL from the JSON
        target_url = data.get("url")
        
        if not target_url:
            print(f"Warning: LLM could not determine a URL for {university}.")
            return None
            
        return target_url
        
    except json.JSONDecodeError:
        print(f"Error: LLM did not return valid JSON for {university}.")
        return None
    except Exception as e:
        print(f"Error finding URL: {e}")
        return None
    
async def courses_finder(university: str, country: str, major: str, semester: str):
    
    # 1. Dynamically find the starting URL
    current_url = get_catalog_url(university, country)
    
    if not current_url:
        return {"error": f"Could not find a starting catalog URL for {university}."}
        
    print(f"Starting URL found: {current_url}")
    
    found_courses = []
    
    async with AsyncWebCrawler() as crawler:
        # Loop up to 10 times to prevent infinite loops
        for page_num in range(1, 11):
            print(f"Scraping: {current_url}")
            
            # 1. Scrape the current page
            result = await crawler.arun(url=current_url)
            
            # 2. Ask the LLM to extract courses AND find the next page link
            agent_prompt = (
                f"You are an academic assistant. Review this course catalog text.\n"
                f"TASK 1: Extract courses for '{major}' taught in English during the '{semester}' semester.\n"
                f"TASK 2: Look at the pagination links at the bottom of the page. Find the URL for the 'Next' page.\n"
                f"Respond ONLY in this strictly formatted JSON structure:\n"
                f"{{\n"
                f"  'courses': [{{'course_name': '...', 'description': '...'}}],\n"
                f"  'next_page_url': 'https://...' (or null if there is no next page)\n"
                f"}}"
            )
            
            # Pass the markdown (which includes link URLs) to the LLM
            llm_response = llmod_chat(agent_prompt, result.markdown[:15000], use_json=True)
            page_data = json.loads(llm_response)
            
            # 3. Save the courses
            found_courses.extend(page_data.get("courses", []))
            
            # 4. Stop if we have enough courses
            if len(found_courses) >= 5:
                print("Found 5 courses! Stopping.")
                break
                
            # 5. Handle the Next Page dynamically
            next_url = page_data.get("next_page_url")
            
            if not next_url:
                print("No 'Next' page found by LLM. Reached the end.")
                break
            else:
                # Update the URL for the next loop iteration
                current_url = next_url 

    return found_courses[:5]
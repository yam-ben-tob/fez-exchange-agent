import asyncio
import json
# Import the function from your orchestration folder
from orchestration.specialists.course_finder import courses_finder

async def main():
    print("--- SYSTEM START: COURSE DISCOVERY TEST ---")
    
    # Configuration for the test run
    test_params = {
        "university": "Technical University of Munich",
        "country": "Germany",
        "major": "Computer Science",
        "semester": "Winter"
    }

    print(f"[TEST] Testing with: {test_params['university']}")
    
    # Execute the finder
    results = await courses_finder(**test_params)

    # Output formatting
    print("\n" + "="*50)
    print("FINAL TEST OUTPUT:")
    print(json.dumps(results, indent=2))
    print("="*50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Test interrupted by user.")
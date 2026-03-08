from orchestration.supervisor import Supervisor  # Assuming your class is in supervisor.py
from tests.user_profiles import get_student_profiles
import json

def run_demonstration():
    print("🚀 Starting Multi-Agent Exchange Search...")
    agent = Supervisor()
    profiles = get_student_profiles()
    
    # We only want to run these three specific test cases
    test_cases = ["default", "high_gpa", "asia_tech_specialist"]
    
    for profile_name in test_cases:
        print(f"\n--- Processing User: {profile_name} ---")
        
        # Use the profile name as the thread_id to keep snapshots organized
        try:
            result = agent.run(
                user_profile_dict=profiles[profile_name],
                thread_id=f"test_{profile_name}"
            )
            print(f"✅ Success! Analysis for {profile_name} complete.")
            print(f"📄 Snapshot saved to: outputs/snapshot_test_{profile_name}_turn_1.json")
        except Exception as e:
            print(f"❌ Failed to process {profile_name}: {e}")

    print("\n✨ All test runs complete. Check the 'outputs' folder for full traces.")

if __name__ == "__main__":
    run_demonstration()
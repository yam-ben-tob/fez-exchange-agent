import streamlit as st
import json
import requests
import os
import pandas as pd
from tests.user_profiles import get_student_profiles
from orchestration.supervisor import Supervisor
import calendar

# --- HELPER FUNCTIONS ---
def render_student_profile_sidebar():
    """
    Renders the student profile input forms in the sidebar and 
    returns the structured dictionary.
    """
    with st.sidebar:
        st.header("Search Settings")
        
        # Load the default profile from your existing utility
        user_dict = get_student_profiles().get("default", {})
        
        # Initialize the nested structure exactly as required
        profile = {
            "academic_profile": {},
            "language_profile": {},
            "availability": {},
            "preferences": {}
        }

        # 1. Academic Profile
        st.markdown("### 🎓 Academic Profile")
        acad = user_dict.get("academic_profile", {})
        profile["academic_profile"]["gpa"] = st.number_input(
            "GPA", value=float(acad.get("gpa", 0.0)), step=0.1
        )
        profile["academic_profile"]["major"] = st.text_input(
            "Major", value=acad.get("major", "")
        )
        profile["academic_profile"]["study_level"] = st.selectbox(
            "Study Level", options=["bsc", "msc", "phd"], 
            index=["bsc", "msc", "phd"].index(acad.get("study_level", "bsc"))
        )
        profile["academic_profile"]["semesters_completed"] = st.number_input(
            "Semesters Completed", value=int(acad.get("semesters_completed", 0))
        )

        # 2. Language Profile
        st.markdown("---")
        st.markdown("### 🗣️ Languages")
        lang = user_dict.get("language_profile", {})
        profile["language_profile"]["non_english_languages"] = st.multiselect(
            "Non-English Languages", 
            options=["Spanish", "French", "German", "Italian", "Chinese", "Korean", "Japanese"],
            default=lang.get("non_english_languages", [])
        )
        profile["language_profile"]["english_test_type"] = st.multiselect(
            "English Test Type", 
            options=["TOEFL", "IELTS", "Duolingo", "Cambridge"],
            default=lang.get("english_test_type", [])
        )
        profile["language_profile"]["english_test_level"] = st.text_input(
            "English Level (e.g. B2)", value=lang.get("english_test_level", "")
        )

        # 3. Availability
        st.markdown("---")
        st.markdown("### 📅 Availability")
        avail = user_dict.get("availability", {})
        c1, c2 = st.columns(2)
        with c1:
            profile["availability"]["start_month"] = st.number_input("Start Month", 1, 12, int(avail.get("start_month", 8)))
            profile["availability"]["start_day"] = st.number_input("Start Day", 1, 31, int(avail.get("start_day", 1)))
        with c2:
            profile["availability"]["end_month"] = st.number_input("End Month", 1, 12, int(avail.get("end_month", 12)))
            profile["availability"]["end_day"] = st.number_input("End Day", 1, 31, int(avail.get("end_day", 31)))

        # 4. Preferences
        st.markdown("---")
        st.markdown("### 🎯 Preferences")
        pref = user_dict.get("preferences", {})
        profile["preferences"]["must_be_erasmus"] = st.checkbox(
            "Must be Erasmus", value=bool(pref.get("must_be_erasmus", False))
        )
        profile["preferences"]["free_language_preferences"] = st.text_area(
            "Additional Preferences & Context", 
            value=pref.get("free_language_preferences", ""), 
            height=200
        )

        st.markdown("---")
        st.markdown("### 📥 Step 2: Start Analysis")
        st.caption("Double-check your info above, then hit the button below.")
        
        # We define the button HERE. 'type="primary"' makes it stand out.
        run_pressed = st.button("🚀 RUN ANALYSIS", use_container_width=True, type="primary")
       
        return profile, run_pressed


def format_exchange_date(month, day):
    if not month:
        return "TBD"
    
    # Get month name (e.g., 9 -> "September")
    month_name = calendar.month_name[int(month)]
    
    # If day exists, return "Day MonthName", else just "MonthName"
    if day and str(day).lower() != 'none':
        return f"{day} {month_name}"
    return month_name

# --- GLOBAL STYLES (Larger Text) ---
st.markdown("""
    <style>
        /* 1. Global Scaling - Increases the base size for everything */
        html, body, [class*="st-"] { 
            font-size: 1.15rem; 
        }

        /* 2. Content Specifics - Paragraphs and standard text */
        .stMarkdown p, .stText { 
            font-size: 1.25rem !important; 
            line-height: 1.6;
        }

        /* 3. Headers - Making them distinct and large */
        .stMarkdown h3 { font-size: 2.0rem !important; font-weight: 700 !important; }
        .stMarkdown h4 { font-size: 1.6rem !important; color: #1f77b4; font-weight: 600 !important; }

        /* 4. Tabs - Essential for your University names */
        button[data-baseweb="tab"] p { 
            font-size: 1.4rem !important; 
            font-weight: 600 !important; 
        }

        /* 5. Tables & Dataframes - Ensures requirements are readable */
        [data-testid="stTable"] td, [data-testid="stDataFrame"] td, [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }

        /* 6. Expanders - Fixing the small text inside notes */
        .stDetails {
            font-size: 1.15rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- SETTINGS ---
USE_API = False  
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

st.set_page_config(page_title="Exchange Agent Pro", layout="wide")
st.title("🎓 University Selection Dashboard")

# Initialize local agent in session state so it remembers memory between clicks
if not USE_API:
    if Supervisor is None:
        st.error("Supervisor class could not be imported. Please check your local imports or switch USE_API to True.")
    elif "agent" not in st.session_state:
        st.session_state.agent = Supervisor()

# --- Sidebar Input ---
user_dict, run_button = render_student_profile_sidebar()
raw_user_str = json.dumps(user_dict)

# --- Main Logic ---
if run_button:
    with st.spinner("Analyzing universities..."):
        try:
            # ==========================================
            # 1. DATA FETCHING (Local vs Server)
            # ==========================================
            if USE_API:
                # --- SERVER RUN ---
                # The API returns "response" as a stringified JSON to satisfy the strict rubric
                res = requests.post(f"{API_URL}/execute", json={"prompt": raw_user_str})
                data = res.json()
                
            else:
                # --- LOCAL RUN ---
                # Replicate the exact routing logic from your FastAPI endpoint
                try:
                    user_profile = json.loads(raw_user_str)
                    chat_msg = "" 
                except json.JSONDecodeError:
                    user_profile = {}
                    chat_msg = raw_user_str
                
                try:
                    # Run the agent directly. result["analysis"] is a Python list of dicts.
                    result = st.session_state.agent.run(
                        new_chat_message=chat_msg, 
                        user_profile_dict=user_profile
                    )
                    
                    # MOCK THE API EXACTLY: Convert the native Python list into a string
                    # so the downstream UI code handles local and server data identically!
                    data = {
                        "status": "ok",
                        "error": None,
                        "response": json.dumps(result.get("analysis", [])), 
                        "steps": result.get("steps", [])
                    }
                except Exception as local_e:
                    # Mock an API error format if the agent crashes locally
                    data = {
                        "status": "error",
                        "error": str(local_e),
                        "response": "[]",
                        "steps": []
                    }

            # ==========================================
            # 2. UI RENDERING (Updated for New Analyzer Fields)
            # ==========================================

            if data.get("status") == "ok":
                raw_response_string = data.get("response", "[]")
                try:
                    universities = json.loads(raw_response_string)
                except json.JSONDecodeError:
                    universities = [] 
                    st.warning("Could not parse the university data from the response string.")
                
                agent_steps = data.get("steps", [])
                st.success(f"Analysis Complete! Found {len(universities)} matches.")
                
                if universities:
                    uni_names = [u.get("university_name", "Unknown") for u in universities]
                    tabs = st.tabs(uni_names)
                    
                    for i, tab in enumerate(tabs):
                        uni = universities[i]
                        reqs = uni.get("requirements", {})
                        logistics = uni.get("logistics", {})
                        
                        # Sub-categories from your updated prompt
                        acad = logistics.get("academic", {})
                        house = logistics.get("housing_and_logistics", {})
                        integ = logistics.get("student_integration", {})

                        with tab:
                        # Top Level Info
                            # Calculate the rank (1-based index)
                            rank = i + 1
                            rank_suffix = "st" if rank == 1 else "nd" if rank == 2 else "rd" if rank == 3 else "th"
                            
                            # Updated Info Banner with Country and Custom Ranking Text
                            st.info(
                                f"**Country:** {reqs.get('country', 'N/A')}\n\n"
                                f"**Why this was chosen for you and ranked {rank}{rank_suffix}:**\n"
                                f"{uni.get('general_fit_reasoning', 'No reasoning provided.')}"
                            )
                            
                            # --- ROW 1: HARD REQUIREMENTS ---
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.markdown("#### ✅ Hard Requirements")
                                elig_data = {
                                    "Min GPA": reqs.get("min_gpa"),
                                    "English Only is Possible?": "✅ Yes" if reqs.get("english_only_possible") else "⚠️ Limited",
                                    "Erasmus Scholarship?": "✅ Yes" if reqs.get("erasmus_available") else "❌ No",
                                    "English Level Requirement": reqs.get("english_test_level", "N/A"),
                                    "Min Semesters": reqs.get("min_semesters_completed")
                                }
                                st.dataframe(pd.DataFrame([elig_data]), hide_index=True, use_container_width=True)                                
                            
                            with col2:
                                st.markdown("#### 📅 Calendar")
                                fall = reqs.get("fall_semester", {})
                                spring = reqs.get("spring_semester", {})

                                # Format the Fall dates
                                fall_start = format_exchange_date(fall.get('start_month'), fall.get('start_day'))
                                fall_end = format_exchange_date(fall.get('end_month'), fall.get('end_day'))
                                
                                # Format the Spring dates
                                spring_start = format_exchange_date(spring.get('start_month'), spring.get('start_day'))
                                spring_end = format_exchange_date(spring.get('spring_end_month') or spring.get('end_month'), spring.get('end_day'))

                                st.write(f"**Fall:** {fall_start} — {fall_end}")
                                st.write(f"**Spring:** {spring_start} — {spring_end}")

                            st.divider()

                            # --- ROW 2: DETAILED LOGISTICS ---
                            st.markdown("### 🏘️ Logistics & Student Experience")
                            l_col1, l_col2, l_col3 = st.columns(3)
                            
                            with l_col1:
                                st.subheader("📚 Academic")
                                st.write(f"**Credits Min:** {acad.get('min_credits_required', 'N/A')}")
                                st.write(f"**Credits Max:** {acad.get('max_credits_allowed', 'N/A')}")
                                st.write(f"**Languages:** {acad.get('instruction_languages', 'N/A')}")
                                with st.expander("Grading & Notes"):
                                    st.write(f"**Grading:** {acad.get('grading_system_summary', 'N/A')}")
                                    st.write(f"**Summary:** {acad.get('academic_summary_notes', 'N/A')}")

                            with l_col2:
                                st.subheader("🏠 Housing & Costs")
                                # Grouping Housing availability with its specific costs
                                st.write(f"**Dorm Available:** {'✅' if house.get('campus_housing_available') else '❌'}")
                                st.write(f"**Dorm Guaranteed:** {'✅' if house.get('campus_housing_guaranteed') else '❌'}")
                                st.write(f"**Housing Cost:** {house.get('estimated_housing_cost_per_month', 'N/A')} {house.get('currency', '')}")
                                st.write(f"**Living Cost:** {house.get('estimated_living_cost_per_month', 'N/A')} {house.get('currency', '')}")
                                
                                with st.expander("Housing & Cost Details"):
                                    st.write(f"**Housing Details:** {house.get('housing_details', 'N/A')}")
                                    st.write(f"**Summary Notes:** {house.get('logistics_summary_notes', 'N/A')}")

                            with l_col3:
                                st.subheader("🛂 Visa & Insurance")
                                # Grouping administrative/legal requirements
                                st.write(f"**Visa Sponsored:** {'✅' if house.get('university_sponsors_visa') else '❌'}")
                                st.write(f"**Processing Time:** {house.get('estimated_visa_processing_weeks', 'N/A')} weeks")
                                st.write(f"**Insurance Mandatory:** {'✅' if house.get('mandatory_insurance_required') else '❌'}")
                                
                                with st.expander("Visa & Insurance Details"):
                                    st.write(f"**Summary Notes:** {house.get('medical_and_insurance_details', 'N/A')}")
                            
                            # --- ROW 3: INTEGRATION ---
                            st.divider()
                            i_col1, i_col2 = st.columns(2)
                            with i_col1:
                                st.subheader("🤝 Support & Integration")
                                st.write(f"**Buddy Program:** {'✅' if integ.get('buddy_program_available') else '❌'}")
                                st.write(f"**Orientation Program:** {'✅' if integ.get('orientation_program_provided') else '❌'}")
                                st.write(f"**Is Orientation Mandatory:** {'✅' if integ.get('orientation_is_mandatory') else '❌'}")
                            
                            with i_col2:
                                st.subheader("🗣️ Language Courses")
                                st.write(f"**Available Pre-Semester:** {'✅' if integ.get('pre_semester_language_course_available') else '❌'}")
                                with st.expander("Integration & Language Notes"):
                                    st.write(f"**Language Course Details:** {integ.get('language_course_details', 'N/A')}")
                                    st.write(f"**Integration Summary:** {integ.get('integration_summary_notes', 'N/A')}")

                # --- EXECUTION TRACE ---
                st.divider()
                st.subheader("🛠 Execution Trace")
                for step in agent_steps:
                    # Check if the step has a university name in its prompt data
                    uni_target = step.get("prompt", {}).get("target_university", "Global")
                    with st.expander(f"Module: {step.get('module', 'Unknown')} | University: {uni_target}"):
                        st.write("**Prompt Preview:**")
                        st.json(step.get("prompt", {}))
                        st.write("**Response:**")
                        st.json(step.get("response", {}))

            elif data.get("status") == "error":
                st.error(f"Agent Error: {data.get('error')}")
        except Exception as e:
             st.error(f"System Error: {e}")
else:
    # This shows up BEFORE they press the button
    st.title("University Exchange Analyzer")
    st.info("👈 Fill out your profile in the sidebar and click 'Run Analysis' to get started!")
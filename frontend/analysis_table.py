import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

st.set_page_config(page_title="Exchange Agent Pro", layout="wide")
st.title("🎓 University Selection Dashboard")

# --- Sidebar Input ---
with st.sidebar:
    st.header("Search Settings")
    default_prompt = '{"academic_profile": {"gpa": 3.5, "major": "Computer Science"}, "preferences": {"vibe": "traditional campus"}}'
    user_json = st.text_area("User Profile (JSON):", value=default_prompt, height=200)
    run_button = st.button("🚀 Run Analysis", use_container_width=True)

# --- Main Logic ---
if run_button:
    with st.spinner("Consulting the experts..."):
        try:
            res = requests.post(f"{API_URL}/execute", json={"prompt": user_json})
            data = res.json()
            
            if data.get("status") == "ok":
                # Using your new nested structure from analysis_results
                universities = data.get("raw_analysis_results", []) 
                
                st.success(f"Analysis complete. Found {len(universities)} top matches.")

                if universities:
                    uni_names = [u.get("university_name", "Unknown") for u in universities]
                    tabs = st.tabs(uni_names)

                    for i, tab in enumerate(tabs):
                        uni = universities[i]
                        
                        # Accessing our new Buckets
                        reqs = uni.get("requirements", {})
                        logistics = uni.get("logistics", {})
                        
                        with tab:
                            col1, col2 = st.columns([2, 1])

                            with col1:
                                st.markdown(f"### 🎯 Why {uni['university_name']} fits you")
                                st.info(uni.get("general_fit_reasoning", "No specific reasoning generated."))
                                
                                # Eligibility Table (Pulled from 'requirements' bucket)
                                st.markdown("#### ✅ Hard Requirements")
                                elig_data = {
                                    "Min GPA": reqs.get("min_gpa"),
                                    "Erasmus?": "✅ Yes" if reqs.get("erasmus_available") else "❌ No",
                                    "MSc Allowed?": "✅ Yes" if reqs.get("msc_allowed") else "❌ No",
                                    "Min Semesters": reqs.get("min_semesters_completed"),
                                    "English Req": f"{reqs.get('english_test_level', 'N/A')} ({', '.join(reqs.get('english_test_type', []))})"
                                }
                                st.table(pd.DataFrame([elig_data]))

                            with col2:
                                # Calendar (Pulled from 'requirements' bucket)
                                st.markdown("#### 📅 Academic Calendar")
                                fall = reqs.get("fall_semester", {})
                                spring = reqs.get("spring_semester", {})
                                
                                st.write("**Fall Semester**")
                                st.caption(f"{fall.get('start_month')}/{fall.get('start_day')} to {fall.get('end_month')}/{fall.get('end_day')}")
                                
                                st.write("**Spring Semester**")
                                st.caption(f"{spring.get('start_month')}/{spring.get('start_day')} to {spring.get('end_month')}/{spring.get('end_day')}")
                                
                                if reqs.get("restricted_majors"):
                                    st.warning(f"**Restricted:** {', '.join(reqs.get('restricted_majors'))}")

                            st.divider()

                            # --- Logistics Tables (Pulled from 'logistics' bucket) ---
                            st.markdown("### 🏘️ Logistics & Student Experience")
                            
                            l_col1, l_col2, l_col3 = st.columns(3)

                            with l_col1:
                                st.subheader("📚 Academic")
                                ac = logistics.get("academic", {})
                                st.write(f"**Languages:** {ac.get('instruction_languages')}")
                                st.write(f"**Credits:** {ac.get('min_credits_required')} - {ac.get('max_credits_allowed')}")
                                with st.expander("Academic Notes"):
                                    st.write(ac.get("academic_summary_notes"))

                            with l_col2:
                                st.subheader("🏠 Housing & Costs")
                                hc = logistics.get("housing_and_logistics", {})
                                st.write(f"**Housing Guaranteed:** {'✅' if hc.get('campus_housing_guaranteed') else '❌'}")
                                st.write(f"**Living Cost:** {hc.get('estimated_living_cost_per_month')} {hc.get('currency')}")
                                with st.expander("Visa & Insurance"):
                                    st.write(f"Visa Weeks: {hc.get('estimated_visa_processing_weeks')}")
                                    st.write(hc.get("medical_and_insurance_details"))

                            with l_col3:
                                st.subheader("🤝 Integration")
                                intg = logistics.get("student_integration", {})
                                st.write(f"**Buddy Program:** {'✅' if intg.get('buddy_program_available') else '❌'}")
                                st.write(f"**Language Course:** {'✅' if intg.get('pre_semester_language_course_available') else '❌'}")
                                with st.expander("Orientation Details"):
                                    st.write(f"Mandatory: {intg.get('orientation_is_mandatory')}")
                                    st.write(intg.get("integration_summary_notes"))

                # --- Execution Trace ---
                st.divider()
                with st.expander("🔍 Internal AI Logic (Trace)"):
                    for step in data.get("steps", []):
                        st.write(f"**Module:** {step['module']}")
                        st.json(step.get("response"))

            else:
                st.error(f"Agent Error: {data.get('error')}")
        except Exception as e:
            st.error(f"System Error: {e}")
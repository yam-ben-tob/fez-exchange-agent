// Tab switching logic
function showTab(index) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${index}`).classList.add('active');
    document.getElementById(`tab-btn-${index}`).classList.add('active');
}

// Auto-load on startup
window.onload = function() {
    loadProfile();
};

// 1. Fills the HTML boxes with data from the chosen profile
function loadProfile() {
    const selector = document.getElementById('profileSelect');
    const profileData = studentProfiles[selector.value]; 

    // Academic
    document.getElementById('f_gpa').value = profileData.academic_profile.gpa || '';
    document.getElementById('f_major').value = profileData.academic_profile.major || '';
    document.getElementById('f_level').value = profileData.academic_profile.study_level || 'bsc';
    document.getElementById('f_semesters').value = profileData.academic_profile.semesters_completed || '';

    // Language
    document.getElementById('f_noneng').value = (profileData.language_profile.non_english_languages || []).join(', ');
    document.getElementById('f_engtype').value = (profileData.language_profile.english_test_type || []).join(', ');
    document.getElementById('f_englvl').value = profileData.language_profile.english_test_level || '';

    // Availability
    document.getElementById('f_smonth').value = profileData.availability.start_month || '';
    document.getElementById('f_sday').value = profileData.availability.start_day || '';
    document.getElementById('f_emonth').value = profileData.availability.end_month || '';
    document.getElementById('f_eday').value = profileData.availability.end_day || '';

    // Preferences
    document.getElementById('f_erasmus').checked = profileData.preferences.must_be_erasmus || false;
    document.getElementById('f_vibe').value = profileData.preferences.free_language_preferences || '';

    // Immediately generate the JSON block at the bottom
    updateJson();
}

// 2. Reads the HTML boxes and builds the live JSON text
function updateJson() {
    // Helper to safely parse numbers
    const getNum = (id) => {
        const val = document.getElementById(id).value;
        return val ? Number(val) : null;
    };
    // Helper to cleanly split comma-separated strings into arrays
    const getArray = (id) => {
        const val = document.getElementById(id).value;
        return val ? val.split(',').map(s => s.trim()).filter(Boolean) : [];
    };

    const currentProfile = {
        academic_profile: {
            gpa: getNum('f_gpa'),
            major: document.getElementById('f_major').value,
            study_level: document.getElementById('f_level').value,
            semesters_completed: getNum('f_semesters')
        },
        language_profile: {
            non_english_languages: getArray('f_noneng'),
            english_test_type: getArray('f_engtype'),
            english_test_level: document.getElementById('f_englvl').value
        },
        availability: {
            start_month: getNum('f_smonth'),
            start_day: getNum('f_sday'),
            end_month: getNum('f_emonth'),
            end_day: getNum('f_eday')
        },
        preferences: {
            must_be_erasmus: document.getElementById('f_erasmus').checked,
            free_language_preferences: document.getElementById('f_vibe').value
        }
    };

    // Update the read-only textarea at the bottom
    document.getElementById('jsonOutput').value = JSON.stringify(currentProfile, null, 4);
}

// Helper to convert month number (1-12) to Month Name
function getMonthName(monthNumber) {
    if (!monthNumber) return 'N/A';
    const months = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"];
    // Arrays start at 0, so month 9 (Sept) is at index 8
    return months[monthNumber - 1] || 'N/A';
}

// Helper to format Month and Day safely
function formatDate(monthNum, dayNum) {
    if (!monthNum) return 'N/A';
    const month = getMonthName(monthNum);
    return dayNum ? `${month} ${dayNum}` : month;
}

// Navigation Functions for Virtual Pages
function showTracePage() {
    document.getElementById('mainView').style.display = 'none';
    document.getElementById('traceView').style.display = 'block';
    window.scrollTo(0, 0); // Scroll to top of the new page
}

function showArchPage() {
    document.getElementById('mainView').style.display = 'none';
    document.getElementById('traceView').style.display = 'none'; // Ensure trace is hidden
    document.getElementById('archView').style.display = 'block'; // Show arch
    window.scrollTo(0, 0);
}

function showMainPage() {
    document.getElementById('traceView').style.display = 'none';
    document.getElementById('archView').style.display = 'none';
    document.getElementById('mainView').style.display = 'block';
    window.scrollTo(0, 0);
}

// Main Execution
async function runAgent() {
    const promptText = document.getElementById('jsonOutput').value;
    // const promptText = document.getElementById('promptInput').value;
    const btn = document.getElementById('runBtn');
    const container = document.getElementById('uiContainer');

    if (!promptText) return alert("Please enter a profile.");

    btn.disabled = true;
    btn.innerText = "Analyzing universities...";
    container.innerHTML = "<p><i>Agent is running... this may take a moment.</i></p>";

    try {
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: promptText })
        });

        const data = await response.json();

        if (data.status === "error") {
            container.innerHTML = `<div style="color: red; padding: 10px; border: 1px solid red;">Agent Error: ${data.error}</div>`;
            return;
        }

        let universities = [];
        try {
            universities = JSON.parse(data.response || "[]");
        } catch (e) {
            container.innerHTML = `<div style="color: orange;">Warning: Could not parse university data. Raw response: ${data.response}</div>`;
        }

        let html = '';

        if (universities.length > 0) {
            html += `<div class="success-banner">Analysis Complete! Found ${universities.length} matches.</div>`;
            
            // Tabs Header
            html += `<div class="tabs">`;
            universities.forEach((uni, index) => {
                html += `<button id="tab-btn-${index}" class="tab-btn ${index === 0 ? 'active' : ''}" onclick="showTab(${index})">${uni.university_name || 'Unknown'}</button>`;
            });
            html += `</div>`;

            // Tabs Content
            universities.forEach((uni, i) => {
                const reqs = uni.requirements || {};
                const logistics = uni.logistics || {};
                const acad = logistics.academic || {};
                const house = logistics.housing_and_logistics || {};
                const integ = logistics.student_integration || {};

                const rank = i + 1;
                const rankSuffix = rank === 1 ? "st" : rank === 2 ? "nd" : rank === 3 ? "rd" : "th";

                html += `<div id="tab-${i}" class="tab-content ${i === 0 ? 'active' : ''}">`;
                
                html += `
                <div class="info-banner">
                    <strong>Country:</strong> ${reqs.country || 'N/A'}<br><br>
                    <strong>Why this was chosen for you and ranked ${rank}${rankSuffix}:</strong><br>
                    ${uni.general_fit_reasoning || 'No reasoning provided.'}
                </div>`;

                html += `
                <div class="row">
                    <div class="col col-2">
                        <h3>✅ Hard Requirements</h3>
                        <table>
                            <tr><th>Min GPA</th><th>English Only?</th><th>Erasmus?</th><th>English Level</th><th>Min Semesters</th></tr>
                            <tr>
                                <td>${reqs.min_gpa || 'N/A'}</td>
                                <td>${reqs.english_only_possible ? '✅ Yes' : '⚠️ Limited'}</td>
                                <td>${reqs.erasmus_available ? '✅ Yes' : '❌ No'}</td>
                                <td>${reqs.english_test_level || 'N/A'}</td>
                                <td>${reqs.min_semesters_completed || 'N/A'}</td>
                            </tr>
                        </table>
                    </div>
                    <div class="col">
                        <h3>📅 Calendar</h3>
                        <strong>Fall:</strong> ${formatDate(reqs.fall_semester?.start_month, reqs.fall_semester?.start_day)} - ${formatDate(reqs.fall_semester?.end_month, reqs.fall_semester?.end_day)}<br>
                        <strong>Spring:</strong> ${formatDate(reqs.spring_semester?.start_month, reqs.spring_semester?.start_day)} - ${formatDate(reqs.spring_semester?.end_month, reqs.spring_semester?.end_day)}
                    </div>
                </div><hr>`;

                html += `
                <h3>🏘️ Logistics & Student Experience</h3>
                <div class="row">
                    <div class="col">
                        <h4>📚 Academic</h4>
                        <strong>Credits Min:</strong> ${acad.min_credits_required || 'N/A'}<br>
                        <strong>Credits Max:</strong> ${acad.max_credits_allowed || 'N/A'}<br>
                        <strong>Languages:</strong> ${acad.instruction_languages || 'N/A'}<br>
                        <details><summary>Grading & Notes</summary><div class="details-content">
                            <strong>Grading:</strong> ${acad.grading_system_summary || 'N/A'}<br>
                            <strong>Summary:</strong> ${acad.academic_summary_notes || 'N/A'}
                        </div></details>
                    </div>
                    <div class="col">
                        <h4>🏠 Housing & Costs</h4>
                        <strong>Dorm Available:</strong> ${house.campus_housing_available ? '✅' : '❌'}<br>
                        <strong>Cost:</strong> ${house.estimated_housing_cost_per_month || 'N/A'} ${house.currency || ''}<br>
                        <details><summary>Housing Details</summary><div class="details-content">
                            ${house.housing_details || 'N/A'}
                        </div></details>
                    </div>
                    <div class="col">
                        <h4>🛂 Visa & Insurance</h4>
                        <strong>Visa Sponsored:</strong> ${house.university_sponsors_visa ? '✅' : '❌'}<br>
                        <strong>Processing:</strong> ${house.estimated_visa_processing_weeks || 'N/A'} weeks<br>
                        <details><summary>Visa Notes</summary><div class="details-content">
                            ${house.medical_and_insurance_details || 'N/A'}
                        </div></details>
                    </div>
                </div><hr>`;

                html += `
                <div class="row">
                    <div class="col">
                        <h4>🤝 Support & Integration</h4>
                        <strong>Buddy Program:</strong> ${integ.buddy_program_available ? '✅' : '❌'}<br>
                        <strong>Orientation:</strong> ${integ.orientation_program_provided ? '✅' : '❌'}
                    </div>
                    <div class="col">
                        <h4>🗣️ Language Courses</h4>
                        <strong>Pre-Semester:</strong> ${integ.pre_semester_language_course_available ? '✅' : '❌'}<br>
                        <details><summary>Integration Notes</summary><div class="details-content">
                            ${integ.integration_summary_notes || 'N/A'}
                        </div></details>
                    </div>
                </div>`;

                html += `</div>`; 
            });
        }

        // Add the "Go to Trace Page" button at the very bottom of the MAIN results
            html += `<hr><button onclick="showTracePage()" style="background-color: #333; width: 100%; padding: 15px; font-size: 1.1em; margin-top: 10px;">🔍 View Full Execution Trace ➔</button>`;
        

        /// --- GENERATE TRACE PAGE CONTENT SEPARATELY ---
        let traceHtml = `<div style="display: flex; flex-direction: column; gap: 10px;">`;
        const allSteps = data.steps || [];
        
        // 🚨 BULLETPROOF MEMORY FILTER: 
        // Search the Agent's massive memory backwards to grab only the most recent steps
        const lastFilter = allSteps.slice().reverse().find(s => s.module === 'Filter');
        const lastRanker = allSteps.slice().reverse().find(s => s.module === 'Ranker');
        
        // Grab strictly the last 5 Analyzers
        const lastAnalyzers = allSteps.filter(s => s.module === 'Analyzer').slice(-5);
        
        // Combine them into a perfect 7-step array
        const finalSteps = [];
        if (lastFilter) finalSteps.push(lastFilter);
        if (lastRanker) finalSteps.push(lastRanker);
        finalSteps.push(...lastAnalyzers);

        // Now loop over our perfectly clean finalSteps array!
        finalSteps.forEach((step, index) => {
            const moduleName = step.module || 'Unknown';
            const targetUni = step.prompt?.target_university || 'Global';
            const stepNumber = index + 1;
            
            // 1. Determine the descriptive text based on the module name
            let stepDescription = "";
            const modLower = moduleName.toLowerCase();
            
            if (modLower.includes('filter')) {
                stepDescription = "Filters eligible universities based on the user's hard constraints (GPA, major, dates) by querying a SQL database of requirements, which was pre-compiled by an AI agent analyzing official factsheets.";
            } else if (modLower.includes('ranker')) {
                stepDescription = "Uses LLM reasoning to evaluate and score each eligible university against the user's free-text preferences, generating custom scores across multiple categories (Academic, Lifestyle, Social, Location, Financial, and Community fit).";
            } else if (modLower.includes('analyzer')) {
                stepDescription = "Uses Retrieval-Augmented Generation (RAG) over official university factsheets to extract specific, comparable logistical details (housing, visa, academics) for the top-ranked matches.";
            }

            // 2. Build the HTML with the new description block injected
            traceHtml += `
            <details style="border-left: 4px solid #4f46e5; overflow: hidden; margin-bottom: 10px;">                <summary style="background-color: #f8f9fa; padding: 12px 15px; font-size: 1.05em; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;">
                    <strong>Step ${stepNumber}:</strong> ${moduleName} <span style="color: #888; font-weight: normal; margin-left: 10px;">(Target: ${targetUni})</span>
                </summary>
                
                <div class="details-content" style="padding: 20px; background-color: #ffffff; border: 1px solid #ddd; border-top: none;">
                    
                    ${stepDescription ? `
                    <div style="background-color: #fff9e6; color: #856404; padding: 10px 15px; border-left: 3px solid #ffeeba; margin-bottom: 20px; font-size: 0.95em; border-radius: 0 4px 4px 0;">
                        💡 <strong>What happens here:</strong> ${stepDescription}
                    </div>
                    ` : ''}

                    <div style="margin-bottom: 15px;">
                        <span style="display: inline-block; background: #e2eef9; color: #004085; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-bottom: 8px;">📤 Prompt Payload</span>
                        <pre style="margin: 0; max-height: 400px; overflow-y: auto; font-size: 13px;">${JSON.stringify(step.prompt, null, 2)}</pre>
                    </div>
                    
                    <div>
                        <span style="display: inline-block; background: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-bottom: 8px;">📥 Agent Response</span>
                        <pre style="margin: 0; max-height: 400px; overflow-y: auto; font-size: 13px;">${JSON.stringify(step.response, null, 2)}</pre>
                    </div>
                </div>
            </details>`;
        });

        // Inject the HTML into their respective containers
        container.innerHTML = html; // Goes to the Main Page
        document.getElementById('traceContainer').innerHTML = traceHtml; // Goes to the Hidden Trace Page

    } catch (error) {
        container.innerHTML = `<div style="color: red;">System Error: ${error.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerText = "🚀 Run Analysis";
    }

}
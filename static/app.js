// Tab switching logic
function showTab(index) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${index}`).classList.add('active');
    document.getElementById(`tab-btn-${index}`).classList.add('active');
}

// Load profile from the dropdown
function loadProfile() {
    const selector = document.getElementById('profileSelect');
    const selectedKey = selector.value;
    const profileData = studentProfiles[selectedKey]; 
    document.getElementById('promptInput').value = JSON.stringify(profileData, null, 4);
}

// Auto-load on startup
window.onload = function() {
    loadProfile();
};

// Main Execution
async function runAgent() {
    const promptText = document.getElementById('promptInput').value;
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
                        <strong>Fall:</strong> ${reqs.fall_semester?.start_month || ''} - ${reqs.fall_semester?.end_month || ''}<br>
                        <strong>Spring:</strong> ${reqs.spring_semester?.start_month || ''} - ${reqs.spring_semester?.end_month || ''}
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

        html += `<hr><h2>🛠 Execution Trace</h2>`;
        const steps = data.steps || [];
        steps.forEach((step) => {
            const moduleName = step.module || 'Unknown';
            const targetUni = step.prompt?.target_university || 'Global';
            html += `
            <details>
                <summary>Module: ${moduleName} | University: ${targetUni}</summary>
                <div class="details-content">
                    <strong>Prompt Preview:</strong>
                    <pre>${JSON.stringify(step.prompt, null, 2)}</pre>
                    <strong>Response:</strong>
                    <pre>${JSON.stringify(step.response, null, 2)}</pre>
                </div>
            </details>`;
        });

        container.innerHTML = html;

    } catch (error) {
        container.innerHTML = `<div style="color: red;">System Error: ${error.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerText = "🚀 Run Analysis";
    }
}
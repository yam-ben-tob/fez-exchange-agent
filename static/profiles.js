const studentProfiles = {
    "default": {
        "academic_profile": { "gpa": 3.2, "major": "Computer Science", "study_level": "bsc", "semesters_completed": 4 },
        "language_profile": { "non_english_languages": ["Spanish"], "english_test_type": ["TOEFL", "IELTS"], "english_test_level": "B2" },
        "availability": { "start_month": 8, "start_day": 15, "end_month": 12, "end_day": 31 },
        "preferences": { "must_be_erasmus": true, "free_language_preferences": "I want a traditional, unified campus where it's easy to make friends...\n\nI'd love a place with cool museums... My absolute max budget is $9,000 for the semester." }
    },
    "high_gpa": {
        "academic_profile": { "gpa": 4.0, "major": "Physics", "study_level": "msc", "semesters_completed": 6 },
        "language_profile": { "non_english_languages": [], "english_test_type": ["TOEFL"], "english_test_level": "C1" },
        "availability": { "start_month": 2, "start_day": 1, "end_month": 6, "end_day": 30 },
        "preferences": { "must_be_erasmus": false, "free_language_preferences": "quiet campus, research focus" }
    },
    "low_gpa": {
        "academic_profile": { "gpa": 2.0, "major": "Business", "study_level": "bsc", "semesters_completed": 2 },
        "language_profile": { "non_english_languages": ["French"], "english_test_type": ["IELTS"], "english_test_level": "B1" },
        "availability": { "start_month": 9, "start_day": 1, "end_month": 1, "end_day": 15 },
        "preferences": { "must_be_erasmus": true, "free_language_preferences": "urban, business hub" }
    },
    "european_master": {
        "academic_profile": { "gpa": 3.8, "major": "Medicine", "study_level": "msc", "semesters_completed": 6 },
        "language_profile": { "non_english_languages": ["French"], "english_test_type": ["IELTS"], "english_test_level": "C1" },
        "availability": { "start_month": 2, "start_day": 1, "end_month": 7, "end_day": 15 },
        "preferences": { "must_be_erasmus": true, "free_language_preferences": "" }
    },
    "english_only_freshman": {
        "academic_profile": { "gpa": 2.5, "major": "Business", "study_level": "bsc", "semesters_completed": 1 },
        "language_profile": { "non_english_languages": [], "english_test_type": ["Duolingo"], "english_test_level": "B1" },
        "availability": { "start_month": null, "start_day": null, "end_month": null, "end_day": null },
        "preferences": { "must_be_erasmus": false, "free_language_preferences": "" }
    }
};
"""
Mock API responses for QA: jobs, resumes, and preps.

Used with Playwright page.route() so the UI works without a live backend.
Structures are generic enough to support common dashboard/list UIs.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

JOBS_RESPONSE = {
    "data": [
        {
            "id": "job-mock-1",
            "title": "Senior Software Engineer",
            "company": "Tech Solutions Inc",
            "companyName": "Tech Solutions Inc",
            "location": "San Francisco, CA",
            "skills": ["Python", "React", "AWS", "SQL"],
            "fitScore": 92,
            "description": "We are looking for a Senior Software Engineer with strong Python and React experience.",
            "postedAt": "2025-02-15T00:00:00Z",
        },
        {
            "id": "job-mock-2",
            "title": "AI Engineer",
            "company": "Data Corp Ltd",
            "companyName": "Data Corp Ltd",
            "location": "Remote",
            "skills": ["Python", "NLP", "Machine Learning", "Node"],
            "fitScore": 88,
            "description": "AI Engineer role for NLP and ML projects.",
            "postedAt": "2025-02-10T00:00:00Z",
        },
        {
            "id": "job-mock-3",
            "title": "Full Stack Developer",
            "company": "StartupXYZ Technologies",
            "companyName": "StartupXYZ Technologies",
            "location": "New York, NY",
            "skills": ["Java", "React", "Node", "SQL"],
            "fitScore": 65,
            "description": "Full stack role with Java and React.",
            "postedAt": "2025-02-01T00:00:00Z",
        },
    ],
    "total": 3,
    "totalJobs": 3,
    "bestFitCount": 2,
    "leastFitCount": 1,
}

# Alternative: list-only shape (some APIs return array directly)
JOBS_LIST_RESPONSE = JOBS_RESPONSE["data"]

# ---------------------------------------------------------------------------
# Resumes
# ---------------------------------------------------------------------------

RESUMES_RESPONSE = {
    "data": [
        {
            "id": "resume-mock-1",
            "targetRole": "AI Engineer",
            "title": "Resume - AI Engineer",
            "fileName": "resume_ai_engineer.pdf",
            "uploadedAt": "2025-02-20T00:00:00Z",
        },
        {
            "id": "resume-mock-2",
            "targetRole": "Data Scientist",
            "title": "Resume - Data Scientist",
            "fileName": "resume_data_scientist.pdf",
            "uploadedAt": "2025-02-18T00:00:00Z",
        },
    ],
    "total": 2,
}

RESUMES_LIST_RESPONSE = RESUMES_RESPONSE["data"]

# ---------------------------------------------------------------------------
# Preps (Job Descriptions / JDs)
# ---------------------------------------------------------------------------

PREPS_RESPONSE = {
    "data": [
        {
            "id": "prep-mock-1",
            "role": "AI Engineer",
            "title": "AI Engineer",
            "skills": "Python, NLP, Machine Learning",
            "experience": "2 years",
            "additionalDetails": "Test automation JD",
            "createdAt": "2025-02-20T00:00:00Z",
        },
        {
            "id": "prep-mock-2",
            "role": "Senior Backend Developer",
            "title": "Senior Backend Developer",
            "skills": "Java, Spring, SQL",
            "experience": "5 years",
            "additionalDetails": "",
            "createdAt": "2025-02-19T00:00:00Z",
        },
    ],
    "total": 2,
}

PREPS_LIST_RESPONSE = PREPS_RESPONSE["data"]

# ---------------------------------------------------------------------------
# User / profile (for dashboard and auth context)
# ---------------------------------------------------------------------------

USER_RESPONSE = {
    "id": "user-mock-1",
    "email": "qa@example.com",
    "name": "QA User",
    "title": "Software Engineer",
    "phone": "+1 555-000-0000",
    "location": "San Francisco, CA",
    "about": "QA test profile for mock environment.",
}

# Dashboard stats (if app fetches stats separately)
DASHBOARD_STATS_RESPONSE = {
    "totalActivities": 10,
    "totalJobs": 3,
    "totalResumes": 2,
    "totalPreps": 2,
}

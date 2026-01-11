import os
import sys

# Ensure backend modules are importable when running pytest from repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from matching.job_filter_production import hard_filter_job


def test_backend_engineer_accepts_backend_titles_without_description():
    job = {
        "title": "Software Engineer - Backend",
        "description": "",  # LinkedIn recommendations often don't include full descriptions
    }
    passed, reason = hard_filter_job(job, role_key="backend_engineer")
    assert passed, reason


def test_backend_engineer_rejects_ai_titles():
    job = {
        "title": "Generative AI Engineer",
        "description": "",  # missing description should still rely on title guardrails
    }
    passed, reason = hard_filter_job(job, role_key="backend_engineer")
    assert not passed
    assert "Title doesn't match" in reason

import sys
from pathlib import Path

# Ensure we can import backend modules without installing as a package
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.routes.ats_routes import calculate_ats_score  # noqa: E402


def test_ats_score_with_sample_text_resume():
    """Regression test: ATS scoring works end-to-end with a known-good resume text."""
    resume_path = PROJECT_ROOT / "data" / "resumes" / "sample_resume.txt"
    assert resume_path.exists(), "sample resume fixture missing"

    resume_text = resume_path.read_text(encoding="utf-8")
    job_description = (
        "We are hiring a Backend Engineer to build REST APIs using FastAPI, "
        "PostgreSQL, Docker, and AWS. Experience with Redis and Kubernetes is a plus."
    )

    payload = calculate_ats_score(resume_text, job_description)
    assert "match_score" in payload
    assert 0 <= payload["match_score"] <= 100
    assert "missing_keywords" in payload
    assert "matched_keywords" in payload

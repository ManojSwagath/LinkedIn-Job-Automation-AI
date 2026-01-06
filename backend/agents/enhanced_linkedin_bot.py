import os
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedLinkedInBot:
    """AI-powered LinkedIn job automation bot."""
    
    def __init__(self):
        """Initialize the bot with API credentials."""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"
        logger.info("EnhancedLinkedInBot initialized successfully")
    
    def generate_job_profile(self, job_description: str) -> Dict[str, Any]:
        """Generate a job profile analysis from a job description."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze this job description and extract: title, required_skills, experience_level, salary_range, benefits. Job: {job_description}"
                    }
                ]
            )
            logger.info("Job profile generated successfully")
            return {"analysis": message.content[0].text}
        except Exception as e:
            logger.error(f"Error generating job profile: {e}")
            return {"error": str(e)}
    
    def generate_cover_letter(self, job_title: str, company: str, user_experience: str) -> str:
        """Generate a personalized cover letter."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"Write a professional cover letter for {job_title} at {company}. My experience: {user_experience}"
                    }
                ]
            )
            logger.info("Cover letter generated successfully")
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return f"Error: {str(e)}"
    
    def optimize_resume(self, resume_text: str, job_description: str) -> str:
        """Optimize resume for a specific job."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": f"Optimize this resume for the job description. Resume: {resume_text}\n\nJob Description: {job_description}"
                    }
                ]
            )
            logger.info("Resume optimized successfully")
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error optimizing resume: {e}")
            return f"Error: {str(e)}"
    
    def generate_interview_prep(self, job_description: str, company: str) -> Dict[str, Any]:
        """Generate interview preparation materials."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate interview preparation materials for a position at {company}. Include: common questions, company research points, and tips. Job Description: {job_description}"
                    }
                ]
            )
            logger.info("Interview prep materials generated successfully")
            return {"prep_materials": message.content[0].text}
        except Exception as e:
            logger.error(f"Error generating interview prep: {e}")
            return {"error": str(e)}
    
    def analyze_job_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Analyze how well a resume matches a job description."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze match between resume and job. Provide match score (0-100), strengths, gaps, and recommendations. Resume: {resume_text}\n\nJob: {job_description}"
                    }
                ]
            )
            logger.info("Job match analysis completed successfully")
            return {"match_analysis": message.content[0].text}
        except Exception as e:
            logger.error(f"Error analyzing job match: {e}")
            return {"error": str(e)}


def main():
    """Main entry point for demonstration."""
    try:
        bot = EnhancedLinkedInBot()
        logger.info("Enhanced LinkedIn Bot initialized and ready")
        
        # Example usage
        sample_job = "Senior Python Developer with 5+ years experience in AI/ML"
        result = bot.generate_job_profile(sample_job)
        logger.info(f"Sample result: {result}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()
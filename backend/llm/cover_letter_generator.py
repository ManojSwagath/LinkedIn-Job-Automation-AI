"""
Advanced Cover Letter Generator
Uses GitHub API (GPT-4o) with Qdrant vector database for context-aware cover letters
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class CoverLetterGenerator:
    """Generate tailored cover letters using GPT-4o via GitHub Models API"""
    
    def __init__(self):
        """Initialize cover letter generator with GitHub API"""
        self.github_api_key = os.getenv('GITHUB_API_KEY', '')
        self.use_github_api = bool(self.github_api_key and not self.github_api_key.startswith('your_'))
        
        if self.use_github_api:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=self.github_api_key,
                )
                print("✅ Cover letter generator initialized with GPT-4o")
            except ImportError:
                print("⚠️  OpenAI SDK not installed. Run: pip install openai")
                self.use_github_api = False
        else:
            print("⚠️  GitHub API key not configured - cover letters will use fallback")
    
    def generate_cover_letter(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        resume_text: str,
        company_context: Optional[Dict] = None,
        max_length: int = 500
    ) -> str:
        """
        Generate tailored cover letter using GPT-4o
        
        Args:
            job_title: Position title
            company_name: Company name
            job_description: Job description text
            resume_text: Candidate's resume text
            company_context: Additional company information from Qdrant (optional)
            max_length: Maximum character length
            
        Returns:
            str: Generated cover letter
        """
        if not self.use_github_api:
            return self._generate_fallback_cover_letter(job_title, company_name, resume_text)
        
        try:
            # Build context from company data
            company_info = ""
            if company_context:
                industry = company_context.get('industry', '')
                mission = company_context.get('mission', '')
                recent_news = company_context.get('recent_news', '')
                
                if industry:
                    company_info += f"\nCompany Industry: {industry}"
                if mission:
                    company_info += f"\nCompany Mission: {mission}"
                if recent_news:
                    company_info += f"\nRecent News: {recent_news}"
            
            # Construct prompt for GPT-4o
            prompt = f"""You are an expert career coach writing a cover letter for a job application.

JOB DETAILS:
Position: {job_title}
Company: {company_name}
{company_info}

JOB DESCRIPTION:
{job_description[:1500]}

CANDIDATE RESUME SUMMARY:
{resume_text[:1500]}

Write a professional, compelling cover letter that:
1. Opens with genuine enthusiasm for the specific role and company
2. Highlights 2-3 key qualifications from the resume that match job requirements
3. Shows knowledge of the company (use company context if provided)
4. Expresses eagerness to contribute and grow with the team
5. Closes with a call to action

Keep it concise (3-4 paragraphs, ~300 words). Use a professional yet conversational tone.
Do NOT include placeholders like [Your Name] or [Date]. Write in first person.
Do NOT include address blocks or signature lines.
"""
            
            # Call GPT-4o via GitHub Models
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert cover letter writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            cover_letter = response.choices[0].message.content.strip()
            
            # Limit length if needed
            if len(cover_letter) > max_length:
                # Trim to last complete sentence within limit
                cover_letter = cover_letter[:max_length]
                last_period = cover_letter.rfind('.')
                if last_period > max_length * 0.7:  # Only trim if we keep most of it
                    cover_letter = cover_letter[:last_period + 1]
            
            print(f"✅ Generated cover letter ({len(cover_letter)} chars) using GPT-4o")
            return cover_letter
            
        except Exception as e:
            print(f"⚠️  GPT-4o cover letter generation failed: {str(e)}")
            return self._generate_fallback_cover_letter(job_title, company_name, resume_text)
    
    def _generate_fallback_cover_letter(
        self,
        job_title: str,
        company_name: str,
        resume_text: str
    ) -> str:
        """
        Generate basic cover letter without AI (fallback)
        
        Args:
            job_title: Position title
            company_name: Company name
            resume_text: Candidate's resume text
            
        Returns:
            str: Simple cover letter template
        """
        # Extract key skills from resume (simple keyword matching)
        skills = []
        skill_keywords = ['python', 'java', 'javascript', 'react', 'aws', 'docker', 'sql', 
                         'machine learning', 'data analysis', 'project management', 'leadership']
        
        resume_lower = resume_text.lower()
        for skill in skill_keywords:
            if skill in resume_lower:
                skills.append(skill.title())
        
        skills_text = ", ".join(skills[:3]) if skills else "my technical and professional skills"
        
        cover_letter = f"""I am writing to express my strong interest in the {job_title} position at {company_name}.

With my background in {skills_text}, I am confident that I can make valuable contributions to your team. My experience aligns well with the requirements of this role, and I am excited about the opportunity to bring my expertise to {company_name}.

I am particularly drawn to this position because it offers the perfect blend of challenge and opportunity for professional growth. I am eager to contribute to your organization's success while continuing to develop my skills in a dynamic environment.

Thank you for considering my application. I look forward to the opportunity to discuss how my qualifications match your needs."""
        
        return cover_letter
    
    def generate_with_qdrant_context(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        resume_text: str,
        qdrant_helper
    ) -> str:
        """
        Generate cover letter enhanced with company data from Qdrant
        
        Args:
            job_title: Position title
            company_name: Company name
            job_description: Job description
            resume_text: Candidate's resume
            qdrant_helper: QdrantHelper instance for retrieving company data
            
        Returns:
            str: Enhanced cover letter with company context
        """
        # Retrieve company context from Qdrant
        company_context = None
        try:
            # Search for company information in Qdrant
            company_query = f"{company_name} company information mission values"
            results = qdrant_helper.search_similar_jobs(company_query, limit=3)
            
            if results:
                # Aggregate company information from results
                company_context = {
                    'industry': results[0].get('industry', ''),
                    'mission': results[0].get('mission', ''),
                    'recent_news': results[0].get('recent_news', ''),
                    'culture': results[0].get('culture', '')
                }
                print(f"✅ Retrieved company context from Qdrant for {company_name}")
        except Exception as e:
            print(f"⚠️  Could not retrieve company context: {str(e)}")
        
        # Generate cover letter with company context
        return self.generate_cover_letter(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            resume_text=resume_text,
            company_context=company_context
        )


# Singleton instance
_cover_letter_generator = None


def get_cover_letter_generator() -> CoverLetterGenerator:
    """Get singleton instance of cover letter generator"""
    global _cover_letter_generator
    if _cover_letter_generator is None:
        _cover_letter_generator = CoverLetterGenerator()
    return _cover_letter_generator

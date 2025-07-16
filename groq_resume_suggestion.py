"""
Groq-powered Resume Suggestion Module for Auto Applier

This module uses Groq API with Llama 4 Scout to generate intelligent
resume tailoring suggestions for IT Support job applications.

Author: MooncakeSG
Created: 2025-07-07
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from groq import Groq
except ImportError:
    Groq = None

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will rely on system environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqResumeSuggestionConfig:
    """Configuration for Groq-powered resume suggestions."""
    
    # Groq API settings
    MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
    MAX_TOKENS = 1500
    TEMPERATURE = 0.7
    
    # Tech job categories and their key focus areas
    TECH_JOB_CATEGORIES = {
        'software_developer': {
            'keywords': ['programming', 'coding', 'development', 'software', 'application', 'web', 'mobile', 'full-stack', 'frontend', 'backend'],
            'focus': 'software development, programming languages, frameworks, and development methodologies'
        },
        'data_scientist': {
            'keywords': ['data', 'analytics', 'machine learning', 'python', 'sql', 'statistics', 'modeling', 'visualization'],
            'focus': 'data analysis, machine learning, statistical modeling, and data visualization'
        },
        'devops': {
            'keywords': ['devops', 'ci/cd', 'docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'automation', 'infrastructure'],
            'focus': 'DevOps practices, cloud infrastructure, automation, and deployment pipelines'
        },
        'cybersecurity': {
            'keywords': ['security', 'cybersecurity', 'penetration', 'vulnerability', 'firewall', 'compliance', 'incident'],
            'focus': 'cybersecurity practices, threat detection, compliance, and security frameworks'
        },
        'it_support': {
            'keywords': ['help desk', 'troubleshooting', 'technical support', 'it support', 'hardware', 'software', 'networking'],
            'focus': 'IT support, troubleshooting, technical assistance, and system administration'
        },
        'product_manager': {
            'keywords': ['product', 'roadmap', 'stakeholder', 'agile', 'scrum', 'requirements', 'strategy'],
            'focus': 'product management, roadmap planning, stakeholder communication, and agile methodologies'
        },
        'qa_engineer': {
            'keywords': ['testing', 'qa', 'quality assurance', 'automation', 'selenium', 'bug', 'test cases'],
            'focus': 'quality assurance, test automation, bug tracking, and testing methodologies'
        },
        'ui_ux_designer': {
            'keywords': ['ui', 'ux', 'design', 'user experience', 'figma', 'sketch', 'prototyping', 'wireframes'],
            'focus': 'user interface design, user experience, prototyping, and design thinking'
        },
        'network_engineer': {
            'keywords': ['networking', 'cisco', 'router', 'switch', 'tcp/ip', 'vpn', 'firewall', 'lan', 'wan'],
            'focus': 'network infrastructure, routing protocols, security, and network optimization'
        },
        'cloud_engineer': {
            'keywords': ['cloud', 'aws', 'azure', 'gcp', 'serverless', 'microservices', 'containers', 'terraform'],
            'focus': 'cloud architecture, cloud services, infrastructure as code, and cloud security'
        }
    }
    
    # Prompt templates
    SYSTEM_PROMPT = """You are an expert tech recruiting consultant and ATS optimization specialist. 
    Your role is to analyze resumes against specific technology job postings and provide actionable, 
    practical suggestions for improving resume-job alignment across various tech roles.

    You specialize in:
    - Software Development (Frontend, Backend, Full-Stack)
    - Data Science & Analytics
    - DevOps & Cloud Engineering
    - Cybersecurity
    - IT Support & System Administration
    - Product Management
    - QA Engineering
    - UI/UX Design
    - Network Engineering
    - And other technology roles

    Focus on:
    - ATS keyword optimization for specific tech roles
    - Technical skills alignment and positioning
    - Experience presentation improvements
    - Industry-specific certifications and qualifications
    - Professional formatting suggestions
    - Bias-free language recommendations

    Provide specific, actionable advice that candidates can immediately implement to improve their 
    chances of passing ATS screening and impressing hiring managers in the tech industry."""
    
    USER_PROMPT_TEMPLATE = """
    **JOB POSTING ANALYSIS:**
    Job Title: {job_title}
    Company: {company}
    Job Category: {job_category}
    Job Description: {job_description}

    **CANDIDATE RESUME:**
    {resume_text}

    **REQUESTED ANALYSIS:**
    Please provide a comprehensive resume improvement analysis with these sections:

    1. **RESUME-JOB FIT SUMMARY** (2-3 sentences)
       - Overall alignment assessment for this {job_category} role
       - Key strengths for this specific tech position

    2. **MISSING ATS KEYWORDS/SKILLS** 
       - 5-8 specific technical keywords from job posting missing from resume
       - Prioritize {job_category} specific terms and technologies
       - Include relevant programming languages, tools, frameworks, or certifications

    3. **RESUME IMPROVEMENT SUGGESTIONS**
       - 4-6 specific, actionable recommendations
       - Focus on technical skills positioning and experience presentation
       - Include suggestions for highlighting relevant projects, achievements, or certifications
       - Recommend quantifiable metrics where applicable

    4. **PROFESSIONAL ADVICE**
       - 2-3 tips for better ATS compatibility in the tech industry
       - Any bias concerns in current resume language
       - Industry-specific formatting recommendations for {job_category} roles
       - Suggestions for technical skill organization and presentation

    Keep suggestions practical, specific, and immediately actionable for {job_category} roles in the tech industry.
    Focus on what hiring managers and ATS systems look for in this specific tech domain.
    """

class GroqResumeSuggestionGenerator:
    """
    Groq-powered resume suggestion generator for IT Support job applications.
    Uses Llama 4 Scout for intelligent resume optimization advice.
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[GroqResumeSuggestionConfig] = None):
        """
        Initialize the Groq resume suggestion generator.
        
        Args:
            api_key (str, optional): Groq API key. If None, reads from environment.
            config: Configuration object for Groq settings
        """
        self.config = config or GroqResumeSuggestionConfig()
        
        # Validate Groq availability
        if not Groq:
            raise ImportError("Groq SDK not installed. Install with: pip install groq")
        
        # Initialize Groq client
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key not found. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        self.client = Groq(api_key=self.api_key)
        
        logger.info("🤖 Groq Resume Suggestion Generator initialized successfully")
    
    def _format_job_description(self, job_data: Dict[str, Any]) -> str:
        """
        Format job data into a clean description for analysis.
        
        Args:
            job_data (Dict): Job posting information
            
        Returns:
            str: Formatted job description
        """
        description_parts = []
        
        # Add main description
        if job_data.get('description'):
            description_parts.append(job_data['description'])
        
        # Add additional fields if available
        if job_data.get('requirements'):
            description_parts.append(f"Requirements: {job_data['requirements']}")
        
        if job_data.get('qualifications'):
            description_parts.append(f"Qualifications: {job_data['qualifications']}")
        
        if job_data.get('responsibilities'):
            description_parts.append(f"Responsibilities: {job_data['responsibilities']}")
        
        # Add salary info if relevant for positioning
        if job_data.get('salary_min') or job_data.get('salary_max'):
            salary_info = f"Salary: {job_data.get('salary_min', 'N/A')} - {job_data.get('salary_max', 'N/A')}"
            description_parts.append(salary_info)
        
        return "\n\n".join(description_parts)
    
    def _clean_resume_text(self, resume_text: str) -> str:
        """
        Clean and prepare resume text for analysis.
        
        Args:
            resume_text (str): Raw resume text
            
        Returns:
            str: Cleaned resume text
        """
        if not resume_text:
            return ""
        
        # Basic cleaning - remove excessive whitespace
        cleaned = ' '.join(resume_text.split())
        
        # Limit length to avoid token limits (keep first 3000 chars)
        if len(cleaned) > 3000:
            cleaned = cleaned[:3000] + "..."
            logger.info(f"📝 Resume text truncated to 3000 characters for analysis")
        
        return cleaned
    
    def _detect_job_category(self, job_data: Dict[str, Any]) -> str:
        """
        Detect the job category based on job title and description.
        
        Args:
            job_data (Dict): Job posting information
            
        Returns:
            str: Detected job category
        """
        job_title = job_data.get('title', '').lower()
        job_description = job_data.get('description', '').lower()
        
        # Combine title and description for analysis
        combined_text = f"{job_title} {job_description}"
        
        # Score each category based on keyword matches
        category_scores = {}
        
        for category, info in self.config.TECH_JOB_CATEGORIES.items():
            score = 0
            keywords = info['keywords']
            
            # Check title first (higher weight)
            for keyword in keywords:
                if keyword in job_title:
                    score += 3  # Title matches are more important
            
            # Check description
            for keyword in keywords:
                if keyword in job_description:
                    score += 1
            
            category_scores[category] = score
        
        # Find the category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        # Default fallback based on common patterns
        if any(word in job_title for word in ['developer', 'engineer', 'programmer', 'software']):
            return 'software_developer'
        elif any(word in job_title for word in ['data', 'analyst', 'scientist']):
            return 'data_scientist'
        elif any(word in job_title for word in ['devops', 'cloud', 'infrastructure']):
            return 'devops'
        elif any(word in job_title for word in ['security', 'cyber']):
            return 'cybersecurity'
        elif any(word in job_title for word in ['support', 'help', 'desk', 'technician']):
            return 'it_support'
        elif any(word in job_title for word in ['product', 'manager']):
            return 'product_manager'
        elif any(word in job_title for word in ['qa', 'test', 'quality']):
            return 'qa_engineer'
        elif any(word in job_title for word in ['ui', 'ux', 'design']):
            return 'ui_ux_designer'
        elif any(word in job_title for word in ['network', 'cisco']):
            return 'network_engineer'
        else:
            return 'software_developer'  # Default fallback
    
    def generate_resume_suggestions(self, resume_text: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered resume improvement suggestions using Groq.
        
        Args:
            resume_text (str): Candidate's resume text
            job_data (Dict): Job posting information
            
        Returns:
            Dict: Structured suggestions and analysis
        """
        try:
            # Prepare inputs
            cleaned_resume = self._clean_resume_text(resume_text)
            if not cleaned_resume:
                return {
                    'error': 'Resume text is empty or could not be processed',
                    'suggestions': None
                }
            
            formatted_job_desc = self._format_job_description(job_data)
            
            # Detect job category
            job_category = self._detect_job_category(job_data)
            category_info = self.config.TECH_JOB_CATEGORIES.get(job_category, {})
            category_display = category_info.get('focus', job_category.replace('_', ' ').title())
            
            # Create prompt
            user_prompt = self.config.USER_PROMPT_TEMPLATE.format(
                job_title=job_data.get('title', 'Unknown Position'),
                company=job_data.get('company', 'Unknown Company'),
                job_category=category_display,
                job_description=formatted_job_desc,
                resume_text=cleaned_resume
            )
            
            logger.info(f"🚀 Generating resume suggestions for {job_data.get('title', 'job')} at {job_data.get('company', 'company')}")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": self.config.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE,
                top_p=0.9,
                stream=False
            )
            
            # Extract suggestions
            suggestions_text = response.choices[0].message.content
            
            # Parse and structure the response
            parsed_suggestions = self._parse_suggestions(suggestions_text)
            
            result = {
                'success': True,
                'job_info': {
                    'title': job_data.get('title', 'Unknown'),
                    'company': job_data.get('company', 'Unknown'),
                    'location': job_data.get('location', 'Unknown'),
                    'category': job_category,
                    'category_display': category_display
                },
                'suggestions': parsed_suggestions,
                'raw_response': suggestions_text,
                'generated_at': datetime.now().isoformat(),
                'model_used': self.config.MODEL_NAME,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
            logger.info(f"✅ Successfully generated resume suggestions using {self.config.MODEL_NAME}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating resume suggestions: {str(e)}")
            return {
                'error': f'Failed to generate suggestions: {str(e)}',
                'success': False,
                'suggestions': None
            }
    
    def _parse_suggestions(self, suggestions_text: str) -> Dict[str, Any]:
        """
        Parse the AI response into structured sections.
        
        Args:
            suggestions_text (str): Raw AI response
            
        Returns:
            Dict: Parsed suggestions by section
        """
        sections = {
            'fit_summary': '',
            'missing_keywords': [],
            'improvement_suggestions': [],
            'professional_advice': [],
            'full_text': suggestions_text
        }
        
        try:
            # Split by sections (basic parsing)
            lines = suggestions_text.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers
                if 'RESUME-JOB FIT SUMMARY' in line.upper():
                    current_section = 'fit_summary'
                    current_content = []
                elif 'MISSING ATS KEYWORDS' in line.upper() or 'MISSING KEYWORDS' in line.upper():
                    current_section = 'missing_keywords'
                    current_content = []
                elif 'IMPROVEMENT SUGGESTIONS' in line.upper() or 'RESUME IMPROVEMENT' in line.upper():
                    current_section = 'improvement_suggestions'
                    current_content = []
                elif 'PROFESSIONAL ADVICE' in line.upper():
                    current_section = 'professional_advice'
                    current_content = []
                else:
                    # Add content to current section
                    if current_section and line:
                        current_content.append(line)
                        
                        # Update sections
                        if current_section == 'fit_summary':
                            sections['fit_summary'] = ' '.join(current_content)
                        elif current_section in ['missing_keywords', 'improvement_suggestions', 'professional_advice']:
                            # Clean up bullet points and add to list
                            clean_line = line.lstrip('- •*').strip()
                            if clean_line and clean_line not in sections[current_section]:
                                sections[current_section].append(clean_line)
            
            # Fallback: if parsing failed, put everything in full_text
            if not any([sections['fit_summary'], sections['missing_keywords'], 
                       sections['improvement_suggestions'], sections['professional_advice']]):
                sections['fit_summary'] = suggestions_text[:200] + "..." if len(suggestions_text) > 200 else suggestions_text
                
        except Exception as e:
            logger.warning(f"⚠️ Error parsing suggestions: {str(e)}. Using raw text.")
            sections['fit_summary'] = suggestions_text[:200] + "..." if len(suggestions_text) > 200 else suggestions_text
        
        return sections

# Convenience functions
def generate_resume_suggestions_groq(resume_text: str, job_data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to generate resume suggestions using Groq.
    
    Args:
        resume_text (str): Resume content
        job_data (Dict): Job posting data
        api_key (str, optional): Groq API key
        
    Returns:
        Dict: Resume improvement suggestions
    """
    try:
        generator = GroqResumeSuggestionGenerator(api_key=api_key)
        return generator.generate_resume_suggestions(resume_text, job_data)
    except Exception as e:
        logger.error(f"❌ Error in convenience function: {str(e)}")
        return {
            'error': str(e),
            'success': False,
            'suggestions': None
        }

def save_suggestions_to_file(suggestions: Dict[str, Any], output_path: str) -> bool:
    """
    Save resume suggestions to a text file.
    
    Args:
        suggestions (Dict): Suggestions data
        output_path (str): Path to save file
        
    Returns:
        bool: Success status
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("RESUME IMPROVEMENT SUGGESTIONS\n")
            f.write("=" * 50 + "\n\n")
            
            # Job info
            job_info = suggestions.get('job_info', {})
            f.write(f"Job: {job_info.get('title', 'Unknown')}\n")
            f.write(f"Company: {job_info.get('company', 'Unknown')}\n")
            f.write(f"Generated: {suggestions.get('generated_at', 'Unknown')}\n")
            f.write(f"AI Model: {suggestions.get('model_used', 'Unknown')}\n\n")
            
            # Suggestions
            if suggestions.get('suggestions'):
                parsed = suggestions['suggestions']
                
                if parsed.get('fit_summary'):
                    f.write("RESUME-JOB FIT SUMMARY:\n")
                    f.write(f"{parsed['fit_summary']}\n\n")
                
                if parsed.get('missing_keywords'):
                    f.write("MISSING ATS KEYWORDS:\n")
                    for keyword in parsed['missing_keywords']:
                        f.write(f"- {keyword}\n")
                    f.write("\n")
                
                if parsed.get('improvement_suggestions'):
                    f.write("RESUME IMPROVEMENT SUGGESTIONS:\n")
                    for suggestion in parsed['improvement_suggestions']:
                        f.write(f"- {suggestion}\n")
                    f.write("\n")
                
                if parsed.get('professional_advice'):
                    f.write("PROFESSIONAL ADVICE:\n")
                    for advice in parsed['professional_advice']:
                        f.write(f"- {advice}\n")
                    f.write("\n")
            
            # Full response
            if suggestions.get('raw_response'):
                f.write("FULL AI RESPONSE:\n")
                f.write("-" * 30 + "\n")
                f.write(suggestions['raw_response'])
        
        logger.info(f"💾 Saved resume suggestions to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save suggestions: {str(e)}")
        return False

def get_groq_match_score_and_explanation(resume_text: str, job_data: dict, api_key: Optional[str] = None) -> dict:
    """
    Use Groq Llama-4-Scout-17B to get a match score (0-100) and a one-sentence explanation for a resume vs. job.
    Returns a dict: {"score": int, "explanation": str}
    """
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Groq SDK not installed. Install with: pip install groq")
    api_key = api_key or os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("Groq API key not found. Set GROQ_API_KEY environment variable or pass api_key parameter.")
    client = Groq(api_key=api_key)
    prompt = f'''
You are an expert job matching assistant. Given the following resume and job description, return a match score from 0 to 100 (where 100 is a perfect fit) and a one-sentence explanation.

Resume:\n{resume_text}\n\nJob Description:\n{job_data.get('description', '')}\n\nRespond in JSON: {{"score": <number>, "explanation": "<string>"}}
'''
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": "You are an expert job matching assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=256,
        temperature=0.2,
        top_p=0.9,
        stream=False
    )
    content = response.choices[0].message.content
    import json as _json
    try:
        result = _json.loads(content)
        score = int(result.get("score", 0))
        explanation = str(result.get("explanation", ""))
        return {"score": score, "explanation": explanation}
    except Exception:
        # fallback: try to extract score/explanation from text
        import re
        score_match = re.search(r'"score"\s*:\s*(\d+)', content)
        explanation_match = re.search(r'"explanation"\s*:\s*"([^"]+)"', content)
        score = int(score_match.group(1)) if score_match else 0
        explanation = explanation_match.group(1) if explanation_match else content.strip()
        return {"score": score, "explanation": explanation}

if __name__ == "__main__":
    # Test the Groq integration
    logger.info("🧪 Testing Groq Resume Suggestion Generator...")
    
    # Sample data for testing
    sample_resume = """
    John Doe
    IT Support Specialist
    
    Experience:
    - 3 years help desk support
    - Windows 10 troubleshooting
    - Customer service excellence
    
    Skills:
    - Microsoft Office
    - Basic networking
    - Remote desktop support
    """
    
    sample_job = {
        'title': 'IT Support Specialist',
        'company': 'TechCorp Inc.',
        'description': 'Seeking IT Support Specialist with Active Directory, Office 365, and ITIL experience. Must have strong troubleshooting skills and help desk background.',
        'location': 'Remote'
    }
    
    # Test if API key is available
    if os.getenv('GROQ_API_KEY'):
        try:
            suggestions = generate_resume_suggestions_groq(sample_resume, sample_job)
            
            if suggestions.get('success'):
                print("✅ Test successful!")
                print(f"Fit Summary: {suggestions['suggestions']['fit_summary']}")
                print(f"Missing Keywords: {len(suggestions['suggestions']['missing_keywords'])}")
                print(f"Improvement Suggestions: {len(suggestions['suggestions']['improvement_suggestions'])}")
            else:
                print(f"⚠️ Test failed: {suggestions.get('error')}")
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
    else:
        print("ℹ️ No GROQ_API_KEY found. Set environment variable to test.")
        print("ℹ️ Groq Resume Suggestion Generator ready for use.") 
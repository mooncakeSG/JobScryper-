"""
Job-Resume Matcher Module for Auto Applier

This module uses TF-IDF vectorization and cosine similarity to intelligently
match job descriptions against resumes, focusing on IT Support roles.

Author: MooncakeSG
Created: 2025-07-07
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None
    ENGLISH_STOP_WORDS = None

from resume_parser import ResumeParser, get_resume_text_for_matching

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobResumeMatcherConfig:
    """Configuration class for the job-resume matcher."""
    
    # IT Support specific keywords with weights
    IT_SUPPORT_KEYWORDS = {
        # Technical Skills (high weight)
        'windows': 2.0, 'linux': 2.0, 'macos': 1.5, 'active directory': 3.0,
        'office 365': 2.5, 'azure': 2.0, 'aws': 2.0, 'powershell': 2.0,
        'python': 1.5, 'sql': 1.5, 'networking': 2.5, 'tcp/ip': 2.0,
        'dhcp': 1.5, 'dns': 1.5, 'vpn': 2.0, 'firewall': 2.0,
        'antivirus': 1.5, 'backup': 1.5, 'restore': 1.5,
        
        # IT Support Tools (high weight)
        'ticketing': 2.5, 'helpdesk': 3.0, 'remote desktop': 2.0,
        'virtualization': 2.0, 'vmware': 2.0, 'hyper-v': 2.0,
        'citrix': 1.5, 'terminal services': 1.5,
        
        # Vendor Systems (medium weight)
        'cisco': 1.5, 'microsoft': 2.0, 'exchange': 2.0, 'sharepoint': 1.5,
        'teams': 1.5, 'slack': 1.0, 'zoom': 1.0,
        
        # Methodologies (medium weight)
        'itil': 2.5, 'incident management': 2.0, 'change management': 1.5,
        'problem management': 2.0, 'service desk': 2.5,
        
        # Hardware (medium weight)
        'hardware': 1.5, 'laptop': 1.0, 'desktop': 1.0, 'printer': 1.0,
        'monitor': 1.0, 'troubleshooting': 2.5, 'diagnostic': 2.0,
        
        # Support Skills (high weight)
        'customer service': 2.0, 'user support': 2.5, 'technical support': 3.0,
        'end user': 2.0, 'help desk': 3.0, 'it support': 3.0
    }
    
    # Stop words specific to job descriptions (to ignore)
    JOB_STOP_WORDS = {
        'experience', 'years', 'required', 'preferred', 'must', 'should',
        'candidate', 'position', 'role', 'job', 'work', 'team', 'company',
        'opportunity', 'looking', 'seeking', 'hiring', 'join', 'benefits',
        'salary', 'competitive', 'excellent', 'great', 'good', 'strong'
    }

class JobResumeMatcher:
    """
    Intelligent job-resume matcher using TF-IDF and cosine similarity.
    Optimized for IT Support role matching with domain-specific enhancements.
    """
    
    def __init__(self, config: Optional[JobResumeMatcherConfig] = None):
        """
        Initialize the job-resume matcher.
        
        Args:
            config: Configuration object with IT Support specific settings
        """
        self.config = config or JobResumeMatcherConfig()
        self.vectorizer = None
        self.resume_text = ""
        self.resume_vector = None
        self.job_vectors = None
        self.processed_jobs = []
        
        # Validate dependencies
        if not all([TfidfVectorizer, cosine_similarity, ENGLISH_STOP_WORDS]):
            raise ImportError("scikit-learn is required for job matching. Install with: pip install scikit-learn")
        
        logger.info("🤖 JobResumeMatcher initialized successfully")
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better TF-IDF vectorization.
        
        Args:
            text (str): Raw text to preprocess
            
        Returns:
            str: Preprocessed text optimized for matching
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\+\#\.]', ' ', text)
        
        # Handle common IT abbreviations and terms
        text = re.sub(r'\bos\b', 'operating system', text)
        text = re.sub(r'\bvm\b', 'virtual machine', text)
        text = re.sub(r'\bpc\b', 'computer', text)
        text = re.sub(r'\bit\b', 'information technology', text)
        text = re.sub(r'\bsla\b', 'service level agreement', text)
        text = re.sub(r'\brca\b', 'root cause analysis', text)
        
        # Expand common abbreviations
        text = re.sub(r'\bad\b', 'active directory', text)
        text = re.sub(r'\brdp\b', 'remote desktop protocol', text)
        text = re.sub(r'\bvpn\b', 'virtual private network', text)
        
        return text.strip()
    
    def extract_job_features(self, job: Dict[str, Any]) -> str:
        """
        Extract and combine relevant features from a job posting.
        
        Args:
            job (Dict): Job posting data
            
        Returns:
            str: Combined text features for matching
        """
        features = []
        
        # Job title (high importance)
        if job.get('title'):
            title = job['title']
            features.append(f"{title} {title}")  # Double weight for title
        
        # Job description (primary content)
        if job.get('description'):
            features.append(job['description'])
        
        # Company (medium importance)
        if job.get('company'):
            features.append(job['company'])
        
        # Location (low importance)
        if job.get('location'):
            features.append(job['location'])
        
        # Skills/Requirements if available
        if job.get('skills'):
            features.append(job['skills'])
        
        # Salary info might contain level indicators
        if job.get('salary_min') or job.get('salary_max'):
            salary_text = f"salary {job.get('salary_min', '')} {job.get('salary_max', '')}"
            features.append(salary_text)
        
        combined_text = ' '.join(filter(None, features))
        return self.preprocess_text(combined_text)
    
    def setup_vectorizer(self, resume_text: str, job_texts: List[str]) -> None:
        """
        Setup and fit the TF-IDF vectorizer with resume and job texts.
        
        Args:
            resume_text (str): Preprocessed resume text
            job_texts (List[str]): List of preprocessed job texts
        """
        # Combine stop words
        custom_stop_words = set(ENGLISH_STOP_WORDS) | self.config.JOB_STOP_WORDS
        
        # Configure TF-IDF vectorizer for IT job matching
        self.vectorizer = TfidfVectorizer(
            max_features=5000,          # Limit vocabulary size
            min_df=1,                   # Include rare terms (important for IT skills)
            max_df=0.8,                 # Exclude very common terms
            ngram_range=(1, 3),         # Include 1-3 word phrases
            stop_words=list(custom_stop_words),
            lowercase=True,
            strip_accents='unicode',
            analyzer='word',
            token_pattern=r'\b[a-zA-Z0-9][a-zA-Z0-9\-\.]*[a-zA-Z0-9]\b|\b[a-zA-Z0-9]\b'
        )
        
        # Combine all texts for fitting
        all_texts = [resume_text] + job_texts
        
        # Fit the vectorizer
        self.vectorizer.fit(all_texts)
        
        logger.info(f"🔧 TF-IDF vectorizer fitted with {len(self.vectorizer.vocabulary_)} features")
    
    def enhance_similarity_score(self, base_score: float, job_text: str, resume_text: str) -> float:
        """
        Enhance the base cosine similarity score with domain-specific knowledge.
        
        Args:
            base_score (float): Base cosine similarity score
            job_text (str): Preprocessed job text
            resume_text (str): Preprocessed resume text
            
        Returns:
            float: Enhanced similarity score
        """
        enhancement = 0.0
        
        # Check for IT Support keyword matches with weights
        job_words = set(job_text.lower().split())
        resume_words = set(resume_text.lower().split())
        
        for keyword, weight in self.config.IT_SUPPORT_KEYWORDS.items():
            keyword_words = set(keyword.lower().split())
            
            # Check if both job and resume contain this keyword
            if (keyword_words.issubset(job_words) and keyword_words.issubset(resume_words)):
                enhancement += 0.01 * weight  # Small boost for keyword matches
        
        # Boost for IT Support role indicators
        it_support_indicators = ['it support', 'technical support', 'help desk', 'helpdesk']
        for indicator in it_support_indicators:
            if indicator in job_text.lower() and any(term in resume_text.lower() for term in ['support', 'technical', 'help']):
                enhancement += 0.02
        
        # Boost for experience level alignment
        if 'entry level' in job_text.lower() or 'junior' in job_text.lower():
            if any(term in resume_text.lower() for term in ['entry', 'junior', 'associate', 'intern']):
                enhancement += 0.01
        
        if 'senior' in job_text.lower() or 'lead' in job_text.lower():
            if any(term in resume_text.lower() for term in ['senior', 'lead', 'manager', 'supervisor']):
                enhancement += 0.01
        
        # Cap the enhancement to prevent over-boosting
        enhancement = min(enhancement, 0.15)
        
        # Combine base score with enhancement
        enhanced_score = base_score + enhancement
        
        # Ensure score stays within valid range
        return min(enhanced_score, 1.0)
    
    def calculate_match_scores(self, resume_text: str, jobs: List[Dict[str, Any]]) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Calculate match scores between resume and all job postings.
        
        Args:
            resume_text (str): Clean resume text
            jobs (List[Dict]): List of job postings
            
        Returns:
            List[Tuple]: List of (job_index, match_score, job_data) sorted by score
        """
        if not jobs:
            logger.warning("⚠️ No jobs provided for matching")
            return []
        
        if not resume_text.strip():
            logger.error("❌ Resume text is empty")
            return []
        
        # Preprocess resume text
        processed_resume = self.preprocess_text(resume_text)
        
        # Extract and preprocess job features
        job_texts = []
        for job in jobs:
            job_text = self.extract_job_features(job)
            job_texts.append(job_text)
        
        # Setup vectorizer
        self.setup_vectorizer(processed_resume, job_texts)
        
        # Transform texts to vectors
        resume_vector = self.vectorizer.transform([processed_resume])
        job_vectors = self.vectorizer.transform(job_texts)
        
        # Calculate cosine similarities
        similarities = cosine_similarity(resume_vector, job_vectors)[0]
        
        # Enhance scores with domain knowledge
        enhanced_scores = []
        for i, (base_score, job_text) in enumerate(zip(similarities, job_texts)):
            enhanced_score = self.enhance_similarity_score(base_score, job_text, processed_resume)
            enhanced_scores.append((i, enhanced_score, jobs[i]))
        
        # Sort by score (highest first)
        enhanced_scores.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"✅ Calculated match scores for {len(jobs)} jobs")
        logger.info(f"📊 Top score: {enhanced_scores[0][1]:.1%} | Bottom score: {enhanced_scores[-1][1]:.1%}")
        
        return enhanced_scores
    
    def get_top_matches(self, resume_path: str, jobs: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N job matches for a given resume.
        
        Args:
            resume_path (str): Path to the resume file
            jobs (List[Dict]): List of job postings
            top_n (int): Number of top matches to return
            
        Returns:
            List[Dict]: Top matched jobs with scores and match details
        """
        try:
            # Extract resume text
            resume_text = get_resume_text_for_matching(resume_path)
            
            if not resume_text:
                logger.error(f"❌ Could not extract text from resume: {resume_path}")
                return []
            
            # Calculate match scores
            match_scores = self.calculate_match_scores(resume_text, jobs)
            
            if not match_scores:
                logger.warning("⚠️ No match scores calculated")
                return []
            
            # Prepare top matches
            top_matches = []
            for i, (job_index, score, job_data) in enumerate(match_scores[:top_n]):
                match_data = {
                    'rank': i + 1,
                    'match_score': score,
                    'match_percentage': round(score * 100, 1),
                    'job_data': job_data,
                    'job_index': job_index,
                    'match_quality': self.get_match_quality(score),
                    'key_factors': self.analyze_match_factors(resume_text, job_data)
                }
                top_matches.append(match_data)
            
            logger.info(f"🎯 Found {len(top_matches)} top matches (requested: {top_n})")
            
            return top_matches
            
        except Exception as e:
            logger.error(f"❌ Error in get_top_matches: {str(e)}")
            return []
    
    def get_match_quality(self, score: float) -> str:
        """
        Determine match quality based on score.
        
        Args:
            score (float): Match score (0-1)
            
        Returns:
            str: Quality description
        """
        if score >= 0.8:
            return "Excellent Match"
        elif score >= 0.6:
            return "Good Match"
        elif score >= 0.4:
            return "Fair Match"
        elif score >= 0.2:
            return "Poor Match"
        else:
            return "Very Poor Match"
    
    def analyze_match_factors(self, resume_text: str, job_data: Dict[str, Any]) -> List[str]:
        """
        Analyze key factors contributing to the match.
        
        Args:
            resume_text (str): Resume text
            job_data (Dict): Job posting data
            
        Returns:
            List[str]: List of key matching factors
        """
        factors = []
        
        job_text = self.extract_job_features(job_data).lower()
        resume_lower = resume_text.lower()
        
        # Check for technical skill matches
        tech_matches = []
        for keyword, weight in self.config.IT_SUPPORT_KEYWORDS.items():
            if keyword in job_text and keyword in resume_lower:
                tech_matches.append(keyword)
        
        if tech_matches:
            factors.append(f"Technical skills: {', '.join(tech_matches[:3])}")
        
        # Check for role alignment
        if 'support' in job_text and 'support' in resume_lower:
            factors.append("Support role alignment")
        
        if 'helpdesk' in job_text and ('helpdesk' in resume_lower or 'help desk' in resume_lower):
            factors.append("Help desk experience")
        
        # Check for industry experience
        if any(term in job_text for term in ['enterprise', 'corporate']) and \
           any(term in resume_lower for term in ['enterprise', 'corporate', 'business']):
            factors.append("Enterprise environment")
        
        return factors[:5]  # Return top 5 factors

# Convenience functions for direct usage
def match_resume_to_jobs(resume_path: str, jobs: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function to match a resume against job postings.
    
    Args:
        resume_path (str): Path to the resume file
        jobs (List[Dict]): List of job postings
        top_n (int): Number of top matches to return
        
    Returns:
        List[Dict]: Top matched jobs with scores
    """
    matcher = JobResumeMatcher()
    return matcher.get_top_matches(resume_path, jobs, top_n)

def calculate_single_match_score(resume_path: str, job_data: Dict[str, Any]) -> float:
    """
    Calculate match score between a resume and single job posting.
    
    Args:
        resume_path (str): Path to the resume file
        job_data (Dict): Single job posting data
        
    Returns:
        float: Match score (0-1)
    """
    matcher = JobResumeMatcher()
    matches = matcher.get_top_matches(resume_path, [job_data], top_n=1)
    
    if matches:
        return matches[0]['match_score']
    return 0.0

if __name__ == "__main__":
    # Test the matcher
    logger.info("🧪 Testing JobResumeMatcher...")
    
    # Sample job for testing
    sample_job = {
        'title': 'IT Support Specialist',
        'description': 'Provide technical support for Windows and Linux systems. Experience with Active Directory, Office 365, and help desk tools required.',
        'company': 'TechCorp Inc.',
        'location': 'Remote'
    }
    
    # Test with existing resume if available
    import os
    assets_dir = "assets"
    if os.path.exists(assets_dir):
        resume_files = [f for f in os.listdir(assets_dir) if f.endswith('.pdf')]
        if resume_files:
            test_resume = os.path.join(assets_dir, resume_files[0])
            matcher = JobResumeMatcher()
            matches = matcher.get_top_matches(test_resume, [sample_job], top_n=1)
            
            if matches:
                print(f"✅ Test successful!")
                print(f"Match Score: {matches[0]['match_percentage']}%")
                print(f"Match Quality: {matches[0]['match_quality']}")
            else:
                print("⚠️ No matches found in test")
        else:
            print("ℹ️ No resume files found for testing")
    else:
        print("ℹ️ Assets directory not found. Matcher ready for use.") 
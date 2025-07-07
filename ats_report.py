"""
ATS Report Module for Auto Applier

This module generates ATS (Applicant Tracking System) keyword scores,
identifies missing job-related keywords, and performs bias detection
for inclusive job targeting in IT Support roles.

Author: MooncakeSG
Created: 2025-07-07
"""

import re
import json
import logging
from typing import Dict, List, Any, Set, Tuple, Optional
from datetime import datetime
from pathlib import Path

from resume_parser import get_resume_text_for_matching

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ATSReportConfig:
    """Configuration class for ATS analysis and bias detection."""
    
    # Critical IT Support keywords for ATS scoring
    CRITICAL_ATS_KEYWORDS = {
        # Must-have technical skills (high score impact)
        'windows': 10, 'linux': 10, 'active directory': 15, 'office 365': 12,
        'help desk': 15, 'helpdesk': 15, 'technical support': 15, 'it support': 15,
        'troubleshooting': 12, 'customer service': 10,
        
        # Important technical skills (medium score impact)
        'networking': 8, 'hardware': 6, 'software': 6, 'microsoft': 8,
        'remote desktop': 8, 'vpn': 6, 'firewall': 6, 'antivirus': 6,
        'backup': 6, 'restore': 6, 'ticketing': 10, 'incident management': 8,
        
        # Valuable skills (lower score impact)
        'azure': 5, 'aws': 5, 'powershell': 5, 'python': 4, 'sql': 4,
        'virtualization': 6, 'vmware': 5, 'citrix': 4, 'exchange': 6,
        'sharepoint': 4, 'teams': 4, 'itil': 8, 'service desk': 10
    }
    
    # Common ATS keywords that boost scores
    GENERAL_ATS_KEYWORDS = {
        'experience': 3, 'years': 2, 'support': 5, 'technology': 3,
        'systems': 4, 'users': 4, 'environment': 3, 'applications': 4,
        'installation': 4, 'configuration': 4, 'maintenance': 4,
        'documentation': 3, 'training': 4, 'communication': 4
    }
    
    # Bias detection patterns - problematic language
    BIAS_PATTERNS = {
        # Age bias
        'age_bias': [
            r'\b(?:young|youthful)\b', r'\b(?:energetic|dynamic)\s+(?:young|junior)\b',
            r'\b(?:recent\s+grad(?:uate)?s?)\s+only\b', r'\b(?:new\s+grad(?:uate)?s?)\s+preferred\b',
            r'\b(?:digital\s+native)\b', r'\b(?:fresh\s+out\s+of\s+college)\b'
        ],
        
        # Gender bias
        'gender_bias': [
            r'\b(?:rockstar|ninja|wizard|guru|hero)\b', r'\b(?:guys?|dudes?)\b',
            r'\b(?:manpower|man-hours)\b', r'\b(?:chairman|salesman)\b',
            r'\b(?:strong|aggressive|competitive)\s+(?:personality|individual)\b'
        ],
        
        # Cultural/linguistic bias
        'cultural_bias': [
            r'\b(?:native\s+(?:english\s+)?speaker)\b', r'\b(?:perfect\s+english)\b',
            r'\b(?:american\s+born)\b', r'\b(?:local\s+candidates\s+only)\b',
            r'\b(?:no\s+accent)\b', r'\b(?:mother\s+tongue)\b'
        ],
        
        # Educational bias
        'education_bias': [
            r'\b(?:ivy\s+league)\b', r'\b(?:top\s+tier\s+university)\b',
            r'\b(?:prestigious\s+university)\b', r'\b(?:elite\s+college)\b'
        ],
        
        # Experience bias (over-qualification)
        'experience_bias': [
            r'\b(?:overqualified)\b', r'\b(?:too\s+experienced)\b',
            r'\b(?:we\'re\s+looking\s+for\s+someone\s+younger)\b'
        ],
        
        # Appearance/physical bias
        'appearance_bias': [
            r'\b(?:attractive|good-looking|presentable)\b',
            r'\b(?:professional\s+appearance)\s+(?:required|mandatory)\b',
            r'\b(?:must\s+be\s+physically\s+fit)\b'
        ]
    }
    
    # Inclusive language indicators (positive bias detection)
    INCLUSIVE_LANGUAGE = [
        'equal opportunity', 'diversity', 'inclusion', 'all backgrounds welcome',
        'underrepresented groups', 'veterans welcome', 'disability accommodation',
        'flexible work arrangements', 'work-life balance', 'family-friendly',
        'remote work', 'flexible schedule', 'part-time', 'job sharing'
    ]
    
    # Red flag phrases that may indicate problematic workplace culture
    RED_FLAG_PHRASES = [
        'work hard, play hard', 'we\'re like a family', 'no 9-to-5 mentality',
        'wear many hats', 'fast-paced startup environment', 'unlimited pto',
        'competitive salary (no range provided)', 'equity instead of salary',
        'unpaid overtime expected', 'must be available 24/7'
    ]

class ATSAnalyzer:
    """
    Comprehensive ATS analysis and bias detection for job postings.
    Focused on IT Support role requirements and inclusive hiring practices.
    """
    
    def __init__(self, config: Optional[ATSReportConfig] = None):
        """
        Initialize the ATS analyzer.
        
        Args:
            config: Configuration object with ATS and bias detection settings
        """
        self.config = config or ATSReportConfig()
        logger.info("📊 ATSAnalyzer initialized successfully")
    
    def extract_job_text(self, job_data: Dict[str, Any]) -> str:
        """
        Extract combined text from job posting for analysis.
        
        Args:
            job_data (Dict): Job posting data
            
        Returns:
            str: Combined job text for analysis
        """
        text_parts = []
        
        # Include all relevant text fields
        fields_to_include = ['title', 'description', 'requirements', 'qualifications', 'responsibilities']
        
        for field in fields_to_include:
            if job_data.get(field):
                text_parts.append(str(job_data[field]))
        
        # Also include company info if available
        if job_data.get('company'):
            text_parts.append(str(job_data['company']))
        
        return ' '.join(text_parts)
    
    def calculate_ats_keyword_score(self, job_text: str, resume_text: str) -> Dict[str, Any]:
        """
        Calculate ATS keyword match score between job and resume.
        
        Args:
            job_text (str): Combined job posting text
            resume_text (str): Resume text
            
        Returns:
            Dict: ATS scoring results
        """
        job_lower = job_text.lower()
        resume_lower = resume_text.lower()
        
        # Track matches and misses
        critical_matches = []
        critical_misses = []
        general_matches = []
        total_possible_score = 0
        earned_score = 0
        
        # Check critical IT Support keywords
        for keyword, score_value in self.config.CRITICAL_ATS_KEYWORDS.items():
            total_possible_score += score_value
            
            if keyword.lower() in job_lower:  # Keyword is in job posting
                if keyword.lower() in resume_lower:  # Also in resume
                    critical_matches.append({
                        'keyword': keyword,
                        'score': score_value,
                        'category': 'critical'
                    })
                    earned_score += score_value
                else:  # Missing from resume
                    critical_misses.append({
                        'keyword': keyword,
                        'score': score_value,
                        'category': 'critical'
                    })
        
        # Check general ATS keywords
        general_possible_score = 0
        for keyword, score_value in self.config.GENERAL_ATS_KEYWORDS.items():
            if keyword.lower() in job_lower:
                general_possible_score += score_value
                if keyword.lower() in resume_lower:
                    general_matches.append({
                        'keyword': keyword,
                        'score': score_value,
                        'category': 'general'
                    })
                    earned_score += score_value
        
        total_possible_score += general_possible_score
        
        # Calculate percentage score
        ats_percentage = (earned_score / total_possible_score * 100) if total_possible_score > 0 else 0
        
        return {
            'ats_score': round(ats_percentage, 1),
            'earned_points': earned_score,
            'possible_points': total_possible_score,
            'critical_matches': critical_matches,
            'critical_misses': critical_misses,
            'general_matches': general_matches,
            'match_count': len(critical_matches) + len(general_matches),
            'miss_count': len(critical_misses)
        }
    
    def identify_missing_keywords(self, job_text: str, resume_text: str) -> List[Dict[str, Any]]:
        """
        Identify important keywords missing from resume but present in job posting.
        
        Args:
            job_text (str): Job posting text
            resume_text (str): Resume text
            
        Returns:
            List[Dict]: Missing keywords with recommendations
        """
        job_lower = job_text.lower()
        resume_lower = resume_text.lower()
        
        missing_keywords = []
        
        # Combine all keyword dictionaries
        all_keywords = {**self.config.CRITICAL_ATS_KEYWORDS, **self.config.GENERAL_ATS_KEYWORDS}
        
        for keyword, importance in all_keywords.items():
            if keyword.lower() in job_lower and keyword.lower() not in resume_lower:
                # Determine category and recommendation
                category = 'critical' if keyword in self.config.CRITICAL_ATS_KEYWORDS else 'general'
                
                recommendation = self.get_keyword_recommendation(keyword, category)
                
                missing_keywords.append({
                    'keyword': keyword,
                    'importance': importance,
                    'category': category,
                    'recommendation': recommendation
                })
        
        # Sort by importance (highest first)
        missing_keywords.sort(key=lambda x: x['importance'], reverse=True)
        
        return missing_keywords
    
    def get_keyword_recommendation(self, keyword: str, category: str) -> str:
        """
        Get specific recommendation for missing keyword.
        
        Args:
            keyword (str): Missing keyword
            category (str): Keyword category (critical/general)
            
        Returns:
            str: Specific recommendation
        """
        recommendations = {
            'windows': 'Add Windows administration or support experience to your resume',
            'linux': 'Include any Linux/Unix experience, even basic command line usage',
            'active directory': 'Mention AD experience in user management or system administration',
            'help desk': 'Emphasize help desk, service desk, or user support experience',
            'technical support': 'Highlight technical troubleshooting and user assistance roles',
            'troubleshooting': 'Detail your problem-solving and diagnostic skills',
            'ticketing': 'Mention experience with ticketing systems like ServiceNow, Jira, etc.',
            'networking': 'Include any network troubleshooting or TCP/IP knowledge',
            'itil': 'Add ITIL certification or framework knowledge if applicable'
        }
        
        specific_rec = recommendations.get(keyword.lower())
        if specific_rec:
            return specific_rec
        
        # Generic recommendations based on category
        if category == 'critical':
            return f'Consider gaining experience with {keyword} or adding related skills to your resume'
        else:
            return f'If you have experience with {keyword}, make sure to include it prominently'
    
    def detect_bias(self, job_text: str) -> Dict[str, Any]:
        """
        Detect potential bias in job posting language.
        
        Args:
            job_text (str): Job posting text
            
        Returns:
            Dict: Bias detection results
        """
        bias_flags = []
        inclusive_indicators = []
        red_flags = []
        
        job_lower = job_text.lower()
        
        # Check for bias patterns
        for bias_type, patterns in self.config.BIAS_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, job_lower, re.IGNORECASE)
                if matches:
                    for match in matches:
                        bias_flags.append({
                            'type': bias_type,
                            'text': match,
                            'severity': self.get_bias_severity(bias_type),
                            'recommendation': self.get_bias_recommendation(bias_type)
                        })
        
        # Check for inclusive language (positive indicators)
        for indicator in self.config.INCLUSIVE_LANGUAGE:
            if indicator.lower() in job_lower:
                inclusive_indicators.append(indicator)
        
        # Check for red flag phrases
        for red_flag in self.config.RED_FLAG_PHRASES:
            if red_flag.lower() in job_lower:
                red_flags.append(red_flag)
        
        # Calculate bias score (lower is better)
        bias_score = len(bias_flags) * 10 - len(inclusive_indicators) * 5 + len(red_flags) * 7
        bias_score = max(0, bias_score)  # Don't go below 0
        
        return {
            'bias_score': bias_score,
            'bias_level': self.get_bias_level(bias_score),
            'bias_flags': bias_flags,
            'inclusive_indicators': inclusive_indicators,
            'red_flags': red_flags,
            'total_flags': len(bias_flags),
            'recommendation': self.get_overall_bias_recommendation(bias_score, len(bias_flags))
        }
    
    def get_bias_severity(self, bias_type: str) -> str:
        """Get severity level for bias type."""
        severity_map = {
            'age_bias': 'High',
            'gender_bias': 'High',
            'cultural_bias': 'Very High',
            'education_bias': 'Medium',
            'experience_bias': 'Medium',
            'appearance_bias': 'High'
        }
        return severity_map.get(bias_type, 'Medium')
    
    def get_bias_recommendation(self, bias_type: str) -> str:
        """Get recommendation for specific bias type."""
        recommendations = {
            'age_bias': 'Focus on skills and experience rather than age-related terms',
            'gender_bias': 'Use gender-neutral language and avoid masculine-coded words',
            'cultural_bias': 'Remove language requirements unless absolutely necessary for the role',
            'education_bias': 'Focus on skills and competencies rather than prestigious institutions',
            'experience_bias': 'Be open to different levels of experience and career paths',
            'appearance_bias': 'Remove appearance-related requirements unless job-relevant'
        }
        return recommendations.get(bias_type, 'Review language for potential bias')
    
    def get_bias_level(self, bias_score: int) -> str:
        """Determine overall bias level from score."""
        if bias_score == 0:
            return 'Excellent (No Bias Detected)'
        elif bias_score <= 10:
            return 'Good (Minimal Bias)'
        elif bias_score <= 25:
            return 'Fair (Some Bias Concerns)'
        elif bias_score <= 50:
            return 'Poor (Multiple Bias Issues)'
        else:
            return 'Very Poor (Significant Bias)'
    
    def get_overall_bias_recommendation(self, bias_score: int, flag_count: int) -> str:
        """Get overall recommendation based on bias analysis."""
        if bias_score == 0:
            return '✅ This job posting demonstrates inclusive language practices'
        elif bias_score <= 10:
            return '⚠️ Minor language improvements recommended for better inclusivity'
        elif bias_score <= 25:
            return '⚠️ Several bias concerns detected - consider revising job posting language'
        else:
            return '❌ Significant bias issues detected - major language revision recommended'
    
    def generate_ats_report(self, job_data: Dict[str, Any], resume_path: str) -> Dict[str, Any]:
        """
        Generate comprehensive ATS report for a job posting and resume.
        
        Args:
            job_data (Dict): Job posting data
            resume_path (str): Path to resume file
            
        Returns:
            Dict: Complete ATS analysis report
        """
        try:
            # Extract texts
            job_text = self.extract_job_text(job_data)
            resume_text = get_resume_text_for_matching(resume_path)
            
            if not resume_text:
                logger.error(f"❌ Could not extract resume text from: {resume_path}")
                return {'error': f'Failed to extract resume text from {resume_path}'}
            
            # Perform ATS analysis
            ats_analysis = self.calculate_ats_keyword_score(job_text, resume_text)
            missing_keywords = self.identify_missing_keywords(job_text, resume_text)
            bias_analysis = self.detect_bias(job_text)
            
            # Generate report
            report = {
                'job_info': {
                    'title': job_data.get('title', 'Unknown'),
                    'company': job_data.get('company', 'Unknown'),
                    'location': job_data.get('location', 'Unknown')
                },
                'resume_info': {
                    'file_path': resume_path,
                    'file_name': Path(resume_path).name
                },
                'ats_analysis': ats_analysis,
                'missing_keywords': missing_keywords[:10],  # Top 10 missing keywords
                'bias_analysis': bias_analysis,
                'generated_at': datetime.now().isoformat(),
                'recommendations': self.generate_recommendations(ats_analysis, missing_keywords, bias_analysis)
            }
            
            logger.info(f"✅ Generated ATS report for {job_data.get('title', 'job')} - Score: {ats_analysis['ats_score']}%")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating ATS report: {str(e)}")
            return {'error': f'ATS report generation failed: {str(e)}'}
    
    def generate_recommendations(self, ats_analysis: Dict, missing_keywords: List, bias_analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # ATS Score recommendations
        ats_score = ats_analysis['ats_score']
        if ats_score < 30:
            recommendations.append("🔴 Low ATS match - consider major resume optimization")
        elif ats_score < 60:
            recommendations.append("🟡 Moderate ATS match - add key missing keywords")
        else:
            recommendations.append("🟢 Good ATS match - minor tweaks may improve score")
        
        # Missing keywords recommendations
        if missing_keywords:
            critical_missing = [kw for kw in missing_keywords if kw['category'] == 'critical']
            if critical_missing:
                recommendations.append(f"❗ Add critical keywords: {', '.join([kw['keyword'] for kw in critical_missing[:3]])}")
        
        # Bias recommendations
        if bias_analysis['bias_flags']:
            recommendations.append(f"⚠️ {len(bias_analysis['bias_flags'])} bias concerns detected in job posting")
        
        if bias_analysis['inclusive_indicators']:
            recommendations.append(f"✅ Job posting shows {len(bias_analysis['inclusive_indicators'])} inclusive practices")
        
        return recommendations

# Convenience functions
def generate_ats_report_for_job(job_data: Dict[str, Any], resume_path: str) -> Dict[str, Any]:
    """
    Convenience function to generate ATS report for a single job.
    
    Args:
        job_data (Dict): Job posting data
        resume_path (str): Path to resume file
        
    Returns:
        Dict: ATS analysis report
    """
    analyzer = ATSAnalyzer()
    return analyzer.generate_ats_report(job_data, resume_path)

def save_ats_report(report: Dict[str, Any], output_path: str) -> bool:
    """
    Save ATS report to JSON file.
    
    Args:
        report (Dict): ATS report data
        output_path (str): Path to save report
        
    Returns:
        bool: Success status
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved ATS report to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save ATS report: {str(e)}")
        return False

def export_ats_report_text(report: Dict[str, Any], output_path: str) -> bool:
    """
    Export ATS report as human-readable text file.
    
    Args:
        report (Dict): ATS report data
        output_path (str): Path to save text report
        
    Returns:
        bool: Success status
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("ATS ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Job info
            job_info = report.get('job_info', {})
            f.write(f"Job Title: {job_info.get('title', 'Unknown')}\n")
            f.write(f"Company: {job_info.get('company', 'Unknown')}\n")
            f.write(f"Location: {job_info.get('location', 'Unknown')}\n\n")
            
            # ATS Analysis
            ats = report.get('ats_analysis', {})
            f.write(f"ATS SCORE: {ats.get('ats_score', 0)}%\n")
            f.write(f"Points Earned: {ats.get('earned_points', 0)}/{ats.get('possible_points', 0)}\n\n")
            
            # Missing Keywords
            missing = report.get('missing_keywords', [])
            if missing:
                f.write("MISSING KEYWORDS:\n")
                for kw in missing[:5]:
                    f.write(f"- {kw['keyword']} ({kw['category']}) - {kw['recommendation']}\n")
                f.write("\n")
            
            # Bias Analysis
            bias = report.get('bias_analysis', {})
            f.write(f"BIAS ANALYSIS:\n")
            f.write(f"Bias Level: {bias.get('bias_level', 'Unknown')}\n")
            f.write(f"Bias Flags: {len(bias.get('bias_flags', []))}\n")
            f.write(f"Inclusive Indicators: {len(bias.get('inclusive_indicators', []))}\n\n")
            
            # Recommendations
            recommendations = report.get('recommendations', [])
            if recommendations:
                f.write("RECOMMENDATIONS:\n")
                for rec in recommendations:
                    f.write(f"- {rec}\n")
        
        logger.info(f"📄 Exported ATS report text to: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to export ATS report text: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the ATS analyzer
    logger.info("🧪 Testing ATSAnalyzer...")
    
    # Sample job for testing
    sample_job = {
        'title': 'IT Support Specialist',
        'description': 'Provide technical support for Windows and Linux systems. Experience with Active Directory, Office 365, and help desk tools required. Strong troubleshooting skills needed.',
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
            analyzer = ATSAnalyzer()
            report = analyzer.generate_ats_report(sample_job, test_resume)
            
            if 'error' not in report:
                print(f"✅ Test successful!")
                print(f"ATS Score: {report['ats_analysis']['ats_score']}%")
                print(f"Missing Keywords: {len(report['missing_keywords'])}")
                print(f"Bias Flags: {len(report['bias_analysis']['bias_flags'])}")
            else:
                print(f"⚠️ Test failed: {report['error']}")
        else:
            print("ℹ️ No resume files found for testing")
    else:
        print("ℹ️ Assets directory not found. Analyzer ready for use.") 
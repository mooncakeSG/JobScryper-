import re
import logging
from typing import List, Dict, Any
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobFilter:
    def __init__(self):
        # Define tech job categories and their keywords
        self.tech_keywords = {
            'it_support': {
                'primary': [
                    'it support', 'it specialist', 'technical support', 'help desk',
                    'helpdesk', 'desktop support', 'it technician', 'it analyst',
                    'computer support', 'technical specialist', 'it assistant',
                    'system support', 'user support', 'application support',
                    'ict support', 'ict technician', 'service desk'
                ],
                'secondary': [
                    'troubleshooting', 'hardware', 'software', 'networking',
                    'windows', 'microsoft', 'office 365', 'active directory',
                    'ticketing', 'remote support', 'onsite support',
                    'pc support', 'laptop support', 'printer support'
                ],
                'technical': [
                    'windows 10', 'windows 11', 'microsoft office', 'outlook',
                    'excel', 'word', 'powerpoint', 'azure', 'tcp/ip',
                    'vpn', 'firewall', 'antivirus', 'backup', 'imaging'
                ]
            },
            'software_developer': {
                'primary': [
                    'software developer', 'software engineer', 'programmer',
                    'full stack developer', 'frontend developer', 'backend developer',
                    'web developer', 'mobile developer', 'application developer',
                    'python developer', 'java developer', 'javascript developer',
                    'react developer', 'angular developer', 'vue developer'
                ],
                'secondary': [
                    'programming', 'coding', 'development', 'software',
                    'application', 'web', 'mobile', 'api', 'database',
                    'framework', 'library', 'version control', 'git'
                ],
                'technical': [
                    'python', 'java', 'javascript', 'react', 'angular', 'vue',
                    'node.js', 'php', 'c#', '.net', 'html', 'css', 'sql',
                    'mongodb', 'postgresql', 'mysql', 'aws', 'docker'
                ]
            },
            'data_science': {
                'primary': [
                    'data scientist', 'data analyst', 'machine learning engineer',
                    'data engineer', 'business intelligence analyst', 'analytics engineer',
                    'ml engineer', 'ai engineer', 'big data engineer', 'statistical analyst',
                    'bi analyst', 'bi developer', 'reporting analyst'
                ],
                'secondary': [
                    'data', 'analytics', 'machine learning', 'artificial intelligence',
                    'statistics', 'modeling', 'analysis', 'visualization',
                    'reporting', 'business intelligence', 'big data'
                ],
                'technical': [
                    'python', 'r', 'sql', 'pandas', 'numpy', 'scikit-learn',
                    'tensorflow', 'pytorch', 'tableau', 'power bi', 'spark',
                    'hadoop', 'kafka', 'airflow', 'jupyter', 'matplotlib'
                ]
            },
            'devops_cloud': {
                'primary': [
                    'devops engineer', 'cloud engineer', 'site reliability engineer',
                    'infrastructure engineer', 'platform engineer', 'cloud architect',
                    'aws engineer', 'azure engineer', 'gcp engineer', 'kubernetes engineer',
                    'docker engineer', 'ci/cd engineer', 'automation engineer'
                ],
                'secondary': [
                    'devops', 'cloud', 'infrastructure', 'deployment', 'automation',
                    'ci/cd', 'continuous integration', 'continuous deployment',
                    'monitoring', 'logging', 'scalability', 'reliability'
                ],
                'technical': [
                    'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'jenkins',
                    'terraform', 'ansible', 'chef', 'puppet', 'prometheus',
                    'grafana', 'elasticsearch', 'linux', 'bash', 'python'
                ]
            },
            'cybersecurity': {
                'primary': [
                    'cybersecurity analyst', 'security engineer', 'information security analyst',
                    'security architect', 'penetration tester', 'security consultant',
                    'incident response analyst', 'compliance analyst', 'risk analyst',
                    'security specialist', 'ethical hacker', 'security auditor'
                ],
                'secondary': [
                    'security', 'cybersecurity', 'information security', 'network security',
                    'application security', 'penetration testing', 'vulnerability assessment',
                    'incident response', 'compliance', 'risk management'
                ],
                'technical': [
                    'nessus', 'metasploit', 'wireshark', 'burp suite', 'kali linux',
                    'owasp', 'cissp', 'ceh', 'gsec', 'firewall', 'ids', 'ips',
                    'siem', 'splunk', 'qradar', 'iso 27001', 'nist'
                ]
            }
        }
        
        # Keywords that should exclude jobs (not IT support)
        self.exclude_keywords = [
            'software engineer', 'software developer', 'programmer',
            'data scientist', 'data analyst', 'web developer',
            'full stack', 'backend', 'frontend', 'devops',
            'machine learning', 'artificial intelligence', 'ai',
            'product manager', 'project manager', 'business analyst',
            'sales', 'marketing', 'hr', 'human resources',
            'accounting', 'finance', 'legal', 'attorney'
        ]
        
        # Location preferences (remote work indicators)
        self.remote_indicators = [
            'remote', 'work from home', 'wfh', 'telecommute',
            'distributed', 'virtual', 'anywhere', 'home office'
        ]
        
        # Experience level mapping
        self.experience_levels = {
            'entry': ['entry level', 'junior', '0-2 years', 'graduate', 'intern'],
            'mid': ['mid level', 'intermediate', '2-5 years', 'experienced'],
            'senior': ['senior', 'lead', '5+ years', 'expert', 'principal']
        }
    
    def filter_jobs(self, jobs: List[Dict[str, Any]], 
                   job_category: str = 'it_support',
                   min_score: float = 0.2,
                   max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Filter jobs based on tech category relevance
        
        Args:
            jobs: List of job dictionaries
            job_category: Tech category to filter for (it_support, software_developer, etc.)
            min_score: Minimum relevance score (0.0-1.0)
            max_results: Maximum number of results to return
            
        Returns:
            List of filtered jobs sorted by relevance score
        """
        logger.info(f"Filtering {len(jobs)} jobs for {job_category} relevance")
        
        filtered_jobs = []
        
        for job in jobs:
            # Calculate relevance score for the specific category
            score = self.calculate_relevance_score(job, job_category)
            
            # Check if job meets minimum score
            if score >= min_score:
                # Add score to job data
                job['relevance_score'] = score
                job['filter_reason'] = self.get_filter_reason(job, job_category)
                filtered_jobs.append(job)
            else:
                logger.debug(f"Job filtered out (score: {score:.2f}): {job.get('title', 'Unknown')}")
        
        # Sort by relevance score (descending)
        filtered_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Limit results
        if max_results:
            filtered_jobs = filtered_jobs[:max_results]
        
        logger.info(f"Filtered to {len(filtered_jobs)} relevant {job_category} jobs")
        return filtered_jobs
    
    def calculate_relevance_score(self, job: Dict[str, Any], job_category: str) -> float:
        """Calculate relevance score for a job in a specific category (0.0-1.0)"""
        try:
            if job_category not in self.tech_keywords:
                logger.warning(f"Unknown job category: {job_category}")
                return 0.0
            
            # Calculate component scores
            title_score = self.score_title(job.get('title', ''), job_category)
            description_score = self.score_description(job.get('description', ''), job_category)
            location_score = self.score_location(job.get('location', ''))
            company_score = self.score_company(job.get('company', ''))
            
            # Weighted final score
            final_score = (
                title_score * 0.4 +        # Title is most important
                description_score * 0.3 +  # Description is second
                location_score * 0.2 +     # Location preference
                company_score * 0.1        # Company relevance
            )
            
            return min(final_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.0
    
    def score_title(self, title: str, job_category: str) -> float:
        """Score job title for category relevance"""
        if not title or job_category not in self.tech_keywords:
            return 0.0
        
        title_lower = title.lower()
        score = 0.0
        keywords = self.tech_keywords[job_category]
        
        # Primary keywords (high weight)
        for keyword in keywords.get('primary', []):
            if keyword in title_lower:
                score += 0.8
        
        # Secondary keywords (medium weight)
        for keyword in keywords.get('secondary', []):
            if keyword in title_lower:
                score += 0.4
        
        # Technical keywords (lower weight)
        for keyword in keywords.get('technical', []):
            if keyword in title_lower:
                score += 0.2
        
        return min(score, 1.0)
    
    def score_description(self, description: str, job_category: str) -> float:
        """Score job description for category relevance"""
        if not description or job_category not in self.tech_keywords:
            return 0.0
        
        description_lower = description.lower()
        score = 0.0
        keyword_count = 0
        keywords = self.tech_keywords[job_category]
        
        # Count all relevant keywords
        all_keywords = (
            keywords.get('primary', []) +
            keywords.get('secondary', []) +
            keywords.get('technical', [])
        )
        
        for keyword in all_keywords:
            if keyword in description_lower:
                keyword_count += 1
                
                # Primary keywords get higher weight
                if keyword in keywords.get('primary', []):
                    score += 0.1
                else:
                    score += 0.05
        
        # Bonus for multiple keywords
        if keyword_count >= 5:
            score += 0.2
        elif keyword_count >= 3:
            score += 0.1
        
        return min(score, 1.0)
    
    def score_location(self, location: str) -> float:
        """Score location for remote work preference"""
        if not location:
            return 0.0
        
        location_lower = location.lower()
        score = 0.0
        
        # Check for remote indicators
        for indicator in self.remote_indicators:
            if indicator in location_lower:
                score += 0.3
        
        # South African locations get a slight boost
        if any(sa_term in location_lower for sa_term in [
            'south africa', 'cape town', 'johannesburg', 'durban',
            'eastern cape', 'western cape', 'gauteng'
        ]):
            score += 0.2
        
        return min(score, 1.0)
    
    def score_company(self, company: str) -> float:
        """Score company for tech relevance"""
        if not company:
            return 0.0
        
        company_lower = company.lower()
        score = 0.0
        
        # Tech company indicators
        tech_indicators = [
            'technology', 'software', 'systems', 'digital', 'tech',
            'data', 'cloud', 'cyber', 'ai', 'ml', 'analytics'
        ]
        
        for indicator in tech_indicators:
            if indicator in company_lower:
                score += 0.1
        
        return min(score, 1.0)
    
    def has_exclusion_keywords(self, text: str) -> bool:
        """Check if text contains keywords that should exclude the job"""
        text_lower = text.lower()
        
        for keyword in self.exclude_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def get_filter_reason(self, job: Dict[str, Any], job_category: str) -> str:
        """Get human-readable reason for why job was included"""
        reasons = []
        
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        
        if job_category in self.tech_keywords:
            keywords = self.tech_keywords[job_category]
            
            # Check primary keywords
            for keyword in keywords.get('primary', []):
                if keyword in title:
                    reasons.append(f"Title contains '{keyword}'")
                    break
            
            # Check for technical skills
            tech_found = []
            for keyword in keywords.get('technical', []):
                if keyword in description:
                    tech_found.append(keyword)
                    if len(tech_found) >= 3:
                        break
            
            if tech_found:
                reasons.append(f"Technical skills: {', '.join(tech_found[:3])}")
        
        return '; '.join(reasons) if reasons else 'General relevance'
    
    def filter_by_experience_level(self, jobs: List[Dict[str, Any]], 
                                  target_level: str) -> List[Dict[str, Any]]:
        """Filter jobs by experience level"""
        if target_level not in self.experience_levels:
            return jobs
        
        level_keywords = self.experience_levels[target_level]
        filtered_jobs = []
        
        for job in jobs:
            combined_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            
            # Check if any level keywords are present
            if any(keyword in combined_text for keyword in level_keywords):
                job['experience_level'] = target_level
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def filter_by_salary(self, jobs: List[Dict[str, Any]], 
                        min_salary: int = None, 
                        max_salary: int = None) -> List[Dict[str, Any]]:
        """Filter jobs by salary range"""
        filtered_jobs = []
        
        for job in jobs:
            salary_text = job.get('salary', '').lower()
            
            if not salary_text:
                # Include jobs without salary info
                filtered_jobs.append(job)
                continue
            
            # Extract salary numbers
            salary_numbers = re.findall(r'\$?(\d+)[k,]?', salary_text)
            
            if not salary_numbers:
                filtered_jobs.append(job)
                continue
            
            # Convert to integers (assume K for thousands)
            salaries = []
            for num in salary_numbers:
                try:
                    if 'k' in salary_text.lower():
                        salaries.append(int(num) * 1000)
                    else:
                        salaries.append(int(num))
                except ValueError:
                    continue
            
            if not salaries:
                filtered_jobs.append(job)
                continue
            
            # Check against min/max
            avg_salary = sum(salaries) / len(salaries)
            
            if min_salary and avg_salary < min_salary:
                continue
            if max_salary and avg_salary > max_salary:
                continue
            
            filtered_jobs.append(job)
        
        return filtered_jobs
    
    def get_filter_stats(self, original_jobs: List[Dict[str, Any]], 
                        filtered_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get filtering statistics"""
        return {
            'original_count': len(original_jobs),
            'filtered_count': len(filtered_jobs),
            'filter_rate': len(filtered_jobs) / len(original_jobs) if original_jobs else 0,
            'avg_score': sum(job.get('relevance_score', 0) for job in filtered_jobs) / len(filtered_jobs) if filtered_jobs else 0
        }

# Example usage
if __name__ == "__main__":
    # Sample job data
    sample_jobs = [
        {
            'title': 'IT Support Specialist',
            'company': 'Tech Solutions Inc',
            'location': 'Remote',
            'description': 'Provide technical support for Windows 10, Office 365, and troubleshooting hardware issues.',
            'salary': '$50,000 - $60,000'
        },
        {
            'title': 'Software Engineer',
            'company': 'StartupCorp',
            'location': 'San Francisco, CA',
            'description': 'Develop web applications using React and Node.js',
            'salary': '$120,000 - $150,000'
        },
        {
            'title': 'Help Desk Technician',
            'company': 'Healthcare Systems',
            'location': 'Chicago, IL',
            'description': 'Answer support tickets, troubleshoot PC issues, and provide phone support',
            'salary': '$40,000 - $45,000'
        }
    ]
    
    # Test filtering
    filter = JobFilter()
    filtered_jobs = filter.filter_jobs(sample_jobs)
    
    print(f"Original jobs: {len(sample_jobs)}")
    print(f"Filtered jobs: {len(filtered_jobs)}")
    
    for job in filtered_jobs:
        print(f"\nTitle: {job['title']}")
        print(f"Score: {job['relevance_score']:.2f}")
        print(f"Reason: {job['filter_reason']}")
    
    # Get statistics
    stats = filter.get_filter_stats(sample_jobs, filtered_jobs)
    print(f"\nFilter Statistics:")
    print(f"Filter rate: {stats['filter_rate']:.2%}")
    print(f"Average score: {stats['avg_score']:.2f}") 
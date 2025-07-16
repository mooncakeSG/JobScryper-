"""
Resume Parser Module for Auto Applier

This module extracts text from uploaded PDF and DOCX resume files
and prepares them for NLP similarity comparison with job descriptions.

Author: MooncakeSG 
Created: 2025-07-07
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    
try:
    import docx2txt
except ImportError:
    docx2txt = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    """
    A comprehensive resume parser that extracts text from PDF and DOCX files
    and prepares them for AI-powered job matching.
    """
    
    def __init__(self):
        """Initialize the resume parser with supported formats."""
        self.supported_formats = ['.pdf', '.docx', '.doc']
        self.extracted_sections = {}
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file using multiple fallback methods.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content
        """
        text_content = ""
        
        # Method 1: Try PyMuPDF (most reliable)
        if fitz:
            try:
                logger.info(f"Extracting PDF text using PyMuPDF: {file_path}")
                doc = fitz.open(file_path)
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text_content += page.get_text()
                doc.close()
                
                if text_content.strip():
                    logger.info(f"✅ Successfully extracted {len(text_content)} characters using PyMuPDF")
                    return text_content
                    
            except Exception as e:
                logger.warning(f"PyMuPDF extraction failed: {e}")
        
        # Method 2: Fallback to PyPDF2
        if PdfReader and not text_content.strip():
            try:
                logger.info(f"Fallback: Extracting PDF text using PyPDF2")
                with open(file_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text()
                        
                if text_content.strip():
                    logger.info(f"✅ Successfully extracted {len(text_content)} characters using PyPDF2")
                    return text_content
                    
            except Exception as e:
                logger.warning(f"PyPDF2 extraction failed: {e}")
        
        if not text_content.strip():
            logger.error(f"❌ Failed to extract text from PDF: {file_path}")
            
        return text_content
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path (str): Path to the DOCX file
            
        Returns:
            str: Extracted text content
        """
        text_content = ""
        
        # Method 1: Try docx2txt (recommended)
        if docx2txt:
            try:
                logger.info(f"Extracting DOCX text using docx2txt: {file_path}")
                text_content = docx2txt.process(file_path)
                
                if text_content.strip():
                    logger.info(f"✅ Successfully extracted {len(text_content)} characters from DOCX")
                    return text_content
                    
            except Exception as e:
                logger.warning(f"docx2txt extraction failed: {e}")
        
        if not text_content.strip():
            logger.error(f"❌ Failed to extract text from DOCX: {file_path}")
            
        return text_content
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text for better NLP processing.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace and normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-printable characters but keep essential punctuation
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        
        # Clean up common PDF artifacts
        text = re.sub(r'[•·▪▫◦‣⁃]', '•', text)  # Standardize bullet points
        text = re.sub(r'[""''‚„]', '"', text)   # Standardize quotes
        text = re.sub(r'[–—]', '-', text)       # Standardize dashes
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Clean up line breaks
        text = text.strip()
        
        return text
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common resume sections for better matching.
        
        Args:
            text (str): Cleaned resume text
            
        Returns:
            Dict[str, str]: Dictionary with extracted sections
        """
        sections = {
            'full_text': text,
            'skills': '',
            'experience': '',
            'education': '',
            'summary': '',
            'technical_skills': ''
        }
        
        # Convert to lowercase for pattern matching
        text_lower = text.lower()
        
        # Skills section patterns
        skills_patterns = [
            r'(?:technical\s+)?skills?[:\s]+(.*?)(?=\n\s*(?:experience|education|work|employment|projects|certifications)|$)',
            r'core\s+competencies[:\s]+(.*?)(?=\n\s*(?:experience|education|work|employment|projects)|$)',
            r'technologies[:\s]+(.*?)(?=\n\s*(?:experience|education|work|employment|projects)|$)'
        ]
        
        for pattern in skills_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['skills'] = match.group(1).strip()
                break
        
        # Experience section patterns
        experience_patterns = [
            r'(?:work\s+)?experience[:\s]+(.*?)(?=\n\s*(?:education|skills|projects|certifications)|$)',
            r'employment\s+history[:\s]+(.*?)(?=\n\s*(?:education|skills|projects)|$)',
            r'professional\s+experience[:\s]+(.*?)(?=\n\s*(?:education|skills|projects)|$)'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['experience'] = match.group(1).strip()
                break
        
        # Education section patterns
        education_patterns = [
            r'education[:\s]+(.*?)(?=\n\s*(?:experience|skills|projects|certifications)|$)',
            r'academic\s+background[:\s]+(.*?)(?=\n\s*(?:experience|skills|projects)|$)'
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['education'] = match.group(1).strip()
                break
        
        # Summary/Objective patterns
        summary_patterns = [
            r'(?:professional\s+)?summary[:\s]+(.*?)(?=\n\s*(?:experience|education|skills|work)|$)',
            r'objective[:\s]+(.*?)(?=\n\s*(?:experience|education|skills|work)|$)',
            r'profile[:\s]+(.*?)(?=\n\s*(?:experience|education|skills|work)|$)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            if match:
                sections['summary'] = match.group(1).strip()
                break
        
        # Extract IT-specific technical skills
        it_keywords = [
            'windows', 'linux', 'macos', 'active directory', 'office 365', 'azure',
            'aws', 'powershell', 'python', 'sql', 'networking', 'tcp/ip', 'dhcp',
            'dns', 'vpn', 'firewall', 'antivirus', 'backup', 'restore', 'ticketing',
            'itil', 'helpdesk', 'remote desktop', 'virtualization', 'vmware',
            'hyper-v', 'cisco', 'microsoft', 'exchange', 'sharepoint', 'teams'
        ]
        
        technical_skills = []
        for keyword in it_keywords:
            if keyword in text_lower:
                technical_skills.append(keyword)
        
        sections['technical_skills'] = ', '.join(technical_skills)
        
        return sections
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Main method to parse a resume file and extract all relevant information.
        
        Args:
            file_path (str): Path to the resume file
            
        Returns:
            Dict[str, Any]: Comprehensive resume data for matching
        """
        if not os.path.exists(file_path):
            logger.error(f"❌ Resume file not found: {file_path}")
            return {'error': f'File not found: {file_path}'}
        
        # Get file extension
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.supported_formats:
            logger.error(f"❌ Unsupported file format: {file_ext}")
            return {'error': f'Unsupported format: {file_ext}'}
        
        # Extract text based on file type
        raw_text = ""
        try:
            if file_ext == '.pdf':
                raw_text = self.extract_text_from_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                raw_text = self.extract_text_from_docx(file_path)
            
            if not raw_text.strip():
                logger.error(f"❌ No text could be extracted from: {file_path}")
                return {'error': 'No text extracted from file'}
            
            # Clean the text
            cleaned_text = self.clean_text(raw_text)
            
            # Extract sections
            sections = self.extract_sections(cleaned_text)
            
            # Prepare result
            result = {
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'file_type': file_ext,
                'raw_text_length': len(raw_text),
                'cleaned_text_length': len(cleaned_text),
                'sections': sections,
                'extracted_at': str(Path(file_path).stat().st_mtime),
                'success': True
            }
            
            logger.info(f"✅ Successfully parsed resume: {Path(file_path).name}")
            logger.info(f"📊 Extracted {len(cleaned_text)} characters with {len(sections)} sections")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error parsing resume {file_path}: {str(e)}")
            return {'error': f'Parsing failed: {str(e)}', 'file_path': file_path}
    
    def get_resume_for_matching(self, file_path: str) -> str:
        """
        Get clean resume text optimized for job matching algorithms.
        
        Args:
            file_path (str): Path to the resume file
            
        Returns:
            str: Clean text ready for TF-IDF vectorization
        """
        parsed_data = self.parse_resume(file_path)
        
        if 'error' in parsed_data:
            logger.error(f"Cannot get resume for matching: {parsed_data['error']}")
            return ""
        
        sections = parsed_data['sections']
        
        # Combine relevant sections for matching
        matching_text_parts = []
        
        # Add sections in order of importance for job matching
        if sections.get('technical_skills'):
            matching_text_parts.append(f"Technical Skills: {sections['technical_skills']}")
        
        if sections.get('skills'):
            matching_text_parts.append(f"Skills: {sections['skills']}")
        
        if sections.get('experience'):
            matching_text_parts.append(f"Experience: {sections['experience']}")
        
        if sections.get('summary'):
            matching_text_parts.append(f"Summary: {sections['summary']}")
        
        if sections.get('education'):
            matching_text_parts.append(f"Education: {sections['education']}")
        
        # If no sections found, use full text
        if not matching_text_parts:
            return sections.get('full_text', '')
        
        return ' '.join(matching_text_parts)

# Convenience function for direct usage
def parse_resume_file(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse a single resume file.
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        Dict[str, Any]: Parsed resume data
    """
    parser = ResumeParser()
    return parser.parse_resume(file_path)

def get_resume_text_for_matching(file_path: str) -> str:
    """
    Convenience function to get clean resume text for job matching.
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        str: Clean text ready for matching algorithms
    """
    parser = ResumeParser()
    return parser.get_resume_for_matching(file_path)

if __name__ == "__main__":
    # Test the resume parser
    parser = ResumeParser()
    
    # Test with a sample file (if available)
    test_file = "assets/resume_20250708_111036.pdf"
    if os.path.exists(test_file):
        result = parser.parse_resume(test_file)
        print("✅ Test Results:")
        print(f"Success: {result.get('success', False)}")
        print(f"Text Length: {result.get('cleaned_text_length', 0)}")
        print(f"Sections Found: {len(result.get('sections', {}))}")
    else:
        print("ℹ️  No test file found. Parser ready for use.") 
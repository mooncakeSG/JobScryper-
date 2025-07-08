# Auto Applyer - Architecture Overview

## System Architecture

Auto Applyer is a modern, AI-powered job search application built with a modular architecture that emphasizes scalability, maintainability, and user experience.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Module Architecture](#module-architecture)
6. [Design Patterns](#design-patterns)
7. [Security Architecture](#security-architecture)
8. [Performance Considerations](#performance-considerations)
9. [Scalability & Future Enhancements](#scalability--future-enhancements)

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│                  (Streamlit Frontend)                       │
├─────────────────────────────────────────────────────────────┤
│                  APPLICATION LAYER                          │
│           ┌─────────────┬─────────────┬─────────────┐       │
│           │Job Search   │Resume       │AI Assistant │       │
│           │Controller   │Controller   │Controller   │       │
│           └─────────────┴─────────────┴─────────────┘       │
├─────────────────────────────────────────────────────────────┤
│                    SERVICE LAYER                            │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │Job Scraping │Document     │AI/ML        │Data         │  │
│  │Services     │Processing   │Services     │Management   │  │
│  │             │Services     │             │Services     │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     DATA LAYER                              │
│    ┌─────────────┬─────────────┬─────────────────────┐      │
│    │Session      │File System  │External APIs        │      │
│    │Storage      │Storage      │(Groq, JobSpy, etc.)│      │
│    └─────────────┴─────────────┴─────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. User Interface Layer
- **Framework**: Streamlit
- **Components**: 
  - Navigation menu (`streamlit-option-menu`)
  - Job cards with actions
  - File upload widgets
  - Data visualization charts
  - Interactive forms

### 2. Application Controllers
- **Job Search Controller** (`app.py`): Handles job search workflow
- **Resume Controller** (`app.py`): Manages resume upload and analysis
- **AI Controller** (`app.py`): Coordinates AI-powered features

### 3. Service Layer

#### Job Scraping Services
- **JobSpy Wrapper** (`jobspy_wrapper.py`): Multi-platform job search
- **Alternative Sources** (`alternative_sources.py`): Additional job APIs
- **LinkedIn Bot** (`linkedin_bot.py`): LinkedIn-specific scraping
- **Indeed Scraper** (`indeed_scraper.py`): Indeed job search

#### Document Processing Services
- **Resume Parser** (`resume_parser.py`): Multi-format document parsing
- **ATS Analyzer** (`ats_report.py`): ATS compatibility analysis

#### AI/ML Services
- **Groq Integration** (`groq_resume_suggestion.py`): AI-powered suggestions
- **Job Matcher** (`matcher.py`): Resume-job compatibility scoring
- **Job Filter** (`filters.py`): Smart job categorization

#### Data Management Services
- **Session Management**: Streamlit session state
- **File Operations**: CSV export/import, resume storage
- **Application Tracking**: Job application history

## Data Flow

### Job Search Flow
```
User Input → Job Search Controller → Multiple Scrapers → Data Standardization → UI Display
     ↓
Job Cards → User Actions (Apply/Analyze) → Tracking/Analysis Services → Results Display
```

### Resume Analysis Flow
```
File Upload → Resume Parser → Text Extraction → AI Analysis → Suggestions Display
     ↓
Job Matching → ATS Analysis → Compatibility Scoring → Recommendations
```

### AI Assistant Flow
```
User Profile → AI Service (Groq) → Job Recommendations → Interview Tips → Downloadable Results
```

## Technology Stack

### Frontend
- **Streamlit**: Web application framework
- **streamlit-option-menu**: Enhanced navigation
- **streamlit-extras**: Additional UI components
- **HTML/CSS**: Custom styling and layouts

### Backend Services
- **Python 3.8+**: Core language
- **pandas**: Data manipulation and analysis
- **requests**: HTTP client for API calls
- **BeautifulSoup4**: HTML parsing
- **selenium**: Web automation
- **playwright**: Modern web automation

### AI & Machine Learning
- **Groq**: Fast AI inference service
- **transformers**: NLP model library
- **sentence-transformers**: Semantic similarity
- **scikit-learn**: Traditional ML algorithms
- **nltk**: Natural language processing

### Document Processing
- **PyMuPDF**: PDF processing
- **python-docx**: Word document handling
- **PyPDF2**: PDF text extraction

### Data Visualization
- **plotly**: Interactive charts
- **matplotlib**: Static plotting
- **seaborn**: Statistical visualization

## Module Architecture

### Core Modules

#### 1. Job Scraping Module
```python
# Abstract base for all job scrapers
class JobScraper:
    def search_jobs(self, criteria) -> List[Job]
    def parse_job_data(self, raw_data) -> Job
    def standardize_output(self, jobs) -> List[StandardJob]

# Implementations
- JobSpyWrapper
- RemoteOKScraper
- AdzunaAPIScraper
- JoobleAPIScraper
```

#### 2. Document Processing Module
```python
class DocumentProcessor:
    def parse_document(self, file_path) -> ParsedDocument
    def extract_text(self, document) -> str
    def identify_sections(self, text) -> Dict[str, str]
    def extract_metadata(self, document) -> Dict
```

#### 3. AI Services Module
```python
class AIService:
    def generate_suggestions(self, context) -> Suggestions
    def analyze_compatibility(self, job, resume) -> Score
    def detect_patterns(self, data) -> Insights
```

### Data Models

#### Job Model
```python
@dataclass
class Job:
    title: str
    company: str
    location: str
    description: str
    url: str
    salary: Optional[str]
    posted_date: str
    source: str
    remote: bool
    easy_apply: bool
    job_type: str
```

#### Resume Model
```python
@dataclass
class ParsedResume:
    raw_text: str
    cleaned_text: str
    sections: Dict[str, str]
    contact_info: Dict[str, str]
    skills: List[str]
    experience: List[Dict]
    education: List[Dict]
```

#### Analysis Model
```python
@dataclass
class ATSAnalysis:
    ats_score: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[str]
    bias_analysis: Dict
```

## Design Patterns

### 1. Factory Pattern
Used for creating different types of job scrapers:

```python
class JobScraperFactory:
    @staticmethod
    def create_scraper(source_type: str) -> JobScraper:
        if source_type == "jobspy":
            return JobSpyWrapper()
        elif source_type == "remoteok":
            return RemoteOKScraper()
        # ... other scrapers
```

### 2. Strategy Pattern
Different parsing strategies for various document formats:

```python
class ParsingStrategy:
    def parse(self, file_path: str) -> str: pass

class PDFParsingStrategy(ParsingStrategy): ...
class DOCXParsingStrategy(ParsingStrategy): ...
class TXTParsingStrategy(ParsingStrategy): ...
```

### 3. Observer Pattern
For updating UI components when data changes:

```python
class DataObserver:
    def update(self, data): pass

class JobSearchObserver(DataObserver): ...
class ApplicationTrackingObserver(DataObserver): ...
```

### 4. Decorator Pattern
For adding functionality like rate limiting and caching:

```python
@rate_limit(calls=10, period=60)
@cache_result(timeout=300)
def search_jobs(criteria):
    # Job search implementation
```

### 5. Command Pattern
For user actions like apply and analyze:

```python
class Command:
    def execute(self): pass

class ApplyToJobCommand(Command): ...
class AnalyzeJobCommand(Command): ...
```

## Security Architecture

### API Security
- **Environment Variables**: Secure API key storage
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Sanitize user inputs
- **Error Handling**: Don't expose sensitive information

### Data Security
- **Local Processing**: Resume data processed locally
- **Temporary Storage**: Minimal data persistence
- **Session Management**: Secure session handling
- **File Validation**: Verify uploaded file types

### Network Security
- **HTTPS**: Secure API communications
- **Request Timeouts**: Prevent hanging connections
- **User Agent Rotation**: Avoid detection as bot

## Performance Considerations

### Optimization Strategies

#### 1. Asynchronous Operations
```python
import asyncio
import aiohttp

async def fetch_jobs_async(sources):
    tasks = [fetch_from_source(source) for source in sources]
    results = await asyncio.gather(*tasks)
    return results
```

#### 2. Caching Layer
```python
from functools import lru_cache
import pickle
import os

@lru_cache(maxsize=100)
def cached_job_search(query_hash):
    # Cache expensive job search operations
```

#### 3. Lazy Loading
```python
class LazyJobLoader:
    def __init__(self):
        self._jobs = None
    
    @property
    def jobs(self):
        if self._jobs is None:
            self._jobs = self._load_jobs()
        return self._jobs
```

#### 4. Database Optimization
```python
# Future database implementation
class JobDatabase:
    def __init__(self):
        self.connection_pool = create_pool()
    
    def batch_insert_jobs(self, jobs):
        # Batch operations for better performance
```

### Performance Metrics

- **Job Search**: Target < 30 seconds
- **Resume Parsing**: Target < 5 seconds
- **AI Analysis**: Target < 10 seconds
- **Memory Usage**: Target < 1GB
- **UI Responsiveness**: Target < 2 seconds for interactions

## Scalability & Future Enhancements

### Horizontal Scaling Options

#### 1. Microservices Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Job       │    │   Resume    │    │     AI      │
│  Service    │    │  Service    │    │  Service    │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌─────────────┐
                    │   Gateway   │
                    │   Service   │
                    └─────────────┘
```

#### 2. Container Deployment
```dockerfile
# Future Docker implementation
FROM python:3.10-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

#### 3. Cloud Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │  Database   │
│  (Vercel)   │    │  (Railway)  │    │(PostgreSQL)│
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌─────────────┐
                    │   Redis     │
                    │   Cache     │
                    └─────────────┘
```

### Database Architecture (Future)

#### Schema Design
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Jobs table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    url VARCHAR(500),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Applications table
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    status VARCHAR(50),
    applied_at TIMESTAMP DEFAULT NOW()
);
```

### API Design (Future)

#### RESTful Endpoints
```python
# Future REST API design
@app.route('/api/v1/jobs/search', methods=['POST'])
def search_jobs():
    # Job search endpoint

@app.route('/api/v1/resume/analyze', methods=['POST'])
def analyze_resume():
    # Resume analysis endpoint

@app.route('/api/v1/applications', methods=['GET', 'POST'])
def handle_applications():
    # Application management endpoint
```

### Monitoring & Observability

#### Metrics Collection
```python
import prometheus_client

# Performance metrics
search_duration = prometheus_client.Histogram(
    'job_search_duration_seconds',
    'Time spent searching for jobs'
)

# Error tracking
error_counter = prometheus_client.Counter(
    'errors_total',
    'Total number of errors',
    ['error_type']
)
```

#### Logging Strategy
```python
import structlog

logger = structlog.get_logger()

def search_jobs(criteria):
    logger.info("Job search started", criteria=criteria)
    try:
        results = perform_search(criteria)
        logger.info("Job search completed", count=len(results))
        return results
    except Exception as e:
        logger.error("Job search failed", error=str(e))
        raise
```

## Integration Points

### External APIs
- **Groq AI**: Fast inference for AI features
- **JobSpy**: Multi-platform job aggregation
- **Adzuna**: Global job board API
- **Jooble**: Worldwide job search API

### File System
- **Assets Directory**: Resume uploads and static files
- **Reports Directory**: Generated analysis reports
- **Logs Directory**: Application logs and debugging

### Session Storage
- **Streamlit Session State**: Temporary data storage
- **Browser Storage**: User preferences (future)
- **Cache Layer**: Performance optimization (future)

---

This architecture provides a solid foundation for the current application while allowing for future growth and enhancement. The modular design ensures maintainability, and the planned scalability features will support larger user bases and more complex functionality.

---

*Last updated: July 8, 2025*
*Version: 1.0* 
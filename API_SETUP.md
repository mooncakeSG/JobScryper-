# Job Search API Setup Guide

This guide shows you how to set up additional job search APIs to enhance your job scraper's capabilities.

## Required APIs (Free Tiers Available)

### 1. GROQ API (AI Features)
- **Purpose**: AI resume analysis and job matching
- **Free tier**: Available
- **Setup**: https://console.groq.com/
- **Environment variable**: `GROQ_API_KEY`

### 2. Adzuna Jobs API
- **Purpose**: Global job search with 1000+ job boards
- **Free tier**: 1000 calls/month
- **Coverage**: US, UK, Australia, Canada, Germany, France, etc.
- **Setup**: https://developer.adzuna.com/
- **Environment variables**: 
  - `ADZUNA_APP_ID`
  - `ADZUNA_APP_KEY`

### 3. Jooble API
- **Purpose**: Global job aggregator
- **Free tier**: Available with registration
- **Coverage**: Worldwide
- **Setup**: https://jooble.org/api/about
- **Environment variable**: `JOOBLE_API_KEY`

## Optional APIs

### 4. The Muse API
- **Purpose**: Company culture and job search
- **Free tier**: 500 calls/day
- **Setup**: https://www.themuse.com/developers/api/v2
- **Environment variable**: `THE_MUSE_API_KEY`

### 5. USAJobs.gov API
- **Purpose**: US Government positions
- **Free tier**: Unlimited
- **Setup**: https://developer.usajobs.gov/
- **Environment variable**: `USAJOBS_API_KEY`

## Setup Instructions

1. **Create a `.env` file** in your project root
2. **Add your API keys** in this format:

```bash
# Required for AI features
GROQ_API_KEY=your_groq_api_key_here

# For enhanced job search
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_app_key_here
JOOBLE_API_KEY=your_jooble_api_key_here

# Optional APIs
THE_MUSE_API_KEY=your_muse_api_key_here
USAJOBS_API_KEY=your_usajobs_api_key_here
```

3. **Restart your application** after adding the keys

## Current Job Sources

### Working Without API Keys:
- **JobSpy**: LinkedIn, Indeed, ZipRecruiter, Glassdoor
- **RemoteOK**: Public API (no key needed)
- **AngelCo**: Web scraping
- **FlexJobs**: Curated sample data

### Enhanced With API Keys:
- **Adzuna**: Global job boards (1000+ sources)
- **Jooble**: Worldwide job aggregation
- **The Muse**: Company culture focus
- **USAJobs**: Government positions

## API Rate Limits

| API | Free Tier Limit | Rate Limit |
|-----|----------------|------------|
| GROQ | Available | As per plan |
| Adzuna | 1000 calls/month | 1 req/second |
| Jooble | Variable | 2 req/second |
| The Muse | 500 calls/day | As needed |
| USAJobs | Unlimited | As needed |
| RemoteOK | Unlimited | 2 req/second |

## Troubleshooting

- **"API credentials missing"**: Check your `.env` file and variable names
- **Rate limit errors**: The app handles this automatically with delays
- **No results**: Try different search terms or locations
- **Connection errors**: Check your internet connection and API status

## Support

- Check API documentation links above
- Verify your API keys are active
- Contact API providers for account issues 
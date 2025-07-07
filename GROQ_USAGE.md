# Groq AI Resume Suggestions - Usage Guide

## Overview

The Auto Applier now includes **AI-powered resume suggestions** using Groq's `meta-llama/llama-4-scout-17b-16e-instruct` model. This feature provides intelligent, actionable advice for optimizing your resume across various technology job categories including software development, data science, DevOps, cybersecurity, IT support, and more.

## Setup

### 1. Install Dependencies
```bash
pip install groq>=0.4.0
```

### 2. Set Up Groq API Key
Get your free API key from [Groq Console](https://console.groq.com/keys)

**Windows:**
```cmd
set GROQ_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY=your_api_key_here
```

**Alternative: Create `.env` file in project root:**
```
GROQ_API_KEY=your_api_key_here
```

## How to Use

### 1. Upload Your Resume
- Go to the **🤖 AI Tech Matching** tab
- Upload your resume (PDF or DOCX)
- The system will automatically parse your resume

### 2. Search for Jobs
- Select your preferred location (Eastern Cape, Cape Town, Johannesburg, or Remote for international)
- Choose your target tech job categories (software development, data science, DevOps, etc.)
- Enable "Include International Remote Jobs" for worldwide remote opportunities
- Use the AI-powered technology job search feature
- Jobs will be ranked by compatibility with your resume

### 3. Get AI Suggestions
- For any job card, click **"💡 Improve Resume for This Job"**
- Wait for AI analysis (typically 3-5 seconds)
- Review the comprehensive suggestions

### 4. Download Suggestions
- Click **"📥 Download Suggestions"** to save as TXT file
- Files are saved in the `reports/` directory

## What You Get

### 📝 Resume-Job Fit Summary
- Overall compatibility assessment
- Your key strengths for this specific role
- Professional alignment evaluation

### 🔍 Missing ATS Keywords
- 5-8 specific technical terms missing from your resume
- Prioritized for your selected tech role categories
- Direct from the job posting requirements

### 🚀 Resume Improvement Suggestions
- 4-6 actionable recommendations
- Content optimization advice
- Skills positioning guidance
- Experience presentation improvements

### 💼 Professional Advice
- ATS optimization tips
- Bias-free language recommendations
- Industry-specific formatting guidance

## Example Output

```
RESUME-JOB FIT SUMMARY:
Your resume shows strong foundational IT skills but lacks specific keywords 
like "Active Directory" and "ITIL" mentioned in this posting. Your help desk 
experience aligns well with the support role requirements.

MISSING ATS KEYWORDS:
• Active Directory • ITIL Framework • Office 365 Administration
• ServiceNow • VPN Configuration • Group Policy Management

RESUME IMPROVEMENT SUGGESTIONS:
1. Add specific Windows Server and Active Directory experience
2. Include ITIL certification or training in your qualifications
3. Highlight Office 365 administration skills prominently
4. Quantify your help desk metrics (tickets resolved, response times)
```

## Features

### ✅ AI-Powered Analysis
- Uses Groq's fast inference for real-time suggestions
- Llama 4 Scout model optimized for professional guidance
- Context-aware recommendations

### ✅ IT Support Focus
- Specialized for IT Support and Help Desk roles
- Industry-specific keyword optimization
- Technical skills alignment

### ✅ Actionable Insights
- Specific, implementable recommendations
- No generic advice - tailored to each job posting
- Professional language improvements

### ✅ Export & Save
- Download suggestions as formatted text files
- Organized file naming with timestamps
- Easy to reference during resume editing

## Technical Details

### Model: `meta-llama/llama-4-scout-17b-16e-instruct`
- **Speed**: ~3-5 seconds per analysis
- **Quality**: Professional-grade suggestions
- **Cost**: Free tier available from Groq

### Token Usage
- **Input**: Resume + Job description (optimized for <4000 tokens)
- **Output**: Structured suggestions (~1000-1500 tokens)
- **Efficiency**: Groq's optimized inference reduces costs

### Error Handling
- Graceful fallback if API key not configured
- Clear error messages for troubleshooting
- Resume parsing continues even if AI suggestions fail

## Troubleshooting

### "No GROQ_API_KEY found"
- Set the environment variable with your API key
- Restart your terminal/command prompt
- Check that the key is valid in Groq Console

### "Failed to generate suggestions"
- Check your internet connection
- Verify API key is correct and not expired
- Try again - temporary API issues are rare

### "Resume text is empty"
- Ensure your resume uploaded successfully
- Check that the file is a valid PDF or DOCX
- Try re-uploading the resume

## Best Practices

### 1. Review Multiple Jobs
- Generate suggestions for 3-5 similar positions
- Look for common missing keywords across suggestions
- Prioritize improvements that appear frequently

### 2. Implement Gradually
- Start with the most impactful suggestions
- Test ATS compatibility with online tools
- Update one section at a time

### 3. Keep Context
- Save suggestions files for reference
- Compare before/after ATS scores
- Track which improvements worked best

## Privacy & Security

- Resume text is processed securely through Groq API
- No data is stored on Groq servers after processing
- All suggestions are saved locally in your `reports/` folder
- Your API key never leaves your environment

## Support

For issues or questions:
1. Check this documentation
2. Verify your API key setup
3. Review the console logs for error details
4. Try the test mode in `groq_resume_suggestion.py`

---

**Ready to optimize your resume with AI?** 🚀

Upload your resume, select your location (South Africa or Remote), choose your tech job categories, and click "💡 Improve Resume for This Job" to get started!

**Perfect for:**
- 🇿🇦 Tech professionals in South Africa (especially Eastern Cape)
- 🌍 Job seekers targeting international remote opportunities  
- 💼 Anyone optimizing resumes for global tech markets 
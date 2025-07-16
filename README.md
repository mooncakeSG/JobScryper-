# Auto Apply for IT Jobs

A comprehensive Streamlit web application that automatically searches and applies for IT support jobs from multiple sources including Indeed and LinkedIn.

## 🚀 Features

- **Multi-source job search**: Simultaneously search Indeed and LinkedIn for IT support positions
- **Smart filtering**: Automatically filters for IT Support, Helpdesk, and Desktop Support roles using AI-powered relevance scoring
- **Auto-apply functionality**: Automatically apply to LinkedIn Easy Apply jobs with your uploaded resume
- **Application tracking**: Keep track of all your applications in one centralized location
- **Resume management**: Upload and store your resume securely
- **Beautiful UI**: Modern, responsive interface with expandable job cards
- **Real-time progress**: Live updates during job searches and applications

## 📋 Project Structure

```
Auto Applyer/
├── app.py                  # Main Streamlit application
├── indeed_scraper.py       # Indeed job scraper using BeautifulSoup
├── linkedin_bot.py         # LinkedIn job search using Playwright
├── apply.py                # Auto-apply functionality using Playwright
├── filters.py              # Job filtering logic for IT support roles
├── setup.py                # Automated setup script
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── assets/                 # Folder for uploaded resumes
└── applications.csv        # Application tracking (created automatically)
```

## 🛠️ Installation

### Development Setup (Local)

1. **Download/Clone the Project**
2. **Run the Setup Script**:
   ```bash
   python setup.py
   ```
   This will automatically:
   - Check your Python version
   - Install all dependencies
   - Install Playwright browsers
   - Create necessary directories
   - Test the installation

### Production Setup (SQLite Cloud)

For production deployment with SQLite Cloud:

1. **Follow the SQLite Cloud Setup Guide**:
   ```bash
   # Read the comprehensive setup guide
   cat SQLITE_CLOUD_SETUP.md
   ```

2. **Configure Production Environment**:
   ```bash
   # Copy and configure production environment
   cp production.env.example .env.production
   # Edit .env.production with your SQLite Cloud credentials
   ```

3. **Deploy to Production**:
   ```bash
   # Run the automated deployment script
   python scripts/deploy_production.py
   ```

4. **Validate Setup**:
   ```bash
   # Validate SQLite Cloud configuration
   python scripts/validate_sqlite_cloud.py
   ```

### Manual Installation

If you prefer to install manually:

#### Prerequisites
- Python 3.8 or higher
- pip package manager

#### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Install Playwright Browsers
```bash
playwright install
```

#### Step 3: Create Assets Directory
```bash
mkdir assets
```

### Common Installation Issues

#### Windows Users (Python 3.13)
If you encounter Playwright errors:
```bash
pip install playwright
playwright install
```

#### Indeed 403 Errors
- This is normal - Indeed blocks automated requests
- Sample data is provided for testing
- Try LinkedIn search instead

#### Playwright Not Working
```bash
playwright install --with-deps
```

## 🚀 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Configuration

1. **Job Search Settings**:
   - Enter your desired job title (e.g., "IT Support", "Helpdesk", "Desktop Support")
   - Specify location (city, state, or "Remote")

2. **LinkedIn Credentials**:
   - Enter your LinkedIn email and password
   - These are only stored in your browser session and used for auto-apply functionality

3. **Resume Upload**:
   - Upload your resume in PDF or DOCX format
   - The file will be stored in the `assets/` folder with a timestamp

### Job Search Process

1. **Search Jobs**:
   - Select which sources to search (Indeed, LinkedIn, or both)
   - Click "Search Jobs" to start the process
   - View real-time progress as jobs are scraped and filtered

2. **Review Results**:
   - Jobs are displayed in expandable cards
   - Each job shows title, company, location, salary (if available), and description
   - Jobs are automatically scored for relevance to IT support roles

3. **Auto Apply**:
   - Click "Auto Apply" on LinkedIn jobs (Easy Apply only)
   - The system will automatically log into LinkedIn, navigate to the job, and submit your application
   - Applications are tracked in the "Applications" tab

### Application Tracking

- View all your applications in the "Applications" tab
- Filter by company, status, or date
- Export your application history as CSV
- Track daily and total application counts

## 🔧 Technical Details

### Job Filtering Algorithm

The application uses a sophisticated scoring system to identify relevant IT support jobs:

- **Primary Keywords**: IT Support, Helpdesk, Desktop Support, Technical Support
- **Secondary Keywords**: Troubleshooting, Hardware, Software, Windows, Microsoft
- **Technical Keywords**: Office 365, Active Directory, TCP/IP, VPN
- **Certifications**: CompTIA A+, Network+, Security+, Microsoft Certified

Jobs are scored based on:
- Title relevance (40% weight)
- Description keywords (30% weight)
- Location preference (20% weight)
- Company relevance (10% weight)

### Auto-Apply Process

The auto-apply feature handles:
- LinkedIn login and authentication
- Job page navigation
- Form field completion (contact info, work authorization, etc.)
- Resume upload
- Multi-step application processes
- Success/failure tracking

### Data Storage

- **Applications**: Stored in `applications.csv` with columns for job title, company, location, date, status, and URL
- **Resumes**: Stored in `assets/` folder with timestamps
- **Session Data**: Temporary storage in Streamlit session state

## ⚠️ Important Notes

### Terms of Service Compliance

- **Respect Rate Limits**: The application includes delays between requests to avoid overwhelming job sites
- **LinkedIn Terms**: Auto-apply functionality is for personal use only and should comply with LinkedIn's terms of service
- **Be Respectful**: Don't spam applications - review job requirements before applying

### Privacy and Security

- **Credentials**: LinkedIn credentials are only stored in your browser session
- **Resume Data**: Files are stored locally in the `assets/` folder
- **No Data Sharing**: No personal information is shared with third parties

### Limitations

- **LinkedIn Easy Apply Only**: Auto-apply works only for LinkedIn jobs marked as "Easy Apply"
- **Captcha Challenges**: Manual intervention may be required for security challenges
- **Site Changes**: Web scrapers may need updates if job sites change their structure

## 🐛 Troubleshooting

### Common Issues

1. **Playwright Installation Issues**:
   ```bash
   playwright install --with-deps
   ```

2. **LinkedIn Login Failures**:
   - Check your credentials
   - Ensure two-factor authentication is disabled or handled manually
   - Clear browser cache if using non-headless mode

3. **No Jobs Found**:
   - Try broader search terms
   - Check if job sites are accessible
   - Verify your internet connection

4. **Application Failures**:
   - Ensure your resume is in PDF or DOCX format
   - Check LinkedIn for any account restrictions
   - Verify that jobs are actually "Easy Apply" eligible

### Debug Mode

To run in debug mode (non-headless browser):
```python
# In apply.py, change:
auto_apply = AutoApply(email, password, resume_path, headless=False)
```

### Logs

Check the console output for detailed logs about the scraping and application process.

## 📊 Performance

- **Search Speed**: ~2-3 minutes for 100 jobs across both platforms
- **Application Speed**: ~30-60 seconds per LinkedIn application
- **Success Rate**: ~85% for standard Easy Apply jobs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/yourusername/auto-apply-it-jobs/issues)
- **Documentation**: Check this README for comprehensive usage instructions
- **Community**: Join discussions in the repository's Discussions tab

## 🎯 Future Enhancements

- [ ] Support for more job boards (Monster, CareerBuilder, etc.)
- [ ] Advanced filtering options (salary range, experience level)
- [ ] Email notifications for application status
- [ ] Integration with ATS systems
- [ ] Chrome extension for one-click applications
- [ ] Mobile app version

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Playwright](https://playwright.dev/) for browser automation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for web scraping
- [Pandas](https://pandas.pydata.org/) for data manipulation

---

**Disclaimer**: This tool is for educational and personal use only. Always review job requirements before applying and ensure your applications are relevant and thoughtful. Respect the terms of service of all job platforms. 
# Resume Evaluation System

A web-based AI system that automatically evaluates resumes against job requirements and provides detailed analysis for HR teams and placement coordinators.

## What This System Does

This system helps HR teams and placement officers by:
- **Automatically scoring resumes** against job descriptions (0-100%)
- **Identifying missing skills** that candidates need to develop
- **Generating detailed feedback** about candidate strengths and weaknesses
- **Providing search and analytics** to find the best candidates quickly
- **Managing job applications** through a clean web interface

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Core Engine    │    │   Data Storage  │
│                 │    │                 │    │                 │
│ • Student Forms │◄──►│ • Text Analysis │◄──►│ • Job Database  │
│ • Admin Panel   │    │ • AI Evaluation │    │ • Resume Store  │
│ • Analytics     │    │ • Scoring Logic │    │ • Results Cache │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

1. **Web Interface (Streamlit)**
   - Student application portal
   - Admin dashboard for reviewing applications
   - Analytics and reporting tools

2. **Document Processing**
   - Extracts text from PDF and DOCX files
   - Parses job descriptions and resumes
   - Identifies skills, experience, and qualifications

3. **AI Evaluation Engine**
   - Compares resumes against job requirements
   - Calculates relevance scores
   - Generates improvement suggestions

4. **Database Layer**
   - Stores jobs, resumes, and evaluations
   - Tracks application status
   - Maintains historical data for analytics

## Key Features

### For Students
- **Easy Application**: Upload resume and apply to available positions
- **Instant Feedback**: Get immediate evaluation of resume relevance
- **Skill Insights**: Understand which skills are missing or need improvement

### For HR/Admin Teams
- **Application Management**: Review all student applications in one place
- **AI-Powered Scoring**: Get objective evaluation scores for each candidate
- **Detailed Analysis**: See exactly why candidates scored high or low
- **Search & Filter**: Find candidates by skills, scores, or other criteria
- **Export Reports**: Download evaluation results for further analysis

### For Placement Teams
- **Advanced Dashboard**: Specialized view for placement coordinators
- **Bulk Operations**: Export shortlisted candidates to CSV
- **Skills Matching**: Find candidates with specific skill combinations
- **Analytics**: Track placement success rates and trends

## Technical Requirements

### Software Dependencies
- Python 3.8 or higher
- 500MB free disk space
- Internet connection (for AI features)

### Optional AI Enhancement
- OpenAI API key (for advanced analysis)
- Enhances evaluation quality but system works without it

## Deployment Options

### Local Development
```bash
streamlit run app/web/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

### Streamlit Cloud Deployment

This application is ready for deployment on Streamlit Cloud. Follow these steps:

#### 1. Prepare Your Repository
- Push your code to GitHub
- Ensure `streamlit_app.py` is in the root directory (✅ already included)
- Verify `requirements.txt` has pinned versions (✅ already optimized)

#### 2. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `sahilhsanas22/Automated-Resume-Relevance-Check-System`
5. Choose branch: `main`
6. Main file path: `streamlit_app.py`
7. Click "Deploy!"

#### 3. Configure Secrets (Optional)
For enhanced AI features, add these secrets in your Streamlit Cloud app settings:

```toml
# In Streamlit Cloud app settings > Secrets
OPENAI_API_KEY = "your_openai_api_key_here"
ADMIN_USERNAME = "your_admin_username"  
ADMIN_PASSWORD = "your_secure_password"
```

#### 4. App Configuration
The app includes optimized settings for cloud deployment:
- ✅ Cloud-optimized server settings
- ✅ File upload limits configured
- ✅ Error handling for missing dependencies
- ✅ Graceful fallback when AI APIs unavailable

#### 5. Expected Build Time
- Initial deployment: 5-10 minutes
- Subsequent updates: 2-3 minutes
- The app will work even if some AI packages fail to install

#### 6. Monitoring Your Deployment
- Check deployment logs in Streamlit Cloud dashboard
- Monitor app performance and usage
- Update secrets as needed without redeployment

### Troubleshooting Cloud Deployment

**Build fails with package errors:**
- Some ML packages might fail on Streamlit Cloud's free tier
- The app is designed to work with graceful fallbacks
- Core functionality will still work

**App loads slowly:**
- First load takes longer due to model downloads
- Subsequent loads are faster
- Consider upgrading to Streamlit Cloud Pro for better performance

**Memory issues:**
- Reduce model sizes in configuration
- Clear browser cache and restart app
- Monitor resource usage in Streamlit Cloud dashboard

## Installation & Setup

### 1. Download and Setup
```bash
# Download the system
git clone [repository-url]
cd Resume

# Create isolated environment
python -m venv .venv

# Activate environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configuration (Optional)
Create a `.env` file for enhanced AI features:
```
OPENAI_API_KEY=your_api_key_here
```

### 3. Run the System
```bash
streamlit run app/web/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Open your browser and go to: `http://127.0.0.1:8501`

## How to Use

### Setting Up Jobs (Admin)
1. Log in as admin (default: admin/admin)
2. Go to "Manage Jobs" 
3. Add job descriptions by:
   - Uploading PDF/DOCX files, or
   - Pasting job text directly
4. Let AI suggest required skills or add them manually
5. Save the job posting

### Student Applications
1. Students visit the main page
2. Select an available job position
3. Fill out application form
4. Upload their resume (PDF/DOCX)
5. Submit application
6. Get instant evaluation results

### Reviewing Applications (Admin)
1. Go to "Review Applications"
2. See all applications with AI scores
3. Review detailed analysis for each candidate
4. Update application status (pending/reviewed/accepted/rejected)
5. Export results for further processing

### Analytics & Reports
1. Visit "Analytics Dashboard"
2. View score distributions and trends
3. Filter by job, score range, or location
4. Export filtered results to CSV
5. Track system performance over time

## Understanding the Evaluation

### Scoring System
- **0-49%**: Low relevance - significant skill gaps
- **50-74%**: Medium relevance - some missing skills
- **75-100%**: High relevance - strong match

### What Gets Analyzed
- **Technical Skills**: Programming languages, tools, frameworks
- **Experience Level**: Years of experience in relevant fields
- **Education**: Degrees, certifications, relevant coursework
- **Keywords**: Industry-specific terms and buzzwords

### AI Features
- **With API Key**: Advanced semantic analysis, detailed feedback
- **Without API Key**: Still provides good keyword-based evaluation

## File Organization

```
Resume/
├── app/
│   ├── web/              # Web interface (Streamlit)
│   ├── db/               # Database models and operations
│   ├── nlp/              # Text analysis and AI logic
│   ├── parsing/          # Document text extraction
│   └── services/         # Core evaluation engine
├── data/                 # Database files (auto-created)
├── requirements.txt      # Required Python packages
└── README.md            # This documentation
```

## Troubleshooting

### Common Issues

**"Module not found" errors**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**"Permission denied" when uploading files**
- Check file permissions
- Ensure files are not open in other programs

**Low evaluation scores**
- Check if job requirements are properly configured
- Ensure resumes contain relevant keywords
- Verify file text extraction worked correctly

**Slow performance**
- Large PDF files take longer to process
- Consider breaking down complex job descriptions
- Check internet connection for AI features

### Getting Help
1. Check the terminal/console for error messages
2. Verify all requirements are installed correctly
3. Ensure Python version compatibility (3.8+)
4. Check file formats are supported (PDF, DOCX only)

## System Limits

- **File Size**: Maximum 10MB per upload
- **Supported Formats**: PDF and DOCX only
- **Concurrent Users**: Designed for small-medium teams (10-50 users)
- **Storage**: Local SQLite database (suitable for thousands of records)

## Security Notes

- System runs locally by default (127.0.0.1)
- No data is sent to external services (except OpenAI if API key provided)
- Files are stored locally on your machine
- Default admin credentials should be changed for production use

## Future Enhancements

- Integration with popular HR systems
- Bulk resume processing
- Advanced reporting templates
- Mobile-responsive design improvements
- Multi-language support
- Custom scoring criteria configuration

---

**This system is ready to use immediately and can significantly improve your resume screening process while saving time for HR teams and providing valuable feedback to candidates.**

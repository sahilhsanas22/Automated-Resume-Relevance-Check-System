import sys
import os

# Add the project root to Python path if not already there
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.database import SessionLocal
from app.db import models, crud
from app.parsing.files import extract_text
from app.parsing.jd_parser import parse_jd_freeform
from app.nlp.skills import extract_candidate_skills
from app.services.evaluator import evaluate_resume_against_job
from app.services.llm_evaluator import llm_evaluator
from app.nlp.advanced_processor import text_processor
from app.config import APP_NAME
from app.auth import show_login_form, is_authenticated, show_logout_button, require_auth

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Ensure models are imported so tables are created
_ = models

# Beautiful Dark Theme UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        font-family: 'Inter', sans-serif;
    }
    
    /* Main content area with dark background */
    .main .block-container {
        background: rgba(30, 30, 46, 0.95);
        border-radius: 15px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        padding: 2rem;
        margin: 1rem;
        max-width: 1200px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Headers with white text */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #b8c5d6;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
        font-family: 'Inter', sans-serif;
    }
    
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: white;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sleek admin login card */
    .admin-login-section {
        background: rgba(45, 45, 65, 0.9);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.4);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        margin: 1rem 0;
        backdrop-filter: blur(15px);
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .student-form-section {
        background: rgba(45, 45, 65, 0.8);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Dark form inputs */
    .stTextInput > div > div > input {
        background-color: rgba(60, 60, 80, 0.8) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-family: 'Inter', sans-serif !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        background-color: rgba(70, 70, 90, 0.9) !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: rgba(60, 60, 80, 0.8) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-family: 'Inter', sans-serif !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        background-color: rgba(70, 70, 90, 0.9) !important;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(60, 60, 80, 0.8) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Beautiful gradient buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #667eea !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Sleek dark sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
        border-right: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white !important;
    }
    
    /* Dark metric cards */
    .metric-card {
        background: rgba(45, 45, 65, 0.8);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        color: white;
    }
    
    /* Dark alert boxes */
    .success-box {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.2) 0%, rgba(32, 201, 151, 0.2) 100%);
        color: #4ade80;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #22c55e;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(10px);
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(255, 152, 0, 0.2) 100%);
        color: #fbbf24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(10px);
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(23, 162, 184, 0.2) 0%, rgba(102, 126, 234, 0.2) 100%);
        color: #60a5fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(10px);
    }
    
    /* Glowing score indicators */
    .score-high {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4);
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .score-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .score-low {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Dark expanders */
    .streamlit-expanderHeader {
        background: rgba(60, 60, 80, 0.6) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        color: white !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* All text white */
    .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div {
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Form labels white */
    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: white !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Dark tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: rgba(60, 60, 80, 0.6);
        border-radius: 8px;
        color: white;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Dark metrics */
    .stMetric {
        background: rgba(45, 45, 65, 0.8);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border-left: 4px solid #667eea;
        color: white;
    }
    
    .stMetric > div {
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Dark alert styling */
    .stAlert > div {
        background: rgba(45, 45, 65, 0.8);
        border-radius: 8px;
        border: none;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        font-family: 'Inter', sans-serif;
        color: white;
        backdrop-filter: blur(10px);
    }
    
    /* Success alerts */
    .stAlert[data-testid="success"] > div {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.2) 0%, rgba(32, 201, 151, 0.2) 100%);
        border-left: 4px solid #22c55e;
        color: #4ade80;
    }
    
    /* Error alerts */
    .stAlert[data-testid="error"] > div {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border-left: 4px solid #ef4444;
        color: #fb7185;
    }
    
    /* Warning alerts */
    .stAlert[data-testid="warning"] > div {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%);
        border-left: 4px solid #f59e0b;
        color: #fbbf24;
    }
    
    /* Info alerts */
    .stAlert[data-testid="info"] > div {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(102, 126, 234, 0.2) 100%);
        border-left: 4px solid #3b82f6;
        color: #60a5fa;
    }
    
    /* Dark file uploader */
    .stFileUploader > div {
        background: rgba(60, 60, 80, 0.6);
        border: 2px dashed #667eea;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        color: white;
    }
    
    /* Dark progress bars */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sleek sidebar navigation */
    .css-1d391kg .element-container {
        color: white !important;
    }
    
    .css-1d391kg .stRadio > label {
        color: white !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 0 !important;
    }
    
    .css-1d391kg .stRadio > div > div {
        background: rgba(60, 60, 80, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        margin: 0.2rem 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .css-1d391kg .stRadio > div > div:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        transform: translateX(5px) !important;
    }
    
    .css-1d391kg .stMarkdown {
        color: white !important;
    }
    
    .css-1d391kg .stMarkdown h3 {
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Ensure all text is white in main content */
    .stApp .main .block-container h1,
    .stApp .main .block-container h2,
    .stApp .main .block-container h3,
    .stApp .main .block-container h4,
    .stApp .main .block-container h5,
    .stApp .main .block-container h6,
    .stApp .main .block-container p,
    .stApp .main .block-container span,
    .stApp .main .block-container div {
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Dark DataFrames */
    .stDataFrame {
        background: rgba(45, 45, 65, 0.8);
        border-radius: 8px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        overflow: hidden;
        color: white;
    }
    
    /* Dark charts */
    .stPlotlyChart {
        background: rgba(45, 45, 65, 0.8);
        border-radius: 8px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        padding: 1rem;
    }
    
    /* Selectbox options dark theme */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(60, 60, 80, 0.8) !important;
        color: white !important;
    }
    
    /* Radio buttons dark theme */
    .stRadio > div {
        color: white !important;
    }
    
    /* Checkbox dark theme */
    .stCheckbox > label {
        color: white !important;
    }
    
    /* Sleek top navigation buttons */
    .stButton > button[kind="secondary"] {
        background: rgba(60, 60, 80, 0.6) !important;
        color: #667eea !important;
        border: 1px solid rgba(102, 126, 234, 0.4) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Compact login form styling */
    .admin-login-section .stButton > button {
        font-size: 0.9rem !important;
        padding: 0.6rem 1.2rem !important;
    }
    
    .admin-login-section .stTextInput > div > div > input {
        padding: 0.6rem !important;
        font-size: 0.9rem !important;
    }
    
    .admin-login-section .section-header {
        font-size: 1.2rem !important;
        margin: 0 0 1rem 0 !important;
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

def page_landing():
    """Clean landing page with clear login/student sections"""
    st.markdown('<h1 class="main-header">AI Resume Evaluation System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Smart Resume Analysis & Job Matching Platform</p>', unsafe_allow_html=True)
    
    # Simple login button at top right
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col4:
        if st.button("🔐 Admin Login", type="secondary", use_container_width=True):
            st.session_state.show_admin_login = True
            st.rerun()
    
    # Show admin login form if requested
    if st.session_state.get('show_admin_login', False) and not is_authenticated():
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="admin-login-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">🔐 Admin Login</h3>', unsafe_allow_html=True)
            
            login_result = show_login_form()
            if login_result:
                st.session_state.show_admin_login = False
                st.session_state.page = "admin_dashboard"
                st.rerun()
            
            if st.button("❌ Cancel", type="secondary", use_container_width=True):
                st.session_state.show_admin_login = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
    
    # Main student application section - always visible, but cleaner presentation
    if not st.session_state.get('show_admin_login', False):
        st.markdown("---")
        st.markdown('<div class="student-form-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">🎓 Student Application Portal</h2>', unsafe_allow_html=True)
        st.info("📋 Apply for available positions by uploading your resume and get instant AI-powered feedback!")
        page_student_application()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("---")
        st.info("💡 Complete the admin login above or cancel to access the student application portal.")

def page_student_application():
    """Professional student application form with resume upload and analysis"""
    # Get available jobs
    with SessionLocal() as db:
        jobs = crud.list_jobs(db)
    
    if not jobs:
        st.warning("No job openings available at the moment. Please check back later.")
        return
    
    # Job selection
    st.markdown("### Available Positions")
    job_options = {f"{job.title} - {job.location}" if job.location else job.title: job.id for job in jobs}
    selected_job_label = st.selectbox("Select Job Position", list(job_options.keys()))
    selected_job_id = job_options[selected_job_label]
    
    # Show selected job details
    selected_job = next(j for j in jobs if j.id == selected_job_id)
    with st.expander("View Job Requirements", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            must_skills = json.loads(selected_job.must_skills_json or '[]')
            st.markdown("**Required Skills:**")
            for skill in must_skills:
                st.markdown(f"• {skill}")
        with col_b:
            nice_skills = json.loads(selected_job.nice_skills_json or '[]')
            st.markdown("**Preferred Skills:**")
            for skill in nice_skills:
                st.markdown(f"• {skill}")
        
        if selected_job.qualifications:
            st.markdown("**Qualifications:**")
            st.text(selected_job.qualifications)
    
    # Application form
    st.markdown("### Application Form")
    with st.form("student_application_form"):
        # Personal information
        st.markdown("**Personal Information**")
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Full Name *", placeholder="Enter your full name")
            email = st.text_input("Email Address *", placeholder="your.email@example.com")
        with col2:
            phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
            location = st.text_input("Location", placeholder="City, Country")
        
        # Resume upload
        st.markdown("**Resume Upload**")
        uploaded_resume = st.file_uploader(
            "Upload your resume (PDF/DOCX) *",
            type=["pdf", "docx"],
            help="Please upload your latest resume for analysis"
        )
        
        # Cover letter
        st.markdown("**Cover Letter (Optional)**")
        cover_letter = st.text_area(
            "Tell us why you're interested in this position",
            placeholder="Write your cover letter here...",
            height=120
        )
        
        # Submit button
        submit_application = st.form_submit_button("Submit Application", type="primary", use_container_width=True)
        
        if submit_application:
            if not all([student_name, email, uploaded_resume]):
                st.error("Please fill in all required fields (Name, Email, Resume)")
            else:
                try:
                    # Extract text from resume
                    content = uploaded_resume.read()
                    resume_text, ext = extract_text(content, uploaded_resume.name)
                    
                    # Create application in database
                    with SessionLocal() as db:
                        application = crud.create_student_application(
                            db=db,
                            job_id=selected_job_id,
                            student_name=student_name,
                            email=email,
                            phone=phone,
                            location=location,
                            resume_file_name=uploaded_resume.name,
                            resume_text=resume_text,
                            cover_letter=cover_letter
                        )
                        
                        # Perform AI analysis for admin dashboard
                        try:
                            # Create temporary resume record for analysis
                            temp_resume = crud.create_resume(
                                db=db,
                                student_name=student_name,
                                file_name=uploaded_resume.name,
                                text=resume_text,
                                location=location
                            )
                            
                            # Run evaluation
                            evaluation = evaluate_resume_against_job(db, selected_job, temp_resume)
                            
                            # Store evaluation ID with application for admin reference
                            application.evaluation_id = evaluation.id
                            db.commit()
                            
                        except Exception as e:
                            print(f"Analysis error: {e}")
                            # Continue even if analysis fails
                    
                    st.success("Application submitted successfully!")
                    
                    # Show submission confirmation
                    st.markdown("### Thank You!")
                    st.info(f"""
                    **Application ID:** {application.id}
                    
                    Your application for **{selected_job.title}** has been submitted successfully!
                    
                    Our HR team will review your application and contact you within 3-5 business days.
                    
                    You will receive a confirmation email at **{email}**
                    """)
                    
                except Exception as e:
                    st.error(f"Error submitting application: {str(e)}")

def page_upload_jd():
    """Admin page for uploading job descriptions"""
    if not require_auth():
        st.warning("🔒 Please login to access this page")
        return
    st.header("Upload Job Description (JD)")
    
    # Option to upload JD file or enter text manually
    input_method = st.radio("How would you like to provide the JD?", 
                           ["Upload File (PDF/DOCX)", "Enter Text Manually"], 
                           horizontal=True)
    
    with st.form("jd_form"):
        title = st.text_input("Job Title", placeholder="e.g., Software Engineer (Backend)")
        location = st.text_input("Location (optional)")
        
        jd_text = ""
        if input_method == "Upload File (PDF/DOCX)":
            uploaded_jd = st.file_uploader("Upload JD File", type=["pdf", "docx"], key="jd_file")
            if uploaded_jd:
                try:
                    content = uploaded_jd.read()
                    jd_text, ext = extract_text(content, uploaded_jd.name)
                    st.text_area("Extracted JD Text (you can edit if needed)", value=jd_text, height=200, key="jd_text_extracted")
                    jd_text = st.session_state.get("jd_text_extracted", jd_text)
                except Exception as e:
                    st.error(f"Failed to extract text from file: {e}")
                    jd_text = st.text_area("Job Description Text (manual entry)", height=200, key="jd_text_manual")
            else:
                st.info("Please upload a JD file above")
                jd_text = ""
        else:
            jd_text = st.text_area("Job Description Text", height=200, key="jd_text_manual")
        
        suggest = st.form_submit_button("Suggest Skills from JD")
        must_skills = st.text_input("Must-have skills (comma-separated)")
        nice_skills = st.text_input("Nice-to-have skills (comma-separated)")
        submitted = st.form_submit_button("Save JD")

        if suggest and jd_text.strip():
            parsed = parse_jd_freeform(jd_text)
            st.info("Suggested skills extracted from JD.")
            st.session_state["jd_suggest_must"] = ", ".join(parsed.get("must", []))
            st.session_state["jd_suggest_nice"] = ", ".join(parsed.get("nice", []))
        else:
            st.session_state.setdefault("jd_suggest_must", "")
            st.session_state.setdefault("jd_suggest_nice", "")

        if st.session_state.get("jd_suggest_must"):
            st.caption("Suggested must-have: " + st.session_state["jd_suggest_must"])
        if st.session_state.get("jd_suggest_nice"):
            st.caption("Suggested nice-to-have: " + st.session_state["jd_suggest_nice"])

        if submitted:
            if not title.strip() or not jd_text.strip():
                st.error("Title and JD text are required.")
            else:
                db = SessionLocal()
                try:
                    must = [s.strip() for s in (must_skills or st.session_state.get("jd_suggest_must", "")).split(",") if s.strip()]
                    nice = [s.strip() for s in (nice_skills or st.session_state.get("jd_suggest_nice", "")).split(",") if s.strip()]
                    job = crud.create_job(db, title=title, jd_text=jd_text, must_skills=must, nice_skills=nice, location=location)
                    st.success(f"Saved JD: {job.title} (id={job.id})")
                finally:
                    db.close()

    st.subheader("Existing JDs")
    db = SessionLocal()
    try:
        jobs = crud.list_jobs(db)
        if jobs:
            df = pd.DataFrame([
                {"id": j.id, "title": j.title, "location": j.location, "created_at": j.created_at}
                for j in jobs
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No JDs yet. Add one above.")
    finally:
        db.close()


def page_upload_resume():
    st.markdown('<h2 class="section-header">📋 Upload Resume and Evaluate</h2>', unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        jobs = crud.list_jobs(db)
        recent_evals = crud.list_evaluations(db)[:5]  # Get last 5 evaluations
    finally:
        db.close()

    if not jobs:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.warning("⚠️ No job descriptions available. Please add a JD first in the 'Upload JD' page.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Select Job Description")
        job_options = {f"{j.title} ({j.location or 'Remote'})": j.id for j in jobs}
        job_label = st.selectbox("", list(job_options.keys()))
        
        # Show selected job details
        selected_job = next(j for j in jobs if j.id == job_options[job_label])
        with st.expander("🔍 View Job Requirements", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                must_skills = json.loads(selected_job.must_skills_json or '[]')
                st.markdown("**🔴 Must-have Skills:**")
                for skill in must_skills:
                    st.markdown(f"• {skill}")
            with col_b:
                nice_skills = json.loads(selected_job.nice_skills_json or '[]')
                st.markdown("**🟡 Nice-to-have Skills:**")
                for skill in nice_skills:
                    st.markdown(f"• {skill}")

        st.markdown("### 📁 Upload Resume")
        uploaded = st.file_uploader("", type=["pdf", "docx"], 
                                  help="Supported formats: PDF, DOCX")
        
        col_a, col_b = st.columns(2)
        with col_a:
            student_name = st.text_input("👤 Student Name", placeholder="Enter full name")
        with col_b:
            location = st.text_input("📍 Location (optional)", placeholder="City, Country")

    with col2:
        st.markdown("### 📊 Recent Evaluations")
        if recent_evals:
            for evaluation in recent_evals:
                verdict_class = f"score-{evaluation.verdict.lower()}"
                st.markdown(f'''
                <div class="{verdict_class}">
                    <strong>{evaluation.resume.student_name if evaluation.resume else 'Unknown'}</strong><br>
                    Score: {evaluation.score}% | {evaluation.verdict}
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No evaluations yet")

    st.markdown("---")
    
    # Enhanced evaluation button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        evaluate_btn = st.button("🚀 Evaluate Resume", type="primary", use_container_width=True)

    if evaluate_btn:
        if not uploaded or not student_name.strip():
            st.error("❌ Please provide resume file and student name.")
            return
            
        # Show progress
        progress = st.progress(0)
        status = st.empty()
        
        try:
            status.text("📄 Extracting text from resume...")
            progress.progress(25)
            content = uploaded.read()
            text, ext = extract_text(content, uploaded.name)
            
            status.text("💾 Saving resume to database...")
            progress.progress(50)
            
            db = SessionLocal()
            try:
                resume = crud.create_resume(db, student_name=student_name, 
                                          file_name=uploaded.name, text=text, location=location)
                
                status.text("🧠 AI is analyzing resume vs job requirements...")
                progress.progress(75)
                
                job_id = job_options[job_label]
                job = crud.get_job(db, job_id)
                ev = evaluate_resume_against_job(db, job, resume)
                
                # Advanced analysis
                status.text("🔍 Extracting entities and generating insights...")
                progress.progress(85)
                
                entities = text_processor.extract_entities(text)
                text_summary = text_processor.get_text_summary(text)
                
                # LLM analysis if available
                llm_analysis = None
                if llm_evaluator.llm:
                    status.text("✨ LLM generating detailed feedback...")
                    progress.progress(95)
                    llm_result = llm_evaluator.evaluate_with_llm(text, job.jd_text)
                    llm_analysis = llm_result
                
                status.text("✅ Evaluation complete!")
                progress.progress(100)
                
                # Beautiful results display
                st.markdown("---")
                st.markdown("### 🎯 Evaluation Results")
                
                # Score display with dynamic styling
                score = ev.score
                if score >= 75:
                    score_class = "score-high"
                    emoji = "🟢"
                elif score >= 50:
                    score_class = "score-medium" 
                    emoji = "🟡"
                else:
                    score_class = "score-low"
                    emoji = "🔴"
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f'''
                    <div class="{score_class}">
                        <h2>{emoji} {score}%</h2>
                        <p>Relevance Score</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'''
                    <div class="{score_class}">
                        <h2>🎯 {ev.verdict}</h2>
                        <p>Verdict</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    missing_count = len(json.loads(ev.missing_json or '[]'))
                    st.markdown(f'''
                    <div class="{score_class}">
                        <h2>📊 {missing_count}</h2>
                        <p>Missing Skills</p>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Enhanced Analysis Section
                if llm_analysis:
                    st.markdown("### 🤖 Advanced LLM Analysis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**🎯 LLM Semantic Score:**")
                        st.progress(llm_analysis.semantic_score)
                        st.caption(f"{llm_analysis.semantic_score:.2f} confidence")
                        
                        if llm_analysis.strengths:
                            st.markdown("**💪 Key Strengths:**")
                            for strength in llm_analysis.strengths[:5]:
                                st.markdown(f"• {strength}")
                    
                    with col2:
                        st.markdown("**🎯 Confidence Score:**")
                        st.progress(llm_analysis.confidence_score)
                        st.caption(f"{llm_analysis.confidence_score:.2f} reliability")
                        
                        if llm_analysis.skill_gaps:
                            st.markdown("**📋 LLM-Identified Gaps:**")
                            for gap in llm_analysis.skill_gaps[:5]:
                                st.markdown(f"• {gap}")
                    
                    if llm_analysis.detailed_feedback:
                        st.markdown("**🤖 Detailed LLM Feedback:**")
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.write(llm_analysis.detailed_feedback)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Entity Extraction Results
                st.markdown("### 🔍 Extracted Information")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**🛠️ Technical Skills:**")
                    if entities.skills:
                        for skill in entities.skills[:8]:
                            st.markdown(f"• {skill}")
                    else:
                        st.caption("None detected")
                
                with col2:
                    st.markdown("**🎓 Education & Certifications:**")
                    if entities.education:
                        for edu in entities.education[:3]:
                            st.markdown(f"• {edu}")
                    if entities.certifications:
                        for cert in entities.certifications[:3]:
                            st.markdown(f"• {cert}")
                    if not entities.education and not entities.certifications:
                        st.caption("None detected")
                
                with col3:
                    st.markdown("**💼 Experience & Companies:**")
                    if entities.experience_years:
                        max_exp = max(entities.experience_years)
                        st.markdown(f"• {max_exp} years experience")
                    if entities.companies:
                        for company in entities.companies[:3]:
                            st.markdown(f"• {company}")
                    if not entities.experience_years and not entities.companies:
                        st.caption("None detected")
                
                # Text Analysis Summary
                with st.expander("📊 Document Analysis", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Word Count", text_summary['word_count'])
                        st.metric("Unique Words", text_summary['unique_words'])
                    with col2:
                        st.metric("Sentences", text_summary['sentence_count'])
                        st.metric("Avg Sentence Length", f"{text_summary['avg_sentence_length']:.1f}")
                
                # Traditional feedback
                if ev.suggestions:
                    st.markdown("### 💡 Traditional AI Suggestions")
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.write(ev.suggestions)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if ev.missing_json:
                    missing_skills = json.loads(ev.missing_json)
                    if missing_skills:
                        st.markdown("### ❌ Missing Must-Have Skills")
                        cols = st.columns(3)
                        for i, skill in enumerate(missing_skills):
                            with cols[i % 3]:
                                st.markdown(f"• **{skill}**")
                
                st.balloons()
                status.empty()
                progress.empty()
                
            finally:
                db.close()
                
        except Exception as e:
            st.error(f"❌ Failed to process resume: {e}")
            status.empty()
            progress.empty()


def page_dashboard():
    st.markdown('<h2 class="section-header">📊 Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        jobs = crud.list_jobs(db)
        all_evals = crud.list_evaluations(db)
        resumes = crud.list_resumes(db)
    finally:
        db.close()

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-container">
            <h2>{len(jobs)}</h2>
            <p>📄 Job Descriptions</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-container">
            <h2>{len(resumes)}</h2>
            <p>📋 Resumes Processed</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        avg_score = sum(e.score for e in all_evals) / len(all_evals) if all_evals else 0
        st.markdown(f'''
        <div class="metric-container">
            <h2>{avg_score:.1f}%</h2>
            <p>📈 Average Score</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        high_matches = len([e for e in all_evals if e.score >= 75])
        st.markdown(f'''
        <div class="metric-container">
            <h2>{high_matches}</h2>
            <p>🎯 High Matches</p>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # Charts row
    if all_evals:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Score Distribution")
            scores = [e.score for e in all_evals]
            fig = px.histogram(x=scores, nbins=20, title="Resume Scores Distribution",
                             labels={'x': 'Score', 'y': 'Count'},
                             color_discrete_sequence=['#667eea'])
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Verdict Breakdown")
            verdict_counts = {}
            for e in all_evals:
                verdict_counts[e.verdict] = verdict_counts.get(e.verdict, 0) + 1
            
            fig = px.pie(values=list(verdict_counts.values()), 
                        names=list(verdict_counts.keys()),
                        title="Evaluation Verdicts",
                        color_discrete_sequence=['#11998e', '#f5576c', '#4facfe'])
            st.plotly_chart(fig, use_container_width=True)

        # Timeline chart
        st.markdown("### 📈 Evaluation Timeline")
        df_timeline = pd.DataFrame([{
            'date': e.created_at.date(),
            'score': e.score,
            'verdict': e.verdict
        } for e in all_evals])
        
        fig = px.scatter(df_timeline, x='date', y='score', color='verdict',
                        title="Scores Over Time",
                        color_discrete_sequence=['#11998e', '#f5576c', '#4facfe'])
        fig.update_layout(xaxis_title="Date", yaxis_title="Score")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Filters section
    st.markdown("### 🔍 Filter Results")
    
    job_map = {"All Jobs": None}
    job_map.update({j.title: j.id for j in jobs})

    col1, col2, col3 = st.columns(3)
    with col1:
        job_sel = st.selectbox("📄 Job Filter", list(job_map.keys()))
    with col2:
        min_score = st.slider("📊 Minimum Score", 0, 100, 0)
    with col3:
        location = st.text_input("📍 Location Filter", placeholder="e.g., New York")

    # Results table
    db = SessionLocal()
    try:
        if job_map[job_sel] is None:
            evs = crud.list_evaluations(db, min_score=min_score, location=location or None)
        else:
            evs = crud.list_evaluations(db, job_id=job_map[job_sel], min_score=min_score, location=location or None)
        
        if evs:
            st.markdown("### 📋 Filtered Results")
            
            rows = []
            for ev in evs:
                # Score styling
                if ev.score >= 75:
                    score_display = f"🟢 {ev.score}%"
                elif ev.score >= 50:
                    score_display = f"🟡 {ev.score}%"
                else:
                    score_display = f"🔴 {ev.score}%"
                
                rows.append({
                    "📊 Score": score_display,
                    "🎯 Verdict": ev.verdict,
                    "📄 Job": ev.job.title if ev.job else "Unknown",
                    "👤 Student": ev.resume.student_name if ev.resume else "Unknown",
                    "📁 Resume": ev.resume.file_name if ev.resume else "Unknown",
                    "📍 Location": ev.resume.location if ev.resume and ev.resume.location else "Not specified",
                    "📅 Date": ev.created_at.strftime("%Y-%m-%d %H:%M"),
                })
            
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, height=400)
            
            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.info("📭 No evaluations match your filters. Try adjusting the criteria above.")
            st.markdown('</div>', unsafe_allow_html=True)
    finally:
        db.close()


def main():
    st.set_page_config(
        page_title=APP_NAME, 
        layout="wide",
        page_icon="📄",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    
    # Main navigation logic
    if not is_authenticated():
        # Public pages - only landing page for students and login
        if st.session_state.page not in ["landing"]:
            st.session_state.page = "landing"
        
        page_landing()
    
    else:
        # Admin pages - full access after authentication
        with st.sidebar:
            st.markdown("### 🎯 Admin Panel")
            
            # Show logout button
            show_logout_button()
            
            # Back to Student Portal button
            if st.button("🎓 Student Portal", use_container_width=True):
                st.session_state.page = "landing"
                st.rerun()
            
            st.markdown("---")
            
            # Admin navigation
            nav_options = [
                "📄 Manage Jobs", 
                "📋 Review Applications",
                "📊 Analytics Dashboard"
            ]
            
            # Map current page to radio selection
            page_mapping = {
                "upload_jd": "📄 Manage Jobs",
                "admin_dashboard": "📋 Review Applications",
                "analytics": "📊 Analytics Dashboard"
            }
            
            # Get current index - default to Manage Jobs for admin
            current_page = st.session_state.get("page", "upload_jd")
            current_selection = page_mapping.get(current_page, "📄 Manage Jobs")
            
            try:
                default_index = nav_options.index(current_selection)
            except ValueError:
                default_index = 0
            
            selected_page = st.radio(
                "Navigate to:", 
                nav_options,
                index=default_index
            )
            
            # Update session state based on selection
            if "Manage Jobs" in selected_page:
                st.session_state.page = "upload_jd"
            elif "Review Applications" in selected_page:
                st.session_state.page = "admin_dashboard"
            elif "Analytics Dashboard" in selected_page:
                st.session_state.page = "analytics"
            
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            
            # Quick stats in sidebar
            try:
                with SessionLocal() as db:
                    total_jobs = len(crud.list_jobs(db))
                    total_applications = len(crud.list_student_applications(db))
                    pending_applications = len(crud.list_student_applications(db, status="pending"))
                    
                    st.metric("📄 Total Jobs", total_jobs)
                    st.metric("📋 Applications", total_applications)
                    st.metric("⏳ Pending", pending_applications)
            except Exception as e:
                st.error(f"Error loading stats: {e}")
        
        # Route to appropriate admin page based on session state
        if st.session_state.page == "landing":
            page_landing()
        elif st.session_state.page == "upload_jd":
            page_upload_jd()
        elif st.session_state.page == "admin_dashboard":
            page_admin_dashboard()
        elif st.session_state.page == "analytics":
            page_dashboard()
        else:
            # Default fallback to manage jobs for admin
            st.session_state.page = "upload_jd"
            page_upload_jd()

def page_admin_dashboard():
    """Admin dashboard for reviewing student applications and their analysis"""
    st.markdown('<h1 class="main-header">📋 Student Applications Dashboard</h1>', unsafe_allow_html=True)
    
    # Get all applications with job data
    with SessionLocal() as db:
        applications = crud.list_student_applications(db)
        jobs = crud.list_jobs(db)
        
        # Create job lookup for filtering
        job_dict = {job.id: job.title for job in jobs}
        
        # Convert to data that doesn't require DB session
        app_data = []
        for app in applications:
            app_info = {
                'id': app.id,
                'student_name': app.student_name,
                'email': app.email,
                'phone': app.phone or 'Not provided',
                'location': app.location or 'Not provided',
                'status': app.status,
                'job_id': app.job_id,
                'job_title': job_dict.get(app.job_id, 'Unknown'),
                'resume_file_name': app.resume_file_name,
                'resume_text': app.resume_text,
                'cover_letter': app.cover_letter,
                'created_at': app.created_at
            }
            app_data.append(app_info)
    
    if not app_data:
        st.info("📭 No student applications yet.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "pending", "reviewed", "accepted", "rejected"])
    with col2:
        job_titles = ["All"] + list(set(app['job_title'] for app in app_data))
        job_filter = st.selectbox("Filter by Job", job_titles)
    with col3:
        sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Name"])
    
    # Filter applications
    filtered_apps = app_data
    if status_filter != "All":
        filtered_apps = [app for app in filtered_apps if app['status'] == status_filter]
    if job_filter != "All":
        filtered_apps = [app for app in filtered_apps if app['job_title'] == job_filter]
    
    # Sort applications
    if sort_by == "Date (Newest)":
        filtered_apps.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Date (Oldest)":
        filtered_apps.sort(key=lambda x: x['created_at'])
    else:
        filtered_apps.sort(key=lambda x: x['student_name'])
    
    st.markdown(f"### 📊 Showing {len(filtered_apps)} applications")
    
    # Display applications
    for app in filtered_apps:
        with st.expander(f"👤 {app['student_name']} - {app['job_title']} | Status: {app['status'].upper()}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📝 Application Details")
                st.write(f"**Email:** {app['email']}")
                st.write(f"**Phone:** {app['phone']}")
                st.write(f"**Location:** {app['location']}")
                st.write(f"**Applied:** {app['created_at'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Resume File:** {app['resume_file_name']}")
                
                if app['cover_letter']:
                    st.markdown("**Cover Letter:**")
                    st.text_area("", value=app['cover_letter'], height=100, disabled=True, key=f"cover_{app['id']}")
            
            with col2:
                st.markdown("#### ⚙️ Actions")
                
                # Status update
                new_status = st.selectbox(
                    "Update Status",
                    ["pending", "reviewed", "accepted", "rejected"],
                    index=["pending", "reviewed", "accepted", "rejected"].index(app['status']),
                    key=f"status_{app['id']}"
                )
                
                if st.button(f"Update Status", key=f"update_{app['id']}"):
                    with SessionLocal() as db:
                        crud.update_application_status(db, app['id'], new_status)
                    st.success(f"Status updated to {new_status}")
                    st.rerun()
            
            # Resume analysis section
            st.markdown("#### 🧠 AI Resume Analysis")
            
            # Perform resume analysis
            try:
                with SessionLocal() as db:
                    # Get the job for analysis
                    job = crud.get_job(db, app['job_id'])
                    if job:
                        # Create temporary resume for analysis
                        temp_resume = crud.create_resume(
                            db=db,
                            student_name=app['student_name'],
                            file_name=app['resume_file_name'],
                            text=app['resume_text'],
                            location=app['location'] if app['location'] != 'Not provided' else ""
                        )
                        
                        # Run evaluation
                        evaluation = evaluate_resume_against_job(db, job, temp_resume)
                        
                        # Display analysis results
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            score_color = "🟢" if evaluation.score >= 75 else "🟡" if evaluation.score >= 50 else "🔴"
                            st.metric("Match Score", f"{evaluation.score}%", delta=None)
                            st.write(f"{score_color} **{evaluation.verdict.upper()}**")
                        
                        with col_b:
                            missing_skills = json.loads(evaluation.missing_json or '[]')
                            st.metric("Missing Skills", len(missing_skills))
                        
                        with col_c:
                            st.metric("Analysis Date", evaluation.created_at.strftime('%m/%d'))
                        
                        # Missing skills
                        if missing_skills:
                            st.markdown("**🚫 Missing Skills:**")
                            for skill in missing_skills[:5]:  # Show top 5
                                st.write(f"• {skill}")
                            if len(missing_skills) > 5:
                                st.write(f"... and {len(missing_skills) - 5} more")
                        
                        # LLM Analysis if available
                        if llm_evaluator.llm:
                            try:
                                llm_result = llm_evaluator.evaluate_with_llm(app['resume_text'], job.jd_text)
                                
                                st.markdown("**🤖 AI Detailed Feedback:**")
                                st.write(llm_result.detailed_feedback)
                                
                                if llm_result.strengths:
                                    st.markdown("**💪 Strengths:**")
                                    for strength in llm_result.strengths[:3]:
                                        st.write(f"• {strength}")
                                
                                if llm_result.improvement_suggestions:
                                    st.markdown("**💡 Improvement Suggestions:**")
                                    for suggestion in llm_result.improvement_suggestions[:3]:
                                        st.write(f"• {suggestion}")
                            
                            except Exception as e:
                                st.warning(f"LLM analysis unavailable: {e}")
                        
                        # Advanced entity extraction
                        try:
                            entities = text_processor.extract_entities(app['resume_text'])
                            
                            col_x, col_y = st.columns(2)
                            with col_x:
                                st.markdown("**🎯 Extracted Skills:**")
                                if entities.skills:
                                    for skill in entities.skills[:10]:
                                        st.write(f"• {skill}")
                            
                            with col_y:
                                st.markdown("**🏢 Experience:**")
                                if entities.experience_years:
                                    max_exp = max(entities.experience_years) if entities.experience_years else 0
                                    st.write(f"Years: {max_exp}")
                                if entities.companies:
                                    st.write("Companies:")
                                    for company in entities.companies[:3]:
                                        st.write(f"• {company}")
                        
                        except Exception as e:
                            st.warning(f"Entity extraction unavailable: {e}")
                    else:
                        st.warning("Job not found for this application")
            
            except Exception as e:
                st.error(f"Analysis error: {e}")

            st.markdown("---")


def page_placement_dashboard():
    """Advanced placement team dashboard with search and filtering"""
    st.markdown('<h1 class="main-header">🎯 Placement Team Dashboard</h1>', unsafe_allow_html=True)
    
    # Get all data
    with SessionLocal() as db:
        jobs = crud.list_jobs(db)
        evaluations = crud.list_evaluations(db)
    
    if not evaluations:
        st.info("📭 No resume evaluations available yet.")
        return
    
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Advanced Filters")
    
    # Job role filter
    job_titles = ["All"] + [job.title for job in jobs]
    selected_job = st.sidebar.selectbox("Job Role", job_titles)
    
    # Score range filter
    min_score, max_score = st.sidebar.slider(
        "Score Range", 
        min_value=0.0, 
        max_value=100.0, 
        value=(0.0, 100.0),
        step=5.0
    )
    
    # Verdict filter
    verdict_options = ["All", "ACCEPT", "MAYBE", "REJECT"]
    selected_verdict = st.sidebar.selectbox("Verdict", verdict_options)
    
    # Location filter
    st.sidebar.text_input("Location (contains)", key="location_filter")
    location_filter = st.session_state.get("location_filter", "")
    
    # Skills filter
    st.sidebar.text_input("Required Skills (comma-separated)", key="skills_filter")
    skills_filter = st.session_state.get("skills_filter", "")
    
    # Apply filters
    filtered_evals = evaluations
    
    # Filter by job
    if selected_job != "All":
        job_id = next((job.id for job in jobs if job.title == selected_job), None)
        if job_id:
            filtered_evals = [e for e in filtered_evals if e.job_id == job_id]
    
    # Filter by score range
    filtered_evals = [e for e in filtered_evals if min_score <= e.score <= max_score]
    
    # Filter by verdict
    if selected_verdict != "All":
        filtered_evals = [e for e in filtered_evals if e.verdict.upper() == selected_verdict]
    
    # Filter by location
    if location_filter:
        filtered_evals = [e for e in filtered_evals 
                         if location_filter.lower() in (e.resume.location or "").lower()]
    
    # Filter by skills
    if skills_filter:
        skill_list = [s.strip().lower() for s in skills_filter.split(',')]
        filtered_evals = [e for e in filtered_evals
                         if any(skill in e.resume.text.lower() for skill in skill_list)]
    
    # Sort by score (descending)
    filtered_evals.sort(key=lambda x: x.score, reverse=True)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Candidates", len(filtered_evals))
    with col2:
        shortlisted = [e for e in filtered_evals if e.score >= 70]
        st.metric("Shortlisted (≥70%)", len(shortlisted))
    with col3:
        avg_score = sum(e.score for e in filtered_evals) / len(filtered_evals) if filtered_evals else 0
        st.metric("Average Score", f"{avg_score:.1f}%")
    with col4:
        accepted = [e for e in filtered_evals if e.verdict.upper() == "ACCEPT"]
        st.metric("Recommended", len(accepted))
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Actions")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("🌟 Show Only Shortlisted"):
            st.session_state["show_shortlisted"] = True
    
    with col_b:
        if st.button("📊 Export to CSV"):
            # Create DataFrame for export
            export_data = []
            for eval in filtered_evals:
                export_data.append({
                    "Student Name": eval.resume.student_name,
                    "Job Title": eval.job.title,
                    "Score": eval.score,
                    "Verdict": eval.verdict,
                    "Location": eval.resume.location or "",
                    "File Name": eval.resume.file_name,
                    "Date": eval.created_at.strftime("%Y-%m-%d")
                })
            
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"placement_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col_c:
        if st.button("🔄 Reset Filters"):
            for key in ["location_filter", "skills_filter", "show_shortlisted"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Apply shortlisted filter if set
    display_evals = filtered_evals
    if st.session_state.get("show_shortlisted", False):
        display_evals = [e for e in filtered_evals if e.score >= 70]
        st.info(f"🌟 Showing only shortlisted candidates (Score ≥ 70%)")
    
    # Display results
    st.markdown(f"### 📋 Candidates ({len(display_evals)} results)")
    
    for eval in display_evals:
        # Color code based on score
        if eval.score >= 80:
            header_color = "🟢"
        elif eval.score >= 60:
            header_color = "🟡"
        else:
            header_color = "🔴"
        
        with st.expander(
            f"{header_color} {eval.resume.student_name} | {eval.job.title} | Score: {eval.score}% | {eval.verdict}",
            expanded=False
        ):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown("#### 👤 Candidate Details")
                st.write(f"**Name:** {eval.resume.student_name}")
                st.write(f"**Location:** {eval.resume.location or 'Not specified'}")
                st.write(f"**Resume File:** {eval.resume.file_name}")
                st.write(f"**Evaluation Date:** {eval.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                # Extract and display skills
                try:
                    entities = text_processor.extract_entities(eval.resume.text)
                    if entities.skills:
                        st.markdown("**🎯 Key Skills:**")
                        skills_display = ", ".join(entities.skills[:8])
                        st.write(skills_display)
                        if len(entities.skills) > 8:
                            st.caption(f"... and {len(entities.skills) - 8} more skills")
                except:
                    pass
            
            with col2:
                st.markdown("#### 📊 Evaluation")
                score_color = "success" if eval.score >= 70 else "warning" if eval.score >= 50 else "error"
                st.metric("Match Score", f"{eval.score}%")
                st.write(f"**Verdict:** {eval.verdict}")
                
                # Missing skills
                try:
                    missing_skills = json.loads(eval.missing_json or '[]')
                    if missing_skills:
                        st.metric("Missing Skills", len(missing_skills))
                        with st.expander("View Missing Skills"):
                            for skill in missing_skills:
                                st.write(f"• {skill}")
                except:
                    pass
            
            with col3:
                st.markdown("#### 🏢 Job Match")
                st.write(f"**Position:** {eval.job.title}")
                st.write(f"**Location:** {eval.job.location or 'Any'}")
                
                # Job description preview
                if st.button(f"View JD", key=f"jd_{eval.id}"):
                    st.text_area(
                        "Job Description",
                        value=eval.job.jd_text[:300] + "...",
                        height=100,
                        disabled=True,
                        key=f"jd_text_{eval.id}"
                    )
            
            # Suggestions and feedback
            if eval.suggestions:
                st.markdown("#### 💡 Improvement Suggestions")
                st.info(eval.suggestions)
            
            # Resume preview
            with st.expander("📄 Resume Preview"):
                resume_preview = eval.resume.text[:500] + "..." if len(eval.resume.text) > 500 else eval.resume.text
                st.text_area("", value=resume_preview, height=150, disabled=True, key=f"resume_{eval.id}")

            st.markdown("---")


if __name__ == "__main__":
    main()

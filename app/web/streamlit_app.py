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

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Ensure models are imported so tables are created
_ = models

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .score-high {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    .score-medium {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    .score-low {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    .success-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #27ae60;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin: 1rem 0;
    }
    .upload-zone {
        border: 2px dashed #3498db;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 8px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

def page_upload_jd():
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
        page_icon="🎯",
        initial_sidebar_state="expanded"
    )
    
    # Beautiful main header
    st.markdown(f'<h1 class="main-header">🎯 {APP_NAME}</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        <p style="font-size: 1.2rem;">AI-Powered Resume Evaluation Engine with Hybrid Scoring</p>
        <p style="font-size: 1rem;">📄 Upload • 🧠 Analyze • 📊 Score • 🎯 Match</p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced sidebar
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        page = st.radio("", [
            "📄 Upload JD", 
            "📋 Upload Resume", 
            "📊 Dashboard"
        ], format_func=lambda x: x.replace("📄 ", "").replace("📋 ", "").replace("📊 ", ""))
        
        st.markdown("---")
        st.markdown("### 📈 Quick Stats")
        
        # Quick stats in sidebar
        db = SessionLocal()
        try:
            jobs_count = len(crud.list_jobs(db))
            resumes_count = len(crud.list_resumes(db))
            evals = crud.list_evaluations(db)
            avg_score = sum(e.score for e in evals) / len(evals) if evals else 0
            
            st.metric("Job Descriptions", jobs_count)
            st.metric("Resumes Evaluated", resumes_count) 
            st.metric("Average Score", f"{avg_score:.1f}")
        finally:
            db.close()
        
        st.markdown("---")
        st.markdown("### ⚙️ AI System Status")
        
        # Check system capabilities
        llm_status = "🟢 Active" if llm_evaluator.llm else "🟡 Fallback"
        vector_status = "🟢 Active" if llm_evaluator.collection else "🔴 Offline"
        
        st.caption(f"� LLM Engine: {llm_status}")
        st.caption(f"🔍 Vector Search: {vector_status}")
        st.caption("� Hybrid Scoring: 🟢 Active")
        st.caption("🎯 Entity Extraction: � Active")
        
        if llm_evaluator.llm:
            st.success("✨ Full AI capabilities enabled!")
        else:
            st.info("💡 Add OpenAI API key for enhanced LLM features")

    pages = {
        "📄 Upload JD": page_upload_jd,
        "📋 Upload Resume": page_upload_resume,
        "📊 Dashboard": page_dashboard,
    }
    
    # Find the selected page
    selected_page = None
    for key in pages.keys():
        if page in key:
            selected_page = key
            break
    
    if selected_page:
        pages[selected_page]()


if __name__ == "__main__":
    main()

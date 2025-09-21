"""
FastAPI backend for the Resume Evaluation System
Provides REST API endpoints for all operations
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uvicorn
import json

from app.db.database import get_db
from app.db import crud, models
from app.parsing.files import extract_text
from app.parsing.jd_parser import parse_jd_freeform
from app.services.evaluator import evaluate_resume_against_job
from app.services.llm_evaluator import llm_evaluator
from app.nlp.advanced_processor import text_processor

# Pydantic models for API
class JobCreate(BaseModel):
    title: str
    jd_text: str
    must_skills: List[str]
    nice_skills: List[str]
    location: Optional[str] = ""

class JobResponse(BaseModel):
    id: int
    title: str
    location: Optional[str]
    must_skills: List[str]
    nice_skills: List[str]
    created_at: str

class ResumeCreate(BaseModel):
    student_name: str
    location: Optional[str] = ""

class EvaluationResponse(BaseModel):
    id: int
    score: float
    verdict: str
    missing_skills: List[str]
    suggestions: str
    llm_feedback: Optional[Dict[str, Any]] = None
    created_at: str

class AdvancedEvaluationResponse(BaseModel):
    basic_evaluation: EvaluationResponse
    llm_analysis: Optional[Dict[str, Any]] = None
    extracted_entities: Dict[str, Any]
    text_summary: Dict[str, int]

class StudentApplicationCreate(BaseModel):
    job_id: int
    student_name: str
    email: str
    phone: Optional[str] = ""
    location: Optional[str] = ""
    cover_letter: Optional[str] = ""

class StudentApplicationResponse(BaseModel):
    id: int
    job_id: int
    student_name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    resume_file_name: str
    cover_letter: Optional[str]
    status: str
    created_at: str
    job_title: str

# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Evaluation Engine API",
    description="Advanced AI-powered resume evaluation with LLM analysis",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AI Resume Evaluation Engine API",
        "version": "2.0.0",
        "features": [
            "LLM-powered evaluation",
            "Vector store semantic search",
            "Advanced entity extraction",
            "Hybrid scoring algorithm"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_available": llm_evaluator.llm is not None,
        "vector_store_available": llm_evaluator.collection is not None
    }

# Job Description endpoints
@app.post("/jobs/", response_model=JobResponse)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job description"""
    try:
        db_job = crud.create_job(
            db=db,
            title=job.title,
            jd_text=job.jd_text,
            must_skills=job.must_skills,
            nice_skills=job.nice_skills,
            location=job.location
        )
        
        # Add to vector store for semantic search
        llm_evaluator.add_to_vector_store(
            text=job.jd_text,
            metadata={
                "type": "job_description",
                "title": job.title,
                "job_id": db_job.id
            },
            doc_id=f"job_{db_job.id}"
        )
        
        return JobResponse(
            id=db_job.id,
            title=db_job.title,
            location=db_job.location,
            must_skills=json.loads(db_job.must_skills_json or '[]'),
            nice_skills=json.loads(db_job.nice_skills_json or '[]'),
            created_at=db_job.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/jobs/", response_model=List[JobResponse])
async def list_jobs(db: Session = Depends(get_db)):
    """List all job descriptions"""
    jobs = crud.list_jobs(db)
    return [
        JobResponse(
            id=job.id,
            title=job.title,
            location=job.location,
            must_skills=json.loads(job.must_skills_json or '[]'),
            nice_skills=json.loads(job.nice_skills_json or '[]'),
            created_at=job.created_at.isoformat()
        )
        for job in jobs
    ]

@app.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job description"""
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse(
        id=job.id,
        title=job.title,
        location=job.location,
        must_skills=json.loads(job.must_skills_json or '[]'),
        nice_skills=json.loads(job.nice_skills_json or '[]'),
        created_at=job.created_at.isoformat()
    )

@app.post("/jobs/upload")
async def upload_job_file(
    title: str,
    location: str = "",
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload job description from file"""
    try:
        content = await file.read()
        jd_text, ext = extract_text(content, file.filename)
        
        # Parse skills from JD
        parsed = parse_jd_freeform(jd_text)
        
        db_job = crud.create_job(
            db=db,
            title=title,
            jd_text=jd_text,
            must_skills=parsed.get("must", []),
            nice_skills=parsed.get("nice", []),
            location=location
        )
        
        # Add to vector store
        llm_evaluator.add_to_vector_store(
            text=jd_text,
            metadata={
                "type": "job_description",
                "title": title,
                "job_id": db_job.id
            },
            doc_id=f"job_{db_job.id}"
        )
        
        return {
            "job_id": db_job.id,
            "extracted_text_length": len(jd_text),
            "suggested_must_skills": parsed.get("must", []),
            "suggested_nice_skills": parsed.get("nice", [])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

# Resume evaluation endpoints
@app.post("/evaluate/", response_model=AdvancedEvaluationResponse)
async def evaluate_resume(
    job_id: int,
    student_name: str,
    location: str = "",
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Comprehensive resume evaluation with LLM analysis"""
    try:
        # Get job
        job = crud.get_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Extract text from resume
        content = await file.read()
        resume_text, ext = extract_text(content, file.filename)
        
        # Create resume record
        resume = crud.create_resume(
            db=db,
            student_name=student_name,
            file_name=file.filename,
            text=resume_text,
            location=location
        )
        
        # Basic evaluation
        basic_eval = evaluate_resume_against_job(db, job, resume)
        
        # Advanced text processing
        entities = text_processor.extract_entities(resume_text)
        text_summary = text_processor.get_text_summary(resume_text)
        
        # LLM-powered evaluation
        llm_analysis = None
        if llm_evaluator.llm:
            llm_result = llm_evaluator.evaluate_with_llm(resume_text, job.jd_text)
            llm_analysis = {
                "semantic_score": llm_result.semantic_score,
                "detailed_feedback": llm_result.detailed_feedback,
                "skill_gaps": llm_result.skill_gaps,
                "strengths": llm_result.strengths,
                "improvement_suggestions": llm_result.improvement_suggestions,
                "relevance_explanation": llm_result.relevance_explanation,
                "confidence_score": llm_result.confidence_score
            }
        
        # Add resume to vector store
        llm_evaluator.add_to_vector_store(
            text=resume_text,
            metadata={
                "type": "resume",
                "student_name": student_name,
                "job_id": job_id,
                "resume_id": resume.id
            },
            doc_id=f"resume_{resume.id}"
        )
        
        return AdvancedEvaluationResponse(
            basic_evaluation=EvaluationResponse(
                id=basic_eval.id,
                score=basic_eval.score,
                verdict=basic_eval.verdict,
                missing_skills=json.loads(basic_eval.missing_json or '[]'),
                suggestions=basic_eval.suggestions,
                created_at=basic_eval.created_at.isoformat()
            ),
            llm_analysis=llm_analysis,
            extracted_entities={
                "skills": entities.skills,
                "experience_years": entities.experience_years,
                "education": entities.education,
                "certifications": entities.certifications,
                "technologies": entities.technologies,
                "companies": entities.companies,
                "locations": entities.locations,
                "contact_info": entities.contact_info
            },
            text_summary=text_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Evaluation failed: {str(e)}")

@app.get("/search/resumes")
async def search_resumes(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Semantic search for resumes"""
    try:
        results = llm_evaluator.semantic_search(query, n_results=limit)
        
        # Filter for resume documents
        resume_results = [r for r in results if r["metadata"].get("type") == "resume"]
        
        return {
            "query": query,
            "results": resume_results[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search failed: {str(e)}")

@app.get("/search/jobs")
async def search_jobs(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Semantic search for job descriptions"""
    try:
        results = llm_evaluator.semantic_search(query, n_results=limit)
        
        # Filter for job documents
        job_results = [r for r in results if r["metadata"].get("type") == "job_description"]
        
        return {
            "query": query,
            "results": job_results[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search failed: {str(e)}")

@app.get("/analytics/dashboard")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get analytics data for dashboard"""
    try:
        jobs = crud.list_jobs(db)
        evaluations = crud.list_evaluations(db)
        
        # Calculate metrics
        total_jobs = len(jobs)
        total_evaluations = len(evaluations)
        avg_score = sum(e.score for e in evaluations) / len(evaluations) if evaluations else 0
        high_scores = len([e for e in evaluations if e.score >= 75])
        
        # Score distribution
        score_ranges = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
        for eval in evaluations:
            if eval.score <= 25:
                score_ranges["0-25"] += 1
            elif eval.score <= 50:
                score_ranges["26-50"] += 1
            elif eval.score <= 75:
                score_ranges["51-75"] += 1
            else:
                score_ranges["76-100"] += 1
        
        # Verdict distribution
        verdict_counts = {}
        for eval in evaluations:
            verdict_counts[eval.verdict] = verdict_counts.get(eval.verdict, 0) + 1
        
        return {
            "total_jobs": total_jobs,
            "total_evaluations": total_evaluations,
            "average_score": round(avg_score, 2),
            "high_score_count": high_scores,
            "score_distribution": score_ranges,
            "verdict_distribution": verdict_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@app.post("/student-applications/", response_model=StudentApplicationResponse)
async def submit_student_application(
    application: StudentApplicationCreate,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Submit a student application with resume"""
    try:
        # Verify job exists
        job = crud.get_job(db, application.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Extract resume text
        content = await file.read()
        resume_text, ext = extract_text(content, file.filename)
        
        # Create application
        db_application = crud.create_student_application(
            db=db,
            job_id=application.job_id,
            student_name=application.student_name,
            email=application.email,
            phone=application.phone,
            location=application.location,
            resume_file_name=file.filename,
            resume_text=resume_text,
            cover_letter=application.cover_letter
        )
        
        return StudentApplicationResponse(
            id=db_application.id,
            job_id=db_application.job_id,
            student_name=db_application.student_name,
            email=db_application.email,
            phone=db_application.phone,
            location=db_application.location,
            resume_file_name=db_application.resume_file_name,
            cover_letter=db_application.cover_letter,
            status=db_application.status,
            created_at=db_application.created_at.isoformat(),
            job_title=job.title
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Application submission failed: {str(e)}")

@app.get("/student-applications/", response_model=List[StudentApplicationResponse])
async def list_student_applications(
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List student applications with filters"""
    applications = crud.list_student_applications(db, job_id=job_id, status=status)
    
    return [
        StudentApplicationResponse(
            id=app.id,
            job_id=app.job_id,
            student_name=app.student_name,
            email=app.email,
            phone=app.phone,
            location=app.location,
            resume_file_name=app.resume_file_name,
            cover_letter=app.cover_letter,
            status=app.status,
            created_at=app.created_at.isoformat(),
            job_title=app.job.title
        )
        for app in applications
    ]

@app.put("/student-applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update application status"""
    if status not in ["pending", "reviewed", "accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    application = crud.update_application_status(db, application_id, status)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": f"Application status updated to {status}", "application_id": application_id}

@app.get("/search/resumes/advanced")
async def advanced_resume_search(
    job_role: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    location: Optional[str] = None,
    verdict: Optional[str] = None,
    skills: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Advanced search for resumes with multiple filters"""
    try:
        # Get all evaluations from database with joins
        evaluations = db.query(models.Evaluation).join(models.Job).join(models.Resume).all()
        filtered_results = []
        
        for evaluation in evaluations:
            # Apply filters
            if min_score is not None and evaluation.score < min_score:
                continue
            if max_score is not None and evaluation.score > max_score:
                continue
            if verdict and evaluation.verdict.lower() != verdict.lower():
                continue
            
            # Get resume text for additional filtering
            resume_text = evaluation.resume.text.lower() if evaluation.resume.text else ""
            
            # Filter by location
            if location and location.lower() not in (evaluation.resume.location or "").lower():
                continue
            
            # Filter by skills
            if skills:
                skill_list = [s.strip().lower() for s in skills.split(',')]
                if not any(skill in resume_text for skill in skill_list):
                    continue
            
            # Filter by job role if provided
            if job_role:
                job_keywords = job_role.lower().split()
                if not any(keyword in resume_text for keyword in job_keywords):
                    continue
            
            filtered_results.append({
                "id": evaluation.id,
                "job_id": evaluation.job_id,
                "job_title": evaluation.job.title,
                "file_name": evaluation.resume.file_name,
                "student_name": evaluation.resume.student_name,
                "score": evaluation.score,
                "verdict": evaluation.verdict,
                "suggestions": evaluation.suggestions,
                "resume_text": evaluation.resume.text[:500] + "..." if len(evaluation.resume.text) > 500 else evaluation.resume.text,
                "location": evaluation.resume.location,
                "created_at": evaluation.created_at.isoformat()
            })
        
        # Sort by score (descending)
        filtered_results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "filters_applied": {
                "job_role": job_role,
                "min_score": min_score,
                "max_score": max_score,
                "location": location,
                "verdict": verdict,
                "skills": skills
            },
            "total_results": len(filtered_results),
            "results": filtered_results[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Advanced search failed: {str(e)}")

@app.get("/shortlisted-resumes")
async def get_shortlisted_resumes(
    job_id: Optional[int] = None,
    min_score: float = 7.0,
    db: Session = Depends(get_db)
):
    """Get shortlisted resumes (high-scoring candidates)"""
    try:
        query = db.query(models.Evaluation).join(models.Job).join(models.Resume)
        
        if job_id:
            query = query.filter(models.Evaluation.job_id == job_id)
        
        evaluations = query.filter(models.Evaluation.score >= min_score).all()
        
        shortlisted = []
        for evaluation in evaluations:
            shortlisted.append({
                "id": evaluation.id,
                "job_id": evaluation.job_id,
                "job_title": evaluation.job.title,
                "file_name": evaluation.resume.file_name,
                "student_name": evaluation.resume.student_name,
                "score": evaluation.score,
                "verdict": evaluation.verdict,
                "suggestions": evaluation.suggestions,
                "location": evaluation.resume.location,
                "created_at": evaluation.created_at.isoformat()
            })
        
        # Sort by score (descending)
        shortlisted.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "shortlist_criteria": {
                "min_score": min_score,
                "job_id": job_id
            },
            "total_shortlisted": len(shortlisted),
            "shortlisted_candidates": shortlisted
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get shortlisted resumes: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
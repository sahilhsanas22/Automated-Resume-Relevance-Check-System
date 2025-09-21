from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from app.db import models
from app.utils import dumps_json, loads_json


# Jobs

def create_job(db: Session, *, title: str, jd_text: str, must_skills: List[str], nice_skills: List[str], qualifications: str = "", location: str = "") -> models.Job:
    job = models.Job(
        title=title.strip(),
        jd_text=jd_text,
        must_skills_json=dumps_json([s.strip() for s in must_skills if s.strip()]),
        nice_skills_json=dumps_json([s.strip() for s in nice_skills if s.strip()]),
        qualifications=qualifications,
        location=location,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session) -> List[models.Job]:
    return db.query(models.Job).order_by(models.Job.created_at.desc()).all()


def get_job(db: Session, job_id: int) -> Optional[models.Job]:
    return db.query(models.Job).filter(models.Job.id == job_id).first()


# Resumes

def create_resume(db: Session, *, student_name: str, file_name: str, text: str, location: str = "") -> models.Resume:
    resume = models.Resume(
        student_name=student_name,
        file_name=file_name,
        text=text,
        location=location,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes(db: Session) -> List[models.Resume]:
    return db.query(models.Resume).order_by(models.Resume.created_at.desc()).all()


# Evaluations

def create_evaluation(db: Session, *, job_id: int, resume_id: int, score: float, verdict: str, missing: List[str], suggestions: str = "") -> models.Evaluation:
    # Validate required fields
    if not job_id:
        raise ValueError("job_id is required for evaluation")
    if not resume_id:
        raise ValueError("resume_id is required for evaluation")
    
    ev = models.Evaluation(
        job_id=job_id,
        resume_id=resume_id,
        score=float(score),
        verdict=verdict,
        missing_json=dumps_json(missing),
        suggestions=suggestions,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def list_evaluations(
    db: Session,
    *,
    job_id: Optional[int] = None,
    min_score: Optional[float] = None,
    location: Optional[str] = None,
) -> List[models.Evaluation]:
    q = db.query(models.Evaluation)
    if job_id:
        q = q.filter(models.Evaluation.job_id == job_id)
    if min_score is not None:
        q = q.filter(models.Evaluation.score >= float(min_score))
    if location:
        # join to resumes table for location filter
        q = q.join(models.Resume).filter(models.Resume.location.ilike(f"%{location}%"))
    q = q.order_by(models.Evaluation.score.desc(), models.Evaluation.created_at.desc())
    return q.all()


# Student Applications

def create_student_application(
    db: Session, 
    *, 
    job_id: int, 
    student_name: str, 
    email: str, 
    phone: str = "", 
    location: str = "", 
    resume_file_name: str, 
    resume_text: str, 
    cover_letter: str = ""
) -> models.StudentApplication:
    application = models.StudentApplication(
        job_id=job_id,
        student_name=student_name.strip(),
        email=email.strip().lower(),
        phone=phone.strip(),
        location=location.strip(),
        resume_file_name=resume_file_name,
        resume_text=resume_text,
        cover_letter=cover_letter,
        status="pending"
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def list_student_applications(
    db: Session,
    *,
    job_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[models.StudentApplication]:
    q = db.query(models.StudentApplication)
    if job_id:
        q = q.filter(models.StudentApplication.job_id == job_id)
    if status:
        q = q.filter(models.StudentApplication.status == status)
    q = q.order_by(models.StudentApplication.created_at.desc())
    return q.all()


def get_student_application(db: Session, application_id: int) -> Optional[models.StudentApplication]:
    return db.query(models.StudentApplication).filter(models.StudentApplication.id == application_id).first()


def update_application_status(db: Session, application_id: int, status: str) -> Optional[models.StudentApplication]:
    application = get_student_application(db, application_id)
    if application:
        application.status = status
        db.commit()
        db.refresh(application)
    return application

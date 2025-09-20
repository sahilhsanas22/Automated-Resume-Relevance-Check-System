from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base, engine


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    jd_text = Column(Text, nullable=False)
    must_skills_json = Column(Text)  # JSON array (string)
    nice_skills_json = Column(Text)  # JSON array (string)
    qualifications = Column(Text)
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    evaluations = relationship("Evaluation", back_populates="job", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(255))
    file_name = Column(String(512))
    text = Column(Text, nullable=False)
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    evaluations = relationship("Evaluation", back_populates="resume", cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    score = Column(Float, nullable=False)
    verdict = Column(String(32), nullable=False)
    missing_json = Column(Text)  # JSON array (string)
    suggestions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="evaluations")
    resume = relationship("Resume", back_populates="evaluations")


# Create tables if not exist
Base.metadata.create_all(bind=engine)

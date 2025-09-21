from typing import List, Tuple
from sqlalchemy.orm import Session

from app.db import crud, models
from app.utils import loads_json
from app.nlp.scoring import (
    hard_match_score,
    soft_match_score,
    weighted_score,
    verdict_for_score,
    suggestions_for_missing,
)
from app.services.llm_evaluator import llm_evaluator
from app.nlp.advanced_processor import text_processor


def evaluate_resume_against_job(db: Session, job: models.Job, resume: models.Resume) -> models.Evaluation:
    """
    Enhanced evaluation with LLM integration and advanced text processing
    """
    # Validate that resume has been saved to database
    if not resume.id:
        raise ValueError("Resume must be saved to database before evaluation. Use crud.create_resume() to save it first.")
    
    must = loads_json(job.must_skills_json) or []
    nice = loads_json(job.nice_skills_json) or []

    # Basic hybrid scoring
    hard, missing, _presence = hard_match_score(resume.text, must, nice)
    soft = soft_match_score(resume.text, job.jd_text)
    
    # LLM-enhanced scoring if available
    llm_score = soft  # Default to basic soft score
    enhanced_suggestions = suggestions_for_missing(missing)
    
    try:
        # Get LLM evaluation
        llm_result = llm_evaluator.evaluate_with_llm(resume.text, job.jd_text)
        
        # Blend LLM score with traditional soft score (70% LLM, 30% traditional)
        if llm_result.semantic_score > 0:
            llm_score = 0.7 * llm_result.semantic_score + 0.3 * soft
        
        # Enhanced suggestions from LLM
        if llm_result.improvement_suggestions:
            enhanced_suggestions = " | ".join(llm_result.improvement_suggestions[:3])
        
        # Add missing skills from LLM analysis
        if llm_result.skill_gaps:
            missing.extend([skill for skill in llm_result.skill_gaps if skill not in missing])
            missing = missing[:10]  # Limit to top 10
    
    except Exception as e:
        print(f"LLM evaluation failed, using fallback: {e}")
    
    # Extract enhanced entities for better missing skill detection
    try:
        entities = text_processor.extract_entities(resume.text)
        
        # Add extracted skills to improve matching
        extracted_skills = [skill.lower() for skill in entities.skills]
        
        # Re-evaluate missing skills considering extracted entities
        refined_missing = []
        for skill in missing:
            if skill.lower() not in extracted_skills:
                refined_missing.append(skill)
        
        missing = refined_missing
    except Exception as e:
        print(f"Advanced text processing failed: {e}")
    
    # Calculate final score
    final = weighted_score(hard, llm_score)
    verdict = verdict_for_score(final)

    return crud.create_evaluation(
        db,
        job_id=job.id,
        resume_id=resume.id,
        score=final,
        verdict=verdict,
        missing=missing,
        suggestions=enhanced_suggestions,
    )

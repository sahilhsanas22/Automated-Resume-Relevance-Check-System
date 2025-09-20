import re
from typing import Dict, List, Tuple

from app.nlp.keyword_match import keyword_presence
from app.nlp.embeddings import embedding_similarity
from app.config import HARD_MATCH_WEIGHT, SOFT_MATCH_WEIGHT, VERDICT_THRESHOLDS


def hard_match_score(resume_text: str, must_skills: List[str], nice_skills: List[str]) -> Tuple[float, List[str], Dict[str, bool]]:
    """
    Returns:
      - hard_score in [0,1]
      - missing_must (list of missing must-have skills)
      - presence_map for all skills
    """
    must_presence = keyword_presence(resume_text, must_skills)
    nice_presence = keyword_presence(resume_text, nice_skills) if nice_skills else {}

    must_total = max(1, len([s for s in must_skills if s.strip()]))
    must_hit = sum(1 for k, v in must_presence.items() if v)
    nice_total = max(1, len([s for s in nice_skills if s.strip()]))
    nice_hit = sum(1 for k, v in nice_presence.items() if v)

    # Weighted: must-have counts more than nice-to-have (e.g., 80/20)
    must_component = (must_hit / must_total)
    nice_component = (nice_hit / nice_total) if nice_skills else 0.0
    hard = 0.8 * must_component + 0.2 * nice_component

    missing = [k for k, v in must_presence.items() if not v]
    presence_map = {**must_presence, **nice_presence}
    return hard, missing, presence_map


def soft_match_score(resume_text: str, jd_text: str) -> float:
    return float(embedding_similarity(jd_text, resume_text))


def weighted_score(hard: float, soft: float) -> float:
    score = HARD_MATCH_WEIGHT * hard + SOFT_MATCH_WEIGHT * soft
    return round(100.0 * max(0.0, min(1.0, score)), 2)


def verdict_for_score(score: float) -> str:
    if score >= VERDICT_THRESHOLDS["high"]:
        return "High"
    if score >= VERDICT_THRESHOLDS["medium"]:
        return "Medium"
    return "Low"


def suggestions_for_missing(missing: List[str]) -> str:
    if not missing:
        return "Good alignment. Consider highlighting quantifiable achievements and relevant projects."
    return (
        "Consider adding evidence of the following requirements: "
        + ", ".join(missing)
        + ". Include projects, internships, or certifications that demonstrate these skills."
    )

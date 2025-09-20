import re
from typing import Dict, List, Tuple

from app.nlp.skills import extract_candidate_skills


def parse_jd_freeform(text: str) -> Dict[str, List[str]]:
    """Heuristic extraction of must-have and nice-to-have skills from a JD text.
    This is a lightweight approach using a skill inventory and simple cues.
    """
    text_l = text.lower()
    # naive hints: lines with 'must', 'required', 'nice', 'preferred'
    lines = [l.strip() for l in text_l.splitlines() if l.strip()]
    must_lines, nice_lines = [], []
    for l in lines:
        if any(k in l for k in ["must have", "required", "requirements:", "mandatory"]):
            must_lines.append(l)
        if any(k in l for k in ["nice to have", "good to have", "preferred", "plus"]):
            nice_lines.append(l)
    # fallback: whole text
    must_text = "\n".join(must_lines) if must_lines else text_l
    nice_text = "\n".join(nice_lines) if nice_lines else text_l

    must_skills = extract_candidate_skills(must_text)
    nice_skills = [s for s in extract_candidate_skills(nice_text) if s not in must_skills]
    return {"must": must_skills, "nice": nice_skills}

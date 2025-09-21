import re
from typing import Dict, List, Tuple

from app.nlp.skills import extract_candidate_skills


def _extract_qualification_lines(text_l: str) -> List[str]:
    """Extract lines that likely contain qualification requirements."""
    lines = [l.strip() for l in text_l.splitlines() if l.strip()]
    quals = []
    for l in lines:
        if any(k in l for k in ["qualification", "qualifications", "education", "degree", "bachelor", "master", "phd", "experience:", "required experience"]):
            quals.append(l)
    return quals


def _extract_certifications(text_l: str) -> List[str]:
    """Heuristically extract certification mentions from JD text."""
    cert_patterns = [
        r'certified?\s+[\w\s]+(?:professional|specialist|expert|developer|administrator)',
        r'[\w\s]+\s+certification',
        r'aws\s+[\w\s]+(?:associate|professional)',
        r'microsoft\s+[\w\s]+(?:associate|expert)',
        r'google\s+[\w\s]+(?:associate|professional)',
        r'cisco\s+[\w\s]+(?:associate|professional)'
    ]
    found = []
    for pattern in cert_patterns:
        matches = re.findall(pattern, text_l, re.IGNORECASE)
        found.extend([m.strip() for m in matches])
    # Normalize duplicates (case-insensitive)
    norm = []
    seen = set()
    for c in found:
        k = c.lower()
        if k not in seen:
            seen.add(k)
            norm.append(c)
    return norm


def _requires_projects(text_l: str) -> bool:
    return any(k in text_l for k in ["project", "capstone", "portfolio"])  # coarse heuristic


def parse_jd_freeform(text: str) -> Dict[str, List[str]]:
    """Heuristic extraction of must-have and nice-to-have skills from a JD text.
    Additionally extracts qualifications, certifications, and whether projects are expected.
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

    # Additional extractions
    quals = _extract_qualification_lines(text_l)
    certs = _extract_certifications(text_l)
    needs_projects = _requires_projects(text_l)

    return {
        "must": must_skills,
        "nice": nice_skills,
        "qualifications": quals,
        "certifications": certs,
        "requires_projects": needs_projects,
    }

from typing import Tuple, List
import re

# A small, extendable skill inventory. In production, consider maintaining in DB.
DEFAULT_SKILLS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "ruby", "php", "rust", "scala", "kotlin",
    # Data / ML
    "sql", "mysql", "postgresql", "mongodb", "redis", "hadoop", "spark", "pandas", "numpy", "sklearn", "pytorch", "tensorflow",
    # Web / Cloud / DevOps
    "html", "css", "react", "angular", "vue", "node", "express", "django", "flask", "fastapi",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "jenkins", "github actions",
    # Security / QA
    "owasp", "pentest", "selenium", "cypress", "junit",
]


def normalize_token(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def extract_candidate_skills(text: str, extra_skills: List[str] = None) -> List[str]:
    tokens = set()
    text_norm = normalize_token(text)
    inventory = set(DEFAULT_SKILLS + (extra_skills or []))
    # Exact token and phrase presence
    for skill in inventory:
        if skill in text_norm:
            tokens.add(skill)
    return sorted(tokens)

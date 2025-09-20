from typing import List, Dict, Any
from rapidfuzz import fuzz
import re


def tokenize(text: str) -> List[str]:
    text = text.lower()
    # simple tokenization on non-word boundaries
    return re.findall(r"[a-zA-Z0-9+#.]+", text)


def keyword_presence(text: str, keywords: List[str], *, fuzzy_threshold: int = 85) -> Dict[str, bool]:
    """Return presence map of each keyword using exact or fuzzy partial match."""
    text_lower = text.lower()
    present = {}
    for kw in keywords:
        k = kw.strip().lower()
        if not k:
            continue
        if k in text_lower:
            present[kw] = True
            continue
        # fuzzy partial ratio on sliding windows is expensive; instead compare directly
        score = fuzz.partial_ratio(k, text_lower)
        present[kw] = score >= fuzzy_threshold
    return present

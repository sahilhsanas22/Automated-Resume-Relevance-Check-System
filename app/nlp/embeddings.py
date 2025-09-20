from typing import Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import EMBEDDINGS_MODEL, USE_EMBEDDINGS

try:
    from sentence_transformers import SentenceTransformer
    _st_model: Optional[SentenceTransformer] = None
except Exception:
    SentenceTransformer = None
    _st_model = None


def _get_st_model() -> Optional["SentenceTransformer"]:
    global _st_model
    if not USE_EMBEDDINGS:
        return None
    if SentenceTransformer is None:
        return None
    if _st_model is None:
        try:
            _st_model = SentenceTransformer(EMBEDDINGS_MODEL)
        except Exception:
            _st_model = None
    return _st_model


def embedding_similarity(text_a: str, text_b: str) -> float:
    """Return cosine similarity between two texts using embeddings if available; TF-IDF fallback."""
    model = _get_st_model()
    if model is not None:
        try:
            vecs = model.encode([text_a, text_b], normalize_embeddings=True)
            # cosine similarity of normalized vectors is dot product
            sim = float(np.dot(vecs[0], vecs[1]))
            return max(0.0, min(1.0, sim))
        except Exception:
            pass
    # Fallback to TF-IDF cosine
    try:
        tfidf = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
        X = tfidf.fit_transform([text_a, text_b])
        sim = cosine_similarity(X[0], X[1])[0, 0]
        return max(0.0, min(1.0, float(sim)))
    except Exception:
        return 0.0

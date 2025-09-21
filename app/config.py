DB_PATH = "data/app.db"

# Scoring weights
HARD_MATCH_WEIGHT = 0.6
SOFT_MATCH_WEIGHT = 0.4

# Verdict thresholds
VERDICT_THRESHOLDS = {
    "high": 75,
    "medium": 50,
}

# Embeddings configuration
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # used if available
USE_EMBEDDINGS = True  # set False to always fallback to TF-IDF

# Misc
APP_NAME = "AI Resume Evaluation Engine"

# Admin auth (read from environment; set in deployment)
import os
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

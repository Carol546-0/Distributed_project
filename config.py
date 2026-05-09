
# =========================
# LLM Configuration
# =========================

LLM_MODEL = "distilgpt2"
LLM_MAX_NEW_TOKENS = 10

# If True, HuggingFace will try to load model files from local cache only.
# Use False the first time you download the model.
LLM_LOCAL_FILES_ONLY = False

# =========================
# RAG Configuration
# =========================

RAG_TOP_K = 3

# =========================
# Worker / GPU Simulation
# =========================

WORKER_MAX_CAPACITY = 16

# =========================
# Master Configuration
# =========================

REQUEST_TIMEOUT = 600
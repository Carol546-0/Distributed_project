import os
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DOCS: List[str] = []
MODEL = None
INDEX = None
EMBEDDINGS = None


def _load_documents() -> List[str]:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_dir = os.path.join(base, "data", "rag_docs")

    docs = []

    if os.path.isdir(docs_dir):
        for filename in os.listdir(docs_dir):
            path = os.path.join(docs_dir, filename)

            if not os.path.isfile(path):
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        docs.append(content)
                        print(f"[RAG] Loaded document: {filename}", flush=True)
            except Exception as e:
                print(f"[RAG ERROR] Could not read {filename}: {e}", flush=True)

    if docs:
        return docs

    print("[RAG] No external docs found. Using fallback documents.", flush=True)

    return [
        "Load balancing distributes incoming requests across multiple compute nodes.",
        "Least-loaded routing sends new requests to the worker with the fewest active tasks.",
        "RAG retrieves relevant context from a knowledge base before LLM generation.",
        "LLM inference processes user queries and generates natural language answers.",
        "Fault tolerance allows the master to retry another worker if one fails.",
        "Parallel processing improves throughput by sending requests to multiple workers.",
        "Scalability is achieved by adding more worker containers or GPU nodes.",
        "GPU inference accelerates LLM generation using CUDA-enabled hardware."
    ]


def _get_model():
    global MODEL

    if MODEL is None:
        print("[RAG] Loading embedding model: all-MiniLM-L6-v2", flush=True)
        MODEL = SentenceTransformer("all-MiniLM-L6-v2")

    return MODEL


def _build_vector_db():
    global DOCS, INDEX, EMBEDDINGS

    if INDEX is not None:
        return

    DOCS = _load_documents()
    model = _get_model()

    print("[RAG] Creating document embeddings...", flush=True)

    EMBEDDINGS = model.encode(
        DOCS,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    dimension = EMBEDDINGS.shape[1]

    INDEX = faiss.IndexFlatIP(dimension)
    INDEX.add(EMBEDDINGS)

    print(f"[RAG] Vector DB ready with {len(DOCS)} documents", flush=True)


def retrieve_context(query: str, top_k: int = 3) -> str:
    global INDEX, DOCS

    _build_vector_db()

    model = _get_model()

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = INDEX.search(query_embedding, top_k)

    selected: List[Tuple[float, str]] = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        selected.append((float(score), DOCS[idx]))

    if not selected:
        return ""

    context = "\n\n".join(doc for score, doc in selected)

    print("[RAG] Retrieved context:", flush=True)
    for score, doc in selected:
        print(f"[RAG] Score={score:.3f} | {doc[:100]}...", flush=True)

    return context
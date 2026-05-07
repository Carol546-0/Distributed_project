import os
from typing import List

DOCS: List[str] = []


def _load_documents() -> List[str]:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_dir = os.path.join(base, "data", "rag_docs")

    if os.path.isdir(docs_dir):
        docs = []
        for filename in os.listdir(docs_dir):
            path = os.path.join(docs_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        docs.append(content)
            except Exception:
                pass

        if docs:
            return docs

    return [
        "Load balancing distributes incoming requests across multiple compute nodes.",
        "Least-loaded routing sends new requests to the worker with the fewest active tasks.",
        "RAG retrieves relevant context from a knowledge base before LLM generation.",
        "LLM inference processes user queries and generates natural language answers.",
        "Docker Compose runs the master node and multiple worker containers.",
        "Fault tolerance allows the master to retry another worker if one fails.",
        "Parallel processing improves throughput by sending requests to multiple workers.",
        "Scalability is achieved by adding more worker containers or GPU nodes."
    ]


def retrieve_context(query: str, top_k: int = 3) -> str:
    global DOCS

    if not DOCS:
        DOCS = _load_documents()

    query_words = set(query.lower().split())

    scored_docs = []
    for doc in DOCS:
        doc_words = set(doc.lower().split())
        score = len(query_words & doc_words)
        scored_docs.append((score, doc))

    scored_docs.sort(reverse=True, key=lambda x: x[0])

    selected = [doc for score, doc in scored_docs[:top_k] if score > 0]

    if not selected:
        selected = DOCS[:top_k]

    return "\n\n".join(selected)
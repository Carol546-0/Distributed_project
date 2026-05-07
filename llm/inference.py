import logging
import time
import config

GENERATOR = None


def load_model():
    global GENERATOR

    if GENERATOR is not None:
        return

    try:
        from transformers import pipeline

        print(f"[LLM] Loading model: {config.LLM_MODEL}", flush=True)

        GENERATOR = pipeline(
            "text-generation",
            model=config.LLM_MODEL
        )

        print("[LLM] Model loaded successfully", flush=True)

    except Exception as e:
        logging.exception("[LLM] Failed to initialize transformers pipeline")
        print(f"[LLM ERROR] {e}", flush=True)
        GENERATOR = None


def run_llm(query: str, context: str = "") -> str:
    start = time.perf_counter()

    load_model()

    if GENERATOR is None:
        return "LLM unavailable."

    prompt = f"""Use the context to answer in one short sentence.

Context:
{context}

Question:
{query}

Short answer:
"""

    try:
        output = GENERATOR(
            prompt,
            max_new_tokens=20,
            do_sample=True,
            temperature=0.7,
            repetition_penalty=1.8,
            top_k=50,
            top_p=0.95,
            return_full_text=False,
            pad_token_id=GENERATOR.tokenizer.eos_token_id,
        )

        text = output[0]["generated_text"]

        text = text.replace("Short answer:", "").replace("Answer:", "").strip()

        elapsed = time.perf_counter() - start
        print(f"[LLM] Finished inference in {elapsed:.2f}s", flush=True)

        return text

    except Exception as e:
        logging.exception("[LLM] Generation failed")
        print(f"[LLM ERROR] {e}", flush=True)
        return "LLM generation failed."
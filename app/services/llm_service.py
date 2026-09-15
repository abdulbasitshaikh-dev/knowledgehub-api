import os
from functools import lru_cache

from google import genai


@lru_cache(maxsize=1)
def get_llm_config() -> tuple[str, int]:
    return ("gemini-3.6-flash", 1024)


@lru_cache(maxsize=1)
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    return genai.Client(api_key=api_key)


def generate_answer(question: str, context: str) -> str:
    model_name, max_tokens = get_llm_config()

    response = get_gemini_client().models.generate_content(
        model=model_name,
        contents=(
            "You are a helpful knowledge assistant.\n"
            "Answer the user's question using only the provided context.\n"
            "Give a complete, concise answer and do not stop mid-sentence.\n"
            "If the context does not contain enough information to answer "
            "the question, say that you don't have enough information.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        ),
        config={
            "max_output_tokens": max_tokens,
        },
    )

    return response.text.strip()
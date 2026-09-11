from functools import lru_cache
import os 

from ollama import Client


@lru_cache(maxsize=1)
def get_llm_config() -> tuple[str, int]:
    return ("llama3.2:3b", 128)


@lru_cache(maxsize=1)
def get_ollama_client() -> Client:
    return Client(
        host=os.getenv(
            "OLLAMA_HOST",
            "http://host.docker.internal:11434",
        )
    )


def generate_answer(
    question: str,
    context: str,
) -> str:
    model_name, max_tokens = get_llm_config()

    response = get_ollama_client().chat(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful knowledge assistant. "
                    "Answer the user's question using only "
                    "the provided context. "
                    "If the context does not contain enough "
                    "information to answer the question, "
                    "say that you don't have enough information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n\n"
                    f"{context}\n\n"
                    f"Question:\n\n"
                    f"{question}"
                ),
            },
        ],
        options={
            "num_predict": 256,
        },
    )

    return response["message"]["content"].strip()
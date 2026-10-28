import pytest
import requests

from src.answer_generator import generate_answer


MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/tags"


@pytest.fixture(scope="module", autouse=True)
def require_ollama():
    """Skip integration tests if Ollama is unavailable."""
    try:
        response = requests.get(OLLAMA_URL, timeout=3)
        response.raise_for_status()
        models = response.json().get("models", [])
    except (requests.RequestException, ValueError):
        pytest.skip("Ollama is not running or its API is unavailable.")

    if not any(model.get("name") == MODEL for model in models):
        pytest.skip(f"Required Ollama model '{MODEL}' is not installed.")


def test_ollama_generates_answer():
    """Verify that Ollama generates an answer using retrieved document text."""
    chunks = [
        {
            "source": "sample.pdf",
            "page": 2,
            "text": (
                "Machine learning is a branch of artificial intelligence "
                "that enables systems to learn patterns from data."
            ),
            "score": 0.85,
        }
    ]

    answer = generate_answer(
        "What is machine learning?",
        chunks,
        model=MODEL,
    )

    assert isinstance(answer, str)
    assert answer.strip(), "Ollama returned an empty answer."
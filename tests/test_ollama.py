
from src.answer_generator import generate_answer

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
    model="llama3.2:3b",
)

print("\nDocuMind AI answer:\n")
print(answer)


import pytest

from src.retriever import SemanticRetriever


@pytest.fixture(scope="module")
def retriever():
    return SemanticRetriever()


def test_retriever_finds_relevant_chunk(retriever):
    chunks = [
        {
            "chunk_id": 0,
            "page": 1,
            "text": "Python is a programming language used for software development.",
        },
        {
            "chunk_id": 1,
            "page": 4,
            "text": "Photosynthesis allows plants to convert sunlight into chemical energy.",
        },
        {
            "chunk_id": 2,
            "page": 7,
            "text": "Neural networks learn patterns from data during model training.",
        },
    ]

    retriever.build_index(chunks)
    results = retriever.search("How do plants use sunlight?", top_k=2)

    assert len(results) == 2
    assert results[0]["chunk_id"] == 1
    assert "page" in results[0]
    assert "score" in results[0]


def test_search_rejects_blank_query(retriever):
    with pytest.raises(ValueError):
        retriever.search("   ")


def test_build_index_rejects_empty_chunks(retriever):
    with pytest.raises(ValueError):
        retriever.build_index([])

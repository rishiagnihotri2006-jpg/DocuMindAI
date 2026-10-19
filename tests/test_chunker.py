
import pytest

from src.chunker import chunk_pages


def test_short_page_creates_one_chunk():
    pages = [{"page": 1, "text": "one two three four"}]

    chunks = chunk_pages(pages, chunk_size=5, overlap=1)

    assert len(chunks) == 1
    assert chunks[0]["page"] == 1
    assert chunks[0]["text"] == "one two three four"


def test_long_page_creates_overlapping_chunks():
    words = [f"word{i}" for i in range(12)]
    pages = [{"page": 2, "text": " ".join(words)}]

    chunks = chunk_pages(pages, chunk_size=5, overlap=2)

    assert len(chunks) == 4
    assert chunks[0]["text"].endswith("word4")
    assert chunks[1]["text"].startswith("word3")
    assert chunks[0]["page"] == 2


def test_each_page_keeps_its_page_number():
    pages = [
        {"page": 1, "text": "first page"},
        {"page": 4, "text": "fourth page"},
    ]

    chunks = chunk_pages(pages, chunk_size=10, overlap=2)

    assert chunks[0]["page"] == 1
    assert chunks[1]["page"] == 4


def test_invalid_chunk_settings_raise_error():
    with pytest.raises(ValueError):
        chunk_pages([], chunk_size=0)

    with pytest.raises(ValueError):
        chunk_pages([], chunk_size=5, overlap=5)


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 100
) -> list[dict]:
    """
    Split extracted page text into overlapping chunks.

    chunk_size and overlap are measured in words.

    Each chunk retains its source page number.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size.")

    chunks = []
    chunk_id = 0
    step = chunk_size - overlap

    for page_data in pages:
        words = page_data["text"].split()
        page_number = page_data["page"]

        for start in range(0, len(words), step):
            chunk_words = words[start:start + chunk_size]

            if not chunk_words:
                break

            chunks.append({
                "chunk_id": chunk_id,
                "page": page_number,
                "text": " ".join(chunk_words)
            })
            chunk_id += 1

            if start + chunk_size >= len(words):
                break

    return chunks


from pathlib import Path
import pymupdf


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from a PDF, preserving page numbers.

    Returns:
        A list of dictionaries, one per page:
        [{"page": 1, "text": "..."}, ...]
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("The provided file must be a PDF.")

    pages = []

    with pymupdf.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page": page_number,
                    "text": text
                })

    return pages

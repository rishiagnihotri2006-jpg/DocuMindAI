
import pytest
import pymupdf

from src.pdf_loader import extract_text_from_pdf


def create_test_pdf(path):
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "DocuMind AI test document.")
        document.save(path)


def test_extracts_text_and_page_number(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    create_test_pdf(pdf_path)

    result = extract_text_from_pdf(str(pdf_path))

    assert len(result) == 1
    assert result[0]["page"] == 1
    assert "DocuMind AI test document." in result[0]["text"]


def test_missing_pdf_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(str(tmp_path / "missing.pdf"))


def test_non_pdf_file_raises_error(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("This is not a PDF.")

    with pytest.raises(ValueError):
        extract_text_from_pdf(str(file_path))

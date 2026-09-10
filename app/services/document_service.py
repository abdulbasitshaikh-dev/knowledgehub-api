from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text(file_path: str, content_type: str) -> str:
    path = Path(file_path)

    if content_type == "text/plain":
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    if content_type == "application/pdf":
        reader = PdfReader(path)

        text = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

        return "\n".join(text)

    if content_type == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        document = DocxDocument(path)

        paragraphs = []

        for paragraph in document.paragraphs:
            if paragraph.text:
                paragraphs.append(paragraph.text)

        return "\n".join(paragraphs)

    raise ValueError("Unsupported document type")
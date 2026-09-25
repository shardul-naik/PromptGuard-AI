from io import BytesIO

from pypdf import PdfReader


def parse_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF.
    """

    reader = PdfReader(BytesIO(file_bytes))

    pages: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n\n".join(pages).strip()


def normalize_text(text: str) -> str:
    """
    Basic whitespace normalization.
    """

    return " ".join(text.split())
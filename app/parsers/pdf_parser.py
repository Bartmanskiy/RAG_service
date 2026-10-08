from io import BytesIO

from pypdf import PdfReader


def parse_pdf(content: bytes) -> list[dict]:
    reader = PdfReader(BytesIO(content))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        text = text.strip()

        if not text:
            continue

        pages.append(
            {
                "text": text,
                "page": page_number,
            }
        )

    return pages

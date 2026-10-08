from pathlib import Path

from app.parsers.md_parser import parse_md
from app.parsers.pdf_parser import parse_pdf
from app.parsers.txt_parser import parse_txt


PARSERS = {
    ".pdf": parse_pdf,
    ".txt": parse_txt,
    ".md": parse_md,
}


def parse_document(
    filename: str,
    content: bytes,
) -> list[dict]:
    extension = Path(filename).suffix.lower()

    parser = PARSERS.get(extension)

    if parser is None:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return parser(content)


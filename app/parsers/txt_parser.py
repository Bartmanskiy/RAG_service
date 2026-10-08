def parse_txt(content: bytes) -> list[dict]:
    text = content.decode("utf-8")

    return [
        {
            "text": text.strip(),
            "page": None,
        }
    ]

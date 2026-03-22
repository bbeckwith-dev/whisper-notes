from pathlib import Path


def read_document(path: Path) -> str:
    """Read text content from a document file."""
    suffix = path.suffix.lower()

    if suffix in (".md", ".txt"):
        return path.read_text(encoding="utf-8")

    if suffix == ".docx":
        from docx import Document
        doc = Document(str(path))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if suffix == ".rtf":
        from striprtf.striprtf import rtf_to_text
        return rtf_to_text(path.read_text(encoding="utf-8"))

    raise ValueError(f"Unsupported format: {suffix}")

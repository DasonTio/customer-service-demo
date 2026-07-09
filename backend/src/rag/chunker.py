from src.rag.constants import CHUNK_OVERLAP_PARAGRAPHS, CHUNK_TARGET_CHARS


def chunk_text(
    text: str,
    target_chars: int = CHUNK_TARGET_CHARS,
    overlap_paragraphs: int = CHUNK_OVERLAP_PARAGRAPHS,
) -> list[str]:
    """Split text into chunks of roughly ``target_chars``, on paragraph boundaries.

    Consecutive chunks share ``overlap_paragraphs`` trailing paragraphs so that
    context spanning a boundary is retrievable from either side. A single
    paragraph longer than ``target_chars`` becomes its own chunk unsplit.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs:
        if current and current_len + len(paragraph) > target_chars:
            chunks.append("\n\n".join(current))
            current = current[-overlap_paragraphs:] if overlap_paragraphs else []
            current_len = sum(len(p) for p in current)
        current.append(paragraph)
        current_len += len(paragraph)

    chunks.append("\n\n".join(current))
    return chunks

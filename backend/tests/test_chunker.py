from src.rag.chunker import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("\n\n  \n\n") == []


def test_short_text_is_single_chunk():
    text = "Hello world.\n\nSecond paragraph."
    assert chunk_text(text) == ["Hello world.\n\nSecond paragraph."]


def test_splits_on_paragraph_boundaries_near_target():
    paragraphs = [f"Paragraph {i} " + "x" * 300 for i in range(10)]
    chunks = chunk_text("\n\n".join(paragraphs), target_chars=1000)
    assert len(chunks) > 1
    for chunk in chunks:
        # Each chunk stays in the same order and keeps whole paragraphs.
        assert chunk.split("\n\n")[0].startswith("Paragraph")


def test_consecutive_chunks_overlap_by_one_paragraph():
    paragraphs = [f"P{i} " + "x" * 400 for i in range(6)]
    chunks = chunk_text("\n\n".join(paragraphs), target_chars=900, overlap_paragraphs=1)
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        last_paragraph_of_prev = prev.split("\n\n")[-1]
        assert nxt.split("\n\n")[0] == last_paragraph_of_prev


def test_oversized_paragraph_becomes_own_chunk():
    huge = "y" * 5000
    text = f"small one\n\n{huge}\n\nsmall two"
    chunks = chunk_text(text, target_chars=1000, overlap_paragraphs=0)
    assert any(chunk == huge for chunk in chunks)


def test_all_content_preserved():
    paragraphs = [f"Unique paragraph {i}" for i in range(20)]
    chunks = chunk_text("\n\n".join(paragraphs), target_chars=100)
    joined = "\n\n".join(chunks)
    for paragraph in paragraphs:
        assert paragraph in joined

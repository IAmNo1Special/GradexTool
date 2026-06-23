from typing import Any
"""Helper functions for the 'scripts' directory."""


def to_sentence_case(text: str) -> str:
    """Capitalize the first letter of each sentence in a text while preserving internal capitalization.

    Args:
        text: The text to convert to sentence case.

    Returns:
        The text with the first letter of each sentence capitalized.
    """
    if not text:
        return text

    sentences = text.split(". ")
    processed_sentences = []
    for s in sentences:
        if s:
            processed_sentences.append(s[0].upper() + s[1:])
        else:
            processed_sentences.append(s)

    return ". ".join(processed_sentences)

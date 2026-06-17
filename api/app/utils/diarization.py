"""
Helper functions for processing diarization data.
"""


def build_speaker_segments(words: list[dict]) -> list[dict]:
    """
    Group consecutive words by speaker into text segments.
    Returns list of {speaker, start, end, text}.
    """
    if not words:
        return []

    segments: list[dict] = []
    current_speaker = words[0].get("speaker")
    current_words: list[dict] = []

    for word in words:
        speaker = word.get("speaker")
        if speaker == current_speaker:
            current_words.append(word)
        else:
            segments.append(_flush_segment(current_speaker, current_words))
            current_speaker = speaker
            current_words = [word]

    if current_words:
        segments.append(_flush_segment(current_speaker, current_words))

    return segments


def _flush_segment(speaker: int | None, words: list[dict]) -> dict:
    """
    Create a single speaker segment from a list of words.
    """
    return {
        "speaker": speaker if speaker is not None else 0,
        "start": words[0].get("start", 0.0),
        "end": words[-1].get("end", 0.0),
        "text": " ".join(w.get("punctuated_word", w.get("word", "")) for w in words),
    }
"""
matching/semantic_matcher.py
Embedding-based similarity matching. Catches cases where a skill is phrased
differently in the resume than in the job description/role list (e.g.
resume says "led a cross-functional team" and JD says "team leadership" —
zero shared words, but semantically the same thing).

Uses sentence-transformers (all-MiniLM-L6-v2): small, fast, fully local
after the first download, no API costs.
"""

from functools import lru_cache

_model = None


def _get_model():
    """Lazily loads the embedding model (first call downloads ~80MB once, then cached)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def overall_semantic_similarity(resume_text, jd_text):
    """
    Returns a 0-100 semantic similarity score between the whole resume
    and the whole job description. Useful as a top-line "how relevant
    is this resume to this JD overall" signal, separate from exact
    keyword matching.
    """
    from sentence_transformers import util

    model = _get_model()
    embeddings = model.encode([resume_text, jd_text], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

    # cosine similarity is -1..1, but in practice for real text it's ~0.2-0.9
    # so we rescale to a more intuitive 0-100 range
    score = max(0, min(100, (similarity + 0.1) / 1.0 * 100))
    return round(score, 1)


def semantic_match_missing_keywords(resume_text, missing_keywords, similarity_threshold=0.55):
    """
    For keywords the exact matcher marked as 'missing', checks if the resume
    contains a semantically similar phrase elsewhere (e.g. resume has
    "worked with stakeholders across departments" which is semantically
    close to missing keyword "stakeholder management").

    Splits resume into sentences and compares each missing keyword against
    every sentence, keeping keywords whose best sentence match clears the
    similarity threshold. Returns (recovered_matches, still_missing).
    """
    if not missing_keywords:
        return [], []

    from sentence_transformers import util
    import re

    model = _get_model()

    sentences = [s.strip() for s in re.split(
        r'[.\n•]', resume_text) if len(s.strip()) > 10]
    if not sentences:
        return [], missing_keywords

    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    keyword_embeddings = model.encode(missing_keywords, convert_to_tensor=True)

    recovered = []
    still_missing = []

    similarities = util.cos_sim(keyword_embeddings, sentence_embeddings)

    for i, keyword in enumerate(missing_keywords):
        best_score = similarities[i].max().item()
        if best_score >= similarity_threshold:
            recovered.append(keyword)
        else:
            still_missing.append(keyword)

    return recovered, still_missing

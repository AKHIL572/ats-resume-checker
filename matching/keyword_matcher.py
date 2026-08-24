"""
matching/keyword_matcher.py
Stemmed, phrase-aware keyword matching. Fixes the bugs from the original
JS version:
- word boundary issues (e.g. "r" matching inside "reporting")
- no stemming (e.g. "managed" vs "management")
- no phrase-level matching for multi-word skills
"""

import re
from nltk.stem import PorterStemmer

from matching.skill_taxonomy import resolve_synonym

# Note: PorterStemmer is a pure rule-based algorithm and needs no downloaded
# data, unlike nltk.corpus.stopwords/punkt (which we used to rely on before
# switching JD parsing over to spaCy's grammar-based filtering below).

_nlp = None


def _get_spacy_model():
    """Lazily loads the spaCy English model (only needed for JD parsing)."""
    global _nlp
    if _nlp is None:
        import spacy
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


stemmer = PorterStemmer()

# Common tech/business acronyms that JD parsing must NOT drop just for being
# short. Without this, real skills like SQL, AWS, BI, R would be silently
# ignored since the JD word-extraction regex only grabs 4+ letter words.
IMPORTANT_SHORT_TERMS = {
    "sql", "api", "aws", "gcp", "bi", "r", "js", "ui", "ux", "hr", "kpi",
    "crm", "erp", "sap", "etl", "css", "sla", "roi", "vba", "aiml", "ml",
    "ai", "qa", "ci", "cd",
}


def stem_words(text):
    """Stem every word in a block of text, return as a set for fast lookup."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return set(stemmer.stem(w) for w in words)


def contains_phrase(text_lower, phrase):
    """Word-boundary exact phrase match (avoids partial-word false positives)."""
    pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
    return re.search(pattern, text_lower) is not None


def contains_keyword(text_lower, stemmed_text_words, keyword):
    """
    Checks if a single keyword appears in text.
    - Short keywords/acronyms (<=3 chars, e.g. 'sql', 'r', 'bi'): exact
      word-boundary match only, no stemming (prevents 'r' matching inside
      'reporting').
    - Longer keywords: stemmed match so 'managed'/'management'/'managing'
      all count as the same skill.
    """
    keyword_lower = keyword.lower()

    if len(keyword_lower) <= 3:
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        return re.search(pattern, text_lower) is not None

    stemmed_keyword = stemmer.stem(keyword_lower)
    return stemmed_keyword in stemmed_text_words


def match_skills(resume_text, role_data):
    """Matches resume text against a role's keyword/phrase list from skills_db.json."""
    text_lower = resume_text.lower()
    stemmed_text_words = stem_words(resume_text)

    matched = []
    missing = []

    for kw in role_data.get("keywords", []):
        if contains_keyword(text_lower, stemmed_text_words, kw):
            matched.append(kw)
        else:
            synonym = resolve_synonym(kw, role_data)
            if synonym and contains_phrase(text_lower, synonym):
                matched.append(kw)
            else:
                missing.append(kw)

    for phrase in role_data.get("phrases", []):
        if contains_phrase(text_lower, phrase):
            matched.append(phrase)
        else:
            missing.append(phrase)

    total = len(matched) + len(missing)
    score = (len(matched) / total * 100) if total > 0 else 0

    return {"matched": matched, "missing": missing, "score": round(score, 1)}


def extract_jd_candidates(job_description):
    """
    Extracts real skill/requirement terms from a job description using
    spaCy's grammar tagging, instead of a crude "any 4+ letter word not
    in a small stopword list" approach.

    Real skills are almost always nouns, proper nouns, or noun phrases
    ("testing", "SQL", "automation framework"). Generic JD filler is
    almost always verbs, adverbs, or adjectives ("looking", "actively",
    "oriented", "ensuring") — spaCy's part-of-speech tags let us filter
    those out reliably, rather than trying to hardcode every filler word
    in the English language.
    """
    nlp = _get_spacy_model()
    doc = nlp(job_description)

    candidates = []

    # Single important terms: nouns and proper nouns only (skips verbs/
    # adjectives/adverbs that are just generic sentence filler)
    for token in doc:
        if token.is_stop or not token.is_alpha:
            continue
        word_lower = token.text.lower()
        if word_lower in IMPORTANT_SHORT_TERMS:
            candidates.append(word_lower)
        elif token.pos_ in ("NOUN", "PROPN") and len(word_lower) > 3:
            candidates.append(token.lemma_.lower())

    # Multi-word noun phrases (e.g. "test case design", "quality assurance")
    for chunk in doc.noun_chunks:
        # Strip leading determiners/pronouns like "the", "a", "our"
        words = [t for t in chunk if not t.is_stop or t.text.lower()
                 in IMPORTANT_SHORT_TERMS]
        if 1 < len(words) <= 4:
            phrase = " ".join(t.text.lower() for t in words)
            if len(phrase) > 4:
                candidates.append(phrase)

    # Preserve order, dedupe
    return list(dict.fromkeys(candidates))


def match_job_description(resume_text, job_description):
    """
    Extracts meaningful keywords/phrases from a pasted job description
    using spaCy POS filtering, then checks how many appear in the resume.
    """
    text_lower = resume_text.lower()
    stemmed_text_words = stem_words(resume_text)

    candidates = extract_jd_candidates(job_description)

    matched = []
    missing = []
    for kw in candidates:
        is_match = (
            contains_phrase(text_lower, kw) if " " in kw
            else contains_keyword(text_lower, stemmed_text_words, kw)
        )
        if is_match:
            matched.append(kw)
        else:
            missing.append(kw)

    total = len(matched) + len(missing)
    score = (len(matched) / total * 100) if total > 0 else 0

    return {"matched": matched[:25], "missing": missing[:20], "score": round(score, 1)}

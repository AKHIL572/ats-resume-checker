"""
matching/skill_taxonomy.py
Loads the skills database (data/skills_db.json) and provides
helper functions for role lookup and synonym resolution.
"""

import json
import os

_SKILLS_DB_CACHE = None


def load_skills_db(path=None):
    """Loads and caches the skills database JSON."""
    global _SKILLS_DB_CACHE
    if _SKILLS_DB_CACHE is not None:
        return _SKILLS_DB_CACHE

    if path is None:
        path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), "data", "skills_db.json")

    with open(path, "r", encoding="utf-8") as f:
        _SKILLS_DB_CACHE = json.load(f)

    return _SKILLS_DB_CACHE


def get_role_names(path=None):
    """Returns list of available job roles."""
    db = load_skills_db(path)
    return sorted(db.keys())


def get_role_data(role_name, path=None):
    """Returns the keyword/phrase/synonym data for a given role."""
    db = load_skills_db(path)
    return db.get(role_name, {"keywords": [], "phrases": [], "synonyms": {}})


def resolve_synonym(term, role_data):
    """
    Given a term, returns its expanded synonym form if one exists
    for this role (e.g. 'bi' -> 'business intelligence'), else returns None.
    """
    synonyms = role_data.get("synonyms", {})
    return synonyms.get(term.lower())

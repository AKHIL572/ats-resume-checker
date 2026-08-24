"""
scoring/score_engine.py
Combines format checks, content checks, and keyword/semantic matching
into one final weighted ATS score, plus a prioritized recommendations list.

Weights (tunable):
- Keywords/skills match: 40%
- Content quality:        25%
- Format/ATS structure:   20%
- (Contact info is folded into format checks already)
"""

WEIGHTS = {
    "keywords": 0.40,
    "content": 0.25,
    "format": 0.20,
    "semantic": 0.15,   # only used if semantic matching was run, else redistributed
}


def calculate_overall_score(format_result, content_result, keyword_result, semantic_score=None):
    """
    format_result / content_result: {"checks": [...], "score": float}
    keyword_result: {"matched": [...], "missing": [...], "score": float}
    semantic_score: float 0-100, or None if semantic matching wasn't run
    """
    if semantic_score is not None:
        overall = (
            keyword_result["score"] * WEIGHTS["keywords"] +
            content_result["score"] * WEIGHTS["content"] +
            format_result["score"] * WEIGHTS["format"] +
            semantic_score * WEIGHTS["semantic"]
        )
    else:
        # redistribute semantic's weight proportionally across the other three
        redistribute = WEIGHTS["semantic"] / 3
        overall = (
            keyword_result["score"] * (WEIGHTS["keywords"] + redistribute) +
            content_result["score"] * (WEIGHTS["content"] + redistribute) +
            format_result["score"] * (WEIGHTS["format"] + redistribute)
        )

    return round(overall, 1)


def generate_recommendations(format_result, content_result, keyword_result, top_n=5):
    """
    Builds a prioritized list of the most impactful things to fix,
    ordered: failures first, then warnings.
    """
    all_checks = []
    for c in format_result["checks"]:
        all_checks.append({**c, "category": "Format"})
    for c in content_result["checks"]:
        all_checks.append({**c, "category": "Content"})

    failing = [c for c in all_checks if c["status"] == "fail"]
    warning = [c for c in all_checks if c["status"] == "warning"]

    recommendations = []

    if keyword_result["missing"]:
        top_missing = ", ".join(keyword_result["missing"][:5])
        recommendations.append({
            "category": "Keywords",
            "status": "fail" if keyword_result["score"] < 50 else "warning",
            "name": "Missing Key Skills/Keywords",
            "message": f"Consider adding (if genuinely applicable): {top_missing}"
        })

    recommendations.extend(failing)
    recommendations.extend(warning)

    return recommendations[:top_n]


def get_score_verdict(overall_score):
    """Returns a headline verdict + description for the score."""
    if overall_score >= 80:
        return {
            "title": "Strong ATS Compatibility",
            "level": "good",
            "description": "This resume should pass most ATS systems and score well on relevant keyword checks."
        }
    elif overall_score >= 60:
        return {
            "title": "Good, With Room for Improvement",
            "level": "medium",
            "description": "Likely to pass ATS filters, but addressing the flagged issues will meaningfully improve ranking."
        }
    else:
        return {
            "title": "Needs Significant Improvement",
            "level": "low",
            "description": "This resume risks being filtered out or ranked low by ATS. Prioritize the recommendations below."
        }

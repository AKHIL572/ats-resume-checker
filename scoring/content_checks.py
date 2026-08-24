"""
scoring/content_checks.py
Checks resume content quality: length, section completeness,
bullet point usage, and quantified/metric-driven achievements.
"""

import re

from parser.section_splitter import get_section_completeness


def run_content_checks(parsed_resume):
    """
    parsed_resume: the dict returned by parser.resume_parser.parse_resume()
    Returns {"checks": [...], "score": float}
    """
    checks = []
    text = parsed_resume["raw_text"]
    word_count = parsed_resume["word_count"]

    # Content length
    has_enough_content = 200 <= word_count <= 1000
    checks.append({
        "name": "Content Length",
        "status": "pass" if has_enough_content else "warning",
        "message": f"{word_count} words — "
        + ("good length" if has_enough_content
           else "consider trimming (too long)" if word_count > 1000
           else "consider adding more detail (too short)")
    })

    # Standard section completeness
    section_info = get_section_completeness(parsed_resume["sections"])
    checks.append({
        "name": "Standard Sections",
        "status": "pass" if section_info["completeness_pct"] == 100 else "warning",
        "message": f"Found: {', '.join(section_info['found']) or 'none'}"
        + (f" | Missing: {', '.join(section_info['missing'])}" if section_info["missing"] else "")
    })

    # Bullet point usage
    bullet_count = len(re.findall(r'[•\-–—]\s', text))
    checks.append({
        "name": "Bullet Points Usage",
        "status": "pass" if bullet_count > 5 else "warning",
        "message": f"{bullet_count} bullet points found"
        + ("" if bullet_count > 5 else " — add more for scannability")
    })

    # Quantified achievements — numbers, percentages, currency, growth verbs
    has_metrics = bool(re.search(
        r'\d+%|\$\d+|₹\d+|\d+\s*(years?|months?)|increased|decreased|improved|reduced|\d+[,.]?\d*\s*(rows|users|records|requests)',
        text, re.IGNORECASE))
    checks.append({
        "name": "Quantified Achievements",
        "status": "pass" if has_metrics else "fail",
        "message": "Metrics/numbers found in achievements" if has_metrics
                   else "Add specific numbers (e.g. 'improved accuracy by 15%', 'processed 2M+ records')"
    })

    score = _calculate_score(checks)
    return {"checks": checks, "score": score}


def _calculate_score(checks):
    if not checks:
        return 0
    weight = 100 / len(checks)
    total = 0
    for c in checks:
        if c["status"] == "pass":
            total += weight
        elif c["status"] == "warning":
            total += weight * 0.5
    return round(total)

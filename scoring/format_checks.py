"""
scoring/format_checks.py
Checks resume format and ATS structural compatibility:
- file type, fonts, special characters, contact info completeness,
  table/column layout risk.
"""

import re


def run_format_checks(parsed_resume, file_extension):
    """
    parsed_resume: the dict returned by parser.resume_parser.parse_resume()
    file_extension: 'pdf' or 'docx'
    Returns {"checks": [...], "score": float}
    """
    checks = []
    text = parsed_resume["raw_text"]
    contact = parsed_resume["contact_info"]

    # File format check
    checks.append({
        "name": "File Format",
        "status": "pass" if file_extension in ("pdf", "docx") else "warning",
        "message": f"{file_extension.upper()} format detected"
        + (" (DOCX is most reliably parsed by ATS)" if file_extension == "docx" else "")
    })

    # Font compliance (PDF: detected from actual glyph fonts; DOCX: from run fonts)
    checks.append({
        "name": "Standard Fonts",
        "status": "pass" if parsed_resume["font_compliant"] else "warning",
        "message": "Standard ATS-friendly fonts used" if parsed_resume["font_compliant"]
                   else f"Non-standard fonts detected: {', '.join(parsed_resume['nonstandard_fonts'][:3])}"
    })

    # Special / unusual characters (emojis, icons, dingbats, rating stars)
    safe_punct = r'[•\-–—@.,()/%&+:|#$*_\~=<>[\]{}\'"“”‘’₹€£;!?]'
    cleaned = re.sub(safe_punct, '', text)
    unusual_symbols = sorted(list(set(re.findall(r'[^\w\s]', cleaned))))
    has_unusual_chars = len(unusual_symbols) > 0
    symbols_str = ", ".join(f"'{s}'" for s in unusual_symbols[:5])
    checks.append({
        "name": "Special Characters",
        "status": "pass" if not has_unusual_chars else "warning",
        "message": "Clean character set" if not has_unusual_chars
                   else f"Unusual symbols/icons detected ({symbols_str}) that may scramble in older ATS parsers"
    })

    # Contact info completeness
    contact_ok = bool(contact["email"]) and bool(contact["phone"])
    checks.append({
        "name": "Contact Information",
        "status": "pass" if contact_ok else "fail",
        "message": ("Email and phone both found"
                    if contact_ok else "Missing email and/or phone number — add both near the top")
    })

    # Professional profile links (LinkedIn/GitHub/Portfolio) — bonus, not critical
    profile_links = [name for name, present in
                     [("LinkedIn", contact["linkedin"]), ("GitHub", contact["github"]),
                      ("Portfolio", contact["portfolio"])] if present]
    checks.append({
        "name": "Professional Profile Links",
        "status": "pass" if profile_links else "warning",
        "message": f"Found: {', '.join(profile_links)}" if profile_links
        else "No LinkedIn/GitHub/Portfolio links detected in text"
    })

    # Rough table/column layout risk detector — real box-drawing chars rarely
    # survive text extraction, so this checks for repeated large gaps instead,
    # which often indicates a multi-column layout.
    suspicious_columns = len(re.findall(r'\S+ {4,}\S+', text)) > 5
    checks.append({
        "name": "Single Column Layout",
        "status": "warning" if suspicious_columns else "pass",
        "message": "Possible multi-column layout detected (can scramble reading order in ATS)"
                   if suspicious_columns else "Single-column format verified"
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

"""
parser/section_splitter.py
Splits resume text into sections (Experience, Education, Skills, etc.)
based on common heading patterns.
"""

SECTION_HEADERS = {
    "experience": ["work experience", "professional experience", "experience", "employment history"],
    "education": ["education", "academic background", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
    "summary": ["summary", "professional summary", "objective", "profile"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
}


def split_into_sections(text):
    """
    Splits resume text into sections based on common heading patterns.
    Returns a dict: {section_name: section_text}
    """
    lines = text.split("\n")
    sections = {}
    # top of resume (name, contact info) before any heading
    current_section = "header"
    section_content = []

    for line in lines:
        stripped = line.strip()
        matched_section = None

        # A heading line is typically short and matches a known keyword exactly
        if 0 < len(stripped) < 40:
            lower_line = stripped.lower().strip(":")
            for section_name, variants in SECTION_HEADERS.items():
                if lower_line in variants:
                    matched_section = section_name
                    break

        if matched_section:
            sections[current_section] = "\n".join(section_content).strip()
            current_section = matched_section
            section_content = []
        else:
            section_content.append(line)

    sections[current_section] = "\n".join(section_content).strip()
    return sections


def get_section_completeness(sections):
    """Returns which of the core expected sections were found."""
    core_sections = ["experience", "education", "skills"]
    found = [s for s in core_sections if s in sections and sections[s].strip()]
    missing = [s for s in core_sections if s not in found]
    return {"found": found, "missing": missing, "completeness_pct": round(len(found) / len(core_sections) * 100, 1)}

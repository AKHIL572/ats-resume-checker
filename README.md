# ATS Resume Checker (Local & Free)

A fully local, offline ATS (Applicant Tracking System) resume checker.
No API keys, no paid services, no data leaves your machine.

## Features
- Parses PDF/DOCX resumes (text, fonts, contact info)
- Matches resume content against a role-specific skills database, or
  against a pasted job description
- Stemmed + phrase-aware + synonym-aware keyword matching
  (fixes common false-positive/false-negative bugs from naive substring
  matching, e.g. short acronyms like "R" or "SQL")
- Optional semantic matching (sentence-transformers) to catch skills
  phrased differently than the exact keyword list
- Weighted overall score across keywords, content quality, and format/ATS
  structural compatibility
- Prioritized, ranked improvement recommendations

## Project Structure
```
app.py                     Streamlit UI entry point
parser/
  resume_parser.py         PDF/DOCX text, font, contact info extraction
  section_splitter.py      Splits resume into Experience/Education/Skills/etc.
matching/
  keyword_matcher.py        Stemmed + phrase-aware keyword matching
  semantic_matcher.py       Embedding-based similarity matching
  skill_taxonomy.py         Loads and queries data/skills_db.json
scoring/
  format_checks.py          Fonts, layout, contact info, special characters
  content_checks.py         Length, sections, bullet points, quantified achievements
  score_engine.py            Combines everything into a weighted final score
data/
  skills_db.json             Role-specific keyword/phrase/synonym database
```

## Setup
```bash
python -m venv venv
venv\Scripts\Activate      # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
(No NLTK data download needed — job description parsing uses spaCy's
grammar tagging, not NLTK's stopword corpus.)

## Run
```bash
streamlit run app.py
```

## Notes
- First run of semantic matching downloads a small (~80MB) embedding model
  once; fully offline afterward.
- The skills database (`data/skills_db.json`) is a starting point, not
  exhaustive — best accuracy comes from pasting real job descriptions
  instead of relying on the generic role list.

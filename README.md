# ats-resume-checker

> A free, privacy-first ATS resume analyzer that runs entirely in your browser — no data ever leaves your device.

---

## Overview

**ATS Checker Pro** helps job applicants quickly find out whether their resume is likely to pass Applicant Tracking Systems (ATS). Upload your resume, optionally target a specific job role or paste a job description, and get an instant compatibility score with actionable recommendations.

All processing happens locally in the browser using JavaScript — no backend, no server uploads, no data collection.

---

## Features

- **Multi-format support** — Upload resumes as PDF, DOCX, DOC, or TXT
- **Role-based analysis** — Choose from built-in job roles (e.g. Data Analyst, Software Engineer, UI/UX Designer) to get role-specific keyword matching
- **Job description matching** — Paste any job description to extract and match keywords directly
- **ATS score** — Get an overall ATS compatibility score plus individual scores across four categories
- **Detailed checks** — See pass / warning / fail results for formatting, content, keywords, and ATS readiness
- **Improvement recommendations** — Prioritized suggestions to fix the weakest areas of your resume
- **Privacy-first** — Zero data uploaded; everything runs client-side

---

## How It Works

1. **Upload** your resume (PDF, DOCX, DOC, or TXT) via drag-and-drop or the file picker
2. **Target** a job role from the list, or paste a job description (optional but recommended)
3. **Analyze** — the app extracts text from your resume and runs heuristic checks
4. **Review results** — see your ATS score, category breakdown, matched keywords, and recommendations

### Analysis Categories

| Category | What it checks |
|---|---|
| **Format** | Tables, columns, font types, layout issues |
| **Content** | Word count, key sections, bullet points, quantified achievements |
| **Keywords** | Match against role keyword set or job description keywords |
| **ATS Readiness** | Contact info, special characters, file format compatibility |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| HTML / CSS / JavaScript | Core app (single-file, no build step) |
| [Tailwind CSS](https://tailwindcss.com/) | Styling via CDN |
| [PDF.js](https://mozilla.github.io/pdf.js/) | PDF text extraction |
| [Mammoth.js](https://github.com/mwilliamson/mammoth.js) | DOCX text extraction |
| Google Fonts (Inter) | Typography |

---

## Getting Started

No installation or build step required.

```bash
# Clone the repo
git clone https://github.com/your-username/ats-resume-checker.git

# Open in browser
open index.html
```

Or simply download `index.html` and open it directly in any modern browser.

---

## Project Structure

```
ats-resume-checker/
└── index.html      # Complete app — HTML, CSS, and JS in one file
```

---

## Supported Job Roles (Built-in)

- Data Analyst
- Business Analyst
- Software Engineer
- UI/UX Designer
- *(and more — see the `roleDatabase` object in index.html)*

Each role includes a curated set of keywords, hard skills, and soft skills used for matching.

---

## Limitations

- ATS scoring is heuristic-based, not a simulation of any specific ATS software
- DOC format support depends on browser text reading capabilities and may be limited
- Results are best used as a guide, not a guarantee of ATS pass/fail

---

## Privacy

This app is entirely client-side. Your resume is never uploaded to any server or stored anywhere outside your browser session.

---

## License

MIT

---

## Contributing

Contributions are welcome! If you'd like to add more job roles, improve keyword matching logic, or enhance the UI, feel free to open a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/add-more-roles`)
3. Commit your changes (`git commit -m 'Add more job roles'`)
4. Push to the branch (`git push origin feature/add-more-roles`)
5. Open a Pull Request

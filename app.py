"""
app.py
Main Streamlit app for the local ATS Resume Checker.
Run with: streamlit run app.py
Everything runs 100% locally — nothing is uploaded anywhere.
"""

import os
import tempfile

import streamlit as st

from parser.resume_parser import parse_resume
from matching.keyword_matcher import match_skills, match_job_description
from matching.skill_taxonomy import get_role_names, get_role_data
from matching import semantic_matcher
from scoring.format_checks import run_format_checks
from scoring.content_checks import run_content_checks
from scoring.score_engine import calculate_overall_score, generate_recommendations, get_score_verdict

st.set_page_config(page_title="ATS Resume Checker",
                   page_icon="📄", layout="wide")

st.title("📄 ATS Resume Checker (Local & Free)")
st.caption("Runs 100% on your machine. Nothing is uploaded anywhere.")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload your resume", type=["pdf", "docx"])

with col2:
    mode = st.radio("Match against:", ["Job Role", "Job Description"])
    selected_role = None
    job_description = ""

    if mode == "Job Role":
        selected_role = st.selectbox("Select target role", get_role_names())
    else:
        job_description = st.text_area(
            "Paste job description here", height=150)

enable_semantic = st.checkbox(
    "Enable semantic matching (catches differently-worded skills; slower, downloads a small model on first run)",
    value=False
)

if uploaded_file is not None and st.button("Analyze Resume", type="primary"):
    file_extension = "pdf" if uploaded_file.name.lower().endswith(".pdf") else "docx"

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    with st.spinner("Parsing resume..."):
        parsed = parse_resume(tmp_path)
    os.remove(tmp_path)

    resume_text = parsed["raw_text"]

    if not resume_text.strip():
        st.error(
            "Could not extract any text from this file. Try a different PDF/DOCX.")
    else:
        # --- Keyword / role / JD matching ---
        semantic_score = None
        if mode == "Job Role" and selected_role:
            role_data = get_role_data(selected_role)
            keyword_result = match_skills(resume_text, role_data)
            match_label = f"{selected_role} Skills Match"
        elif mode == "Job Description" and job_description.strip():
            keyword_result = match_job_description(
                resume_text, job_description)
            match_label = "Job Description Match"
        else:
            st.warning("Please select a role or paste a job description.")
            st.stop()

        if enable_semantic:
            with st.spinner("Running semantic matching (first run downloads a small model)..."):
                if keyword_result["missing"]:
                    recovered, still_missing = semantic_matcher.semantic_match_missing_keywords(
                        resume_text, keyword_result["missing"]
                    )
                    keyword_result["matched"].extend(recovered)
                    keyword_result["missing"] = still_missing
                    total = len(keyword_result["matched"]) + \
                        len(keyword_result["missing"])
                    keyword_result["score"] = round(
                        (len(keyword_result["matched"]) /
                         total * 100) if total > 0 else 0, 1
                    )
                if mode == "Job Description":
                    semantic_score = semantic_matcher.overall_semantic_similarity(
                        resume_text, job_description)

        # --- Format & content checks ---
        format_result = run_format_checks(parsed, file_extension)
        content_result = run_content_checks(parsed)

        overall_score = calculate_overall_score(
            format_result, content_result, keyword_result, semantic_score)
        verdict = get_score_verdict(overall_score)
        recommendations = generate_recommendations(
            format_result, content_result, keyword_result)

        # ================= DISPLAY =================
        st.divider()
        top1, top2 = st.columns([1, 2])
        with top1:
            st.metric("Overall ATS Score", f"{overall_score}%")
        with top2:
            st.subheader(verdict["title"])
            st.write(verdict["description"])

        st.divider()

        # Contact info
        st.subheader("📇 Contact & Profile Links")
        contact = parsed["contact_info"]
        cc1, cc2, cc3, cc4, cc5 = st.columns(5)
        cc1.write(f"**Email:** {'✅' if contact['email'] else '❌'}")
        cc2.write(f"**Phone:** {'✅' if contact['phone'] else '❌'}")
        cc3.write(f"**LinkedIn:** {'✅' if contact['linkedin'] else '❌'}")
        cc4.write(f"**GitHub:** {'✅' if contact['github'] else '❌'}")
        cc5.write(f"**Portfolio:** {'✅' if contact['portfolio'] else '❌'}")

        st.divider()

        # Keyword match
        st.subheader(f"🎯 {match_label}")
        st.metric("Match Score", f"{keyword_result['score']}%")
        if semantic_score is not None:
            st.metric("Semantic Similarity (overall resume vs JD)",
                      f"{semantic_score}%")

        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown("**✅ Found**")
            st.write(", ".join(
                keyword_result["matched"]) if keyword_result["matched"] else "None found")
        with mc2:
            st.markdown("**❌ Missing**")
            st.write(", ".join(
                keyword_result["missing"]) if keyword_result["missing"] else "None — great coverage!")

        st.divider()

        # Format & content checks
        fc1, fc2 = st.columns(2)
        with fc1:
            st.subheader(
                f"🧱 Format & ATS Structure — {format_result['score']}%")
            for check in format_result["checks"]:
                icon = "✅" if check["status"] == "pass" else (
                    "⚠️" if check["status"] == "warning" else "❌")
                st.write(f"{icon} **{check['name']}** — {check['message']}")

        with fc2:
            st.subheader(f"📝 Content Quality — {content_result['score']}%")
            for check in content_result["checks"]:
                icon = "✅" if check["status"] == "pass" else (
                    "⚠️" if check["status"] == "warning" else "❌")
                st.write(f"{icon} **{check['name']}** — {check['message']}")

        st.divider()

        # Recommendations
        st.subheader("🚀 Priority Improvements")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(
                    f"**{i}. [{rec['category']}] {rec['name']}** — {rec['message']}")
        else:
            st.success("No major issues found — this resume looks ATS-ready!")

else:
    st.info("👆 Upload a PDF or DOCX resume, choose a role or paste a job description, then click Analyze.")

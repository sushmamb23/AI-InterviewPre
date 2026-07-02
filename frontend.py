import streamlit as st
from pathlib import Path
import requests

st.set_page_config(page_title="AI Interview Coach", layout="wide")
st.title("AI Interview Coach")

st.markdown("Upload a resume and describe the role to generate interview questions. Then answer them and receive evaluation feedback.")

with st.form("analysis_form"):
    role = st.text_input("Target role")
    experience = st.text_input("Years of experience")
    resume_file = st.file_uploader("Upload resume", type=["pdf", "txt", "md", "docx"])
    submitted = st.form_submit_button("Analyze")

if submitted:
    if not role or not experience or not resume_file:
        st.error("Please fill in all fields and upload a resume.")
        st.stop()

    files = {"resume_file": (resume_file.name, resume_file.getvalue(), resume_file.type)}
    data = {"role": role, "experience": experience}

    with st.spinner("Analyzing resume and generating interview prep..."):
        response = requests.post("http://127.0.0.1:8000/analyze", files=files, data=data, timeout=120)

    if response.ok:
        payload = response.json()
        if payload.get("success"):
            result = payload["result"]
            st.success("Analysis complete")
            questions = result.get("interview_questions", [])
            if questions:
                st.subheader("Answer the questions below")
                answers = {}
                for question in questions:
                    answers[question] = st.text_area(question, key=question)
                if st.button("Evaluate answers"):
                    eval_response = requests.post(
                        "http://127.0.0.1:8000/evaluate",
                        json={"role": role, "resume_summary": result.get("resume_summary", ""), "gaps": result.get("gaps", []), "questions": questions, "answers": answers},
                        timeout=120,
                    )
                    if eval_response.ok:
                        eval_payload = eval_response.json()
                        if eval_payload.get("success"):
                            for item in eval_payload.get("evaluations", []):
                                st.markdown(f"**Q:** {item.get('question')}")
                                st.markdown(f"**Score:** {item.get('score')}/10")
                                st.markdown(f"**Feedback:** {item.get('feedback')}")
                                st.write("")
                        else:
                            st.error(eval_payload.get("error", "Evaluation failed"))
                    else:
                        st.error(f"Evaluation request failed: {eval_response.text}")
            st.json(result)
            if result.get("report_path"):
                st.download_button(
                    label="Download report",
                    data=Path(result["report_path"]).read_bytes(),
                    file_name=Path(result["report_path"]).name,
                    mime="application/octet-stream",
                )
        else:
            st.error(payload.get("error", "Analysis failed"))
    else:
        st.error(f"Request failed: {response.text}")

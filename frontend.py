import streamlit as st
from pathlib import Path
import requests

st.set_page_config(page_title="AI Interview Coach", layout="wide")
st.title("AI Interview Coach")

st.markdown("Upload a resume and describe the role to generate interview questions. Then answer them one by one and receive evaluation feedback.")

# Initialize session state
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "questions" not in st.session_state:
    st.session_state.questions = []
if "in_qa_phase" not in st.session_state:
    st.session_state.in_qa_phase = False
if "result" not in st.session_state:
    st.session_state.result = None
if "role" not in st.session_state:
    st.session_state.role = ""

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
                st.session_state.result = result
                st.session_state.questions = questions
                st.session_state.in_qa_phase = True
                st.session_state.role = role
                st.session_state.current_question_index = 0
                st.session_state.answers = {}
                st.rerun()
        else:
            st.error(payload.get("error", "Analysis failed"))
    else:
        st.error(f"Request failed: {response.text}")

# Q&A Phase
if st.session_state.in_qa_phase and st.session_state.questions:
    total_questions = len(st.session_state.questions)
    current_index = st.session_state.current_question_index
    
    # Only show Q&A if we haven't finished all questions
    if current_index < total_questions:
        st.subheader(f"Interview Questions - Question {current_index + 1} of {total_questions}")
        
        # Progress bar
        progress = (current_index) / total_questions
        st.progress(progress)
        
        current_question = st.session_state.questions[current_index]
        st.write(f"**{current_question}**")
        
        # Text area for answer
        answer = st.text_area("Your answer:", value=st.session_state.answers.get(current_question, ""), key=f"answer_{current_index}")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_index > 0:
                if st.button("← Previous"):
                    st.session_state.answers[current_question] = answer
                    st.session_state.current_question_index -= 1
                    st.rerun()
        
        with col2:
            if st.button("Save & Next →", use_container_width=True):
                if answer.strip():
                    st.session_state.answers[current_question] = answer
                    if current_index < total_questions - 1:
                        st.session_state.current_question_index += 1
                        st.rerun()
                    else:
                        # All questions answered, move to evaluation
                        st.session_state.current_question_index = total_questions
                        st.rerun()
                else:
                    st.warning("Please provide an answer before proceeding.")
        
        with col3:
            if current_index == total_questions - 1:
                if st.button("Submit Answers", use_container_width=True):
                    if answer.strip():
                        st.session_state.answers[current_question] = answer
                        st.session_state.current_question_index = total_questions
                        st.rerun()
                    else:
                        st.warning("Please provide an answer before submitting.")

# Evaluation Phase
if st.session_state.in_qa_phase and st.session_state.current_question_index >= len(st.session_state.questions) and st.session_state.questions:
    st.subheader("Evaluation")
    
    if st.button("Evaluate Answers"):
        result = st.session_state.result
        questions = st.session_state.questions
        answers = st.session_state.answers
        
        with st.spinner("Evaluating your answers..."):
            eval_response = requests.post(
                "http://127.0.0.1:8000/evaluate",
                json={
                    "role": st.session_state.role,
                    "resume_summary": result.get("resume_summary", ""),
                    "gaps": result.get("gaps", []),
                    "questions": questions,
                    "answers": answers
                },
                timeout=120,
            )
        
        if eval_response.ok:
            eval_payload = eval_response.json()
            if eval_payload.get("success"):
                st.success("Evaluation complete!")
                
                # Calculate overall score
                evaluations = eval_payload.get("evaluations", [])
                if evaluations:
                    overall_score = sum(e.get("score", 0) for e in evaluations) / len(evaluations)
                    st.metric("Overall Score", f"{overall_score:.1f}/10")
                
                # Show individual evaluations
                for item in evaluations:
                    with st.expander(f"Q: {item.get('question')[:60]}..."):
                        st.markdown(f"**Score:** {item.get('score')}/10")
                        st.markdown(f"**Your Answer:** {item.get('answer', 'N/A')}")
                        st.markdown(f"**Feedback:** {item.get('feedback')}")
                
                # Download report
                if result.get("report_path"):
                    st.download_button(
                        label="📥 Download Report",
                        data=Path(result["report_path"]).read_bytes(),
                        file_name=Path(result["report_path"]).name,
                        mime="application/octet-stream",
                    )
            else:
                st.error(eval_payload.get("error", "Evaluation failed"))
        else:
            st.error(f"Evaluation request failed: {eval_response.text}")


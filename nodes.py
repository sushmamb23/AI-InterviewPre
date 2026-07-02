import json
from typing import Dict, List
from state import InterviewState
from tools import extract_resume_insights, build_interview_questions, generate_feedback, evaluate_user_answers, write_report


def parse_resume_node(state: InterviewState) -> dict:
    resume_summary = extract_resume_insights(state["resume_text"], state["role"], state["experience"])
    return {"resume_summary": resume_summary}


def identify_gaps_node(state: InterviewState) -> dict:
    gaps = []
    if "python" in state["resume_text"].lower():
        gaps.append("Strengthen Python and backend engineering examples")
    if state["experience"].startswith("0"):
        gaps.append("Add more project-based evidence and impact statements")
    return {"gaps": gaps}


def generate_questions_node(state: InterviewState) -> dict:
    questions = build_interview_questions(state["role"], state["resume_summary"], state["gaps"])
    return {"interview_questions": questions}


def generate_feedback_node(state: InterviewState) -> dict:
    feedback = generate_feedback(state["role"], state["resume_summary"], state["gaps"], state["interview_questions"])
    return {"feedback": feedback}


def evaluate_answers_node(state: InterviewState) -> dict:
    evaluations = evaluate_user_answers(
        state["role"],
        state.get("resume_summary", ""),
        state.get("gaps", []),
        state.get("interview_questions", []),
        [state.get("answers", {}).get(q, "") for q in state.get("interview_questions", [])],
    )
    return {"evaluations": evaluations}


def finalize_report_node(state: InterviewState) -> dict:
    report_path = write_report(state, "reports")
    return {"report_path": report_path, "completed": True}

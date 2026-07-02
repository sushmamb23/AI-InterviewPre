from langgraph.graph import StateGraph, START, END
from state import InterviewState
from nodes import (
    parse_resume_node,
    identify_gaps_node,
    generate_questions_node,
    generate_feedback_node,
    evaluate_answers_node,
    finalize_report_node,
)


def build_graph():
    builder = StateGraph(InterviewState)
    builder.add_node("parse_resume", parse_resume_node)
    builder.add_node("identify_gaps", identify_gaps_node)
    builder.add_node("generate_questions", generate_questions_node)
    builder.add_node("generate_feedback", generate_feedback_node)
    builder.add_node("evaluate_answers", evaluate_answers_node)
    builder.add_node("finalize_report", finalize_report_node)

    builder.add_edge(START, "parse_resume")
    builder.add_edge("parse_resume", "identify_gaps")
    builder.add_edge("identify_gaps", "generate_questions")
    builder.add_edge("generate_questions", "generate_feedback")
    builder.add_edge("generate_feedback", "evaluate_answers")
    builder.add_edge("evaluate_answers", "finalize_report")
    builder.add_edge("finalize_report", END)

    return builder.compile()

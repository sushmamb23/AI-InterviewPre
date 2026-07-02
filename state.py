from typing import TypedDict, List, Optional, Annotated
import operator


class InterviewState(TypedDict):
    role: str
    experience: str
    resume_text: str
    resume_summary: str
    gaps: List[str]
    interview_questions: List[str]
    feedback: List[str]
    report_path: str
    answers: dict
    current_question: str
    completed: bool
    error: Optional[str]
    evaluations: List[dict]

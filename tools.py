import json
from pathlib import Path
from typing import List

import PyPDF2
from docx import Document

from ollama_client import chat
from prompts import feedback_prompt, question_generation_prompt, resume_analysis_prompt, answer_evaluation_prompt


def load_resume_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        reader = PyPDF2.PdfReader(str(file_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    if suffix == ".docx":
        doc = Document(str(file_path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return file_path.read_text(encoding="utf-8", errors="ignore")


def _looks_like_llm_error(text: str) -> bool:
    lowered = (text or "").lower()
    return "ollama unavailable" in lowered or "not found" in lowered or "error" in lowered


def _build_resume_summary(resume_text: str, role: str, experience: str) -> str:
    text = resume_text or ""
    lower = text.lower()
    years = experience.strip() or "relevant"
    technologies = []
    for tech in [
        "python",
        "powerbi",
        "sql",
        "aws",
        "azure",
        "service now",
        "servicenow",
        "c#",
        "java",
        "net",
        "docker",
        "linux",
        "windows",
        "ansible",
        "api",
    ]:
        if tech in lower:
            technologies.append(tech.upper() if tech in {"aws", "api"} else tech.title())

    strengths = []
    if "python" in lower:
        strengths.append("Python-based automation and application development")
    if "sql" in lower or "sql server" in lower:
        strengths.append("database design and reporting")
    if "itil" in lower or "servicenow" in lower:
        strengths.append("incident management and service operations")
    if "aws" in lower:
        strengths.append("cloud awareness with AWS")
    if "ai" in lower or "generative" in lower:
        strengths.append("Generative AI adoption for productivity")
    if "lead" in lower or "consultant" in lower or "manager" in lower:
        strengths.append("leadership and client-facing delivery")

    if not strengths:
        strengths = ["enterprise software delivery", "cross-functional collaboration"]

    tech_text = ", ".join(technologies[:5]) if technologies else "software engineering"
    return (
        f"{role.title()} candidate with about {years} years of experience. "
        f"The resume highlights strengths in {tech_text} and emphasizes {', '.join(strengths[:4])}."
    )


def extract_resume_insights(resume_text: str, role: str, experience: str) -> str:
    prompt = resume_analysis_prompt(role, experience, resume_text)
    response = chat(prompt)
    if not response or _looks_like_llm_error(response):
        return _build_resume_summary(resume_text, role, experience)
    return response


def build_interview_questions(role: str, resume_summary: str, gaps: List[str]) -> List[str]:
    prompt = question_generation_prompt(role, resume_summary, gaps)
    response = chat(prompt)
    try:
        data = json.loads(response)
        if isinstance(data, list) and data:
            return [str(item) for item in data]
    except Exception:
        pass

    base_questions = [
        f"Tell me about a project where you delivered measurable impact for a {role} role.",
        f"How have you used your experience to solve a challenging problem in {role} work?",
        "What results or metrics did you improve in your most relevant project?",
        "How would you handle a difficult stakeholder or cross-team situation?",
    ]
    if gaps:
        base_questions.append(f"How would you address the gap around {gaps[0].lower()}?")
    return base_questions[:6]


def generate_feedback(role: str, resume_summary: str, gaps: List[str], questions: List[str]) -> List[str]:
    prompt = feedback_prompt(role, resume_summary, gaps, questions)
    response = chat(prompt)
    try:
        data = json.loads(response)
        if isinstance(data, list) and data:
            return [str(item) for item in data]
    except Exception:
        pass

    base_feedback = [
        f"Frame your experience around business outcomes relevant to {role}.",
        "Use STAR stories with clear ownership, action, result, and learning.",
        "Be ready to explain how you used tools like Python, SQL, cloud platforms, and automation in delivery.",
        "If you mention leadership or consulting work, quantify team size, scope, and impact.",
    ]
    if gaps:
        base_feedback.append(f"Prepare a concise example that strengthens {gaps[0].lower()}.")
    return base_feedback[:5]


def evaluate_user_answers(role: str, resume_summary: str, gaps: List[str], questions: List[str], answers: List[str]) -> List[dict]:
    prompt = answer_evaluation_prompt(role, resume_summary, gaps, questions, answers)
    response = chat(prompt)
    try:
        data = json.loads(response)
        if isinstance(data, list) and data:
            return data
    except Exception:
        pass

    evaluations = []
    for question, answer in zip(questions, answers):
        score = 7 if answer and len(answer.split()) >= 8 else 5
        evaluations.append({
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": "Add more concrete evidence, metrics, and a clear outcome to strengthen this answer." if score < 8 else "Strong answer with clear ownership and impact.",
        })
    return evaluations


def save_report(result: dict, reports_dir: Path) -> str:
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / "interview_report.json"
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return str(report_path)


def write_report(state: dict, reports_dir_name: str) -> str:
    reports_dir = Path(reports_dir_name)
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / "interview_report.json"
    report_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return str(report_path)

def resume_analysis_prompt(role: str, experience: str, resume_text: str) -> str:
    return f"""
You are an expert technical recruiter and interview coach.
Role: {role}
Experience: {experience}
Resume:
{resume_text}

Summarize the candidate's profile and list actionable interview preparation points.
"""


def question_generation_prompt(role: str, resume_summary: str, gaps: list[str]) -> str:
    return f"""
Create 8 interview questions tailored for a {role} role.
Candidate summary:
{resume_summary}

Focus on these gaps:
{gaps if gaps else 'None'}
Return a JSON array of questions.
"""


def feedback_prompt(role: str, resume_summary: str, gaps: list[str], questions: list[str]) -> str:
    return f"""
Provide concise interview coaching feedback for a {role} candidate.
Summary:
{resume_summary}
Gaps:
{gaps if gaps else 'None'}
Questions:
{questions}
Return a JSON array of coaching bullet points.
"""


def answer_evaluation_prompt(role: str, resume_summary: str, gaps: list[str], questions: list[str], answers: list[str]) -> str:
    return f"""
You are an interview coach evaluating candidate answers.
Role: {role}
Summary:
{resume_summary}
Gaps:
{gaps if gaps else 'None'}
Questions:
{questions}
Answers:
{answers}
Return a JSON array where each item has: question, answer, score (0-10), and feedback.
"""

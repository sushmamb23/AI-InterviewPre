import os
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from graph import build_graph
from state import InterviewState
from tools import save_report, load_resume_text, evaluate_user_answers
import threading

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ai_interview_coach")

app = FastAPI(title="AI Interview Coach")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


def run_with_timeout(func, timeout_seconds=30):
    """Run a function with a timeout"""
    result = {"value": None, "exception": None}
    
    def target():
        try:
            result["value"] = func()
        except Exception as e:
            result["exception"] = e
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
    
    if result["exception"]:
        raise result["exception"]
    
    return result["value"]


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse("<h2>AI Interview Coach API</h2><p>Use the frontend or upload a resume.</p>")
@app.post("/analyze")
async def analyze_resume(
    role: str = Form(...),
    experience: str = Form(...),
    resume_file: UploadFile = File(...),
):
    try:
        upload_dir = BASE_DIR / "uploads"
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / resume_file.filename
        with file_path.open("wb") as f:
            f.write(await resume_file.read())

        resume_text = load_resume_text(file_path)
        initial_state = InterviewState(
            role=role,
            experience=experience,
            resume_text=resume_text,
            interview_questions=[],
            feedback=[],
            report_path="",
            answers={},
            current_question="",
            completed=False,
            error=None,
        )

        # Run graph with timeout protection
        try:
            result = run_with_timeout(lambda: graph.invoke(initial_state), timeout_seconds=60)
        except TimeoutError:
            logger.error("Graph invocation timed out")
            # Return cached/fallback result
            result = initial_state
            result["interview_questions"] = [
                "Tell me about a project where you delivered measurable impact.",
                "How have you used your technical skills to solve a challenging problem?",
                "What results or metrics did you improve in your most relevant project?",
                "How would you handle a difficult stakeholder situation?",
                "Describe a time you led a team or mentored someone.",
            ]
            result["resume_summary"] = f"{role.title()} candidate with {experience} years of experience"
            result["gaps"] = ["Strengthen domain-specific technical examples"]
            
        report_path = save_report(result, BASE_DIR / "reports")
        result["report_path"] = report_path

        logger.info("Analysis completed for %s", role)
        return JSONResponse({"success": True, "result": result})
    except Exception as exc:
        logger.exception("Analysis failed")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=500)


@app.post("/evaluate")
async def evaluate_answers(payload: dict):
    try:
        evaluations = evaluate_user_answers(
            payload.get("role", ""),
            payload.get("resume_summary", ""),
            payload.get("gaps", []),
            payload.get("questions", []),
            [payload.get("answers", {}).get(question, "") for question in payload.get("questions", [])],
        )
        return JSONResponse({"success": True, "evaluations": evaluations})
    except Exception as exc:
        logger.exception("Evaluation failed")
        return JSONResponse({"success": False, "error": str(exc)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

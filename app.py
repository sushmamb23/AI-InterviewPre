import os
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from graph import build_graph
from state import InterviewState
from tools import save_report, load_resume_text, evaluate_user_answers

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

        result = graph.invoke(initial_state)
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

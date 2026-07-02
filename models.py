from pydantic import BaseModel


class InterviewRequest(BaseModel):
    role: str
    experience: str

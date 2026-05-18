from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import get_db
from models import DailyPlan, StudySession, User
from auth import decode_token
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/planner", tags=["Planner"])

class PlanCreate(BaseModel):
    subject: str
    planned_minutes: int

class FaceRegistered(BaseModel):
    registered: bool

def get_current_user(authorization: Optional[str] = Header(None), db: DBSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/today")
def get_today_plan(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    plans = db.query(DailyPlan).filter(
        DailyPlan.user_id == user.id,
        DailyPlan.date == today
    ).all()

    # Get today's actual time per subject
    today_sessions = db.query(StudySession).filter(
        StudySession.user_id == user.id
    ).all()

    subject_done = {}
    for s in today_sessions:
        if s.started_at and s.started_at.strftime("%Y-%m-%d") == today:
            key = s.subject or "Unknown"
            subject_done[key] = subject_done.get(key, 0) + (s.actual_duration or 0)

    return [
        {
            "id": p.id,
            "subject": p.subject,
            "planned_minutes": p.planned_minutes,
            "done_minutes": subject_done.get(p.subject, 0),
            "completed": subject_done.get(p.subject, 0) >= p.planned_minutes
        }
        for p in plans
    ]

@router.post("/add")
def add_plan(data: PlanCreate, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    existing = db.query(DailyPlan).filter(
        DailyPlan.user_id == user.id,
        DailyPlan.subject == data.subject,
        DailyPlan.date == today
    ).first()
    if existing:
        existing.planned_minutes = data.planned_minutes
        db.commit()
        return {"message": "Plan updated"}
    plan = DailyPlan(
        user_id=user.id,
        subject=data.subject,
        planned_minutes=data.planned_minutes,
        date=today
    )
    db.add(plan)
    db.commit()
    return {"message": "Plan added"}

@router.delete("/remove/{plan_id}")
def remove_plan(plan_id: int, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    plan = db.query(DailyPlan).filter(DailyPlan.id == plan_id, DailyPlan.user_id == user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Plan removed"}

@router.post("/register-face")
def register_face(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    user.face_registered = True
    db.commit()
    return {"message": "Face registered successfully"}

@router.get("/face-status")
def face_status(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    return {"face_registered": user.face_registered}
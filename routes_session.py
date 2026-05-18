from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session as DBSession
from database import get_db
from models import StudySession, User
from schemas import SessionCreate, SessionEnd
from auth import decode_token
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/session", tags=["Sessions"])

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

@router.post("/start")
def start_session(data: SessionCreate, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    new_session = StudySession(
        user_id=user.id,
        subject=data.subject,
        planned_duration=data.planned_duration,
        actual_duration=0,
        started_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.id, "message": "Session started"}

@router.post("/end")
def end_session(data: SessionEnd, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    session = db.query(StudySession).filter(StudySession.id == data.session_id, StudySession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.actual_duration = data.actual_duration
    session.status = data.status
    session.focus_score = data.focus_score
    session.ended_at = datetime.utcnow()
    db.commit()
    return {"message": "Session saved successfully"}

@router.get("/history")
def get_history(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = db.query(StudySession).filter(StudySession.user_id == user.id).order_by(StudySession.started_at.desc()).all()
    return [
        {
            "id": s.id,
            "subject": s.subject,
            "planned_duration": s.planned_duration,
            "actual_duration": s.actual_duration,
            "focus_score": round(s.focus_score or 0, 1),
            "status": s.status,
            "started_at": s.started_at.strftime("%Y-%m-%d %H:%M") if s.started_at else ""
        }
        for s in sessions
    ]
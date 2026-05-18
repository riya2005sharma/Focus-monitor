from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session as DBSession
from database import get_db
from models import StudySession, User
from auth import decode_token
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["Analytics"])

class GoalUpdate(BaseModel):
    daily_goal_minutes: int

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

@router.get("/summary")
def get_summary(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = db.query(StudySession).filter(StudySession.user_id == user.id).all()
    if not sessions:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "avg_focus_score": 0,
            "completed_sessions": 0,
            "daily_goal_minutes": user.daily_goal_minutes,
            "today_minutes": 0,
            "streak": 0
        }

    total_sessions = len(sessions)
    total_minutes = sum(s.actual_duration or 0 for s in sessions)
    avg_focus = round(sum(s.focus_score or 0 for s in sessions) / total_sessions, 1)
    completed = sum(1 for s in sessions if s.status == "completed")

    # Today's minutes
    today = datetime.utcnow().date()
    today_minutes = sum(
        s.actual_duration or 0 for s in sessions
        if s.started_at and s.started_at.date() == today
    )

    # Streak calculation
    streak = 0
    check_date = today
    while True:
        day_sessions = [s for s in sessions if s.started_at and s.started_at.date() == check_date]
        if day_sessions:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "avg_focus_score": avg_focus,
        "completed_sessions": completed,
        "daily_goal_minutes": user.daily_goal_minutes,
        "today_minutes": today_minutes,
        "streak": streak
    }

@router.get("/by-subject")
def get_by_subject(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = db.query(StudySession).filter(StudySession.user_id == user.id).all()
    subject_map = {}
    for s in sessions:
        key = s.subject or "Unknown"
        if key not in subject_map:
            subject_map[key] = {"minutes": 0, "sessions": 0, "focus_total": 0}
        subject_map[key]["minutes"] += s.actual_duration or 0
        subject_map[key]["sessions"] += 1
        subject_map[key]["focus_total"] += s.focus_score or 0
    result = []
    for subject, data in subject_map.items():
        result.append({
            "subject": subject,
            "minutes": data["minutes"],
            "sessions": data["sessions"],
            "avg_focus": round(data["focus_total"] / data["sessions"], 1)
        })
    result.sort(key=lambda x: x["minutes"], reverse=True)
    return result

@router.get("/focus-trend")
def get_focus_trend(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = db.query(StudySession).filter(
        StudySession.user_id == user.id
    ).order_by(StudySession.started_at.asc()).limit(20).all()
    return [
        {
            "label": s.started_at.strftime("%d %b") if s.started_at else "",
            "focus_score": s.focus_score or 0,
            "subject": s.subject or ""
        }
        for s in sessions
    ]

@router.get("/insights")
def get_insights(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = db.query(StudySession).filter(StudySession.user_id == user.id).all()
    if not sessions:
        return {"insights": ["Start your first session to get personalized insights! 🚀"]}

    insights = []

    # Best subject
    subject_map = {}
    for s in sessions:
        key = s.subject or "Unknown"
        if key not in subject_map:
            subject_map[key] = {"focus_total": 0, "count": 0, "minutes": 0}
        subject_map[key]["focus_total"] += s.focus_score or 0
        subject_map[key]["count"] += 1
        subject_map[key]["minutes"] += s.actual_duration or 0

    best = max(subject_map.items(), key=lambda x: x[1]["focus_total"] / x[1]["count"])
    worst = min(subject_map.items(), key=lambda x: x[1]["focus_total"] / x[1]["count"])

    best_score = round(best[1]["focus_total"] / best[1]["count"], 1)
    worst_score = round(worst[1]["focus_total"] / worst[1]["count"], 1)

    insights.append(f"🌟 Your best focus subject is {best[0]} with {best_score}% avg focus score.")

    if best[0] != worst[0]:
        insights.append(f"⚠️ {worst[0]} needs more attention — only {worst_score}% avg focus. Try shorter sessions.")

    # Total time
    total_minutes = sum(s.actual_duration or 0 for s in sessions)
    hours = total_minutes // 60
    if hours >= 10:
        insights.append(f"🔥 Amazing! You've studied for {hours} hours total. Keep it up!")
    elif hours >= 1:
        insights.append(f"📚 You've studied for {hours} hours total. Great start!")
    else:
        insights.append("💡 Try to study at least 1 hour today to build momentum.")

    # Avg focus
    avg_focus = sum(s.focus_score or 0 for s in sessions) / len(sessions)
    if avg_focus >= 75:
        insights.append("🧠 Excellent focus overall! You're in the zone.")
    elif avg_focus >= 50:
        insights.append("👍 Good focus. Try eliminating phone distractions for even better scores.")
    else:
        insights.append("💪 Focus needs improvement. Try the Pomodoro technique — 25 min work, 5 min break.")

    # Abandoned sessions
    abandoned = sum(1 for s in sessions if s.status == "abandoned")
    if abandoned > 2:
        insights.append(f"📉 You abandoned {abandoned} sessions. Try setting shorter, more achievable durations.")

    return {"insights": insights}

@router.post("/set-goal")
def set_goal(data: GoalUpdate, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    user.daily_goal_minutes = data.daily_goal_minutes
    db.commit()
    return {"message": "Goal updated successfully"}
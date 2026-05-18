from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    daily_goal_minutes = Column(Integer, default=60)
    face_registered = Column(Boolean, default=False)  # ← new
    created_at = Column(DateTime, default=datetime.utcnow)

class StudySession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    planned_duration = Column(Integer)
    actual_duration = Column(Integer)
    focus_score = Column(Float, default=0.0)
    status = Column(String, default="completed")
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

class DailyPlan(Base):                              # ← new
    __tablename__ = "daily_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    planned_minutes = Column(Integer)
    date = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
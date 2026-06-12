from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Base, engine
import models
from routes_auth import router as auth_router
from routes_session import router as session_router
from routes_analytics import router as analytics_router
from routes_planner import router as planner_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Focus Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(session_router)
app.include_router(analytics_router)
app.include_router(planner_router)

# ✅ Fixed path
app.mount("/app", StaticFiles(directory=".", html=True), name="frontend")

@app.get("/")
def root():
    return {"message": "Focus Monitor API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
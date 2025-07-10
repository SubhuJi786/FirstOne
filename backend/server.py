from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import sys
import os
from datetime import datetime, timedelta
import json
import uuid

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager
from enhanced_ai_coach import EnhancedAICoach
from roadmap_generator import RoadmapGenerator
from mock_test_system import MockTestSystem

app = FastAPI(title="Enhanced AI Coach API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize systems
db = DatabaseManager()
roadmap_gen = RoadmapGenerator(db)
mock_test_system = MockTestSystem(db)

# OpenAI API key
OPENAI_API_KEY = "sk-304502f4c76949c084c41590b0ef4ee1"

# Pydantic models
class UserCreate(BaseModel):
    name: str
    exam_type: str  # JEE or NEET
    target_year: int = 2025

class UserProfileUpdate(BaseModel):
    learning_style: Optional[str] = None
    difficulty_preference: Optional[str] = None
    preferred_explanation_style: Optional[str] = None
    study_hours_per_day: Optional[int] = None
    preferred_study_time: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    topic_id: Optional[str] = None

class ProgressUpdate(BaseModel):
    topic_id: str
    mastery_level: float
    time_spent: int
    attempts: int = 0
    correct_answers: int = 0

class MockTestSchedule(BaseModel):
    exam_type: str
    test_name: str
    scheduled_date: Optional[datetime] = None

class MockTestAnswer(BaseModel):
    question_id: str
    user_answer: str
    time_taken: int

# Global variables to store user sessions
user_sessions = {}

def get_user_session(user_id: str) -> Dict:
    """Get or create user session"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'ai_coach': EnhancedAICoach(user_id, OPENAI_API_KEY),
            'created_at': datetime.now()
        }
    return user_sessions[user_id]

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    print("🚀 Enhanced AI Coach API starting up...")
    print("✅ Database initialized")
    print("✅ AI Coach system ready")
    print("✅ Roadmap generator ready")
    print("✅ Mock test system ready")

@app.get("/")
async def root():
    return {"message": "Enhanced AI Coach API is running!", "version": "1.0.0"}

# User Management Endpoints
@app.post("/api/users")
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        user_id = db.create_user(user_data.name, user_data.exam_type, user_data.target_year)
        return {"user_id": user_id, "message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Get user profile"""
    try:
        profile = db.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/users/{user_id}")
async def update_user(user_id: str, updates: UserProfileUpdate):
    """Update user profile"""
    try:
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        db.update_user_profile(user_id, **update_data)
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/progress")
async def get_user_progress(user_id: str):
    """Get user progress"""
    try:
        progress = db.get_user_progress(user_id)
        return {"progress": progress}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users/{user_id}/progress")
async def update_progress(user_id: str, progress_data: ProgressUpdate):
    """Update user progress"""
    try:
        db.update_progress(
            user_id, 
            progress_data.topic_id, 
            progress_data.mastery_level,
            progress_data.time_spent,
            progress_data.attempts,
            progress_data.correct_answers
        )
        return {"message": "Progress updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Coach Endpoints
@app.post("/api/chat/{user_id}")
async def chat_with_coach(user_id: str, message: ChatMessage):
    """Chat with AI coach"""
    try:
        session = get_user_session(user_id)
        ai_coach = session['ai_coach']
        
        response = ai_coach.generate_personalized_response(
            message.message, 
            message.topic_id
        )
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{user_id}/suggestions")
async def get_suggestions(user_id: str):
    """Get personalized suggestions"""
    try:
        session = get_user_session(user_id)
        ai_coach = session['ai_coach']
        
        suggestions = ai_coach.get_personalized_suggestions()
        motivational_message = ai_coach.generate_motivational_message()
        
        return {
            "suggestions": suggestions,
            "motivational_message": motivational_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{user_id}/analytics")
async def get_performance_analytics(user_id: str):
    """Get performance analytics"""
    try:
        session = get_user_session(user_id)
        ai_coach = session['ai_coach']
        
        analytics = ai_coach.analyze_performance_trends()
        
        return {"analytics": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/topics/{topic_id}/strategy")
async def get_study_strategy(topic_id: str, user_id: str = Query(...)):
    """Get study strategy for a topic"""
    try:
        session = get_user_session(user_id)
        ai_coach = session['ai_coach']
        
        strategy = ai_coach.get_study_strategy(topic_id)
        
        return {"strategy": strategy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Subjects and Topics Endpoints
@app.get("/api/subjects")
async def get_subjects(exam_type: str = Query(...)):
    """Get subjects for exam type"""
    try:
        subjects = db.get_subjects_for_exam(exam_type)
        return {"subjects": subjects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/subjects/{subject_id}/topics")
async def get_topics(subject_id: str):
    """Get topics for a subject"""
    try:
        topics = db.get_topics_for_subject(subject_id)
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Roadmap Endpoints
@app.post("/api/roadmap/{user_id}")
async def generate_roadmap(user_id: str, week_offset: int = 0):
    """Generate weekly roadmap"""
    try:
        roadmap = roadmap_gen.generate_weekly_roadmap(user_id, week_offset)
        return {"roadmap": roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/roadmap/{user_id}")
async def get_roadmap(user_id: str, week_offset: int = 0):
    """Get current roadmap"""
    try:
        roadmap = roadmap_gen.get_roadmap(user_id, week_offset)
        if not roadmap:
            # Generate new roadmap if none exists
            roadmap = roadmap_gen.generate_weekly_roadmap(user_id, week_offset)
        return {"roadmap": roadmap}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/roadmap/items/{item_id}")
async def update_roadmap_item(item_id: str, status: str = Body(...)):
    """Update roadmap item status"""
    try:
        roadmap_gen.update_roadmap_progress(item_id, status)
        return {"message": "Roadmap item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/roadmap/{user_id}/analytics")
async def get_roadmap_analytics(user_id: str):
    """Get roadmap analytics"""
    try:
        analytics = roadmap_gen.get_roadmap_analytics(user_id)
        adaptations = roadmap_gen.adapt_roadmap_based_on_performance(user_id)
        
        return {
            "analytics": analytics,
            "adaptations": adaptations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mock Test Endpoints
@app.post("/api/mock-tests/{user_id}")
async def schedule_mock_test(user_id: str, test_data: MockTestSchedule):
    """Schedule a mock test"""
    try:
        test_id = mock_test_system.schedule_mock_test(
            user_id, 
            test_data.exam_type, 
            test_data.test_name, 
            test_data.scheduled_date
        )
        return {"test_id": test_id, "message": "Mock test scheduled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mock-tests/{user_id}")
async def get_mock_tests(user_id: str):
    """Get user's mock tests"""
    try:
        tests = mock_test_system.get_user_mock_tests(user_id)
        return {"tests": tests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mock-tests/{test_id}/start")
async def start_mock_test(test_id: str):
    """Start a mock test"""
    try:
        test_session = mock_test_system.start_mock_test(test_id)
        return {"session": test_session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mock-tests/{test_id}/submit")
async def submit_answer(test_id: str, answer_data: MockTestAnswer):
    """Submit an answer"""
    try:
        result = mock_test_system.submit_answer(
            test_id, 
            answer_data.question_id, 
            answer_data.user_answer, 
            answer_data.time_taken
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mock-tests/{test_id}/complete")
async def complete_mock_test(test_id: str):
    """Complete a mock test"""
    try:
        results = mock_test_system.complete_mock_test(test_id)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mock-tests/{user_id}/trends")
async def get_performance_trends(user_id: str):
    """Get performance trends"""
    try:
        trends = mock_test_system.get_performance_trends(user_id)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mock-tests/{user_id}/schedule-regular")
async def schedule_regular_tests(user_id: str, exam_type: str = Query(...), frequency: str = Query("weekly")):
    """Schedule regular mock tests"""
    try:
        scheduled_tests = mock_test_system.schedule_regular_tests(user_id, exam_type, frequency)
        return {"scheduled_tests": scheduled_tests, "message": f"Scheduled {len(scheduled_tests)} tests"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Learning Session Endpoints
@app.post("/api/sessions/{user_id}")
async def create_learning_session(user_id: str, topic_id: str = Query(...), session_type: str = Query(...)):
    """Create a learning session"""
    try:
        session_id = db.create_learning_session(user_id, topic_id, session_type)
        return {"session_id": session_id, "message": "Learning session created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/sessions/{session_id}/end")
async def end_learning_session(
    session_id: str, 
    performance_score: float = Query(...),
    understanding_level: int = Query(...),
    mood: str = Query("neutral"),
    notes: str = Query("")
):
    """End a learning session"""
    try:
        db.end_learning_session(session_id, performance_score, understanding_level, mood, notes)
        return {"message": "Learning session ended successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "ai_coach": "ready",
            "roadmap_generator": "ready",
            "mock_test_system": "ready"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
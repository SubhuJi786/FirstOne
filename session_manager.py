import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st
from config import MOOD_OPTIONS, DEFAULT_USER_ID


class SessionManager:
    def __init__(self, user_id: str = DEFAULT_USER_ID):
        self.user_id = user_id
        self.session_file = f"user_data/{user_id}_sessions.json"
        self.mood_file = f"user_data/{user_id}_mood_history.json"
        self.current_session = None

    def start_new_session(self, content_type: str, content_title: str) -> str:
        """Start a new learning session"""
        session_id = f"session_{self.user_id}_{int(datetime.now().timestamp())}"

        self.current_session = {
            "session_id": session_id,
            "user_id": self.user_id,
            "start_time": datetime.now().isoformat(),
            "content_type": content_type,
            "content_title": content_title,
            "activities": [],
            "mood_checkins": [],
            "total_time": 0,
            "completed": False,
            "final_mood": None,
            "understanding_level": None
        }

        return session_id

    def log_activity(self, activity_type: str, details: Dict = None):
        """Log an activity within the current session"""
        if not self.current_session:
            return

        activity = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "details": details or {}
        }

        self.current_session["activities"].append(activity)

    def mood_checkin(self, mood_emoji: str, notes: str = "") -> bool:
        """Record a mood check-in"""
        if mood_emoji not in MOOD_OPTIONS:
            return False

        mood_data = {
            "timestamp": datetime.now().isoformat(),
            "mood_emoji": mood_emoji,
            "mood_name": MOOD_OPTIONS[mood_emoji],
            "notes": notes,
            "session_id": self.current_session["session_id"] if self.current_session else None
        }

        # Save to current session if active
        if self.current_session:
            self.current_session["mood_checkins"].append(mood_data)

        # Save to mood history
        self._save_mood_history(mood_data)

        return True

    def _save_mood_history(self, mood_data: Dict):
        """Save mood data to history file"""
        mood_history = []
        if os.path.exists(self.mood_file):
            with open(self.mood_file, 'r') as f:
                mood_history = json.load(f)

        mood_history.append(mood_data)

        # Keep only last 100 mood entries
        mood_history = mood_history[-100:]

        with open(self.mood_file, 'w') as f:
            json.dump(mood_history, f, indent=2)

    def end_session(self, understanding_level: int, final_mood: str):
        """End the current session"""
        if not self.current_session:
            return

        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["understanding_level"] = understanding_level
        self.current_session["final_mood"] = final_mood
        self.current_session["completed"] = True

        # Calculate total session time
        start_time = datetime.fromisoformat(self.current_session["start_time"])
        end_time = datetime.now()
        self.current_session["total_time"] = (end_time - start_time).total_seconds()

        # Save session
        self._save_session()
        self.current_session = None

    def _save_session(self):
        """Save session to file"""
        sessions = []
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r') as f:
                sessions = json.load(f)

        sessions.append(self.current_session)

        with open(self.session_file, 'w') as f:
            json.dump(sessions, f, indent=2)

    def get_session_history(self, days: int = 30) -> List[Dict]:
        """Get session history for specified days"""
        if not os.path.exists(self.session_file):
            return []

        with open(self.session_file, 'r') as f:
            sessions = json.load(f)

        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_sessions = [
            s for s in sessions
            if datetime.fromisoformat(s["start_time"]) > cutoff_date
        ]

        return recent_sessions

    def get_mood_history(self, days: int = 30) -> List[Dict]:
        """Get mood history for specified days"""
        if not os.path.exists(self.mood_file):
            return []

        with open(self.mood_file, 'r') as f:
            mood_history = json.load(f)

        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_moods = [
            m for m in mood_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_date
        ]

        return recent_moods

    def get_learning_analytics(self) -> Dict:
        """Get comprehensive learning analytics"""
        sessions = self.get_session_history(30)
        moods = self.get_mood_history(30)

        if not sessions:
            return {
                "total_sessions": 0,
                "total_time": 0,
                "avg_session_time": 0,
                "completion_rate": 0,
                "avg_understanding": 0,
                "mood_trends": {},
                "activity_breakdown": {}
            }

        # Calculate session analytics
        total_sessions = len(sessions)
        completed_sessions = [s for s in sessions if s["completed"]]
        total_time = sum(s["total_time"] for s in completed_sessions)
        avg_session_time = total_time / len(completed_sessions) if completed_sessions else 0
        completion_rate = len(completed_sessions) / total_sessions if total_sessions > 0 else 0

        # Understanding level analysis
        understanding_levels = [s["understanding_level"] for s in completed_sessions if s["understanding_level"]]
        avg_understanding = sum(understanding_levels) / len(understanding_levels) if understanding_levels else 0

        # Mood analysis
        mood_counts = {}
        for mood in moods:
            mood_name = mood["mood_name"]
            mood_counts[mood_name] = mood_counts.get(mood_name, 0) + 1

        # Activity breakdown
        activity_counts = {}
        for session in sessions:
            for activity in session["activities"]:
                activity_type = activity["type"]
                activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1

        return {
            "total_sessions": total_sessions,
            "total_time": total_time,
            "avg_session_time": avg_session_time,
            "completion_rate": completion_rate,
            "avg_understanding": avg_understanding,
            "mood_trends": mood_counts,
            "activity_breakdown": activity_counts,
            "recent_sessions": sessions[-5:] if sessions else []
        }

    def get_streak_data(self) -> Dict:
        """Calculate learning streaks"""
        sessions = self.get_session_history(90)  # Last 90 days

        if not sessions:
            return {"current_streak": 0, "longest_streak": 0, "total_days": 0}

        # Group sessions by date
        session_dates = {}
        for session in sessions:
            date = datetime.fromisoformat(session["start_time"]).date()
            if date not in session_dates:
                session_dates[date] = []
            session_dates[date].append(session)

        # Calculate streaks
        dates = sorted(session_dates.keys())
        current_streak = 0
        longest_streak = 0
        temp_streak = 0

        # Check for consecutive days
        for i, date in enumerate(dates):
            if i == 0:
                temp_streak = 1
            else:
                prev_date = dates[i - 1]
                if (date - prev_date).days == 1:
                    temp_streak += 1
                else:
                    temp_streak = 1

            longest_streak = max(longest_streak, temp_streak)

        # Calculate current streak (from today backwards)
        today = datetime.now().date()
        current_streak = 0

        for i in range(len(dates)):
            check_date = today - timedelta(days=i)
            if check_date in session_dates:
                current_streak += 1
            else:
                break

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_days": len(session_dates)
        }

    def suggest_next_activity(self) -> str:
        """Suggest next learning activity based on history"""
        analytics = self.get_learning_analytics()

        if analytics["total_sessions"] == 0:
            return "🌟 Start your learning journey by uploading some content!"

        # Analyze recent patterns
        recent_activities = analytics["activity_breakdown"]

        suggestions = []

        # Based on completion rate
        if analytics["completion_rate"] < 0.7:
            suggestions.append("💪 Try shorter focused sessions to build consistency")

        # Based on understanding levels
        if analytics["avg_understanding"] < 3:
            suggestions.append("🎯 Review previous content with different summary modes")

        # Based on mood trends
        if "Frustrated" in analytics["mood_trends"] and analytics["mood_trends"]["Frustrated"] > 2:
            suggestions.append("🧘 Take breaks and try visual mode summaries")

        # Based on activity patterns
        if recent_activities.get("quiz", 0) < 2:
            suggestions.append("🎮 Test your knowledge with some quizzes")

        if recent_activities.get("flashcard", 0) < 2:
            suggestions.append("🧩 Try flashcards for better retention")

        if not suggestions:
            suggestions.append("🚀 You're doing great! Keep exploring new content")

        return random.choice(suggestions) if suggestions else "📚 Continue learning!"
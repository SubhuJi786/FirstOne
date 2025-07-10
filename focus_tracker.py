import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

class FocusTracker:
   def __init__(self, user_id: str):
       self.user_id = user_id
       self.session_file = f"user_data/{user_id}_focus_sessions.json"
       self.current_session = None
       self.focus_start_time = None

   def start_focus_session(self, content_type: str, content_title: str):
       """Start a new focus tracking session"""
       session_id = f"{self.user_id}_{int(time.time())}"
       self.current_session = {
           "session_id": session_id,
           "start_time": datetime.now().isoformat(),
           "content_type": content_type,
           "content_title": content_title,
           "interactions": [],
           "focus_breaks": [],
           "total_focus_time": 0,
           "completed": False
       }
       self.focus_start_time = time.time()
       return session_id

   def log_interaction(self, interaction_type: str, response_time: float = None, correct: bool = None):
       """Log user interaction during session"""
       if not self.current_session:
           return

       interaction = {
           "timestamp": datetime.now().isoformat(),
           "type": interaction_type,
           "response_time": response_time,
           "correct": correct,
           "focus_duration_before": time.time() - self.focus_start_time if self.focus_start_time else 0
       }

       self.current_session["interactions"].append(interaction)

       # Detect focus break if response time is too long
       if response_time and response_time > 10:  # 10 seconds threshold
           self.log_focus_break("slow_response", response_time)

   def log_focus_break(self, break_type: str, duration: float):
       """Log focus break event"""
       if not self.current_session:
           return

       focus_break = {
           "timestamp": datetime.now().isoformat(),
           "type": break_type,
           "duration": duration
       }

       self.current_session["focus_breaks"].append(focus_break)
       self.focus_start_time = time.time()  # Reset focus timer

   def end_session(self, completed: bool = True):
       """End current focus session and save data"""
       if not self.current_session:
           return

       self.current_session["end_time"] = datetime.now().isoformat()
       self.current_session["completed"] = completed
       self.current_session["total_focus_time"] = self._calculate_total_focus_time()

       # Save session data
       self._save_session_data()
       self.current_session = None

   def _calculate_total_focus_time(self) -> float:
       """Calculate total focused time excluding breaks"""
       if not self.current_session:
           return 0

       start_time = datetime.fromisoformat(self.current_session["start_time"])
       end_time = datetime.now()
       total_time = (end_time - start_time).total_seconds()

       # Subtract break durations
       break_time = sum(break_event["duration"] for break_event in self.current_session["focus_breaks"])

       return max(0, total_time - break_time)

   def _save_session_data(self):
       """Save session data to file"""
       sessions = []
       if os.path.exists(self.session_file):
           with open(self.session_file, 'r') as f:
               sessions = json.load(f)

       sessions.append(self.current_session)

       with open(self.session_file, 'w') as f:
           json.dump(sessions, f, indent=2)

   def get_focus_analytics(self, days: int = 7) -> Dict:
       """Get focus analytics for the specified number of days"""
       if not os.path.exists(self.session_file):
           return {"total_sessions": 0, "avg_focus_time": 0, "focus_patterns": []}

       with open(self.session_file, 'r') as f:
           sessions = json.load(f)

       # Filter recent sessions
       cutoff_date = datetime.now() - timedelta(days=days)
       recent_sessions = [
           s for s in sessions
           if datetime.fromisoformat(s["start_time"]) > cutoff_date
       ]

       if not recent_sessions:
           return {
               "total_sessions": 0,
               "avg_focus_time": 0,
               "completion_rate": 0,
               "avg_response_time": 0,
               "accuracy": 0,
               "focus_patterns": [],
               "break_frequency": {
                   "avg_breaks_per_session": 0,
                   "most_common_break_type": "none",
                   "break_types": {}
               }
           }

       # Calculate analytics
       total_sessions = len(recent_sessions)
       avg_focus_time = sum(s["total_focus_time"] for s in recent_sessions) / total_sessions
       completion_rate = sum(1 for s in recent_sessions if s["completed"]) / total_sessions

       # Analyze focus patterns
       focus_patterns = self._analyze_focus_patterns(recent_sessions)

       # Response time analysis
       all_interactions = []
       for session in recent_sessions:
           all_interactions.extend(session["interactions"])

       avg_response_time = 0
       accuracy = 0
       if all_interactions:
           response_times = [i["response_time"] for i in all_interactions if i["response_time"]]
           if response_times:
               avg_response_time = sum(response_times) / len(response_times)

           correct_responses = [i for i in all_interactions if i["correct"] is not None]
           if correct_responses:
               accuracy = sum(1 for i in correct_responses if i["correct"]) / len(correct_responses)

       return {
           "total_sessions": total_sessions,
           "avg_focus_time": avg_focus_time,
           "completion_rate": completion_rate,
           "avg_response_time": avg_response_time,
           "accuracy": accuracy,
           "focus_patterns": focus_patterns,
           "break_frequency": self._analyze_break_frequency(recent_sessions)
       }

   def _analyze_focus_patterns(self, sessions: List[Dict]) -> List[Dict]:
       """Analyze when user focuses best"""
       hourly_focus = {}

       for session in sessions:
           hour = datetime.fromisoformat(session["start_time"]).hour
           if hour not in hourly_focus:
               hourly_focus[hour] = []
           hourly_focus[hour].append(session["total_focus_time"])

       patterns = []
       for hour, times in hourly_focus.items():
           patterns.append({
               "hour": hour,
               "avg_focus_time": sum(times) / len(times),
               "session_count": len(times)
           })

       return sorted(patterns, key=lambda x: x["avg_focus_time"], reverse=True)

   def _analyze_break_frequency(self, sessions: List[Dict]) -> Dict:
       """Analyze break patterns"""
       all_breaks = []
       for session in sessions:
           all_breaks.extend(session["focus_breaks"])

       if not all_breaks:
           return {"avg_breaks_per_session": 0, "most_common_break_type": "none"}

       break_types = {}
       for break_event in all_breaks:
           break_type = break_event["type"]
           break_types[break_type] = break_types.get(break_type, 0) + 1

       most_common = max(break_types.items(), key=lambda x: x[1])[0]

       return {
           "avg_breaks_per_session": len(all_breaks) / len(sessions),
           "most_common_break_type": most_common,
           "break_types": break_types
       }

   def create_focus_visualization(self, analytics: Dict) -> go.Figure:
       """Create focus analytics visualization"""
       if not analytics["focus_patterns"]:
           return None

       # Create hourly focus pattern chart
       df = pd.DataFrame(analytics["focus_patterns"])

       fig = px.bar(
           df,
           x="hour",
           y="avg_focus_time",
           title="Focus Patterns by Hour",
           labels={"hour": "Hour of Day", "avg_focus_time": "Average Focus Time (seconds)"}
       )

       fig.update_layout(
           xaxis=dict(tickmode='linear', tick0=0, dtick=2),
           yaxis_title="Focus Time (seconds)",
           showlegend=False
       )

       return fig
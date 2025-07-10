import random
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple
import streamlit as st
from config import QUIZ_QUESTION_COUNT
from neuro_summarizer import NeuroSummarizer
from visual_feedback_manager import VisualFeedbackManager

class EnhancedGamifiedQuizSystem:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.quiz_history_file = f"user_data/{user_id}_quiz_history.json"
        self.streak_file = f"user_data/{user_id}_streaks.json"
        self.summarizer = NeuroSummarizer()
        self.visual_feedback = VisualFeedbackManager(user_id)

    def generate_quiz_questions(self, content: str, difficulty: str = "Medium") -> List[Dict]:
        """Generate quiz questions from content"""
        try:
            system_prompt = f"""Generate {QUIZ_QUESTION_COUNT} quiz questions from the provided content. 
            Difficulty level: {difficulty}

            Format each question as JSON with this structure:
            {{
                "question": "The question text",
                "options": ["A", "B", "C", "D"],
                "correct_answer": 0,
                "explanation": "Why this answer is correct",
                "type": "multiple_choice"
            }}

            Question types based on difficulty:
            - Easy: Direct recall, definitions
            - Medium: Understanding, application
            - Hard: Analysis, synthesis, evaluation

            Make questions neuro-friendly:
            - Clear, concise language
            - Avoid trick questions
            - Include context when needed
            - Focus on understanding over memorization

            Return only valid JSON array of questions."""

            response = self.summarizer._call_openai(system_prompt, content[:2000])

            # Try to parse JSON response
            if response.startswith('[') and response.endswith(']'):
                questions = json.loads(response)
                return questions[:QUIZ_QUESTION_COUNT]
            else:
                return self._generate_basic_questions(content)

        except Exception as e:
            st.warning(f"Using basic question generation: {str(e)}")
            return self._generate_basic_questions(content)

    def _generate_basic_questions(self, content: str) -> List[Dict]:
        """Generate basic questions when AI is not available"""
        # Simple pattern-based question generation
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20][:10]
        questions = []

        for i, sentence in enumerate(sentences[:QUIZ_QUESTION_COUNT]):
            # Create fill-in-the-blank questions
            words = sentence.split()
            if len(words) > 5:
                # Remove a key word (not articles/prepositions)
                key_words = [w for w in words if len(w) > 3 and w.lower() not in ['the', 'and', 'but', 'for', 'with']]
                if key_words:
                    target_word = random.choice(key_words)
                    question_text = sentence.replace(target_word, "_____")

                    # Generate options
                    options = [target_word]
                    # Add some dummy options (simple approach)
                    dummy_options = ["information", "concept", "system", "process", "method", "result"]
                    options.extend(random.sample(dummy_options, 3))
                    random.shuffle(options)

                    questions.append({
                        "question": f"Fill in the blank: {question_text}",
                        "options": options,
                        "correct_answer": options.index(target_word),
                        "explanation": f"The correct answer is '{target_word}' based on the context.",
                        "type": "fill_blank"
                    })

        return questions

    def create_quiz_session(self, questions: List[Dict], content_title: str) -> str:
        """Create a new quiz session"""
        session_id = f"quiz_{self.user_id}_{int(datetime.now().timestamp())}"

        session_data = {
            "session_id": session_id,
            "content_title": content_title,
            "questions": questions,
            "start_time": datetime.now().isoformat(),
            "current_question": 0,
            "score": 0,
            "responses": [],
            "completed": False
        }

        # Store in session state
        st.session_state[f"quiz_{session_id}"] = session_data
        return session_id

    def get_quiz_session(self, session_id: str) -> Dict:
        """Get quiz session data"""
        session = st.session_state.get(f"quiz_{session_id}", {})
        # Ensure title field exists for backward compatibility
        if session and "title" not in session and "content_title" in session:
            session["title"] = session["content_title"]
        return session

    def submit_answer(self, session_id: str, answer_index: int, response_time: float) -> Dict:
        """Submit answer and get enhanced visual feedback"""
        session = self.get_quiz_session(session_id)
        if not session:
            return {"error": "Session not found"}

        current_q_index = session["current_question"]
        if current_q_index >= len(session["questions"]):
            return {"error": "Quiz completed"}

        question = session["questions"][current_q_index]
        is_correct = answer_index == question["correct_answer"]

        # Performance data for visual feedback
        performance_data = {
            "correct": is_correct,
            "response_time": response_time,
            "question_type": question.get("type", "multiple_choice"),
            "difficulty": "medium"  # Could be dynamic based on question
        }

        # Generate enhanced visual feedback
        visual_feedback = self.visual_feedback.get_contextual_feedback(
            "quiz_result", performance_data
        )

        response_data = {
            "question_index": current_q_index,
            "answer_given": answer_index,
            "correct": is_correct,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
            "visual_feedback": visual_feedback
        }

        session["responses"].append(response_data)

        if is_correct:
            session["score"] += 1

        session["current_question"] += 1

        # Check if quiz is completed
        if session["current_question"] >= len(session["questions"]):
            session["completed"] = True
            session["end_time"] = datetime.now().isoformat()
            self._save_quiz_results(session)

            # Generate completion feedback
            final_performance = {
                "score": session["score"],
                "total": len(session["questions"]),
                "completion_time": response_time
            }
            completion_feedback = self.visual_feedback.get_contextual_feedback(
                "quiz_result", final_performance
            )
            session["completion_feedback"] = completion_feedback

            self._update_streak(session["score"], len(session["questions"]))

        # Update session state
        st.session_state[f"quiz_{session_id}"] = session

        return {
            "correct": is_correct,
            "explanation": question["explanation"],
            "visual_feedback": visual_feedback,
            "score": session["score"],
            "total_questions": len(session["questions"]),
            "completed": session["completed"],
            "completion_feedback": session.get("completion_feedback")
        }

    def _save_quiz_results(self, session: Dict):
        """Save completed quiz results"""
        history = []
        if os.path.exists(self.quiz_history_file):
            with open(self.quiz_history_file, 'r') as f:
                history = json.load(f)

        quiz_result = {
            "session_id": session["session_id"],
            "content_title": session["content_title"],
            "score": session["score"],
            "total_questions": len(session["questions"]),
            "accuracy": session["score"] / len(session["questions"]),
            "start_time": session["start_time"],
            "end_time": session["end_time"],
            "avg_response_time": sum(r["response_time"] for r in session["responses"]) / len(session["responses"]),
            "has_visual_feedback": True
        }

        history.append(quiz_result)

        with open(self.quiz_history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def _update_streak(self, score: int, total: int):
        """Update user's quiz streak with visual feedback"""
        streaks = {"current_streak": 0, "best_streak": 0, "total_quizzes": 0, "last_quiz_date": None}

        if os.path.exists(self.streak_file):
            with open(self.streak_file, 'r') as f:
                streaks = json.load(f)

        today = datetime.now().date().isoformat()
        last_quiz_date = streaks.get("last_quiz_date")

        streaks["total_quizzes"] += 1
        streaks["last_quiz_date"] = today

        # Consider it a successful quiz if score > 60%
        success = score / total >= 0.6

        if success:
            # Check if this continues a streak
            if last_quiz_date:
                last_date = datetime.fromisoformat(last_quiz_date).date()
                today_date = datetime.now().date()
                days_diff = (today_date - last_date).days

                if days_diff <= 1:  # Same day or consecutive day
                    if days_diff == 1:  # Only increment for new day
                        streaks["current_streak"] += 1
                else:
                    streaks["current_streak"] = 1  # Reset streak
            else:
                streaks["current_streak"] = 1

            # Update best streak
            if streaks["current_streak"] > streaks["best_streak"]:
                streaks["best_streak"] = streaks["current_streak"]

            # Generate streak feedback
            if streaks["current_streak"] >= 3:
                streak_performance = {"streak_days": streaks["current_streak"]}
                streak_feedback = self.visual_feedback.get_contextual_feedback(
                    "learning_streak", streak_performance
                )
                # Store streak feedback for display
                st.session_state["streak_feedback"] = streak_feedback
        else:
            streaks["current_streak"] = 0

        with open(self.streak_file, 'w') as f:
            json.dump(streaks, f, indent=2)

    def get_streak_info(self) -> Dict:
        """Get current streak information with visual elements"""
        if os.path.exists(self.streak_file):
            with open(self.streak_file, 'r') as f:
                streak_data = json.load(f)
        else:
            streak_data = {"current_streak": 0, "best_streak": 0, "total_quizzes": 0}

        # Add visual motivation based on streak
        if streak_data["current_streak"] >= 7:
            motivation_visual = self.visual_feedback.create_meme_image(
                "learning_streak",
                f"🔥 {streak_data['current_streak']}-day streak!",
                "achievement"
            )
        elif streak_data["current_streak"] >= 3:
            motivation_visual = self.visual_feedback.create_meme_image(
                "learning_streak",
                f"Building momentum: {streak_data['current_streak']} days!",
                "confident"
            )
        else:
            motivation_visual = self.visual_feedback.create_meme_image(
                "study_motivation",
                "Ready to start your streak?",
                "learning"
            )

        streak_data["motivation_visual"] = motivation_visual
        return streak_data

    def get_quiz_history(self, limit: int = 10) -> List[Dict]:
        """Get recent quiz history"""
        if os.path.exists(self.quiz_history_file):
            with open(self.quiz_history_file, 'r') as f:
                history = json.load(f)
                return history[-limit:]
        return []

    def get_performance_analytics(self) -> Dict:
        """Get performance analytics with visual insights"""
        history = self.get_quiz_history(20)

        if not history:
            return {
                "avg_accuracy": 0,
                "avg_response_time": 0,
                "improvement_trend": "No data",
                "total_quizzes": 0,
                "progress_visual": self.visual_feedback.create_meme_image(
                    "study_motivation", "Start your learning journey!", "learning"
                )
            }

        avg_accuracy = sum(q["accuracy"] for q in history) / len(history)
        avg_response_time = sum(q["avg_response_time"] for q in history) / len(history)

        # Calculate improvement trend (compare last 5 vs previous 5)
        if len(history) >= 10:
            recent_avg = sum(q["accuracy"] for q in history[-5:]) / 5
            older_avg = sum(q["accuracy"] for q in history[-10:-5]) / 5
            trend = "Improving" if recent_avg > older_avg else "Declining" if recent_avg < older_avg else "Stable"
        else:
            trend = "Building data"

        # Create progress visualization
        progress_data = {
            "total_concepts": 20,  # Could be dynamic
            "mastered_concepts": int(avg_accuracy * 20),
            "accuracy": avg_accuracy
        }
        progress_visual = self.visual_feedback.create_progress_visualization(progress_data)

        return {
            "avg_accuracy": avg_accuracy,
            "avg_response_time": avg_response_time,
            "improvement_trend": trend,
            "total_quizzes": len(history),
            "progress_visual": progress_visual
        }

    def generate_reward_message(self, streak_info: Dict) -> str:
        """Generate reward message based on achievements"""
        current_streak = streak_info["current_streak"]
        best_streak = streak_info["best_streak"]
        total_quizzes = streak_info["total_quizzes"]

        if current_streak == best_streak and current_streak > 0:
            if current_streak >= 10:
                return "🏆 LEGENDARY STREAK! You're on fire! 🔥"
            elif current_streak >= 5:
                return "⭐ AMAZING STREAK! Keep it up! ⭐"
            elif current_streak >= 3:
                return "🎯 Great streak! You're building momentum! 🚀"
            else:
                return "💪 Nice start! Keep learning! 📚"
        elif current_streak > 0:
            return f"📈 {current_streak} in a row! Aim for your best: {best_streak}!"
        else:
            return "🌟 Every expert was once a beginner. Keep going! 🌟"

    def get_daily_quiz_motivation(self) -> Dict:
        """Get daily motivational content for quiz taking"""
        return self.visual_feedback.get_daily_motivation_visual()
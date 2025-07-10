import openai
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import random
from database_manager import DatabaseManager

class EnhancedAICoach:
    def __init__(self, user_id: str, api_key: str):
        self.user_id = user_id
        self.db = DatabaseManager()
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=api_key)
        
        # Initialize sentence transformer for semantic search
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {e}")
            self.sentence_model = None
        
        # Load user profile
        self.user_profile = self.db.get_user_profile(user_id)
        if not self.user_profile:
            # Create default user if not exists
            self.db.create_user("Demo User", "JEE", 2025)
            self.user_profile = self.db.get_user_profile(user_id)
    
    def generate_personalized_response(self, user_message: str, topic_id: str = None) -> str:
        """Generate personalized response using enhanced AI coaching"""
        
        # Analyze user message for intent and emotion
        analysis = self.analyze_message(user_message)
        
        # Get relevant context
        context = self.get_relevant_context(user_message, topic_id)
        
        # Build system prompt based on user profile and exam type
        system_prompt = self.build_system_prompt(analysis, context)
        
        # Generate response
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            coach_response = response.choices[0].message.content.strip()
            
            # Save conversation
            self.db.save_conversation(
                self.user_id, user_message, coach_response, 
                analysis.get('type', 'general'), topic_id, analysis.get('sentiment', 'neutral')
            )
            
            # Update user profile based on interaction
            self.update_user_profile_from_interaction(analysis)
            
            return coach_response
            
        except Exception as e:
            return f"I'm having trouble right now. Please try again later. Error: {str(e)}"
    
    def analyze_message(self, message: str) -> Dict:
        """Analyze user message for intent, emotion, and type"""
        message_lower = message.lower()
        
        # Determine message type
        if any(word in message_lower for word in ['solve', 'calculate', 'find', 'what is', 'how to']):
            msg_type = 'problem_solving'
        elif any(word in message_lower for word in ['explain', 'understand', 'concept', 'theory']):
            msg_type = 'conceptual'
        elif any(word in message_lower for word in ['strategy', 'plan', 'prepare', 'study']):
            msg_type = 'strategy'
        elif any(word in message_lower for word in ['motivate', 'encourage', 'confidence', 'worried']):
            msg_type = 'motivation'
        elif any(word in message_lower for word in ['previous year', 'pyq', 'exam pattern', 'syllabus']):
            msg_type = 'exam_specific'
        else:
            msg_type = 'general'
        
        # Determine sentiment
        if any(word in message_lower for word in ['confused', 'stuck', 'difficult', 'hard', 'frustrated']):
            sentiment = 'frustrated'
        elif any(word in message_lower for word in ['excited', 'confident', 'easy', 'understand']):
            sentiment = 'positive'
        elif any(word in message_lower for word in ['worried', 'anxious', 'scared', 'nervous']):
            sentiment = 'anxious'
        else:
            sentiment = 'neutral'
        
        # Extract subject if mentioned
        subjects = ['physics', 'chemistry', 'mathematics', 'biology', 'math', 'bio', 'chem', 'phy']
        mentioned_subject = None
        for subject in subjects:
            if subject in message_lower:
                mentioned_subject = subject
                break
        
        return {
            'type': msg_type,
            'sentiment': sentiment,
            'subject': mentioned_subject,
            'difficulty_indicators': self.extract_difficulty_indicators(message_lower)
        }
    
    def extract_difficulty_indicators(self, message: str) -> List[str]:
        """Extract difficulty level indicators from message"""
        indicators = []
        
        easy_words = ['easy', 'simple', 'basic', 'fundamental']
        medium_words = ['moderate', 'intermediate', 'standard']
        hard_words = ['difficult', 'hard', 'complex', 'advanced', 'challenging']
        
        for word in easy_words:
            if word in message:
                indicators.append('easy')
        for word in medium_words:
            if word in message:
                indicators.append('medium')
        for word in hard_words:
            if word in message:
                indicators.append('hard')
        
        return indicators
    
    def get_relevant_context(self, message: str, topic_id: str = None) -> Dict:
        """Get relevant context for the user message"""
        context = {
            'user_progress': [],
            'recent_conversations': [],
            'struggling_topics': [],
            'strong_topics': [],
            'current_roadmap': None
        }
        
        # Get user progress
        progress = self.db.get_user_progress(self.user_id)
        context['user_progress'] = progress
        
        # Get struggling and strong topics
        for p in progress:
            if p['status'] == 'struggling':
                context['struggling_topics'].append(p['topic_name'])
            elif p['status'] == 'completed' and p['mastery_level'] >= 0.8:
                context['strong_topics'].append(p['topic_name'])
        
        # Get recent conversations
        context['recent_conversations'] = self.db.get_recent_conversations(self.user_id, 3)
        
        # Get current roadmap
        context['current_roadmap'] = self.get_current_week_roadmap()
        
        return context
    
    def build_system_prompt(self, analysis: Dict, context: Dict) -> str:
        """Build comprehensive system prompt for JEE/NEET coaching"""
        
        exam_type = self.user_profile.get('exam_type', 'JEE')
        
        base_prompt = f"""You are an expert AI coach specializing in {exam_type} preparation. You have deep knowledge of:

🎯 **EXAM EXPERTISE:**
- {exam_type} syllabus, patterns, and strategies
- Previous year question trends and analysis
- Subject-wise preparation strategies
- Time management and exam techniques

🧠 **COACHING ABILITIES:**
- Problem-solving strategies and shortcuts
- Concept linking across subjects
- Doubt resolution with step-by-step explanations
- Motivation and confidence building

📊 **STUDENT PROFILE:**
- Learning Style: {self.user_profile.get('learning_style', 'mixed')}
- Confidence Level: {self.user_profile.get('confidence_level', 0.5):.1%}
- Preferred Explanation: {self.user_profile.get('preferred_explanation_style', 'analogies')}
- Current Level: {self.user_profile.get('current_level', 'beginner')}
- Exam Type: {exam_type}

📈 **CURRENT STATUS:**
- Struggling Topics: {', '.join(context['struggling_topics'][:3]) if context['struggling_topics'] else 'None identified'}
- Strong Topics: {', '.join(context['strong_topics'][:3]) if context['strong_topics'] else 'Building foundation'}
"""
        
        # Add message-specific adaptations
        if analysis['type'] == 'problem_solving':
            base_prompt += """
🔧 **PROBLEM-SOLVING MODE:**
- Provide step-by-step solutions
- Explain the reasoning behind each step
- Suggest alternative approaches
- Highlight key formulas and concepts
- Connect to previous year questions if relevant
"""
        
        elif analysis['type'] == 'conceptual':
            base_prompt += """
📚 **CONCEPTUAL TEACHING MODE:**
- Use analogies and real-world examples
- Break down complex concepts into simple parts
- Provide visual descriptions where helpful
- Connect concepts across subjects
- Suggest practice problems to reinforce understanding
"""
        
        elif analysis['type'] == 'strategy':
            base_prompt += """
🎯 **STRATEGIC GUIDANCE MODE:**
- Provide personalized study plans
- Suggest time management techniques
- Recommend resources and practice methods
- Address preparation milestones
- Focus on high-yield topics
"""
        
        elif analysis['type'] == 'motivation':
            base_prompt += """
💪 **MOTIVATIONAL SUPPORT MODE:**
- Provide encouragement and confidence building
- Share success stories and strategies
- Address anxiety and stress management
- Set realistic goals and milestones
- Celebrate progress and improvements
"""
        
        # Add sentiment-specific adaptations
        if analysis['sentiment'] == 'frustrated':
            base_prompt += """
😤 **FRUSTRATION SUPPORT:**
- Acknowledge the student's feelings
- Break down problems into smaller steps
- Provide extra encouragement
- Suggest taking breaks if needed
- Focus on building confidence
"""
        
        elif analysis['sentiment'] == 'anxious':
            base_prompt += """
😰 **ANXIETY SUPPORT:**
- Provide reassurance and calm guidance
- Focus on manageable steps
- Avoid overwhelming information
- Emphasize progress over perfection
- Suggest stress management techniques
"""
        
        # Add exam-specific knowledge
        if exam_type == 'JEE':
            base_prompt += """
📋 **JEE-SPECIFIC KNOWLEDGE:**
- JEE Main: 90 questions, 3 hours, NTA pattern
- JEE Advanced: 54 questions, 3 hours, IIT pattern
- Physics: Mechanics, Electricity, Modern Physics focus
- Chemistry: Organic, Inorganic, Physical Chemistry
- Mathematics: Calculus, Algebra, Coordinate Geometry
- Weightage: Physics (33%), Chemistry (33%), Mathematics (34%)
"""
        
        elif exam_type == 'NEET':
            base_prompt += """
📋 **NEET-SPECIFIC KNOWLEDGE:**
- NEET: 180 questions, 3 hours, NTA pattern
- Physics: 45 questions, Mechanics and Modern Physics
- Chemistry: 45 questions, Organic and Inorganic focus
- Biology: 90 questions, Botany and Zoology
- Weightage: Physics (25%), Chemistry (25%), Biology (50%)
"""
        
        base_prompt += """
🎯 **RESPONSE GUIDELINES:**
- Be encouraging and supportive
- Use clear, simple language
- Provide actionable advice
- Include relevant examples
- End with a motivational note
- Keep responses focused and practical
"""
        
        return base_prompt
    
    def update_user_profile_from_interaction(self, analysis: Dict):
        """Update user profile based on interaction patterns"""
        updates = {}
        
        # Update confidence based on sentiment
        current_confidence = self.user_profile.get('confidence_level', 0.5)
        if analysis['sentiment'] == 'positive':
            updates['confidence_level'] = min(1.0, current_confidence + 0.05)
        elif analysis['sentiment'] == 'frustrated':
            updates['confidence_level'] = max(0.0, current_confidence - 0.03)
        
        # Update difficulty preference based on message
        if 'easy' in analysis['difficulty_indicators']:
            updates['difficulty_preference'] = 'easy'
        elif 'hard' in analysis['difficulty_indicators']:
            updates['difficulty_preference'] = 'hard'
        
        # Update weak subjects
        if analysis['subject']:
            weak_subjects = json.loads(self.user_profile.get('weak_subjects', '[]'))
            if analysis['sentiment'] == 'frustrated' and analysis['subject'] not in weak_subjects:
                weak_subjects.append(analysis['subject'])
                updates['weak_subjects'] = json.dumps(weak_subjects)
        
        if updates:
            self.db.update_user_profile(self.user_id, **updates)
            # Refresh user profile
            self.user_profile = self.db.get_user_profile(self.user_id)
    
    def get_current_week_roadmap(self) -> Optional[Dict]:
        """Get current week's roadmap"""
        # This would be implemented with the roadmap system
        return None
    
    def get_personalized_suggestions(self) -> List[str]:
        """Get personalized learning suggestions"""
        suggestions = []
        
        # Get user progress
        progress = self.db.get_user_progress(self.user_id)
        
        # Analyze performance
        if not progress:
            suggestions.append("🌟 Start your journey by taking a diagnostic test to identify your strengths")
            suggestions.append("📚 Begin with fundamental concepts in your chosen subjects")
            suggestions.append("🎯 Set up your weekly study schedule")
        else:
            # Check for struggling topics
            struggling = [p for p in progress if p['status'] == 'struggling']
            if struggling:
                topic_names = [p['topic_name'] for p in struggling[:2]]
                suggestions.append(f"🎯 Focus on strengthening: {', '.join(topic_names)}")
            
            # Check for completed topics
            completed = [p for p in progress if p['status'] == 'completed']
            if completed:
                suggestions.append(f"🚀 Great progress! You've mastered {len(completed)} topics")
                suggestions.append("📈 Ready for more advanced practice in your strong areas")
            
            # Check study consistency
            recent_sessions = [p for p in progress if p['last_studied'] and 
                             datetime.fromisoformat(p['last_studied']) > datetime.now() - timedelta(days=7)]
            if len(recent_sessions) < 3:
                suggestions.append("📅 Try to study more consistently - aim for daily practice")
        
        # Add exam-specific suggestions
        exam_type = self.user_profile.get('exam_type', 'JEE')
        if exam_type == 'JEE':
            suggestions.append("🔢 Practice numerical problems daily for JEE Main")
            suggestions.append("⏰ Time yourself while solving - speed is crucial")
        elif exam_type == 'NEET':
            suggestions.append("🧬 Focus on Biology - it carries 50% weightage")
            suggestions.append("📊 Practice diagrams and labeling questions")
        
        return suggestions[:4]
    
    def get_study_strategy(self, topic_id: str) -> Dict:
        """Get personalized study strategy for a specific topic"""
        # Get topic details
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, s.name as subject_name FROM topics t
            JOIN subjects s ON t.subject_id = s.id
            WHERE t.id = ?
        ''', (topic_id,))
        
        topic = cursor.fetchone()
        conn.close()
        
        if not topic:
            return {"error": "Topic not found"}
        
        # Get user progress for this topic
        progress = self.db.get_user_progress(self.user_id)
        topic_progress = next((p for p in progress if p['topic_id'] == topic_id), None)
        
        strategy = {
            'topic_name': topic[2],  # name
            'subject': topic[8],     # subject_name
            'difficulty': topic[4],  # difficulty_level
            'estimated_hours': topic[6],  # estimated_hours
            'current_mastery': topic_progress['mastery_level'] if topic_progress else 0.0,
            'study_plan': self.generate_study_plan(topic, topic_progress),
            'resources': self.get_topic_resources(topic_id),
            'practice_questions': self.get_practice_questions(topic_id)
        }
        
        return strategy
    
    def generate_study_plan(self, topic, progress) -> List[Dict]:
        """Generate study plan for a topic"""
        plans = []
        
        mastery_level = progress['mastery_level'] if progress else 0.0
        
        if mastery_level < 0.3:
            # Beginner level
            plans.append({
                'phase': 'Foundation',
                'duration': '2-3 hours',
                'activities': [
                    'Read basic concepts from NCERT',
                    'Watch concept videos',
                    'Make notes with key formulas',
                    'Solve basic numerical problems'
                ]
            })
        elif mastery_level < 0.6:
            # Intermediate level
            plans.append({
                'phase': 'Practice',
                'duration': '3-4 hours',
                'activities': [
                    'Solve previous year questions',
                    'Practice mixed problems',
                    'Review common mistakes',
                    'Time-bound practice sessions'
                ]
            })
        else:
            # Advanced level
            plans.append({
                'phase': 'Mastery',
                'duration': '2-3 hours',
                'activities': [
                    'Solve advanced problems',
                    'Take topic-wise tests',
                    'Review and revise concepts',
                    'Teach concepts to others'
                ]
            })
        
        return plans
    
    def get_topic_resources(self, topic_id: str) -> List[Dict]:
        """Get recommended resources for a topic"""
        # This would return curated resources based on topic
        return [
            {'type': 'video', 'title': 'Concept explanation', 'source': 'Khan Academy'},
            {'type': 'book', 'title': 'NCERT Chapter', 'source': 'NCERT'},
            {'type': 'practice', 'title': 'Previous Year Questions', 'source': 'JEE/NEET Archive'}
        ]
    
    def get_practice_questions(self, topic_id: str) -> List[Dict]:
        """Get practice questions for a topic"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM questions 
            WHERE topic_id = ?
            ORDER BY difficulty_level
            LIMIT 5
        ''', (topic_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return []
        
        columns = ['id', 'topic_id', 'question_text', 'question_type', 'difficulty_level',
                  'options', 'correct_answer', 'explanation', 'year', 'exam_type', 'source']
        
        return [dict(zip(columns, row)) for row in results]
    
    def generate_motivational_message(self) -> str:
        """Generate personalized motivational message"""
        progress = self.db.get_user_progress(self.user_id)
        exam_type = self.user_profile.get('exam_type', 'JEE')
        
        if not progress:
            messages = [
                f"🌟 Welcome to your {exam_type} journey! Every expert was once a beginner.",
                f"🎯 Your {exam_type} preparation starts now. Small consistent steps lead to big results!",
                f"💪 You have the potential to crack {exam_type}. Let's build your foundation step by step!"
            ]
        else:
            completed_topics = len([p for p in progress if p['status'] == 'completed'])
            if completed_topics > 0:
                messages = [
                    f"🚀 Amazing! You've mastered {completed_topics} topics. Keep this momentum going!",
                    f"⭐ Your dedication shows! {completed_topics} topics completed. You're on the right track!",
                    f"🔥 Fantastic progress! {completed_topics} topics down, many more to conquer!"
                ]
            else:
                messages = [
                    f"🌱 Every {exam_type} topper started where you are. Keep pushing forward!",
                    "💡 Learning is a journey, not a destination. Enjoy the process!",
                    "🎯 Focus on progress, not perfection. You're building something great!"
                ]
        
        return random.choice(messages)
    
    def analyze_performance_trends(self) -> Dict:
        """Analyze user's performance trends"""
        progress = self.db.get_user_progress(self.user_id)
        
        if not progress:
            return {
                'overall_progress': 0.0,
                'subject_wise': {},
                'improvement_areas': [],
                'strengths': [],
                'recommendation': 'Start with diagnostic assessment'
            }
        
        # Calculate overall progress
        overall_progress = sum(p['mastery_level'] for p in progress) / len(progress)
        
        # Subject-wise analysis
        subject_wise = {}
        for p in progress:
            subject = p['subject_name']
            if subject not in subject_wise:
                subject_wise[subject] = {'mastery': [], 'topics': []}
            subject_wise[subject]['mastery'].append(p['mastery_level'])
            subject_wise[subject]['topics'].append(p['topic_name'])
        
        # Calculate subject averages
        for subject in subject_wise:
            subject_wise[subject]['average'] = sum(subject_wise[subject]['mastery']) / len(subject_wise[subject]['mastery'])
        
        # Identify strengths and weaknesses
        strengths = []
        improvement_areas = []
        
        for subject, data in subject_wise.items():
            if data['average'] >= 0.7:
                strengths.append(subject)
            elif data['average'] < 0.4:
                improvement_areas.append(subject)
        
        # Generate recommendation
        if overall_progress < 0.3:
            recommendation = "Focus on building strong foundations. Take it one topic at a time."
        elif overall_progress < 0.6:
            recommendation = "Good progress! Increase practice and problem-solving sessions."
        else:
            recommendation = "Excellent work! Focus on advanced problems and mock tests."
        
        return {
            'overall_progress': overall_progress,
            'subject_wise': subject_wise,
            'improvement_areas': improvement_areas,
            'strengths': strengths,
            'recommendation': recommendation
        }
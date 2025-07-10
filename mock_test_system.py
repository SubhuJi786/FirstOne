import sqlite3
import json
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database_manager import DatabaseManager

class MockTestSystem:
    def __init__(self, db: DatabaseManager):
        self.db = db
        
        # Exam configurations
        self.exam_configs = {
            'JEE_MAIN': {
                'duration': 180,  # 3 hours
                'total_questions': 75,
                'subjects': {
                    'Physics': {'questions': 25, 'marks_per_question': 4},
                    'Chemistry': {'questions': 25, 'marks_per_question': 4},
                    'Mathematics': {'questions': 25, 'marks_per_question': 4}
                },
                'negative_marking': -1,
                'passing_percentile': 90
            },
            'JEE_ADVANCED': {
                'duration': 180,  # 3 hours
                'total_questions': 54,
                'subjects': {
                    'Physics': {'questions': 18, 'marks_per_question': 3},
                    'Chemistry': {'questions': 18, 'marks_per_question': 3},
                    'Mathematics': {'questions': 18, 'marks_per_question': 3}
                },
                'negative_marking': -1,
                'passing_percentile': 95
            },
            'NEET': {
                'duration': 180,  # 3 hours
                'total_questions': 180,
                'subjects': {
                    'Physics': {'questions': 45, 'marks_per_question': 4},
                    'Chemistry': {'questions': 45, 'marks_per_question': 4},
                    'Biology': {'questions': 90, 'marks_per_question': 4}
                },
                'negative_marking': -1,
                'passing_percentile': 50
            }
        }
    
    def schedule_mock_test(self, user_id: str, exam_type: str, test_name: str, 
                          scheduled_date: datetime = None) -> str:
        """Schedule a mock test"""
        
        if exam_type not in self.exam_configs:
            raise ValueError(f"Invalid exam type: {exam_type}")
        
        if scheduled_date is None:
            scheduled_date = datetime.now() + timedelta(days=1)
        
        config = self.exam_configs[exam_type]
        
        mock_test_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mock_tests 
            (id, user_id, exam_type, test_name, scheduled_date, duration, total_questions, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (mock_test_id, user_id, exam_type, test_name, scheduled_date, 
              config['duration'], config['total_questions'], 'scheduled'))
        
        conn.commit()
        conn.close()
        
        return mock_test_id
    
    def generate_mock_test_questions(self, mock_test_id: str) -> List[Dict]:
        """Generate questions for a mock test"""
        
        # Get mock test details
        mock_test = self.get_mock_test(mock_test_id)
        if not mock_test:
            return []
        
        exam_type = mock_test['exam_type']
        config = self.exam_configs[exam_type]
        
        # Get user profile to determine difficulty
        user_profile = self.db.get_user_profile(mock_test['user_id'])
        user_progress = self.db.get_user_progress(mock_test['user_id'])
        
        # Calculate average mastery for difficulty adjustment
        if user_progress:
            avg_mastery = sum(p['mastery_level'] for p in user_progress) / len(user_progress)
            if avg_mastery < 0.3:
                difficulty_preference = [1, 2, 3]  # Easy to medium
            elif avg_mastery < 0.7:
                difficulty_preference = [2, 3, 4]  # Medium to hard
            else:
                difficulty_preference = [3, 4, 5]  # Hard to very hard
        else:
            difficulty_preference = [1, 2, 3]  # Default to easier
        
        all_questions = []
        
        # Generate questions for each subject
        for subject_name, subject_config in config['subjects'].items():
            num_questions = subject_config['questions']
            
            # Get subject ID
            subjects = self.db.get_subjects_for_exam(exam_type.split('_')[0])
            subject_id = None
            for subject in subjects:
                if subject['name'] == subject_name:
                    subject_id = subject['id']
                    break
            
            if not subject_id:
                continue
            
            # Get existing questions from database
            existing_questions = self.get_questions_for_subject(subject_id, difficulty_preference)
            
            # If not enough questions, generate more
            if len(existing_questions) < num_questions:
                generated_questions = self.generate_questions_for_subject(
                    subject_id, num_questions - len(existing_questions), difficulty_preference
                )
                existing_questions.extend(generated_questions)
            
            # Select random questions
            selected_questions = random.sample(existing_questions, min(num_questions, len(existing_questions)))
            
            # Add to all questions
            all_questions.extend(selected_questions)
        
        # Shuffle all questions
        random.shuffle(all_questions)
        
        # Save question IDs to mock test responses
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for i, question in enumerate(all_questions):
            cursor.execute('''
                INSERT INTO mock_test_responses 
                (id, mock_test_id, question_id, user_answer, is_correct, time_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), mock_test_id, question['id'], None, 0, 0))
        
        conn.commit()
        conn.close()
        
        return all_questions
    
    def get_questions_for_subject(self, subject_id: str, difficulty_preference: List[int]) -> List[Dict]:
        """Get existing questions for a subject"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get topics for the subject
        topics = self.db.get_topics_for_subject(subject_id)
        topic_ids = [topic['id'] for topic in topics]
        
        if not topic_ids:
            conn.close()
            return []
        
        # Get questions for these topics
        placeholders = ','.join(['?' for _ in topic_ids])
        difficulty_placeholders = ','.join(['?' for _ in difficulty_preference])
        
        cursor.execute(f'''
            SELECT * FROM questions 
            WHERE topic_id IN ({placeholders}) 
            AND difficulty_level IN ({difficulty_placeholders})
            ORDER BY RANDOM()
        ''', topic_ids + difficulty_preference)
        
        results = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'topic_id', 'question_text', 'question_type', 'difficulty_level',
                  'options', 'correct_answer', 'explanation', 'year', 'exam_type', 'source']
        
        return [dict(zip(columns, row)) for row in results]
    
    def generate_questions_for_subject(self, subject_id: str, num_questions: int, 
                                     difficulty_preference: List[int]) -> List[Dict]:
        """Generate new questions for a subject"""
        # Get topics for the subject
        topics = self.db.get_topics_for_subject(subject_id)
        
        if not topics:
            return []
        
        generated_questions = []
        
        # Generate questions for each topic
        questions_per_topic = max(1, num_questions // len(topics))
        
        for topic in topics:
            for _ in range(questions_per_topic):
                if len(generated_questions) >= num_questions:
                    break
                
                question = self.generate_single_question(topic, difficulty_preference)
                if question:
                    generated_questions.append(question)
        
        return generated_questions
    
    def generate_single_question(self, topic: Dict, difficulty_preference: List[int]) -> Optional[Dict]:
        """Generate a single question for a topic"""
        # This is a simplified question generation
        # In a real system, you'd use AI or have a comprehensive question bank
        
        difficulty = random.choice(difficulty_preference)
        question_types = ['mcq', 'numerical', 'assertion']
        question_type = random.choice(question_types)
        
        # Sample question templates
        if question_type == 'mcq':
            question_text = f"Which of the following is true about {topic['name']}?"
            options = [
                f"Option A about {topic['name']}",
                f"Option B about {topic['name']}",
                f"Option C about {topic['name']}",
                f"Option D about {topic['name']}"
            ]
            correct_answer = "0"  # First option
            explanation = f"The correct answer is related to the fundamental concept of {topic['name']}."
        
        elif question_type == 'numerical':
            question_text = f"Calculate the value related to {topic['name']} given the following conditions."
            options = []
            correct_answer = "42"  # Sample numerical answer
            explanation = f"The calculation involves applying the principles of {topic['name']}."
        
        else:  # assertion
            question_text = f"Assertion: {topic['name']} follows certain principles. Reason: These principles are fundamental."
            options = [
                "Both assertion and reason are true and reason is the correct explanation",
                "Both assertion and reason are true but reason is not the correct explanation",
                "Assertion is true but reason is false",
                "Assertion is false but reason is true"
            ]
            correct_answer = "0"
            explanation = f"The assertion about {topic['name']} is based on fundamental principles."
        
        # Create question dictionary
        question = {
            'id': str(uuid.uuid4()),
            'topic_id': topic['id'],
            'question_text': question_text,
            'question_type': question_type,
            'difficulty_level': difficulty,
            'options': json.dumps(options),
            'correct_answer': correct_answer,
            'explanation': explanation,
            'year': None,
            'exam_type': 'generated',
            'source': 'ai_generated'
        }
        
        # Save to database
        self.save_question(question)
        
        return question
    
    def save_question(self, question: Dict):
        """Save a generated question to the database"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO questions 
            (id, topic_id, question_text, question_type, difficulty_level, options, 
             correct_answer, explanation, year, exam_type, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            question['id'], question['topic_id'], question['question_text'],
            question['question_type'], question['difficulty_level'], question['options'],
            question['correct_answer'], question['explanation'], question['year'],
            question['exam_type'], question['source']
        ))
        
        conn.commit()
        conn.close()
    
    def start_mock_test(self, mock_test_id: str) -> Dict:
        """Start a mock test session"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Update test status
        cursor.execute('''
            UPDATE mock_tests 
            SET status = 'in_progress'
            WHERE id = ?
        ''', (mock_test_id,))
        
        conn.commit()
        conn.close()
        
        # Generate questions if not already generated
        questions = self.generate_mock_test_questions(mock_test_id)
        
        return {
            'mock_test_id': mock_test_id,
            'questions': questions,
            'total_questions': len(questions),
            'start_time': datetime.now().isoformat()
        }
    
    def submit_answer(self, mock_test_id: str, question_id: str, user_answer: str, 
                     time_taken: int) -> Dict:
        """Submit an answer for a mock test question"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get correct answer
        cursor.execute('''
            SELECT correct_answer FROM questions WHERE id = ?
        ''', (question_id,))
        correct_answer = cursor.fetchone()
        
        if not correct_answer:
            conn.close()
            return {"error": "Question not found"}
        
        is_correct = user_answer.strip().lower() == correct_answer[0].strip().lower()
        
        # Update response
        cursor.execute('''
            UPDATE mock_test_responses 
            SET user_answer = ?, is_correct = ?, time_taken = ?
            WHERE mock_test_id = ? AND question_id = ?
        ''', (user_answer, is_correct, time_taken, mock_test_id, question_id))
        
        conn.commit()
        conn.close()
        
        return {
            'is_correct': is_correct,
            'correct_answer': correct_answer[0],
            'submitted': True
        }
    
    def complete_mock_test(self, mock_test_id: str) -> Dict:
        """Complete a mock test and calculate results"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get test details
        cursor.execute('''
            SELECT * FROM mock_tests WHERE id = ?
        ''', (mock_test_id,))
        test_data = cursor.fetchone()
        
        if not test_data:
            conn.close()
            return {"error": "Test not found"}
        
        # Get all responses
        cursor.execute('''
            SELECT mtr.*, q.question_type, q.difficulty_level, t.subject_id, s.name as subject_name
            FROM mock_test_responses mtr
            JOIN questions q ON mtr.question_id = q.id
            JOIN topics t ON q.topic_id = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE mtr.mock_test_id = ?
        ''', (mock_test_id,))
        
        responses = cursor.fetchall()
        
        # Calculate scores
        exam_type = test_data[2]  # exam_type column
        config = self.exam_configs[exam_type]
        
        total_score = 0
        correct_answers = 0
        subject_scores = {}
        
        # Initialize subject scores
        for subject_name in config['subjects']:
            subject_scores[subject_name] = {'correct': 0, 'total': 0, 'score': 0}
        
        for response in responses:
            subject_name = response[12]  # subject_name
            if subject_name not in subject_scores:
                continue
                
            subject_scores[subject_name]['total'] += 1
            
            if response[3]:  # is_correct
                correct_answers += 1
                subject_scores[subject_name]['correct'] += 1
                marks = config['subjects'][subject_name]['marks_per_question']
                total_score += marks
                subject_scores[subject_name]['score'] += marks
            elif response[2] is not None:  # attempted but wrong
                total_score += config['negative_marking']
                subject_scores[subject_name]['score'] += config['negative_marking']
        
        # Calculate percentile (simplified)
        max_score = sum(config['subjects'][subject]['questions'] * config['subjects'][subject]['marks_per_question'] 
                       for subject in config['subjects'])
        
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Simple percentile calculation (in real system, compare with other students)
        if percentage >= 95:
            percentile = 99
        elif percentage >= 80:
            percentile = 95
        elif percentage >= 60:
            percentile = 85
        elif percentage >= 40:
            percentile = 70
        else:
            percentile = max(0, percentage)
        
        # Update mock test with results
        cursor.execute('''
            UPDATE mock_tests 
            SET status = 'completed', score = ?, percentile = ?
            WHERE id = ?
        ''', (total_score, percentile, mock_test_id))
        
        conn.commit()
        conn.close()
        
        # Calculate analytics
        analytics = self.calculate_test_analytics(responses, subject_scores)
        
        return {
            'mock_test_id': mock_test_id,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
            'percentile': percentile,
            'correct_answers': correct_answers,
            'total_questions': len(responses),
            'subject_scores': subject_scores,
            'analytics': analytics,
            'recommendations': self.generate_recommendations(subject_scores, analytics)
        }
    
    def calculate_test_analytics(self, responses: List[Tuple], subject_scores: Dict) -> Dict:
        """Calculate detailed test analytics"""
        analytics = {
            'time_analysis': {},
            'difficulty_analysis': {},
            'subject_analysis': subject_scores,
            'weak_areas': [],
            'strong_areas': []
        }
        
        # Time analysis
        total_time = sum(response[4] for response in responses if response[4])  # time_taken
        avg_time_per_question = total_time / len(responses) if responses else 0
        
        analytics['time_analysis'] = {
            'total_time': total_time,
            'avg_time_per_question': avg_time_per_question,
            'time_management': 'good' if avg_time_per_question < 120 else 'needs_improvement'
        }
        
        # Difficulty analysis
        difficulty_stats = {}
        for response in responses:
            difficulty = response[10]  # difficulty_level
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {'correct': 0, 'total': 0}
            
            difficulty_stats[difficulty]['total'] += 1
            if response[3]:  # is_correct
                difficulty_stats[difficulty]['correct'] += 1
        
        analytics['difficulty_analysis'] = difficulty_stats
        
        # Identify weak and strong areas
        for subject, scores in subject_scores.items():
            if scores['total'] > 0:
                accuracy = scores['correct'] / scores['total']
                if accuracy < 0.4:
                    analytics['weak_areas'].append(subject)
                elif accuracy > 0.7:
                    analytics['strong_areas'].append(subject)
        
        return analytics
    
    def generate_recommendations(self, subject_scores: Dict, analytics: Dict) -> List[str]:
        """Generate personalized recommendations based on test performance"""
        recommendations = []
        
        # Subject-specific recommendations
        for subject, scores in subject_scores.items():
            if scores['total'] > 0:
                accuracy = scores['correct'] / scores['total']
                if accuracy < 0.4:
                    recommendations.append(f"📚 Focus on {subject} fundamentals - accuracy is {accuracy:.1%}")
                elif accuracy > 0.8:
                    recommendations.append(f"🎯 Excellent work in {subject}! Try advanced problems")
        
        # Time management recommendations
        if analytics['time_analysis']['time_management'] == 'needs_improvement':
            recommendations.append("⏰ Work on time management - practice with time limits")
        
        # Difficulty-based recommendations
        difficulty_stats = analytics['difficulty_analysis']
        if 1 in difficulty_stats and difficulty_stats[1]['total'] > 0:
            easy_accuracy = difficulty_stats[1]['correct'] / difficulty_stats[1]['total']
            if easy_accuracy < 0.8:
                recommendations.append("🌱 Strengthen your basics - focus on easier topics first")
        
        # General recommendations
        if not recommendations:
            recommendations.append("🎉 Good overall performance! Keep practicing consistently")
        
        return recommendations
    
    def get_mock_test(self, mock_test_id: str) -> Optional[Dict]:
        """Get mock test details"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM mock_tests WHERE id = ?
        ''', (mock_test_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        columns = ['id', 'user_id', 'exam_type', 'test_name', 'scheduled_date', 
                  'duration', 'total_questions', 'status', 'score', 'percentile', 'created_at']
        
        return dict(zip(columns, result))
    
    def get_user_mock_tests(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's mock test history"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM mock_tests 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'user_id', 'exam_type', 'test_name', 'scheduled_date', 
                  'duration', 'total_questions', 'status', 'score', 'percentile', 'created_at']
        
        return [dict(zip(columns, row)) for row in results]
    
    def get_performance_trends(self, user_id: str) -> Dict:
        """Get performance trends across multiple mock tests"""
        tests = self.get_user_mock_tests(user_id, 20)
        completed_tests = [t for t in tests if t['status'] == 'completed']
        
        if not completed_tests:
            return {'trends': [], 'improvement': 'insufficient_data'}
        
        # Calculate trends
        scores = [t['score'] for t in completed_tests]
        percentiles = [t['percentile'] for t in completed_tests]
        
        # Simple trend analysis
        if len(scores) >= 3:
            recent_avg = sum(scores[-3:]) / 3
            older_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]
            
            if recent_avg > older_avg * 1.1:
                trend = 'improving'
            elif recent_avg < older_avg * 0.9:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'total_tests': len(completed_tests),
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'avg_percentile': sum(percentiles) / len(percentiles) if percentiles else 0,
            'best_score': max(scores) if scores else 0,
            'recent_performance': scores[-3:] if len(scores) >= 3 else scores,
            'trend': trend,
            'improvement_rate': (recent_avg - older_avg) / older_avg * 100 if len(scores) >= 3 and older_avg > 0 else 0
        }
    
    def schedule_regular_tests(self, user_id: str, exam_type: str, frequency: str = 'weekly') -> List[str]:
        """Schedule regular mock tests"""
        scheduled_tests = []
        
        if frequency == 'weekly':
            # Schedule next 4 weeks
            for week in range(1, 5):
                test_date = datetime.now() + timedelta(weeks=week)
                test_name = f"Weekly Mock Test - Week {week}"
                
                test_id = self.schedule_mock_test(user_id, exam_type, test_name, test_date)
                scheduled_tests.append(test_id)
        
        elif frequency == 'bi_weekly':
            # Schedule next 8 weeks (every 2 weeks)
            for week in range(2, 9, 2):
                test_date = datetime.now() + timedelta(weeks=week)
                test_name = f"Bi-weekly Mock Test - Week {week}"
                
                test_id = self.schedule_mock_test(user_id, exam_type, test_name, test_date)
                scheduled_tests.append(test_id)
        
        return scheduled_tests
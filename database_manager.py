import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

class DatabaseManager:
    def __init__(self, db_path: str = "enhanced_ai_coach.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                exam_type TEXT NOT NULL,  -- JEE or NEET
                target_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User profiles with enhanced JEE/NEET specific data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                learning_style TEXT DEFAULT 'mixed',
                difficulty_preference TEXT DEFAULT 'medium',
                preferred_explanation_style TEXT DEFAULT 'analogies',
                confidence_level REAL DEFAULT 0.5,
                curiosity_level REAL DEFAULT 0.7,
                patience_level REAL DEFAULT 0.6,
                current_level TEXT DEFAULT 'beginner',
                adaptive_difficulty REAL DEFAULT 0.5,
                study_hours_per_day INTEGER DEFAULT 4,
                preferred_study_time TEXT DEFAULT 'morning',
                weak_subjects TEXT DEFAULT '[]',  -- JSON array
                strong_subjects TEXT DEFAULT '[]',  -- JSON array
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Subjects and topics for JEE/NEET
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                exam_type TEXT NOT NULL,  -- JEE, NEET, or BOTH
                weightage INTEGER DEFAULT 33,  -- percentage weightage
                total_chapters INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                subject_id TEXT NOT NULL,
                name TEXT NOT NULL,
                chapter_number INTEGER,
                difficulty_level INTEGER DEFAULT 1,  -- 1-5 scale
                importance INTEGER DEFAULT 3,  -- 1-5 scale
                estimated_hours INTEGER DEFAULT 8,
                prerequisites TEXT DEFAULT '[]',  -- JSON array of topic IDs
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        # User progress tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                mastery_level REAL DEFAULT 0.0,  -- 0-1 scale
                time_spent INTEGER DEFAULT 0,  -- minutes
                last_studied TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                status TEXT DEFAULT 'not_started',  -- not_started, in_progress, completed, struggling
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (topic_id) REFERENCES topics (id),
                UNIQUE(user_id, topic_id)
            )
        ''')
        
        # Learning sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                topic_id TEXT,
                session_type TEXT NOT NULL,  -- study, quiz, mock_test, revision
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration INTEGER DEFAULT 0,  -- minutes
                performance_score REAL DEFAULT 0.0,
                understanding_level INTEGER DEFAULT 3,  -- 1-5 scale
                mood TEXT DEFAULT 'neutral',
                notes TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        
        # Roadmaps
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmaps (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                week_number INTEGER NOT NULL,
                year INTEGER NOT NULL,
                status TEXT DEFAULT 'active',  -- active, completed, skipped
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmap_items (
                id TEXT PRIMARY KEY,
                roadmap_id TEXT NOT NULL,
                topic_id TEXT NOT NULL,
                day_of_week INTEGER NOT NULL,  -- 1-7 (Monday-Sunday)
                study_hours INTEGER DEFAULT 2,
                priority INTEGER DEFAULT 1,  -- 1-5 scale
                status TEXT DEFAULT 'pending',  -- pending, completed, skipped
                FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id),
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        
        # Questions and answers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                topic_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL,  -- mcq, numerical, assertion, comprehension
                difficulty_level INTEGER DEFAULT 1,  -- 1-5 scale
                options TEXT DEFAULT '[]',  -- JSON array for MCQ
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                year INTEGER,  -- for previous year questions
                exam_type TEXT,  -- JEE_MAIN, JEE_ADVANCED, NEET
                source TEXT DEFAULT 'generated',
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        
        # Mock tests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mock_tests (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                exam_type TEXT NOT NULL,  -- JEE_MAIN, JEE_ADVANCED, NEET
                test_name TEXT NOT NULL,
                scheduled_date TIMESTAMP,
                duration INTEGER DEFAULT 180,  -- minutes
                total_questions INTEGER DEFAULT 90,
                status TEXT DEFAULT 'scheduled',  -- scheduled, in_progress, completed
                score REAL DEFAULT 0.0,
                percentile REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mock_test_responses (
                id TEXT PRIMARY KEY,
                mock_test_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                user_answer TEXT,
                is_correct BOOLEAN DEFAULT 0,
                time_taken INTEGER DEFAULT 0,  -- seconds
                marked_for_review BOOLEAN DEFAULT 0,
                FOREIGN KEY (mock_test_id) REFERENCES mock_tests (id),
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        ''')
        
        # AI Coach interactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coach_conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                coach_response TEXT NOT NULL,
                conversation_type TEXT DEFAULT 'general',  -- general, doubt, strategy, motivation
                topic_id TEXT,
                sentiment TEXT DEFAULT 'neutral',  -- positive, negative, neutral, frustrated
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        
        # Knowledge base for semantic search
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id TEXT PRIMARY KEY,
                topic_id TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'concept',  -- concept, formula, example, strategy
                embedding TEXT,  -- JSON array of embeddings
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize with JEE and NEET data
        self.populate_initial_data()
    
    def populate_initial_data(self):
        """Populate initial subjects and topics for JEE and NEET"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM subjects")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # JEE and NEET subjects
        subjects_data = [
            # Physics
            {
                'id': 'physics_jee_neet',
                'name': 'Physics',
                'exam_type': 'BOTH',
                'weightage': 33,
                'total_chapters': 30
            },
            # Chemistry
            {
                'id': 'chemistry_jee_neet',
                'name': 'Chemistry',
                'exam_type': 'BOTH',
                'weightage': 33,
                'total_chapters': 30
            },
            # Mathematics (JEE only)
            {
                'id': 'mathematics_jee',
                'name': 'Mathematics',
                'exam_type': 'JEE',
                'weightage': 34,
                'total_chapters': 25
            },
            # Biology (NEET only)
            {
                'id': 'biology_neet',
                'name': 'Biology',
                'exam_type': 'NEET',
                'weightage': 34,
                'total_chapters': 40
            }
        ]
        
        for subject in subjects_data:
            cursor.execute('''
                INSERT OR REPLACE INTO subjects (id, name, exam_type, weightage, total_chapters)
                VALUES (?, ?, ?, ?, ?)
            ''', (subject['id'], subject['name'], subject['exam_type'], subject['weightage'], subject['total_chapters']))
        
        # Physics topics
        physics_topics = [
            ('Mechanics', 1, 4, 5, 40),
            ('Heat and Thermodynamics', 2, 3, 4, 25),
            ('Waves and Oscillations', 3, 4, 4, 30),
            ('Electricity and Magnetism', 4, 5, 5, 45),
            ('Optics', 5, 3, 4, 20),
            ('Modern Physics', 6, 4, 4, 25),
            ('Semiconductors', 7, 3, 3, 15),
            ('Communication Systems', 8, 2, 3, 12),
            ('Gravitation', 9, 3, 4, 18),
            ('Rotational Motion', 10, 4, 4, 22),
            ('Simple Harmonic Motion', 11, 3, 4, 20),
            ('Fluid Mechanics', 12, 3, 3, 18),
            ('Kinetic Theory of Gases', 13, 3, 3, 16),
            ('Electromagnetic Waves', 14, 4, 4, 20),
            ('Alternating Current', 15, 4, 4, 25)
        ]
        
        for topic_name, chapter, difficulty, importance, hours in physics_topics:
            topic_id = f"physics_{topic_name.lower().replace(' ', '_')}"
            cursor.execute('''
                INSERT OR REPLACE INTO topics (id, subject_id, name, chapter_number, difficulty_level, importance, estimated_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (topic_id, 'physics_jee_neet', topic_name, chapter, difficulty, importance, hours))
        
        # Chemistry topics
        chemistry_topics = [
            ('Atomic Structure', 1, 3, 5, 20),
            ('Chemical Bonding', 2, 4, 5, 25),
            ('Thermodynamics', 3, 4, 4, 30),
            ('Chemical Equilibrium', 4, 4, 4, 25),
            ('Ionic Equilibrium', 5, 4, 4, 22),
            ('Electrochemistry', 6, 4, 4, 28),
            ('Chemical Kinetics', 7, 4, 4, 25),
            ('Organic Chemistry Basics', 8, 3, 5, 35),
            ('Hydrocarbons', 9, 3, 4, 30),
            ('Organic Reactions', 10, 5, 5, 40),
            ('Biomolecules', 11, 3, 3, 20),
            ('Polymers', 12, 2, 3, 15),
            ('Coordination Compounds', 13, 4, 4, 25),
            ('Metallurgy', 14, 3, 3, 18),
            ('P-Block Elements', 15, 3, 4, 22)
        ]
        
        for topic_name, chapter, difficulty, importance, hours in chemistry_topics:
            topic_id = f"chemistry_{topic_name.lower().replace(' ', '_')}"
            cursor.execute('''
                INSERT OR REPLACE INTO topics (id, subject_id, name, chapter_number, difficulty_level, importance, estimated_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (topic_id, 'chemistry_jee_neet', topic_name, chapter, difficulty, importance, hours))
        
        # Mathematics topics (JEE only)
        math_topics = [
            ('Algebra', 1, 4, 5, 45),
            ('Trigonometry', 2, 4, 5, 35),
            ('Coordinate Geometry', 3, 5, 5, 40),
            ('Calculus', 4, 5, 5, 50),
            ('Vectors', 5, 4, 4, 25),
            ('3D Geometry', 6, 4, 4, 30),
            ('Probability', 7, 4, 4, 25),
            ('Statistics', 8, 3, 3, 20),
            ('Complex Numbers', 9, 4, 4, 22),
            ('Matrices and Determinants', 10, 4, 4, 28),
            ('Sequences and Series', 11, 3, 4, 20),
            ('Binomial Theorem', 12, 3, 3, 15),
            ('Permutations and Combinations', 13, 3, 4, 18),
            ('Mathematical Reasoning', 14, 2, 3, 12),
            ('Sets and Functions', 15, 3, 4, 20)
        ]
        
        for topic_name, chapter, difficulty, importance, hours in math_topics:
            topic_id = f"mathematics_{topic_name.lower().replace(' ', '_')}"
            cursor.execute('''
                INSERT OR REPLACE INTO topics (id, subject_id, name, chapter_number, difficulty_level, importance, estimated_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (topic_id, 'mathematics_jee', topic_name, chapter, difficulty, importance, hours))
        
        # Biology topics (NEET only)
        biology_topics = [
            ('Cell Biology', 1, 3, 5, 25),
            ('Genetics', 2, 4, 5, 30),
            ('Evolution', 3, 3, 4, 20),
            ('Plant Physiology', 4, 4, 4, 28),
            ('Animal Physiology', 5, 4, 5, 35),
            ('Ecology', 6, 3, 4, 22),
            ('Reproduction', 7, 3, 4, 25),
            ('Biotechnology', 8, 4, 4, 20),
            ('Molecular Biology', 9, 4, 4, 25),
            ('Human Health', 10, 3, 4, 20),
            ('Morphology of Plants', 11, 2, 3, 18),
            ('Morphology of Animals', 12, 2, 3, 18),
            ('Diversity of Life', 13, 3, 4, 22),
            ('Biomolecules', 14, 3, 4, 20),
            ('Respiration', 15, 4, 4, 25)
        ]
        
        for topic_name, chapter, difficulty, importance, hours in biology_topics:
            topic_id = f"biology_{topic_name.lower().replace(' ', '_')}"
            cursor.execute('''
                INSERT OR REPLACE INTO topics (id, subject_id, name, chapter_number, difficulty_level, importance, estimated_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (topic_id, 'biology_neet', topic_name, chapter, difficulty, importance, hours))
        
        conn.commit()
        conn.close()
    
    def create_user(self, name: str, exam_type: str, target_year: int = 2025) -> str:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (id, name, exam_type, target_year)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, exam_type, target_year))
        
        # Create user profile
        cursor.execute('''
            INSERT INTO user_profiles (user_id)
            VALUES (?)
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, up.* FROM users u
            JOIN user_profiles up ON u.id = up.user_id
            WHERE u.id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        return None
    
    def update_user_profile(self, user_id: str, **kwargs):
        """Update user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update user_profiles table
        profile_fields = ['learning_style', 'difficulty_preference', 'preferred_explanation_style',
                         'confidence_level', 'curiosity_level', 'patience_level', 'current_level',
                         'adaptive_difficulty', 'study_hours_per_day', 'preferred_study_time',
                         'weak_subjects', 'strong_subjects']
        
        for field in profile_fields:
            if field in kwargs:
                cursor.execute(f'''
                    UPDATE user_profiles SET {field} = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (kwargs[field], user_id))
        
        conn.commit()
        conn.close()
    
    def get_subjects_for_exam(self, exam_type: str) -> List[Dict]:
        """Get subjects for specific exam type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM subjects 
            WHERE exam_type = ? OR exam_type = 'BOTH'
        ''', (exam_type,))
        
        results = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'name', 'exam_type', 'weightage', 'total_chapters']
        return [dict(zip(columns, row)) for row in results]
    
    def get_topics_for_subject(self, subject_id: str) -> List[Dict]:
        """Get topics for a specific subject"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM topics 
            WHERE subject_id = ?
            ORDER BY chapter_number
        ''', (subject_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'subject_id', 'name', 'chapter_number', 'difficulty_level', 
                  'importance', 'estimated_hours', 'prerequisites']
        return [dict(zip(columns, row)) for row in results]
    
    def update_progress(self, user_id: str, topic_id: str, mastery_level: float, 
                       time_spent: int, attempts: int = 0, correct_answers: int = 0):
        """Update user progress for a topic"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine status based on mastery level
        if mastery_level >= 0.8:
            status = 'completed'
        elif mastery_level >= 0.4:
            status = 'in_progress'
        elif attempts > 3 and mastery_level < 0.3:
            status = 'struggling'
        else:
            status = 'in_progress'
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_progress 
            (id, user_id, topic_id, mastery_level, time_spent, last_studied, attempts, correct_answers, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (f"{user_id}_{topic_id}", user_id, topic_id, mastery_level, time_spent, 
              datetime.now(), attempts, correct_answers, status))
        
        conn.commit()
        conn.close()
    
    def get_user_progress(self, user_id: str) -> List[Dict]:
        """Get all user progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT up.*, t.name as topic_name, t.subject_id, s.name as subject_name
            FROM user_progress up
            JOIN topics t ON up.topic_id = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE up.user_id = ?
            ORDER BY up.last_studied DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'user_id', 'topic_id', 'mastery_level', 'time_spent', 
                  'last_studied', 'attempts', 'correct_answers', 'status',
                  'topic_name', 'subject_id', 'subject_name']
        return [dict(zip(columns, row)) for row in results]
    
    def save_conversation(self, user_id: str, user_message: str, coach_response: str, 
                         conversation_type: str = 'general', topic_id: str = None, 
                         sentiment: str = 'neutral'):
        """Save AI coach conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conversation_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO coach_conversations 
            (id, user_id, user_message, coach_response, conversation_type, topic_id, sentiment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (conversation_id, user_id, user_message, coach_response, conversation_type, topic_id, sentiment))
        
        conn.commit()
        conn.close()
        return conversation_id
    
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM coach_conversations 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'user_id', 'user_message', 'coach_response', 'conversation_type', 
                  'topic_id', 'sentiment', 'created_at']
        return [dict(zip(columns, row)) for row in results]
    
    def create_learning_session(self, user_id: str, topic_id: str, session_type: str) -> str:
        """Create a new learning session"""
        session_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_sessions 
            (id, user_id, topic_id, session_type, start_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, topic_id, session_type, datetime.now()))
        
        conn.commit()
        conn.close()
        return session_id
    
    def end_learning_session(self, session_id: str, performance_score: float, 
                           understanding_level: int, mood: str = 'neutral', notes: str = ''):
        """End a learning session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE learning_sessions 
            SET end_time = ?, performance_score = ?, understanding_level = ?, mood = ?, notes = ?
            WHERE id = ?
        ''', (datetime.now(), performance_score, understanding_level, mood, notes, session_id))
        
        # Calculate duration
        cursor.execute('''
            UPDATE learning_sessions 
            SET duration = (julianday(end_time) - julianday(start_time)) * 24 * 60
            WHERE id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
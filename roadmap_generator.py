import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random
from database_manager import DatabaseManager

class RoadmapGenerator:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def generate_weekly_roadmap(self, user_id: str, week_offset: int = 0) -> Dict:
        """Generate weekly roadmap based on user progress and exam type"""
        
        # Get user profile
        user_profile = self.db.get_user_profile(user_id)
        if not user_profile:
            return {"error": "User not found"}
        
        exam_type = user_profile['exam_type']
        target_year = user_profile['target_year']
        
        # Calculate target week
        today = datetime.now()
        target_week = today + timedelta(weeks=week_offset)
        week_number = target_week.isocalendar()[1]
        year = target_week.year
        
        # Get user progress to identify focus areas
        progress = self.db.get_user_progress(user_id)
        
        # Get subjects for the exam type
        subjects = self.db.get_subjects_for_exam(exam_type)
        
        # Create roadmap strategy
        roadmap_strategy = self.create_roadmap_strategy(user_profile, progress, subjects)
        
        # Generate weekly plan
        weekly_plan = self.generate_weekly_plan(roadmap_strategy, user_profile)
        
        # Save roadmap to database
        roadmap_id = self.save_roadmap(user_id, week_number, year, weekly_plan)
        
        return {
            'roadmap_id': roadmap_id,
            'week_number': week_number,
            'year': year,
            'exam_type': exam_type,
            'study_hours_per_day': user_profile['study_hours_per_day'],
            'weekly_plan': weekly_plan,
            'strategy': roadmap_strategy
        }
    
    def create_roadmap_strategy(self, user_profile: Dict, progress: List[Dict], subjects: List[Dict]) -> Dict:
        """Create personalized roadmap strategy"""
        
        # Calculate months remaining until exam
        target_year = user_profile['target_year']
        exam_month = 4 if user_profile['exam_type'] == 'JEE' else 5  # JEE in April, NEET in May
        exam_date = datetime(target_year, exam_month, 1)
        months_remaining = max(1, (exam_date.year - datetime.now().year) * 12 + exam_date.month - datetime.now().month)
        
        # Analyze current progress
        if not progress:
            phase = 'foundation'
            focus_areas = ['basic_concepts', 'ncert_completion']
        else:
            avg_mastery = sum(p['mastery_level'] for p in progress) / len(progress)
            if avg_mastery < 0.3:
                phase = 'foundation'
                focus_areas = ['concept_building', 'basic_practice']
            elif avg_mastery < 0.6:
                phase = 'intermediate'
                focus_areas = ['problem_solving', 'previous_year_questions']
            else:
                phase = 'advanced'
                focus_areas = ['mock_tests', 'advanced_problems', 'revision']
        
        # Identify weak and strong subjects
        subject_performance = {}
        for subject in subjects:
            subject_progress = [p for p in progress if p['subject_name'] == subject['name']]
            if subject_progress:
                avg_mastery = sum(p['mastery_level'] for p in subject_progress) / len(subject_progress)
                subject_performance[subject['name']] = avg_mastery
            else:
                subject_performance[subject['name']] = 0.0
        
        # Determine time allocation based on exam type and performance
        if user_profile['exam_type'] == 'JEE':
            base_allocation = {'Physics': 33, 'Chemistry': 33, 'Mathematics': 34}
        else:  # NEET
            base_allocation = {'Physics': 25, 'Chemistry': 25, 'Biology': 50}
        
        # Adjust allocation based on performance
        adjusted_allocation = {}
        for subject, base_percent in base_allocation.items():
            if subject in subject_performance:
                performance = subject_performance[subject]
                if performance < 0.3:
                    # Increase time for weak subjects
                    adjusted_allocation[subject] = min(50, base_percent + 10)
                elif performance > 0.7:
                    # Reduce time for strong subjects
                    adjusted_allocation[subject] = max(20, base_percent - 5)
                else:
                    adjusted_allocation[subject] = base_percent
            else:
                adjusted_allocation[subject] = base_percent
        
        # Normalize to 100%
        total = sum(adjusted_allocation.values())
        for subject in adjusted_allocation:
            adjusted_allocation[subject] = round(adjusted_allocation[subject] * 100 / total)
        
        return {
            'phase': phase,
            'months_remaining': months_remaining,
            'focus_areas': focus_areas,
            'subject_allocation': adjusted_allocation,
            'subject_performance': subject_performance,
            'priority_subjects': self.get_priority_subjects(subject_performance),
            'study_intensity': self.calculate_study_intensity(months_remaining, phase)
        }
    
    def get_priority_subjects(self, subject_performance: Dict) -> List[str]:
        """Get priority subjects based on performance"""
        # Sort subjects by performance (ascending - worst first)
        sorted_subjects = sorted(subject_performance.items(), key=lambda x: x[1])
        return [subject for subject, _ in sorted_subjects]
    
    def calculate_study_intensity(self, months_remaining: int, phase: str) -> str:
        """Calculate recommended study intensity"""
        if months_remaining <= 2:
            return 'high'
        elif months_remaining <= 6:
            return 'medium_high'
        elif months_remaining <= 12:
            return 'medium'
        else:
            return 'low_medium'
    
    def generate_weekly_plan(self, strategy: Dict, user_profile: Dict) -> Dict:
        """Generate detailed weekly study plan"""
        
        study_hours_per_day = user_profile['study_hours_per_day']
        total_weekly_hours = study_hours_per_day * 7
        
        # Allocate hours to subjects
        subject_hours = {}
        for subject, percentage in strategy['subject_allocation'].items():
            subject_hours[subject] = round(total_weekly_hours * percentage / 100)
        
        # Create day-wise plan
        weekly_plan = {}
        
        # Get topics for each subject
        subjects = self.db.get_subjects_for_exam(user_profile['exam_type'])
        all_topics = {}
        for subject in subjects:
            all_topics[subject['name']] = self.db.get_topics_for_subject(subject['id'])
        
        # Generate 7-day plan
        for day in range(1, 8):  # Monday to Sunday
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day-1]
            
            if day == 7:  # Sunday - revision and mock tests
                weekly_plan[day_name] = {
                    'day': day,
                    'focus': 'revision_and_assessment',
                    'activities': [
                        {'type': 'revision', 'duration': study_hours_per_day//2, 'subject': 'Mixed'},
                        {'type': 'mock_test', 'duration': study_hours_per_day//2, 'subject': 'Mixed'}
                    ]
                }
            else:
                # Regular study days
                primary_subject = strategy['priority_subjects'][day % len(strategy['priority_subjects'])]
                secondary_subject = strategy['priority_subjects'][(day + 1) % len(strategy['priority_subjects'])]
                
                # Get topics for the day
                primary_topics = self.select_topics_for_day(
                    all_topics.get(primary_subject, []), 
                    user_profile['user_id'], 
                    strategy['phase']
                )
                
                activities = []
                
                # Primary subject (70% of time)
                primary_hours = int(study_hours_per_day * 0.7)
                if primary_topics:
                    activities.append({
                        'type': 'concept_study',
                        'subject': primary_subject,
                        'topic': primary_topics[0]['name'],
                        'topic_id': primary_topics[0]['id'],
                        'duration': primary_hours,
                        'priority': 'high'
                    })
                
                # Secondary subject (20% of time)
                secondary_hours = int(study_hours_per_day * 0.2)
                if secondary_subject in all_topics:
                    secondary_topics = self.select_topics_for_day(
                        all_topics[secondary_subject], 
                        user_profile['user_id'], 
                        strategy['phase']
                    )
                    if secondary_topics:
                        activities.append({
                            'type': 'practice',
                            'subject': secondary_subject,
                            'topic': secondary_topics[0]['name'],
                            'topic_id': secondary_topics[0]['id'],
                            'duration': secondary_hours,
                            'priority': 'medium'
                        })
                
                # Revision/Practice (10% of time)
                revision_hours = study_hours_per_day - primary_hours - secondary_hours
                activities.append({
                    'type': 'revision',
                    'subject': 'Mixed',
                    'duration': revision_hours,
                    'priority': 'low'
                })
                
                weekly_plan[day_name] = {
                    'day': day,
                    'focus': primary_subject,
                    'activities': activities
                }
        
        return weekly_plan
    
    def select_topics_for_day(self, topics: List[Dict], user_id: str, phase: str) -> List[Dict]:
        """Select appropriate topics for a study day"""
        if not topics:
            return []
        
        # Get user progress for these topics
        progress = self.db.get_user_progress(user_id)
        topic_progress = {p['topic_id']: p for p in progress}
        
        # Filter topics based on phase and progress
        suitable_topics = []
        for topic in topics:
            topic_id = topic['id']
            user_progress = topic_progress.get(topic_id, {})
            mastery_level = user_progress.get('mastery_level', 0.0)
            
            if phase == 'foundation':
                # Focus on basic and unstarted topics
                if mastery_level < 0.4:
                    suitable_topics.append(topic)
            elif phase == 'intermediate':
                # Focus on partially learned topics
                if 0.3 <= mastery_level < 0.7:
                    suitable_topics.append(topic)
            else:  # advanced
                # Focus on nearly mastered topics for perfection
                if mastery_level >= 0.6:
                    suitable_topics.append(topic)
        
        # If no suitable topics, fall back to all topics
        if not suitable_topics:
            suitable_topics = topics
        
        # Sort by importance and difficulty
        suitable_topics.sort(key=lambda x: (x['importance'], x['difficulty_level']), reverse=True)
        
        return suitable_topics[:3]  # Return top 3 topics
    
    def save_roadmap(self, user_id: str, week_number: int, year: int, weekly_plan: Dict) -> str:
        """Save roadmap to database"""
        roadmap_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Insert roadmap
        cursor.execute('''
            INSERT INTO roadmaps (id, user_id, week_number, year, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (roadmap_id, user_id, week_number, year, 'active'))
        
        # Insert roadmap items
        for day_name, day_plan in weekly_plan.items():
            for activity in day_plan['activities']:
                if activity.get('topic_id'):
                    cursor.execute('''
                        INSERT INTO roadmap_items (id, roadmap_id, topic_id, day_of_week, study_hours, priority)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        str(uuid.uuid4()),
                        roadmap_id,
                        activity['topic_id'],
                        day_plan['day'],
                        activity['duration'],
                        1 if activity['priority'] == 'high' else 2 if activity['priority'] == 'medium' else 3
                    ))
        
        conn.commit()
        conn.close()
        
        return roadmap_id
    
    def get_roadmap(self, user_id: str, week_offset: int = 0) -> Optional[Dict]:
        """Get roadmap for a specific week"""
        target_week = datetime.now() + timedelta(weeks=week_offset)
        week_number = target_week.isocalendar()[1]
        year = target_week.year
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.*, ri.*, t.name as topic_name, s.name as subject_name
            FROM roadmaps r
            LEFT JOIN roadmap_items ri ON r.id = ri.roadmap_id
            LEFT JOIN topics t ON ri.topic_id = t.id
            LEFT JOIN subjects s ON t.subject_id = s.id
            WHERE r.user_id = ? AND r.week_number = ? AND r.year = ?
        ''', (user_id, week_number, year))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return None
        
        # Build roadmap structure
        roadmap_info = results[0][:6]  # roadmap columns
        roadmap = {
            'id': roadmap_info[0],
            'user_id': roadmap_info[1],
            'week_number': roadmap_info[2],
            'year': roadmap_info[3],
            'status': roadmap_info[4],
            'items': []
        }
        
        for result in results:
            if result[6]:  # has roadmap item
                item = {
                    'id': result[6],
                    'topic_id': result[8],
                    'day_of_week': result[9],
                    'study_hours': result[10],
                    'priority': result[11],
                    'status': result[12],
                    'topic_name': result[13],
                    'subject_name': result[14]
                }
                roadmap['items'].append(item)
        
        return roadmap
    
    def update_roadmap_progress(self, roadmap_item_id: str, status: str):
        """Update progress on a roadmap item"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE roadmap_items 
            SET status = ?
            WHERE id = ?
        ''', (status, roadmap_item_id))
        
        conn.commit()
        conn.close()
    
    def get_roadmap_analytics(self, user_id: str, weeks_back: int = 4) -> Dict:
        """Get roadmap completion analytics"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get recent roadmaps
        cursor.execute('''
            SELECT r.week_number, r.year, ri.status, COUNT(*) as count
            FROM roadmaps r
            JOIN roadmap_items ri ON r.id = ri.roadmap_id
            WHERE r.user_id = ? AND r.week_number >= ?
            GROUP BY r.week_number, r.year, ri.status
            ORDER BY r.year DESC, r.week_number DESC
        ''', (user_id, datetime.now().isocalendar()[1] - weeks_back))
        
        results = cursor.fetchall()
        conn.close()
        
        # Process analytics
        weekly_stats = {}
        for result in results:
            week_key = f"{result[1]}-W{result[0]}"
            if week_key not in weekly_stats:
                weekly_stats[week_key] = {'completed': 0, 'pending': 0, 'skipped': 0, 'total': 0}
            
            weekly_stats[week_key][result[2]] = result[3]
            weekly_stats[week_key]['total'] += result[3]
        
        # Calculate completion rates
        for week in weekly_stats:
            total = weekly_stats[week]['total']
            completed = weekly_stats[week]['completed']
            weekly_stats[week]['completion_rate'] = (completed / total * 100) if total > 0 else 0
        
        return {
            'weekly_stats': weekly_stats,
            'avg_completion_rate': sum(w['completion_rate'] for w in weekly_stats.values()) / len(weekly_stats) if weekly_stats else 0,
            'total_weeks_tracked': len(weekly_stats)
        }
    
    def adapt_roadmap_based_on_performance(self, user_id: str) -> Dict:
        """Adapt future roadmaps based on user performance"""
        
        # Get recent performance data
        analytics = self.get_roadmap_analytics(user_id, 2)
        progress = self.db.get_user_progress(user_id)
        
        adaptations = []
        
        # If completion rate is low, reduce daily study hours
        if analytics['avg_completion_rate'] < 50:
            adaptations.append({
                'type': 'reduce_workload',
                'reason': 'Low completion rate',
                'action': 'Reduce daily study hours by 1'
            })
        
        # If certain subjects are consistently struggling
        subject_struggles = {}
        for p in progress:
            if p['status'] == 'struggling':
                subject = p['subject_name']
                subject_struggles[subject] = subject_struggles.get(subject, 0) + 1
        
        for subject, count in subject_struggles.items():
            if count >= 2:
                adaptations.append({
                    'type': 'increase_focus',
                    'subject': subject,
                    'reason': f'Struggling with {count} topics',
                    'action': f'Increase {subject} study time by 30%'
                })
        
        # If performance is excellent, increase difficulty
        if analytics['avg_completion_rate'] > 80:
            avg_mastery = sum(p['mastery_level'] for p in progress) / len(progress) if progress else 0
            if avg_mastery > 0.7:
                adaptations.append({
                    'type': 'increase_difficulty',
                    'reason': 'Excellent performance',
                    'action': 'Add advanced topics and mock tests'
                })
        
        return {
            'adaptations': adaptations,
            'recommended_changes': len(adaptations) > 0
        }
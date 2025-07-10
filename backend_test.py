import unittest
import sys
import os
import json
from file_processor import FileProcessor
from neuro_summarizer import NeuroSummarizer
from tts_engine import NeuroTTSEngine
from flashcard_generator import FlashcardGenerator
from focus_tracker import FocusTracker
from ai_coach import EnhancedAICoach
from quiz_system import EnhancedGamifiedQuizSystem
from session_manager import SessionManager
from config import DEFAULT_USER_ID


class EduVoiceBackendTests(unittest.TestCase):
    """Test suite for EduVoice.AI backend components"""

    def setUp(self):
        """Initialize components for testing"""
        self.user_id = DEFAULT_USER_ID
        self.file_processor = FileProcessor()
        self.summarizer = NeuroSummarizer()
        self.tts_engine = NeuroTTSEngine()
        self.flashcard_gen = FlashcardGenerator()
        self.focus_tracker = FocusTracker(self.user_id)
        self.ai_coach = EnhancedAICoach(self.user_id)
        self.quiz_system = EnhancedGamifiedQuizSystem(self.user_id)
        self.session_manager = SessionManager(self.user_id)

        # Sample test content
        self.test_content = """
        Machine learning is a field of inquiry devoted to understanding and building methods that 'learn', 
        that is, methods that leverage data to improve performance on some set of tasks. It is seen as a 
        part of artificial intelligence. Machine learning algorithms build a model based on sample data, 
        known as training data, in order to make predictions or decisions without being explicitly 
        programmed to do so. Machine learning algorithms are used in a wide variety of applications, 
        such as in medicine, email filtering, speech recognition, and computer vision, where it is 
        difficult or unfeasible to develop conventional algorithms to perform the needed tasks.
        """
        self.test_title = "Machine Learning Introduction"

    def test_file_processor(self):
        """Test file processor functionality"""
        print("\n--- Testing File Processor ---")
        try:
            filepath = self.file_processor.save_content(
                self.test_content, self.test_title, "Text Input"
            )
            self.assertIsNotNone(filepath)
            print(f"✅ File processor saved content to: {filepath}")

            # Test content exists
            self.assertTrue(os.path.exists(filepath))
            print("✅ File exists on disk")
        except Exception as e:
            print(f"❌ File processor test failed: {str(e)}")
            self.fail(str(e))

    def test_summarizer(self):
        """Test summarizer functionality"""
        print("\n--- Testing Neuro Summarizer ---")
        try:
            summaries = self.summarizer.get_all_summaries(self.test_content)
            self.assertIsInstance(summaries, dict)
            self.assertIn('basic', summaries)
            self.assertIn('story', summaries)
            self.assertIn('visual', summaries)
            print("✅ Summarizer generated all summary types")

            # Check content of summaries
            for summary_type, content in summaries.items():
                self.assertIsInstance(content, str)
                self.assertTrue(len(content) > 0)
                print(f"✅ {summary_type.capitalize()} summary generated successfully")
        except Exception as e:
            print(f"❌ Summarizer test failed: {str(e)}")
            self.fail(str(e))

    def test_tts_engine(self):
        """Test text-to-speech engine"""
        print("\n--- Testing TTS Engine ---")
        try:
            test_text = "This is a test of the text to speech engine."
            audio_file = self.tts_engine.create_audio_file(test_text)

            if audio_file:
                self.assertTrue(os.path.exists(audio_file))
                print(f"✅ TTS engine created audio file: {audio_file}")
            else:
                print("⚠️ TTS engine returned None - this might be expected if API keys aren't configured")
        except Exception as e:
            print(f"❌ TTS engine test failed: {str(e)}")
            self.fail(str(e))

    def test_flashcard_generator(self):
        """Test flashcard generator"""
        print("\n--- Testing Flashcard Generator ---")
        try:
            flashcards = self.flashcard_gen.generate_flashcards(self.test_content, "Easy")
            self.assertIsInstance(flashcards, list)

            if flashcards:
                print(f"✅ Generated {len(flashcards)} flashcards")

                # Check flashcard structure
                for card in flashcards:
                    self.assertIn('question', card)
                    self.assertIn('answer', card)
                    print(f"✅ Flashcard validated: {card['question'][:30]}...")
            else:
                print("⚠️ No flashcards generated - this might be expected if API keys aren't configured")
        except Exception as e:
            print(f"❌ Flashcard generator test failed: {str(e)}")
            self.fail(str(e))

    def test_quiz_system(self):
        """Test quiz system"""
        print("\n--- Testing Quiz System ---")
        try:
            questions = self.quiz_system.generate_quiz_questions(self.test_content, "Easy")

            if questions:
                self.assertIsInstance(questions, list)
                print(f"✅ Generated {len(questions)} quiz questions")

                # Check question structure
                for question in questions:
                    self.assertIn('question', question)
                    self.assertIn('options', question)
                    self.assertIn('correct_answer', question)
                    self.assertIn('explanation', question)
                    print(f"✅ Quiz question validated: {question['question'][:30]}...")

                # Test quiz session creation
                session_id = self.quiz_system.create_quiz_session(questions, self.test_title)
                self.assertIsNotNone(session_id)
                print(f"✅ Created quiz session with ID: {session_id}")

                # Test getting quiz session
                session = self.quiz_system.get_quiz_session(session_id)
                self.assertIsNotNone(session)
                self.assertEqual(session['title'], self.test_title)
                print("✅ Retrieved quiz session successfully")
            else:
                print("⚠️ No quiz questions generated - this might be expected if API keys aren't configured")
        except Exception as e:
            print(f"❌ Quiz system test failed: {str(e)}")
            self.fail(str(e))

    def test_focus_tracker(self):
        """Test focus tracker"""
        print("\n--- Testing Focus Tracker ---")
        try:
            # Start a focus session
            session_id = self.focus_tracker.start_focus_session("test", "Test Session")
            self.assertIsNotNone(session_id)
            print(f"✅ Started focus session with ID: {session_id}")

            # Get focus analytics
            analytics = self.focus_tracker.get_focus_analytics(7)  # Last 7 days
            self.assertIsInstance(analytics, dict)
            print("✅ Retrieved focus analytics successfully")
        except Exception as e:
            print(f"❌ Focus tracker test failed: {str(e)}")
            self.fail(str(e))

    def test_ai_coach(self):
        """Test AI coach"""
        print("\n--- Testing AI Coach ---")
        try:
            # Get motivational message
            message = self.ai_coach.generate_motivational_message()
            self.assertIsInstance(message, str)
            self.assertTrue(len(message) > 0)
            print(f"✅ Generated motivational message: {message[:50]}...")

            # Get learning suggestions
            suggestions = self.ai_coach.get_learning_suggestions()
            self.assertIsInstance(suggestions, list)
            print(f"✅ Generated {len(suggestions)} learning suggestions")

            # Test coach response
            response = self.ai_coach.generate_coach_response(
                "How can I improve my focus?", self.test_title
            )
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            print(f"✅ Generated coach response: {response[:50]}...")
        except Exception as e:
            print(f"❌ AI coach test failed: {str(e)}")
            self.fail(str(e))

    def test_session_manager(self):
        """Test session manager"""
        print("\n--- Testing Session Manager ---")
        try:
            # Test mood check-in
            result = self.session_manager.mood_checkin("😊")
            self.assertTrue(result)
            print("✅ Recorded mood check-in")

            # Get mood history
            mood_history = self.session_manager.get_mood_history(7)  # Last 7 days
            self.assertIsInstance(mood_history, list)
            print(f"✅ Retrieved mood history with {len(mood_history)} entries")

            # Get learning analytics
            analytics = self.session_manager.get_learning_analytics()
            self.assertIsInstance(analytics, dict)
            print("✅ Retrieved learning analytics successfully")
        except Exception as e:
            print(f"❌ Session manager test failed: {str(e)}")
            self.fail(str(e))


if __name__ == "__main__":
    print("=== Running EduVoice.AI Backend Tests ===")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\n=== Backend Tests Completed ===")
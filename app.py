# EduVoice.AI - Advanced Neuro-Friendly Learning Platform
# Enhanced with comprehensive learning features and Voice-to-Voice AI Coach

import streamlit as st
import whisper
import time
import os
import json
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
import base64
import tempfile
import streamlit.components.v1 as components
# Import our custom modules
from file_processor import FileProcessor
from neuro_summarizer import NeuroSummarizer
from tts_engine import NeuroTTSEngine
from flashcard_generator import FlashcardGenerator
from focus_tracker import FocusTracker
from ai_coach import EnhancedAICoach
from visual_feedback_manager import VisualFeedbackManager
from quiz_system import EnhancedGamifiedQuizSystem
from session_manager import SessionManager
from voice_to_voice_coach import VoiceToVoiceCoach, LiveKitVoiceCoach
from config import *

# === STREAMLIT PAGE CONFIG ===
st.set_page_config(
    page_title="EduVoice.AI - Neuro-Friendly Learning",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS ===
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .mood-selector {
        font-size: 2rem;
        text-align: center;
        padding: 0.5rem;
        margin: 0.2rem;
        border-radius: 10px;
        cursor: pointer;
    }
    .streak-display {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
import streamlit as st
import streamlit.components.v1 as components
import asyncio
import json
from voice_to_voice_coach import VoiceToVoiceCoach


def create_realtime_voice_chat():
    """Create real-time voice chat interface"""

    # JavaScript for real-time audio recording
    audio_recorder_js = """
    <div id="voice-chat-container">
        <style>
            .voice-chat {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                margin: 20px 0;
            }
            .voice-button {
                background: #ff4b4b;
                color: white;
                border: none;
                border-radius: 50%;
                width: 80px;
                height: 80px;
                font-size: 30px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .voice-button:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            .voice-button.recording {
                background: #00ff00;
                animation: pulse 1s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            .status-text {
                color: white;
                margin: 15px 0;
                font-size: 18px;
                font-weight: bold;
            }
            .transcript {
                background: rgba(255,255,255,0.9);
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                min-height: 50px;
            }
        </style>

        <div class="voice-chat">
            <div class="status-text" id="status">🎙️ Click to start speaking</div>
            <button class="voice-button" id="voiceBtn" onclick="toggleRecording()">🎤</button>
            <div class="transcript" id="transcript">Your speech will appear here...</div>
            <div id="ai-response" class="transcript" style="background: rgba(100,200,100,0.9);">AI response will appear here...</div>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let isRecording = false;
        let audioChunks = [];

        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    audioChunks = [];

                    // Convert to base64 and send to Streamlit
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        window.parent.postMessage({
                            type: 'audio_recorded',
                            audio: base64Audio
                        }, '*');
                    };
                    reader.readAsDataURL(audioBlob);
                };

                mediaRecorder.start();
                isRecording = true;
                updateUI();

            } catch (err) {
                console.error('Error accessing microphone:', err);
                document.getElementById('status').innerText = '❌ Microphone access denied';
            }
        }

        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                updateUI();
            }
        }

        function toggleRecording() {
            if (isRecording) {
                stopRecording();
            } else {
                startRecording();
            }
        }

        function updateUI() {
            const btn = document.getElementById('voiceBtn');
            const status = document.getElementById('status');

            if (isRecording) {
                btn.classList.add('recording');
                btn.innerHTML = '⏹️';
                status.innerText = '🔴 Recording... Click to stop';
            } else {
                btn.classList.remove('recording');
                btn.innerHTML = '🎤';
                status.innerText = '🎙️ Click to start speaking';
            }
        }

        // Listen for responses from Streamlit
        window.addEventListener('message', (event) => {
            if (event.data.type === 'ai_response') {
                document.getElementById('ai-response').innerText = event.data.response;
            }
            if (event.data.type === 'transcript') {
                document.getElementById('transcript').innerText = event.data.text;
            }
        });

        // Auto-start when page loads (optional)
        document.addEventListener('DOMContentLoaded', () => {
            console.log('Voice chat interface loaded');
        });
    </script>
    """

    return components.html(audio_recorder_js, height=400)


def handle_realtime_audio(audio_data, voice_coach):
    """Handle real-time audio processing"""
    try:
        # Process audio with voice coach
        result = voice_coach.process_audio_input(audio_data)

        if result["status"] == "success":
            return {
                "transcript": result["user_text"],
                "ai_response": result["ai_response"],
                "audio_response": result.get("audio_response")
            }
        else:
            return {"error": result["message"]}

    except Exception as e:
        return {"error": str(e)}


# === INITIALIZATION ===
@st.cache_resource
def initialize_components():
    """Initialize all learning components"""
    return {
        'file_processor': FileProcessor(),
        'summarizer': NeuroSummarizer(),
        'tts_engine': NeuroTTSEngine(),
        'flashcard_gen': FlashcardGenerator(),
    }


# Initialize components
components = initialize_components()

# Initialize session-specific components
if 'user_id' not in st.session_state:
    st.session_state.user_id = DEFAULT_USER_ID

user_id = st.session_state.user_id
focus_tracker = FocusTracker(user_id)
ai_coach = EnhancedAICoach(user_id)
quiz_system = EnhancedGamifiedQuizSystem(user_id)
visual_feedback = VisualFeedbackManager(user_id)
session_manager = SessionManager(user_id)

# Initialize Voice-to-Voice Coach
if 'voice_coach' not in st.session_state:
    st.session_state.voice_coach = VoiceToVoiceCoach(user_id)
voice_coach = st.session_state.voice_coach

# === SIDEBAR ===
with st.sidebar:
    st.markdown("## 🧠 EduVoice.AI")
    st.markdown("*Neuro-Friendly Learning Platform*")

    # Mood Check-in
    st.markdown("### 🌈 How are you feeling?")
    mood_cols = st.columns(3)
    for i, (emoji, name) in enumerate(MOOD_OPTIONS.items()):
        col_idx = i % 3
        with mood_cols[col_idx]:
            if st.button(emoji, key=f"mood_{emoji}", help=name):
                session_manager.mood_checkin(emoji)
                st.success(f"Feeling {name} noted! 💙")

    # Enhanced Streak Display with Visual Motivation
    streak_info = quiz_system.get_streak_info()

    # Display streak motivation visual
    if streak_info.get('motivation_visual'):
        st.image(f"data:image/png;base64,{streak_info['motivation_visual']}",
                 caption="Your Learning Journey", width=250)

    st.markdown(f"""
    <div class="streak-display">
        🔥 Current Streak: {streak_info['current_streak']} days<br>
        🏆 Best Streak: {streak_info['best_streak']} days<br>
        📊 Total Quizzes: {streak_info['total_quizzes']}
    </div>
    """, unsafe_allow_html=True)

    # Achievement Summary
    achievements = visual_feedback.get_user_achievements()
    if achievements['total_badges'] > 0:
        st.markdown("### 🏆 Recent Achievements")
        for badge in achievements['recent_badges']:
            st.write(f"🏅 {badge['title']}")
        st.write(f"**Total Points:** {achievements['total_points']}")

    # Quick Stats
    analytics = session_manager.get_learning_analytics()
    st.markdown("### 📊 Quick Stats")
    st.metric("Total Sessions", analytics['total_sessions'])
    st.metric("Avg Understanding", f"{analytics['avg_understanding']:.1f}/5")
    st.metric("Time Learned", f"{analytics['total_time'] / 3600:.1f}h")

# === MAIN HEADER ===
st.markdown("""
<div class="main-header">
    <h1>🧠 EduVoice.AI - Neuro-Friendly Learning</h1>
    <p>Upload • Summarize • Learn • Practice • Grow</p>
</div>
""", unsafe_allow_html=True)

# === DAILY MOTIVATION ===
try:
    daily_motivation = visual_feedback.get_daily_motivation_visual()
    col1, col2 = st.columns([1, 2])
    with col1:
        if daily_motivation.get('image'):
            st.image(f"data:image/png;base64,{daily_motivation['image']}",
                     caption="Daily Inspiration", width=200)
    with col2:
        st.markdown(f"### 🌟 {daily_motivation.get('text', 'Ready to learn?')}")
except Exception as e:
    st.info("💡 Ready to start your learning journey today!")

st.markdown("---")

# === MAIN TABS ===
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📤 Upload & Process",
    "🧠 Smart Summaries",
    "🧩 Flashcards & Quiz",
    "🤝 AI Coach",
    "🎙️ Voice Coach",
    "📊 Analytics",
    "🎧 Audio Library"
])

# === TAB 1: UPLOAD & PROCESS ===
with tab1:
    st.header("📄 Upload Your Learning Material")

    # File upload options
    upload_type = st.radio("Choose your content type:",
                           ["📄 PDF Document", "🎥 YouTube Video", "📝 Text Input", "🎤 Voice Command"])

    content_text = ""
    content_title = ""

    if upload_type == "📄 PDF Document":
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
        if uploaded_file:
            with st.spinner("🔄 Extracting text from PDF..."):
                content_text = components['file_processor'].extract_pdf_text(uploaded_file)
                content_title = uploaded_file.name

            if content_text:
                st.success("✅ PDF processed successfully!")
                st.text_area("Extracted Content Preview:", content_text[:500] + "...", height=150)

    elif upload_type == "🎥 YouTube Video":
        youtube_url = st.text_input("🔗 Enter YouTube URL:")
        if youtube_url and st.button("🎬 Process Video"):
            with st.spinner("🎥 Extracting transcript from video..."):
                content_title, content_text = components['file_processor'].extract_youtube_transcript(youtube_url)

            if content_text:
                st.success(f"✅ Video '{content_title}' processed!")
                st.text_area("Transcript Preview:", content_text[:500] + "...", height=150)

    elif upload_type == "📝 Text Input":
        content_title = st.text_input("📝 Content Title:")
        content_text = st.text_area("✍️ Paste your text here:", height=200)

    elif upload_type == "🎤 Voice Command":
        st.info("🎤 Upload an audio file to transcribe")
        audio_file = st.file_uploader("Upload audio file", type=['wav', 'mp3', 'm4a'])
        if audio_file:
            with st.spinner("🎵 Transcribing audio..."):
                # Save audio file temporarily
                with open("temp_audio.wav", "wb") as f:
                    f.write(audio_file.read())

                # Transcribe
                model = whisper.load_model("base")
                result = model.transcribe("temp_audio.wav")
                content_text = result['text']
                content_title = "Voice Input"

                # Clean up
                os.remove("temp_audio.wav")

            if content_text:
                st.success("✅ Audio transcribed!")
                st.text_area("Transcription:", content_text, height=150)

    # Save processed content
    if content_text and content_title:
        if st.button("💾 Save Content for Learning"):
            filepath = components['file_processor'].save_content(content_text, content_title, upload_type)
            if filepath:
                st.session_state.current_content = content_text
                st.session_state.current_title = content_title
                # Add to AI Coach knowledge base
                ai_coach.add_to_knowledge_base(content_text[:1000], content_title, upload_type)
                st.success("🎉 Content saved! Move to the next tab to generate summaries.")

# === TAB 2: SMART SUMMARIES ===
with tab2:
    st.header("🧠 Neuro-Friendly Summaries")

    if 'current_content' not in st.session_state:
        st.warning("📋 Please upload and save content in the Upload tab first!")
    else:
        st.success(f"📖 Working with: {st.session_state.get('current_title', 'Your Content')}")

        # Summary generation
        if st.button("✨ Generate All Summary Modes"):
            with st.spinner("🧠 Creating neuro-friendly summaries..."):
                summaries = components['summarizer'].get_all_summaries(st.session_state.current_content)
                st.session_state.summaries = summaries

        # Display summaries if available
        if 'summaries' in st.session_state:
            summary_tab1, summary_tab2, summary_tab3 = st.tabs(["📝 Basic", "📚 Story Mode", "🎨 Visual"])

            with summary_tab1:
                st.markdown("### 📝 Basic Summary")
                st.markdown(st.session_state.summaries['basic'])

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔊 Listen to Basic Summary"):
                        audio_file = components['tts_engine'].create_summary_audio(
                            st.session_state.summaries, 'basic'
                        )
                        if audio_file:
                            st.audio(audio_file)

                with col2:
                    if st.button("📚 Start Focus Session - Basic"):
                        focus_tracker.start_focus_session("summary", "Basic Summary")
                        st.success("🎯 Focus tracking started!")

            with summary_tab2:
                st.markdown("### 📚 Story Mode Summary")
                st.markdown(st.session_state.summaries['story'])

                # Add visual enhancement for Story Mode
                try:
                    story_visual = visual_feedback.create_meme_image(
                        "concept_mastery",
                        "📖 Learning through stories!",
                        "curious"
                    )
                    st.image(f"data:image/png;base64,{story_visual}",
                             caption="Story-based Learning", width=300)
                except Exception as e:
                    st.info("📚 Story mode visualization loading...")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔊 Listen to Story Summary"):
                        audio_file = components['tts_engine'].create_summary_audio(
                            st.session_state.summaries, 'story'
                        )
                        if audio_file:
                            st.audio(audio_file)

                with col2:
                    if st.button("📚 Start Focus Session - Story"):
                        focus_tracker.start_focus_session("summary", "Story Summary")
                        st.success("🎯 Focus tracking started!")

            with summary_tab3:
                st.markdown("### 🎨 Visual Summary")
                st.markdown(st.session_state.summaries['visual'])

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔊 Listen to Visual Summary"):
                        audio_file = components['tts_engine'].create_summary_audio(
                            st.session_state.summaries, 'visual'
                        )
                        if audio_file:
                            st.audio(audio_file)

                with col2:
                    if st.button("📚 Start Focus Session - Visual"):
                        focus_tracker.start_focus_session("summary", "Visual Summary")
                        st.success("🎯 Focus tracking started!")

# === TAB 3: FLASHCARDS & QUIZ ===
with tab3:
    st.header("🧩 Adaptive Learning & Quizzes")

    if 'current_content' not in st.session_state:
        st.warning("📋 Please upload content first!")
    else:
        # Flashcards Section
        st.subheader("🧩 Smart Flashcards")

        difficulty = st.selectbox("Choose difficulty:", ["Easy", "Medium", "Hard"])

        if st.button("🎯 Generate Flashcards"):
            with st.spinner("🧩 Creating adaptive flashcards..."):
                flashcards = components['flashcard_gen'].generate_flashcards(
                    st.session_state.current_content, difficulty
                )
                st.session_state.flashcards = flashcards

        # Display flashcards
        if 'flashcards' in st.session_state and st.session_state.flashcards:
            st.success(f"📚 Generated {len(st.session_state.flashcards)} flashcards!")

            # Flashcard practice
            if 'current_flashcard_idx' not in st.session_state:
                st.session_state.current_flashcard_idx = 0

            if st.session_state.current_flashcard_idx < len(st.session_state.flashcards):
                current_card = st.session_state.flashcards[st.session_state.current_flashcard_idx]

                st.markdown(
                    f"**Card {st.session_state.current_flashcard_idx + 1} of {len(st.session_state.flashcards)}**")
                st.markdown(f"### ❓ {current_card['question']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔍 Show Answer"):
                        st.session_state.show_answer = True

                with col2:
                    if st.button("➡️ Next Card"):
                        st.session_state.current_flashcard_idx += 1
                        st.session_state.show_answer = False
                        st.rerun()

                if st.session_state.get('show_answer', False):
                    st.success(f"✅ **Answer:** {current_card['answer']}")

                    # Performance tracking
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("😊 I knew it!"):
                            components['flashcard_gen'].save_flashcard_performance(
                                user_id, current_card, True, 3.0
                            )
                            st.success("Great job! 🎉")

                    with col2:
                        if st.button("🤔 Need to review"):
                            components['flashcard_gen'].save_flashcard_performance(
                                user_id, current_card, False, 8.0
                            )
                            st.info("No worries, practice makes perfect! 💪")

        st.markdown("---")

        # Quiz Section
        st.subheader("🎮 Gamified Quiz")

        if st.button("🚀 Start Quiz"):
            with st.spinner("🎯 Generating quiz questions..."):
                questions = quiz_system.generate_quiz_questions(
                    st.session_state.current_content, difficulty
                )
                if questions:
                    session_id = quiz_system.create_quiz_session(
                        questions, st.session_state.current_title
                    )
                    st.session_state.current_quiz_session = session_id
                    st.session_state.quiz_start_time = time.time()
                    st.rerun()

        # Display quiz
        if 'current_quiz_session' in st.session_state:
            quiz_session = quiz_system.get_quiz_session(st.session_state.current_quiz_session)

            if quiz_session and not quiz_session.get('completed', False):
                current_q_idx = quiz_session['current_question']
                if current_q_idx < len(quiz_session['questions']):
                    question = quiz_session['questions'][current_q_idx]

                    st.markdown(f"**Question {current_q_idx + 1} of {len(quiz_session['questions'])}**")
                    st.markdown(f"### {question['question']}")

                    # Multiple choice options
                    selected_answer = st.radio(
                        "Choose your answer:",
                        range(len(question['options'])),
                        format_func=lambda x: f"{chr(65 + x)}. {question['options'][x]}",
                        key=f"quiz_q_{current_q_idx}"
                    )

                    if st.button("✅ Submit Answer"):
                        response_time = time.time() - st.session_state.quiz_start_time
                        result = quiz_system.submit_answer(
                            st.session_state.current_quiz_session, selected_answer, response_time
                        )

                        # Enhanced Visual Feedback
                        visual_feedback_data = result.get('visual_feedback', {})

                        if visual_feedback_data.get('image'):
                            # Display visual feedback image
                            st.image(f"data:image/png;base64,{visual_feedback_data['image']}",
                                     caption=visual_feedback_data.get('message', ''), width=300)

                        if result.get('correct'):
                            st.success(f"✅ **Explanation:** {result['explanation']}")
                        else:
                            st.info(f"💡 **Explanation:** {result['explanation']}")

                        # Show badge if earned
                        if visual_feedback_data.get('badge'):
                            badge = visual_feedback_data['badge']
                            st.success(f"🏆 **New Achievement:** {badge['title']}")
                            if badge.get('image'):
                                st.image(f"data:image/png;base64,{badge['image']}", width=200)
                            st.write(f"*{badge['description']}* (+{badge['points']} points)")

                        st.info(f"📊 Score: {result['score']}/{result['total_questions']}")

                        if result.get('completed'):
                            st.balloons()
                            st.success("🎉 Quiz completed!")

                            # Show completion feedback
                            completion_feedback = result.get('completion_feedback', {})
                            if completion_feedback.get('image'):
                                st.image(f"data:image/png;base64,{completion_feedback['image']}",
                                         caption="Quiz Complete!", width=400)

                            reward_msg = quiz_system.generate_reward_message(
                                quiz_system.get_streak_info()
                            )
                            st.markdown(f"### {reward_msg}")

                            # Show streak feedback if available
                            if 'streak_feedback' in st.session_state:
                                streak_fb = st.session_state['streak_feedback']
                                if streak_fb.get('image'):
                                    st.image(f"data:image/png;base64,{streak_fb['image']}",
                                             caption="Streak Achievement!", width=300)

                        st.session_state.quiz_start_time = time.time()
                        time.sleep(2)
                        st.rerun()

# === TAB 4: AI COACH ===
with tab4:
    st.header("🤝 Your Personal AI Learning Coach")

    # Motivational message
    motivation = ai_coach.generate_motivational_message()
    st.info(motivation)

    # Learning suggestions
    suggestions = ai_coach.get_personalized_suggestions()
    st.markdown("### 💡 Personalized Suggestions")
    for suggestion in suggestions:
        st.markdown(f"• {suggestion}")

    # Enhanced Learning Insights
    st.markdown("### 🧠 Your Learning Profile")
    learning_insights = ai_coach.get_learning_insights()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🎯 Learning Patterns**")
        personality = learning_insights["personality_analysis"]
        st.metric("Confidence Level", f"{personality['confidence_level']:.1%}")
        st.metric("Curiosity Level", f"{personality['curiosity_level']:.1%}")

        progress = learning_insights["progress_summary"]
        st.metric("Concepts Mastered", progress["concepts_mastered"])
        st.metric("Knowledge Base Size", progress["knowledge_base_size"])

    with col2:
        st.markdown("**🎲 Question Patterns**")
        question_patterns = learning_insights["learning_patterns"]["question_types"]
        if question_patterns:
            for q_type, count in sorted(question_patterns.items(), key=lambda x: x[1], reverse=True)[:3]:
                st.write(f"• {q_type.replace('_', ' ').title()}: {count} times")
        else:
            st.write("Start asking questions to see patterns!")

        difficulty = learning_insights["progress_summary"]["adaptive_difficulty"]
        st.metric("Adaptive Difficulty", f"{difficulty:.1%}")

    st.markdown("---")

    st.markdown("### 💬 Ask Your Coach")

    # Display conversation history
    if 'coach_messages' not in st.session_state:
        st.session_state.coach_messages = []

    # Chat display
    for message in st.session_state.coach_messages[-5:]:  # Show last 5 exchanges
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about your learning..."):
        # Add user message
        st.session_state.coach_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Coach is thinking..."):
                current_topic = st.session_state.get('current_title', '')
                response = ai_coach.generate_personalized_response(prompt, current_topic)
                st.markdown(response)

                # Add to message history
                st.session_state.coach_messages.append({"role": "assistant", "content": response})

with tab5:
    st.header("🎙️ Real-Time Voice AI Coach")
    st.markdown("*Speak directly with your AI coach - No file uploads needed!*")

    # Voice Coach Status
    voice_status = voice_coach.get_session_status()

    col1, col2, col3 = st.columns(3)
    with col1:
        if voice_status["active"]:
            st.success("🎙️ Voice Session Active")
        else:
            st.info("🔇 Voice Session Inactive")

    with col2:
        if st.button("🎙️ Start Voice Session", type="primary", disabled=voice_status["active"]):
            result = voice_coach.start_voice_session()
            if result["status"] == "success":
                st.success("Voice session started! You can now speak.")
                st.rerun()

    with col3:
        if st.button("🔇 Stop Voice Session", disabled=not voice_status["active"]):
            result = voice_coach.stop_voice_session()
            if result["status"] == "success":
                st.success("Voice session ended.")
                st.rerun()

    if voice_status["active"]:
        st.markdown("---")

        # Real-time voice chat interface
        st.markdown("### 🗣️ Speak with Your AI Coach")
        st.markdown("**Click the microphone button below and start speaking!**")

        # Custom real-time voice component
        audio_component = st.empty()

        with audio_component.container():
            # JavaScript-based real-time voice recorder
            components.html("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px;">
                <div id="status" style="color: white; margin: 15px 0; font-size: 18px;">🎙️ Click to start speaking</div>
                <button id="voiceBtn" onclick="toggleRecording()" style="
                    background: #ff4b4b; color: white; border: none; border-radius: 50%; 
                    width: 80px; height: 80px; font-size: 30px; cursor: pointer;
                    transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                ">🎤</button>
                <div id="transcript" style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 15px 0; min-height: 50px;">
                    Your speech will appear here...
                </div>
                <div id="ai-response" style="background: rgba(100,200,100,0.9); padding: 15px; border-radius: 10px; margin: 15px 0; min-height: 50px;">
                    AI response will appear here...
                </div>
            </div>

            <script>
                let mediaRecorder;
                let isRecording = false;
                let audioChunks = [];

                async function startRecording() {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);

                        mediaRecorder.ondataavailable = (event) => {
                            audioChunks.push(event.data);
                        };

                        mediaRecorder.onstop = async () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            audioChunks = [];

                            // Send audio to Streamlit backend
                            const formData = new FormData();
                            formData.append('audio', audioBlob);

                            try {
                                document.getElementById('transcript').innerText = '🔄 Processing your speech...';

                                // Here you would send to your Streamlit backend
                                // For now, simulate processing
                                setTimeout(() => {
                                    document.getElementById('transcript').innerText = '✅ Speech processed successfully!';
                                    document.getElementById('ai-response').innerText = '🤖 AI Coach: Great question! Let me help you with that...';
                                }, 2000);

                            } catch (error) {
                                document.getElementById('transcript').innerText = '❌ Error processing speech';
                            }
                        };

                        mediaRecorder.start();
                        isRecording = true;
                        updateUI();

                    } catch (err) {
                        document.getElementById('status').innerText = '❌ Microphone access denied. Please allow microphone access.';
                    }
                }

                function stopRecording() {
                    if (mediaRecorder && isRecording) {
                        mediaRecorder.stop();
                        mediaRecorder.stream.getTracks().forEach(track => track.stop());
                        isRecording = false;
                        updateUI();
                    }
                }

                function toggleRecording() {
                    if (isRecording) {
                        stopRecording();
                    } else {
                        startRecording();
                    }
                }

                function updateUI() {
                    const btn = document.getElementById('voiceBtn');
                    const status = document.getElementById('status');

                    if (isRecording) {
                        btn.style.background = '#00ff00';
                        btn.style.animation = 'pulse 1s infinite';
                        btn.innerHTML = '⏹️';
                        status.innerText = '🔴 Recording... Click to stop and send';
                    } else {
                        btn.style.background = '#ff4b4b';
                        btn.style.animation = 'none';
                        btn.innerHTML = '🎤';
                        status.innerText = '🎙️ Click to start speaking';
                    }
                }
            </script>

            <style>
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
            </style>
            """, height=400)

        # Instructions
        st.markdown("### 💡 How to Use:")
        st.markdown("""
        1. **🎤 Click the microphone button** to start recording
        2. **🗣️ Speak your question or topic** clearly
        3. **⏹️ Click again to stop** and send your voice to the AI coach
        4. **🤖 Listen to the AI response** and continue the conversation!

        **💬 Example questions to try:**
        - "Explain photosynthesis in simple terms"
        - "Help me understand calculus derivatives"
        - "What are good study techniques?"
        - "I'm struggling with physics, can you help?"
        """)

        # Show conversation history
        conversation_history = voice_coach.get_conversation_history(3)
        if conversation_history:
            st.markdown("### 📜 Recent Conversation")
            for exchange in reversed(conversation_history):
                with st.expander(f"💬 {exchange['timestamp'][:16]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**🗣️ You:**")
                        st.write(exchange["user_text"])
                    with col2:
                        st.markdown("**🤖 Coach:**")
                        st.write(exchange["ai_response"])
    else:
        st.info("👆 Click 'Start Voice Session' to begin real-time voice chat with your AI coach!")

        st.markdown("### 🌟 Real-Time Voice Features:")
        st.markdown("""
        - **🎤 One-Click Recording**: Just click and speak
        - **🔄 Instant Processing**: Get immediate AI responses
        - **🗣️ Natural Conversation**: No file uploads needed
        - **🎧 Audio Responses**: Hear the AI coach speak back
        - **📱 Hands-Free**: Perfect for learning on the go
        - **🧠 Context Aware**: AI remembers your conversation
        """)

# === TAB 6: ANALYTICS ===
with tab6:
    st.header("📊 Learning Analytics & Insights")

    # Time period selector
    time_period = st.selectbox("📅 View data for:", ["Last 7 days", "Last 30 days", "All time"])
    days = {"Last 7 days": 7, "Last 30 days": 30, "All time": 365}[time_period]

    # Get focus analytics
    focus_analytics = focus_tracker.get_focus_analytics(days)

    # Handle zero-session case
    total_sessions = focus_analytics.get("total_sessions", 0)
    avg_focus_time = focus_analytics.get("avg_focus_time", 0)
    completion_rate = focus_analytics.get("completion_rate", 0)
    avg_response_time = focus_analytics.get("avg_response_time", 0)
    accuracy = focus_analytics.get("accuracy", 0)
    break_info = focus_analytics.get("break_frequency", {})

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎯 Total Sessions", total_sessions)
        st.metric("⏱️ Avg Focus Time", f"{avg_focus_time:.1f}s")

    with col2:
        st.metric("✅ Completion Rate", f"{completion_rate:.1%}")
        st.metric("⚡ Avg Response Time", f"{avg_response_time:.1f}s")

    with col3:
        st.metric("🎯 Accuracy", f"{accuracy:.1%}")
        st.metric("📈 Breaks/Session", f"{break_info.get('avg_breaks_per_session', 0):.1f}")

    # Optional: Show most common break type
    if break_info.get("most_common_break_type") and break_info["most_common_break_type"] != "none":
        st.info(f"🛑 Most Frequent Break Type: **{break_info['most_common_break_type'].capitalize()}**")

    # Focus pattern visualization (if available)
    if focus_analytics.get("focus_patterns"):
        fig = focus_tracker.create_focus_visualization(focus_analytics)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Mood analytics
    mood_history = session_manager.get_mood_history(days)
    if mood_history:
        st.subheader("🌈 Mood Trends")
        mood_df = pd.DataFrame(mood_history)
        mood_counts = mood_df['mood_name'].value_counts()

        fig_mood = go.Figure(data=[go.Pie(labels=mood_counts.index, values=mood_counts.values)])
        fig_mood.update_layout(title="Mood Distribution")
        st.plotly_chart(fig_mood, use_container_width=True)

    # Enhanced Performance Analytics with Visual Progress
    perf_analytics = quiz_system.get_performance_analytics()
    if perf_analytics['total_quizzes'] > 0:
        st.subheader("📈 Quiz Performance & Progress")

        # Display progress visualization
        if perf_analytics.get('progress_visual'):
            st.image(f"data:image/png;base64,{perf_analytics['progress_visual']}",
                     caption="Your Learning Progress", use_column_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("📊 Average Accuracy", f"{perf_analytics['avg_accuracy']:.1%}")
            st.metric("⏱️ Average Response Time", f"{perf_analytics['avg_response_time']:.1f}s")

        with col2:
            st.metric("📈 Improvement Trend", perf_analytics['improvement_trend'])
            st.metric("🎯 Total Quizzes", perf_analytics['total_quizzes'])

        # Achievement showcase
        st.subheader("🏆 Your Achievements")
        achievements = visual_feedback.get_user_achievements()
        if achievements['total_badges'] > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏅 Total Badges", achievements['total_badges'])
            with col2:
                st.metric("⭐ Total Points", achievements['total_points'])
            with col3:
                st.metric("🎯 Recent Badges", len(achievements['recent_badges']))

            # Show recent badges
            if achievements['recent_badges']:
                st.markdown("**Latest Achievements:**")
                for badge in achievements['recent_badges']:
                    st.write(f"🏅 **{badge['title']}** - {badge['description']} (+{badge['points']} pts)")
        else:
            st.info("🎯 Complete quizzes and maintain streaks to earn achievement badges!")

# === TAB 7: AUDIO LIBRARY ===
with tab7:
    st.header("🎧 Your Personal Audio Library")

    # List saved audio files
    audio_dir = "audio"
    if os.path.exists(audio_dir):
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]

        if audio_files:
            st.success(f"🎵 Found {len(audio_files)} audio files")

            for audio_file in audio_files:
                audio_path = os.path.join(audio_dir, audio_file)
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.audio(audio_path)
                    st.caption(audio_file)

                with col2:
                    if st.button(f"🗑️ Delete", key=f"del_{audio_file}"):
                        os.remove(audio_path)
                        st.success("Audio deleted!")
                        st.rerun()
        else:
            st.info("🎵 No audio files yet. Generate summaries with audio to build your library!")

    # Text-to-speech generator
    st.subheader("🎙️ Create Custom Audio")
    custom_text = st.text_area("Enter text to convert to speech:", height=100)

    if custom_text and st.button("🎵 Generate Audio"):
        with st.spinner("🎙️ Creating audio..."):
            audio_file = components['tts_engine'].create_audio_file(custom_text)
            if audio_file:
                st.success("✅ Audio created!")
                st.audio(audio_file)

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🧠 <strong>EduVoice.AI</strong> - Empowering neuro-friendly learning for everyone</p>
    <p>Made with ❤️ for better learning experiences</p>
</div>
""", unsafe_allow_html=True)

# === KEYBOARD SHORTCUTS INFO ===
with st.expander("⌨️ Keyboard Shortcuts & Tips"):
    st.markdown("""
    **Tips for Neuro-Friendly Learning:**
    - 🎯 Use 15-20 minute focused sessions
    - 🧠 Try different summary modes for different learning styles
    - 🔄 Take regular breaks when you feel overwhelmed
    - 📊 Check your analytics to find your optimal learning times
    - 🤝 Don't hesitate to ask the AI Coach for help!

    **Best Practices:**
    - 📝 Start with Basic summaries, then try Story or Visual modes
    - 🧩 Use flashcards for active recall
    - 🎮 Take quizzes to test understanding
    - 🎧 Listen to audio summaries during commutes or breaks
    """)
import openai
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import streamlit as st
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from config import AZURE_OPENAI_API_KEY, ENDPOINT_URL, DEPLOYMENT_NAME

class EnhancedAICoach:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client = openai.AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-02-01",
            azure_endpoint=ENDPOINT_URL
        )
        self.model = DEPLOYMENT_NAME

        # File paths for enhanced features
        self.conversation_file = f"user_data/{user_id}_coach_conversations.json"
        self.user_profile_file = f"user_data/{user_id}_enhanced_profile.json"
        self.knowledge_base_file = f"user_data/{user_id}_knowledge_base.pkl"
        self.learning_path_file = f"user_data/{user_id}_learning_path.json"

        # Initialize Sentence Transformer model
        self._init_sentence_transformer()

        # Load user data
        self.load_user_profile()
        self.load_knowledge_base()
        self.load_learning_path()

    def _init_sentence_transformer(self):
        """Initialize sentence transformer model for semantic understanding"""
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            st.success("🧠 AI Coach enhanced with semantic understanding!")
        except Exception as e:
            st.warning(f"Using basic AI Coach (Sentence Transformers not available): {e}")
            self.sentence_model = None

    def load_user_profile(self):
        """Load enhanced user learning profile"""
        if os.path.exists(self.user_profile_file):
            with open(self.user_profile_file, 'r') as f:
                self.user_profile = json.load(f)
        else:
            self.user_profile = {
                "learning_style": "mixed",
                "difficulty_preference": "medium",
                "topics_struggled": [],
                "topics_mastered": [],
                "preferred_explanation_style": "analogies",
                "language_preference": "English",
                "learning_goals": [],
                "personality_traits": {
                    "confidence_level": 0.5,
                    "curiosity_level": 0.7,
                    "patience_level": 0.6,
                    "preferred_feedback_style": "encouraging"
                },
                "interaction_patterns": {
                    "question_types": {},
                    "common_struggles": [],
                    "breakthrough_moments": [],
                    "optimal_study_times": []
                }
            }

    def save_user_profile(self):
        """Save updated user profile"""
        with open(self.user_profile_file, 'w') as f:
            json.dump(self.user_profile, f, indent=2)

    def load_knowledge_base(self):
        """Load semantic knowledge base using FAISS"""
        if os.path.exists(self.knowledge_base_file):
            with open(self.knowledge_base_file, 'rb') as f:
                kb_data = pickle.load(f)
                self.knowledge_embeddings = kb_data.get('embeddings', [])
                self.knowledge_texts = kb_data.get('texts', [])
                self.knowledge_metadata = kb_data.get('metadata', [])

                # Rebuild FAISS index
                if len(self.knowledge_embeddings) > 0:
                    self.faiss_index = faiss.IndexFlatIP(len(self.knowledge_embeddings[0]))
                    self.faiss_index.add(np.array(self.knowledge_embeddings))
                else:
                    self.faiss_index = None
        else:
            self.knowledge_embeddings = []
            self.knowledge_texts = []
            self.knowledge_metadata = []
            self.faiss_index = None

    def save_knowledge_base(self):
        """Save semantic knowledge base"""
        kb_data = {
            'embeddings': self.knowledge_embeddings,
            'texts': self.knowledge_texts,
            'metadata': self.knowledge_metadata
        }
        with open(self.knowledge_base_file, 'wb') as f:
            pickle.dump(kb_data, f)

    def load_learning_path(self):
        """Load personalized learning path"""
        if os.path.exists(self.learning_path_file):
            with open(self.learning_path_file, 'r') as f:
                self.learning_path = json.load(f)
        else:
            self.learning_path = {
                "current_level": "beginner",
                "completed_concepts": [],
                "struggling_concepts": [],
                "recommended_next": [],
                "learning_milestones": [],
                "adaptive_difficulty": 0.5
            }

    def save_learning_path(self):
        """Save learning path"""
        with open(self.learning_path_file, 'w') as f:
            json.dump(self.learning_path, f, indent=2)

    def add_to_knowledge_base(self, text: str, topic: str, content_type: str):
        """Add new content to semantic knowledge base"""
        if not self.sentence_model:
            return

        try:
            # Generate embedding
            embedding = self.sentence_model.encode([text])[0]

            # Add to knowledge base
            self.knowledge_embeddings.append(embedding.tolist())
            self.knowledge_texts.append(text)
            self.knowledge_metadata.append({
                "topic": topic,
                "content_type": content_type,
                "timestamp": datetime.now().isoformat(),
                "user_interaction": 0  # Track how often this is referenced
            })

            # Rebuild FAISS index
            if self.faiss_index is None:
                self.faiss_index = faiss.IndexFlatIP(len(embedding))

            self.faiss_index = faiss.IndexFlatIP(len(embedding))
            self.faiss_index.add(np.array(self.knowledge_embeddings))

            # Save updated knowledge base
            self.save_knowledge_base()

        except Exception as e:
            st.warning(f"Could not add to knowledge base: {e}")

    def find_relevant_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find semantically relevant context from knowledge base"""
        if not self.sentence_model or self.faiss_index is None or len(self.knowledge_texts) == 0:
            return []

        try:
            # Encode query
            query_embedding = self.sentence_model.encode([query])

            # Search for similar content
            scores, indices = self.faiss_index.search(query_embedding, min(top_k, len(self.knowledge_texts)))

            relevant_contexts = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.knowledge_texts) and score > 0.3:  # Similarity threshold
                    relevant_contexts.append({
                        "text": self.knowledge_texts[idx],
                        "metadata": self.knowledge_metadata[idx],
                        "similarity": float(score)
                    })

                    # Update interaction count
                    self.knowledge_metadata[idx]["user_interaction"] += 1

            return relevant_contexts

        except Exception as e:
            st.warning(f"Context search failed: {e}")
            return []

    def analyze_question_semantics(self, question: str) -> Dict:
        """Analyze question semantics and intent"""
        if not self.sentence_model:
            return self._basic_question_analysis(question)

        # Question type patterns
        question_patterns = {
            "definition": ["what is", "define", "meaning of", "what does", "explain"],
            "how_to": ["how to", "how do", "how can", "steps to", "process"],
            "why": ["why", "reason", "because", "cause", "purpose"],
            "comparison": ["difference", "compare", "versus", "vs", "better than"],
            "example": ["example", "instance", "demonstrate", "show me"],
            "clarification": ["confused", "don't understand", "unclear", "help"]
        }

        question_lower = question.lower()
        detected_types = []

        for q_type, patterns in question_patterns.items():
            if any(pattern in question_lower for pattern in patterns):
                detected_types.append(q_type)

        # Emotional tone detection
        emotional_indicators = {
            "frustrated": ["frustrated", "confused", "stuck", "difficult", "hard", "don't get"],
            "curious": ["interesting", "wonder", "curious", "what if", "tell me more"],
            "confident": ["understand", "got it", "clear", "makes sense", "easy"],
            "urgent": ["quick", "fast", "immediately", "asap", "urgent"]
        }

        emotional_tone = "neutral"
        for emotion, indicators in emotional_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                emotional_tone = emotion
                break

        return {
            "question_types": detected_types if detected_types else ["general"],
            "emotional_tone": emotional_tone,
            "complexity_level": self._assess_question_complexity(question),
            "key_concepts": self._extract_key_concepts(question)
        }

    def _basic_question_analysis(self, question: str) -> Dict:
        """Basic question analysis when sentence transformers unavailable"""
        question_lower = question.lower()

        if any(word in question_lower for word in ["what", "define", "meaning"]):
            q_type = "definition"
        elif any(word in question_lower for word in ["how", "steps", "process"]):
            q_type = "how_to"
        elif "why" in question_lower:
            q_type = "why"
        else:
            q_type = "general"

        emotion = "neutral"
        if any(word in question_lower for word in ["frustrated", "confused", "stuck"]):
            emotion = "frustrated"
        elif any(word in question_lower for word in ["interesting", "curious"]):
            emotion = "curious"

        return {
            "question_types": [q_type],
            "emotional_tone": emotion,
            "complexity_level": "medium",
            "key_concepts": []
        }

    def _assess_question_complexity(self, question: str) -> str:
        """Assess complexity of the question"""
        complexity_indicators = {
            "high": ["analyze", "synthesize", "evaluate", "compare", "contrast", "justify"],
            "medium": ["explain", "describe", "discuss", "relate", "apply"],
            "low": ["what", "who", "when", "where", "list", "name"]
        }

        question_lower = question.lower()

        for level, indicators in complexity_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                return level

        return "medium"

    def _extract_key_concepts(self, question: str) -> List[str]:
        """Extract key concepts from question (basic implementation)"""
        # Simple concept extraction - can be enhanced with NER
        common_subjects = [
            "math", "mathematics", "algebra", "geometry", "calculus",
            "science", "physics", "chemistry", "biology",
            "history", "literature", "english", "grammar",
            "programming", "coding", "computer", "technology"
        ]

        question_lower = question.lower()
        found_concepts = [concept for concept in common_subjects if concept in question_lower]

        return found_concepts

    def generate_personalized_response(self, user_message: str, current_topic: str = "") -> str:
        """Generate personalized response using semantic understanding"""
        if not AZURE_OPENAI_API_KEY:
            return "🤖 AI Coach not available - please configure Azure OpenAI credentials"

        # Analyze question semantics
        question_analysis = self.analyze_question_semantics(user_message)

        # Find relevant context from knowledge base
        relevant_contexts = self.find_relevant_context(user_message)

        # Update interaction patterns
        self._update_interaction_patterns(user_message, question_analysis)

        # Build enhanced system prompt
        system_prompt = self._build_enhanced_system_prompt(
            question_analysis, current_topic, relevant_contexts
        )

        # Prepare conversation context
        messages = [{"role": "system", "content": system_prompt}]

        # Add relevant context as system information
        if relevant_contexts:
            context_info = "Relevant context from user's learning history:\
"
            for ctx in relevant_contexts[:2]:  # Top 2 most relevant
                context_info += f"- {ctx['text'][:200]}...\
"
            messages.append({"role": "system", "content": context_info})

        # Add recent conversation history
        recent_conversations = self._get_recent_conversations(3)
        for conv in recent_conversations:
            messages.extend([
                {"role": "user", "content": conv["user_message"]},
                {"role": "assistant", "content": conv["coach_response"]}
            ])

        # Add current message
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=600
            )
            coach_response = response.choices[0].message.content.strip()

            # Save conversation with analysis
            self._save_enhanced_conversation(user_message, coach_response, question_analysis)

            # Update learning path based on interaction
            self._update_learning_path(user_message, question_analysis, current_topic)

            return coach_response

        except Exception as e:
            return f"🤖 Sorry, I'm having trouble right now. Error: {str(e)}"

    def _build_enhanced_system_prompt(self, analysis: Dict, current_topic: str, contexts: List[Dict]) -> str:
        """Build enhanced system prompt based on semantic analysis"""
        base_prompt = """You are an advanced AI learning coach with deep understanding of pedagogy and personalized learning. Your capabilities include:

- Semantic understanding of student questions and learning patterns
- Adaptive teaching based on individual learning styles and history
- Emotional intelligence to respond appropriately to student mood
- Contextual awareness from previous interactions and learned content

Your personality traits:
- Empathetic and encouraging, celebrating progress
- Intellectually curious, asking thought-provoking questions  
- Patient and supportive, especially when students struggle
- Adaptive communication style based on student needs
- Uses analogies, stories, and real-world examples effectively
"""

        # Add analysis-based adaptations
        question_types = analysis.get("question_types", [])
        emotional_tone = analysis.get("emotional_tone", "neutral")
        complexity = analysis.get("complexity_level", "medium")

        # Question type specific guidance
        if "definition" in question_types:
            base_prompt += "\
\
The student is asking for definitions. Provide clear, concise explanations with examples and analogies."
        elif "how_to" in question_types:
            base_prompt += "\
\
The student wants step-by-step guidance. Break down the process into manageable steps with clear instructions."
        elif "why" in question_types:
            base_prompt += "\
\
The student wants deeper understanding. Explain underlying principles, causes, and connections."
        elif "comparison" in question_types:
            base_prompt += "\
\
The student wants comparisons. Provide clear distinctions, similarities, and when to use each option."

        # Emotional adaptation
        emotion_adaptations = {
            "frustrated": "\
\
The student seems frustrated. Be extra patient, acknowledge their feeling, break things down simply, and offer encouragement.",
            "curious": "\
\
The student is curious and engaged. Feed their curiosity with interesting details, related concepts, and thought-provoking questions.",
            "confident": "\
\
The student seems confident. Challenge them with slightly advanced concepts and encourage deeper exploration.",
            "urgent": "\
\
The student needs quick help. Provide concise, direct answers while ensuring understanding."
        }

        if emotional_tone in emotion_adaptations:
            base_prompt += emotion_adaptations[emotional_tone]

        # Complexity adaptation
        if complexity == "high":
            base_prompt += "\
\
This is a complex question. Use advanced explanations, multiple perspectives, and encourage critical thinking."
        elif complexity == "low":
            base_prompt += "\
\
This is a basic question. Use simple language, concrete examples, and build foundational understanding."

        # User profile context
        profile_context = f"""

Student Profile:
- Learning style: {self.user_profile.get('learning_style', 'mixed')}
- Preferred difficulty: {self.user_profile.get('difficulty_preference', 'medium')}
- Explanation style preference: {self.user_profile.get('preferred_explanation_style', 'analogies')}
- Current confidence level: {self.user_profile['personality_traits']['confidence_level']:.1f}/1.0
- Topics struggling with: {', '.join(self.user_profile.get('topics_struggled', []))}
- Topics mastered: {', '.join(self.user_profile.get('topics_mastered', []))}
"""

        # Current topic context
        if current_topic:
            base_prompt += f"\
\
Current learning topic: {current_topic}"

        return base_prompt + profile_context

    def _update_interaction_patterns(self, message: str, analysis: Dict):
        """Update user interaction patterns for better personalization"""
        # Update question type frequency
        question_types = analysis.get("question_types", [])
        for q_type in question_types:
            current_count = self.user_profile["interaction_patterns"]["question_types"].get(q_type, 0)
            self.user_profile["interaction_patterns"]["question_types"][q_type] = current_count + 1

        # Track emotional patterns
        emotional_tone = analysis.get("emotional_tone", "neutral")
        if emotional_tone == "frustrated":
            struggle_text = message[:100]  # First 100 chars as struggle indicator
            if struggle_text not in self.user_profile["interaction_patterns"]["common_struggles"]:
                self.user_profile["interaction_patterns"]["common_struggles"].append(struggle_text)

        # Update personality traits based on interactions
        if emotional_tone == "curious":
            self.user_profile["personality_traits"]["curiosity_level"] = min(1.0,
                                                                             self.user_profile["personality_traits"][
                                                                                 "curiosity_level"] + 0.05)
        elif emotional_tone == "confident":
            self.user_profile["personality_traits"]["confidence_level"] = min(1.0,
                                                                              self.user_profile["personality_traits"][
                                                                                  "confidence_level"] + 0.05)
        elif emotional_tone == "frustrated":
            self.user_profile["personality_traits"]["confidence_level"] = max(0.0,
                                                                              self.user_profile["personality_traits"][
                                                                                  "confidence_level"] - 0.03)

        # Save updated profile
        self.save_user_profile()

    def _update_learning_path(self, message: str, analysis: Dict, current_topic: str):
        """Update personalized learning path based on interaction"""
        key_concepts = analysis.get("key_concepts", [])
        emotional_tone = analysis.get("emotional_tone", "neutral")

        # Track concept struggles and mastery
        for concept in key_concepts:
            if emotional_tone in ["frustrated", "confused"]:
                if concept not in self.learning_path["struggling_concepts"]:
                    self.learning_path["struggling_concepts"].append(concept)
            elif emotional_tone in ["confident", "curious"]:
                if concept not in self.learning_path["completed_concepts"]:
                    self.learning_path["completed_concepts"].append(concept)
                # Remove from struggling if mastered
                if concept in self.learning_path["struggling_concepts"]:
                    self.learning_path["struggling_concepts"].remove(concept)

        # Adjust adaptive difficulty
        if emotional_tone == "frustrated":
            self.learning_path["adaptive_difficulty"] = max(0.1,
                                                            self.learning_path["adaptive_difficulty"] - 0.1)
        elif emotional_tone == "confident":
            self.learning_path["adaptive_difficulty"] = min(1.0,
                                                            self.learning_path["adaptive_difficulty"] + 0.1)

        # Save updated learning path
        self.save_learning_path()

    def _get_recent_conversations(self, limit: int = 5) -> List[Dict]:
        """Get recent conversation history"""
        if os.path.exists(self.conversation_file):
            try:
                with open(self.conversation_file, 'r') as f:
                    conversations = json.load(f)
                    return conversations[-limit:]
            except:
                return []
        return []

    def _save_enhanced_conversation(self, user_message: str, coach_response: str, analysis: Dict):
        """Save conversation with semantic analysis"""
        conversations = []
        if os.path.exists(self.conversation_file):
            try:
                with open(self.conversation_file, 'r') as f:
                    conversations = json.load(f)
            except:
                conversations = []

        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "coach_response": coach_response,
            "analysis": analysis,
            "user_profile_snapshot": {
                "confidence_level": self.user_profile["personality_traits"]["confidence_level"],
                "curiosity_level": self.user_profile["personality_traits"]["curiosity_level"]
            }
        }

        conversations.append(conversation_entry)

        # Keep only last 100 conversations
        conversations = conversations[-100:]

        with open(self.conversation_file, 'w') as f:
            json.dump(conversations, f, indent=2)

    def get_personalized_suggestions(self) -> List[str]:
        """Generate personalized suggestions based on semantic analysis"""
        suggestions = []

        # Based on struggling concepts
        if self.learning_path["struggling_concepts"]:
            suggestions.append(
                f"🎯 Let's work on {', '.join(self.learning_path['struggling_concepts'][:2])} with a different approach")

        # Based on mastered concepts
        if self.learning_path["completed_concepts"]:
            mastered = self.learning_path["completed_concepts"][-2:]
            suggestions.append(f"🚀 Great progress on {', '.join(mastered)}! Ready for advanced topics?")

        # Based on question patterns
        question_patterns = self.user_profile["interaction_patterns"]["question_types"]
        if question_patterns:
            most_common = max(question_patterns.items(), key=lambda x: x[1])[0]
            if most_common == "definition":
                suggestions.append("📚 Try flashcards to reinforce definitions you've learned")
            elif most_common == "how_to":
                suggestions.append("🛠️ Practice with step-by-step exercises")
            elif most_common == "why":
                suggestions.append("🤔 Explore deeper connections between concepts")

        # Based on confidence level
        confidence = self.user_profile["personality_traits"]["confidence_level"]
        if confidence < 0.4:
            suggestions.append("💪 Start with easier topics to build confidence")
        elif confidence > 0.7:
            suggestions.append("🎯 Challenge yourself with advanced problems")

        # Adaptive difficulty suggestion
        difficulty = self.learning_path["adaptive_difficulty"]
        if difficulty < 0.3:
            suggestions.append("🌱 Focus on fundamentals before moving to complex topics")
        elif difficulty > 0.7:
            suggestions.append("🚀 Ready for expert-level challenges!")

        # Default suggestions if none specific
        if not suggestions:
            suggestions = [
                "🎯 Try a focused 15-minute learning session",
                "🧩 Generate flashcards for active recall",
                "📊 Check your analytics to optimize study time",
                "🎮 Take a quiz to test understanding"
            ]

        return suggestions[:4]

    def get_learning_insights(self) -> Dict:
        """Get comprehensive learning insights"""
        insights = {
            "personality_analysis": self.user_profile["personality_traits"],
            "learning_patterns": self.user_profile["interaction_patterns"],
            "progress_summary": {
                "concepts_mastered": len(self.learning_path["completed_concepts"]),
                "concepts_struggling": len(self.learning_path["struggling_concepts"]),
                "adaptive_difficulty": self.learning_path["adaptive_difficulty"],
                "knowledge_base_size": len(self.knowledge_texts)
            },
            "recommendations": self.get_personalized_suggestions()
        }

        return insights

    def generate_motivational_message(self) -> str:
        """Generate personalized motivational message based on user progress"""
        confidence = self.user_profile["personality_traits"]["confidence_level"]
        curiosity = self.user_profile["personality_traits"]["curiosity_level"]
        mastered_count = len(self.learning_path["completed_concepts"])
        struggling_count = len(self.learning_path["struggling_concepts"])

        if confidence < 0.3:
            messages = [
                "🌱 Every expert was once a beginner. You're building strong foundations!",
                "💪 Small steps lead to big achievements. Keep going!",
                "🌟 Your dedication to learning shows real strength!",
                "🧠 Your brain is forming new connections with every question you ask!"
            ]
        elif confidence > 0.7:
            messages = [
                "🚀 You're mastering concepts at an impressive pace!",
                "⭐ Your curiosity and confidence are your superpowers!",
                "🎯 Ready for the next challenge? You've got this!",
                "🔥 Your learning momentum is unstoppable!"
            ]
        else:
            messages = [
                "🌟 You're making steady progress - that's what matters!",
                "🧠 Every question you ask makes you smarter!",
                "💡 Your learning journey is unique and valuable!",
                "🎯 Focus on progress, not perfection!"
            ]

        if mastered_count > 0:
            messages.append(f"🎉 You've mastered {mastered_count} concepts - amazing progress!")

        if curiosity > 0.8:
            messages.append("🤔 Your curiosity is your greatest learning asset!")

        # Select message based on current day for some variety
        return messages[datetime.now().day % len(messages)]

    # Compatibility methods for backend_test.py
    def get_learning_suggestions(self) -> List[str]:
        """Compatibility method for get_personalized_suggestions"""
        return self.get_personalized_suggestions()

    def generate_coach_response(self, user_message: str, current_topic: str = "") -> str:
        """Compatibility method for generate_personalized_response"""
        return self.generate_personalized_response(user_message, current_topic)
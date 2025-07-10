import spacy
import random
import re
from typing import List, Dict, Tuple
import streamlit as st
from datetime import datetime
import json
import os


class FlashcardGenerator:
    def __init__(self):
        self.nlp = None
        self.setup_spacy()

    def setup_spacy(self):
        """Initialize spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except IOError:
            st.warning("spaCy model not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                st.error("Could not load spaCy model. Flashcards will use basic mode.")

    def extract_key_concepts(self, text: str) -> List[Dict]:
        """Extract key concepts and definitions from text"""
        concepts = []

        if self.nlp:
            doc = self.nlp(text)

            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT", "WORK_OF_ART", "LAW"]:
                    concepts.append({
                        "term": ent.text,
                        "type": "entity",
                        "context": self._get_context(text, ent.text)
                    })

            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) > 1 and len(chunk.text) > 5:
                    concepts.append({
                        "term": chunk.text,
                        "type": "concept",
                        "context": self._get_context(text, chunk.text)
                    })

        # Pattern-based extraction for definitions
        definition_patterns = [
            r'(.+?) is (.+?)[\.\
]',
            r'(.+?) means (.+?)[\.\
]',
            r'(.+?) refers to (.+?)[\.\
]',
            r'Define (.+?): (.+?)[\.\
]'
        ]

        for pattern in definition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                if len(term) < 50 and len(definition) < 200:
                    concepts.append({
                        "term": term,
                        "definition": definition,
                        "type": "definition"
                    })

        return concepts[:20]  # Limit to 20 concepts

    def _get_context(self, text: str, term: str) -> str:
        """Get surrounding context for a term"""
        sentences = text.split('.')
        for sentence in sentences:
            if term.lower() in sentence.lower():
                return sentence.strip()[:200]
        return ""

    def generate_flashcards(self, text: str, difficulty: str = "Medium") -> List[Dict]:
        """Generate adaptive flashcards based on difficulty level"""
        concepts = self.extract_key_concepts(text)
        flashcards = []

        for concept in concepts:
            if concept.get("type") == "definition":
                # Direct definition cards
                flashcards.append({
                    "question": f"What is {concept['term']}?",
                    "answer": concept["definition"],
                    "type": "definition",
                    "difficulty": difficulty
                })

                # Reverse card for harder difficulty
                if difficulty in ["Medium", "Hard"]:
                    flashcards.append({
                        "question": f"Which term is defined as: {concept['definition'][:100]}...?",
                        "answer": concept["term"],
                        "type": "reverse_definition",
                        "difficulty": difficulty
                    })

            elif concept.get("context"):
                # Context-based questions
                flashcards.append({
                    "question": f"Complete the concept: {concept['term']}",
                    "answer": concept["context"],
                    "type": "context",
                    "difficulty": difficulty
                })

        # Add difficulty-specific questions
        if difficulty == "Hard":
            flashcards.extend(self._generate_analytical_questions(text))

        return random.sample(flashcards, min(10, len(flashcards)))

    def _generate_analytical_questions(self, text: str) -> List[Dict]:
        """Generate analytical questions for hard difficulty"""
        return [
            {
                "question": "What are the main themes in this content?",
                "answer": "Analyze the key themes and concepts presented",
                "type": "analytical",
                "difficulty": "Hard"
            },
            {
                "question": "How do the concepts relate to each other?",
                "answer": "Consider the connections and relationships between ideas",
                "type": "analytical",
                "difficulty": "Hard"
            }
        ]

    def save_flashcard_performance(self, user_id: str, flashcard: Dict, correct: bool, response_time: float):
        """Save flashcard performance for adaptation"""
        performance_file = f"user_data/{user_id}_flashcard_performance.json"

        performance_data = []
        if os.path.exists(performance_file):
            with open(performance_file, 'r') as f:
                performance_data = json.load(f)

        performance_data.append({
            "timestamp": datetime.now().isoformat(),
            "question": flashcard["question"],
            "type": flashcard["type"],
            "difficulty": flashcard["difficulty"],
            "correct": correct,
            "response_time": response_time
        })

        with open(performance_file, 'w') as f:
            json.dump(performance_data, f, indent=2)

    def get_adaptive_difficulty(self, user_id: str) -> str:
        """Determine adaptive difficulty based on performance"""
        performance_file = f"user_data/{user_id}_flashcard_performance.json"

        if not os.path.exists(performance_file):
            return "Medium"

        with open(performance_file, 'r') as f:
            performance_data = json.load(f)

        if len(performance_data) < 5:
            return "Medium"

        # Analyze recent performance (last 10 attempts)
        recent_performance = performance_data[-10:]
        accuracy = sum(p["correct"] for p in recent_performance) / len(recent_performance)
        avg_response_time = sum(p["response_time"] for p in recent_performance) / len(recent_performance)

        # Adaptive logic
        if accuracy > 0.8 and avg_response_time < 5:
            return "Hard"
        elif accuracy < 0.5 or avg_response_time > 15:
            return "Easy"
        else:
            return "Medium"
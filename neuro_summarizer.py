import openai
import re
import streamlit as st
from typing import Dict, List
from config import AZURE_OPENAI_API_KEY, ENDPOINT_URL, DEPLOYMENT_NAME

class NeuroSummarizer:
    def __init__(self):
        self.client = openai.AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-02-01",
            azure_endpoint=ENDPOINT_URL
        )
        self.model = DEPLOYMENT_NAME

    def _call_openai(self, system_prompt: str, user_content: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return f"Error generating summary: {str(e)}"

    def basic_summary(self, content: str) -> str:
        system_prompt = """You are a neuro-friendly learning assistant. Create a clear, concise summary that:
        - Uses simple, direct language
        - Breaks down complex concepts into digestible chunks
        - Highlights the most important points
        - Uses bullet points for better readability
        - Keeps sentences short and clear
        - Is suitable for students with attention difficulties"""

        return self._call_openai(system_prompt, f"Summarize this content: {content[:3000]}")

    def story_mode_summary(self, content: str) -> str:
        system_prompt = """You are a storytelling tutor for neuro-friendly learning. Transform the content into:
        - An engaging narrative or story format
        - Use analogies and metaphors to explain concepts
        - Create connections between ideas using "story bridges"
        - Make abstract concepts concrete with examples
        - Use a conversational tone like explaining to a friend
        - Include memory hooks and mnemonics
        - Make it emotionally engaging but educational"""

        return self._call_openai(system_prompt, f"Turn this into an engaging story: {content[:3000]}")

    def visual_mode_summary(self, content: str) -> str:
        system_prompt = """You are a visual learning specialist. Create a structured summary that:
        - Uses emojis and visual symbols extensively 📚✨
        - Organizes information in clear hierarchies
        - Creates visual mind-map style layouts
        - Uses indentation and spacing for structure
        - Includes diagrams described in text when helpful
        - Uses colors described in words (e.g., "🔴 Important:", "🔵 Details:")
        - Makes information scannable and visually appealing
        - Uses symbols, arrows, and visual connectors
        - Perfect for visual learners and those with reading difficulties"""

        return self._call_openai(system_prompt, f"Create a visual summary: {content[:3000]}")

    def get_all_summaries(self, content: str) -> Dict[str, str]:
        summaries = {}

        with st.spinner("🧠 Generating Basic Summary..."):
            summaries['basic'] = self.basic_summary(content)

        with st.spinner("📖 Creating Story Mode..."):
            summaries['story'] = self.story_mode_summary(content)

        with st.spinner("🎨 Building Visual Summary..."):
            summaries['visual'] = self.visual_mode_summary(content)

        return summaries

    def chunk_content(self, content: str, chunk_size: int = 500) -> List[str]:
        sentences = re.split(r'[.!?]+', content)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
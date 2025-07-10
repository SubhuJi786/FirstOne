import os
import tempfile
import fitz  # PyMuPDF
import PyPDF2
import yt_dlp
import whisper
from typing import Optional, Tuple
import streamlit as st


class FileProcessor:
    def __init__(self):
        self.whisper_model = None

    def get_whisper_model(self):
        """Load whisper model lazily"""
        if self.whisper_model is None:
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model

    def extract_pdf_text(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            # Try PyMuPDF first (better for complex PDFs)
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            if text.strip():
                return text

            # Fallback to PyPDF2
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            return text

        except Exception as e:
            st.error(f"Error extracting PDF text: {str(e)}")
            return ""

    def extract_youtube_transcript(self, url: str) -> Tuple[str, str]:
        """Extract transcript from YouTube video"""
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'temp_audio.%(ext)s',
                'extractaudio': True,
                'audioformat': 'wav',
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Video')

                # Download audio
                ydl.download([url])

                # Find the downloaded file
                audio_file = None
                for file in os.listdir('.'):
                    if file.startswith('temp_audio'):
                        audio_file = file
                        break

                if audio_file:
                    # Transcribe audio
                    model = self.get_whisper_model()
                    result = model.transcribe(audio_file)

                    # Clean up
                    os.remove(audio_file)

                    return title, result['text']
                else:
                    return title, "Could not extract audio from video"

        except Exception as e:
            st.error(f"Error processing YouTube video: {str(e)}")
            return "Error", ""

    def save_content(self, content: str, filename: str, content_type: str) -> str:
        """Save processed content to file"""
        try:
            filepath = os.path.join("uploads", f"{filename}_{content_type}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return filepath
        except Exception as e:
            st.error(f"Error saving content: {str(e)}")
            return ""
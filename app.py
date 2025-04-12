import streamlit as st
st.set_page_config(page_title="Gita Wisdom + Emotion AI", layout="wide")
from typing import Dict, List, Optional, Any
import cv2
from PIL import Image
import numpy as np
import asyncio
import pandas as pd
import json
import os
from transformers import pipeline
import google.generativeai as genai

# Load emotion detection model
emotion_pipe = pipeline("image-classification", model="prithivMLmods/Facial-Emotion-Detection-SigLIP2")

# Gemini API Bot Class
class GitaGeminiBot:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.verses_db = self.load_gita_database()

    def load_gita_database(self) -> Dict:
        path = "bhagavad_gita_verses.csv"
        verses_df = pd.read_csv(path)
        verses_db = {}
        for _, row in verses_df.iterrows():
            chapter = f"chapter_{row['chapter_number']}"
            if chapter not in verses_db:
                verses_db[chapter] = {
                    "title": row['chapter_title'],
                    "verses": {}
                }
            verse_num = str(row['chapter_verse'])
            verses_db[chapter]["verses"][verse_num] = {
                "translation": row['translation']
            }
        return verses_db

    def format_response(self, raw_text: str) -> Dict:
        try:
            try:
                return json.loads(raw_text)
            except json.JSONDecodeError:
                pass

            if '{' in raw_text and '}' in raw_text:
                json_str = raw_text[raw_text.find('{'):raw_text.rfind('}')+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

            lines = raw_text.split('\n')
            response = {
                "verse_reference": "",
                "sanskrit": "",
                "translation": "",
                "explanation": "",
                "application": ""
            }
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if "Chapter" in line and "Verse" in line:
                    response["verse_reference"] = line
                elif line.startswith("Sanskrit:"):
                    response["sanskrit"] = line.replace("Sanskrit:", "").strip()
                elif line.startswith("Translation:"):
                    response["translation"] = line.replace("Translation:", "").strip()
                elif line.startswith("Explanation:"):
                    current_section = "explanation"
                    response["explanation"] = line.replace("Explanation:", "").strip()
                elif line.startswith("Application:"):
                    current_section = "application"
                    response["application"] = line.replace("Application:", "").strip()
                elif current_section:
                    response[current_section] += " " + line
            return response

        except Exception as e:
            return {
                "verse_reference": "Unable to parse verse",
                "sanskrit": "",
                "translation": raw_text,
                "explanation": "",
                "application": ""
            }

    async def get_response(self, emotion: str, question: str) -> Dict:
        try:
            prompt = f"""
            The user is currently feeling: {emotion}.
            Their question is: {question}.
            Based on the Bhagavad Gita, suggest guidance considering both the emotion and the question.

            Format the answer strictly like this:
            Chapter X, Verse Y
            Sanskrit: [Sanskrit verse]
            Translation: [English translation]
            Explanation: [Explain meaning clearly]
            Application: [How to apply it in modern life]
            """
            response = self.model.generate_content(prompt)
            return self.format_response(response.text)

        except Exception as e:
            return {
                "verse_reference": "Error",
                "sanskrit": "",
                "translation": f"Error: {str(e)}",
                "explanation": "",
                "application": ""
            }

# Setup session
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'bot' not in st.session_state:
    st.session_state.bot = GitaGeminiBot(api_key="YOUR_GEMINI_API_KEY")

# UI Layout
st.title("🧘‍♂️ Real-Time Emotion + Gita Guidance")
st.markdown("Use your emotion and question to receive relevant wisdom from the Bhagavad Gita.")

# Real-time emotion capture
FRAME_WINDOW = st.image([])
cap = cv2.VideoCapture(0)
stframe = st.empty()
st.markdown("### Emotion Detection")

if st.button("Capture Emotion"):
    ret, frame = cap.read()
    if ret:
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(img_rgb, caption="Captured Frame", use_column_width=True)

        pil_image = Image.fromarray(img_rgb)
        result = emotion_pipe(pil_image)[0]
        emotion = result['label']
        st.success(f"Detected Emotion: {emotion}")

        # Get user question
        question = st.text_input("What is your question or situation?")
        if question:
            with st.spinner("Thinking deeply..."):
                response = asyncio.run(st.session_state.bot.get_response(emotion, question))
                st.session_state.messages.append({"role": "assistant", **response})
                st.rerun()

# Show chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"**{message['verse_reference']}**")
        if message.get("sanskrit"): st.markdown(f"*{message['sanskrit']}*")
        if message.get("translation"): st.markdown(message["translation"])
        if message.get("explanation"):
            st.markdown("### Understanding")
            st.markdown(message["explanation"])
        if message.get("application"):
            st.markdown("### How to Apply")
            st.markdown(message["application"])

# Cleanup
cap.release()

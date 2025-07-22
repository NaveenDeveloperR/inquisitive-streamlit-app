import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
from langdetect import detect
from googletrans import Translator
import re
import os
import openai  # Added for fallback

# --- API Key Configuration ---
API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not API_KEY and not OPENAI_KEY:
    st.error("No API keys found. Please set 'GOOGLE_API_KEY' or 'OPENAI_API_KEY'.")
    st.stop()

# Try Gemini configuration
try:
    if API_KEY:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
except Exception as e:
    st.warning(f"Gemini config failed: {e}")
    model = None

if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

translator = Translator()

# --- Question Generation Logic ---

def generate_with_openai(text):
    try:
        prompt = f"""Generate a list of questions based on the following text.
Each question should be directly answerable from the text provided.
Provide the questions as a numbered list.

Text:
---
{text}
---

Questions:
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI fallback failed: {e}")
        return None

def generate_questions(text):
    if model:
        try:
            prompt = f"""Generate a list of questions based on the following text.
Each question should be directly answerable from the text provided.
Provide the questions as a numbered list.

Text:
---
{text}
---

Questions:
"""
            response = model.generate_content(prompt)
            questions = response.text.strip()
            if not questions:
                return "No questions generated."
            return questions
        except exceptions.GoogleAPIError as e:
            st.warning(f"Gemini API failed: {e}. Falling back to OpenAI.")
        except Exception as e:
            st.warning(f"Gemini error: {e}. Falling back to OpenAI.")

    # Fallback to OpenAI
    if OPENAI_KEY:
        return generate_with_openai(text)
    else:
        st.error("No fallback available. Please set OPENAI_API_KEY.")
        return None

# --- Streamlit App ---

def main():
    st.title("Inquisitive (Gemini + OpenAI Fallback)")

    st.info("Enter any text. The app will generate questions using Google Gemini, and fallback to OpenAI GPT-3.5 if needed.")

    user_text = st.text_area("Enter text:")

    word_count = len(re.findall(r'\w+', user_text))
    min_word_limit = 5

    if word_count < min_word_limit:
        st.warning(f"Please enter at least {min_word_limit} words.")
        st.button("Generate Questions", disabled=True)
    else:
        if st.button("Generate Questions"):
            detected_language = 'en'
            translated_text = user_text
            translation_needed = False

            try:
                detected_language = detect(user_text)
                if detected_language != 'en':
                    translated_text = translator.translate(user_text, src=detected_language, dest="en").text
                    translation_needed = True
                    st.info(f"Detected language: {detected_language}. Translating to English.")
                else:
                    st.info("Detected language: English.")
            except Exception as e:
                st.warning(f"Language detection/translation failed. Proceeding with original text. Error: {e}")

            questions = generate_questions(translated_text)

            if questions:
                if translation_needed and detected_language != 'en':
                    try:
                        questions = translator.translate(questions, src="en", dest=detected_language).text
                        st.info(f"Translated questions back to {detected_language}.")
                    except Exception as e:
                        st.warning(f"Translation back to {detected_language} failed. Showing English. Error: {e}")

                st.subheader("Generated Questions:")
                st.write(questions)

if __name__ == "__main__":
    main()

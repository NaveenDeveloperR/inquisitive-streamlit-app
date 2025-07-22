import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
from langdetect import detect
from googletrans import Translator
import re
import os
import openai

# --- API Key Configuration ---
API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not API_KEY and not OPENAI_KEY:
    st.error("❌ No API keys found. Please set 'GOOGLE_API_KEY' or 'OPENAI_API_KEY'.")
    st.stop()

# Try Gemini configuration
model = None
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    except Exception as e:
        st.warning(f"⚠️ Failed to initialize Gemini: {e}")
        model = None

if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

translator = Translator()

# --- OpenAI Fallback Logic ---
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
        st.error(f"❌ OpenAI fallback failed: {e}")
        return None

# --- Unified Question Generator ---
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
            if "quota" in str(e).lower() or "RATE_LIMIT_EXCEEDED" in str(e):
                st.warning("⚠️ Gemini API quota exceeded. Falling back to OpenAI.")
            else:
                st.error(f"❌ Gemini API error: {e}")
            # Proceed to fallback

        except Exception as e:
            st.warning("⚠️ Gemini generation failed. Falling back to OpenAI.")

    # --- Fallback to OpenAI ---
    if OPENAI_KEY:
        return generate_with_openai(text)
    else:
        st.error("❌ No fallback available. Please set OPENAI_API_KEY.")
        return None

# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="Inquisitive", page_icon="🤖", layout="centered")
    st.title("🧠 Inquisitive (Gemini + OpenAI Fallback)")
    st.info("Enter any text below. This app will generate relevant questions using **Google Gemini**, and fall back to **OpenAI GPT-3.5** if needed.")

    user_text = st.text_area("Enter your text here:", height=200)

    word_count = len(re.findall(r"\w+", user_text))
    min_word_limit = 5

    if word_count < min_word_limit:
        st.warning(f"⚠️ Please enter at least {min_word_limit} words to proceed.")
        st.button("Generate Questions", disabled=True)
    else:
        if st.button("Generate Questions"):
            detected_language = "en"
            translated_text = user_text
            translation_needed = False

            # --- Detect & Translate to English if needed ---
            try:
                detected_language = detect(user_text)
                if detected_language != "en":
                    translated_text = translator.translate(user_text, src=detected_language, dest="en").text
                    translation_needed = True
                    st.info(f"🌐 Detected language: {detected_language.upper()}. Translating to English for better question generation.")
                else:
                    st.info("✅ Detected language: English.")
            except Exception as e:
                st.warning(f"⚠️ Language detection or translation failed. Proceeding with original text. Error: {e}")

            # --- Generate Questions ---
            questions = generate_questions(translated_text)

            # --- Translate Back if Needed ---
            if questions:
                if translation_needed:
                    try:
                        questions = translator.translate(questions, src="en", dest=detected_language).text
                        st.info(f"🌐 Translated questions back to {detected_language.upper()}.")
                    except Exception as e:
                        st.warning(f"⚠️ Translation back to {detected_language.upper()} failed. Showing questions in English.")

                st.subheader("📋 Generated Questions:")
                st.write(questions)

if __name__ == "__main__":
    main()

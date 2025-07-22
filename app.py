import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions # Import specific exception class
from langdetect import detect
from googletrans import Translator # Note: googletrans is unofficial and can be unreliable
import re
import os # Import os to access environment variables

# --- Configuration ---

# Get the API key from environment variables
# Replace "GOOGLE_API_KEY" with the actual name of your environment variable if different
# Ensure you set this environment variable where you run the app (e.g., Render settings, .env file)
API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

# Check if the API key is available
if not API_KEY:
    st.error("Google API key not found. Please set the 'GOOGLE_API_KEY' environment variable.")
    st.stop() # Stop the app if the key is missing

st.subheader("Available Models")
for model_info in genai.list_models():
    st.write(model_info.name)

# Configure the Gemini API
try:
    genai.configure(api_key=API_KEY)
    # Define the model - Using gemini-1.0-pro as it's generally available and robust
    # If you specifically need 1.5-pro, ensure your key has access and keep that name.
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}")
    st.stop()

translator = Translator() # Note: googletrans is unofficial

# --- Functions ---

# Function to generate questions from text using Gemini
def generate_questions(text):
    # Add a try-except block specifically for the API call
    try:
        # Use a slightly more robust prompt for question generation
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
        # Access the generated text
        questions = response.text.strip()
        if not questions:
             return "No questions could be generated from the provided text."
        return questions

    except exceptions.GoogleAPIError as e:
        # Catch specific API errors
        st.error(f"Google API Error: {e}")
        st.error("Possible reasons: Invalid API key, quota limits reached, network issues, or text violates content policy.")
        return None # Return None to indicate failure
    except Exception as e:
        # Catch any other unexpected errors during generation
        st.error(f"An unexpected error occurred during question generation: {e}")
        return None # Return None to indicate failure


# --- Streamlit App ---

def main():
    st.title("Inquisitive (Gemini Version)")

    st.info("This app generates questions from text using the Google Gemini API.")

    # Input text from the user
    user_text = st.text_area("Enter the text you want questions generated from:")

    # Calculate the number of words
    word_count = len(re.findall(r'\w+', user_text))

    # Define minimum word limit
    min_word_limit = 5

    # Display information based on word count and trigger generation
    if word_count < min_word_limit:
        st.warning(f"Please enter at least {min_word_limit} words.")
        # Disable the button if the word count is too low
        if st.button("Generate Questions", disabled=True):
             pass # Button is disabled, so this block won't run
    else:
        # Display the Generate Questions button
        if st.button("Generate Questions"):
            # Language detection and translation
            detected_language = 'en' # Assume English initially
            translated_text = user_text # Start with original text
            translation_needed = False

            try:
                detected_language = detect(user_text)
                if detected_language != 'en':
                    translated_text = translator.translate(user_text, src=detected_language, dest="en").text
                    translation_needed = True
                    st.info(f"Detected language: {detected_language}. Translating to English for processing.")
                else:
                    st.info("Detected language: English.")
            except Exception as e:
                st.warning(f"Could not reliably detect language or translate. Proceeding with text as is. Error: {str(e)}")
                # Continue with the original text if detection/translation fails
                translated_text = user_text
                detected_language = 'en' # Assume English for later translation step

            # Generate questions using Gemini API
            questions = generate_questions(translated_text)

            # If questions were successfully generated (not None)
            if questions is not None:
                # Translate questions back to the original language if needed
                if translation_needed and detected_language != 'en':
                    try:
                        st.info(f"Translating questions back to {detected_language}.")
                        questions = translator.translate(questions, src="en", dest=detected_language).text
                    except Exception as e:
                        st.warning(f"Error during translation of questions back to {detected_language}. Displaying in English. Error: {str(e)}")
                        # If translation back fails, keep the English questions

                # Display generated questions
                st.subheader("Generated Questions:")
                st.write(questions)

if __name__ == "__main__":
    main()
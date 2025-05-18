import streamlit as st
import google.generativeai as genai  # Update to Gemini API
from langdetect import detect
from googletrans import Translator
import re
import os

# Configure the Gemini API with your API key
genai.configure(api_key="AIzaSyBB2npUDIRkEfAuzo4g93YI03IYt9ImXd8")  # Replace with your actual Gemini API key
translator = Translator()

# Define the model
model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest')  # Assuming 'gemini-pro' is the model you want

# Function to generate questions from text using Gemini
def generate_questions(text):
    response = model.generate_content(f"Generate questions from the following text:\n\n{text}\n\nQuestions:")
    # Extract generated text from the response (adjusting based on actual Gemini response format)
    questions = response.text.strip() if response.text else "No questions generated."
    return questions

def main():
    st.title("Inquisitive (Gemini Version)")
    
    # Input text from the user
    user_text = st.text_area("Enter the text you want questions generated from:")
    
    # Calculate the number of words
    word_count = len(re.findall(r'\w+', user_text))
    
    # Define minimum word limit
    min_word_limit = 5
    
    # Display information based on word count
    if word_count < min_word_limit:
        st.warning(f"Please enter at least {min_word_limit} words.")
    else:
        # Display the Generate Questions button
        if st.button("Generate Questions"):
            # Language detection and translation
            try:
                detected_language = detect(user_text)
                if detected_language != 'en':
                    translated_text = translator.translate(user_text, src=detected_language, dest="en").text
                else:
                    translated_text = user_text
            except Exception as e:
                st.error(f"Error during language detection or translation: {str(e)}")
                return
            
            # Generate questions using Gemini API
            questions = generate_questions(translated_text)
                
            # Translate questions back to the original language if needed 
            if detected_language != 'en':
                try:
                    questions = translator.translate(questions, src="en", dest=detected_language).text
                except Exception as e:
                    st.error(f"Error during translation of questions: {str(e)}")
                    return
                
            # Display generated questions
            st.subheader("Generated Questions:")
            st.write(questions)

if __name__ == "__main__":
    main()


import streamlit as st
import google.generativeai as palm
from langdetect import detect
from googletrans import Translator
import re

# Configure the API with your API key
palm.configure(api_key="AIzaSyBxGYppk4xTJZS15tE8apj0ODi7aq75AK0")
translator = Translator()

# List available models and select one
models = [model for model in palm.list_models()]
if len(models) > 1:
    model_name = models[1].name  # Assuming there are models available
else:
    model_name = "default_model_name"  # Set a default model name if no models are listed

# Function to generate questions from text
def generate_questions(model_name, text):
    response = palm.generate_text(
        model=model_name,
        prompt=f"Generate questions from the following text: \n\n{text}\n\nQuestions:",
        max_output_tokens=150
    )
    # Extract generated text from the result attribute
    questions = response.result.strip() if response.result else "No questions generated."
    return questions

def main():
    st.title("Inquisitive")
    
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
            
            # Generate questions
            questions = generate_questions(model_name, translated_text)
                
            # Translate questions back to the original language if translated 
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

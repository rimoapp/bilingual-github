import openai  # Correct library
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")  # Set the API key correctly

def translate_text(text, target_language):
    try:
        # Correct method call
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Specify the model
            messages=[
                {"role": "system", "content": f"Translate this text to {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        
        translation = response['choices'][0]['message']['content']  # Parse response correctly
        
        return translation
    
    except Exception as e:
        print(f"Error in translation: {e}")
        return None

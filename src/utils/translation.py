import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Set up OpenAI client with API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def translate_text(text, target_language):
    try:
        # Send request to OpenAI's chat API for translation
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Adjust model version if needed
            messages=[
                {"role": "system", "content": f"Translate this text to {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        
        # Extract translation from the response
        translation = response.choices[0].message.content
        
        return translation
    
    except Exception as e:
        print(f"Error in translation: {e}")
        return None

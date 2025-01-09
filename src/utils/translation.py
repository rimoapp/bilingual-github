import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def translate_text(text, target_language):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": f"Translate this text to {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        
        translation = response.choices[0].message.content
        
        return translation
    
    except Exception as e:
        print(f"Error in translation: {e}")
        return None

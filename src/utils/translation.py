import openai
import yaml

# Load configuration
with open("config/config.yml", "r") as file:
    config = yaml.safe_load(file)

openai.api_key = config["llm"]["api_key"]

def translate_text(text, target_language):
    try:
        response = openai.ChatCompletion.create(
            model=config["llm"]["model"],
            messages=[
                {"role": "system", "content": f"Translate this text to {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in translation: {e}")
        return None

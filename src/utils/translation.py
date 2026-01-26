import os
import re
from dotenv import load_dotenv
import requests

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please ensure it is defined in the environment.")


def _detect_language_unicode(text):
    """
    Fallback language detection using Unicode character ranges.
    Returns 'ja' if Japanese characters are found, 'en' otherwise.
    """
    HIRAGANA = '\u3040-\u309F'
    KATAKANA = '\u30A0-\u30FF'
    KANJI = '\u4E00-\u9FFF'
    HALF_WIDTH_KATAKANA = '\uFF60-\uFF9F'

    jp_pattern = f'[{HIRAGANA}{KATAKANA}{KANJI}{HALF_WIDTH_KATAKANA}]'
    has_japanese = bool(re.search(jp_pattern, text))

    return "ja" if has_japanese else "en"


def detect_language(text):
    """
    Detect language using LLM. Returns 'ja' for Japanese, 'en' for English.
    Falls back to Unicode detection if API fails.
    """
    if not text or not text.strip():
        return "en"

    try:
        url = "https://api.openai.com/v1/chat/completions"

        # Limit text to first 500 chars to reduce cost
        sample_text = text[:500] if len(text) > 500 else text

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a language detector. Analyze the text and respond with ONLY 'ja' if the text is primarily Japanese, or 'en' if it's primarily English or any other language. Output only the 2-letter language code, nothing else."
                },
                {
                    "role": "user",
                    "content": sample_text
                }
            ],
            "temperature": 0,
            "max_tokens": 5
        }

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '').strip()}"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()
            detected = result["choices"][0]["message"]["content"].strip().lower()

            # Validate response is one of expected values
            if detected in ["ja", "en"]:
                return detected
            else:
                print(f"Unexpected language detection response: {detected}, falling back to Unicode detection")
                return _detect_language_unicode(text)
        else:
            print(f"Language detection API failed with status {response.status_code}, falling back to Unicode detection")
            return _detect_language_unicode(text)

    except Exception as e:
        print(f"Error in language detection: {e}, falling back to Unicode detection")
        return _detect_language_unicode(text)

def translate_text(text, target_language):
    try:
        url = "https://api.openai.com/v1/chat/completions"

        payload = {
            "model": "gpt-4o-mini",  
            "messages": [
                {"role": "system", "content": f"Translate this text to {target_language}."},
                {"role": "user", "content": text}
            ]
        }

        headers = {
           "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '').strip()}"
        }
        if "Bearer" not in headers["Authorization"]:
            print("Error: Authorization header is malformed.")

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            translation = result["choices"][0]["message"]["content"]
            return translation
        else:
            print(f"Failed to connect to OpenAI API. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"Error in translation: {e}")
        return None


def translate_incremental(base_content, current_content, existing_translation, target_lang):
    """
    Translate only the changed portions using GPT with three-file context.
    
    Args:
        base_content: The previous version of the source document
        current_content: The updated version of the source document (with changes)
        existing_translation: The current translation of the base version
        target_lang: Target language for translation
    
    Returns:
        Updated translation with only the necessary changes applied, or None on failure
    """
    print(f"\n[DEBUG] translate_incremental called:")
    print(f"  - base_content: {len(base_content)} chars")
    print(f"  - current_content: {len(current_content)} chars")
    print(f"  - existing_translation: {len(existing_translation)} chars")
    print(f"  - target_lang: {target_lang}")
    
    prompt = f"""You are translating a markdown document to {target_lang}.

I will provide you with three versions of the document:
1. BASE VERSION: The previous version of the source document
2. CURRENT VERSION: The updated version of the source document (with changes)
3. EXISTING TRANSLATION: The current translation of the base version

Your task:
- Identify what changed between BASE and CURRENT versions
- Update ONLY the changed portions in the EXISTING TRANSLATION
- Preserve all unchanged parts of the EXISTING TRANSLATION exactly as they are
- Maintain the same markdown structure and formatting

CRITICAL: Return ONLY the complete updated translation. Do NOT include any explanations, notes, or comments. Do NOT say "Since there are no changes" or similar messages. Just return the translated document content.

BASE VERSION:
{base_content}

CURRENT VERSION:
{current_content}

EXISTING TRANSLATION:
{existing_translation}

Updated translation:"""

    try:
        url = "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": f"You are a precise translator. Return ONLY the translated content without any explanations or comments. Translate only the changed portions to {target_lang}."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        
        print(f"\n[DEBUG] Sending request to OpenAI API:")
        print(f"  - model: gpt-4")
        print(f"  - prompt length: {len(prompt)} chars")
        print(f"  - system message: 'You are a precise translator. Translate only the changed portions to {target_lang}.'")
        print(f"  - Prompt preview (first 200 chars): {prompt[:200]}...")
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '').strip()}"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"\n[DEBUG] OpenAI API response:")
        print(f"  - status_code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            translation = result["choices"][0]["message"]["content"]
            print(f"  - ✓ SUCCESS: translation received")
            print(f"  - translation length: {len(translation)} chars")
            print(f"  - translation lines: {len(translation.splitlines())} lines")
            print(f"  - Translation preview (first 200 chars): {translation[:200]}...")
            return translation
        else:
            print(f"  - ✗ ERROR: Incremental translation failed")
            print(f"  - Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n[DEBUG] ✗ Exception in incremental translation: {e}")
        import traceback
        traceback.print_exc()
        return None


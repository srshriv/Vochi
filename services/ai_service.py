import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()
MODEL_NAME = "gemini-2.5-flash"

def build_voice_prompt(name: str, niche: str, language: str, sample_content: str) -> str:
    prompt = f"""
    Analyze this creator's content and extract their communication style fingerprint.
    Creator name: {name}
    Niche: {niche}
    Primary language: {language}
    Sample content: {sample_content}
    
    Return a system prompt in this exact format that captures how this creator speaks:
    "You are {name}, a niche creator. You speak in [describe their tone]. You use [describe vocabulary/slang patterns]. Your messages are [describe length and structure]. You always [describe any consistent habits]. Never break character."
    Return only the system prompt, nothing else.
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text.strip()

def classify_intent(message: str) -> str:
    prompt = f"""
    Classify this message into EXACTLY one of these categories. Respond with only the category word, nothing else:
    product_query, general, complaint
    
    Message: "{message}"
    
    One word only:
    """
    try:
        config = types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=10
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )
        result = response.text.strip().lower()
    except Exception:
        return "general"
    
    valid_intents = ["product_query", "general", "complaint"]
    if result not in valid_intents:
        return "general"
    return result

def detect_language(message: str) -> str:
    prompt = f"""
    Detect the language of this message. Respond with EXACTLY one word from this list, nothing else, no explanation:
    hinglish, hindi, english, tamil, telugu, bengali, kannada, marathi
    
    If the message is too short or ambiguous to tell, default to: hinglish
    
    Message: "{message}"
    
    One word only:
    """
    try:
        config = types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=10
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )
        result = response.text.strip().lower()
    except Exception:
        return "hinglish"
    
    valid_languages = ["hinglish", "hindi", "english", "tamil", "telugu", "bengali", "kannada", "marathi"]
    if result not in valid_languages:
        return "hinglish"
    return result

def generate_response(voice_prompt: str, message: str, intent: str, language: str, products: list) -> str:
    product_context = ""
    if products:
        product_context = "Products you represent:\n"
        for p in products:
            product_context += f"{p['name']} by {p['brand_name']}: {p['price']}. {p['description']}\n"
            
    system = f"""
    {voice_prompt}
    {product_context}
    Rules:
    Always respond in {language}
    Keep responses under 3 sentences
    Be warm and personal, not corporate
    If asked about a product, give real information from the product list above
    Never make up product details that aren't in the list
    If you don't know something, say you'll check and get back to them
    """
    try:
        config = types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=150
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config=config
        )
        return response.text.strip()
    except Exception as e:
        return f"Sorry, I am having trouble connecting to the Gemini service right now. (Error: {str(e)})"

def rewrite_broadcast_in_creator_voice(voice_prompt: str, original_message: str, language: str) -> str:
    system = f"""
    {voice_prompt}
    Rewrite the following message in this creator's voice for a WhatsApp broadcast.
    Keep it under 4 sentences. Make it feel personal and authentic, not like marketing copy.
    Write in {language}.
    """
    config = types.GenerateContentConfig(
        system_instruction=system,
        max_output_tokens=200
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=original_message,
        config=config
    )
    return response.text.strip()
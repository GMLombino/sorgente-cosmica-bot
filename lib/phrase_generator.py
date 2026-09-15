"""
Generazione della frase quotidiana tramite l'API di testo di Pollinations
(https://text.pollinations.ai/openai, compatibile OpenAI).
"""
import json
from google import genai
from google.genai import types
from pydantic import BaseModel

class PhraseOutput(BaseModel):
    frase: str
    tema: str

def generate_phrase(system_prompt: str, recent_phrases: list[str], api_key: str) -> dict:
    if not api_key:
        raise ValueError("GEMINI_API_KEY non configurata.")

    client = genai.Client(api_key=api_key)

    user_prompt = "Genera una nuova frase spirituale."
    if recent_phrases:
        user_prompt += "\n\nEvita di ripetere o rielaborare frasi simili a queste già usate di recente:\n"
        user_prompt += "\n".join(f"- {p}" for p in recent_phrases)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
        response_mime_type="application/json",
        response_schema=PhraseOutput,
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=config,
    )

    data = json.loads(response.text)
    return {"frase": data["frase"], "tema": data["tema"]}

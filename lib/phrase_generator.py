"""
Generazione della frase quotidiana tramite l'API Gemini
"""
import json
from google import genai
from google.genai import types
from pydantic import BaseModel


class PhraseOutput(BaseModel):
    frase_immagine: str
    spiegazione: str
    hashtags: str
    tema: str


def generate_phrase(system_prompt: str, recent_phrases: list[str], api_key: str) -> dict:
    if not api_key:
        raise ValueError("GEMINI_API_KEY non configurata.")

    client = genai.Client(api_key=api_key)

    user_prompt = "Genera un nuovo contenuto spirituale per oggi."
    if recent_phrases:
        user_prompt += "\n\nEvita di ripetere o rielaborare frasi simili a queste già usate di recente:\n"
        user_prompt += "\n".join(f"- {p}" for p in recent_phrases)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
        response_mime_type="application/json",
        response_schema=PhraseOutput,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=config,
    )

    data = json.loads(response.text)
    return {
        "frase_immagine": data["frase_immagine"],
        "spiegazione": data["spiegazione"],
        "hashtags": data["hashtags"],
        "tema": data["tema"],
    }

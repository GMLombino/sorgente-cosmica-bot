"""
Generazione della frase quotidiana tramite l'API Gemini
"""
import json
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError
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

    # Tempi di attesa estesi per superare i picchi di traffico reali (in secondi)
    retry_delays = [30, 60, 120, 180]  # Totale attesa potenziale: ~4.5 minuti
    max_retries = len(retry_delays) + 1

    for attempt in range(1, max_retries + 1):
        try:
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
        except (APIError, Exception) as err:
            is_transient = False
            
            # Controllo se è un errore di server o rate limit (503, 429, 500, 504)
            if isinstance(err, APIError) and err.code in (503, 429, 500, 504):
                is_transient = True
            elif any(code in str(err) for code in ["503", "UNAVAILABLE", "429", "504"]):
                is_transient = True

            if is_transient and attempt < max_retries:
                wait_time = retry_delays[attempt - 1]
                print(f"[phrase_generator] Errore temporaneo Gemini ({err}). Server saturo, attesa di {wait_time}s (tentativo {attempt}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise err

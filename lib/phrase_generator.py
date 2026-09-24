import json
import config
from google import genai
from groq import Groq


def _generate_with_gemini(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    """Tenta la generazione con il nuovo SDK ufficiale google-genai."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"{system_prompt}\n\n{user_prompt}",
    )
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw_text)


def _generate_with_groq(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    """Fallback su Groq con modello Llama attivo e verificato."""
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # In alternativa: llama3-8b-8192
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    raw_text = response.choices[0].message.content.strip()
    return json.loads(raw_text)


def generate_phrase(system_prompt: str, recent_phrases: list, recent_topics: list, api_key: str) -> dict:
    """Funzione principale con gestione del Fallback tra Gemini e Groq."""
    user_prompt = (
        f"FRASI USATE DI RECENTE (da non ripetere):\n{recent_phrases}\n\n"
        f"TEMI USATI DI RECENTE (da evitare se possibile):\n{recent_topics}"
    )

    # 1. Tentativo primario: Gemini 2.5 Flash
    try:
        print("[phrase_generator] Tentativo con Gemini 2.5 Flash...")
        return _generate_with_gemini(system_prompt, user_prompt, api_key)
    except Exception as err:
        print(f"[phrase_generator] ERRORE con Gemini: {err}")
        print("[phrase_generator] Attivazione fallback su Groq...")

    # 2. Tentativo secondario (Fallback): Groq
    groq_key = getattr(config, "GROQ_API_KEY", None)
    if groq_key:
        try:
            content = _generate_with_groq(system_prompt, user_prompt, groq_key)
            print("[phrase_generator] Generazione completata con successo tramite Groq!")
            return content
        except Exception as err:
            print(f"[phrase_generator] ERRORE anche con Groq: {err}")

    raise RuntimeError("Tutti i fornitori AI (Gemini e Groq) hanno risposto con errore.")

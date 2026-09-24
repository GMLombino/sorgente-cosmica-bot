import json
import config
import google.generativeai as genai
from groq import Groq


def _generate_with_gemini(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw_text)


def _generate_with_groq(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Modello gratuito, veloce e preciso
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
    user_prompt = (
        f"FRASI USATE DI RECENTE (da non ripetere):\n{recent_phrases}\n\n"
        f"TEMI USATI DI RECENTE (da evitare se possibile):\n{recent_topics}"
    )

    # 1. Tentativo primario con Gemini
    try:
        print("[phrase_generator] Tentativo con Gemini...")
        return _generate_with_gemini(system_prompt, user_prompt, api_key)
    except Exception as err:
        print(f"[phrase_generator] ERRORE con Gemini: {err}")
        print("[phrase_generator] Attivazione fallback su Groq (Llama 3.1)...")

    # 2. Fallback gratuito su Groq
    groq_key = getattr(config, "GROQ_API_KEY", None)
    if groq_key:
        try:
            content = _generate_with_groq(system_prompt, user_prompt, groq_key)
            print("[phrase_generator] Generazione completata con successo tramite Groq!")
            return content
        except Exception as err:
            print(f"[phrase_generator] ERRORE anche con Groq: {err}")

    raise RuntimeError("Tutti i fornitori AI (Gemini e Groq) hanno risposto con errore.")

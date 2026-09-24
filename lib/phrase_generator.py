import json
import config
from google import genai
from groq import Groq


def _generate_with_gemini(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    """Tenta la generazione con il nuovo SDK ufficiale google-genai."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # Oppure "gemini-3.6-flash" quando si resetta la quota
        contents=f"{system_prompt}\n\n{user_prompt}",
    )
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw_text)


def _generate_with_groq(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    """Fallback su Groq con modello attivo e garantito sul piano free."""
    client = Groq(api_key=api_key)
    
    # Prove in sequenza con modelli standard leggeri di Groq
    models_to_try = ["llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768"]
    last_err = None

    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )
            raw_text = response.choices[0].message.content.strip()
            return json.loads(raw_text)
        except Exception as err:
            last_err = err
            continue

    raise last_err


def generate_phrase(system_prompt: str, recent_phrases: list, recent_topics: list, api_key: str) -> dict:
    """Funzione principale con gestione del Fallback tra Gemini e Groq."""
    user_prompt = (
        f"FRASI USATE DI RECENTE (da non ripetere):\n{recent_phrases}\n\n"
        f"TEMI USATI DI RECENTE (da evitare se possibile):\n{recent_topics}"
    )

    # 1. Tentativo primario: Gemini
    try:
        print("[phrase_generator] Tentativo con Gemini...")
        return _generate_with_gemini(system_prompt, user_prompt, api_key)
    except Exception as err:
        print(f"[phrase_generator] Gemini in errore/quota esaurita ({err}). Passaggio a Groq...")

    # 2. Tentativo secondario (Fallback): Groq
    groq_key = getattr(config, "GROQ_API_KEY", None)
    if groq_key:
        try:
            print("[phrase_generator] Tentativo di generazione con Groq...")
            content = _generate_with_groq(system_prompt, user_prompt, groq_key)
            print("[phrase_generator] Post generato con successo tramite Groq!")
            return content
        except Exception as err:
            print(f"[phrase_generator] ERRORE anche con Groq: {err}")

    raise RuntimeError("Tutti i fornitori AI (Gemini e Groq) hanno risposto con errore.")

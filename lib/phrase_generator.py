import json
import config
from google import genai
from groq import Groq


def _parse_json_response(raw_text: str) -> dict:
    if not raw_text:
        raise ValueError("Risposta vuota dal modello.")

    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[len("```json"):].strip()
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[len("```"):].strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-len("```")].strip()

    result = json.loads(cleaned_text)
    if not isinstance(result, dict):
        raise ValueError("La risposta JSON non è un oggetto.")

    return result


# ============================================================
# DISCOVERY DINAMICA GEMINI
# ============================================================

def _discover_gemini_models(client) -> list:
    """Richiede a Google i modelli disponibili ed estrae solo quelli idonei."""
    valid_models = []
    
    try:
        print("[phrase_generator] Interrogazione API Gemini per elenco modelli attivi...")
        models_page = client.models.list()
        
        for m in models_page:
            model_id = getattr(m, "name", "").replace("models/", "")
            
            # Filtro 1: Deve contenere 'gemini' nel nome
            if "gemini" not in model_id.lower():
                continue
                
            # Filtro 2: Escludiamo modelli di solo embedding o audio/visione pura
            if any(forbidden in model_id.lower() for forbidden in ["embedding", "imagen", "audio", "whisper", "tts"]):
                continue

            # Filtro 3: Verifica della capacità 'generateContent' se dichiarata
            supported_actions = getattr(m, "supported_actions", None)
            if supported_actions and "generateContent" not in supported_actions:
                continue

            valid_models.append(model_id)

        # Ordina per mettere in cima i modelli più recenti o performanti
        valid_models.sort(reverse=True)
        print(f"[phrase_generator] Modelli Gemini idonei trovati: {valid_models}")

    except Exception as err:
        print(f"[phrase_generator] Errore durante la discovery Gemini: {err}")

    return valid_models


def _generate_with_gemini(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    client = genai.Client(api_key=api_key)
    models_to_try = _discover_gemini_models(client)

    if not models_to_try:
        raise RuntimeError("Nessun modello Gemini idoneo rilevato dall'API.")

    last_err = None
    for model_name in models_to_try:
        try:
            print(f"[phrase_generator] Gemini: tentativo con {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=f"{system_prompt}\n\n{user_prompt}",
            )
            return _parse_json_response(response.text)

        except Exception as err:
            last_err = err
            print(f"[phrase_generator] Gemini {model_name} non disponibile o fallito: {err}")
            continue

    raise last_err or RuntimeError("Nessun modello Gemini ha risposto.")


# ============================================================
# DISCOVERY DINAMICA GROQ
# ============================================================

def _discover_groq_models(client) -> list:
    """Richiede a Groq i modelli disponibili ed estrae i modelli di chat."""
    valid_models = []

    try:
        print("[phrase_generator] Interrogazione API Groq per elenco modelli attivi...")
        response = client.models.list()
        
        for m in response.data:
            model_id = getattr(m, "id", "")

            # Escludiamo audio (Whisper) e guardrails
            if any(forbidden in model_id.lower() for forbidden in ["whisper", "guard", "safetensors"]):
                continue

            valid_models.append(model_id)

        print(f"[phrase_generator] Modelli Groq idonei trovati: {valid_models}")

    except Exception as err:
        print(f"[phrase_generator] Errore durante la discovery Groq: {err}")

    return valid_models


def _generate_with_groq(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    client = Groq(api_key=api_key)
    models_to_try = _discover_groq_models(client)

    if not models_to_try:
        raise RuntimeError("Nessun modello Groq idoneo rilevato dall'API.")

    last_err = None
    for model_name in models_to_try:
        try:
            print(f"[phrase_generator] Groq: tentativo con {model_name}...")
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
            return _parse_json_response(raw_text)

        except Exception as err:
            last_err = err
            print(f"[phrase_generator] Groq {model_name} non disponibile o fallito: {err}")
            continue

    raise last_err or RuntimeError("Nessun modello Groq ha risposto.")


# ============================================================
# MAIN
# ============================================================

def generate_phrase(system_prompt: str, recent_phrases: list, recent_topics: list, api_key: str) -> dict:
    user_prompt = (
        "FRASI USATE DI RECENTE (da non ripetere):\n"
        f"{recent_phrases}\n\n"
        "TEMI USATI DI RECENTE (da evitare se possibile):\n"
        f"{recent_topics}"
    )

    # 1. Tentativo Gemini dinamico
    try:
        return _generate_with_gemini(system_prompt, user_prompt, api_key)
    except Exception as err:
        print(f"[phrase_generator] Tutti i modelli Gemini sono falliti ({err}). Passaggio a Groq...")

    # 2. Fallback Groq dinamico
    groq_key = getattr(config, "GROQ_API_KEY", None)
    if groq_key:
        try:
            return _generate_with_groq(system_prompt, user_prompt, groq_key)
        except Exception as err:
            print(f"[phrase_generator] Errore anche con Groq dinamico: {err}")

    raise RuntimeError("Nessun provider AI ha risposto con successo.")

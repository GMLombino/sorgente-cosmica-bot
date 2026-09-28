import json
import re
import time
import config
from google import genai
from groq import Groq


# ============================================================
# UTILITY PARSING JSON
# ============================================================

def _parse_json_response(raw_text: str) -> dict:
    """Converte la risposta del modello in un dizionario Python."""
    if not raw_text:
        raise ValueError("Il modello ha restituito una risposta vuota.")

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
# GEMINI - SCORING & DISCOVERY DINAMICA
# ============================================================

def _score_gemini_model(model_id: str) -> float:
    """
    Calcola un punteggio dinamico di idoneità per il modello.
    Più alto è il punteggio, più il modello è recente e adatto al testo.
    """
    score = 0.0
    name_lower = model_id.lower()

    # 1. Estrazione dinamica della versione (es. '3.8', '3.5')
    version_match = re.search(r"gemini-(\d+(?:\.\d+)?)", name_lower)
    if version_match:
        try:
            version_num = float(version_match.group(1))
            score += version_num * 100.0  # Es. v3.8 -> 380, v3.5 -> 350
        except ValueError:
            pass

    # 2. Bonus per famiglie adatte alla generazione di testo
    if "pro" in name_lower:
        score += 50.0
    elif "flash" in name_lower:
        score += 40.0

    # 3. Penalizzazione per varianti meno idonee o sperimentali
    if "lite" in name_lower:
        score -= 10.0
    if "preview" in name_lower or "exp" in name_lower:
        score -= 5.0

    return score


def _discover_gemini_models(client) -> list:
    """
    Richiede a Google i modelli attivi, filtra quelli non testuali, specialistici
    o deprecati e li ordina dinamicamente dal più performante al meno performante.
    """
    FORBIDDEN_KEYWORDS = [
        "robotics", "image", "audio", "whisper", "tts", 
        "embedding", "imagen", "transcribe", "computer-use", "customtools",
        # Modelli deprecati o ritirati
        "2.5-pro", "2.5-flash", "2.5-flash-lite"
    ]

    valid_models_with_score = []

    try:
        print("[phrase_generator] Interrogazione API Gemini per elenco modelli attivi...")
        models_page = client.models.list()

        for m in models_page:
            model_id = getattr(m, "name", "").replace("models/", "")

            # Filtro 1: Deve essere un modello Gemini
            if "gemini" not in model_id.lower():
                continue

            # Filtro 2: Esclusione di modelli specialistici o deprecati
            if any(forbidden in model_id.lower() for forbidden in FORBIDDEN_KEYWORDS):
                continue

            # Filtro 3: Controllo capability generateContent
            supported_actions = getattr(m, "supported_actions", None)
            if supported_actions and "generateContent" not in supported_actions:
                continue

            # Calcolo del punteggio dinamico
            score = _score_gemini_model(model_id)
            valid_models_with_score.append((model_id, score))

        # Ordinamento decrescente in base al punteggio
        valid_models_with_score.sort(key=lambda x: x[1], reverse=True)

        sorted_models = [m[0] for m in valid_models_with_score]

        print("[phrase_generator] Modelli Gemini idonei ordinati dinamicamente per punteggio:")
        for model, score in valid_models_with_score[:5]:
            print(f"  -> {model} (punteggio: {score})")

        return sorted_models

    except Exception as err:
        print(f"[phrase_generator] Errore durante la discovery Gemini: {err}")
        return []


def _generate_with_gemini(system_prompt: str, user_prompt: str, api_key: str) -> dict:
    client = genai.Client(api_key=api_key)
    models_to_try = _discover_gemini_models(client)

    if not models_to_try:
        raise RuntimeError("Nessun modello Gemini idoneo rilevato dall'API.")

    last_err = None
    for model_name in models_to_try:
        # Fino a 2 tentativi per modello con una breve pausetta per superare picchi temporanei (503/429)
        for attempt in range(2):
            try:
                if attempt > 0:
                    print(f"[phrase_generator] Ritentativo per {model_name} (pausa 3s per rate limit)...")
                    time.sleep(3)

                print(f"[phrase_generator] Gemini: tentativo con {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"{system_prompt}\n\n{user_prompt}",
                )

                if not response.text:
                    raise ValueError("Risposta vuota da Gemini.")

                return _parse_json_response(response.text)

            except Exception as err:
                last_err = err
                err_msg = str(err)
                
                # Se è un problema di domanda/quota temporanea (503 / 429), fa un retry veloce
                if ("503" in err_msg or "429" in err_msg) and attempt == 0:
                    print(f"[phrase_generator] Gemini {model_name} in sovraccarico o rate limit (tentativo 1/2).")
                    continue
                
                print(f"[phrase_generator] Gemini {model_name} non disponibile o fallito: {err}")
                break

    raise last_err or RuntimeError("Nessun modello Gemini ha risposto.")


# ============================================================
# GROQ - DISCOVERY DINAMICA
# ============================================================

def _discover_groq_models(client) -> list:
    """Richiede a Groq i modelli disponibili ed estrae i modelli di chat idonei."""
    valid_models = []

    try:
        print("[phrase_generator] Interrogazione API Groq per elenco modelli attivi...")
        response = client.models.list()

        for m in response.data:
            model_id = getattr(m, "id", "")

            # Escludiamo modelli audio e guardrails
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
# FUNZIONE PRINCIPALE
# ============================================================

def generate_phrase(
    system_prompt: str,
    recent_phrases: list,
    recent_topics: list,
    api_key: str,
) -> dict:
    user_prompt = (
        "FRASI USATE DI RECENTE (da non ripetere):\n"
        f"{recent_phrases}\n\n"
        "TEMI USATI DI RECENTE (da evitare se possibile):\n"
        f"{recent_topics}"
    )

    # 1. Tentativo Gemini dinamico
    try:
        print("[phrase_generator] Avvio generazione con Gemini...")
        return _generate_with_gemini(system_prompt, user_prompt, api_key)
    except Exception as err:
        print(f"[phrase_generator] Tutti i modelli Gemini sono falliti ({err}). Passaggio a Groq...")

    # 2. Fallback Groq dinamico
    groq_key = getattr(config, "GROQ_API_KEY", None)
    if groq_key:
        try:
            print("[phrase_generator] Avvio generazione con Groq...")
            return _generate_with_groq(system_prompt, user_prompt, groq_key)
        except Exception as err:
            print(f"[phrase_generator] Errore anche con Groq dinamico: {err}")

    raise RuntimeError("Nessun provider AI ha risposto con successo.")

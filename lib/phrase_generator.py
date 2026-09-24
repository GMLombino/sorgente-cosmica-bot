import json

import config
from google import genai
from groq import Groq


# ============================================================
# MODELLI CONFIGURATI
# ============================================================

GEMINI_MODELS_TO_TRY = [
    "gemini-2.5-flash",
]

GROQ_MODELS_TO_TRY = [
    "openai/gpt-oss-20b",
]


# ============================================================
# UTILITY
# ============================================================

def _parse_json_response(raw_text: str) -> dict:
    """
    Converte la risposta del modello in un dizionario Python.

    Gestisce anche eventuali blocchi Markdown ```json ... ```.
    """

    if not raw_text:
        raise ValueError(
            "Il modello ha restituito una risposta vuota."
        )

    cleaned_text = raw_text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[
            len("```json"):
        ].strip()

    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[
            len("```"):
        ].strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[
            :-len("```")
        ].strip()

    result = json.loads(cleaned_text)

    if not isinstance(result, dict):
        raise ValueError(
            "La risposta JSON non è un oggetto."
        )

    return result


# ============================================================
# GEMINI
# ============================================================

def _generate_with_gemini(
    system_prompt: str,
    user_prompt: str,
    api_key: str,
) -> dict:
    """
    Tenta la generazione tramite il nuovo SDK google-genai.
    """

    client = genai.Client(
        api_key=api_key
    )

    last_err = None

    for model_name in GEMINI_MODELS_TO_TRY:

        try:
            print(
                f"[phrase_generator] Gemini: "
                f"tentativo con {model_name}..."
            )

            response = client.models.generate_content(
                model=model_name,
                contents=(
                    f"{system_prompt}\n\n"
                    f"{user_prompt}"
                ),
            )

            raw_text = response.text

            return _parse_json_response(
                raw_text
            )

        except Exception as err:

            last_err = err

            print(
                f"[phrase_generator] Gemini "
                f"{model_name} fallito: {err}"
            )

    if last_err is not None:
        raise last_err

    raise RuntimeError(
        "Nessun modello Gemini configurato."
    )


# ============================================================
# GROQ
# ============================================================

def _generate_with_groq(
    system_prompt: str,
    user_prompt: str,
    api_key: str,
) -> dict:
    """
    Fallback su Groq.

    Usa modelli attualmente indicati nella documentazione
    Groq come disponibili e compatibili con JSON mode.
    """

    client = Groq(
        api_key=api_key
    )

    last_err = None

    for model_name in GROQ_MODELS_TO_TRY:

        try:
            print(
                f"[phrase_generator] Groq: "
                f"tentativo con {model_name}..."
            )

            response = client.chat.completions.create(
                model=model_name,
                response_format={
                    "type": "json_object"
                },
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.7,
            )

            raw_text = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            return _parse_json_response(
                raw_text
            )

        except Exception as err:

            last_err = err

            print(
                f"[phrase_generator] Groq "
                f"{model_name} fallito: {err}"
            )

    if last_err is not None:
        raise last_err

    raise RuntimeError(
        "Nessun modello Groq configurato."
    )


# ============================================================
# FUNZIONE PRINCIPALE
# ============================================================

def generate_phrase(
    system_prompt: str,
    recent_phrases: list,
    recent_topics: list,
    api_key: str,
) -> dict:
    """
    Genera una frase con fallback automatico:

    1. Gemini
    2. Groq

    Restituisce un dizionario ottenuto dal JSON del modello.
    """

    user_prompt = (
        "FRASI USATE DI RECENTE "
        "(da non ripetere):\n"
        f"{recent_phrases}\n\n"
        "TEMI USATI DI RECENTE "
        "(da evitare se possibile):\n"
        f"{recent_topics}"
    )

    # --------------------------------------------------------
    # 1. Gemini
    # --------------------------------------------------------

    try:

        print(
            "[phrase_generator] "
            "Tentativo di generazione con Gemini..."
        )

        result = _generate_with_gemini(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key,
        )

        print(
            "[phrase_generator] "
            "Post generato con successo tramite Gemini."
        )

        return result

    except Exception as err:

        print(
            "[phrase_generator] "
            f"Gemini in errore: {err}. "
            "Passaggio a Groq..."
        )

    # --------------------------------------------------------
    # 2. Groq
    # --------------------------------------------------------

    groq_key = getattr(
        config,
        "GROQ_API_KEY",
        None,
    )

    if groq_key:

        try:

            print(
                "[phrase_generator] "
                "Tentativo di generazione con Groq..."
            )

            result = _generate_with_groq(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                api_key=groq_key,
            )

            print(
                "[phrase_generator] "
                "Post generato con successo tramite Groq."
            )

            return result

        except Exception as err:

            print(
                "[phrase_generator] "
                f"ERRORE anche con Groq: {err}"
            )

    else:

        print(
            "[phrase_generator] "
            "GROQ_API_KEY non configurata."
        )

    raise RuntimeError(
        "Tutti i fornitori AI "
        "(Gemini e Groq) hanno risposto con errore."
    )

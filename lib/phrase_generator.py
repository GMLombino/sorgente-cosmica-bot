"""
Generazione della frase quotidiana tramite l'API di testo di Pollinations
(https://text.pollinations.ai/openai, compatibile OpenAI).
"""
import json
import time
import requests

TEXT_ENDPOINT = "https://text.pollinations.ai/openai"


def _build_user_prompt(recent_phrases: list) -> str:
    if not recent_phrases:
        return "Genera la prima frase."
    elenco = "\n".join(f"- {p}" for p in recent_phrases)
    return (
        "Queste sono le frasi già pubblicate di recente: evita di ripeterle "
        "o di generarne di troppo simili nel significato.\n" + elenco
    )


def generate_phrase(system_prompt: str, recent_phrases: list, api_key: str = "",
                     max_retries: int = 3) -> dict:
    """
    Ritorna un dict {"frase": ..., "tema": ...}.
    Solleva un'eccezione se dopo max_retries tentativi non ottiene una risposta valida.
    """
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": _build_user_prompt(recent_phrases)},
        ],
        "temperature": 1.1,
        "max_tokens": 300,
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(TEXT_ENDPOINT, headers=headers, json=payload, timeout=60)
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"HTTP {resp.status_code} da Pollinations: {resp.text[:500]!r}"
                )
            try:
                response_json = resp.json()
            except ValueError as exc:
                raise RuntimeError(
                    f"Risposta non JSON (status {resp.status_code}): {resp.text[:500]!r}"
                ) from exc
            content = response_json["choices"][0]["message"]["content"]
            content = content.strip()
            if not content:
                raise RuntimeError(f"Contenuto vuoto nella risposta: {response_json!r}")
            # Il modello a volte avvolge il JSON in blocchi ```json ... ``` nonostante le istruzioni
            if content.startswith("```"):
                content = content.strip("`")
                content = content.split("\n", 1)[-1] if content.lower().startswith("json") else content
            data = json.loads(content)
            if "frase" in data and data["frase"].strip():
                return {"frase": data["frase"].strip(), "tema": data.get("tema", "").strip()}
            last_error = ValueError(f"Risposta senza campo 'frase' valido: {content!r}")
        except Exception as exc:  # noqa: BLE001 - vogliamo loggare e ritentare qualsiasi errore
            last_error = exc

        wait = 2 ** attempt
        print(f"[phrase_generator] tentativo {attempt} fallito ({last_error}); riprovo tra {wait}s")
        time.sleep(wait)

    raise RuntimeError(f"Generazione frase fallita dopo {max_retries} tentativi: {last_error}")

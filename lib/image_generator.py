"""
Generazione dell'immagine di sfondo tramite l'API immagini di Pollinations
(https://image.pollinations.ai/prompt/{prompt}).
"""
import random
import time
import requests
from urllib.parse import quote

IMAGE_ENDPOINT = "https://image.pollinations.ai/prompt/{prompt}"


def generate_background(prompt: str, width: int, height: int, api_key: str = "",
                         max_retries: int = 3) -> bytes:
    """
    Ritorna i byte dell'immagine generata (jpg/png).
    Usa un seed casuale ad ogni chiamata così lo sfondo varia ogni giorno
    pur partendo dallo stesso prompt di stile.
    """
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    url = IMAGE_ENDPOINT.format(prompt=quote(prompt))
    params = {
        "width": width,
        "height": height,
        "model": "flux",
        "seed": random.randint(1, 10_000_000),
        "nologo": "true",  # richiede un account gratuito registrato per essere onorato
        "safe": "true",
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=120)
            resp.raise_for_status()
            if resp.headers.get("content-type", "").startswith("image/"):
                return resp.content
            last_error = ValueError("La risposta non è un'immagine valida")
        except Exception as exc:  # noqa: BLE001
            last_error = exc

        wait = 2 ** attempt
        print(f"[image_generator] tentativo {attempt} fallito ({last_error}); riprovo tra {wait}s")
        time.sleep(wait)

    raise RuntimeError(f"Generazione immagine fallita dopo {max_retries} tentativi: {last_error}")

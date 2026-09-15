"""
- Carica un file nel repo GitHub pubblico (per ottenere un URL pubblico da dare a Instagram)
- Pubblica un'immagine sull'account Instagram tramite la Graph API
"""
import base64
import time
import requests

GITHUB_API = "https://api.github.com"
GRAPH_API = "https://graph.facebook.com/v21.0"


def _github_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def upload_file_to_github(repo: str, path: str, content_bytes: bytes, token: str,
                            branch: str, commit_message: str) -> str:
    """
    Crea o aggiorna un file nel repo tramite la Contents API.
    Ritorna l'URL raw pubblico del file.
    """
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"
    headers = _github_headers(token)

    # Se il file esiste già (es. history.json), serve lo sha corrente per aggiornarlo
    sha = None
    existing = requests.get(url, headers=headers, params={"ref": branch}, timeout=30)
    if existing.status_code == 200:
        sha = existing.json().get("sha")

    payload = {
        "message": commit_message,
        "content": base64.b64encode(content_bytes).decode("utf-8"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    resp = requests.put(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()

    return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"


def _graph_request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(method, f"{GRAPH_API}/{path}", timeout=60, **kwargs)
    if resp.status_code >= 400:
        raise RuntimeError(f"Errore Graph API ({resp.status_code}): {resp.text}")
    return resp.json()


def publish_image_to_instagram(ig_user_id: str, access_token: str, image_url: str,
                                caption: str, max_wait_seconds: int = 90) -> str:
    """
    Crea il container media, attende che sia pronto, poi lo pubblica.
    Ritorna l'ID del media pubblicato.
    """
    # Stampa di debug temporanea e pulizia stringhe
    clean_token = access_token.strip() if access_token else ""
    clean_user_id = ig_user_id.strip() if ig_user_id else ""

    print(f"[debug] User ID: '{clean_user_id}'")
    print(f"[debug] Token length: {len(clean_token)}, Inizia con: '{clean_token[:10]}...'")

    container = _graph_request(
        "POST",
        f"{clean_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": clean_token,
        },
    )
    container_id = container["id"]

    # Attende che Instagram finisca di scaricare/processare l'immagine
    waited = 0
    while waited < max_wait_seconds:
        status = _graph_request(
            "GET",
            container_id,
            params={"fields": "status_code", "access_token": clean_token},
        )
        code = status.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise RuntimeError(f"Instagram ha segnalato un errore sul container {container_id}")
        time.sleep(5)
        waited += 5

    publish = _graph_request(
        "POST",
        f"{clean_user_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": clean_token,
        },
    )
    return publish["id"]

"""
Modulo principale del bot Instagram per la generazione e pubblicazione di post spirituali.
"""
import io
import json
import os
import sys
import time

import config
from lib import background, compose, phrase_generator, publisher


def load_history() -> list[dict]:
    """Carica lo storico delle frasi e dei post precedenti."""
    if os.path.exists(config.HISTORY_FILE):
        try:
            with open(config.HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:  # noqa: BLE001
            print(f"[main] Errore nel caricamento di {config.HISTORY_FILE}: {exc}")
    return []


def save_history(history: list[dict]) -> None:
    """Salva lo storico aggiornato nel file JSON."""
    try:
        with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"[main] Storico aggiornato in {config.HISTORY_FILE}.")
    except Exception as exc:  # noqa: BLE001
        print(f"[main] Errore nel salvataggio di {config.HISTORY_FILE}: {exc}")


def get_background() -> bytes:
    """
    Pesca uno sfondo casuale dalla cartella assets/backgrounds.
    In caso di cartella vuota o inesistente, usa il colore di fallback specificato in config.
    """
    img = background.get_random_background(
        config.BACKGROUNDS_DIR,
        config.BACKGROUND_COLOR_HEX,
        config.IMAGE_WIDTH,
        config.IMAGE_HEIGHT,
    )

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=95)
    return out.getvalue()


def run() -> None:
    """Esegue il flusso completo del bot: generazione, composizione e pubblicazione."""
    print("=== AVVIO BOT INSTAGRAM ===")

    # 1. Caricamento storico
    history = load_history()
    recent_phrases = [
        item["frase_immagine"]
        for item in history[-config.MAX_HISTORY_PHRASES_IN_PROMPT:]
        if "frase_immagine" in item
    ]
    recent_topics = [
        item["tema"]
        for item in recent_history
        if item.get("tema")
    ]

    # 2. Generazione contenuto via Gemini API
    print("[main] Richiesta frase a Gemini...")
    content = phrase_generator.generate_phrase(
        system_prompt=config.PHRASE_SYSTEM_PROMPT,
        recent_phrases=recent_phrases,
        recent_topics=recent_topics,  # <--- Passiamo anche i temi usati!
        api_key=config.GEMINI_API_KEY,
    )
    print(f"[main] Tema scelto: {content.get('tema', 'Non specificato')}")
    print(f"[main] Frase: {content['frase_immagine']}")

    # 3. Caricamento sfondo dalla cartella
    background_bytes = get_background()

    # 4. Composizione dell'immagine finale con il testo
    print("[main] Composizione immagine in corso...")
    font_body_var = getattr(config, "FONT_BODY_VARIATION", "Regular")
    font_sig_var = getattr(config, "FONT_SIGNATURE_VARIATION", "Regular")

    final_image_bytes = compose.compose_image(
        background_bytes=background_bytes,
        phrase=content["frase_immagine"],
        signature=config.SIGNATURE_TEXT,
        width=config.IMAGE_WIDTH,
        height=config.IMAGE_HEIGHT,
        font_body_path=config.FONT_BODY_PATH,
        font_body_variation=font_body_var,
        font_signature_path=config.FONT_SIGNATURE_PATH,
        font_signature_variation=font_sig_var,
        gold_hex=config.GOLD_HEX,
        white_hex=config.WHITE_HEX,
    )

    # 5. Hosting dell'immagine su GitHub (per URL pubblico)
    print("[main] Caricamento immagine su GitHub Pages/Repository...")
    timestamp = int(time.time())
    target_path = f"generated_posts/post_{timestamp}.jpg"

    public_image_url = publisher.upload_file_to_github(
        repo=config.GITHUB_REPO,
        path=target_path,
        content_bytes=final_image_bytes,
        token=config.GITHUB_TOKEN,
        branch=config.GITHUB_IMAGES_BRANCH,
        commit_message=f"Bot update: generate post {timestamp}",
    )
    print(f"[main] Immagine pubblicata su URL: {public_image_url}")

    # 6. Preparazione della caption per Instagram
    caption = (
        f"{content['spiegazione']}\n\n"
        f"{content['hashtags']}"
    )

    # 7. Pubblicazione su Instagram tramite Graph API
    print("[main] Pubblicazione su Instagram in corso...")
    post_id = publisher.publish_image_to_instagram(
        ig_user_id=config.IG_USER_ID,
        access_token=config.IG_ACCESS_TOKEN,
        image_url=public_image_url,
        caption=caption,
    )
    print(f"[main] Post pubblicato con successo! ID: {post_id}")

    # 8. Aggiornamento e salvataggio dello storico
    new_entry = {
        "post_id": post_id,
        "image_url": public_image_url,
        "frase_immagine": content["frase_immagine"],
        "spiegazione": content["spiegazione"],
        "hashtags": content["hashtags"],
        "tema": content.get("tema", ""),
    }
    history.append(new_entry)
    save_history(history)

    print("=== ESECUZIONE COMPLETATA CON SUCCESSO ===")


if __name__ == "__main__":
    try:
        run()
    except Exception as err:
        print(f"[main] ERRORE FATALE: {err}", file=sys.stderr)
        sys.exit(1)

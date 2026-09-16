"""
Script principale: da lanciare una volta al giorno (via GitHub Actions o cron).

Flusso:
1. Genera una frase (evitando ripetizioni rispetto allo storico)
2. Genera un'immagine di sfondo
3. Sovrappone frase + firma con Pillow
4. Carica l'immagine finale su GitHub (per avere un URL pubblico)
5. Pubblica su Instagram
6. Aggiorna lo storico (in locale e su GitHub)
"""
import sys
from datetime import date

import config
from lib import history, phrase_generator, image_generator, background, compose, publisher


def get_unique_phrase() -> dict:
    """Genera una frase, ritentando se per caso coincide con una già usata."""
    recent = history.recent_phrases(config.HISTORY_FILE, config.MAX_HISTORY_PHRASES_IN_PROMPT)

    for _ in range(3):
        result = phrase_generator.generate_phrase(
            config.PHRASE_SYSTEM_PROMPT, recent, config.GEMINI_API_KEY
        )
        if not history.is_duplicate(config.HISTORY_FILE, result["frase"]):
            return result
        print(f"[main] Frase duplicata generata, riprovo: {result['frase']!r}")

    return result


def get_background() -> bytes:
    """
    Genera lo sfondo secondo la sorgente scelta in config.
    Se la generazione via IA fallisce, ripiega sul locale invece di
    saltare la pubblicazione del giorno.
    """
    if config.BACKGROUND_SOURCE == "ia":
        try:
            data = image_generator.generate_background(
                config.IMAGE_PROMPT_TEMPLATE, config.IMAGE_WIDTH, config.IMAGE_HEIGHT,
                config.POLLINATIONS_API_KEY,
            )
            print("[main] Sfondo generato via IA.")
            return data
        except Exception as exc:  # noqa: BLE001
            print(f"[main] Sfondo IA non disponibile ({exc}); uso lo sfondo locale.")

    data = background.generate_background(
        config.IMAGE_WIDTH, config.IMAGE_HEIGHT, config.BACKGROUND_COLOR_HEX
    )
    print("[main] Sfondo generato in locale.")
    return data


def build_caption(frase: str, spiegazione: str, hashtags: str) -> str:
    """Compone la caption finale per Instagram con frase, spiegazione e hashtag."""
    return f"{frase}\n\n✨ {spiegazione}\n\n.\n.\n{hashtags}"


def run() -> None:
    print("[main] Avvio generazione contenuto del giorno...")

    fraseData = get_unique_phrase()
    
    # Estraiamo i campi ricevuti dal nuovo JSON dell'IA
    # (Se fraseData supporta il fallback per 'frase', gestiamo il controllo duplicati in modo sicuro)
    frase = fraseData.get("frase_immagine") or fraseData.get("frase", "")
    spiegazione = fraseData.get("spiegazione", "")
    hashtags = fraseData.get("hashtags", "")
    tema = fraseData.get("tema", "") # Manteniamo eventuale campo tema per lo storico

    print(f"[main] Frase generata per l'immagine: {frase}")

    sfondo = get_background()

    final_image = compose.compose_image(
        sfondo, frase, config.SIGNATURE_TEXT,
        config.IMAGE_WIDTH, config.IMAGE_HEIGHT,
        config.FONT_BODY_PATH, config.FONT_BODY_VARIATION,
        config.FONT_SIGNATURE_PATH, config.FONT_SIGNATURE_VARIATION,
        config.GOLD_HEX, config.WHITE_HEX,
    )
    print("[main] Immagine finale composta.")

    today_str = date.today().isoformat()
    image_path = f"{config.GITHUB_IMAGES_PATH}/{today_str}.jpg"
    image_url = publisher.upload_file_to_github(
        config.GITHUB_REPO, image_path, final_image, config.GITHUB_TOKEN,
        config.GITHUB_IMAGES_BRANCH, f"Immagine del {today_str}",
    )
    print(f"[main] Immagine caricata: {image_url}")

    # Costruiamo la nuova caption formattata
    caption = build_caption(frase, spiegazione, hashtags)
    
    media_id = publisher.publish_image_to_instagram(
        config.IG_USER_ID, config.IG_ACCESS_TOKEN, image_url, caption,
    )
    print(f"[main] Pubblicato su Instagram, media id: {media_id}")

    history.add_entry(config.HISTORY_FILE, frase, tema)
    with open(config.HISTORY_FILE, "rb") as f:
        publisher.upload_file_to_github(
            config.GITHUB_REPO, config.HISTORY_FILE, f.read(), config.GITHUB_TOKEN,
            config.GITHUB_IMAGES_BRANCH, f"Aggiorna storico - {today_str}",
        )
    print("[main] Storico aggiornato su GitHub.")


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:  # noqa: BLE001
        print(f"[main] ERRORE FATALE: {exc}", file=sys.stderr)
        sys.exit(1)

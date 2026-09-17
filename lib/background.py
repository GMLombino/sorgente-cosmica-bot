"""
Gestione degli sfondi per le immagini: lettura dinamica da cartella locale
o generazione di emergenza in caso di cartella vuota.
"""
from pathlib import Path
import random
from PIL import Image


def get_random_background(backgrounds_dir: str, fallback_hex: str, width: int, height: int) -> Image.Image:
    """
    Legge tutti i file immagine (.jpg, .jpeg, .png, .webp) nella cartella indicata
    e ne restituisce uno a caso, ridimensionandolo a width x height.
    Se la cartella è vuota o non esiste, genera un colore solido di fallback.
    """
    dir_path = Path(backgrounds_dir)
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    
    image_paths = []
    if dir_path.exists() and dir_path.is_dir():
        image_paths = [
            p for p in dir_path.iterdir()
            if p.suffix.lower() in valid_extensions
        ]

    if image_paths:
        selected_path = random.choice(image_paths)
        print(f"[background] Sfondo caricato da file: {selected_path.name}")
        img = Image.open(selected_path).convert("RGB")
        # Ridimensiona e adatta esattamente alle dimensioni target
        return img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Fallback in caso la cartella sia vuota o inesistente
    print(f"[background] Nessuna immagine trovata in '{backgrounds_dir}'. Uso colore fisso {fallback_hex}")
    return Image.new("RGB", (width, height), fallback_hex)

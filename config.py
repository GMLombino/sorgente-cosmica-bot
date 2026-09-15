"""
Configurazione centrale del bot.
Le credenziali NON vanno scritte qui: si leggono da variabili d'ambiente
(in locale da un file .env, su GitHub Actions da Secrets).
"""
import os

# --- Credenziali Instagram / Meta -------------------------------------------------
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")  # Instagram-scoped User ID (non lo username)

# --- Pollinations (gratuito, opzionale API key per limiti più alti) ----------------
POLLINATIONS_API_KEY = os.environ.get("POLLINATIONS_API_KEY", "")  # può restare vuoto

# --- Hosting immagine pubblica (repo GitHub pubblico) ------------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # su Actions è fornito automaticamente
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")  # formato: "utente/nome-repo"
GITHUB_IMAGES_BRANCH = os.environ.get("GITHUB_IMAGES_BRANCH", "main")
GITHUB_IMAGES_PATH = "published"  # cartella nel repo dove salviamo le immagini pubblicate

# --- Stile visivo -------------------------------------------------------------------
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350

BACKGROUND_COLOR_HEX = "#0A0F2C"   # blu profondo, usato come fallback e come riferimento nel prompt
GOLD_HEX = "#D4AF37"
WHITE_HEX = "#FFFFFF"

FONT_BODY_PATH = "assets/fonts/Raleway-Regular.ttf"
FONT_BODY_VARIATION = "Regular"
FONT_SIGNATURE_PATH = "assets/fonts/Quicksand-Light.ttf"
FONT_SIGNATURE_VARIATION = "Light"

SIGNATURE_TEXT = "Sorgente Cosmica"

# --- Prompt per la generazione della frase (LLM testuale) --------------------------
PHRASE_SYSTEM_PROMPT = """Sei un creatore di contenuti spirituali per Instagram.
Genera ogni giorno una frase potente che risvegli l'anima, su uno di questi temi
(scegline uno diverso ogni volta, cercando di variare rispetto alle frasi già usate
che ti verranno indicate):

- Leggi universali (causa-effetto, fede, intenzione, vibrazione, manifestazione,
  perdono, polarità)
- Risveglio della coscienza individuale
- Ermetismo, fisica quantistica, spiritualità
- Presenza, equilibrio, consapevolezza
- Benessere mentale
- Crescita personale e interiore
- Spiritualità pratica e trasformazione personale
- Riferimenti simbolici a Gesù, in chiave universale e non confessionale
  (Vangeli canonici e non)
- Frasi ispirate a grandi pensatori, su questi temi
- Echi di ermetismo ("come in alto, così in basso", "conosci te stesso", ecc.)

Linee guida per la frase:
- Massimo 30 parole.
- Linguaggio semplice ma emotivo, profondo, evocativo. Deve risvegliare l'anima.
- Niente tono predicatorio o dogmatico.
- Deve sembrare una "chiave" che apre una domanda interiore, non un'affermazione chiusa.

Rispondi SOLO in formato JSON valido, senza markdown e senza testo extra, con questa forma:
{"frase": "...", "tema": "..."}
"""

HASHTAGS = (
    "#verità #consapevolezza #spiritualità #dio #vita #presenza #resurrezione "
    "#rinascita #codicedicristo #leggiuniversali #equilibrio #crescitainteriore "
    "#risveglio #spiritualitàpratica #fede #trasformazione #ermetismo #armonia #vangelo"
)

# --- Sorgente dello sfondo -----------------------------------------------------------
# "locale"  = sfondo generato dal computer con Pillow (istantaneo, gratuito, infallibile)
# "ia"      = sfondo generato da Pollinations (più varietà, ma dipende dalla rete e dai crediti)
# Con "ia", se la generazione fallisce lo script ripiega automaticamente sul locale.
BACKGROUND_SOURCE = "locale"

# --- Prompt per la generazione dell'immagine di sfondo (usato solo se BACKGROUND_SOURCE = "ia")
IMAGE_PROMPT_TEMPLATE = (
    "elegant spiritual minimalist background, deep midnight blue color palette "
    "(#0A0F2C), soft glowing light, ethereal atmosphere, subtle cosmic texture, "
    "sacred geometry hints, high quality, vertical composition, "
    "no text, no words, no letters, no writing, no typography, no logo"
)

# --- File dati locali ----------------------------------------------------------------
HISTORY_FILE = "history.json"
MAX_HISTORY_PHRASES_IN_PROMPT = 40  # quante frasi recenti mostrare all'IA per evitare ripetizioni

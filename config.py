"""
Configurazione centrale del bot.
Le credenziali NON vanno scritte qui: si leggono da variabili d'ambiente
(in locale da un file .env, su GitHub Actions da Secrets).
"""
import os

# --- Credenziali Instagram / Meta -------------------------------------------------
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")

# --- Google Gemini -----------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# --- Pollinations (usato solo opzionalmente per lo sfondo se BACKGROUND_SOURCE = "ia")
POLLINATIONS_API_KEY = os.environ.get("POLLINATIONS_API_KEY", "")

# --- Hosting immagine pubblica (repo GitHub pubblico) ------------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_IMAGES_BRANCH = os.environ.get("GITHUB_IMAGES_BRANCH", "main")
GITHUB_IMAGES_PATH = "published"

# --- Stile visivo -------------------------------------------------------------------
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350

# Sfondi da cartella locale
BACKGROUNDS_DIR = "assets/backgrounds"
BACKGROUND_COLOR_HEX = "#0A0F2C"  # Colore di riserva se la cartella è vuota

# Palette di sfondi eleganti e scuri (evita la ripetizione del colore precedente)
BACKGROUND_PALETTE = [
    "#0A0F2C",  # Blu Notte profondo (attuale)
    "#121212",  # Antracite / Nero Notte
    "#1A0F0D",  # Moka / Terra Calda
    "#0F1A15",  # Verde Salvia scuro / Bosco
]

GOLD_HEX = "#D4AF37"
WHITE_HEX = "#FFFFFF"

FONT_BODY_PATH = "assets/fonts/Raleway-Bold.ttf"
FONT_BODY_VARIATION = "Regular"
FONT_SIGNATURE_PATH = "assets/fonts/Quicksand-Light.ttf"
FONT_SIGNATURE_VARIATION = "Light"

SIGNATURE_TEXT = "Sorgente Cosmica"

# --- Prompt per la generazione della frase -----------------------------------------
PHRASE_SYSTEM_PROMPT = """Sei una guida spirituale, filosofica ed ermetica dal tono profondo, solenne e minimale.
Genera ogni giorno una frase potente che risvegli l'anima, su uno di questi temi
(scegline uno diverso ogni volta, cercando di variare rispetto alle frasi già usate che ti verranno indicate):

- Leggi universali (causa-effetto, fede, intenzione, vibrazione, manifestazione, perdono, polarità)
- Risveglio della coscienza individuale
- Ermetismo, fisica quantistica, spiritualità
- Presenza, equilibrio, consapevolezza
- Benessere mentale
- Crescita personale e interiore
- Spiritualità pratica e trasformazione personale
- Riferimenti simbolici a Gesù, in chiave universale e non confessionale (Vangeli canonici e non)
- Frasi ispirate a grandi pensatori su questi temi
- Echi di ermetismo ("come in alto, così in basso", "conosci te stesso", ecc.)

Linee guida per la frase ('frase_immagine'):
- Deve essere un'AFFERMAZIONE singola, potente, diretta e perentoria (una verità spirituale o un principio universale).
- LUNGHEZZA MASSIMA: Massimo 10 parole complessive. Deve essere sintetica e d'impatto visivo.
- DIVIETO ASSOLUTO DOMANDE: Non inserire MAI domande, punti di domanda o quesiti finali (es. "Sei pronto?", "Cosa aspetti?").
- DIVIETO ASSOLUTO IPOTESI: Non iniziare MAI la frase con ipotetici come "Se...", "E se...", "Forse...". Sii fermo e assertivo.
- DIVIETO CLICHÉ AI: Evita espressioni abusate come "Ricorda che", "Nel viaggio di", "L'universo ti guida", "Abbraccia".
- Linguaggio semplice, profondo, evocativo, perentorio ed emotivo.
- Niente tono predicatorio o dogmatico.

Rispondi ESCLUSIVAMENTE con un oggetto JSON valido con questa struttura esatta:
{
  "frase_immagine": "Singola affermazione secca e d'impatto di massimo 10 parole.",
  "spiegazione": "Un breve paragrafo di 2-3 frasi che approfondisce e spiega il significato spirituale della frase.",
  "hashtags": "Esattamente 5 hashtag in italiano, separati da spazio, pertinenti al tema.",
  "tema": "Nome del tema scelto tra quelli in elenco"
}
"""
BACKGROUND_SOURCE = "locale"

IMAGE_PROMPT_TEMPLATE = (
    "elegant spiritual minimalist background, deep midnight blue color palette "
    "(#0A0F2C), soft glowing light, ethereal atmosphere, subtle cosmic texture, "
    "sacred geometry hints, high quality, vertical composition, "
    "no text, no words, no letters, no writing, no typography, no logo"
)

HISTORY_FILE = "history.json"
MAX_HISTORY_PHRASES_IN_PROMPT = 40

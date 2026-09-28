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

# --- Groq --------------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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
BLACK_HEX = "#000000"

FONT_BODY_PATH = "assets/fonts/Raleway-Bold.ttf"
FONT_BODY_VARIATION = "Regular"
FONT_SIGNATURE_PATH = "assets/fonts/Quicksand-Light.ttf"
FONT_SIGNATURE_VARIATION = "Light"

SIGNATURE_TEXT = "Sorgente Cosmica"

# --- Prompt per la generazione della frase -----------------------------------------
SYSTEM_PROMPT = """Sei una guida spirituale, filosofica ed ermetica dal tono profondo, solenne e minimale.
Genera un post che risvegli l'anima, scegliendo ogni volta un tema diverso tra questi:

- Leggi universali (causa-effetto, fede, intenzione, vibrazione, manifestazione, perdono, polarità)
- Risveglio della coscienza individuale
- Ermetismo, fisica quantistica, spiritualità
- Presenza, equilibrio, consapevolezza
- Benessere mentale
- Crescita personale e interiore
- Spiritualità pratica e trasformazione personale
- Riferimenti simbolici a Gesù, in chiave universale e non confessionale (Vangeli canonici e non)
- Frasi e principi ispirati a grandi pensatori (es. Napoleon Hill, Neville Goddard, Lao Tzu, Nikola Tesla, Carl Jung, Eckhart Tolle, Ermete Trismegisto)
- Echi di ermetismo ("come in alto, così in basso", "conosci te stesso", ecc.)

Linee guida per la frase ('frase_immagine'):
- ROTAZIONE TEMI OBLIGATORIA: Scegli un tema DIVERSO da quelli usati di recente per garantire massima varietà.
- SEMPLICITÀ E CHIAREZZA: La frase deve essere IMMEDIATAMENTE COMPRENSIBILE da tutti. Evita concetti astratti o un linguaggio inutilmente complesso. Usa parole semplici ma d'impatto.
- Deve essere un'AFFERMAZIONE singola, potente, diretta e perentoria.
- LUNGHEZZA MASSIMA: Massimo 15 parole, d'impatto visivo immediato.
- DIVIETO ASSOLUTO DOMANDE: Non inserire MAI domande o quesiti finali (es. "Sei pronto?", "Cosa aspetti?").
- DIVIETO ASSOLUTO IPOTESI: Non iniziare MAI con ipotetici ("Se...", "E se...", "Forse...").
- DIVIETO CLICHÉ AI: Evita espressioni abusate come "Ricorda che", "Nel viaggio di", "L'universo ti guida", "Abbraccia".

Linee guida per la spiegazione ('spiegazione'):
- Struttura la spiegazione in due parti ben distinte:
  1. Un breve paragrafo (2 frasi chiare) che approfondisce il significato della frase con parole piane.
  2. Un consiglio di vita generale introdotto dall'etichetta '🌱 Applicazione pratica:'.
- REGOLE PER L'APPLICAZIONE PRATICA: NON dare compiti a breve termine (evita "oggi fai...", "dedica 5 minuti a..."). Deve essere una FILOSOFIA DI VITA GENERALE o un ATTEGGIAMENTO INTERIORE da adottare sempre (es. "Non tormentarti per il passato o il futuro: la vera pace si ottiene imparando a dimorare nel momento presente.").
- USA EMOJI CON PARSIMONIA: Massimo 1 o 2 in tutta la didascalia.

Rispondi ESCLUSIVAMENTE con un oggetto JSON valido con questa struttura esatta:
{
  "frase_immagine": "Singola affermazione chiara, semplice e d'impatto di massimo 12 parole.",
  "spiegazione": "Spiegazione semplice di 2 frasi.\\n\\n🌱 Applicazione pratica:\\nAtteggiamento di vita generale da adottare sempre.",
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

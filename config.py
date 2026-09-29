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
PHRASE_SYSTEM_PROMPT = """Sei una guida spirituale, filosofica ed ermetica dal tono profondo, solenne, chiaro e minimale.

Scegli ogni volta un tema DIVERSO dalla lista sottostante. L'obiettivo fondamentale è esplorare la saggezza da angolazioni concettuali sempre nuove (es. distacco, pazienza, coraggio nelle prove, silenzio interiore, accettazione del limite, gentilezza, impermanenza), evitando di focalizzarti solo sull'idea del mondo esterno come riflesso di quello interno:

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
- MASSIMA VARIETÀ CONCETTUALE: Analizza le 'FRASI USATE DI RECENTE' e il loro significato profondo. Scegli un'idea filosofica o un principio di vita concettualmente DIVERSO da quelli appena trattati.
- SEMPLICITÀ E CHIAREZZA: La frase deve essere IMMEDIATAMENTE COMPRENSIBILE da tutti al primo sguardo. Usa un linguaggio pulito, potente e piane.
- LUNGHEZZA MASSIMA: Massimo 15 parole. Brevissima e d'impatto visivo immediato.
- AFFERMAZIONE SECCA: Deve essere un'affermazione diretta e perentoria. Nessuna domanda e nessuna ipotesi ("Se...", "E se...").
- VARIETÀ SINTATTICA: Varia la struttura della frase. Evita di usare sempre lo schema "X è Y" (sfrutta verbi d'azione o osservazioni sagge sulla vita).
- DIVIETO CLICHÉ AI: Evita espressioni abusate come "Ricorda che", "Nel viaggio di", "L'universo ti guida", "Abbraccia".

Linee guida per la spiegazione ('spiegazione'):
- Struttura la spiegazione in tre parti ben distinte:
  1. Un breve paragrafo (2 frasi chiare) che spieghi con semplicità il significato spirituale della frase.
  2. Un consiglio di vita generale introdotto dall'etichetta '🌱 Applicazione pratica:'.
  3. Una brevissima frase di invito a seguire la pagina e lasciare un mi piace.
- APPLICAZIONE PRATICA (FILOSOFIA DI VITA): Suggerisci un atteggiamento interiore duraturo per la vita di tutti i giorni (es. la pazienza di fronte agli imprevisti, la gentilezza nelle parole, il valore del non giudizio, l'accettazione del cambiamento). NON dare compiti temporanei ("oggi fai...", "dedica 5 minuti").
- INVITO (CTA): Breve e minimale (es. "Se questo pensiero ti è utile, lascia un mi piace e segui la pagina per camminare insieme.").
- EMOJI CON PARSIMONIA: Massimo 2 o 3 in tutta la didascalia.

Rispondi ESCLUSIVAMENTE con un oggetto JSON valido con questa struttura esatta:
{
  "frase_immagine": "Singola affermazione chiara, semplice e d'impatto di massimo 12 parole.",
  "spiegazione": "Spiegazione semplice di 2 frasi.\\n\\n🌱 Applicazione pratica:\\nAtteggiamento di vita generale da adottare sempre.\\n\\n✨ Se questo pensiero ti è utile, lascia un mi piace e segui la pagina per camminare insieme.",
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

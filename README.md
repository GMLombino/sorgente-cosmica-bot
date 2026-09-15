# Bot Instagram — frasi spirituali generate con IA

Ogni giorno genera una frase spirituale + un'immagine di sfondo, le compone insieme,
e pubblica il risultato su Instagram. Completamente gratuito.

## Come funziona

1. **Frase**: generata con l'API di testo di Pollinations.ai (serve una API key gratuita),
   evitando ripetizioni rispetto allo storico (`history.json`).
2. **Sfondo**: generato **in locale** con Pillow — blu profondo, sfumatura morbida, accenno
   di nebulosa e stelle. Nessuna chiamata di rete, quindi istantaneo e senza consumo di crediti.
   Ogni giorno varia leggermente (posizione della luce, stelle, sfumature) mantenendo lo stesso stile.
   In `config.py` puoi impostare `BACKGROUND_SOURCE = "ia"` per farlo generare invece da Pollinations:
   in quel caso, se la chiamata fallisce, lo script ripiega automaticamente sullo sfondo locale.
3. **Composizione**: la frase e la firma "Sorgente Cosmica" vengono disegnate sopra lo sfondo
   con Pillow (font Raleway per il testo, Quicksand per la firma).
4. **Pubblicazione**: l'immagine finale viene caricata nel repo GitHub (per avere un URL pubblico)
   e pubblicata su Instagram tramite la Graph API.
5. **Storico**: ogni frase pubblicata viene salvata in `history.json` per non ripetersi.

## Setup

### 1. Crea il repository su GitHub

Carica questi file in un **repository pubblico** (deve essere pubblico perché le immagini
vengano servite tramite `raw.githubusercontent.com` — un repo privato non funzionerebbe
per questo scopo senza costi aggiuntivi).

### 2. Configura i Secrets del repository

Vai su **Settings → Secrets and variables → Actions → New repository secret** e aggiungi:

| Nome secret            | Valore                                                          |
| ----------------------- | ---------------------------------------------------------------- |
| `IG_ACCESS_TOKEN`       | Il token generato nella dashboard Meta (API setup con Instagram Login) |
| `IG_USER_ID`            | L'Instagram User ID collegato al token (visibile nella stessa schermata) |
| `POLLINATIONS_API_KEY`  | **Necessaria.** Chiave gratuita da enter.pollinations.ai (registrazione con email, niente carta di credito). Le richieste anonime da GitHub Actions falliscono perché l'IP è condiviso con molti altri progetti e la quota anonima risulta esaurita. |

Non serve creare un secret per `GITHUB_TOKEN`: GitHub Actions lo fornisce automaticamente
ad ogni esecuzione, con permessi di scrittura sul repo (già abilitati nel workflow).

### 3. Personalizza l'orario di pubblicazione

Nel file `.github/workflows/daily-post.yml`, modifica la riga `cron` con l'orario UTC
desiderato (il commento nel file spiega la conversione da/verso l'ora italiana).

### 4. Test manuale

Prima di affidarti allo scheduling automatico, vai su **Actions → Pubblicazione giornaliera
Instagram → Run workflow** per lanciarlo manualmente una volta e verificare che tutto funzioni.

### 5. Rinnovo del token (ogni ~60 giorni)

Il token Instagram generato dalla dashboard è a lunga durata (60 giorni) ma scade.
Segnati la data di generazione e rigeneralo manualmente dalla stessa schermata Meta
prima della scadenza, aggiornando il secret `IG_ACCESS_TOKEN`.

## Esecuzione in locale (per test)

```bash
pip install -r requirements.txt

export IG_ACCESS_TOKEN="..."
export IG_USER_ID="..."
export GITHUB_TOKEN="..."      # un Personal Access Token con permessi "repo"
export GITHUB_REPO="tuo-utente/tuo-repo"
export GITHUB_IMAGES_BRANCH="main"

python main.py
```

## Personalizzare il tema

Il tema, le linee guida per la frase e gli hashtag si modificano in `config.py`,
nella variabile `PHRASE_SYSTEM_PROMPT`. Lo stile visivo (colori, font, layout)
si modifica nelle variabili più in basso nello stesso file.

"""
Composizione dell'immagine finale: sfondo generato dall'IA + frase + firma,
disegnati con Pillow per un risultato tipografico controllato e coerente.
"""
import io
from itertools import combinations

import config

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageStat,
)


# ============================================================
# FONT
# ============================================================

def _load_variable_font(size):
    """
    Carica il font configurato in config.py.
    """
    return ImageFont.truetype(config.FONT_PATH, size=size)


# ============================================================
# UTILITY TESTO
# ============================================================

def _text_width(draw, text, font):
    """
    Restituisce la larghezza effettiva del testo.
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _text_height(draw, text, font):
    """
    Restituisce l'altezza effettiva del testo.
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


# ============================================================
# CONVERSIONE COLORI
# ============================================================

def _hex_to_rgba(hex_color, alpha=255):
    """
    Converte un colore HEX (#RRGGBB oppure RRGGBB)
    in una tupla RGBA.
    """
    value = hex_color.strip().lstrip("#")

    if len(value) != 6:
        raise ValueError(
            f"Colore HEX non valido: {hex_color}"
        )

    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
        alpha,
    )


# ============================================================
# WRAPPING BILANCIATO
# ============================================================

def _make_balanced_lines(
    draw,
    text,
    font,
    max_width,
    max_lines=3,
):
    """
    Cerca una suddivisione del testo visivamente equilibrata.

    La funzione:
    - prova una riga se possibile;
    - prova tutte le divisioni possibili a 2 e 3 righe;
    - privilegia righe di lunghezza equilibrata;
    - penalizza le righe troppo corte;
    - dà un piccolo bonus alle divisioni dopo la punteggiatura.

    Non forza mai una divisione se questa rende il testo
    troppo largo per il limite disponibile.
    """

    words = text.split()

    if not words:
        return []

    # --------------------------------------------------------
    # Una sola riga
    # --------------------------------------------------------

    one_line = " ".join(words)

    if _text_width(draw, one_line, font) <= max_width:
        return [one_line]

    # --------------------------------------------------------
    # Funzione di scoring
    # --------------------------------------------------------

    def punctuation_bonus(left, right):
        """
        Piccolo bonus se la divisione cade dopo una pausa naturale.
        """
        stripped = left.rstrip()

        if not stripped:
            return 0

        if stripped.endswith((",", ";", ":", "—", "-", ".", "!", "?")):
            return 0.12

        return 0

    def score(lines):
        widths = [
            _text_width(draw, line, font)
            for line in lines
        ]

        # Se una riga supera il limite, soluzione non valida.
        if any(width > max_width for width in widths):
            return None

        max_w = max(widths)
        min_w = min(widths)

        # Quanto sono equilibrate le righe.
        imbalance = (max_w - min_w) / max(max_w, 1)

        # Penalizza righe eccessivamente corte.
        short_penalty = 0

        if len(lines) > 1:
            for width in widths:
                ratio = width / max(max_w, 1)

                if ratio < 0.45:
                    short_penalty += (0.45 - ratio)

        # Penalizza leggermente l'uso insufficiente dello spazio.
        average_width = sum(widths) / len(widths)
        unused_space = 1 - (
            average_width / max(max_width, 1)
        )

        punctuation = 0

        for i in range(len(lines) - 1):
            punctuation += punctuation_bonus(
                lines[i],
                lines[i + 1],
            )

        return (
            imbalance
            + short_penalty * 0.8
            + unused_space * 0.20
            - punctuation
        )

    # --------------------------------------------------------
    # Due / tre righe
    # --------------------------------------------------------

    best_lines = None
    best_score = None

    for line_count in range(2, max_lines + 1):

        if len(words) < line_count:
            continue

        # Posizioni possibili delle divisioni.
        for cuts in combinations(
            range(1, len(words)),
            line_count - 1,
        ):
            positions = (0,) + cuts + (len(words),)

            lines = []

            for i in range(len(positions) - 1):
                start = positions[i]
                end = positions[i + 1]

                line = " ".join(words[start:end])
                lines.append(line)

            current_score = score(lines)

            if current_score is None:
                continue

            if best_score is None or current_score < best_score:
                best_score = current_score
                best_lines = lines

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if best_lines is not None:
        return best_lines

    # Se nessuna combinazione è valida, wrapping semplice.
    lines = []
    current = ""

    for word in words:

        candidate = (
            word
            if not current
            else current + " " + word
        )

        if _text_width(draw, candidate, font) <= max_width:
            current = candidate

        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


# ============================================================
# FONT + WRAPPING
# ============================================================

def _fit_font_and_wrap(
    draw,
    text,
    max_width,
    max_height,
    start_size=90,
    min_size=38,
    max_lines=3,
):
    """
    Cerca automaticamente la dimensione del font e
    una suddivisione del testo compatibile con lo spazio.
    """

    for size in range(start_size, min_size - 1, -1):

        font = _load_variable_font(size)

        lines = _make_balanced_lines(
            draw,
            text,
            font,
            max_width,
            max_lines=max_lines,
        )

        if not lines:
            continue

        line_height = int(
            _text_height(draw, "Ag", font) * 1.18
        )

        total_height = (
            line_height * len(lines)
        )

        if total_height <= max_height:
            return (
                font,
                lines,
                line_height,
                total_height,
            )

    # Fallback minimo.
    font = _load_variable_font(min_size)

    lines = _make_balanced_lines(
        draw,
        text,
        font,
        max_width,
        max_lines=max_lines,
    )

    line_height = int(
        _text_height(draw, "Ag", font) * 1.18
    )

    total_height = line_height * len(lines)

    return (
        font,
        lines,
        line_height,
        total_height,
    )


# ============================================================
# LUMINOSITÀ
# ============================================================

def _get_brightness(image, box):
    """
    Calcola la luminosità media dell'area indicata.

    Il box viene prima limitato ai bordi reali dell'immagine,
    evitando che Image.crop() introduca aree nere artificiali.
    """

    width, height = image.size

    x1, y1, x2, y2 = box

    x1 = max(0, min(width, int(x1)))
    y1 = max(0, min(height, int(y1)))
    x2 = max(0, min(width, int(x2)))
    y2 = max(0, min(height, int(y2)))

    # Box non valido.
    if x2 <= x1 or y2 <= y1:
        return 0

    crop = image.crop(
        (x1, y1, x2, y2)
    )

    grayscale = crop.convert("L")

    stat = ImageStat.Stat(grayscale)

    return stat.mean[0]


# ============================================================
# OVERLAY LOCALIZZATO
# ============================================================

def _create_text_overlay(
    image,
    text_box,
    opacity,
    padding_x=45,
    padding_y=30,
    radius=28,
):
    """
    Crea un supporto scuro localizzato intorno al testo.

    Non crea più una fascia orizzontale sull'intera immagine.
    """

    if opacity <= 0:
        return None

    width, height = image.size

    x1, y1, x2, y2 = text_box

    x1 -= padding_x
    y1 -= padding_y
    x2 += padding_x
    y2 += padding_y

    # Clamp ai bordi.
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(width, int(x2))
    y2 = min(height, int(y2))

    if x2 <= x1 or y2 <= y1:
        return None

    overlay = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(overlay)

    draw.rounded_rectangle(
        (x1, y1, x2, y2),
        radius=radius,
        fill=(0, 0, 0, opacity),
    )

    # Sfocatura morbida per evitare l'effetto "riquadro".
    overlay = overlay.filter(
        ImageFilter.GaussianBlur(18)
    )

    return overlay


# ============================================================
# PARAMETRI IN BASE ALLA LUMINOSITÀ
# ============================================================

def _params_for_brightness(
    brightness,
    gold_color,
    white_color,
):
    """
    Determina:
    - colore del testo
    - opacità dell'overlay
    - colore/intensità dell'ombra

    I colori vengono ricevuti dall'esterno, quindi
    GOLD_HEX / WHITE_HEX di config.py restano realmente
    configurabili.
    """

    if brightness >= 170:

        return {
            "overlay_opacity": 115,
            "text_color": white_color,
            "shadow_color": (0, 0, 0, 175),
        }

    elif brightness >= 135:

        return {
            "overlay_opacity": 85,
            "text_color": gold_color,
            "shadow_color": (0, 0, 0, 160),
        }

    elif brightness >= 95:

        return {
            "overlay_opacity": 50,
            "text_color": gold_color,
            "shadow_color": (0, 0, 0, 145),
        }

    else:

        # Sfondo sufficientemente scuro:
        # niente overlay.
        return {
            "overlay_opacity": 0,
            "text_color": gold_color,
            "shadow_color": (0, 0, 0, 125),
        }


# ============================================================
# COMPOSIZIONE PRINCIPALE
# ============================================================

def compose_image(
    background,
    phrase,
    signature=None,
    gold_hex=None,
    white_hex=None,
):
    """
    Compone l'immagine finale.

    Parametri:
        background:
            PIL.Image oppure bytes dell'immagine.

        phrase:
            Frase generata dall'AI.

        signature:
            Firma opzionale.

        gold_hex:
            Colore principale configurabile.

        white_hex:
            Colore chiaro configurabile.

    Ritorna:
        PIL.Image RGB pronta per il salvataggio.
    """

    # --------------------------------------------------------
    # COLORI
    # --------------------------------------------------------

    if gold_hex is None:
        gold_hex = config.GOLD_HEX

    if white_hex is None:
        white_hex = config.WHITE_HEX

    gold_color = _hex_to_rgba(
        gold_hex,
        alpha=255,
    )

    white_color = _hex_to_rgba(
        white_hex,
        alpha=255,
    )

    # --------------------------------------------------------
    # CARICAMENTO BACKGROUND
    # --------------------------------------------------------

    if isinstance(background, Image.Image):
        image = background.convert("RGB")

    else:
        image = Image.open(
            io.BytesIO(background)
        ).convert("RGB")

    # --------------------------------------------------------
    # DIMENSIONI
    # --------------------------------------------------------

    target_width = config.IMAGE_WIDTH
    target_height = config.IMAGE_HEIGHT

    image = image.resize(
        (target_width, target_height),
        Image.Resampling.LANCZOS,
    )

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    draw = ImageDraw.Draw(image)

    width, height = image.size

    # Margine laterale.
    margin = int(width * 0.10)

    max_text_width = width - (
        margin * 2
    )

    # Limiti verticali del testo.
    max_text_height = int(
        height * 0.32
    )

    # --------------------------------------------------------
    # FONT E RIGHE
    # --------------------------------------------------------

    (
        font,
        lines,
        line_height,
        total_text_height,
    ) = _fit_font_and_wrap(
        draw,
        phrase,
        max_width=max_text_width,
        max_height=max_text_height,
        start_size=90,
        min_size=38,
        max_lines=3,
    )

    # --------------------------------------------------------
    # POSIZIONE CENTRALE
    # --------------------------------------------------------

    center_x = width / 2
    center_y = height * 0.50

    start_y = int(
        center_y
        - total_text_height / 2
    )

    # --------------------------------------------------------
    # BOUNDING BOX REALE DEL TESTO
    # --------------------------------------------------------

    text_width = 0

    for line in lines:
        text_width = max(
            text_width,
            _text_width(
                draw,
                line,
                font,
            ),
        )

    text_box = (
        int(center_x - text_width / 2),
        int(start_y),
        int(center_x + text_width / 2),
        int(start_y + total_text_height),
    )

    # --------------------------------------------------------
    # LUMINOSITÀ LOCALE
    # --------------------------------------------------------

    brightness = _get_brightness(
        image,
        text_box,
    )

    params = _params_for_brightness(
        brightness,
        gold_color,
        white_color,
    )

    # --------------------------------------------------------
    # OVERLAY LOCALE
    # --------------------------------------------------------

    overlay = _create_text_overlay(
        image,
        text_box,
        params["overlay_opacity"],
        padding_x=45,
        padding_y=30,
        radius=28,
    )

    if overlay is not None:
        image = Image.alpha_composite(
            image.convert("RGBA"),
            overlay,
        ).convert("RGB")

        draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # TESTO
    # --------------------------------------------------------

    current_y = start_y

    for line in lines:

        line_width = _text_width(
            draw,
            line,
            font,
        )

        x = int(
            center_x - line_width / 2
        )

        # Ombra morbida, senza stroke pesante.
        draw.text(
            (
                x + 2,
                current_y + 3,
            ),
            line,
            font=font,
            fill=params["shadow_color"],
        )

        draw.text(
            (
                x,
                current_y,
            ),
            line,
            font=font,
            fill=params["text_color"],
        )

        current_y += line_height

    # ========================================================
    # FIRMA
    # ========================================================

    if signature:

        sig_font = _load_variable_font(30)

        sig_bbox = draw.textbbox(
            (0, 0),
            signature,
            font=sig_font,
        )

        sig_width = (
            sig_bbox[2] - sig_bbox[0]
        )

        sig_height = (
            sig_bbox[3] - sig_bbox[1]
        )

        sig_x = int(
            center_x - sig_width / 2
        )

        sig_y = int(
            height * 0.90
        )

        # Box reale della firma.
        sig_box = (
            sig_x,
            sig_y,
            sig_x + sig_width,
            sig_y + sig_height,
        )

        # ----------------------------------------------------
        # Luminosità locale firma
        # ----------------------------------------------------

        sig_brightness = _get_brightness(
            image,
            sig_box,
        )

        sig_params = _params_for_brightness(
            sig_brightness,
            gold_color,
            white_color,
        )

        # Firma più discreta:
        # overlay ridotto rispetto alla frase.
        sig_overlay_opacity = int(
            sig_params["overlay_opacity"] * 0.65
        )

        sig_overlay = _create_text_overlay(
            image,
            sig_box,
            sig_overlay_opacity,
            padding_x=20,
            padding_y=12,
            radius=18,
        )

        if sig_overlay is not None:

            image = Image.alpha_composite(
                image.convert("RGBA"),
                sig_overlay,
            ).convert("RGB")

            draw = ImageDraw.Draw(image)

        # ----------------------------------------------------
        # Disegno firma
        # ----------------------------------------------------

        draw.text(
            (
                sig_x + 1,
                sig_y + 2,
            ),
            signature,
            font=sig_font,
            fill=sig_params["shadow_color"],
        )

        draw.text(
            (
                sig_x,
                sig_y,
            ),
            signature,
            font=sig_font,
            fill=sig_params["text_color"],
        )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    return image.convert("RGB")


# ============================================================
# SALVATAGGIO
# ============================================================

def save_composed_image(
    image,
    output_path,
):
    """
    Salva l'immagine JPEG finale.
    """

    image.save(
        output_path,
        format="JPEG",
        quality=95,
        optimize=True,
    )

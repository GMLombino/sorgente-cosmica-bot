"""
Composizione dell'immagine finale: sfondo generato dall'IA + frase + firma,
disegnati con Pillow per un risultato tipografico controllato e coerente.
"""
import io
import config
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def _load_variable_font(path: str, size: int, variation_name: str) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(path, size)
    try:
        font.set_variation_by_name(variation_name)
    except Exception:
        pass  # se il font non supporta varianti, si usa il default
    return font


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
               max_width: int) -> list:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_font_and_wrap(draw, text, font_path, variation, max_width, max_height,
                       start_size=64, min_size=28):
    """Riduce la dimensione del font finché il testo (a capo) non entra nell'area disponibile."""
    size = start_size
    while size >= min_size:
        font = _load_variable_font(font_path, size, variation)
        lines = _wrap_text(draw, text, font, max_width)
        line_height = draw.textbbox((0, 0), "Ag", font=font)[3] * 1.35
        total_height = line_height * len(lines)
        if total_height <= max_height:
            return font, lines, line_height
        size -= 4
    # fallback: ritorna comunque l'ultima versione, anche se un po' stretta
    return font, lines, line_height


def compose_image(background_bytes: bytes, phrase: str, signature: str,
                   width: int, height: int,
                   font_body_path: str, font_body_variation: str,
                   font_signature_path: str, font_signature_variation: str,
                   gold_hex: str, white_hex: str) -> bytes:
    base = Image.open(io.BytesIO(background_bytes)).convert("RGB")
    base = base.resize((width, height))

    # Overlay scuro semi-trasparente potenziato (da 90 a 130 d'opacità)
    # per garantire massima leggibilità anche su cieli molto chiari.
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    gradient_top = int(height * 0.30)
    gradient_bottom = int(height * 0.78)
    overlay_draw.rectangle([0, gradient_top, width, gradient_bottom], fill=(10, 15, 44, 130))
    overlay = overlay.filter(ImageFilter.GaussianBlur(40))

    base = base.convert("RGBA")
    base.alpha_composite(overlay)
    draw = ImageDraw.Draw(base)

    margin_x = int(width * 0.12)
    max_text_width = width - 2 * margin_x
    max_text_height = int(height * 0.40)

    font, lines, line_height = _fit_font_and_wrap(
        draw, phrase, font_body_path, font_body_variation,
        max_text_width, max_text_height,
    )

    total_text_height = line_height * len(lines)
    text_block_center_y = height * 0.52
    start_y = text_block_center_y - total_text_height / 2

    y = start_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) / 2
        # Aggiunto stroke_width=2 e stroke_fill scuro per contornare le lettere
        draw.text(
            (x, y), 
            line, 
            font=font, 
            fill=gold_hex, 
            stroke_width=2, 
            stroke_fill=(15, 10, 5)
        )
        y += line_height

    # Firma fissa, sempre in basso centrata (aggiunto piccolo stroke anche alla firma per uniformità)
    sig_font = _load_variable_font(font_signature_path, 34, font_signature_variation)
    sig_bbox = draw.textbbox((0, 0), signature, font=sig_font)
    sig_width = sig_bbox[2] - sig_bbox[0]
    sig_y = height * 0.90
    draw.text(
        ((width - sig_width) / 2, sig_y), 
        signature, 
        font=sig_font, 
        fill=config.BLACK_HEX,
        stroke_width=1,
        stroke_fill=(255, 255, 255)
    )

    out = io.BytesIO()
    base.convert("RGB").save(out, format="JPEG", quality=92)
    return out.getvalue()

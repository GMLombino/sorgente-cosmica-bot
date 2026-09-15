"""
Generazione dello sfondo in locale con Pillow: nessuna chiamata di rete,
istantanea e gratuita. Blu profondo con un accenno di luminosità e stelle.
"""
import io
import math
import random

from PIL import Image, ImageDraw, ImageFilter


def _hex_to_rgb(value: str) -> tuple:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _vertical_gradient(width: int, height: int, top_rgb: tuple, bottom_rgb: tuple) -> Image.Image:
    """Sfumatura verticale morbida tra due tonalità di blu."""
    gradient = Image.new("RGB", (1, height))
    draw = ImageDraw.Draw(gradient)
    for y in range(height):
        t = y / max(height - 1, 1)
        # curva morbida, evita una transizione troppo lineare/artificiale
        t = t * t * (3 - 2 * t)
        color = tuple(
            int(top_rgb[i] + (bottom_rgb[i] - top_rgb[i]) * t) for i in range(3)
        )
        draw.point((0, y), fill=color)
    return gradient.resize((width, height))


def _add_glow(image: Image.Image, center: tuple, radius: int, color: tuple,
               intensity: int) -> Image.Image:
    """Alone luminoso diffuso, per dare profondità senza disegnare forme nette."""
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse(
        [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
        fill=color + (intensity,),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 2))
    image = image.convert("RGBA")
    image.alpha_composite(glow)
    return image


def _add_stars(image: Image.Image, count: int, seed: int) -> Image.Image:
    """Stelle sottili sparse, di dimensione e luminosità variabili."""
    rng = random.Random(seed)
    stars = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(stars)
    width, height = image.size

    for _ in range(count):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        size = rng.choice([1, 1, 1, 2, 2, 3])
        alpha = rng.randint(60, 210)
        tint = rng.choice([
            (255, 255, 255),
            (255, 250, 235),
            (220, 230, 255),
            (212, 175, 55),  # qualche stella dorata, in richiamo al colore del testo
        ])
        draw.ellipse([x, y, x + size, y + size], fill=tint + (alpha,))

    # leggerissima sfocatura: le stelle non devono sembrare pixel netti
    stars = stars.filter(ImageFilter.GaussianBlur(0.4))
    image = image.convert("RGBA")
    image.alpha_composite(stars)
    return image


def _add_nebula(image: Image.Image, seed: int) -> Image.Image:
    """Accenno di nebulosa: due o tre macchie molto diffuse e poco visibili."""
    rng = random.Random(seed + 1)
    width, height = image.size
    nebula = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(nebula)

    palette = [
        (40, 60, 130),
        (70, 50, 120),
        (30, 80, 130),
    ]

    for _ in range(rng.randint(2, 3)):
        cx = rng.randint(0, width)
        cy = rng.randint(int(height * 0.1), int(height * 0.9))
        rx = rng.randint(int(width * 0.25), int(width * 0.55))
        ry = rng.randint(int(height * 0.12), int(height * 0.28))
        angle = rng.uniform(0, math.pi)
        color = rng.choice(palette)

        patch = Image.new("RGBA", (rx * 2, ry * 2), (0, 0, 0, 0))
        ImageDraw.Draw(patch).ellipse([0, 0, rx * 2, ry * 2], fill=color + (46,))
        patch = patch.rotate(math.degrees(angle), expand=True)
        nebula.alpha_composite(patch, (cx - patch.width // 2, cy - patch.height // 2))

    nebula = nebula.filter(ImageFilter.GaussianBlur(90))
    image = image.convert("RGBA")
    image.alpha_composite(nebula)
    return image


def generate_background(width: int, height: int, base_hex: str, seed: int = None) -> bytes:
    """
    Crea lo sfondo completo e ritorna i byte JPEG.
    Il seed rende ogni giorno leggermente diverso pur mantenendo lo stile.
    """
    if seed is None:
        seed = random.randint(1, 10_000_000)
    rng = random.Random(seed)

    base_rgb = _hex_to_rgb(base_hex)
    # tonalità leggermente più chiara in alto, più scura in basso
    top_rgb = tuple(min(255, c + rng.randint(8, 20)) for c in base_rgb)
    bottom_rgb = tuple(max(0, c - rng.randint(2, 6)) for c in base_rgb)

    image = _vertical_gradient(width, height, top_rgb, bottom_rgb)
    image = _add_nebula(image, seed)

    # un alone luminoso principale, posizionato in alto in modo variabile
    glow_x = rng.randint(int(width * 0.2), int(width * 0.8))
    glow_y = rng.randint(int(height * 0.08), int(height * 0.28))
    image = _add_glow(image, (glow_x, glow_y), int(width * 0.45), (150, 180, 255), 30)

    image = _add_stars(image, count=rng.randint(70, 110), seed=seed)

    # vignettatura leggera: scurisce i bordi e porta l'occhio verso il centro
    vignette = Image.new("L", (width, height), 0)
    ImageDraw.Draw(vignette).ellipse(
        [-width * 0.2, -height * 0.15, width * 1.2, height * 1.15], fill=255
    )
    vignette = vignette.filter(ImageFilter.GaussianBlur(width // 8))
    dark = Image.new("RGB", (width, height), (4, 6, 18))
    image = Image.composite(image.convert("RGB"), dark, vignette)

    out = io.BytesIO()
    image.convert("RGB").save(out, format="JPEG", quality=94)
    return out.getvalue()

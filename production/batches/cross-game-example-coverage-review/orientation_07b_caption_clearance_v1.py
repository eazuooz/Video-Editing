"""Whole-source, aspect-preserving reframing for two evidenced side-view cuts."""
from PIL import Image, ImageFilter

INTERVALS = ((390, 583), (1622, 1789))

def affected(frame):
    return any(start <= frame < end for start, end in INTERVALS)

def reframe(image):
    assert image.size == (1920, 1080)
    # Retain every native source pixel in the sharp image, including controls
    # and speed HUD. The full-screen background uses this same source frame.
    background = image.filter(ImageFilter.GaussianBlur(24))
    foreground = image.resize((1728, 972), Image.Resampling.LANCZOS)
    background.paste(foreground, (96, 0))
    return background

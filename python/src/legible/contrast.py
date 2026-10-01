"""WCAG 2.x contrast, the measure `accent-is-attention` reads its pairings in.

Separation between data colours is a perceptual distance (``legible.cvd``); whether text or a stroke
can be read on what it sits on is a luminance ratio, and the two are different rulers for different
questions. This module is the second ruler and nothing else.
"""

from __future__ import annotations

from legible.cvd import hex_to_rgb1


def relative_luminance(colour: str) -> float:
    """A hex colour's relative luminance, by the WCAG 2.x definition."""
    channels = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in hex_to_rgb1(colour)
    ]
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(foreground: str, background: str) -> float:
    """The WCAG contrast ratio between two hex colours, from 1 to 21. Symmetric."""
    lighter, darker = sorted(
        (relative_luminance(foreground), relative_luminance(background)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)

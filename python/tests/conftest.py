import json
from pathlib import Path
from textwrap import dedent

import pytest

from legible import load_palette

THEMES_DIR = Path(__file__).resolve().parents[2] / "themes"


@pytest.fixture
def themes_dir() -> Path:
    return THEMES_DIR


@pytest.fixture
def write_deck(tmp_path: Path):
    """Write a slide markdown deck to a temp file and hand back the path."""

    def _write(markdown: str, name: str = "slides.md") -> Path:
        path = tmp_path / name
        path.write_text(dedent(markdown), encoding="utf-8")
        return path

    return _write


@pytest.fixture
def write_theme(tmp_path: Path):
    """Write a palette dict to a temp .json file and hand back the path."""

    def _write(palette: dict, name: str = "theme.json") -> Path:
        path = tmp_path / name
        path.write_text(json.dumps(palette))
        return path

    return _write


@pytest.fixture
def base_palette() -> dict:
    """A minimal schema-complete palette, for tests that vary one thing about it."""
    return {
        "meta": {"name": "test"},
        "ink": "#102a43",
        "neutral": "#486581",
        "neutral-soft": "#93a4b8",
        "surface": "#ffffff",
        "surface-alt": "#f4f7fb",
        "hairline": "#dde5ee",
        "brand": "#00407a",
        "brand-strong": "#1d8db0",
        "accent": "#dd8a2e",
        "accent-strong": "#b3541e",
        "reference": "#111111",
        "muted": "#778496",
        "series": ["#1b6fb0", "#57c0ae", "#4c3a78"],
    }


@pytest.fixture
def palette(base_palette: dict, write_theme):
    """``base_palette`` loaded, for the callers that take a Palette rather than a file."""
    return load_palette(write_theme(base_palette))


@pytest.fixture
def colliding_palette(base_palette: dict) -> dict:
    """A palette whose series-2 sits a hair off series-1 — indistinguishable under every
    condition, so it breaks the floor rather than only warning."""
    base_palette["series"][1] = "#1b70b2"
    return base_palette


@pytest.fixture
def grayscale_clash_palette(base_palette: dict) -> dict:
    """A palette whose series-2 is a rust: well clear of series-1 in colour, near-identical to it
    in lightness, so only the grayscale check — the advisory one — notices."""
    base_palette["series"][1] = "#a34a2a"
    return base_palette


@pytest.fixture
def faint_attention_palette(base_palette: dict) -> dict:
    """A palette whose text-and-stroke role is the fill colour itself: a warm tone that clears
    contrast under ink, and fails it as text on the ground."""
    base_palette["accent-strong"] = base_palette["accent"]
    return base_palette

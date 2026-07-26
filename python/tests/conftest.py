import json
from pathlib import Path

import pytest

THEMES_DIR = Path(__file__).resolve().parents[2] / "themes"


@pytest.fixture
def themes_dir() -> Path:
    return THEMES_DIR


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
        "reference": "#111111",
        "muted": "#778496",
        "series": ["#1b6fb0", "#57c0ae", "#4c3a78"],
    }

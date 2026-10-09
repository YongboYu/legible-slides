"""What a release publishes: one version everywhere, under the names a user installs.

The project ships as packages released together from one tag (#46), so a release is a single number
and every file that names it has to agree. Each version string is read here the way the file
states it — a regex over the TOML, because ``tomllib`` arrived in 3.11 and the project supports
3.10 — so a bump that missed one fails before a tag can publish mismatched packages.

The distribution's name and links are read off the installed metadata, which is what a user's
machine sees, rather than off ``pyproject.toml``, which says why the name differs from the import's.
"""

import json
import re
from importlib import metadata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: The name on PyPI, and the one a user installs.
DISTRIBUTION = "legible-slides"

REPOSITORY = "https://github.com/YongboYu/legible-slides"

#: The `[project]` table of a pyproject, up to the next table header.
_PROJECT_TABLE = re.compile(r"^\[project\]\s*$(?P<body>.*?)(?=^\[|\Z)", re.MULTILINE | re.DOTALL)
_TOML_VERSION = re.compile(r'^version\s*=\s*"(?P<version>[^"]+)"\s*$', re.MULTILINE)


def _pyproject_version(relative: str) -> str:
    text = (REPO / relative).read_text(encoding="utf-8")
    table = _PROJECT_TABLE.search(text)
    assert table, f"{relative} has no [project] table"
    versions = _TOML_VERSION.findall(table["body"])
    assert len(versions) == 1, f"{relative} states its version {len(versions)} times"
    return versions[0]


def _package_json_version(relative: str) -> str:
    return json.loads((REPO / relative).read_text(encoding="utf-8"))["version"]


#: Every place a release's version is written, and how to read it. The create package and the
#: starter's two pins (the theme dependency and the checks launcher's) join this as they land.
VERSIONS = {
    "python/pyproject.toml": _pyproject_version,
    "theme/package.json": _package_json_version,
}


def test_every_version_string_names_the_same_release():
    found = {where: read(where) for where, read in VERSIONS.items()}

    assert len(set(found.values())) == 1, f"versions drifted: {found}"


def test_the_checks_install_as_legible_slides_and_keep_their_commands():
    commands = {
        entry.name
        for entry in metadata.distribution(DISTRIBUTION).entry_points
        if entry.group == "console_scripts"
    }

    assert commands == {"legible", "cvd-validate"}


def test_the_package_page_links_to_the_repository_the_docs_and_the_issue_tracker():
    urls = dict(
        (label.strip(), url.strip())
        for label, url in (
            field.split(",", 1) for field in metadata.metadata(DISTRIBUTION).get_all("Project-URL")
        )
    )

    assert urls == {
        "Repository": REPOSITORY,
        "Documentation": f"{REPOSITORY}/blob/main/docs/method.md",
        "Issues": f"{REPOSITORY}/issues",
    }

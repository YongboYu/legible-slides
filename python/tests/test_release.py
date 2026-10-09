"""What a release publishes: one version everywhere, under the names a user installs.

The project ships as packages released together from one tag (#46), so a release is a single number
and every file that names it has to agree. Each version string is read here the way the file
states it — a regex over the TOML, because ``tomllib`` arrived in 3.11 and the project supports
3.10 — so a bump that missed one fails before a tag can publish mismatched packages. The release
workflow sets ``RELEASE_TAG`` and holds the tag to the same strings, and every npm package that
workflow lists has to name this repository, or npm turns its provenance away.

The distribution's name and links are read off the installed metadata, which is what a user's
machine sees, rather than off ``pyproject.toml``, which says why the name differs from the import's.
"""

import json
import os
import re
from importlib import metadata
from pathlib import Path

import pytest

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


def _package_json(relative: str) -> dict:
    return json.loads((REPO / relative).read_text(encoding="utf-8"))


def _package_json_version(relative: str) -> str:
    return _package_json(relative)["version"]


#: The theme a stamped deck depends on, under the name it has on npm.
THEME_PACKAGE = "slidev-theme-legible"


def _starter_theme_pin(relative: str) -> str:
    """The version the starter depends on the theme at, as written. Read raw, so a range such as
    ``^0.1.0`` fails the comparison: a stamped deck pins the theme exactly."""
    return _package_json(relative)["dependencies"][THEME_PACKAGE]


#: The checks launcher's pin, one line of shell.
_LAUNCHER_VERSION = re.compile(r"^VERSION=(?P<version>\S*)$", re.MULTILINE)


def _launcher_version(relative: str) -> str:
    text = (REPO / relative).read_text(encoding="utf-8")
    versions = _LAUNCHER_VERSION.findall(text)
    assert len(versions) == 1, f"{relative} states its version {len(versions)} times"
    return versions[0]


#: Every place a release's version is written, and how to read it.
VERSIONS = {
    "python/pyproject.toml": _pyproject_version,
    "theme/package.json": _package_json_version,
    "create/package.json": _package_json_version,
    "skill/template/package.json": _starter_theme_pin,
    "skill/template/bin/legible": _launcher_version,
}


def _versions() -> dict[str, str]:
    return {where: read(where) for where, read in VERSIONS.items()}


def test_every_version_string_names_the_same_release():
    found = _versions()

    assert len(set(found.values())) == 1, f"versions drifted: {found}"


#: The tag a release is being cut from, set by the release workflow's check job. Unset everywhere
#: else, because only a release has a tag to compare against. The workflow runs this test with
#: pytest's skipping plugin off, so there an unset tag fails rather than skips.
RELEASE_TAG = os.environ.get("RELEASE_TAG", "")


@pytest.mark.skipif(not RELEASE_TAG, reason="no release tag to check; set RELEASE_TAG")
def test_the_release_tag_names_the_version_every_file_states():
    assert RELEASE_TAG.startswith("v"), f"release tags start with v, got {RELEASE_TAG!r}"
    tagged = RELEASE_TAG.removeprefix("v")
    found = _versions()

    assert all(version == tagged for version in found.values()), (
        f"tag {RELEASE_TAG} names {tagged}, but the files state {found}"
    )


#: The npm packages the release workflow publishes, one directory each, as its env states them.
_NPM_PACKAGES = re.compile(r"^\s*NPM_PACKAGES:\s*(?P<dirs>.+?)\s*$", re.MULTILINE)


def _npm_packages() -> list[str]:
    workflow = (REPO / ".github/workflows/release.yml").read_text(encoding="utf-8")
    listed = _NPM_PACKAGES.findall(workflow)
    assert len(listed) == 1, f"release.yml lists its npm packages {len(listed)} times"
    return listed[0].split()


@pytest.mark.parametrize("package", ["theme", "create"])
def test_the_release_publishes_the_theme_and_the_create_package_to_npm(package):
    assert package in _npm_packages()


def test_every_npm_package_the_release_publishes_names_this_repository():
    # npm checks a provenance statement against the package's `repository`, and refuses the
    # publish when the two disagree, so a package without one fails on the release tag itself.
    for package in _npm_packages():
        repository = _package_json(f"{package}/package.json").get("repository", {})

        assert repository.get("url") == f"git+{REPOSITORY}.git", f"{package}/ names {repository}"
        assert repository.get("directory") == package, f"{package}/ names {repository}"


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

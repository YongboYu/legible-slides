"""`npm create legible-slides`, held to what an author receives from it.

The create package stamps the starter into a new directory with no clone (#51). What it hands an
author is a deck, so these tests run the command the way npm runs it, from the packed package, and
read the directory it leaves behind. Packing is part of what is under test: npm drops a
`.gitignore` from a package, so a create command tried only from a checkout would pass here and
stamp a deck without one.

The package is packed from a copy of this checkout's two directories it reads, so packing never
writes into the checkout itself. CI's scaffold job runs the same tarball through `npm exec` and
builds the deck it stamps.
"""

import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CREATE = REPO / "create"
STARTER = REPO / "skill" / "template"

pytestmark = pytest.mark.skipif(
    shutil.which("npm") is None, reason="packing the create package needs npm"
)

#: Unpacks the way a modern tarfile asks to be told to; the filter arrived in 3.12 and was
#: backported to later patch releases of 3.10 and 3.11.
_UNPACK = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}


@pytest.fixture(scope="module")
def checkout(tmp_path_factory) -> Path:
    """The two directories of this checkout the create package reads, at their own paths."""
    root = tmp_path_factory.mktemp("checkout")
    shutil.copytree(CREATE, root / "create")
    shutil.copytree(STARTER, root / "skill" / "template")
    return root


@pytest.fixture(scope="module")
def package(checkout, tmp_path_factory) -> Path:
    """The create package as npm hands it to an author: packed, then unpacked."""
    packed = tmp_path_factory.mktemp("packed")
    environment = {
        **os.environ,
        "npm_config_cache": str(tmp_path_factory.mktemp("npm-cache")),
        "npm_config_update_notifier": "false",
    }
    subprocess.run(
        ["npm", "pack", "./create", "--pack-destination", str(packed)],
        cwd=checkout,
        env=environment,
        capture_output=True,
        check=True,
    )
    (tarball,) = packed.glob("create-legible-slides-*.tgz")
    unpacked = tmp_path_factory.mktemp("unpacked")
    with tarfile.open(tarball) as archive:
        archive.extractall(unpacked, **_UNPACK)
    return unpacked / "package"


def _create(package: Path, target: Path) -> subprocess.CompletedProcess:
    """Run the create command the way `npm create legible-slides my-talk` does: from the directory
    the author is in, naming the new one relative to it."""
    return subprocess.run(
        ["node", str(package / "index.js"), target.name],
        cwd=target.parent,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def stamped(package, tmp_path) -> Path:
    """A deck stamped from the packed package into a new directory, as an author would."""
    deck = tmp_path / "my-talk"
    result = _create(package, deck)
    assert result.returncode == 0, result.stderr
    return deck


def test_the_deck_is_named_after_its_directory(stamped):
    manifest = json.loads((stamped / "package.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "my-talk"


def _files(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in root.rglob("*") if path.is_file()}


def test_the_deck_is_the_whole_starter_dotfiles_included(stamped):
    """Every file the starter carries, its `.gitignore` among them, so `node_modules` and the build
    stay out of the author's repository from the first commit."""
    assert _files(stamped) == _files(STARTER)
    for path in _files(STARTER) - {Path("package.json")}:
        assert (stamped / path).read_bytes() == (STARTER / path).read_bytes(), path


def test_the_launchers_arrive_executable_whatever_the_package_kept(package, tmp_path):
    """The checks run straight after stamping, with no chmod. The starter's launchers are executable
    in git and npm keeps the bit when it packs on Linux, but a package packed or unpacked elsewhere
    can lose it, so the command sets it rather than trusting the copy."""
    stripped = tmp_path / "package"
    shutil.copytree(package, stripped)
    for launcher in (stripped / "template" / "bin").iterdir():
        launcher.chmod(0o644)
    deck = tmp_path / "my-talk"

    assert _create(stripped, deck).returncode == 0
    launchers = sorted((deck / "bin").iterdir())
    assert [path.name for path in launchers] == ["cvd-validate", "legible"]
    for launcher in launchers:
        assert os.access(launcher, os.X_OK), f"bin/{launcher.name} is not executable"


def _contents(root: Path) -> dict[Path, bytes]:
    return {path: (root / path).read_bytes() for path in _files(root)}


def test_it_refuses_a_directory_that_is_not_empty_and_leaves_it_untouched(package, tmp_path):
    """An author's work is never overwritten, not even a stray dotfile of it: the command stops
    before it writes anything."""
    deck = tmp_path / "my-talk"
    deck.mkdir()
    (deck / "notes.md").write_text("an outline nobody else has\n", encoding="utf-8")
    (deck / ".env").write_text("SECRET=1\n", encoding="utf-8")
    before = _contents(deck)

    result = _create(package, deck)

    assert result.returncode != 0
    assert "my-talk" in result.stderr
    assert _contents(deck) == before


def test_it_prints_the_next_steps_in_order(package, tmp_path):
    """Into the deck, install, and the dev server, as the commands an author types."""
    result = _create(package, tmp_path / "my-talk")
    commands = [line.strip() for line in result.stdout.splitlines()]

    steps = ["cd my-talk", "pnpm install", "pnpm dev"]
    assert all(step in commands for step in steps), result.stdout
    assert sorted(steps, key=commands.index) == steps


def test_packing_leaves_no_bundled_starter_behind(checkout, package):
    """The bundle is an artifact of the pack. Left in a checkout, it would be a second starter for
    the create command to prefer over the one being edited."""
    assert (package / "template").is_dir()
    assert not (checkout / "create" / "template").exists()


def test_from_a_checkout_it_stamps_the_starter_in_the_repo(checkout, tmp_path):
    """Run from a clone, with nothing packed, it stamps the starter being edited."""
    deck = tmp_path / "my-talk"

    result = _create(checkout / "create", deck)

    assert result.returncode == 0, result.stderr
    assert _files(deck) == _files(STARTER)
    assert json.loads((deck / "package.json").read_text(encoding="utf-8"))["name"] == "my-talk"


def test_with_no_directory_named_it_says_how_to_name_one(package, tmp_path):
    result = subprocess.run(
        ["node", str(package / "index.js")], cwd=tmp_path, capture_output=True, text=True
    )

    assert result.returncode != 0
    assert "npm create legible-slides my-talk" in result.stderr
    assert not any(tmp_path.iterdir())

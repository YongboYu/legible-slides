"""The project's licence, in everything a user receives.

MIT asks for its notice in every copy, and a copy here is a package rather than the repo: the wheel
and the sdist are built from ``python/``, and the npm archives from ``theme/`` and ``create/``. None
of them sees the root, so each carries the root's licence word for word.
"""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("package", ["python", "theme", "create"])
def test_each_shipped_package_carries_the_project_s_licence(package):
    shipped = REPO / package / "LICENSE"

    assert shipped.is_file(), f"{package}/ ships without the project's licence"
    assert shipped.read_bytes() == (REPO / "LICENSE").read_bytes(), f"{package}/LICENSE drifted"

"""Distribution metadata must expose the documented consumer library safely."""

import subprocess
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_distribution_uses_the_locked_uv_build_backend() -> None:
    """The repository publishes an installable package without a fallback backend."""
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)

    assert project["build-system"] == {
        "requires": ["uv_build>=0.11.28,<0.12"],
        "build-backend": "uv_build",
    }
    assert project["tool"]["uv"]["package"] is True


def test_distribution_includes_typed_consumer_package() -> None:
    """The runtime-facing OIDC library is present in the source distribution tree."""
    assert (ROOT / "src" / "neural_brain" / "consumer" / "__init__.py").is_file()
    assert (ROOT / "src" / "neural_brain" / "py.typed").is_file()


def test_offline_build_contains_the_typed_oidc_consumer(tmp_path: Path) -> None:
    """The documented build command creates an artifact without network access."""
    output = tmp_path / "dist"
    subprocess.run(
        ("uv", "build", "--offline", "--out-dir", str(output), "--clear"),
        cwd=ROOT,
        check=True,
    )

    wheel = output / "neural_brain-0.0.0-py3-none-any.whl"
    assert (output / "neural_brain-0.0.0.tar.gz").is_file()
    assert wheel.is_file()
    with zipfile.ZipFile(wheel) as archive:
        assert "neural_brain/consumer/__init__.py" in archive.namelist()
        assert "neural_brain/py.typed" in archive.namelist()

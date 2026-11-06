from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples" / "nube_pago" / "docs"


@pytest.fixture
def samples() -> Path:
    return SAMPLES


@pytest.fixture
def repo() -> Path:
    return ROOT

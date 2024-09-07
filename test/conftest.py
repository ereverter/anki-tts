from pathlib import Path

import pytest


@pytest.fixture
def samples_path():
    current_dir = Path(__file__).resolve().parent
    return current_dir / "samples"

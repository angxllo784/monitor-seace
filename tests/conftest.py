from pathlib import Path

import pytest


@pytest.fixture
def fixture_html() -> str:
    ruta = Path(__file__).parent / "fixtures" / "resultados.html"
    return ruta.read_text(encoding="utf-8")

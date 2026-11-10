"""Navegación del portal con Playwright.

Playwright se importa dentro del método (no al cargar el módulo) para que
las pruebas y el modo demo funcionen sin tener el navegador instalado.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from . import config
from .models import Oferta
from .parser import parsear_resultados

MENSAJE_SIN_PLAYWRIGHT = (
    "Playwright no está instalado. Ejecuta:\n"
    "    pip install -r requirements.txt\n"
    "    playwright install chromium"
)


class MonitorSEACE:
    """Busca convocatorias en el portal y devuelve las ofertas parseadas."""

    def __init__(
        self,
        url: str = config.URL_BUSQUEDA,
        headless: bool = True,
        timeout_ms: int = config.TIMEOUT_MS,
    ) -> None:
        self.url = url
        self.headless = headless
        self.timeout_ms = timeout_ms

    # -- API pública ------------------------------------------------------

    def buscar(self, palabra_clave: str = "", max_paginas: int = 1) -> List[Oferta]:
        """Abre el buscador, escribe la palabra clave y extrae los resultados."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:  # pragma: no cover - depende del entorno
            raise RuntimeError(MENSAJE_SIN_PLAYWRIGHT) from error

        ofertas: List[Oferta] = []
        with sync_playwright() as playwright:
            navegador = playwright.chromium.launch(headless=self.headless)
            try:
                pagina = navegador.new_page()
                pagina.goto(self.url, wait_until="domcontentloaded", timeout=self.timeout_ms)

                if palabra_clave:
                    pagina.fill(config.SELECTOR_CAJA_BUSQUEDA, palabra_clave)
                    pagina.click(config.SELECTOR_BOTON_BUSCAR)
                    pagina.wait_for_load_state("networkidle", timeout=self.timeout_ms)

                for _ in range(max(1, max_paginas)):
                    pagina.wait_for_selector(
                        config.SELECTOR_TABLA_RESULTADOS, timeout=self.timeout_ms
                    )
                    ofertas.extend(parsear_resultados(pagina.content()))

                    siguiente = pagina.query_selector("a.siguiente-pagina")
                    if not siguiente:
                        break
                    siguiente.click()
                    pagina.wait_for_load_state("networkidle", timeout=self.timeout_ms)
            finally:
                navegador.close()

        return _sin_duplicados(ofertas)

    @staticmethod
    def desde_archivo(ruta: Path | str = config.FIXTURE_DEMO) -> List[Oferta]:
        """Modo demo: lee un HTML guardado, sin usar la red."""
        html = Path(ruta).read_text(encoding="utf-8")
        return parsear_resultados(html)


def _sin_duplicados(ofertas: List[Oferta]) -> List[Oferta]:
    """Elimina ofertas repetidas conservando el primer resultado."""
    vistos: set[str] = set()
    resultado: List[Oferta] = []
    for oferta in ofertas:
        if oferta.clave in vistos:
            continue
        vistos.add(oferta.clave)
        resultado.append(oferta)
    return resultado

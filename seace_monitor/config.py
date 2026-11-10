"""Configuración central del monitor.

Los selectores viven aquí y no dentro del scraper para que, cuando el
portal cambie su maquetación, solo haya que ajustar este archivo.
"""

from pathlib import Path

# --- Rutas ---------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ / "data"
BASE_DATOS_POR_DEFECTO = CARPETA_DATOS / "seace.db"
FIXTURE_DEMO = RAIZ / "tests" / "fixtures" / "resultados.html"

# --- Portal --------------------------------------------------------------

# URL del buscador de convocatorias. Se mantiene como constante para poder
# apuntar a un entorno de pruebas sin tocar el código.
URL_BUSQUEDA = "https://www.seace.gob.pe/"

# Selectores usados por el scraper (ajustar si el portal cambia).
SELECTOR_CAJA_BUSQUEDA = "input[name='txtBuscar']"
SELECTOR_BOTON_BUSCAR = "button[type='submit']"
SELECTOR_TABLA_RESULTADOS = "table.tabla-resultados"
SELECTOR_SIN_RESULTADOS = ".mensaje-sin-resultados"

# --- Comportamiento ------------------------------------------------------

TIMEOUT_MS = 30_000
MAX_PAGINAS = 5

"""Extracción de ofertas desde el HTML del portal.

Se usa ``html.parser`` de la biblioteca estándar (en lugar de BeautifulSoup)
para que el proyecto no dependa de librerías externas solo para leer una
tabla. El parser está separado del navegador, de modo que se puede probar
con un archivo HTML guardado.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from html.parser import HTMLParser
from typing import List, Optional

from .models import Oferta

#: Orden de las columnas de la tabla de resultados.
COLUMNAS = ("codigo", "titulo", "entidad", "fecha", "monto", "estado")

_ESPACIOS = re.compile(r"\s+")


def limpiar_texto(valor: str) -> str:
    """Colapsa espacios y saltos de línea en un texto de una sola línea."""
    return _ESPACIOS.sub(" ", valor or "").strip()


def parsear_fecha(valor: str) -> Optional[date]:
    """Convierte ``dd/mm/aaaa`` o ``aaaa-mm-dd`` en ``date``.

    Devuelve ``None`` si el texto no es una fecha válida; así una fila con
    formato inesperado no rompe toda la extracción.
    """
    texto = limpiar_texto(valor)
    if not texto:
        return None
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def parsear_monto(valor: str) -> Optional[float]:
    """Convierte ``S/ 1,234.56`` en ``1234.56``.

    Acepta también montos sin símbolo de moneda y devuelve ``None`` cuando
    la celda está vacía o contiene un guion.
    """
    texto = limpiar_texto(valor)
    if not texto or texto in {"-", "—", "N/A"}:
        return None

    texto = texto.replace("S/", "").replace("S/.", "").replace(" ", "")
    if "," in texto and "." in texto:
        # Formato 1,234.56 -> la coma separa miles.
        texto = texto.replace(",", "")
    elif "," in texto:
        # Formato 1234,56 -> la coma es decimal.
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


class _TablaParser(HTMLParser):
    """Recolecta las filas de la tabla de resultados."""

    def __init__(self, clase_tabla: str) -> None:
        super().__init__(convert_charrefs=True)
        self.clase_tabla = clase_tabla
        self.filas: List[List[str]] = []
        self.enlaces: List[str] = []

        self._en_tabla = False
        self._profundidad_tabla = 0
        self._en_fila = False
        self._en_celda = False
        self._celda: List[str] = []
        self._fila: List[str] = []
        self._enlace_fila = ""
        self._fila_es_encabezado = False

    # -- etiquetas --------------------------------------------------------

    def handle_starttag(self, tag: str, attrs) -> None:
        atributos = dict(attrs)
        if tag == "table":
            if not self._en_tabla and self.clase_tabla in (atributos.get("class") or "").split():
                self._en_tabla = True
                self._profundidad_tabla = 1
            elif self._en_tabla:
                self._profundidad_tabla += 1
        elif not self._en_tabla:
            return
        elif tag == "tr":
            self._en_fila = True
            self._fila = []
            self._enlace_fila = ""
            self._fila_es_encabezado = False
        elif tag in ("td", "th") and self._en_fila:
            self._en_celda = True
            self._celda = []
            if tag == "th":
                self._fila_es_encabezado = True
        elif tag == "a" and self._en_fila and not self._enlace_fila:
            self._enlace_fila = atributos.get("href") or ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._en_tabla:
            self._profundidad_tabla -= 1
            if self._profundidad_tabla <= 0:
                self._en_tabla = False
        elif not self._en_tabla:
            return
        elif tag in ("td", "th") and self._en_celda:
            self._fila.append(limpiar_texto("".join(self._celda)))
            self._en_celda = False
            self._celda = []
        elif tag == "tr" and self._en_fila:
            if self._fila and not self._fila_es_encabezado:
                self.filas.append(self._fila)
                self.enlaces.append(self._enlace_fila)
            self._en_fila = False
            self._fila = []

    def handle_data(self, data: str) -> None:
        if self._en_celda:
            self._celda.append(data)


def parsear_resultados(html: str, clase_tabla: str = "tabla-resultados") -> List[Oferta]:
    """Devuelve las ofertas encontradas en el HTML indicado.

    Las filas con menos columnas que el encabezado se ignoran para no
    generar registros incompletos.
    """
    parser = _TablaParser(clase_tabla)
    parser.feed(html)
    parser.close()

    ofertas: List[Oferta] = []
    for celdas, enlace in zip(parser.filas, parser.enlaces):
        if len(celdas) < 5:
            continue
        datos = dict(zip(COLUMNAS, celdas))
        ofertas.append(
            Oferta(
                codigo=datos.get("codigo", ""),
                titulo=datos.get("titulo", ""),
                entidad=datos.get("entidad", ""),
                fecha_publicacion=parsear_fecha(datos.get("fecha", "")),
                monto=parsear_monto(datos.get("monto", "")),
                estado=datos.get("estado", ""),
                url=enlace,
            )
        )
    return ofertas

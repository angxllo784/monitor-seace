"""Modelos de datos del monitor de contrataciones."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Oferta:
    """Una convocatoria de contratación pública.

    Es inmutable (frozen) para poder usarla como clave en conjuntos y
    para evitar modificaciones accidentales después de guardarla.
    """

    codigo: str
    titulo: str
    entidad: str
    fecha_publicacion: Optional[date] = None
    monto: Optional[float] = None
    estado: str = ""
    url: str = ""

    @property
    def clave(self) -> str:
        """Identificador estable: el código oficial o, si falta, el título."""
        return self.codigo or self.titulo

    def monto_texto(self) -> str:
        """Devuelve el monto formateado o '—' cuando no hay información."""
        if self.monto is None:
            return "—"
        return f"S/ {self.monto:,.2f}"

    def fecha_texto(self) -> str:
        """Devuelve la fecha en formato dd/mm/aaaa o '—'."""
        if self.fecha_publicacion is None:
            return "—"
        return self.fecha_publicacion.strftime("%d/%m/%Y")

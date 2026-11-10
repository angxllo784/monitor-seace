"""Persistencia en SQLite.

Se guarda una fila por convocatoria usando el código oficial como clave
primaria. Al volver a ejecutar el monitor, las ofertas existentes se
actualizan en lugar de duplicarse.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple

from .models import Oferta

ESQUEMA = """
CREATE TABLE IF NOT EXISTS ofertas (
    codigo            TEXT PRIMARY KEY,
    titulo            TEXT NOT NULL,
    entidad           TEXT NOT NULL,
    fecha_publicacion TEXT,
    monto             REAL,
    estado            TEXT,
    url               TEXT,
    actualizado_en    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ofertas_fecha
    ON ofertas (fecha_publicacion DESC);
"""


@contextmanager
def abrir(ruta: Path | str) -> Iterator[sqlite3.Connection]:
    """Abre la base de datos, garantiza el esquema y cierra al salir."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    try:
        conexion.executescript(ESQUEMA)
        yield conexion
        conexion.commit()
    finally:
        conexion.close()


def guardar(conexion: sqlite3.Connection, ofertas: Iterable[Oferta]) -> Tuple[int, int]:
    """Inserta o actualiza las ofertas y devuelve ``(nuevas, actualizadas)``."""
    lote = list(ofertas)
    if not lote:
        return 0, 0

    codigos = [oferta.clave for oferta in lote]
    marcadores = ",".join("?" * len(codigos))
    existentes = {
        fila["codigo"]
        for fila in conexion.execute(
            f"SELECT codigo FROM ofertas WHERE codigo IN ({marcadores})", codigos
        )
    }

    conexion.executemany(
        """
        INSERT INTO ofertas (codigo, titulo, entidad, fecha_publicacion, monto, estado, url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(codigo) DO UPDATE SET
            titulo            = excluded.titulo,
            entidad           = excluded.entidad,
            fecha_publicacion = excluded.fecha_publicacion,
            monto             = excluded.monto,
            estado            = excluded.estado,
            url               = excluded.url,
            actualizado_en    = datetime('now')
        """,
        [
            (
                oferta.clave,
                oferta.titulo,
                oferta.entidad,
                oferta.fecha_publicacion.isoformat() if oferta.fecha_publicacion else None,
                oferta.monto,
                oferta.estado,
                oferta.url,
            )
            for oferta in lote
        ],
    )

    nuevas = sum(1 for codigo in codigos if codigo not in existentes)
    return nuevas, len(lote) - nuevas


def listar(
    conexion: sqlite3.Connection,
    palabra_clave: Optional[str] = None,
    desde: Optional[date] = None,
) -> List[Oferta]:
    """Devuelve las ofertas filtradas, de la más reciente a la más antigua."""
    consulta = "SELECT * FROM ofertas"
    condiciones: List[str] = []
    parametros: List[Sequence[object]] = []

    if palabra_clave:
        condiciones.append("(titulo LIKE ? OR entidad LIKE ?)")
        patron = f"%{palabra_clave}%"
        parametros.extend([patron, patron])

    if desde:
        condiciones.append("fecha_publicacion >= ?")
        parametros.append(desde.isoformat())

    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)

    consulta += " ORDER BY fecha_publicacion DESC, titulo ASC"

    filas = conexion.execute(consulta, parametros).fetchall()
    return [
        Oferta(
            codigo=fila["codigo"],
            titulo=fila["titulo"],
            entidad=fila["entidad"],
            fecha_publicacion=(
                date.fromisoformat(fila["fecha_publicacion"])
                if fila["fecha_publicacion"]
                else None
            ),
            monto=fila["monto"],
            estado=fila["estado"] or "",
            url=fila["url"] or "",
        )
        for fila in filas
    ]


def contar(conexion: sqlite3.Connection) -> int:
    """Cantidad total de ofertas almacenadas."""
    return int(conexion.execute("SELECT COUNT(*) FROM ofertas").fetchone()[0])

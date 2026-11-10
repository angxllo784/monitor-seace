"""Exportación de resultados a CSV y a un reporte HTML.

El CSV usa punto y coma como separador para que Excel en configuración
regional de Perú lo abra en columnas sin pasos extra.
"""

from __future__ import annotations

import csv
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Iterable, List

from .models import Oferta

ENCABEZADOS = (
    "Código",
    "Título",
    "Entidad",
    "Fecha de publicación",
    "Monto",
    "Estado",
    "Enlace",
)


def exportar_csv(ofertas: Iterable[Oferta], ruta: Path | str) -> Path:
    """Escribe las ofertas en un archivo CSV y devuelve su ruta."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    with ruta.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow(ENCABEZADOS)
        for oferta in ofertas:
            escritor.writerow(
                [
                    oferta.codigo,
                    oferta.titulo,
                    oferta.entidad,
                    oferta.fecha_texto(),
                    oferta.monto_texto(),
                    oferta.estado,
                    oferta.url,
                ]
            )
    return ruta


def _fila_html(oferta: Oferta) -> str:
    enlace = (
        f'<a href="{escape(oferta.url)}" target="_blank" rel="noopener">Ver</a>'
        if oferta.url
        else "—"
    )
    return (
        "<tr>"
        f"<td>{escape(oferta.codigo)}</td>"
        f'<td class="titulo">{escape(oferta.titulo)}</td>'
        f"<td>{escape(oferta.entidad)}</td>"
        f"<td>{oferta.fecha_texto()}</td>"
        f"<td class=\"monto\">{oferta.monto_texto()}</td>"
        f"<td>{escape(oferta.estado)}</td>"
        f"<td>{enlace}</td>"
        "</tr>"
    )


def exportar_html(
    ofertas: List[Oferta],
    ruta: Path | str,
    titulo: str = "Monitor de contrataciones",
) -> Path:
    """Genera un reporte HTML listo para abrir en el navegador."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    filas = "\n".join(_fila_html(oferta) for oferta in ofertas) or (
        '<tr><td colspan="7" class="vacio">No se encontraron ofertas.</td></tr>'
    )
    generado = datetime.now().strftime("%d/%m/%Y %H:%M")

    documento = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
          margin: 2rem; color: #1f2933; background: #f7f9fb; }}
  h1 {{ font-size: 1.4rem; margin: 0 0 .25rem; }}
  p.meta {{ color: #616e7c; margin: 0 0 1.25rem; font-size: .9rem; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff;
           box-shadow: 0 1px 3px rgba(0,0,0,.08); font-size: .9rem; }}
  th, td {{ padding: .55rem .7rem; text-align: left; border-bottom: 1px solid #e4e7eb; }}
  th {{ background: #243b53; color: #fff; font-weight: 600; }}
  tr:hover td {{ background: #f0f4f8; }}
  td.titulo {{ min-width: 18rem; }}
  td.monto {{ white-space: nowrap; }}
  td.vacio {{ text-align: center; color: #616e7c; padding: 2rem; }}
  a {{ color: #0b69a3; }}
</style>
</head>
<body>
<h1>{escape(titulo)}</h1>
<p class="meta">{len(ofertas)} convocatoria(s) · generado el {generado}</p>
<table>
<thead><tr>{''.join(f'<th>{escape(c)}</th>' for c in ENCABEZADOS)}</tr></thead>
<tbody>
{filas}
</tbody>
</table>
</body>
</html>
"""
    ruta.write_text(documento, encoding="utf-8")
    return ruta

"""Interfaz de línea de comandos del monitor."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from . import config, storage
from .models import Oferta
from .report import exportar_csv, exportar_html
from .scraper import MonitorSEACE


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seace-monitor",
        description="Busca convocatorias, las guarda en SQLite y genera reportes.",
    )
    parser.add_argument(
        "-p", "--palabra",
        default="",
        help="texto a buscar (por defecto trae la primera página del portal)",
    )
    parser.add_argument(
        "--db",
        default=str(config.BASE_DATOS_POR_DEFECTO),
        help="ruta del archivo SQLite",
    )
    parser.add_argument("--csv", help="exporta los resultados a un CSV")
    parser.add_argument("--html", help="exporta los resultados a un reporte HTML")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="usa el HTML de ejemplo incluido (sin conexión a internet)",
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="muestra el navegador durante la ejecución",
    )
    parser.add_argument(
        "--paginas",
        type=int,
        default=1,
        help="número máximo de páginas a recorrer (por defecto 1)",
    )
    return parser


def ejecutar(args: argparse.Namespace) -> int:
    if args.demo:
        ofertas = MonitorSEACE.desde_archivo()
        origen = "HTML de ejemplo"
    else:
        monitor = MonitorSEACE(headless=not args.visible)
        ofertas = monitor.buscar(args.palabra, max_paginas=args.paginas)
        origen = monitor.url

    print(f"Origen: {origen}")
    print(f"Ofertas encontradas: {len(ofertas)}")

    with storage.abrir(args.db) as conexion:
        nuevas, actualizadas = storage.guardar(conexion, ofertas)
        total = storage.contar(conexion)
        guardadas = storage.listar(
            conexion,
            palabra_clave=args.palabra or None,
        )

    print(f"Nuevas: {nuevas} · Actualizadas: {actualizadas} · En base: {total}")

    if args.csv:
        ruta = exportar_csv(guardadas, args.csv)
        print(f"CSV generado: {ruta}")
    if args.html:
        ruta = exportar_html(guardadas, args.html, titulo="Convocatorias encontradas")
        print(f"Reporte HTML generado: {ruta}")

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        return ejecutar(args)
    except RuntimeError as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

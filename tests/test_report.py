import csv
from datetime import date

from seace_monitor.models import Oferta
from seace_monitor.report import exportar_csv, exportar_html


def _ofertas():
    return [
        Oferta(
            codigo="SEACE-001",
            titulo="Servicio de <software> & soporte",
            entidad="Municipalidad del Callao",
            fecha_publicacion=date(2025, 3, 12),
            monto=1500.5,
            estado="Publicado",
            url="https://www.seace.gob.pe/detalle/1",
        ),
        Oferta(codigo="SEACE-002", titulo="Compra de equipos", entidad="GORE Callao"),
    ]


def test_exportar_csv_usa_punto_y_coma(tmp_path):
    ruta = exportar_csv(_ofertas(), tmp_path / "salida.csv")

    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.reader(archivo, delimiter=";"))

    assert filas[0][0] == "Código"
    assert len(filas) == 3
    assert filas[1][4] == "S/ 1,500.50"
    assert filas[2][3] == "—"  # sin fecha


def test_exportar_html_escapa_contenido(tmp_path):
    ruta = exportar_html(_ofertas(), tmp_path / "reporte.html")
    html = ruta.read_text(encoding="utf-8")

    assert "Servicio de &lt;software&gt; &amp; soporte" in html
    assert "<software>" not in html
    assert "2 convocatoria(s)" in html


def test_exportar_html_sin_ofertas(tmp_path):
    html = exportar_html([], tmp_path / "vacio.html").read_text(encoding="utf-8")
    assert "No se encontraron ofertas." in html

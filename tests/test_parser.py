from datetime import date

import pytest

from seace_monitor.parser import (
    limpiar_texto,
    parsear_fecha,
    parsear_monto,
    parsear_resultados,
)


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("12/03/2025", date(2025, 3, 12)),
        ("2025-03-05", date(2025, 3, 5)),
        ("", None),
        ("sin fecha", None),
    ],
)
def test_parsear_fecha(entrada, esperado):
    assert parsear_fecha(entrada) == esperado


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("S/ 185,400.50", 185400.50),
        ("S/ 1,240,000.00", 1240000.0),
        ("1234,56", 1234.56),
        ("—", None),
        ("", None),
    ],
)
def test_parsear_monto(entrada, esperado):
    assert parsear_monto(entrada) == esperado


def test_limpiar_texto_colapsa_espacios():
    assert limpiar_texto("  Servicio\n   de\tsoporte ") == "Servicio de soporte"


def test_parsear_resultados_extrae_ofertas_completas(fixture_html):
    ofertas = parsear_resultados(fixture_html)

    assert len(ofertas) == 4  # la fila incompleta se descarta

    primera = ofertas[0]
    assert primera.codigo == "SEACE-2025-001"
    assert primera.titulo == "Servicio de desarrollo de software a medida"
    assert primera.entidad == "Municipalidad Provincial del Callao"
    assert primera.fecha_publicacion == date(2025, 3, 12)
    assert primera.monto == pytest.approx(185400.50)
    assert primera.url.endswith("/001")
    assert primera.estado == "Publicado"


def test_parsear_resultados_acepta_monto_vacio(fixture_html):
    tercera = parsear_resultados(fixture_html)[2]
    assert tercera.monto is None
    assert tercera.fecha_publicacion == date(2025, 3, 5)

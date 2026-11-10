from datetime import date

from seace_monitor import storage
from seace_monitor.models import Oferta


def _oferta(codigo="SEACE-001", titulo="Servicio de software"):
    return Oferta(
        codigo=codigo,
        titulo=titulo,
        entidad="Municipalidad del Callao",
        fecha_publicacion=date(2025, 3, 12),
        monto=1500.0,
        estado="Publicado",
        url="https://www.seace.gob.pe/detalle/1",
    )


def test_guardar_e_insertar(tmp_path):
    with storage.abrir(tmp_path / "test.db") as conexion:
        nuevas, actualizadas = storage.guardar(conexion, [_oferta()])

        assert (nuevas, actualizadas) == (1, 0)
        assert storage.contar(conexion) == 1


def test_guardar_actualiza_sin_duplicar(tmp_path):
    with storage.abrir(tmp_path / "test.db") as conexion:
        storage.guardar(conexion, [_oferta()])
        nuevas, actualizadas = storage.guardar(
            conexion, [_oferta(titulo="Servicio de software (actualizado)")]
        )

        assert (nuevas, actualizadas) == (0, 1)
        assert storage.contar(conexion) == 1
        assert storage.listar(conexion)[0].titulo.endswith("(actualizado)")


def test_listar_filtra_por_palabra_y_fecha(tmp_path):
    with storage.abrir(tmp_path / "test.db") as conexion:
        storage.guardar(
            conexion,
            [
                _oferta("A", "Servicio de mesa de ayuda"),
                _oferta("B", "Compra de equipos"),
            ],
        )

        assert len(storage.listar(conexion, palabra_clave="ayuda")) == 1
        assert len(storage.listar(conexion, desde=date(2025, 3, 13))) == 0
        assert len(storage.listar(conexion, desde=date(2025, 3, 1))) == 2


def test_guardar_lista_vacia(tmp_path):
    with storage.abrir(tmp_path / "test.db") as conexion:
        assert storage.guardar(conexion, []) == (0, 0)

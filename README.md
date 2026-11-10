# Monitor de convocatorias SEACE

Herramienta en Python que automatiza la búsqueda de convocatorias de
contratación pública, guarda los resultados en SQLite y genera reportes en
CSV y HTML.

Nació de una necesidad concreta: revisar a mano las publicaciones del portal
todas las semanas era lento y se prestaba a errores. Con este monitor la
consulta se ejecuta sola, los registros no se duplican y el reporte queda
listo para revisar o compartir.

## Características

- **Búsqueda automatizada** con Playwright (navegador real, soporta sitios
  que cargan contenido con JavaScript).
- **Almacenamiento idempotente** en SQLite: el código oficial de la
  convocatoria es la clave primaria, así que volver a ejecutar actualiza en
  lugar de duplicar.
- **Reportes** en CSV (compatible con Excel en español: separador `;` y
  UTF-8 con BOM) y en HTML con tabla responsiva.
- **Parser independiente del navegador**, probado con un HTML de ejemplo:
  se puede ejecutar el proyecto completo sin internet.
- **Manejo de datos sucios**: fechas en varios formatos, montos con separador
  de miles, celdas vacías o con guion.
- **Pruebas** con `pytest` sobre parser, almacenamiento y reportes.

## Stack

Python 3.12 · Playwright · SQLite · `html.parser` (biblioteca estándar) ·
pytest

## Estructura

```
monitor-seace/
├── seace_monitor/
│   ├── config.py      # URL, selectores y rutas
│   ├── models.py      # dataclass Oferta
│   ├── parser.py      # extracción y limpieza del HTML
│   ├── scraper.py     # navegación con Playwright
│   ├── storage.py     # persistencia en SQLite
│   ├── report.py      # exportación CSV / HTML
│   └── cli.py         # línea de comandos
├── tests/
│   ├── fixtures/resultados.html
│   ├── test_parser.py
│   ├── test_storage.py
│   └── test_report.py
├── requirements.txt
└── requirements-dev.txt
```

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
playwright install chromium
```

## Uso

Modo demo (sin internet, usa el HTML de ejemplo):

```bash
python -m seace_monitor --demo --csv salida.csv --html reporte.html
```

Consulta real:

```bash
python -m seace_monitor --palabra "software" --paginas 3 --csv salida.csv
```

Salida esperada:

```
Origen: https://www.seace.gob.pe/
Ofertas encontradas: 4
Nuevas: 4 · Actualizadas: 0 · En base: 4
CSV generado: salida.csv
```

| Opción | Descripción |
| --- | --- |
| `-p`, `--palabra` | texto a buscar |
| `--paginas` | máximo de páginas a recorrer |
| `--db` | ruta del archivo SQLite |
| `--csv`, `--html` | exportar resultados |
| `--demo` | usar el HTML local, sin red |
| `--visible` | mostrar el navegador durante la ejecución |

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Decisiones técnicas

- **El parser no depende de Playwright.** El navegador solo entrega HTML; la
  extracción es una función pura que recibe texto. Eso permite probarla con
  un fixture y aislar los fallos: si el portal cambia, se ajusta
  `parser.py`/`config.py` sin tocar la automatización.
- **Idempotencia en la base de datos.** `INSERT ... ON CONFLICT DO UPDATE`
  evita duplicados y permite ejecutar el monitor a diario.
- **Los selectores viven en `config.py`.** Cuando el portal cambia su
  maquetación, solo se edita un archivo.

## Autor

Angello Mathias Silva Saldaña — [LinkedIn](https://www.linkedin.com/in/angello-silva-6b980436)

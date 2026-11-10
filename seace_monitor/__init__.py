"""Monitor de convocatorias de contratación pública.

Uso rápido:
    python -m seace_monitor --demo --csv salida.csv --html reporte.html
"""

__version__ = "1.0.0"

from .models import Oferta
from .parser import parsear_resultados

__all__ = ["Oferta", "parsear_resultados", "__version__"]

"""
Importador base para cargar archivos CSV en las tablas del tablero.

Uso:
    python scripts/import_csv.py data/exportaciones_provinciales.csv exportaciones_provinciales
    python scripts/import_csv.py data/exportaciones_provinciales.csv exportaciones_provinciales --replace

Tablas soportadas:
    exportaciones_provinciales
    exportaciones_productos
    exportaciones_destinos
    precios_minerales
    balances_comerciales

Revisá docs/estructura_datos.md para ver columnas esperadas.
"""
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app import create_app, db  # noqa: E402
from app.models import ExportacionProvincial, ExportacionProducto, ExportacionDestino, PrecioMineral, BalanceComercial  # noqa: E402

MODELS = {
    "exportaciones_provinciales": ExportacionProvincial,
    "exportaciones_productos": ExportacionProducto,
    "exportaciones_destinos": ExportacionDestino,
    "precios_minerales": PrecioMineral,
    "balances_comerciales": BalanceComercial,
}


def main():
    if len(sys.argv) not in (3, 4):
        print("Uso: python scripts/import_csv.py archivo.csv nombre_tabla [--replace]")
        sys.exit(1)
    path = Path(sys.argv[1])
    table = sys.argv[2]
    replace = len(sys.argv) == 4 and sys.argv[3] == "--replace"
    if len(sys.argv) == 4 and not replace:
        print(f"Opción no soportada: {sys.argv[3]}")
        sys.exit(1)
    if table not in MODELS:
        print(f"Tabla no soportada: {table}")
        sys.exit(1)
    if not path.exists():
        print(f"No existe el archivo: {path}")
        sys.exit(1)

    df = pd.read_csv(path, sep=None, engine="python")
    app = create_app()
    Model = MODELS[table]
    with app.app_context():
        if replace:
            db.session.query(Model).delete()
        for _, row in df.iterrows():
            clean = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            clean.pop("id", None)
            db.session.add(Model(**clean))
        db.session.commit()
    action = "Reemplazadas e importadas" if replace else "Importadas"
    print(f"{action} {len(df)} filas en {table}")


if __name__ == "__main__":
    main()

# Portal de Información Provincial

Portal en **Flask + Plotly + SQLite/PostgreSQL** para consultar tableros provinciales. Actualmente incluye el módulo de minería con exportaciones mineras, precios internacionales, destinos y composición por producto.

## Qué incluye

- Login con usuario y contraseña.
- Página principal para seleccionar módulos.
- Módulo de minería disponible en `/mineria`.
- Módulo inicial de recursos provinciales preparado para futuros indicadores.
- Gráficos interactivos con Plotly.
- Carga automática de datos desde los CSV del proyecto.
- Compatibilidad con PostgreSQL mediante `DATABASE_URL`.
- Script importador de CSV.
- Configuración para despliegue en Vercel.

## Credenciales

Por defecto, para desarrollo local:

```text
Usuario: admin
Contraseña: mineria2026
```

Para producción, configurar variables de entorno:

```text
DASHBOARD_USER=usuario
DASHBOARD_PASSWORD=contraseña_segura
SECRET_KEY=clave_secreta_larga
```

## Estructura del proyecto

```text
mineria_sanjuan_dashboard/
├─ app/
│  ├─ __init__.py
│  ├─ models.py
│  ├─ routes.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ login.html
│  │  ├─ portal.html
│  │  ├─ dashboard.html
│  │  ├─ datos.html
│  │  └─ recursos_provinciales.html
│  └─ static/
│     ├─ css/styles.css
│     └─ js/dashboard.js
├─ data/
│  ├─ exportaciones_provinciales.csv
│  ├─ exportaciones_productos.csv
│  ├─ exportaciones_destinos.csv
│  ├─ precios_minerales.csv
│  └─ balances_comerciales.csv
├─ docs/
│  └─ estructura_datos.md
├─ scripts/
│  └─ import_csv.py
├─ pyproject.toml
├─ requirements.txt
├─ vercel.json
└─ run.py
```

## Instalación local en Windows

Abrí una terminal en la carpeta del proyecto y ejecutá:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\import_csv.py data/exportaciones_provinciales.csv exportaciones_provinciales --replace
python scripts\import_csv.py data/exportaciones_productos.csv exportaciones_productos --replace
python scripts\import_csv.py data/exportaciones_destinos.csv exportaciones_destinos --replace
python scripts\import_csv.py data/precios_minerales.csv precios_minerales --replace
python scripts\import_csv.py data/balances_comerciales.csv balances_comerciales --replace
python run.py
```

Después abrí:

```text
http://127.0.0.1:5000
```

## Instalación local en Linux/Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/import_csv.py data/exportaciones_provinciales.csv exportaciones_provinciales --replace
python scripts/import_csv.py data/exportaciones_productos.csv exportaciones_productos --replace
python scripts/import_csv.py data/exportaciones_destinos.csv exportaciones_destinos --replace
python scripts/import_csv.py data/precios_minerales.csv precios_minerales --replace
python scripts/import_csv.py data/balances_comerciales.csv balances_comerciales --replace
python run.py
```

## Despliegue en Vercel

El proyecto incluye `vercel.json` y `pyproject.toml`. En Vercel se crea una base SQLite temporal y se cargan automáticamente los CSV ubicados en `data/`.

En Vercel conviene configurar:

```text
DASHBOARD_USER=usuario
DASHBOARD_PASSWORD=contraseña_segura
SECRET_KEY=clave_secreta_larga
```

## Usar PostgreSQL

Crear base:

```sql
CREATE DATABASE mineria_sanjuan;
```

Configurar la variable de entorno:

```text
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/mineria_sanjuan
```

Luego ejecutar las cargas CSV con `scripts/import_csv.py` y correr la aplicación.

## Actualización de datos

Los archivos principales están en `data/`. Para actualizar el tablero, completá los CSV con las columnas indicadas en `docs/estructura_datos.md` y ejecutá:

```bash
python scripts/import_csv.py data/exportaciones_provinciales.csv exportaciones_provinciales --replace
python scripts/import_csv.py data/exportaciones_productos.csv exportaciones_productos --replace
python scripts/import_csv.py data/exportaciones_destinos.csv exportaciones_destinos --replace
python scripts/import_csv.py data/precios_minerales.csv precios_minerales --replace
python scripts/import_csv.py data/balances_comerciales.csv balances_comerciales --replace
```

## Próximas mejoras recomendadas

- Agregar roles de usuario.
- Agregar carga desde Excel con varias hojas.
- Agregar indicadores de recursos provinciales.
- Agregar módulo de escenarios de cobre para Los Azules y Vicuña.
- Agregar mapa de proyectos con coordenadas.
- Agregar comparación contra PBG, empleo, regalías y recaudación provincial.
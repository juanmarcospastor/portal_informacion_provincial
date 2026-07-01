# Estructura de datos recomendada

El tablero trabaja con una base en formato largo. Esto permite filtrar por fecha, provincia, mineral, destino y fuente sin rehacer el modelo.

## 1. exportaciones_provinciales

Archivo sugerido: `data/exportaciones_provinciales.csv`

| columna | tipo | formato / valor de referencia | comentario |
|---|---:|---|---|
| fecha | texto YYYY-MM | 2026-04 | mes de referencia |
| provincia | texto | San Juan | usar también Argentina para total nacional |
| exportaciones_mineras_usd | número | 233000000 | valor FOB minero |
| exportaciones_totales_usd | número | 256000000 | total exportado provincial; puede quedar vacío |
| variacion_interanual_pct | número | 77.9 | porcentaje, sin símbolo % |
| fuente | texto | Origen Provincial DNPEM | fuente del dato |

## 2. exportaciones_productos

Archivo sugerido: `data/exportaciones_productos.csv`

| columna | tipo | formato / valor de referencia |
|---|---:|---|
| fecha | texto YYYY-MM | 2026-04 |
| provincia | texto | San Juan |
| producto | texto | Oro |
| valor_fob_usd | número | 230000000 |
| participacion_pct | número | 99.0 |
| fuente | texto | Origen Provincial DNPEM |

## 3. exportaciones_destinos

Archivo sugerido: `data/exportaciones_destinos.csv`

| columna | tipo | formato / valor de referencia |
|---|---:|---|
| fecha | texto YYYY-MM | 2026-04 |
| provincia | texto | San Juan |
| destino | texto | Suiza |
| valor_fob_usd | número | 149000000 |
| participacion_pct | número | 64.1 |
| fuente | texto | Origen Provincial DNPEM |

## 4. precios_minerales

Archivo sugerido: `data/precios_minerales.csv`

| columna | tipo | formato / valor de referencia |
|---|---:|---|
| fecha | texto YYYY-MM | 2026-04 |
| mineral | texto | Oro |
| precio_usd | número | 4721 |
| unidad | texto | USD/Ozt |
| variacion_interanual_pct | número | 46.7 |
| variacion_mensual_pct | número | -2.8 |
| fuente | texto | Banco Mundial / DNPEM |

## 5. balances_comerciales

Archivo sugerido: `data/balances_comerciales.csv`

| columna | tipo | formato / valor de referencia |
|---|---:|---|
| fecha | texto YYYY-MM | 2026-04 |
| alcance | texto | Minerales Argentina |
| exportaciones_usd | número | 817000000 |
| importaciones_usd | número | 128000000 |
| balance_usd | número | 689000000 |
| fuente | texto | Balance Comercial de Minerales DNPEM |

## Indicadores calculados por el tablero

- Participación minera provincial = exportaciones_mineras_usd / exportaciones_totales_usd.
- Participación nacional = exportaciones_mineras_usd provincial / exportaciones_mineras_usd Argentina.

## Próximas tablas sugeridas

Cuando avances con más datos, conviene sumar:

- `proyectos_mineros`: proyecto, provincia, mineral, empresa, etapa, inversión estimada, empleo, coordenadas.
- `escenarios_cobre`: año, proyecto, producción estimada, precio cobre, exportaciones estimadas.
- `pbg_san_juan`: año, sector, valor agregado, fuente.

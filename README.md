# MLOps Prueba

Este es un proyecto de prueba para practicar MLOps y uso de GitHub.

## Contenido
- Script de Python para limpieza de datos y cálculo de indicadores.
- Archivos de ejemplo en formato CSV.

## Requisitos
- Python 3.10 o superior
- Librerías: `pandas`, `argparse`

## Ejecución
```bash
python abcd.py --csv data/sales.csv --categoria "producto" --valor "ingresos" --indicador promedio --desde 2025-01-01 --hasta 2025-12-31 --out outputs/reporte.csv

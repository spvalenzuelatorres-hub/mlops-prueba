
# -*- coding: utf-8 -*-
"""
Script de limpieza y cálculo de indicadores.
Uso:
  python main.py --csv data/sales.csv --categoria "producto" --valor "ingresos" \
                 --indicador promedio --desde 2025-01-01 --hasta 2025-12-31 \
                 --out outputs/reporte.csv
"""

import argparse
from pathlib import Path
import pandas as pd

INDICADORES_VALIDOS = {"suma", "promedio", "mediana", "conteo"}

def leer_csv(ruta: Path) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    if df.empty:
        raise ValueError("El archivo CSV está vacío.")
    return df

def limpiar_df(df: pd.DataFrame, columna_valor: str) -> pd.DataFrame:
    # Quitar duplicados completos
    df = df.drop_duplicates()

    # Intentar convertir la columna de valor a numérica
    if columna_valor not in df.columns:
        raise KeyError(f"No existe la columna de valor: {columna_valor}")
    df[columna_valor] = pd.to_numeric(df[columna_valor], errors="coerce")

    # Eliminar filas sin valor numérico
    df = df.dropna(subset=[columna_valor])

    return df

def filtrar_por_fecha(df: pd.DataFrame, desde: str | None, hasta: str | None) -> pd.DataFrame:
    # Si existe una columna de fecha común, la usamos
    posibles_fechas = [c for c in df.columns if c.lower() in {"fecha", "date", "dia", "day"}]
    if not posibles_fechas or (desde is None and hasta is None):
        return df

    col_fecha = posibles_fechas[0]
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
    df = df.dropna(subset=[col_fecha])

    if desde:
        df = df[df[col_fecha] >= pd.to_datetime(desde)]
    if hasta:
        df = df[df[col_fecha] <= pd.to_datetime(hasta)]
    return df

def calcular_indicador(df: pd.DataFrame, categoria: str, valor: str, indicador: str) -> pd.DataFrame:
    if categoria not in df.columns:
        raise KeyError(f"No existe la columna de categoría: {categoria}")
    if indicador not in INDICADORES_VALIDOS:
        raise ValueError(f"Indicador inválido. Usa uno de: {', '.join(sorted(INDICADORES_VALIDOS))}")

    g = df.groupby(categoria, dropna=False)[valor]
    if indicador == "suma":
        res = g.sum()
    elif indicador == "promedio":
        res = g.mean()
    elif indicador == "mediana":
        res = g.median()
    else:  # conteo
        res = g.count()

    return res.reset_index(name=f"{indicador}_{valor}")

def parse_args():
    p = argparse.ArgumentParser(description="Limpia datos y calcula indicadores.")
    p.add_argument("--csv", required=True, help="Ruta al CSV de entrada (p.ej., data/sales.csv)")
    p.add_argument("--categoria", required=True, help="Columna categórica para agrupar (p.ej., 'producto')")
    p.add_argument("--valor", required=True, help="Columna numérica para el indicador (p.ej., 'ingresos')")
    p.add_argument("--indicador", default="promedio", choices=sorted(INDICADORES_VALIDOS),
                   help="Indicador a calcular")
    p.add_argument("--desde", help="Fecha mínima (YYYY-MM-DD), opcional")
    p.add_argument("--hasta", help="Fecha máxima (YYYY-MM-DD), opcional")
    p.add_argument("--out", default="reporte.csv", help="Ruta de salida del reporte CSV")
    return p.parse_args()

def main():
    args = parse_args()
    ruta = Path(args.csv)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el CSV: {ruta}")

    df = leer_csv(ruta)
    df = limpiar_df(df, args.valor)
    df = filtrar_por_fecha(df, args.desde, args.hasta)
    reporte = calcular_indicador(df, args.categoria, args.valor, args.indicador)

    # Guardar
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    reporte.to_csv(out_path, index=False, encoding="utf-8")

    # Mostrar resumen en consola
    print("\n✅ Reporte generado:", out_path.resolve())
    print("\n📊 Vista previa:")
    print(reporte.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
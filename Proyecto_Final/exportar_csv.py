"""Junta la muestra de trabajo en un solo CSV (datos/muestra_completa.csv) para abrirla en Excel."""
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).parent / "datos"

df = pd.concat([pd.read_parquet(p) for p in sorted(DATOS.glob("*.parquet"))], ignore_index=True)
df["fecha"] = pd.to_datetime(df["timestamp"], unit="ms")
df.to_csv(DATOS / "muestra_completa.csv", index=False, encoding="utf-8-sig")
print(f"datos/muestra_completa.csv: {len(df):,} reseñas")

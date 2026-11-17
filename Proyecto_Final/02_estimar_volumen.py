"""
Estimación del volumen real de reseñas por categoría (2019 en adelante).

La muestra de 01_captura_datos.py tiene el mismo tamaño para cada categoría,
así que no sirve para comparar volúmenes. Para eso usamos:
    volumen 2019+ = total oficial de reseñas de la categoría
                    x proporción de reseñas de 2019+ (medida en trozos aleatorios del archivo)
Totales oficiales (#Rating): https://amazon-reviews-2023.github.io/ (tabla "Grouped by Category").
"""
import json
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from importlib import import_module
captura = import_module("01_captura_datos")

TOTAL_OFICIAL = {  # millones de reseñas, todos los años (1996 - sep 2023)
    "Electronics": 43.9, "Cell_Phones_and_Accessories": 20.8, "Home_and_Kitchen": 67.4,
    "Toys_and_Games": 16.3, "Sports_and_Outdoors": 19.6, "Tools_and_Home_Improvement": 27.0,
    "Beauty_and_Personal_Care": 23.9, "Automotive": 20.0, "Clothing_Shoes_and_Jewelry": 66.0,
    "Pet_Supplies": 16.8, "Patio_Lawn_and_Garden": 16.5, "Office_Products": 12.8,
    "Baby_Products": 6.0, "Video_Games": 4.6, "Health_and_Household": 25.6,
}
TROZOS = 300
TAM_TROZO = 16_000


def fechas_trozo(url, inicio):
    fechas = []
    for linea in captura.descargar_rango(url, inicio, TAM_TROZO).split("\n")[1:-1]:
        try:
            fechas.append(json.loads(linea)["timestamp"])
        except (json.JSONDecodeError, KeyError):
            pass
    return fechas


def main():
    tamanos = {f["path"].split("/")[-1][:-6]: f["size"] for f in requests.get(captura.TREE, timeout=60).json()}
    filas = []
    for cat, total in TOTAL_OFICIAL.items():
        url = captura.BASE + cat + ".jsonl"
        rng = random.Random(f"{captura.SEMILLA}-volumen-{cat}")
        inicios = [rng.randrange(0, tamanos[cat] - TAM_TROZO) for _ in range(TROZOS)]
        with ThreadPoolExecutor(8) as ex:
            fechas = pd.to_datetime([f for t in ex.map(lambda i: fechas_trozo(url, i), inicios) for f in t], unit="ms")
        prop = (fechas >= captura.DESDE).mean()
        filas.append({"category": cat, "total_oficial_millones": total, "prop_2019": round(prop, 3),
                      "resenas_2019_millones": round(total * prop, 2), "n_medidas": len(fechas)})
        print(filas[-1])
    pd.DataFrame(filas).to_csv(Path(__file__).parent / "datos" / "volumen_categorias.csv", index=False)


if __name__ == "__main__":
    main()

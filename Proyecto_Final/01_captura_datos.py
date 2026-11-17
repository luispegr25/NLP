"""
Captura de datos: Amazon Reviews 2023 (McAuley Lab, UC San Diego)
https://amazon-reviews-2023.github.io/

Cada categoría es un archivo JSONL de varios GB, agrupado por usuario.
Tomar las primeras N filas daría una muestra sesgada (pocos usuarios),
así que leemos trozos en posiciones aleatorias del archivo
(HTTP Range requests) y tomamos las reseñas completas de cada trozo.
Resultado: una muestra aleatoria de cada categoría sin descargar el archivo completo.
"""
import json
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

BASE = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/"
TREE = "https://huggingface.co/api/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw/review_categories"

CATEGORIAS = [
    "Electronics", "Cell_Phones_and_Accessories", "Home_and_Kitchen", "Toys_and_Games",
    "Sports_and_Outdoors", "Tools_and_Home_Improvement", "Beauty_and_Personal_Care",
    "Automotive", "Clothing_Shoes_and_Jewelry", "Pet_Supplies", "Patio_Lawn_and_Garden",
    "Office_Products", "Baby_Products", "Video_Games", "Health_and_Household",
]
POR_CATEGORIA = 20_000   # reseñas por categoría
TROZOS = 1000            # posiciones aleatorias por archivo
TAM_TROZO = 80_000       # bytes leídos en cada posición
PAUSA = 0.11             # segundos mínimos entre solicitudes (límite de Hugging Face)
SEMILLA = 42
DESDE = pd.Timestamp("2019-01-01")  # solo los últimos ~5 años: la decisión es sobre la situación actual

SALIDA = Path(__file__).parent / "datos"
SALIDA.mkdir(exist_ok=True)


_candado = threading.Lock()
_ultima = [0.0]


def respetar_limite():
    # Hugging Face permite 3,000 solicitudes cada 5 minutos (10 por segundo): nos quedamos por debajo
    with _candado:
        espera = _ultima[0] + PAUSA - time.monotonic()
        if espera > 0:
            time.sleep(espera)
        _ultima[0] = time.monotonic()


def descargar_rango(url, inicio, tam):
    # si una solicitud falla, reintentamos con espera creciente
    for intento in range(6):
        respetar_limite()
        try:
            r = requests.get(url, headers={"Range": f"bytes={inicio}-{inicio + tam}"}, timeout=60)
            if r.status_code == 206:
                return r.text
        except requests.RequestException:
            pass
        time.sleep(2 ** intento)
    return ""


def leer_trozo(url, inicio):
    lineas = descargar_rango(url, inicio, TAM_TROZO).split("\n")[1:-1]  # la primera y la última pueden venir cortadas
    filas = []
    for linea in lineas:
        try:
            filas.append(json.loads(linea))
        except json.JSONDecodeError:
            pass
    return filas


def muestrear(categoria, tamano_archivo):
    url = BASE + categoria + ".jsonl"
    rng = random.Random(f"{SEMILLA}-{categoria}")  # semilla propia: la muestra no depende del orden de descarga
    inicios = sorted(rng.randrange(0, tamano_archivo - TAM_TROZO) for _ in range(TROZOS))
    with ThreadPoolExecutor(8) as ex:
        trozos = list(ex.map(lambda i: leer_trozo(url, i), inicios))
    filas = [f for t in trozos for f in t]
    df = pd.DataFrame(filas).drop(columns=["images"], errors="ignore")
    df = df.drop_duplicates(subset=["user_id", "asin", "timestamp"])
    df = df[pd.to_datetime(df["timestamp"], unit="ms") >= DESDE]
    df = df.sample(n=min(POR_CATEGORIA, len(df)), random_state=SEMILLA)
    df["category"] = categoria
    return df


def main():
    tamanos = {f["path"].split("/")[-1][:-6]: f["size"] for f in requests.get(TREE, timeout=60).json()}
    cats = sys.argv[1:] or CATEGORIAS
    for cat in cats:
        destino = SALIDA / f"{cat}.parquet"
        if destino.exists():
            print(f"{cat}: ya existe, se omite")
            continue
        df = muestrear(cat, tamanos[cat])
        df.to_parquet(destino, index=False)
        print(f"{cat}: {len(df):,} reseñas")


if __name__ == "__main__":
    main()

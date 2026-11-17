"""
Extracto crudo del dataset original, tal cual viene de la fuente (sin ningún cambio).

Guarda el primer MB (unas 1,200 a 1,900 reseñas) de cada archivo original (.jsonl) de Amazon Reviews 2023,
byte por byte, para poder inspeccionar el formato original de los datos.
Los archivos completos pesan de 4 a 31 GB cada uno; se descargan desde:
https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw/review_categories
"""
from importlib import import_module
from pathlib import Path

captura = import_module("01_captura_datos")

BYTES = 1_000_000  # primer MB de cada archivo
CRUDOS = Path(__file__).parent / "datos_crudos"
CRUDOS.mkdir(exist_ok=True)

for cat in captura.CATEGORIAS:
    texto = captura.descargar_rango(captura.BASE + cat + ".jsonl", 0, BYTES)
    lineas = texto.split("\n")[:-1]  # la última línea puede venir cortada
    (CRUDOS / f"{cat}_extracto_original.jsonl").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{cat}: {len(lineas):,} reseñas originales")

"""
Construye la presentación final (presentacion/index.html) con los resultados del notebook.

Entradas: dashboard/datos.json, dashboard/textos.json, dashboard/modelo.json, datos/*.parquet
          y presentacion/plantilla.html
Salida:   presentacion/index.html (se abre en el navegador; flechas para avanzar, F para pantalla completa)
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).parent
# Botón "Abrir el dashboard" de la diapositiva de demo. Cuando esté en Render, poner aquí su dirección
# (por ejemplo "https://sar-resenas.onrender.com"); mientras tanto abre la copia local.
URL_DASHBOARD = "../dashboard/index.html"
DASH = RAIZ / "dashboard"
PRES = RAIZ / "presentacion"

datos = json.loads((DASH / "datos.json").read_text())
textos = json.loads((DASH / "textos.json").read_text())
modelo = json.loads((DASH / "modelo.json").read_text())

for cat in datos["categorias"]:
    cat["frases"] = [{"en": f, "es": textos["frases"].get(f, f)} for f in cat["frases"]]
    cat.pop("ejemplos", None)
    cat.pop("tendencia", None)
datos["recomendacion"] = textos["recomendacion"]

# distribución de estrellas de la muestra completa
muestra = pd.concat([pd.read_parquet(p, columns=["rating"]) for p in sorted((RAIZ / "datos").glob("*.parquet"))])
datos["estrellas"] = (muestra["rating"].value_counts(normalize=True).sort_index() * 100).round(1).tolist()

# términos con más peso hacia cada clase en la Regresión Logística
datos["palabras"] = {
    clase: [t for t, _ in sorted(modelo["vocab"].items(), key=lambda kv: -kv[1][k + 1])[:10]]
    for k, clase in enumerate(modelo["clases"])
}

cuerpo = (PRES / "plantilla.html").read_text().replace(
    "/*__DATOS__*/", json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")).replace("__URL_DASHBOARD__", URL_DASHBOARD)
cabeza, resto = cuerpo.split('<div class="escenario">', 1)
html = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + cabeza + '</head>\n<body>\n<div class="escenario">' + resto + "\n</body>\n</html>\n")
(PRES / "index.html").write_text(html)
print(f"presentacion/index.html: {len(html) / 1e3:.0f} KB")

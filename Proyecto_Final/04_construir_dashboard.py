"""
Construye el dashboard web a partir de los resultados del notebook.

Entradas:
    dashboard/datos.json         resultados por categoría (exportados por el notebook)
    dashboard/modelo.json        vocabulario, IDF y pesos de la Regresión Logística
    dashboard/textos.json        traducciones al español y textos de la recomendación
    dashboard/plantilla.html     diseño del dashboard
Salida:
    dashboard/index.html         página lista para publicar (Vercel, Render o abrir en el navegador)
"""
import json
from pathlib import Path

DASH = Path(__file__).parent / "dashboard"

datos = json.loads((DASH / "datos.json").read_text())
textos = json.loads((DASH / "textos.json").read_text())
modelo = (DASH / "modelo.json").read_text()

faltan = []
for cat in datos["categorias"]:
    cat["frases"] = [{"en": f, "es": textos["frases"].get(f, f)} for f in cat["frases"]]
    for ej in cat["ejemplos"]:
        tr = textos["ejemplos"].get(ej["clave"])
        if tr is None:
            faltan.append(ej["clave"])
            tr = {"titulo": ej["titulo"], "texto": ej["texto"]}
        ej["titulo_es"], ej["texto_es"] = tr["titulo"], tr["texto"]
    cat.pop("margen", None)

datos.update({k: textos[k] for k in ["recomendacion", "hallazgo", "metodo", "ejemplos_modelo"]})
datos_txt = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

cuerpo = ((DASH / "plantilla.html").read_text()
          .replace("/*__DATOS__*/", datos_txt)
          .replace("/*__MODELO__*/", modelo))
cabeza, resto = cuerpo.split('<div class="pagina">', 1)  # título, fuentes y estilos van en <head>
html = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + cabeza + '</head>\n<body>\n<div class="pagina">' + resto + "\n</body>\n</html>\n")
(DASH / "index.html").write_text(html)
print(f"dashboard/index.html: {len(html) / 1e6:.1f} MB")
if faltan:
    print(f"Aviso: {len(faltan)} reseñas de ejemplo sin traducción")

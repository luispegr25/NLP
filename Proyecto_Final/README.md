# SAR · Sistema de Análisis de Reseñas

**Proyecto final · Procesamiento de Lenguaje Natural · Luis Pedro González**

De cientos de miles de reseñas a una decisión de negocio: **¿a qué 3 categorías les asigno primero el presupuesto de mejora y qué problema ataco en cada una?**

**Dashboard:** _(enlace de Render)_

---

## El problema

| | |
|---|---|
| **Usuario final** | Gerente de categorías / equipo de experiencia del cliente de una tienda en línea |
| **Decisión** | A qué 3 categorías asignar primero el presupuesto de mejora y qué problema atacar en cada una |
| **Por qué NLP** | Las estrellas dicen *cuánto* molesta algo, pero no *qué* molesta. La causa está escrita en el texto, y nadie puede leer millones de reseñas a mano. |
| **Producto** | Dashboard web con el ranking de prioridad, las causas, la evolución por año, reseñas de ejemplo y un clasificador de sentimiento en vivo |

## Resultado

| # | Categoría | Reseñas negativas estimadas 2019-2023 | Problema a atacar |
|---|---|---|---|
| 1 | Hogar y cocina | 7.5 millones (16.9 %) | Se rompe / mala calidad (28 % de las quejas) |
| 2 | Ropa, zapatos y joyería | 6.8 millones (16.2 %) | La talla no corresponde (36 %) |
| 3 | Electrónica | 4.2 millones (19.5 %) | Deja de funcionar (20 %) y batería o carga (16 %) |

- **El porcentaje solo no alcanza:** por % de quejas, la prioridad sería Patio y jardín, Videojuegos y Celulares. Hogar y cocina está en el puesto 11 por porcentaje, pero tiene 19 veces más quejas que Videojuegos.
- **La decisión es estable:** son las mismas 3 prioridades en cada año de 2019 a 2023, y las tres empeoraron entre 4 y 5 puntos.
- **El modelo aporta:** la Regresión Logística (F1 macro 0.69) supera a Naive Bayes (0.63) y a una regla de palabras clave (0.50). Sin ver las estrellas, el modelo llega a las mismas 3 prioridades y estima el total de quejas con un error del 1 %; la regla lo infla un 43 %.

## Datos

**Amazon Reviews 2023** (McAuley Lab, UC San Diego): reseñas reales con su distribución natural. Ver [FUENTE_DE_DATOS.md](FUENTE_DE_DATOS.md) para la fuente, la cita, los campos y cómo se capturó la muestra.

- 15 categorías × 20,000 reseñas al azar de 2019 a 2023 = **300,000 reseñas** (295,439 después de la limpieza)
- Los datos están en inglés; todo el análisis, el dashboard y la documentación están en español.

## Estructura

| Archivo / carpeta | Qué contiene |
|---|---|
| [`03_analisis_sar.ipynb`](03_analisis_sar.ipynb) | **El análisis completo**, ya ejecutado: captura, exploración, limpieza, modelado, decisión y limitaciones |
| `01_captura_datos.py` | Descarga la muestra aleatoria de cada categoría |
| `01b_extracto_crudo.py` | Guarda un extracto de los archivos originales sin modificar |
| `02_estimar_volumen.py` | Estima cuántas reseñas reales tiene cada categoría desde 2019 |
| `04_construir_dashboard.py` | Genera `dashboard/index.html` a partir de los resultados del notebook |
| `05_construir_presentacion.py` | Genera la presentación final (`presentacion/index.html`) con los mismos resultados |
| `exportar_csv.py` | Genera `datos/muestra_completa.csv` para abrir la muestra en Excel |
| `datos/` | La muestra de trabajo (un parquet por categoría), y el volumen real estimado por categoría |
| `datos_crudos/` | Extractos de los archivos originales, tal cual vienen de la fuente |
| `figuras/` | Las gráficas del notebook |
| `dashboard/` | El dashboard (`index.html`) y sus insumos |
| `presentacion/` | La presentación final: abrir `index.html` en el navegador (flechas para avanzar, F para pantalla completa) |

## Cómo reproducirlo

```bash
pip install -r requirements.txt
python 01_captura_datos.py        # ~40 min: respeta el límite de solicitudes de Hugging Face
python 01b_extracto_crudo.py
python 02_estimar_volumen.py
jupyter nbconvert --to notebook --execute --inplace 03_analisis_sar.ipynb
python 04_construir_dashboard.py
python 05_construir_presentacion.py
```

Los datos ya vienen incluidos, así que basta con abrir el notebook o `dashboard/index.html` en el navegador.

## Técnicas del curso

Normalización de texto y stopwords (conservando negaciones), TF-IDF con unigramas y bigramas, Naive Bayes, Regresión Logística, evaluación con entrenamiento / validación / prueba, F1 macro, matriz de confusión, análisis de errores e interpretación de pesos.

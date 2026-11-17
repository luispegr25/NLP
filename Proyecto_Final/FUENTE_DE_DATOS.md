# Fuente de datos: Amazon Reviews 2023

## Por qué este dataset

Para una decisión de negocio los porcentajes y volúmenes tienen que reflejar lo que pasa en realidad. Este dataset
conserva la **distribución natural** de las reseñas de Amazon (sin balancear las estrellas), trae fecha, producto y
votos de "útil", y es de una fuente académica reconocida. Los datos están en inglés; el análisis, el dashboard y la
presentación están en español.

## El dataset

| | |
|---|---|
| **Nombre** | Amazon Reviews 2023 |
| **Autores** | McAuley Lab, University of California San Diego (Hou, Li, He, Yan, Chen y McAuley) |
| **Artículo** | *Bridging Language and Items for Retrieval and Recommendation*, arXiv:2403.03952 (2024) |
| **Página oficial** | https://amazon-reviews-2023.github.io/ |
| **Descarga** | https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023 |
| **Tamaño total** | 571.54 millones de reseñas, 33 categorías, de mayo 1996 a septiembre 2023 |
| **Distribución** | La real de Amazon.com (EE. UU.), sin balanceo artificial |
| **Formato original** | Un archivo JSON Lines (`.jsonl`) por categoría, una reseña por línea |
| **Uso** | Publicado para investigación académica. Se cita el artículo de arriba. |

### Campos originales de cada reseña

| Campo | Descripción |
|---|---|
| `rating` | Estrellas, de 1.0 a 5.0 |
| `title` | Título de la reseña |
| `text` | Texto de la reseña |
| `images` | Fotos que subió el cliente (no se usan) |
| `asin` / `parent_asin` | Identificador del producto (`parent_asin` agrupa variantes de color o talla) |
| `user_id` | Identificador anónimo del cliente |
| `timestamp` | Fecha y hora en milisegundos (Unix) |
| `helpful_vote` | Cuántas personas marcaron la reseña como útil |
| `verified_purchase` | Si la compra fue verificada por Amazon |

Ejemplo real (primera línea del archivo original de *Electronics*): ver `datos_crudos/Electronics_extracto_original.jsonl`.

## Cómo se capturaron los datos

Los 15 archivos de las categorías elegidas pesan en total cerca de **200 GB**, así que no se descargaron completos.

1. **`01_captura_datos.py`**: de cada categoría lee **1,000 trozos en posiciones aleatorias** del archivo original
   (solicitudes HTTP con rango de bytes) y toma **20,000 reseñas al azar de 2019 en adelante**.
   Los archivos vienen agrupados por cliente. Tomar las primeras filas daría una muestra de pocos clientes, y las posiciones
   aleatorias evitan ese sesgo. El script respeta el límite de solicitudes de Hugging Face.
2. **`02_estimar_volumen.py`**: estima cuántas reseñas reales tiene cada categoría desde 2019
   (total oficial × proporción de reseñas de 2019+), porque la muestra tiene el mismo tamaño por categoría.
3. **`01b_extracto_crudo.py`**: guarda las primeras reseñas (1 MB, entre 1,177 y 1,891) de cada archivo original **tal cual**,
   sin ningún cambio, para inspeccionar el formato original.

## Archivos en esta carpeta

| Carpeta / archivo | Contenido |
|---|---|
| `datos_crudos/*_extracto_original.jsonl` | Primer MB de cada archivo original (1,177 a 1,891 reseñas), sin tocar, byte por byte como viene de la fuente |
| `datos/*.parquet` | La muestra de trabajo: 20,000 reseñas por categoría (2019-2023), con los campos originales (sin `images`) |
| `datos/muestra_completa.csv` | La misma muestra (300,000 reseñas) en un solo CSV para abrirla en Excel, con una columna `fecha` legible. No se sube a GitHub por su tamaño (~90 MB); se genera con `python exportar_csv.py` |
| `datos/volumen_categorias.csv` | Volumen real estimado por categoría |

## Categorías usadas (15)

Electronics, Cell Phones and Accessories, Home and Kitchen, Toys and Games, Sports and Outdoors,
Tools and Home Improvement, Beauty and Personal Care, Automotive, Clothing Shoes and Jewelry, Pet Supplies,
Patio Lawn and Garden, Office Products, Baby Products, Video Games, Health and Household.

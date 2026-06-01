# 🚀 Análisis de Ventas con PySpark + Dashboard Streamlit

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)](https://python.org)
[![PySpark](https://img.shields.io/badge/PySpark-3.5.1-orange?logo=apache-spark)](https://spark.apache.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema completo para procesar datos de ventas con **Apache Spark (PySpark)** y visualizarlos con un **Dashboard interactivo en Streamlit**.

---

## 📋 Descripción del Proyecto

Una empresa recibe diariamente un archivo CSV con información de ventas. Este proyecto:

| Paso | Tarea |
|------|-------|
| 1️⃣ | Carga el CSV con PySpark |
| 2️⃣ | Calcula `total_venta = cantidad × precio` |
| 3️⃣ | Muestra el resultado en consola |
| 4️⃣ | Guarda los datos en formato **Parquet** |
| 5️⃣ | Visualiza todo en un **dashboard interactivo** |

---

## 🗂️ Estructura del Proyecto

```
agente/
├── ventas.csv                  # Datos de entrada
├── pyspark_ventas.py           # Script PySpark principal
├── app.py                      # Dashboard Streamlit
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
├── tutorial_pyspark.md         # Tutorial paso a paso
└── output/
    └── ventas_procesadas.parquet/   # Salida generada por PySpark
```

---

## ⚙️ Requisitos Previos

- **Python** 3.10 o superior
- **Java JDK 11+** (requerido por Apache Spark)
- pip actualizado

### Verificar Java

```bash
java -version
```

Si no tienes Java, descárgalo desde [adoptium.net](https://adoptium.net/).

---

## 🛠️ Instalación

```bash
# 1. Clonar/descargar el repositorio
cd agente

# 2. Crear entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## ▶️ Ejecución

### Paso 1 – Procesar datos con PySpark

```bash
python pyspark_ventas.py
```

**Salida esperada en consola:**

```
📂  Schema del CSV cargado:
root
 |-- id_venta: integer (nullable = true)
 |-- producto: string (nullable = true)
 |-- cantidad: integer (nullable = true)
 |-- precio: integer (nullable = true)

📋  Datos originales:
+--------+--------+--------+------+
|id_venta|producto|cantidad|precio|
+--------+--------+--------+------+
|       1|  Laptop|       2|  2500|
|       2|   Mouse|       5|    50|
|       3| Teclado|       3|   120|
+--------+--------+--------+------+

✅  Datos con total_venta calculado:
+--------+--------+--------+------+-----------+
|id_venta|producto|cantidad|precio|total_venta|
+--------+--------+--------+------+-----------+
|       1|  Laptop|       2|  2500|       5000|
|       2|   Mouse|       5|    50|        250|
|       3| Teclado|       3|   120|        360|
+--------+--------+--------+------+-----------+

💾  Archivo Parquet guardado en: output/ventas_procesadas.parquet
```

### Paso 2 – Lanzar el Dashboard

```bash
streamlit run app.py
```

Abre tu navegador en `http://localhost:8501` 🎉

---

## 📊 Características del Dashboard

| Sección | Descripción |
|---------|-------------|
| 🎛️ Sidebar | Selector de fuente (Parquet/CSV), recarga de datos |
| 📈 KPI Cards | Ingresos totales, productos, venta máxima, estrella |
| 📊 Barras horizontales | Total de venta por producto |
| 🍕 Donut chart | Distribución porcentual de ingresos |
| 📦 Barras verticales | Cantidad vendida por producto |
| 🔵 Scatter plot | Precio vs Total de Venta (tamaño = cantidad) |
| 📋 Tabla completa | Todos los datos formateados |

---

## 🧪 Datos de Ejemplo

| id_venta | producto | cantidad | precio | total_venta |
|----------|----------|----------|--------|-------------|
| 1 | Laptop | 2 | $2,500 | **$5,000** |
| 2 | Mouse | 5 | $50 | **$250** |
| 3 | Teclado | 3 | $120 | **$360** |

---

## 🔧 Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Apache Spark / PySpark | 3.5.1 | ETL distribuido |
| Pandas | 2.2.2 | Análisis local |
| PyArrow | 16.0.0 | Lectura Parquet |
| Streamlit | 1.35.0 | Dashboard web |
| Plotly | 5.22.0 | Visualizaciones interactivas |

---

## 📄 Licencia

MIT © 2024 – Proyecto educativo de análisis de datos con PySpark.

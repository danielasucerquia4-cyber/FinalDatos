# 📘 Tutorial Paso a Paso: PySpark + Streamlit Dashboard

> **Objetivo:** Entender desde cero cómo procesar datos con Apache Spark (PySpark), guardarlos en Parquet y visualizarlos en un dashboard web interactivo.

---

## 🗺️ Índice

1. [¿Qué es PySpark?](#1-qué-es-pyspark)
2. [Arquitectura del pipeline](#2-arquitectura-del-pipeline)
3. [Configurar el entorno](#3-configurar-el-entorno)
4. [Crear el archivo CSV](#4-crear-el-archivo-csv)
5. [Iniciar una SparkSession](#5-iniciar-una-sparksession)
6. [Cargar el CSV con PySpark](#6-cargar-el-csv-con-pyspark)
7. [Transformar los datos (columna calculada)](#7-transformar-los-datos-columna-calculada)
8. [Mostrar el resultado](#8-mostrar-el-resultado)
9. [Guardar en formato Parquet](#9-guardar-en-formato-parquet)
10. [Visualizar con Streamlit](#10-visualizar-con-streamlit)
11. [Conceptos clave de PySpark](#11-conceptos-clave-de-pyspark)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)

---

## 1. ¿Qué es PySpark?

**Apache Spark** es un motor de procesamiento de datos distribuido capaz de manejar petabytes de información.  
**PySpark** es su API oficial para Python.

```
Ventajas de PySpark:
┌─────────────────────────────────────────────────────┐
│  ⚡ Velocidad    → Procesa datos en memoria RAM      │
│  📈 Escalable   → De 1 máquina a miles de nodos     │
│  🐍 Python API  → Familiar para científicos de datos│
│  🗂️ Multi-formato → CSV, JSON, Parquet, Delta Lake  │
└─────────────────────────────────────────────────────┘
```

---

## 2. Arquitectura del Pipeline

```
ventas.csv
    │
    ▼
┌─────────────────────┐
│   SparkSession      │  ← Motor de Spark (local o cluster)
└────────┬────────────┘
         │  spark.read.csv()
         ▼
┌─────────────────────┐
│   DataFrame Spark   │  ← Tabla distribuida (inmutable)
│  id_venta │ producto│
│  cantidad │ precio  │
└────────┬────────────┘
         │  .withColumn("total_venta", col("cantidad") * col("precio"))
         ▼
┌─────────────────────┐
│  DataFrame Procesado│
│  + total_venta      │
└────────┬────────────┘
         │  .write.parquet()
         ▼
┌─────────────────────┐
│  output/            │
│  ventas_procesadas  │  ← Archivos Parquet comprimidos
│  .parquet/          │
└────────┬────────────┘
         │  pandas.read_parquet()
         ▼
┌─────────────────────┐
│  Dashboard Streamlit│  ← Visualización interactiva
│  Plotly Charts      │
└─────────────────────┘
```

---

## 3. Configurar el Entorno

### 3.1 Instalar Java (requisito de Spark)

Apache Spark está escrito en Scala/JVM; necesita Java 11+.

```bash
# Verificar si Java está instalado
java -version

# Si no está instalado, descargar desde:
# https://adoptium.net/temurin/releases/
```

En Windows, después de instalar Java, configura la variable de entorno:

```
Variable: JAVA_HOME
Valor:    C:\Program Files\Eclipse Adoptium\jdk-11.x.x.x-hotspot
```

### 3.2 Crear entorno virtual Python

```bash
# Crear entorno aislado
python -m venv .venv

# Activar (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activar (Windows CMD)
.venv\Scripts\activate.bat

# Activar (Linux/Mac)
source .venv/bin/activate
```

### 3.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

Las librerías que se instalan:

| Paquete | Para qué sirve |
|---------|---------------|
| `pyspark` | Motor de procesamiento distribuido |
| `pandas` | Manipulación de datos en Python |
| `pyarrow` | Leer/escribir formato Parquet |
| `streamlit` | Crear el dashboard web |
| `plotly` | Gráficos interactivos |

---

## 4. Crear el Archivo CSV

El archivo `ventas.csv` contiene los datos de entrada:

```csv
id_venta,producto,cantidad,precio
1,Laptop,2,2500
2,Mouse,5,50
3,Teclado,3,120
```

> **Nota:** En producción este archivo llegaría automáticamente cada día desde un sistema ERP, FTP, S3, etc.

---

## 5. Iniciar una SparkSession

La `SparkSession` es el punto de entrada a todas las funcionalidades de Spark.

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("AnalisisVentas")   # Nombre que aparece en la Spark UI
    .master("local[*]")          # Usar todos los núcleos del CPU local
    .getOrCreate()               # Crear o reutilizar sesión existente
)
```

### ¿Qué significa `local[*]`?

| Master | Descripción |
|--------|-------------|
| `local` | 1 hilo (sin paralelismo) |
| `local[2]` | 2 hilos paralelos |
| `local[*]` | Todos los núcleos disponibles |
| `spark://host:7077` | Cluster Spark real |

---

## 6. Cargar el CSV con PySpark

```python
df = (
    spark.read
    .option("header", "true")       # Primera fila = nombres de columnas
    .option("inferSchema", "true")  # Detectar tipos (int, string, float...)
    .csv("ventas.csv")
)
```

### Opciones importantes de lectura

| Opción | Valor | Efecto |
|--------|-------|--------|
| `header` | `true/false` | Usar primera fila como cabecera |
| `inferSchema` | `true/false` | Detectar tipos automáticamente |
| `sep` | `,` `;` `\t` | Separador de columnas |
| `encoding` | `UTF-8` | Codificación del archivo |
| `nullValue` | `"NA"` | String que representa nulo |

### Verificar el esquema

```python
df.printSchema()
# root
#  |-- id_venta: integer (nullable = true)
#  |-- producto: string (nullable = true)
#  |-- cantidad: integer (nullable = true)
#  |-- precio: integer (nullable = true)
```

> **¿Por qué importa el schema?** Spark necesita conocer los tipos de datos para optimizar las operaciones. Con `inferSchema=false` todo sería `string`.

---

## 7. Transformar los Datos (Columna Calculada)

```python
from pyspark.sql.functions import col

df_procesado = df.withColumn(
    "total_venta",           # Nombre de la nueva columna
    col("cantidad") * col("precio")   # Expresión de cálculo
)
```

### Concepto clave: Inmutabilidad

Los DataFrames de Spark son **inmutables**. `withColumn()` **no modifica** `df`, sino que devuelve un **nuevo** DataFrame con la columna extra.

```
df (original)          df_procesado (nuevo)
┌──────────────┐       ┌──────────────────────┐
│ id_venta     │       │ id_venta             │
│ producto     │  ───► │ producto             │
│ cantidad     │       │ cantidad             │
│ precio       │       │ precio               │
└──────────────┘       │ total_venta  ← NUEVA │
                       └──────────────────────┘
```

### Otras transformaciones comunes con PySpark

```python
from pyspark.sql.functions import col, round, when, lit

# Redondear
df.withColumn("precio_iva", round(col("precio") * 1.16, 2))

# Columna condicional
df.withColumn("categoria",
    when(col("total_venta") > 1000, "Alto")
    .when(col("total_venta") > 500, "Medio")
    .otherwise("Bajo")
)

# Filtrar filas
df.filter(col("cantidad") > 2)

# Agrupar y agregar
df.groupBy("producto").agg({"total_venta": "sum"})
```

---

## 8. Mostrar el Resultado

```python
df_procesado.show()
```

**Salida:**

```
+--------+--------+--------+------+-----------+
|id_venta|producto|cantidad|precio|total_venta|
+--------+--------+--------+------+-----------+
|       1|  Laptop|       2|  2500|       5000|
|       2|   Mouse|       5|    50|        250|
|       3| Teclado|       3|   120|        360|
+--------+--------+--------+------+-----------+
```

### Concepto: Evaluación Perezosa (Lazy Evaluation)

Spark **no ejecuta** ningún cálculo hasta que llamas a una **acción** como `.show()`, `.count()`, o `.write`.

```
Transformaciones (lazy):    Acciones (ejecutan el plan):
  .read.csv()     ─┐          .show()
  .withColumn()   ─┤  ─────►  .count()
  .filter()       ─┘          .write.parquet()
                  Plan         Ejecución real
```

Esto permite a Spark **optimizar** todo el pipeline antes de ejecutarlo (Catalyst Optimizer).

---

## 9. Guardar en Formato Parquet

```python
df_procesado.write.mode("overwrite").parquet("output/ventas_procesadas.parquet")
```

### ¿Por qué Parquet?

| Característica | CSV | Parquet |
|---------------|-----|---------|
| Formato | Texto plano | Binario columnar |
| Tamaño | Grande | **3-10x más pequeño** |
| Velocidad de lectura | Lenta | **Muy rápida** |
| Tipos de datos | No | **Sí (preservados)** |
| Compresión | No | **Snappy/GZIP** |
| Compatible con | Cualquier cosa | Spark, Pandas, BigQuery, Athena... |

### Modos de escritura

| Modo | Comportamiento |
|------|---------------|
| `overwrite` | Elimina y reescribe |
| `append` | Añade al final |
| `ignore` | No hace nada si existe |
| `error` | Lanza error si existe (default) |

### ¿Qué genera Spark en disco?

```
output/ventas_procesadas.parquet/
├── _SUCCESS                     ← Indicador de éxito
├── part-00000-xxxx.snappy.parquet  ← Partición 1
└── part-00001-xxxx.snappy.parquet  ← Partición 2 (si hay >1 núcleo)
```

> **Nota:** Spark divide la salida en múltiples archivos (*partitions*) para paralelizar la escritura. Pandas puede leerlos todos automáticamente.

---

## 10. Visualizar con Streamlit

El dashboard se conecta directamente a los archivos Parquet generados por PySpark.

```python
import glob
import pandas as pd

# Leer todos los part-files de Parquet
archivos = glob.glob("output/ventas_procesadas.parquet/*.parquet")
df = pd.concat([pd.read_parquet(f) for f in archivos])
```

### Ejecutar el dashboard

```bash
streamlit run app.py
```

El dashboard ofrece:
- **4 KPI Cards** con métricas clave
- **Gráfico de barras** – ingresos por producto
- **Donut chart** – distribución de ingresos
- **Scatter plot** – precio vs. total de venta
- **Tabla interactiva** – todos los datos formateados

---

## 11. Conceptos Clave de PySpark

### DataFrame vs RDD

| | DataFrame | RDD |
|-|-----------|-----|
| Nivel | Alto nivel (SQL-like) | Bajo nivel |
| Optimización | Automática (Catalyst) | Manual |
| Uso recomendado | ✅ Siempre que puedas | Solo casos especiales |

### Particiones

Spark divide los datos en particiones para procesarlas en paralelo:

```python
# Ver número de particiones
df.rdd.getNumPartitions()   # Típicamente = núcleos CPU

# Reparticionar (útil antes de guardar)
df.repartition(1)  # Un solo archivo de salida
df.coalesce(2)     # Reducir particiones eficientemente
```

### Spark UI

Mientras Spark ejecuta, puedes ver el progreso en:
```
http://localhost:4040
```

---

## 12. Preguntas Frecuentes

**❓ ¿Por qué Spark tarda más que Pandas con datos pequeños?**  
Spark tiene un overhead de inicio (JVM, planificador). Es más eficiente con **millones de filas**. Para menos de 100k filas, Pandas es más rápido.

**❓ ¿Puedo usar PySpark sin un cluster?**  
Sí. Con `master("local[*]")` Spark corre en tu máquina local usando múltiples hilos.

**❓ ¿Qué pasa si el CSV tiene valores nulos?**  
```python
df.na.fill({"cantidad": 0, "precio": 0})   # Rellenar nulos
df.na.drop()                                # Eliminar filas con nulos
```

**❓ ¿Cómo leer el Parquet generado con Pandas?**  
```python
import pandas as pd
df = pd.read_parquet("output/ventas_procesadas.parquet")
```

**❓ ¿Puedo procesar múltiples CSVs a la vez?**  
```python
df = spark.read.csv("data/*.csv", header=True, inferSchema=True)
```

---

> 💡 **Próximos pasos recomendados:**  
> - Conectar a una base de datos real (PostgreSQL, MySQL) con JDBC  
> - Usar **Spark Structured Streaming** para datos en tiempo real  
> - Desplegar en **Databricks** o **AWS EMR** para escalar a Big Data  
> - Añadir pruebas con `pytest` + `chispa` (testing de PySpark)

"""
pyspark_ventas.py
-----------------
Script PySpark que:
  1. Carga ventas.csv
  2. Calcula total_venta = cantidad * precio
  3. Muestra el resultado en consola
  4. Guarda los datos procesados en formato Parquet
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# ─────────────────────────────────────────────
# 1. Crear sesión Spark
# ─────────────────────────────────────────────
spark = (
    SparkSession.builder
    .appName("AnalisisVentas")
    .master("local[*]")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# ─────────────────────────────────────────────
# 2. Cargar el archivo CSV
# ─────────────────────────────────────────────
df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv("ventas.csv")
)

print("\n📂  Schema del CSV cargado:")
df.printSchema()

print("📋  Datos originales:")
df.show()

# ─────────────────────────────────────────────
# 3. Calcular nueva columna total_venta
# ─────────────────────────────────────────────
df_procesado = df.withColumn(
    "total_venta",
    col("cantidad") * col("precio")
)

print("✅  Datos con total_venta calculado:")
df_procesado.show()

# ─────────────────────────────────────────────
# 4. Guardar en formato Parquet
# ─────────────────────────────────────────────
OUTPUT_PATH = "output/ventas_procesadas.parquet"

df_procesado.write.mode("overwrite").parquet(OUTPUT_PATH)
print(f"💾  Archivo Parquet guardado en: {OUTPUT_PATH}")

spark.stop()

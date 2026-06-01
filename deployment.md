# 🚀 Guía de Despliegue – PySpark Ventas + Streamlit Dashboard

> Esta guía cubre tres escenarios de despliegue: **local**, **Streamlit Community Cloud** y **Docker**.

---

## 📋 Índice

1. [Despliegue Local](#1-despliegue-local)
2. [Despliegue en Streamlit Community Cloud](#2-despliegue-en-streamlit-community-cloud)
3. [Despliegue con Docker](#3-despliegue-con-docker)
4. [Variables de Entorno](#4-variables-de-entorno)
5. [Monitoreo y Logs](#5-monitoreo-y-logs)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Despliegue Local

### Requisitos previos

| Software | Versión mínima | Verificar con |
|----------|---------------|---------------|
| Python | 3.10+ | `python --version` |
| Java JDK | 11+ | `java -version` |
| pip | 23+ | `pip --version` |

### Pasos

```bash
# ── 1. Clonar / descargar el proyecto ──────────────────
cd c:\Users\USUARIO\Desktop\agente

# ── 2. Crear entorno virtual ───────────────────────────
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# ── 3. Instalar dependencias ───────────────────────────
pip install -r requirements.txt

# ── 4. Ejecutar el pipeline PySpark ───────────────────
python pyspark_ventas.py
# → Genera output/ventas_procesadas.parquet/

# ── 5. Lanzar el dashboard ─────────────────────────────
streamlit run app.py
# → Abre http://localhost:8501
```

### Verificación rápida

```bash
# Comprobar que el Parquet fue generado
dir output\ventas_procesadas.parquet\

# Debe mostrar archivos .parquet y _SUCCESS
```

---

## 2. Despliegue en Streamlit Community Cloud

Streamlit Community Cloud permite desplegar dashboards **gratis** desde GitHub.

> ⚠️ **Nota:** PySpark requiere Java en el servidor. En Streamlit Cloud, el script PySpark **no se puede ejecutar directamente**, pero el dashboard puede leer el CSV como fuente alternativa (cambia la fuente a "CSV directo" en el sidebar).

### Pasos

#### 2.1 Subir el proyecto a GitHub

```bash
# Inicializar repositorio
git init
git add .
git commit -m "feat: PySpark ventas dashboard"

# Crear repo en GitHub y hacer push
git remote add origin https://github.com/TU_USUARIO/pyspark-ventas.git
git branch -M main
git push -u origin main
```

#### 2.2 Conectar a Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Haz clic en **"New app"**
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio `pyspark-ventas`
5. En **"Main file path"** escribe: `app.py`
6. Haz clic en **"Deploy!"**

#### 2.3 Configurar `requirements.txt` para Cloud

Para Streamlit Cloud (sin PySpark), usa esta versión ligera:

```txt
# requirements_cloud.txt  (sin pyspark ni pyarrow pesado)
pandas==2.2.2
streamlit==1.35.0
plotly==5.22.0
pyarrow==16.0.0
```

> En el sidebar del dashboard, selecciona **"CSV directo"** para leer `ventas.csv` sin necesitar Parquet.

---

## 3. Despliegue con Docker

Docker garantiza que el entorno sea **idéntico** en cualquier máquina.

### 3.1 Crear `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Instalar Java (requerido por Spark)
RUN apt-get update && apt-get install -y \
    default-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno para Java
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer puerto de Streamlit
EXPOSE 8501

# Ejecutar PySpark y luego Streamlit
CMD ["bash", "-c", "python pyspark_ventas.py && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
```

### 3.2 Crear `.dockerignore`

```
.venv/
__pycache__/
*.pyc
.git/
output/
```

### 3.3 Construir y ejecutar

```bash
# Construir la imagen
docker build -t pyspark-ventas:latest .

# Ejecutar el contenedor
docker run -p 8501:8501 pyspark-ventas:latest

# El dashboard estará disponible en:
# http://localhost:8501
```

### 3.4 Docker Compose (opcional)

```yaml
# docker-compose.yml
version: "3.9"
services:
  ventas-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./output:/app/output   # Persistir Parquet entre reinicios
    environment:
      - PYTHONUNBUFFERED=1
```

```bash
docker compose up --build
```

---

## 4. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Ruta al CSV de entrada
CSV_PATH=ventas.csv

# Ruta de salida Parquet
PARQUET_OUTPUT=output/ventas_procesadas.parquet

# Puerto de Streamlit (solo para despliegue)
STREAMLIT_PORT=8501
```

Carga las variables en Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()
csv_path = os.getenv("CSV_PATH", "ventas.csv")
parquet_path = os.getenv("PARQUET_OUTPUT", "output/ventas_procesadas.parquet")
```

> Añade `python-dotenv` a `requirements.txt` si usas este patrón.

---

## 5. Monitoreo y Logs

### Spark UI (durante ejecución local)

Mientras `pyspark_ventas.py` se ejecuta, abre:

```
http://localhost:4040
```

Verás:
- **Jobs** ejecutados
- **Stages** y su duración
- **Storage** (datos en caché)
- **Environment** (configuración)

### Logs de Streamlit

```bash
# Ver logs en tiempo real
streamlit run app.py --logger.level=debug

# Guardar logs en archivo
streamlit run app.py 2>&1 | tee streamlit.log
```

### Automatizar ejecución diaria (Windows Task Scheduler)

```powershell
# Script: ejecutar_pipeline.ps1
Set-Location "C:\Users\USUARIO\Desktop\agente"
.\.venv\Scripts\Activate.ps1
python pyspark_ventas.py
Write-Host "Pipeline ejecutado: $(Get-Date)" >> pipeline.log
```

Configura una tarea programada en Windows para ejecutar este script cada día a las 08:00.

---

## 6. Troubleshooting

### ❌ Error: `JAVA_HOME is not set`

```powershell
# Windows – Configurar JAVA_HOME permanentemente
[System.Environment]::SetEnvironmentVariable(
    "JAVA_HOME",
    "C:\Program Files\Eclipse Adoptium\jdk-11.x.x.x-hotspot",
    "Machine"
)
```

### ❌ Error: `Permission denied` al escribir Parquet

```bash
# Verificar que la carpeta output/ exista y sea escribible
mkdir output
# En Windows:
New-Item -ItemType Directory -Path output -Force
```

### ❌ Error: `Port 8501 already in use`

```bash
# Cambiar el puerto de Streamlit
streamlit run app.py --server.port 8502
```

### ❌ Dashboard muestra "No se encontraron archivos Parquet"

1. Verifica que el script PySpark se ejecutó sin errores: `python pyspark_ventas.py`
2. Revisa que existe la carpeta `output/ventas_procesadas.parquet/`
3. Comprueba que hay archivos `.parquet` dentro
4. En el sidebar del dashboard, usa "📄 CSV directo" como fuente temporal

### ❌ `ModuleNotFoundError: No module named 'pyspark'`

```bash
# Asegúrate de que el entorno virtual está activado
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## ✅ Checklist Final de Despliegue

- [ ] Java 11+ instalado y `JAVA_HOME` configurado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas con `pip install -r requirements.txt`
- [ ] `python pyspark_ventas.py` ejecutado sin errores
- [ ] Carpeta `output/ventas_procesadas.parquet/` generada
- [ ] `streamlit run app.py` lanza el dashboard en `http://localhost:8501`
- [ ] El dashboard muestra los 4 KPIs y los 4 gráficos correctamente

---

> 🎉 **¡Proyecto desplegado exitosamente!**  
> Para escalar a producción con datos reales, considera **Databricks**, **AWS EMR** o **Google Dataproc**.

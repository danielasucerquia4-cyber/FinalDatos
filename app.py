"""
app.py  –  Dashboard Streamlit para visualizar ventas procesadas con PySpark
"""

import os
import glob
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ──────────────────────────────────────────────
# Configuración de la página
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="📊 Dashboard de Ventas PySpark",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CSS personalizado – diseño premium oscuro
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo degradado oscuro */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
    }

    /* Tarjetas de métricas */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 20px 24px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(100, 100, 255, 0.25);
    }
    div[data-testid="metric-container"] label {
        color: #a78bfa !important;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.9rem !important;
        font-weight: 700;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.85);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    /* Títulos */
    h1 { color: #c4b5fd !important; }
    h2, h3 { color: #a78bfa !important; }

    /* DataTable */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Botones */
    .stButton>button {
        background: linear-gradient(90deg, #6d28d9, #4f46e5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: opacity 0.2s;
    }
    .stButton>button:hover { opacity: 0.85; }

    /* Dividers */
    hr { border-color: rgba(255,255,255,0.1); }
    </style>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────
# Helpers – carga de datos
# ──────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cargar_desde_parquet(ruta: str) -> pd.DataFrame:
    """Lee todos los part-files Parquet en el directorio."""
    archivos = glob.glob(os.path.join(ruta, "*.parquet"))
    if not archivos:
        return pd.DataFrame()
    return pd.concat([pd.read_parquet(f) for f in archivos], ignore_index=True)


@st.cache_data(show_spinner=False)
def cargar_desde_csv(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    df["total_venta"] = df["cantidad"] * df["precio"]
    return df


# ──────────────────────────────────────────────
# Sidebar – controles
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")

    fuente = st.radio(
        "Fuente de datos",
        ["📂 Parquet (PySpark output)", "📄 CSV directo"],
        index=0,
    )

    parquet_path = st.text_input(
        "Ruta Parquet",
        value="output/ventas_procesadas.parquet",
        help="Carpeta generada por el script PySpark",
    )
    csv_path = st.text_input("Ruta CSV", value="ventas.csv")

    st.markdown("---")
    if st.button("🔄 Recargar datos"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### 🛠 Stack tecnológico")
    st.markdown(
        """
        - 🔥 **PySpark** – procesamiento
        - 🐼 **Pandas** – análisis local
        - 📊 **Plotly** – visualización
        - 🌐 **Streamlit** – dashboard
        """
    )

# ──────────────────────────────────────────────
# Carga de datos según la fuente elegida
# ──────────────────────────────────────────────
df: pd.DataFrame = pd.DataFrame()

if "Parquet" in fuente:
    with st.spinner("Cargando Parquet..."):
        df = cargar_desde_parquet(parquet_path)
    if df.empty:
        st.warning(
            "⚠️ No se encontraron archivos Parquet en la ruta indicada.  \n"
            "Ejecuta primero `python pyspark_ventas.py` para generarlos."
        )
else:
    if os.path.exists(csv_path):
        with st.spinner("Cargando CSV..."):
            df = cargar_desde_csv(csv_path)
    else:
        st.error(f"❌ No se encontró el archivo: `{csv_path}`")

# ──────────────────────────────────────────────
# Encabezado principal
# ──────────────────────────────────────────────
st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:0;'>
        🚀 Dashboard de Ventas
    </h1>
    <p style='text-align:center; color:#8b8ba8; font-size:1rem; margin-top:4px;'>
        Procesamiento con <strong>PySpark</strong> · Visualización con <strong>Streamlit</strong>
    </p>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

if df.empty:
    st.info("Selecciona una fuente de datos válida en el panel lateral.")
    st.stop()

# ──────────────────────────────────────────────
# KPI Cards
# ──────────────────────────────────────────────
total_ingresos = df["total_venta"].sum()
num_productos = df["producto"].nunique()
venta_max = df["total_venta"].max()
producto_estrella = df.loc[df["total_venta"].idxmax(), "producto"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Ingresos", f"${total_ingresos:,.0f}")
col2.metric("📦 Productos únicos", num_productos)
col3.metric("🏆 Venta más alta", f"${venta_max:,.0f}")
col4.metric("⭐ Producto estrella", producto_estrella)

st.markdown("---")

# ──────────────────────────────────────────────
# Gráficos
# ──────────────────────────────────────────────
left, right = st.columns(2, gap="large")

PALETTE = ["#6d28d9", "#4f46e5", "#7c3aed", "#a78bfa", "#c4b5fd"]

with left:
    st.markdown("### 💵 Total de Venta por Producto")
    fig_bar = px.bar(
        df.sort_values("total_venta", ascending=True),
        x="total_venta",
        y="producto",
        orientation="h",
        color="total_venta",
        color_continuous_scale=["#4f46e5", "#c4b5fd"],
        text="total_venta",
        labels={"total_venta": "Total ($)", "producto": "Producto"},
    )
    fig_bar.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside",
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
    )
    fig_bar.update_xaxes(showgrid=False, zeroline=False)
    fig_bar.update_yaxes(showgrid=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    st.markdown("### 🍕 Distribución de Ingresos")
    fig_pie = px.pie(
        df,
        names="producto",
        values="total_venta",
        color_discrete_sequence=PALETTE,
        hole=0.55,
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        textfont_color="#e0e0e0",
        marker_line_width=2,
        marker_line_color="rgba(0,0,0,0.3)",
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Segunda fila de gráficos ──
left2, right2 = st.columns(2, gap="large")

with left2:
    st.markdown("### 📦 Cantidad Vendida por Producto")
    fig_cant = px.bar(
        df,
        x="producto",
        y="cantidad",
        color="producto",
        color_discrete_sequence=PALETTE,
        text="cantidad",
        labels={"cantidad": "Unidades", "producto": "Producto"},
    )
    fig_cant.update_traces(textposition="outside")
    fig_cant.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
    )
    fig_cant.update_yaxes(showgrid=False)
    st.plotly_chart(fig_cant, use_container_width=True)

with right2:
    st.markdown("### 💲 Precio Unitario vs Total de Venta")
    fig_scatter = px.scatter(
        df,
        x="precio",
        y="total_venta",
        size="cantidad",
        color="producto",
        color_discrete_sequence=PALETTE,
        text="producto",
        labels={"precio": "Precio unitario ($)", "total_venta": "Total venta ($)"},
    )
    fig_scatter.update_traces(textposition="top center", marker_opacity=0.85)
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ──────────────────────────────────────────────
# Tabla de datos completa
# ──────────────────────────────────────────────
st.markdown("### 📋 Datos completos procesados")

df_display = df.copy()
df_display["precio"] = df_display["precio"].apply(lambda x: f"${x:,.2f}")
df_display["total_venta"] = df_display["total_venta"].apply(lambda x: f"${x:,.2f}")
df_display.columns = [c.replace("_", " ").title() for c in df_display.columns]

st.dataframe(df_display, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown(
    """
    <br>
    <p style='text-align:center; color:#6b6b8a; font-size:0.82rem;'>
        Generado con 🔥 PySpark + 🌐 Streamlit &nbsp;|&nbsp;
        Dashboard by Antigravity
    </p>
    """,
    unsafe_allow_html=True,
)

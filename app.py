# import streamlit as st
# import pandas as pd



# def kpi_card(title, value, target, inverse=False):
#     """
#     inverse=True → menor valor es mejor
#     """

#     if inverse:
#         ok = value <= target
#     else:
#         ok = value >= target

#     color = "#16a34a" if ok else "#dc2626"
#     arrow = "▲" if ok else "▼"

#     st.markdown(
#         f"""
#         <div style="
#             background-color:#111827;
#             padding:20px;
#             border-radius:12px;
#             text-align:center;
#             border:2px solid {color};
#         ">
#             <h4 style="color:#9ca3af;">{title}</h4>
#             <h1 style="color:{color};">
#                 {value:,} {arrow}
#             </h1>
#             <p style="color:#9ca3af;">
#                 Objetivo: {target:,}
#             </p>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )



# OBJ_IR014 = 500
# OBJ_CH001 = 300
# OBJ_DEMORA = 8000
# OBJ_ITIN = 200

# # -----------------------------------
# # CONFIG
# # -----------------------------------
# st.set_page_config(
#     page_title="Dashboard Itinerarios",
#     layout="wide",
#     page_icon="📊"
# )

# st.markdown("""
# <style>

# [data-testid="metric-container"] {
#     background-color: #111827;
#     border: 1px solid #374151;
#     padding: 18px;
#     border-radius: 12px;
#     text-align: center;
# }

# [data-testid="metric-container"] label {
#     font-size: 14px;
#     color: #9ca3af;
# }

# [data-testid="metric-container"] div {
#     font-size: 28px;
#     font-weight: 700;
# }

# </style>
# """, unsafe_allow_html=True)

# st.title("📊 Dashboard de Itinerarios")

# # -----------------------------------
# # CARGA CSV
# # -----------------------------------
# uploaded_file = st.sidebar.file_uploader(
#     "Subir archivo CSV",
#     type=["csv"]
# )

# if uploaded_file is None:
#     st.info("⬅️ Subí un archivo CSV para comenzar")
#     st.stop()

# # -----------------------------------
# # LECTURA
# # -----------------------------------
# # df = pd.read_csv(uploaded_file)
# def leer_csv_seguro(file):
#     encodings = ["utf-8", "latin1", "cp1252", "utf-16"]

#     for enc in encodings:
#         try:
#             file.seek(0)
#             return pd.read_csv(file, encoding=enc, sep=None, engine="python")
#         except:
#             continue

#     raise Exception("No se pudo leer el archivo con codificaciones comunes")


# df = leer_csv_seguro(uploaded_file)

# # Normalizar nombres
# df.columns = df.columns.str.lower()

# # convertir fecha
# # df["f_lteor"] = pd.to_datetime(df["f_lteor"])
# df["f_lteor"] = pd.to_datetime(df["f_lteor"], format="%d/%m/%Y %H:%M:%S", errors="coerce")

# # -------------------------
# # FILTRO DE FECHAS
# # -------------------------

# st.sidebar.subheader("Filtro de fechas")

# fecha_min = df["f_lteor"].min()
# fecha_max = df["f_lteor"].max()

# fecha_inicio, fecha_fin = st.sidebar.date_input(
#     "Rango de fechas",
#     [fecha_min, fecha_max],
# )

# df_filtrado = df[
#     (df["f_lteor"] >= pd.to_datetime(fecha_inicio)) &
#     (df["f_lteor"] <= pd.to_datetime(fecha_fin))
# ]

# # -------------------------
# # CALCULO KPIs
# # -------------------------

# total_programados = df_filtrado["total_programados"].sum()
# total_leidos_ftl = df_filtrado["total_leidos_ftl"].sum()

# lecturas_pendientes = total_programados - total_leidos_ftl

# # KPI 1
# kpi_atraso = 1.4

# # KPI 2
# kpi_reglamentarios = df_filtrado["reglamentarios"].mean()

# # KPI 3
# avance_descarga = (total_leidos_ftl / total_programados * 100) if total_programados > 0 else 0

# # KPI 4
# porcentaje_pendientes = (lecturas_pendientes / total_programados * 100) if total_programados > 0 else 0

# # KPI 5
# lecturas_descargadas = total_leidos_ftl

# # KPI 6
# lecturas_pendientes_total = lecturas_pendientes

# # KPI 7
# total_dias = df["f_lteor"].nunique()
# dias_filtrados = df_filtrado["f_lteor"].nunique()

# dias_restantes = total_dias - dias_filtrados

# promedio_requerido = (
#     lecturas_pendientes_total / dias_restantes
#     if dias_restantes > 0 else 0
# )

# # -------------------------
# # MOSTRAR KPIs
# # -------------------------

# # FILA 1
# col1, col2, col3, col4 = st.columns(4)

# # col1.metric(
# #     "ATRASO",
# #     f"{kpi_atraso}"
# # )
# col1.metric(
#     "ATRASO",
#     f"{kpi_atraso:.2f}"
# )

# col2.metric(
#     "PLAZOS REGLAMENTARIOS",
#     f"{kpi_reglamentarios:.2f}"
# )

# col3.metric(
#     "AVANCE DE DESCARGA",
#     f"{avance_descarga:.2f}%"
# )

# col4.metric(
#     "% LECTURAS PENDIENTES",
#     f"{porcentaje_pendientes:.2f}%"
# )

# # FILA 2
# col5, col6, col7 = st.columns(3)

# col5.metric(
#     "LECTURAS DESCARGADAS",
#     f"{lecturas_descargadas:,.0f}"
# )

# col6.metric(
#     "LECTURAS PENDIENTES",
#     f"{lecturas_pendientes_total:,.0f}"
# )

# col7.metric(
#     "PROMEDIO REQUERIDO A DESCARGAR",
#     f"{promedio_requerido:,.0f} / día"
# )

# # -------------------------
# # TABLA
# # -------------------------

# st.subheader("Datos filtrados")

# st.dataframe(df_filtrado, use_container_width=True)


import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------------
# CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Dashboard Lectura",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
<style>

.kpi-card{
    //background: linear-gradient(145deg,#111827,#1f2937);
    //background: linear-gradient(145deg,#31405E,#445069);
    border-radius:14px;
    padding:32px;
    text-align:center;
    border:2px solid;
    box-shadow:0 4px 14px rgba(0,0,0,0.35);
    transition:0.2s;
    margin: 20px 0;
}

.kpi-card:hover{
    transform:translateY(-4px);
    box-shadow:0 10px 22px rgba(0,0,0,0.45);
}

.kpi-title{
    font-size:24px;
    //color:#9ca3af;
    //color: white;
    margin-bottom:6px;
    font-weight: bold;
}

.kpi-value{
    font-size:54px;
    font-weight:700;
}

.kpi-sub{
    font-size:13px;
    //color:#9ca3af;
    color: black;
    margin-top:6px;
}

</style>
""", unsafe_allow_html=True)

def kpi_visual(titulo, valor, color, sub=""):
    
    st.markdown(
        f"""
        <div class="kpi-card" style="border-color:{color}">
            <div class="kpi-title">{titulo}</div>
            <div class="kpi-value" style="color:{color}">
                {valor}
            </div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.title("📊 Dashboard de Lecturas")

# -----------------------------------
# CARGA CSV
# -----------------------------------
uploaded_file = st.sidebar.file_uploader(
    "Subir archivo CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info("⬅️ Subí un archivo CSV para comenzar")
    st.stop()

# -----------------------------------
# LECTURA SEGURA
# -----------------------------------
def leer_csv_seguro(file):
    encodings = ["utf-8", "latin1", "cp1252", "utf-16"]

    for enc in encodings:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc, sep=None, engine="python")
        except:
            continue

    raise Exception("No se pudo leer el archivo con codificaciones comunes")

df = leer_csv_seguro(uploaded_file)

df.columns = df.columns.str.lower()

# -----------------------------------
# CONVERTIR FECHA
# -----------------------------------
df["f_lteor"] = pd.to_datetime(
    df["f_lteor"],
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)

# -----------------------------------
# FILTRO DE FECHAS
# -----------------------------------

# st.sidebar.subheader("Filtro de fechas")
st.sidebar.subheader("Filtro para plazos reglamentarios + atraso")

fecha_min = df["f_lteor"].min()
fecha_max = df["f_lteor"].max()

fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas",
    [fecha_min, fecha_max],
)

df_rango = df[
    (df["f_lteor"] >= pd.to_datetime(fecha_inicio)) &
    (df["f_lteor"] <= pd.to_datetime(fecha_fin))
]

# -----------------------------------
# NUEVO FILTRO: EXCLUIR DIAS
# -----------------------------------

# dias_disponibles = sorted(df_rango["f_lteor"].dt.date.unique())

# dias_seleccionados = st.sidebar.multiselect(
#     "Excluir días específicos",
#     dias_disponibles,
#     default=[]
# )

# df_filtrado = df_rango[
#     ~df_rango["f_lteor"].dt.date.isin(dias_seleccionados)
# ]
df_filtrado = df_rango


 # -----------------------------
    # FILTRO PARA DESELECCIONAR FILAS
    # -----------------------------
# st.subheader("Deseleccionar filas manualmente")

# df_filtrado = df_filtrado.reset_index(drop=True)

# filas_excluir = st.multiselect(
#         "Seleccionar filas a excluir",
#         df_filtrado.index.tolist()
#     )

# if filas_excluir:
#         df_filtrado = df_filtrado.drop(filas_excluir)



# -----------------------------
# FILTRO PARA SELECCIONAR FILAS A CONSIDERAR
# -----------------------------
# st.subheader("Seleccionar filas a considerar")

# df_filtrado_regl = df_filtrado.reset_index(drop=True)

# # crear etiqueta visual para cada fila
# df_filtrado_regl["fila_label"] = (
#     "Fila "
#     + df_filtrado_regl.index.astype(str)
#     + " | "
#     + df_filtrado_regl["f_lteor"].astype(str)
# )

# opciones_filas = df_filtrado_regl["fila_label"].tolist()

# # checkbox para seleccionar todo
# seleccionar_todo = st.checkbox("Seleccionar todas las filas", value=True)

# if seleccionar_todo:
#     filas_seleccionadas = opciones_filas
# else:
#     filas_seleccionadas = st.multiselect(
#         "Seleccionar filas",
#         opciones_filas
#     )

# # filtrar dataframe
# df_filtrado_regl = df_filtrado_regl[
#     df_filtrado_regl["fila_label"].isin(filas_seleccionadas)
# ]

# # eliminar columna auxiliar
# df_filtrado_regl = df_filtrado_regl.drop(columns=["fila_label"])


# -----------------------------------
# CALCULO KPIs
# -----------------------------------

# total_programados = df_filtrado["total_programados"].sum()
# total_leidos_ftl = df_filtrado["total_leidos_ftl"].sum()
total_programados = df["total_programados"].sum()
total_leidos_ftl = df["total_leidos_ftl"].sum()

lecturas_pendientes = total_programados - total_leidos_ftl

# # KPI 1
# kpi_atraso = 1.4
# KPI 1 — ATRASO EN DÍAS

# agrupamos por día
df_dias = df_filtrado.groupby("f_lteor").agg({
    "total_programados": "sum",
    "total_leidos_ftl": "sum"
}).reset_index()

# calculamos diferencia diaria
df_dias["pendiente"] = df_dias["total_programados"] - df_dias["total_leidos_ftl"]

# solo consideramos pendientes positivos
pendiente_total = df_dias[df_dias["pendiente"] > 0]["pendiente"].sum()

# promedio diario programado
promedio_diario_programado = df_dias["total_programados"].mean()

# atraso en días
kpi_atraso = (
    pendiente_total / promedio_diario_programado
    if promedio_diario_programado > 0 else 0
)

kpi_atraso = round(kpi_atraso, 2)

# KPI 2
kpi_reglamentarios = df_filtrado["reglamentarios"].mean()
# kpi_reglamentarios = df_filtrado_regl["reglamentarios"].mean()

# KPI 3
avance_descarga = (total_leidos_ftl / total_programados * 100) if total_programados > 0 else 0

# KPI 4
porcentaje_pendientes = (lecturas_pendientes / total_programados * 100) if total_programados > 0 else 0

# KPI 5
lecturas_descargadas = total_leidos_ftl

# KPI 6
lecturas_pendientes_total = lecturas_pendientes

# KPI 7
# total_dias = df["f_lteor"].nunique()
# dias_filtrados = df_filtrado["f_lteor"].nunique()

# dias_restantes = total_dias - dias_filtrados
# total de dias posibles en el dataset
total_dias = df["f_lteor"].dt.date.nunique()

# primer día del dataset (registro 0)
primer_dia = df["f_lteor"].min().date()

# día actual
hoy = datetime.today().date()

# días transcurridos desde el primer registro hasta hoy
dias_transcurridos = (hoy - primer_dia).days + 1

# días restantes del período
dias_restantes = total_dias - dias_transcurridos

promedio_requerido = (
    lecturas_pendientes_total / dias_restantes
    if dias_restantes > 0 else 0
)

# -----------------------------------
# MOSTRAR KPIs
# -----------------------------------

# col1, col2, col3, col4 = st.columns(4)

# col1.metric(
#     "ATRASO",
#     f"{kpi_atraso}"
# )

# col2.metric(
#     "PLAZOS REGLAMENTARIOS",
#     f"{kpi_reglamentarios:.2f}%"
# )

# col3.metric(
#     "AVANCE DE DESCARGA",
#     f"{avance_descarga:.2f}%"
# )

# col4.metric(
#     "% LECTURAS PENDIENTES",
#     f"{porcentaje_pendientes:.2f}%"
# )
col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_visual(
        "ATRASO",
        f"{kpi_atraso}",
        "#ef4444"
    )

with col2:
    kpi_visual(
        "PLAZOS REGLAMENTARIOS",
        f"{kpi_reglamentarios:.2f}%",
        "#3b82f6"
    )

with col3:
    kpi_visual(
        "AVANCE DE DESCARGA",
        f"{avance_descarga:.2f}%",
        "#22c55e"
    )

with col4:
    kpi_visual(
        "% LECTURAS PENDIENTES",
        f"{porcentaje_pendientes:.2f}%",
        "#f59e0b"
    )

# col5, col6, col7 = st.columns(3)

# col5.metric(
#     "LECTURAS DESCARGADAS",
#     f"{lecturas_descargadas:,.0f}"
# )

# col6.metric(
#     "LECTURAS PENDIENTES",
#     f"{lecturas_pendientes_total:,.0f}"
# )

# col7.metric(
#     "PROMEDIO REQUERIDO A DESCARGAR",
#     f"{promedio_requerido:,.0f} / día"
# )

col5, col6, col7 = st.columns(3)

with col5:
    kpi_visual(
        "LECTURAS DESCARGADAS",
        f"{lecturas_descargadas:,.0f}",
        "#10b981"
    )

with col6:
    kpi_visual(
        "LECTURAS PENDIENTES",
        f"{lecturas_pendientes_total:,.0f}",
        "#ef4444"
    )

with col7:
    kpi_visual(
        "PROMEDIO REQUERIDO A DESCARGAR",
        f"{promedio_requerido:,.0f} / día",
        "#8b5cf6"
    )

# -----------------------------------
# TABLA
# -----------------------------------

st.subheader("Datos filtrados")
st.dataframe(df_filtrado, use_container_width=True)

st.subheader("Todos los datos")
st.dataframe(df, use_container_width=True)
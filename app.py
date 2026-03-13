import streamlit as st
import pandas as pd
from datetime import datetime
import logging
# import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
from graficos import graf_ev_lect_atraso_ritmo, graf_ev_lect

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


def cargar_csv_universal(file):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "utf-16",
        "latin1",
        "cp1252"
    ]

    separadores = [",", ";", "\t", "|"]

    for enc in encodings:
        for sep in separadores:
            try:
                file.seek(0)
                df = pd.read_csv(
                    file,
                    encoding=enc,
                    sep=sep,
                    engine="python"
                )

                # validar que tenga más de una columna
                if len(df.columns) > 1:
                    
                    # limpiar columnas
                    df.columns = (
                        df.columns
                        .str.strip()
                        .str.lower()
                        .str.replace("\ufeff", "", regex=False)
                    )

                    return df

            except:
                continue

    raise Exception("No se pudo interpretar el archivo CSV")
# df = leer_csv_seguro(uploaded_file)

# df.columns = df.columns.str.lower()
# df = leer_csv_seguro(uploaded_file)
df = cargar_csv_universal(uploaded_file)

# limpiar nombres de columnas
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)

# st.write("Columnas detectadas:", df.columns)

# -----------------------------------
# CONVERTIR FECHA
# -----------------------------------
df["f_lteor"] = pd.to_datetime(
    df["f_lteor"],
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)



# -----------------------------------
# FILTROS ADICIONALES
# -----------------------------------

st.sidebar.subheader("Filtros adicionales")

# FILTRO MES
if "mes" in df.columns:
    meses = sorted(df["mes"].dropna().unique())

    meses_seleccionados = st.sidebar.multiselect(
        "Filtrar por mes",
        meses,
        default=meses
    )
else:
    meses_seleccionados = None


# FILTRO TARIFA
if "tarifa" in df.columns:
    tarifas = sorted(df["tarifa"].dropna().unique())

    tarifas_seleccionadas = st.sidebar.multiselect(
        "Filtrar por tarifa",
        tarifas,
        default=tarifas
    )
else:
    tarifas_seleccionadas = None




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


df_filtrado = df_rango.copy()

# aplicar filtro mes
if meses_seleccionados is not None:
    df_filtrado = df_filtrado[df_filtrado["mes"].isin(meses_seleccionados)]

# aplicar filtro tarifa
if tarifas_seleccionadas is not None:
    df_filtrado = df_filtrado[df_filtrado["tarifa"].isin(tarifas_seleccionadas)]






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



# df_filtrado = df_rango


df_base = df.copy()

# filtro mes
if meses_seleccionados:
    df_base = df_base[df_base["mes"].isin(meses_seleccionados)]

# filtro tarifa
if tarifas_seleccionadas:
    df_base = df_base[df_base["tarifa"].isin(tarifas_seleccionadas)]


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
# total_programados = df["total_programados"].sum()
# total_leidos_ftl = df["total_leidos_ftl"].sum()
total_programados = df_base["total_programados"].sum()
total_leidos_ftl = df_base["total_leidos_ftl"].sum()

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



if kpi_atraso <= 1:
    estado = "NORMAL"
    color = "#16a34a"
    emoji = "🟢"

elif kpi_atraso <= 2:
    estado = "RIESGO"
    color = "#f59e0b"
    emoji = "🟡"

else:
    estado = "CRÍTICO"
    color = "#ef4444"
    emoji = "🔴"





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
total_dias = df_base["f_lteor"].dt.date.nunique()

# primer día del dataset (registro 0)
# primer_dia = df["f_lteor"].min().date()

# # día actual
# hoy = datetime.today().date()

# # días transcurridos desde el primer registro hasta hoy
# dias_transcurridos = (hoy - primer_dia).days + 1


hoy = datetime.today().date()

df_base["fecha"] = df_base["f_lteor"].dt.date

primer_dia = df_base["fecha"].min()

# fecha_cercana = df[df["fecha"] <= hoy]["fecha"].max()
fecha_cercana = df_base[df_base["fecha"] < hoy]["fecha"].max()

dias_transcurridos = df_base[
    (df_base["fecha"] >= primer_dia) &
    (df_base["fecha"] <= fecha_cercana)
]["fecha"].nunique()

# días restantes del período
dias_restantes = total_dias - dias_transcurridos

promedio_requerido = (
    lecturas_pendientes_total / dias_restantes
    if dias_restantes > 0 else 0
)

# st.header(f"total dias:  {total_dias}")
# st.header(f"dias transcurridos:  {dias_transcurridos}")
# st.header(f"dias restantes:  {dias_restantes}")

st.space("medium") # Añade un espacio grande
st.info(f"Total de días: {total_dias}")
st.info(f"Días transcurridos: {dias_transcurridos}")
st.info(f"Días restantes: {dias_restantes}")
st.space("medium") # Añade un espacio grande
# st.success("Esto es un mensaje de éxito.")
# st.warning("Esto es una advertencia.")
# st.error("Esto es un mensaje de error.")


# atraso diario en días
# df_dias["atraso_dias"] = (
#     (df_dias["total_programados"] - df_dias["total_leidos_ftl"])
#     / promedio_diario_programado
# )

# df_dias["atraso_dias"] = df_dias["atraso_dias"].clip(lower=0)


# st.sidebar.subheader("Filtro de atraso")

# rango_atraso = st.sidebar.slider(
#     "Rango de atraso (días)",
#     0.0,
#     float(df_dias["atraso_dias"].max()),
#     (0.0, float(df_dias["atraso_dias"].max())),
#     step=0.1
# )


# df_dias_filtrado = df_dias[
#     (df_dias["atraso_dias"] >= rango_atraso[0]) &
#     (df_dias["atraso_dias"] <= rango_atraso[1])
# ]







st.subheader("Estado operativo")

st.markdown(
    f"""
    <div style="
        background-color:{color};
        padding:25px;
        border-radius:12px;
        text-align:center;
        color:white;
        font-size:28px;
        font-weight:bold;
    ">
        {emoji} {estado} <br>
        Atraso: {kpi_atraso:.2f} días
    </div>
    """,
    unsafe_allow_html=True
)





st.space("large") # Añade un espacio grande



# st.subheader("Indicador de atraso operativo")

# fig = go.Figure(go.Indicator(
#     mode="gauge+number",
#     value=kpi_atraso,
#     title={'text': "Atraso (días)"},
    
#     gauge={
#         'axis': {'range': [0, 5]},
        
#         'bar': {'color': "black"},
        
#         'steps': [
#             {'range': [0, 1], 'color': "#16a34a"},   # verde
#             {'range': [1, 2], 'color': "#f59e0b"},   # amarillo
#             {'range': [2, 5], 'color': "#ef4444"}    # rojo
#         ],
        
#         'threshold': {
#             'line': {'color': "black", 'width': 4},
#             'thickness': 0.75,
#             'value': kpi_atraso
#         }
#     }
# ))

# st.plotly_chart(fig, use_container_width=True)

# max_atraso = total_programados / promedio_diario_programado















st.space("large") # Añade un espacio grande

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












st.space("large") # Añade un espacio grande
# lecturas realizadas hasta hoy
lecturas_realizadas = df_filtrado["total_leidos_ftl"].sum()

# ritmo actual (lecturas por día)
ritmo_actual = (
    lecturas_realizadas / dias_transcurridos
    if dias_transcurridos > 0 else 0
)

# lecturas pendientes
lecturas_pendientes = total_programados - lecturas_realizadas

# días necesarios al ritmo actual
dias_necesarios = (
    lecturas_pendientes / ritmo_actual
    if ritmo_actual > 0 else 0
)

fecha_estimada_fin = hoy + timedelta(days=dias_necesarios)

st.subheader("Proyección de finalización")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Ritmo actual",
        f"{ritmo_actual:.0f} lecturas/día"
    )

with col2:
    st.metric(
        "Días necesarios",
        f"{dias_necesarios:.1f}"
    )

with col3:
    st.metric(
        "Fecha estimada de finalización",
        fecha_estimada_fin.strftime("%d-%m-%Y")
    )











st.space("large") # Añade un espacio grande
st.subheader("Proyección de cumplimiento del período")

# df_proy = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados": "sum",
#     "total_leidos_ftl": "sum"
# }).reset_index()
df_proy = df_base.groupby(df_base["f_lteor"].dt.date).agg({
    "total_programados": "sum",
    "total_leidos_ftl": "sum"
}).reset_index()

df_proy = df_proy.rename(columns={"f_lteor":"fecha",  "leidos_acum":"Lecturas acumuladas",
    "ritmo_ideal":"Ritmo ideal"})

# acumulados
df_proy["prog_acum"] = df_proy["total_programados"].cumsum()
df_proy["leidos_acum"] = df_proy["total_leidos_ftl"].cumsum()



total_prog_periodo = df_proy["total_programados"].sum()

df_proy["ritmo_ideal"] = (
    total_prog_periodo / len(df_proy)
) * (df_proy.index + 1)





st.line_chart(
    df_proy.set_index("fecha")[[
        "leidos_acum",
        "ritmo_ideal"
    ]]
)

# df_proy = df_proy.rename(columns={
#     "leidos_acum":"Lecturas acumuladas",
#     "ritmo_ideal":"Ritmo ideal"
# })









st.space("large") # Añade un espacio grande
st.subheader("Evolución del backlog")

# df_backlog = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados": "sum",
#     "total_leidos_ftl": "sum"
# }).reset_index()
df_backlog = df_base.groupby(df_base["f_lteor"].dt.date).agg({
    "total_programados": "sum",
    "total_leidos_ftl": "sum"
}).reset_index()

df_backlog = df_backlog.rename(columns={"f_lteor": "fecha"})

df_backlog["prog_acum"] = df_backlog["total_programados"].cumsum()
df_backlog["leidos_acum"] = df_backlog["total_leidos_ftl"].cumsum()

df_backlog["backlog"] = df_backlog["prog_acum"] - df_backlog["leidos_acum"]


st.line_chart(
    df_backlog.set_index("fecha")[["backlog"]]
)





















# st.space("large") # Añade un espacio grande
# st.subheader("Mapa de calor por ciclo de lectura")

# df_ciclo = df_filtrado.groupby(["ciclo", df_filtrado["f_lteor"].dt.date]).agg({
#     "total_programados":"sum",
#     "total_leidos_ftl":"sum"
# }).reset_index()

# df_ciclo["avance_pct"] = (
#     df_ciclo["total_leidos_ftl"] /
#     df_ciclo["total_programados"] * 100
# )

# tabla_heatmap = df_ciclo.pivot(
#     index="ciclo",
#     columns="f_lteor",
#     values="avance_pct"
# )

# st.dataframe(
#     tabla_heatmap.style.background_gradient(
#         cmap="RdYlGn"
#     ).format("{:.0f}%"),
#     use_container_width=True
# )














st.space("large") # Añade un espacio grande
st.subheader("Top 10 días con mayor atraso")

# df_dias = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_ftl":"sum"
# }).reset_index()

df_dias = df_base.groupby(df_base["f_lteor"].dt.date).agg({
    "total_programados":"sum",
    "total_leidos_ftl":"sum"
}).reset_index()

df_dias["atraso"] = (
    df_dias["total_programados"] -
    df_dias["total_leidos_ftl"]
)


top_atrasos = df_dias.sort_values(
    "atraso",
    ascending=False
).head(10)

st.dataframe(
    top_atrasos,
    use_container_width=True
)


























# lecturas_realizadas = df_filtrado["total_leidos_ftl"].sum()
lecturas_realizadas = df_base["total_leidos_ftl"].sum()

ritmo_actual = (
    lecturas_realizadas / dias_transcurridos
    if dias_transcurridos > 0 else 0
)


lecturas_pendientes = total_programados - lecturas_realizadas


capacidad_restante = ritmo_actual * dias_restantes

atraso_final = lecturas_pendientes - capacidad_restante

st.space("large") # Añade un espacio grande
st.subheader("Predicción de atraso al cierre")

if atraso_final <= 0:
    st.success(
        f"🟢 El período terminaría al día o adelantado"
    )
else:
    st.error(
        f"🔴 Atraso proyectado: {int(atraso_final)} lecturas"
    )

















st.space("large") # Añade un espacio grande
st.subheader("Evolución diaria de lecturas")

df_evol = df_base.groupby(df_base["f_lteor"].dt.date).agg({
    "total_programados":"sum",
    "total_leidos_ftl":"sum"
}).reset_index()

df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

df_graf = df_evol.rename(columns={
    "total_programados": "Lecturas programadas",
    "total_leidos_ftl": "Lecturas realizadas s/FTL"
})

# import plotly.express as px

df_graf["Atraso diario"] = (
    df_graf["Lecturas programadas"] -
    df_graf["Lecturas realizadas s/FTL"]
)

total_programado_periodo = df_graf["Lecturas programadas"].sum()
total_dias = len(df_graf)

df_graf["dia_n"] = range(1, total_dias + 1)

df_graf["Ritmo ideal"] = (
    total_programado_periodo / total_dias
) * df_graf["dia_n"]

# fig = px.line(
#     df_graf,
#     x="fecha",
#     y=["Lecturas programadas", "Lecturas realizadas s/FTL"
#        , "Atraso diario"],
#     labels={
#         "fecha": "Día de lectura",
#         "value": "Cantidad de lecturas",
#         "variable": "Tipo"
#     },
#      markers=True,
#      title="Evolución diaria de lecturas s/FTL",
#     #  color_discrete_sequence=["#1f77b4", "#d62728"]  # azul y rojo
#      color_discrete_sequence=[
#         "#2563eb",  # azul programados
#         "#16a34a",  # verde leídos
#         "#ef4444"   # rojo atraso
#     ]
# )

# fig.update_layout(
#     yaxis=dict(
#         tickformat=","
#     )
# )

# fig.update_traces(
#     texttemplate='%{y:,.0f}',
#     textposition="top center"
# )
# for trace in fig.data:
#     trace.text = trace.y
#     trace.texttemplate = '%{text:,.0f}'
#     trace.textposition = 'top center'
#     trace.mode = 'lines+markers+text'


# import plotly.graph_objects as go

# fig = go.Figure()

# # Línea programados
# fig.add_trace(go.Scatter(
#     x=df_graf["fecha"],
#     y=df_graf["Lecturas programadas"],
#     mode="lines+markers+text",
#     name="Lecturas programadas",
#     line=dict(color="#2563eb"),
#     text=df_graf["Lecturas programadas"],
#     texttemplate="%{text:,.0f}",
#     textposition="top center"
# ))

# # Línea leídos
# fig.add_trace(go.Scatter(
#     x=df_graf["fecha"],
#     y=df_graf["Lecturas realizadas s/FTL"],
#     mode="lines+markers+text",
#     name="Lecturas realizadas s/FTL",
#     line=dict(color="#16a34a"),
#     text=df_graf["Lecturas realizadas s/FTL"],
#     texttemplate="%{text:,.0f}",
#     textposition="bottom center",
#     fill="tonexty",  # 🔥 relleno entre líneas
#     fillcolor="rgba(239,68,68,0.25)"
# ))

# fig.update_layout(
#     title="Evolución diaria de lecturas s/FTL",
#     xaxis_title="Día de lectura",
#     yaxis_title="Cantidad de lecturas",
#     yaxis=dict(tickformat=",")
# )

# fig = go.Figure()

# # PROGRAMADOS
# fig.add_trace(go.Scatter(
#     x=df_graf["fecha"],
#     y=df_graf["Lecturas programadas"],
#     mode="lines+markers+text",
#     name="Lecturas programadas",
#     line=dict(color="#2563eb"),
#     text=df_graf["Lecturas programadas"],
#     texttemplate="%{text:,.0f}",
#     textposition="top center"
# ))

# # LEIDOS
# fig.add_trace(go.Scatter(
#     x=df_graf["fecha"],
#     y=df_graf["Lecturas realizadas s/FTL"],
#     mode="lines+markers+text",
#     name="Lecturas realizadas",
#     line=dict(color="#16a34a"),
#     text=df_graf["Lecturas realizadas s/FTL"],
#     texttemplate="%{text:,.0f}",
#     textposition="bottom center",
#     fill="tonexty",
#     fillcolor="rgba(239,68,68,0.25)"
# ))

# # RITMO IDEAL
# fig.add_trace(go.Scatter(
#     x=df_graf["fecha"],
#     y=df_graf["Ritmo ideal"],
#     mode="lines",
#     name="Ritmo ideal",
#     line=dict(
#         color="#f59e0b",
#         dash="dash",
#         width=3
#     )
# ))

# fig.update_layout(
#     title="Evolución diaria de lecturas s/FTL",
#     xaxis_title="Día de lectura",
#     yaxis_title="Cantidad de lecturas",
#     yaxis=dict(tickformat=",")
# )

# # st.plotly_chart(fig, use_container_width=True, key="todo_ftl")

# st.plotly_chart(fig, use_container_width=True, key="todo_ftl_completo")










graf_ev_lect_atraso_ritmo(
    df_base,
    col_leidos="total_leidos_ftl",
    titulo="Evolución diaria de lecturas s/FTL",
    titulo_col_leidos="Lecturas realizadas s/FTL",
    key="grafico_ftl"
)

graf_ev_lect_atraso_ritmo(
    df_base,
    col_leidos="total_leidos_actual",
    titulo="Evolución diaria de lecturas s/fecha actual",
    titulo_col_leidos="Lecturas realizadas s/fecha actual",
    key="grafico_ftl2"
)

graf_ev_lect_atraso_ritmo(
    df_filtrado,
    col_leidos="total_leidos_ftl",
    titulo="Evolución diaria de lecturas s/FTL",
    titulo_col_leidos="Lecturas realizadas s/FTL",
    key="grafico_ftl3"
)

graf_ev_lect_atraso_ritmo(
    df_filtrado,
    col_leidos="total_leidos_actual",
    titulo="Evolución diaria de lecturas s/fecha actual",
    titulo_col_leidos="Lecturas realizadas s/fecha actual",
    key="grafico_ftl4"
)
















lecturas_realizadas = df_graf["Lecturas realizadas s/FTL"].sum()

dias_transcurridos = len(df_graf)

ritmo_actual = (
    lecturas_realizadas / dias_transcurridos
    if dias_transcurridos > 0 else 0
)


total_programado = df_graf["Lecturas programadas"].sum()

dias_estimados = (
    total_programado / ritmo_actual
    if ritmo_actual > 0 else 0
)

from datetime import timedelta

fecha_inicio = df_graf["fecha"].min()

fecha_fin_estimada = fecha_inicio + timedelta(days=int(dias_estimados))

st.metric(
    "📅 Fecha estimada de finalización",
    fecha_fin_estimada.strftime("%d-%m-%Y")
)










fecha_fin_programada = df_graf["fecha"].max()

desvio = (fecha_fin_estimada - fecha_fin_programada).days


st.metric(
    "⏱ Desvío estimado",
    f"{desvio} días",
    delta=desvio
)












ritmo_necesario = (
    lecturas_pendientes_total / dias_restantes
    if dias_restantes > 0 else 0
)

ratio_ritmo = (
    ritmo_actual / ritmo_necesario
    if ritmo_necesario > 0 else 1
)


# ratio >= 1     → ritmo suficiente
# ratio 0.8-1    → riesgo medio
# ratio < 0.8    → riesgo alto

if ratio_ritmo >= 1:
    estado = "🟢 Bajo riesgo"
    color = "green"
elif ratio_ritmo >= 0.8:
    estado = "🟡 Riesgo medio"
    color = "orange"
else:
    estado = "🔴 Alto riesgo"
    color = "red"


st.subheader("Indicador de riesgo operativo")

st.markdown(
    f"""
    <div style="
        background-color:{color};
        padding:20px;
        border-radius:10px;
        text-align:center;
        font-size:22px;
        color:white;
        font-weight:bold;
    ">
        {estado}
    </div>
    """,
    unsafe_allow_html=True
)


































st.space("large") # Añade un espacio grande
st.subheader("Evolución diaria de lecturas")

# df_evol = df_base.groupby(df_base["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_ftl":"sum"
# }).reset_index()

# df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

# df_graf = df_evol.rename(columns={
#     "total_programados": "Lecturas programadas",
#     "total_leidos_ftl": "Lecturas realizadas s/FTL"
# })

# # import plotly.express as px

# fig = px.line(
#     df_graf,
#     x="fecha",
#     y=["Lecturas programadas", "Lecturas realizadas s/FTL"],
#     labels={
#         "fecha": "Día de lectura",
#         "value": "Cantidad de lecturas",
#         "variable": "Tipo"
#     },
#      markers=True,
#        title="Evolución diaria de lecturas s/FTL"
# )

# fig.update_layout(
#     yaxis=dict(
#         tickformat=","
#     )
# )

# st.plotly_chart(fig, use_container_width=True, key="todo_ftl")





graf_ev_lect(
        df_base,
        col_leidos="total_leidos_ftl",
        titulo="Evolución diaria de lecturas s/FTL",
        key="ev_todo_ftl",
        titulo_col_leidos="Lecturas realizadas s/FTL"
    )


graf_ev_lect(
        df_base,
        col_leidos="total_leidos_actual",
        titulo="Evolución diaria de lecturas s/fecha actual",
        key="ev_todo_actual",
        titulo_col_leidos="Lecturas realizadas"
    )

graf_ev_lect(
        df_filtrado,
        col_leidos="total_leidos_ftl",
        titulo="Evolución diaria de lecturas s/FTL",
        key="ev_filtrado_ftl",
        titulo_col_leidos="Lecturas realizadas s/FTL"
    )


graf_ev_lect(
        df_filtrado,
        col_leidos="total_leidos_actual",
        titulo="Evolución diaria de lecturas s/fecha actual",
        key="ev_filtrado_actual",
        titulo_col_leidos="Lecturas realizadas"
    )





graf_ev_lect(
        df_base,
        col_leidos="total_leidos_ftl",
        titulo="Evolución diaria de lecturas s/FTL",
        key="ev_todo_ftl_val",
        titulo_col_leidos="Lecturas realizadas s/FTL",
        mostrar_val=True
    )


graf_ev_lect(
        df_base,
        col_leidos="total_leidos_actual",
        titulo="Evolución diaria de lecturas s/fecha actual",
        key="ev_todo_actual_val",
        titulo_col_leidos="Lecturas realizadas",
        mostrar_val=True
    )

graf_ev_lect(
        df_filtrado,
        col_leidos="total_leidos_ftl",
        titulo="Evolución diaria de lecturas s/FTL",
        key="ev_filtrado_ftl_val",
        titulo_col_leidos="Lecturas realizadas s/FTL",
        mostrar_val=True
    )


graf_ev_lect(
        df_filtrado,
        col_leidos="total_leidos_actual",
        titulo="Evolución diaria de lecturas s/fecha actual",
        key="ev_filtrado_actual_val",
        titulo_col_leidos="Lecturas realizadas",
        mostrar_val=True
    )































# st.space("large") # Añade un espacio grande
# st.subheader("Evolución diaria de lecturas")

# df_evol = df_base.groupby(df_base["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_actual":"sum"
# }).reset_index()

# df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

# df_graf = df_evol.rename(columns={
#     "total_programados": "Lecturas programadas",
#     "total_leidos_actual": "Lecturas realizadas"
# })

# # import plotly.express as px

# fig = px.line(
#     df_graf,
#     x="fecha",
#     y=["Lecturas programadas", "Lecturas realizadas"],
#     labels={
#         "fecha": "Día de lectura",
#         "value": "Cantidad de lecturas",
#         "variable": "Tipo"
#     },
#      markers=True,
#        title="Evolución diaria de lecturas s/fecha actual"
# )

# fig.update_layout(
#     yaxis=dict(
#         tickformat=","
#     )
# )

# st.plotly_chart(fig, use_container_width=True, key="todo_actual")


























# st.space("large") # Añade un espacio grande
# st.subheader("Evolución diaria de lecturas")

# df_evol = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_ftl":"sum"
# }).reset_index()

# df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

# df_graf = df_evol.rename(columns={
#     "total_programados": "Lecturas programadas",
#     "total_leidos_ftl": "Lecturas realizadas s/FTL"
# })

# # import plotly.express as px

# fig = px.line(
#     df_graf,
#     x="fecha",
#     y=["Lecturas programadas", "Lecturas realizadas s/FTL"],
#     labels={
#         "fecha": "Día de lectura",
#         "value": "Cantidad de lecturas",
#         "variable": "Tipo"
#     },
#      markers=True,
#        title="Evolución diaria de lecturas s/FTL"
# )

# fig.update_layout(
#     yaxis=dict(
#         tickformat=","
#     )
# )

# st.plotly_chart(fig, use_container_width=True, key="filtrado_ftl")





















# st.space("large") # Añade un espacio grande
# st.subheader("Evolución diaria de lecturas")

# df_evol = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_actual":"sum"
# }).reset_index()

# df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

# df_graf = df_evol.rename(columns={
#     "total_programados": "Lecturas programadas",
#     "total_leidos_actual": "Lecturas realizadas"
# })

# # import plotly.express as px

# fig = px.line(
#     df_graf,
#     x="fecha",
#     y=["Lecturas programadas", "Lecturas realizadas"],
#     labels={
#         "fecha": "Día de lectura",
#         "value": "Cantidad de lecturas",
#         "variable": "Tipo"
#     },
#      markers=True,
#        title="Evolución diaria de lecturas s/fecha actual"
     
# )

# fig.update_layout(
#     yaxis=dict(
#         tickformat=","
#     )
# )

# st.plotly_chart(fig, use_container_width=True, key="filtrado_actual")













# ----------------------------------
# GRAFICO EVOLUCION DIARIA DE LECTURAS
# -----------------------------------
st.space("large") # Añade un espacio grande
st.subheader("Evolución diaria de lecturas")

# df_evol = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_ftl":"sum"
# }).reset_index()
df_evol = df_base.groupby(df_base["f_lteor"].dt.date).agg({
    "total_programados":"sum",
    "total_leidos_ftl":"sum"
}).reset_index()

# df_evol["fecha_str"] = df_evol["f_lteor"].dt.strftime("%d-%m")
# df_evol["dia"] = df_evol["f_lteor"].dt.day

df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

df_graf = df_evol.rename(columns={
    "total_programados": "Lecturas programadas",
    "total_leidos_ftl": "Lecturas realizadas s/FTL"
})

st.line_chart(
    df_graf.set_index("fecha")[[
        "Lecturas programadas",
        "Lecturas realizadas s/FTL"
    ]]
)





# df_graf = df_evol.rename(columns={
#     "total_programados": "Lecturas programadas",
#     "total_leidos_actual": "Lecturas realizadas"
# })

# fig = px.line(
#     df_graf,
#     x="fecha",
#     y=["Lecturas programadas", "Lecturas realizadas"],
#     labels={
#         "fecha": "Día de lectura",
#         "value": "Cantidad de lecturas",
#         "variable": "Tipo"
#     }
# )

# st.plotly_chart(fig, use_container_width=True)



# st.line_chart(
#     df_evol.set_index("fecha")[[
#         "total_programados",
#         "total_leidos_ftl"
#     ]]
# )
# st.line_chart(
#     df_evol.set_index("fecha_str")[[
#         "total_programados",
#         "total_leidos_ftl"
#     ]]
# )













# ----------------------------------
# GRAFICO EVOLUCION DIARIA DE LECTURAS
# -----------------------------------
st.space("large") # Añade un espacio grande
st.subheader("Evolución diaria de lecturas")

# df_evol = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_ftl":"sum"
# }).reset_index()
df_evol = df_base.groupby(df_base["f_lteor"].dt.date).agg({
    "total_programados":"sum",
    "total_leidos_actual":"sum"
}).reset_index()

# df_evol["fecha_str"] = df_evol["f_lteor"].dt.strftime("%d-%m")
# df_evol["dia"] = df_evol["f_lteor"].dt.day

df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

df_graf = df_evol.rename(columns={
    "total_programados": "Lecturas programadas",
    "total_leidos_actual": "Lecturas realizadas"
})

st.line_chart(
    df_graf.set_index("fecha")[[
        "Lecturas programadas",
        "Lecturas realizadas"
    ]]
)


# st.line_chart(
#     df_evol.set_index("fecha")[[
#         "total_programados",
#         "total_leidos_actual"
#     ]]
# )
# st.line_chart(
#     df_evol.set_index("fecha_str")[[
#         "total_programados",
#         "total_leidos_ftl"
#     ]]
# )





















# ----------------------------------
# GRAFICO EVOLUCION DIARIA DE LECTURAS
# -----------------------------------
st.space("large") # Añade un espacio grande
st.subheader("Evolución diaria de lecturas")

# df_evol = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_ftl":"sum"
# }).reset_index()
df_evol = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
    "total_programados":"sum",
    "total_leidos_ftl":"sum"
}).reset_index()

# df_evol["fecha_str"] = df_evol["f_lteor"].dt.strftime("%d-%m")
# df_evol["dia"] = df_evol["f_lteor"].dt.day

df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

df_graf = df_evol.rename(columns={
    "total_programados": "Lecturas programadas",
    "total_leidos_ftl": "Lecturas realizadas s/FTL"
})

st.line_chart(
    df_graf.set_index("fecha")[[
        "Lecturas programadas",
        "Lecturas realizadas s/FTL"
    ]]
)


# st.line_chart(
#     df_evol.set_index("fecha")[[
#         "total_programados",
#         "total_leidos_ftl"
#     ]]
# )
# st.line_chart(
#     df_evol.set_index("fecha_str")[[
#         "total_programados",
#         "total_leidos_ftl"
#     ]]
# )
















# ----------------------------------
# GRAFICO EVOLUCION DIARIA DE LECTURAS
# -----------------------------------
st.space("large") # Añade un espacio grande
st.subheader("Evolución diaria de lecturas")

# df_evol = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados":"sum",
#     "total_leidos_ftl":"sum"
# }).reset_index()
df_evol = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
    "total_programados":"sum",
    "total_leidos_actual":"sum"
}).reset_index()

# df_evol["fecha_str"] = df_evol["f_lteor"].dt.strftime("%d-%m")
# df_evol["dia"] = df_evol["f_lteor"].dt.day

df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

df_graf = df_evol.rename(columns={
    "total_programados": "Lecturas programadas",
    "total_leidos_actual": "Lecturas realizadas"
})

st.line_chart(
    df_graf.set_index("fecha")[[
        "Lecturas programadas",
        "Lecturas realizadas"
    ]]
)


# st.line_chart(
#     df_evol.set_index("fecha")[[
#         "total_programados",
#         "total_leidos_actual"
#     ]]
# )
# st.line_chart(
#     df_evol.set_index("fecha_str")[[
#         "total_programados",
#         "total_leidos_ftl"
#     ]]
# )











st.space("large") # Añade un espacio grande
st.subheader("Progreso del período de lectura")

progreso_periodo = dias_transcurridos / total_dias if total_dias > 0 else 0

st.progress(progreso_periodo)

st.caption(
    f"{dias_transcurridos} de {total_dias} días del período transcurridos "
    f"({progreso_periodo*100:.1f}%)"
)




st.space("large") # Añade un espacio grande
st.subheader("Desempeño diario")

# df_heatmap = df_filtrado.groupby(df_filtrado["f_lteor"].dt.date).agg({
#     "total_programados": "sum",
#     "total_leidos_ftl": "sum"
# }).reset_index()
df_heatmap = df_base.groupby(df_base["f_lteor"].dt.date).agg({
    "total_programados": "sum",
    "total_leidos_ftl": "sum"
}).reset_index()

df_heatmap["avance_pct"] = (
    df_heatmap["total_leidos_ftl"] /
    df_heatmap["total_programados"] * 100
)

df_heatmap = df_heatmap.rename(columns={"f_lteor":"fecha"})


def color_avance(val):
    if val >= 95:
        color = "#16a34a"   # verde
    elif val >= 85:
        color = "#f59e0b"   # amarillo
    else:
        color = "#ef4444"   # rojo
    return f"background-color: {color}; color: white"


st.dataframe(
    df_heatmap.style.applymap(color_avance, subset=["avance_pct"])
    .format({
        "avance_pct": "{:.1f}%"
    }),
    use_container_width=True
)




# -----------------------------------
# TABLA
# -----------------------------------
st.space("large") # Añade un espacio grande
st.subheader("Datos filtrados s/ plazos reglamentarios + atraso")
st.dataframe(df_filtrado, use_container_width=True)

st.space("large") # Añade un espacio grande
st.subheader("Datos filtrados s/ mes y tarifa")
st.dataframe(df_base, use_container_width=True)

st.space("large") # Añade un espacio grande
st.subheader("Todos los datos")
st.dataframe(df, use_container_width=True)





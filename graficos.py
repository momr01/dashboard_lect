import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def graf_ev_lect_atraso_ritmo(
        df,
        col_leidos,
        titulo="Evolución diaria de lecturas",
        key="grafico",
        titulo_col_leidos="Lecturas realizadas",
        mostrar_markers=True
    ):

    df_evol = df.groupby(df["f_lteor"].dt.date).agg({
        "total_programados":"sum",
        col_leidos:"sum"
    }).reset_index()

    df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

    df_graf = df_evol.rename(columns={
        "total_programados": "Lecturas programadas",
        col_leidos: titulo_col_leidos
    })

    # atraso
    df_graf["Atraso diario"] = (
        df_graf["Lecturas programadas"] -
        df_graf[titulo_col_leidos]
    )

    # ritmo ideal
    total_programado = df_graf["Lecturas programadas"].sum()
    total_dias = len(df_graf)

    df_graf["dia_n"] = range(1, total_dias + 1)

    df_graf["Ritmo ideal"] = (
        total_programado / total_dias
    ) * df_graf["dia_n"]

    fig = go.Figure()

    mode = "lines+markers+text" if mostrar_markers else "lines"

    # PROGRAMADOS
    fig.add_trace(go.Scatter(
        x=df_graf["fecha"],
        y=df_graf["Lecturas programadas"],
        mode=mode,
        name="Lecturas programadas",
        line=dict(color="#2563eb"),
        text=df_graf["Lecturas programadas"] if mostrar_markers else None,
        texttemplate="%{text:,.0f}" if mostrar_markers else None,
        textposition="top center"
    ))

    # LEIDOS
    fig.add_trace(go.Scatter(
        x=df_graf["fecha"],
        y=df_graf[titulo_col_leidos],
        mode=mode,
        name=titulo_col_leidos,
        line=dict(color="#16a34a"),
        text=df_graf[titulo_col_leidos] if mostrar_markers else None,
        texttemplate="%{text:,.0f}" if mostrar_markers else None,
        textposition="bottom center",
        fill="tonexty",
        fillcolor="rgba(239,68,68,0.25)"
    ))

    # RITMO IDEAL
    fig.add_trace(go.Scatter(
        x=df_graf["fecha"],
        y=df_graf["Ritmo ideal"],
        mode="lines",
        name="Ritmo ideal",
        line=dict(
            color="#f59e0b",
            dash="dash",
            width=3
        )
    ))

    fig.update_layout(
        title=titulo,
        xaxis_title="Día de lectura",
        yaxis_title="Cantidad de lecturas",
        yaxis=dict(tickformat=",")
    )

    st.plotly_chart(fig, use_container_width=True, key=key)





def graf_ev_lect(
        df,
        col_leidos,
        titulo="Evolución diaria de lecturas",
        key="grafico",
        titulo_col_leidos="Lecturas realizadas"
    ):
    df_evol = df.groupby(df["f_lteor"].dt.date).agg({
        "total_programados":"sum",
        col_leidos:"sum"
    }).reset_index()

    df_evol = df_evol.rename(columns={"f_lteor":"fecha"})

    df_graf = df_evol.rename(columns={
        "total_programados": "Lecturas programadas",
        col_leidos: titulo_col_leidos
    })

    # import plotly.express as px

    fig = px.line(
        df_graf,
        x="fecha",
        y=["Lecturas programadas", titulo_col_leidos],
        labels={
            "fecha": "Día de lectura",
            "value": "Cantidad de lecturas",
            "variable": "Tipo"
        },
        markers=True,
        title=titulo,
        color_discrete_sequence=[
        "#2563eb",  # azul programados
        "#16a34a",  # verde leídos
     ]
    )

    fig.update_layout(
        yaxis=dict(
            tickformat=","
        )
    )

    st.plotly_chart(fig, use_container_width=True, key=key)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Volve Production Insights",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ESTILO CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    [data-testid="stSidebar"] {
        background-color: #0e1117;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


# --- LÓGICA DE CÁLCULO (Se mantiene intacta) ---
def j_calc(q_test, pwf_test, pr, pb, ef=1):
    if ef == 1:
        if pwf_test >= pb:
            return q_test / (pr - pwf_test)
        else:
            return q_test / ((pr - pb) + (pb / 1.8) * (
                        1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))
    else:
        if pwf_test >= pb:
            return q_test / (pr - pwf_test)
        else:
            return q_test / ((pr - pb) + (pb / 1.8) * (
                        1.8 * (1 - pwf_test / pb) - 0.8 * ef * (
                            1 - pwf_test / pb) ** 2))


def Qo_calc(q_test, pwf_test, pr, pwf, pb, ef=1):
    j_val = j_calc(q_test, pwf_test, pr, pb, ef)
    if pwf >= pb:
        return j_val * (pr - pwf)
    else:
        q_at_pb = j_val * (pr - pb)
        if ef == 1:
            return q_at_pb + ((j_val * pb) / 1.8) * (
                        1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2)
        else:
            return q_at_pb + ((j_val * pb) / 1.8) * (
                        1.8 * (1 - pwf / pb) - 0.8 * ef * (1 - pwf / pb) ** 2)


# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.image(
        "https://www.shutterstock.com/image-vector/oil-rig-logo-template-vector-260nw-1490217038.jpg",
        width=100)  # Placeholder para logo
    st.title("Volve Analytics")
    st.markdown("---")
    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Historial VOLVE", "Potencial Yacimiento", "Análisis Nodal"],
        icons=["house", "database", "graph-up-arrow", "vector-pen"],
        menu_icon="cast",
        default_index=2,
        styles={
            "container": {"padding": "0!important", "background-color": "#0e1117"},
            "icon": {"color": "#00d4ff", "font-size": "18px"},
            "nav-link": {"color": "white", "font-size": "15px", "text-align": "left",
                         "margin": "0px"},
            "nav-link-selected": {"background-color": "#262730"},
        }
    )

# --- SECCIÓN: INICIO ---
if selected == "Inicio":
    st.title("🚀 Dashboard de Ingeniería de Producción")
    st.markdown("""
    Bienvenido a la plataforma de análisis del *Campo Volve*. 
    Esta herramienta permite optimizar la toma de decisiones mediante:
    * *Visualización de Históricos:* Análisis de tendencias de producción.
    * *Modelado IPR:* Curvas de oferta del yacimiento.
    * *Optimización:* Análisis nodal y sensibilidad.
    """)

    col_a, col_b = st.columns(2)
    with col_a:
        st.info(
            "💡 *Tip:* Comience configurando los datos en la sección 'Potencial Yacimiento'.")

# --- SECCIÓN: POTENCIAL DEL YACIMIENTO ---
elif selected == "Potencial Yacimiento":
    st.subheader("🎯 Análisis de Potencial y Curva IPR")

    # Layout de entrada y salida
    main_col1, main_col2 = st.columns([1, 2.5], gap="large")

    with main_col1:
        with st.container(border=True):
            st.markdown("### 📥 Parámetros")
            pr = st.number_input("Presión Reservorio (psi)", value=4000)
            pb = st.number_input("Presión Burbuja (psi)", value=2500)
            ef = st.slider("Eficiencia de Flujo", 0.1, 2.0, 1.0, 0.1)

            st.markdown("---")
            st.markdown("### 🧪 Datos de Prueba")
            q_test = st.number_input("Caudal prueba (bpd)", value=800)
            pwf_test = st.number_input("Pwf prueba (psi)", value=3200)

    with main_col2:
        # Cálculo de valores clave
        j_val = j_calc(q_test, pwf_test, pr, pb, ef)
        aof_val = Qo_calc(q_test, pwf_test, pr, 0, pb, ef)
        qb_val = j_val * (pr - pb)

        # KPIs en la parte superior
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Índice de Prod. (J)", f"{j_val:.2f}",
                    help="Barriles por día por cada psi de caída")
        kpi2.metric("Qb @ Pb", f"{qb_val:.0f} bpd")
        kpi3.metric("AOF (Potencial Máx)", f"{aof_val:.0f} bpd", delta_color="normal")

        # Espacio para el gráfico
        with st.container(border=True):
            pwf_values = np.linspace(0, pr, 100)
            qo_values = [Qo_calc(q_test, pwf_test, pr, p, pb, ef) for p in pwf_values]

            fig = go.Figure()

            # Línea IPR
            fig.add_trace(go.Scatter(
                x=qo_values, y=pwf_values,
                name="Curva IPR",
                line=dict(color='#00d4ff', width=4),
                fill='tozerox',  # Sombreado bajo la curva
                fillcolor='rgba(0, 212, 255, 0.1)'
            ))

            # Punto de la prueba
            fig.add_trace(go.Scatter(
                x=[q_test], y=[pwf_test],
                mode='markers',
                name='Punto de Prueba',
                marker=dict(color='orange', size=12, symbol='diamond')
            ))

            # Estética del gráfico
            fig.update_layout(
                title="<b>Inflow Performance Relationship (IPR)</b>",
                xaxis_title="Caudal (bpd)",
                yaxis_title="Pwf (psi)",
                template="plotly_dark",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=50, b=20),
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )

            # Línea de Pb
            fig.add_hline(y=pb, line_dash="dash", line_color="red",
                          annotation_text=f"Pb: {pb} psi",
                          annotation_position="top right")

            st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN: HISTORIAL VOLVE ---
elif selected == "Historial VOLVE":
    st.title("📊 Historial de Producción")
    st.info("Cargue los datos históricos para visualizar el comportamiento del campo.")

    uploaded_file = st.file_uploader("Cargar archivo Excel de Volve",
                                     type=["xlsx", "csv"])

    if uploaded_file:
        st.success("Archivo cargado correctamente (Simulación)")
        # Aquí iría el código de procesamiento de datos

# --- SECCIÓN: ANÁLISIS NODAL ---
elif selected == "Análisis Nodal":
    st.title("🕸️ Análisis Nodal")
    st.warning("Sección en desarrollo: Integración de curvas VLP próximamente.")

# --- FOOTER ---
st.markdown("---")
st.caption("Desarrollado para Ingeniería de Producción | Campo Volve Open Data Project")
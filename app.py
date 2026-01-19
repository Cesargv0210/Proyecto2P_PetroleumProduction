import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Production Analisis",
    page_icon="Logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
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
    /* OCULTAR SOLO EL MENÚ SUPERIOR */
    header {
    display: none;
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

# --- LÓGICA DE CÁLCULO ---
def j(q_test, pwf_test, pr, pb, ef=1, ef2=None):
    if ef == 1 and pb is None:
        J = q_test/(pr - pwf_test)
    if ef == 1 and pb is not None:  # Darcy & Vogel
        if pwf_test >= pb:  # Subsaturated reservoir
            J = q_test / (pr - pwf_test)
        else:  # Saturated reservoir
            J = q_test / ((pr - pb) + (pb / 1.8) * \
            (1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))

    elif ef != 1 and ef2 is None and pb is not None:  # Darcy & Standing
        if pwf_test >= pb:  # Subsaturated reservoir
            J = q_test / (pr - pwf_test)
        else:  # Saturated reservoir
            J = q_test / ((pr - pb) + (pb / 1.8) * \
            (1.8 * (1 - pwf_test / pb) - 0.8 * ef * (
             1 - pwf_test / pb) ** 2))

    elif ef != 1 and ef2 is not None and pb is not None:  # Darcy & Standing
        if pwf_test >= pb:  # Subsaturated reservoir
            J = ((q_test / (pr - pwf_test)) / ef) * ef2
        else:  # Saturated reservoir
            J = ((q_test / ((pr - pb) + (pb / 1.8) * \
            (1.8 * (1 - pwf_test / pb) - 0.8 * \
            ef * (1 - pwf_test / pb) ** 2))) / ef) * ef2
    return J

def J_Darcy(pr, pwf_test, q_test):
    J = q_test/(pr - pwf_test)
    return J
def Q_Darcy(J, Pr, pwf):
    Q = J * (Pr - pwf)
    return Q

def faming(Q, ID):
    f = (2.083/1000)((100*Q/(34.3*120))1.85)((1/ID)**4.8655)
    return f

def Qo_calc(q_test, pwf_test, pr, pwf, pb, ef=1):
    j_val = j(q_test, pwf_test, pr, pb, ef)
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
        "Company.png",
        width=200)  # Placeholder para logo
    st.markdown(
        """
        <div style="
            color:#f39c12;
            text-align:center;
            font-size:30px;
            font-weight:700;
            margin-bottom:12px;
        ">
            Production Analisis
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        """
        <h4 style="
            color:#f39c12;
            text-align:left;
            margin:10px 0px 5px 0px;
        ">
            Options
        </h4>
        """,
        unsafe_allow_html=True
    )
    selected = option_menu(
        menu_title=None,
        options=["Inicio", "Historial VOLVE", "Potencial Yacimiento", "Análisis Nodal"],
        icons=["house", "database", "graph-up-arrow", "vector-pen"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#0e1117"},
            "icon": {"color": "#f39c12", "font-size": "18px"},
            "nav-link": {"color": "white", "font-size": "15px", "text-align": "left",
                         "margin": "0px"},
            "nav-link-selected": {"background-color": "#262730"},
        }
    )

# --- SECCIÓN: INICIO ---
if selected == "Inicio":

    # --- HERO SECTION ---
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0e1117, #1f2933);
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
    ">
        <h1 style="color:#f39c12; font-size:42px; margin-bottom:10px;">
            Production Analysis Dashboard
        </h1>
        <p style="color:#d1d5db; font-size:18px; max-width:900px;">
            Plataforma interactiva para el análisis integral de producción,
            evaluación del potencial del yacimiento y análisis nodal del sistema
            yacimiento–pozo–superficie.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- MÉTRICAS RESUMEN ---
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📊 Módulos Activos", "4")
    col2.metric("🛢️ Campo", "VOLVE")
    col3.metric("⚙️ Modelos", "Darcy • Vogel • Standing.")
    col4.metric("📈 Enfoque", "Ingeniería de Producción")

    st.markdown("---")

    # --- TARJETAS DE MÓDULOS ---
    st.markdown("## 🔎 Módulos Disponibles")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="stMetric">
        <h4>📊 Historial VOLVE</h4>
        <p style="font-size:14px;">
        Visualización histórica de producción de petróleo y agua por pozo.
        Identificación de tendencias y comportamiento productivo.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="stMetric">
        <h4>🎯 Potencial del Yacimiento</h4>
        <p style="font-size:14px;">
        Evaluación del índice de productividad, curvas IPR (Darcy/Vogel)
        y estimación del AOF.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="stMetric">
        <h4>📈 Análisis Nodal</h4>
        <p style="font-size:14px;">
        Integración IPR–VLP–Sistema para análisis del punto de operación
        del pozo.
        </p>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="stMetric">
        <h4>⚙️ Optimización</h4>
        <p style="font-size:14px;">
        Evaluación de sensibilidad operacional y soporte a decisiones
        de levantamiento artificial.
        </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- FLUJO RECOMENDADO ---
    st.markdown("## 🧭 Flujo Recomendado de Uso")

    st.markdown("""
    1. *Historial VOLVE*  
       Analice el comportamiento histórico del pozo (oil y water).

    2. *Potencial del Yacimiento*  
       Determine el índice de productividad y el potencial máximo (AOF).

    3. *Análisis Nodal*  
       Integre el sistema completo para identificar el punto de operación.

    > 💡 Este flujo replica el proceso real de evaluación en ingeniería de producción.
    """)

    st.markdown("---")

    # --- MENSAJE FINAL ---
    st.info(
        "📌 Esta herramienta está diseñada para análisis técnico, soporte a decisiones "
        "operacionales y entrenamiento en ingeniería de producción."
    )
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
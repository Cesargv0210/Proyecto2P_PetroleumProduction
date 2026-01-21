import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# --- CONFIGURACIÓN DE PÁGINA --
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
#<<<<<<< Paso_5
    f = (2.083/1000)*((100*Q/(34.3*120))**1.85)*((1/ID)**4.8655)
#=======
    f = (2.083/1000)*((100*Q/(34.3*120))*1.85)*((1/ID)**4.8655)
#>>>>>>> develop
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


def Qo(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    ef_activa = ef if ef2 is None else ef2
    j_val = j(q_test, pwf_test, pr, pb, ef, ef2)

    # Yacimiento saturado
    if pb is not None and pr < pb:
        return ((j_val * pr) / 1.8) * (
            1 - 0.2 * (pwf / pr) - 0.8 * (pwf / pr) ** 2
        )

    # Darcy
    if pb is None or pwf >= pb:
        return j_val * (pr - pwf)

    # Vogel / Standing
    q_at_pb = j_val * (pr - pb)

    if ef_activa == 1:
        return q_at_pb + ((j_val * pb) / 1.8) * (
            1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2
        )
    else:
        return q_at_pb + ((j_val * pb) / 1.8) * (
            1.8 * (1 - pwf / pb) -
            0.8 * ef_activa * (1 - pwf / pb) ** 2
        )

###################################################################################
#Calculos
# Productivity Index
def j(q_test, pwf_test, pr, pb, ef=1, ef2 = 1):
    if ef == 1:  # Darcy & Vogel
        if pwf_test >= pb:  # Subsaturated reservoir
            J = q_test / (pr - pwf_test)
        else:  # Saturated reservoir
            J = q_test / ((pr - pb) + (pb / 1.8) * \
                          (1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))

    elif ef != 1 and ef2 == 1:  # Darcy & Standing
        if pwf_test >= pb:  # Subsaturated reservoir
            J = q_test / (pr - pwf_test)
        else:  # Saturated reservoir
            J = q_test / ((pr - pb) + (pb / 1.8) * \
                          (1.8 * (1 - pwf_test / pb) - 0.8 * ef * (
                                      1 - pwf_test / pb) ** 2))

    elif ef != 1 and ef2 != 1:  # Darcy & Standing
        if pwf_test >= pb:  # Subsaturated reservoir
            J = ((q_test / (pr - pwf_test)) / ef) * ef2
        else:  # Saturated reservoir
            J = ((q_test / ((pr - pb) + (pb / 1.8) * \
                            (1.8 * (1 - pwf_test / pb) - 0.8 * \
                             ef * (1 - pwf_test / pb) ** 2))) / ef) * ef2
    return J

# Q(bpd) @ Pb
def Qb(q_test, pwf_test, pr, pb, ef=1, ef2= 1):
    qb = j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pb)
    return qb


# AOF(bpd)
def aof(q_test, pwf_test, pr, pb, ef=1, ef2= 1):
    if (ef == 1 and ef2 == 1):  # Darcy & Vogel
        if pr > pb:  # Yac. subsaturado
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef=1) + (
                            (j(q_test, pwf_test, pr, pb) * pb) / 1.8)
        else:  # Yac. Saturado
            AOF = q_test / (1 - 0.2 * (pwf_test / pr) - 0.8 * (pwf_test / pr) ** 2)

    elif (ef < 1 and ef2 == 1):  # Darcy & Standing
        if pr > pb:  # Yac. subsatuado
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef) + (
                            (j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                                  1.8 - 0.8 * ef)
        else:  # Yac. saturado
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                        1 - pwf_test / pr) ** 2)) * (1.8 * ef - 0.8 * ef ** 2)

    elif (ef > 1 and ef2 == 1):  # Darcy & Standing
        if pr > pb:  # Yac. subsaturado
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef) + (
                            (j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                                  0.624 + 0.376 * ef)
        else:  # Yac. saturado
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                        1 - pwf_test / pr) ** 2)) * (0.624 + 0.376 * ef)

    elif (ef < 1 and ef2 >= 1):  # Darcy & Standing (stimulation)
        if pr > pb:  # Yac. subsaturado
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef, ef2) + (
                            j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                                  0.624 + 0.376 * ef2)
        else:  # Yac. saturado
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                        1 - pwf_test / pr) ** 2)) * (0.624 + 0.376 * ef2)

    elif (ef > 1 and ef2 <= 1):  # Darcy & Standing (Higher skin)
        if pr > pb:  # Yac. subsaturado
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef, ef2) + (
                            j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                                  1.8 - 0.8 * ef2)
        else:  # Yac. saturado
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                        1 - pwf_test / pr) ** 2)) * (1.8 - 0.8 * ef2 ** 2)

    return AOF

# Qo (bpd) @ Darcy Conditions
def qo_darcy(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    qo = j(q_test, pwf_test, pr, pb) * (pr - pwf)
    return qo

#Qo(bpd) @ vogel conditions
def qo_vogel(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    qo = aof(q_test, pwf_test, pr, pb) * \
         (1 - 0.2 * (pwf / pr) - 0.8 * ( pwf / pr)**2)
    return qo

# Qo(bpd) @Standing Conditions
def qo_standing(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    qo = aof(q_test, pwf_test, pr, pb, ef) * (1.8 * ef * (1 - pwf / pr) - 0.8 * ef**2 * (1 - pwf / pr)**2)
    return qo

#Qo(bpd) @ all conditions
def Qo(q_test, pwf_test, pr, pwf, pb, ef=1, ef2= 1):
    qo = 0  # Initialize qo with a default value

    if ef == 1 and ef2 == 1:
        if pr > pb:  # Yacimiento subsaturado
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb)
            elif pwf < pb:
                qo = Qb(q_test, pwf_test, pr, pb) + \
                    ((j(q_test, pwf_test, pr, pb) * pb) / 1.8) * \
                    (1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb)**2)
        else:  # Yacimiento saturado
            qo = qo_vogel(q_test, pwf_test, pr, pwf, pb)

    elif ef != 1 and ef2 == 1:
        if pr > pb:  # Yacimiento subsaturado
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef)
            elif pwf < pb:
                qo = Qb(q_test, pwf_test, pr, pb, ef) + \
                    ((j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * \
                    (1.8 * (1 - pwf / pb) - 0.8 * ef * (1 - pwf / pb)**2)
        else:  # Yacimiento saturado
            qo = qo_standing(q_test, pwf_test, pr, pwf, pb, ef)

    elif ef != 1 and ef2 != 1:
        if pr > pb:  # Yacimiento subsaturado
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
            elif pwf < pb:
                qo = Qb(q_test, pwf_test, pr, pb, ef, ef2) + \
                    ((j(q_test, pwf_test, pr, pb, ef, ef2) * pb) / 1.8) * \
                    (1.8 * (1 - pwf / pb) - 0.8 * ef * (1 - pwf / pb)**2)
        else:  # Yacimiento saturado
            qo = qo_standing(q_test, pwf_test, pr, pwf, pb, ef, ef2)

    else:
        raise ValueError("Invalid combination of ef and ef2 values")

    return qo


# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.image(
        "Company.png",
        width=500)  # Placeholder para logo
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

    # --- IMAGEN DEBAJO DEL HERO ---
    st.image(
        "Sistema_produccion.png",
        use_container_width=True
    )

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

    st.markdown("""
    <h2 style="font-size:36px; color:#f39c12;">
        ¿Qué hace un ingeniero en producción?
    </h2>
    """, unsafe_allow_html=True)

    main_col1, main_col2 = st.columns([2, 2], gap="large")

    # ---------------- INPUTS ----------------
    with main_col1:
        with st.container(border=True):
            st.markdown("# COMO SE FORMO EL PETROLEO")
            st.markdown("## rompiendo mitos, el petroleo se forma de una manera increible"
                        ", y no es de los dinosaurios como todos creen")
            # --- VIDEO LOCAL ---
            st.video("https://www.youtube.com/watch?v=KQbWFGB_Io4")
    with main_col2:
        with st.container(border=True):
            st.markdown("# QUE ES LA INGERNERIA PETROLERA")
            st.markdown("## Conoce los diferentes campos y oportunidades que ofrece la ingeneria petrolera")
            # --- VIDEO LOCAL ---
            st.video("petroleos.mp4")

    # --- MENSAJE FINAL ---
    st.info(
        "📌 Esta herramienta está diseñada para análisis técnico, soporte a decisiones "
        "operacionales y entrenamiento en ingeniería de producción."
    )
    st.info(
        "📌 Esta pagina fue desarrollada por Cesar Garcia (Geologia) y Marco Aspiazu (Petroleos)."
    )

#-----SECCION POTENCIAL YACIMIENTO-----------------------
elif selected == "Potencial Yacimiento":
    st.title("🎯 Análisis de Potencial y Curva IPR")

    main_col1, main_col2 = st.columns([1, 3], gap="large")

    # ---------------- INPUTS ----------------
    with main_col1:
        with st.container(border=True):
            st.markdown("### 📥 Parámetros")

            pr = st.number_input("Presión Reservorio (psi)", value=4000)

            use_pb = st.checkbox("Considerar Presión de Burbuja (Pb)", value=True)
            pb = st.number_input("Presión Burbuja (psi)", value=2500) if use_pb else 0

            ef = st.slider("Eficiencia de Flujo", 0.1, 2.0, 1.0, 0.1)

            use_ef2 = st.checkbox("Considerar Eficiencia de Flujo 2", value=False)
            ef2 = st.slider("Eficiencia de Flujo 2", 0.1, 2.0, 1.0, 0.1) if use_ef2 else 1

            st.markdown("---")
            st.markdown("### 🧪 Datos de Prueba")
            q_test = st.number_input("Caudal prueba (bpd)", value=800)
            pwf_test = st.number_input("Pwf prueba (psi)", value=3200)

    # ---------------- CALCULOS ----------------
    with main_col2:

        j_val = j(q_test, pwf_test, pr, pb, ef, ef2)
        aof_val = aof(q_test, pwf_test, pr, pb, ef, ef2)

        if pb is None or pr <= pb:
            qb_val = None
        else:
            qb_val = Qb(q_test, pwf_test, pr, pb, ef, ef2)

        # ---------------- KPIs ----------------
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        kpi1.metric("Índice de Prod. (J)", f"{j_val:.2f}")

        kpi2.metric(
            "Qb @ Pb",
            "NO" if (pb == 0 or pr < pb) else f"{qb_val:.0f} bpd"
        )

        kpi3.metric("AOF (Caudal Máximo)", f"{aof_val:.0f} bpd")

        if pb == 0:
            modelo = "Darcy"
        elif pr > pb and ef == 1:
            modelo = "Darcy + Vogel"
        elif pr < pb and ef == 1:
            modelo = "Vogel"
        elif pr < pb and ef != 1:
            modelo = "Standing"
        elif pr > pb and ef != 1:
            modelo = "Darcy + Standing"

        kpi4.metric("Modelo", modelo)

        # ---------------- GRAFICA IPR ----------------
        with st.container(border=True):

            pwf_values = np.linspace(0, pr, 100)

            # ===============================
            # CASO 1: SIN PRESIÓN DE BURBUJA
            # ===============================
            if pb == 0:

                # EF1 (Darcy puro)
                j_ef1 = j(q_test, pwf_test, pr, pb, ef, None)
                qo_values_ef1 = [
                    j_ef1 * (pr - p)
                    for p in pwf_values
                ]

                # EF2 (Darcy con J ajustado)
                if ef2 == 1:
                    j_ef2 = j(q_test, pwf_test, pr, pb, ef, ef2)
                    qo_values_ef2 = [
                        j_ef2 * (pr - p)
                        for p in pwf_values
                    ]

            # ===============================
            # CASO 2: CON PRESIÓN DE BURBUJA
            # ===============================
            else:

                # EF1 (Darcy / Vogel / Standing)
                qo_values_ef1 = [
                    Qo(q_test, pwf_test, pr, p, pb, ef, ef2)
                    for p in pwf_values
                ]

                # EF2 (si existe)
                if ef2 != 1:
                    qo_values_ef2 = [
                        Qo(q_test, pwf_test, pr, p, pb, ef, ef2)
                        for p in pwf_values
                    ]

            # ===============================
            # CONSTRUCCIÓN DE LA GRÁFICA
            # ===============================
            fig = go.Figure()

            # Curva IPR – EF1
            fig.add_trace(go.Scatter(
                x=qo_values_ef1,
                y=pwf_values,
                name=f"IPR – EF1 = {ef}",
                line=dict(color='#00d4ff', width=4),
                fill='tozerox',
                fillcolor='rgba(0, 212, 255, 0.1)'
            ))

            # Curva IPR – EF2 (si existe)
            if ef2 != 1:
                fig.add_trace(go.Scatter(
                    x=qo_values_ef2,
                    y=pwf_values,
                    name=f"IPR – EF2 = {ef2}",
                    line=dict(color='lime', width=3, dash='dash')
                ))

            # Punto de prueba
            fig.add_trace(go.Scatter(
                x=[q_test],
                y=[pwf_test],
                mode='markers',
                name='Punto de Prueba',
                marker=dict(color='orange', size=12, symbol='diamond')
            ))

            # Línea de Pb (solo si existe)
            if pb != 0:
                fig.add_hline(
                    y=pb,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Pb: {pb} psi",
                    annotation_position="top right"
                )

            # Estética
            fig.update_layout(
                title="<b>Inflow Performance Relationship (IPR)</b>",
                xaxis_title="Caudal (bpd)",
                yaxis_title="Pwf (psi)",
                template="plotly_dark",
                hovermode="x unified",
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )

            st.plotly_chart(fig, use_container_width=True)


# --- SECCIÓN: HISTORIAL VOLVE ---
elif selected == "Historial VOLVE":
    st.title("📊 Historial de Producción – Campo Volve")

    # --- IMAGEN DEBAJO DEL HERO ---
    st.image(
        "Volve.png",
        use_container_width=True
    )

    st.markdown("# INFORMACION CAMPO VOLVE (NORUEGA)")
    st.markdown("## El campo Volve, ubicado en el Mar del Norte, es conocido por sus "
                "importantes reservas de hidrocarburos y su complejidad geológica. "
                "Este campo ha sido objeto de numerosos estudios debido a su relevancia "
                "como reservorio productivo y la disponibilidad de su información al "
                "público.")

    # --- Carga de archivo ---
    uploaded_file = st.file_uploader(
        "Cargar Excel de producción",
        type="xlsx"
    )

    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name=1)
        st.success("Archivo cargado por el usuario")
    else:
        df = pd.read_excel("data/Volve_production_data.xlsx", sheet_name=1)
        st.warning("Usando archivo local por defecto")

    # --- Limpieza de columnas ---
    df.columns = df.columns.str.lower().str.strip()

    # --- Renombrar columnas ---
    df = df.rename(columns={
        "wellbore name": "WELL",
        "year": "TIME_YEARS",
        "oil": "Q_OIL",
        "water": "Q_WATER"
    })

    # --- Selector de pozo ---
    wells = sorted(df["WELL"].dropna().unique())
    selected_well = st.selectbox(
        "Seleccione un pozo",
        wells
    )

    df_well = df[df["WELL"] == selected_well]

    # --- GRÁFICAS ---
    col1, col2 = st.columns(2, gap="large")

    # 🛢️ Petróleo
    with col1:
        fig_oil = go.Figure()
        fig_oil.add_trace(go.Scatter(
            x=df_well["TIME_YEARS"],
            y=df_well["Q_OIL"],
            mode="lines+markers",
            name="Oil"
        ))

        fig_oil.update_layout(
            title=f"Caudal de Petróleo – {selected_well}",
            xaxis_title="Tiempo (años)",
            yaxis_title="Q Oil (bpd)",
            template="plotly_dark",
            height=400
        )

        st.plotly_chart(fig_oil, use_container_width=True)

    # 💧 Agua
    with col2:
        fig_water = go.Figure()
        fig_water.add_trace(go.Scatter(
            x=df_well["TIME_YEARS"],
            y=df_well["Q_WATER"],
            mode="lines+markers",
            name="Water"
        ))

        fig_water.update_layout(
            title=f"Caudal de Agua – {selected_well}",
            xaxis_title="Tiempo (años)",
            yaxis_title="Q Water (bpd)",
            template="plotly_dark",
            height=400
        )

        st.plotly_chart(fig_water, use_container_width=True)

    # --- GRÁFICA COMBINADA ---
    st.markdown("### 📈 Producción Oil + Water")

    fig_combined = go.Figure()

    fig_combined.add_trace(go.Scatter(
        x=df_well["TIME_YEARS"],
        y=df_well["Q_OIL"],
        mode="lines",
        name="Oil"
    ))

    fig_combined.add_trace(go.Scatter(
        x=df_well["TIME_YEARS"],
        y=df_well["Q_WATER"],
        mode="lines",
        name="Water"
    ))

    fig_combined.update_layout(
        title=f"Producción Total – {selected_well}",
        xaxis_title="Tiempo (años)",
        yaxis_title="Caudal (bpd)",
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(fig_combined, use_container_width=True)

    # --- TABLA ---
    with st.expander("📄 Ver datos del pozo"):
        st.dataframe(
            df_well[["TIME_YEARS", "Q_OIL", "Q_WATER"]],
            use_container_width=True
        )

# --- SECCIÓN: ANÁLISIS NODAL ---
elif selected == "Análisis Nodal":
    st.title("Análisis Nodal Monofasico")
    st.markdown(
        "Esta sección permite evaluar el comportamiento integral del sistema "
        "yacimiento–pozo–superficie mediante el análisis de curvas IPR y VLP."
    )

    # Layout de entrada y salida
    main_col1, main_col2 = st.columns([1, 2.5], gap="large")

    with main_col1:
        with st.container(border=True):
            st.markdown("### 📥 Parámetros")
            pr = st.number_input("Presión Reservorio (psi)", value=2800)
            q_test = st.number_input("Caudal prueba (bpd)", value=1500)
            pwf_test = st.number_input("Pwf prueba (psi)", value=2150)
            THP = st.number_input("THP (psi)", value=360)
            WC = st.number_input("corte de agua (%)", value=0.35)
            SGH2O = st.number_input("SGH2O", value=1.09)
            API = st.number_input("API", value=27)
            ID = st.number_input("Diametro interno (in)", value=3.5)
            TVD = st.number_input("True vertical depth (ft)", value=9000)
            MD = st.number_input("Measured Depth (ft)", value=10500)

    with main_col2:
        # Cálculo de valores clave
        j_val = J_Darcy(pr, pwf_test, q_test)
        AOF = Q_Darcy(j_val, pr, 0)
        SGoil = 141.5/(131.5 + API)
        SGavg = SGoil * (1 - WC) + SGH2O * WC
        Gavg = SGavg * 0.433
        Pg = SGavg * 0.433

        # KPIs en la parte superior
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Índice de Prod. (J)", f"{j_val:.2f} bbl/d/psi",
                    help="Barriles por día por cada psi de caída")
        kpi2.metric("AOF (caudal maximo)", f"{AOF:.0f} bpd")
        kpi3.metric("SGoil", f"{SGoil:.4f} ", delta_color="normal")
        kpi4.metric("SGavg", f"{SGavg:.4f} ", delta_color="normal")
        kpi5.metric("Gavg", f"{Gavg:.4f} psi/ft", delta_color="normal")

        st.markdown("---")

        st.markdown("### 📊 Tabla IPR – Nodal")

        # Rango de presiones desde Pr hasta 0 en pasos de 100 psi
        pressure_values = list(range(int(pr), -1, -100))

        # Caudales calculados con IPR (Darcy)
        Q_values = [Q_Darcy(j_val, pr, pwf) for pwf in pressure_values]

        # Factor de fricción
        f_values = [faming(Q, ID) for Q in Q_values]

        # Pérdida por fricción acumulada
        F_values = [f * MD for f in f_values]

        # Pérdida por fricción corregida por gravedad
        PF_values = [F * SGavg for F in F_values]

        # Presión de operación
        PO_values = [THP + Pg + PF for PF in PF_values]

        # Presión del sistema
        Psys_values = [PO - pwf for PO, pwf in zip(PO_values, pressure_values)]

        # DataFrame final
        df_nodal = pd.DataFrame({
            "Pwf (psi)": pressure_values,
            "Q (bpd)": Q_values,
            "THP (psi)": [THP] * len(pressure_values),
            "Pg (psi/ft)": [Pg] * len(pressure_values),
            "f": f_values,
            "F": F_values,
            "PF": PF_values,
            "PO (psi)": PO_values,
            "Psys (psi)": Psys_values
        })

        # Mostrar tabla
        st.dataframe(
            df_nodal,
            use_container_width=True,
            hide_index=True
        )

        fig = go.Figure()

        # Curva IPR
        fig.add_trace(go.Scatter(
            x=Q_values,
            y=pressure_values,
            mode="lines+markers",
            name="IPR",
            line=dict(dash="solid"),
            marker=dict(size=6)
        ))

        # Curva VLP
        fig.add_trace(go.Scatter(
            x=Q_values,
            y=PO_values,
            mode="lines+markers",
            name="VLP",
            line=dict(dash="dash"),
            marker=dict(size=6)
        ))

        # Curva del Sistema
        fig.add_trace(go.Scatter(
            x=Q_values,
            y=Psys_values,
            mode="lines+markers",
            name="Sistema",
            line=dict(dash="dot"),
            marker=dict(size=6)
        ))

        # Layout correcto para análisis nodal
        fig.update_layout(
            title="Curvas IPR – VLP – Sistema",
            xaxis_title="Caudal (bpd)",
            yaxis_title="Presión (psi)",
            yaxis_autorange= True,  # Presión decrece hacia abajo
            template="plotly_dark",
            legend=dict(x=0.01, y=0.99),
            height=500
        )

#<<<<<<< Paso_5
        st.plotly_chart(fig, use_container_width=True)
#=======
        st.plotly_chart(fig, use_container_width=True)
#>>>>>>> develop

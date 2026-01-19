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
    f = (2.083/1000)*((100*Q/(34.3*120))*1.85)*((1/ID)**4.8655)
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
    st.title("🎯 Análisis de Potencial y Curva IPR")

    # Layout de entrada y salida
    main_col1, main_col2 = st.columns([1, 3], gap="large")

    with main_col1:
        with st.container(border=True):
            st.markdown("### 📥 Parámetros")
            pr = st.number_input("Presión Reservorio (psi)", value=4000)
            use_pb = st.checkbox("Considerar Presión de Burbuja (Pb)", value=True)
            if use_pb:
                pb = st.number_input("Presión Burbuja (psi)", value=2500)
            else:
                pb = None
            ef = st.slider("Eficiencia de Flujo", 0.1, 2.0, 1.0, 0.1)

            st.markdown("---")
            st.markdown("### 🧪 Datos de Prueba")
            q_test = st.number_input("Caudal prueba (bpd)", value=800)
            pwf_test = st.number_input("Pwf prueba (psi)", value=3200)

    with main_col2:
        # Cálculo de valores clave
        j_val = j(q_test, pwf_test, pr, pb, ef)
        if pb is None:
            aof_val = j_val * pr
        else:
            aof_val = Qo_calc(q_test, pwf_test, pr, 0, pb, ef)

        if pb is None:
            qb_val = "NO"
        else:
            qb_val = j_val * (pr - pb)

        # KPIs en la parte superior
        kpi1, kpi2, kpi3, kpi4= st.columns(4)
        kpi1.metric("Índice de Prod. (J)", f"{j_val:.2f}",
                    help="Barriles por día por cada psi de caída")
        if pb is None:
            kpi2.metric("Qb @ Pb", "NO")
        else:
            kpi2.metric("Qb @ Pb", f"{qb_val:.0f} bpd")
        kpi3.metric("AOF (Potencial Máx)", f"{aof_val:.0f} bpd", delta_color="normal")

        if pb is None:
            kpi4.metric("Modelo", "Darcy")
        else:
            kpi4.metric("Modelo", "Vogel")


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
    st.title("📊 Historial de Producción – Campo Volve")

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
        kpi5.metric("Gavg", f"{Gavg:.4f} ", delta_color="normal")

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
            yaxis=dict(autorange="reversed"),  # Presión decrece hacia abajo
            template="plotly_dark",
            legend=dict(x=0.01, y=0.99),
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)
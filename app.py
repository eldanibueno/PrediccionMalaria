import streamlit as st
import matplotlib.pyplot as plt
import io

# Importar el backend de ecuaciones diferenciales
from malaria_engine import ejecutar_simulacion

st.set_page_config(page_title="Predicción de Malaria - Minsalud", layout="wide")

# Estilo visual clínico/médico
st.markdown(
    """
    <style>
      .stApp { background-color: #0d161f; color: #e1e9f0; }
      .stButton button { border-radius: 8px; font-weight: bold; color: #000000; }
      h1, h2, h3, h4, h5, span, p { color: #ffffff !important; }
      section[data-testid='stSidebar'] { background-color: #121e2b; }
      section[data-testid='stSidebar'] * { color: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🦠 Sistema Predictivo de Malaria — Zonas Rurales Colombia")
st.caption("Plataforma Epidemiológica Basada en Ecuaciones Diferenciales (Modelo Ross-Macdonald) para el Sistema Médico Colombiano")
st.markdown("---")

# 1. PARAMETRIZACIÓN REGIONAL (SELECCIÓN DE FOCO)
st.subheader("📍 Ubicación y Datos Demográficos del Foco de Estudio")

col_reg1, col_reg2, col_reg3 = st.columns(3)

with col_reg1:
    region = st.selectbox(
        "Seleccione el Departamento objetivo:",
        ["Chocó (Alto Atrato / Quibdó)", "Amazonas (Leticia / Tarapacá)", "Guaviare (San José / Retorno)"]
    )

# Configuración de población base adaptada según la región elegida
if "Chocó" in region:
    sh_def, sm_def = 8000.0, 35000.0
    beta_h_def, beta_m_def = 0.000025, 0.000015
elif "Amazonas" in region:
    sh_def, sm_def = 4500.0, 22000.0
    beta_h_def, beta_m_def = 0.000020, 0.000010
else: # Guaviare
    sh_def, sm_def = 5000.0, 20000.0
    beta_h_def, beta_m_def = 0.000020, 0.000010

with col_reg2:
    poblacion_humana = st.number_input("Población Humana Inicial (S_h)", min_value=100, max_value=50000, value=int(sh_def), step=500)

with col_reg3:
    poblacion_mosquitos = st.number_input("Población Estimada de Mosquitos (S_m)", min_value=500, max_value=200000, value=int(sm_def), step=1000)

# Iniciales de infectados en el día cero
st.markdown("##### Casos Iniciales Activos (Día 0)")
col_inf1, col_inf2 = st.columns(2)
with col_inf1:
    ih_0 = st.slider("Humanos Infectados Iniciales (I_h)", min_value=1, max_value=100, value=5)
with col_inf2:
    im_0 = st.slider("Mosquitos Infectados Iniciales (I_m)", min_value=1, max_value=500, value=20)


# 2. PANEL LATERAL: CONTROLES SANITARIOS (VARIABLES DE INTERVENCIÓN)
# Control para mostrar/ocultar la sidebar sin perder los controles
# Streamlit no permite “volver a abrir” la sidebar si el usuario la colapsa manualmente;
# por eso se renderiza un panel propio dentro del layout.
show_controls = st.sidebar.button("🛠️ Mostrar controles", use_container_width=True)

# Si el usuario no presiona, mostramos la sidebar colapsada por defecto.
# Además, si ya está abierta, mantenemos el botón visible para ocultar.
if 'controls_visible' not in st.session_state:
    st.session_state['controls_visible'] = True

# Alternar visibilidad cuando se presiona el botón
if show_controls:
    st.session_state['controls_visible'] = not st.session_state['controls_visible']

# Re-render condicional del panel de controles
if st.session_state['controls_visible']:
    with st.sidebar:
        st.header("🛡️ Estrategias de Control Médico")
    st.caption("Modifica los parámetros de las EDO según las intervenciones de salud pública:")
    
    st.markdown("---")
    # Control de tasas mediante acciones de mitigación
    uso_toldillos = st.slider("Uso de Toldillos / Mosquiteros (%)", 0, 100, 20)
    intensidad_fumigacion = st.slider("Campañas de Fumigación Vial (%)", 0, 100, 15)
    acceso_tratamiento = st.slider("Acceso Prontitud Tratamiento Médico (%)", 0, 100, 40)
    
    st.markdown("---")
    dias_simulacion = st.slider("Horizonte de Tiempo (Días)", 30, 365, 150)

# Ajuste matemático dinámico de los coeficientes de las EDO basado en los sliders sanitarios
# A mayor uso de toldillos y fumigación, decae la tasa de transmisión cruzada beta
factor_mitigacion = (1.0 - (uso_toldillos / 180.0)) * (1.0 - (intensidad_fumigacion / 200.0))
beta_h_efectiva = beta_h_def * factor_mitigacion
beta_m_efectiva = beta_m_def * factor_mitigacion

# Tasa de recuperación gamma (inversa del tiempo de enfermedad). Acceso médico rápido -> mayor gamma -> recuperación veloz
# Tasa de recuperación gamma (inversa del tiempo de enfermedad).
# Slider: acceso_tratamiento (%). A mayor acceso, mayor gamma.
gamma_efectiva = 0.05 + (acceso_tratamiento / 400.0)


# 3. EJECUCIÓN Y RESOLUCIÓN NUMÉRICA
if st.button("📈 Resolver Ecuaciones Diferenciales y Evaluar Riesgo"):
    
    # Invocar el resolvedor RK45 de scipy desde el motor
    res = ejecutar_simulacion(
        Sh_0=poblacion_humana,
        Ih_0=ih_0,
        Sm_0=poblacion_mosquitos,
        Im_0=im_0,
        beta_h=beta_h_efectiva,
        beta_m=beta_m_efectiva,
        gamma=gamma_efectiva,
        dias=dias_simulacion
    )
    
    # 4. ENTREGA DE ALERTAS BIOMÉDICAS (R0)
    st.markdown("### ⚠️ Diagnóstico Epidemiológico del Foco")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        st.metric("Número Reproductivo Básico (R₀)", f"{res.R0:.3f}")
    
    with col_m2:
        # Encontrar el pico de la curva de infectados humanos
        pico_casos = float(res.Ih.max())
        dia_pico = int(res.t[res.Ih.argmax()])
        st.metric("Pico Máximo de Contagios Humanos", f"{pico_casos:.1f} casos", f"Día {dia_pico}")
        
    with col_m3:
        # Estado de alerta según el R0 calculado
        if res.R0 > 1.0:
            st.error("🚨 ALERTA: Brote Epidémico Activo (R₀ > 1). La enfermedad se propagará en la región.")
        elif res.R0 < 1.0:
            st.success("✅ CONTROLADO: Brote en Decrecimiento (R₀ < 1). La malaria desaparecerá en el tiempo.")
        else:
            st.warning("⚠️ ESTABLE: Riesgo Endémico Neutro (R₀ = 1).")

    st.markdown("---")
    
    # 5. VISUALIZACIÓN GRÁFICA DE LAS CURVAS EPIDÉMICAS COUPLADAS
    st.write("### 📊 Curvas de Evolución Temporal de la Enfermedad")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.write("#### 🧑‍🤝‍🧑 Dinámica de la Población Humana")
        fig_h, ax_h = plt.subplots(figsize=(6, 3.5))
        fig_h.patch.set_facecolor('#0d161f')
        ax_h.set_facecolor('#121e2b')
        
        ax_h.plot(res.t, res.Sh, label="Susceptibles (S_h)", color="#2ecc71", linewidth=2)
        ax_h.plot(res.t, res.Ih, label="Infectados (I_h)", color="#e74c3c", linewidth=2.5)
        
        ax_h.set_xlabel("Tiempo (Días)", color="white")
        ax_h.set_ylabel("Número de Personas", color="white")
        ax_h.tick_params(colors="white")
        ax_h.grid(True, linestyle="--", alpha=0.3)
        ax_h.legend(facecolor='#121e2b', labelcolor='white')
        st.pyplot(fig_h)
        
    with col_g2:
        st.write("#### 🦟 Dinámica del Vector (Mosquito Anopheles)")
        fig_m, ax_m = plt.subplots(figsize=(6, 3.5))
        fig_m.patch.set_facecolor('#0d161f')
        ax_m.set_facecolor('#121e2b')
        
        ax_m.plot(res.t, res.Sm, label="Mosquitos Sanos (S_m)", color="#3498db", linewidth=2)
        ax_m.plot(res.t, res.Im, label="Mosquitos Infectados (I_m)", color="#f1c40f", linewidth=2.5)
        
        ax_m.set_xlabel("Tiempo (Días)", color="white")
        ax_m.set_ylabel("Número de Vectores", color="white")
        ax_m.tick_params(colors="white")
        ax_m.grid(True, linestyle="--", alpha=0.3)
        ax_m.legend(facecolor='#121e2b', labelcolor='white')
        st.pyplot(fig_m)

    st.markdown("---")
    
    # 6. REPORTE DE DATOS Y EXPORTACIÓN
    st.write("### 📋 Matriz de Datos Predictivos para el Hospital Local")
    st.dataframe(res.df_trends.style.format({
        "Día": "{:.1f}",
        "Humanos Susceptibles (Sh)": "{:.0f}",
        "Humanos Infectados (Ih)": "{:.1f}",
        "Mosquitos Susceptibles (Sm)": "{:.0f}",
        "Mosquitos Infectados (Im)": "{:.1f}"
    }))
    
    # Botón para descargar el reporte médico en formato CSV
    csv_buffer = io.StringIO()
    res.df_trends.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    st.download_button(
        label="📥 Descargar Reporte Epidemiológico (CSV)",
        data=csv_bytes,
        file_name=f"reporte_predictivo_malaria_{region.split()[0]}.csv",
        mime="text/csv"
    )
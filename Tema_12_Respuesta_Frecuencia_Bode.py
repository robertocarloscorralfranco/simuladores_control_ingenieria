import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Tema 12: Respuesta a la Frecuencia (Bode)", layout="wide")

st.title("📡 Tema 12: Respuesta a la Frecuencia (Bode)")
st.markdown("---")

# Menú lateral
opcion = st.sidebar.radio(
    "Selecciona la herramienta:",
    ["12.1 Gráficas Logarítmicas", "12.3 Márgenes de Fase y Ganancia"]
)

# Parámetros del sistema en la barra lateral
st.sidebar.subheader("Definición del Sistema G(s)")
k = st.sidebar.slider("Ganancia (K)", 0.1, 100.0, 10.0)
tau1 = st.sidebar.slider("Constante de tiempo 1 (tau1)", 0.1, 5.0, 1.0)
tau2 = st.sidebar.slider("Constante de tiempo 2 (tau2)", 0.0, 5.0, 0.5)

# Construcción de la Función de Transferencia G(s) = K / [(tau1*s + 1)(tau2*s + 1)]
s = ctrl.TransferFunction.s
if tau2 > 0:
    G = k / ((tau1 * s + 1) * (tau2 * s + 1))
else:
    G = k / (tau1 * s + 1)

# ------------------------------------------------------------------
# 12.1 GRÁFICAS LOGARÍTMICAS (MAGNITUD Y FASE)
# ------------------------------------------------------------------
if opcion == "12.1 Gráficas Logarítmicas":
    st.header("📊 12.1 Diagramas de Magnitud y Fase")
    st.write("Visualiza la respuesta del sistema en el dominio de la frecuencia logarítmica.")
    
    st.latex(r"|G(j\omega)|_{dB} = 20 \log_{10} |G(j\omega)|")
    st.latex(r"\phi(\omega) = \angle G(j\omega)")

    # Cálculo de Bode
    mag, phase, omega = ctrl.bode(G, plot=False)
    
    fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Magnitud
    ax_mag.semilogx(omega, 20 * np.log10(mag), color='blue', lw=2)
    ax_mag.set_ylabel("Magnitud (dB)")
    ax_mag.set_title("Diagrama de Bode")
    ax_mag.grid(True, which="both", linestyle='--', alpha=0.5)
    
    # Fase
    ax_phase.semilogx(omega, np.rad2deg(phase), color='red', lw=2)
    ax_phase.set_ylabel("Fase (grados)")
    ax_phase.set_xlabel("Frecuencia (rad/s)")
    ax_phase.grid(True, which="both", linestyle='--', alpha=0.5)
    
    st.pyplot(fig)
    st.info("Nota cómo la magnitud cae 20 dB/década por cada polo después de su frecuencia de corte.")

# ------------------------------------------------------------------
# 12.3 MÁRGENES DE ESTABILIDAD
# ------------------------------------------------------------------
else:
    st.header("🛡️ 12.3 Márgenes de Ganancia y Fase")
    st.write("Determina qué tan robusto es el sistema antes de volverse inestable.")

    # Obtener márgenes
    gm, pm, wg, wp = ctrl.margin(G)
    gm_db = 20 * np.log10(gm)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Indicadores de Estabilidad")
        st.metric("Margen de Ganancia (GM)", f"{gm_db:.2f} dB")
        st.metric("Margen de Fase (PM)", f"{pm:.2f}°")
        
        if gm_db > 0 and pm > 0:
            st.success("✅ El sistema es estable en lazo cerrado.")
        else:
            st.error("❌ El sistema es inestable o marginalmente estable.")
            
        st.write(f"**Frecuencia de cruce de ganancia (wp):** {wp:.2f} rad/s")
        st.write(f"**Frecuencia de cruce de fase (wg):** {wg:.2f} rad/s")

    with col2:
        # Gráfica de Bode con márgenes resaltados
        fig_m, ax_m = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        ctrl.bode_plot(G, margins=True, ax=ax_m)
        st.pyplot(fig_m)
        
    st.markdown("""
    > **Interpretación Crítica:** > El **Margen de Fase** indica cuánto retraso adicional puede tolerar el sistema antes de oscilar indefinidamente. Para un diseño robusto en la industria mecatrónica, se suele buscar un PM entre 45° y 60°.
    """)
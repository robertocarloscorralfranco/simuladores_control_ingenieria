import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# 1. Configuración de página
st.set_page_config(page_title="Tema 13: Nyquist y Gráficas Polares", layout="wide")

st.title("🌀 Tema 13: Gráficas Polares y Estabilidad de Nyquist")
st.markdown("---")

# Parámetros del sistema en la barra lateral
st.sidebar.header("Definición de G(s)H(s)")
k = st.sidebar.slider("Ganancia (K)", 0.1, 50.0, 2.0)
p1 = st.sidebar.slider("Polo 1 (s = -p1)", 0.1, 10.0, 1.0)
p2 = st.sidebar.slider("Polo 2 (s = -p2)", 0.1, 10.0, 2.0)
p3 = st.sidebar.slider("Polo 3 (s = -p3)", 0.0, 10.0, 0.0) # 0 para sistema tipo 1

# Construcción de la función de transferencia
s = ctrl.TransferFunction.s
G = k / ((s + p1) * (s + p2))
if p3 != 0:
    G = G / (s + p3)
else:
    G = G / s  # Agrega un integrador (Tipo 1)

opcion = st.sidebar.radio("Selecciona el análisis:", ["13.1 Representación Polar", "13.2 y 13.3 Criterio de Nyquist"])

# ------------------------------------------------------------------
# 13.1 REPRESENTACIÓN POLAR
# ------------------------------------------------------------------
if opcion == "13.1 Representación Polar":
    st.header("📍 13.1 Diagrama Polar (Locus de Frecuencia)")
    st.write("Representación de la magnitud y fase de $G(j\omega)$ en coordenadas polares.")

    mag, phase, omega = ctrl.freqresp(G, np.logspace(-1, 2, 500))
    real = mag * np.cos(phase)
    imag = mag * np.sin(phase)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(real, imag, color='purple', lw=2, label='G(jω)')
    ax.axhline(0, color='black', lw=1)
    ax.axvline(0, color='black', lw=1)
    ax.set_title("Gráfica Polar")
    ax.set_xlabel("Real")
    ax.set_ylabel("Imaginario")
    ax.grid(True, linestyle='--')
    ax.legend()
    st.pyplot(fig)

# ------------------------------------------------------------------
# 13.2 y 13.3 CRITERIO DE NYQUIST
# ------------------------------------------------------------------
else:
    st.header("🛡️ 13.3 Criterio de Estabilidad de Nyquist")
    st.write("Análisis de estabilidad basado en los rodeos al punto crítico $(-1, j0)$.")
    
    

    st.latex(r"Z = N + P")
    st.info("""
    **Donde:**
    - **P:** Polos de $G(s)H(s)$ en el semiplano derecho (RHP).
    - **N:** Número de rodeos en sentido horario al punto $(-1, j0)$.
    - **Z:** Polos del sistema en lazo cerrado en el RHP. (Para estabilidad, **Z debe ser 0**).
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_nyq, ax_nyq = plt.subplots(figsize=(8, 8))
        # Dibujar Nyquist usando la librería control
        ctrl.nyquist_plot(G, ax=ax_nyq)
        # Resaltar el punto crítico
        ax_nyq.plot(-1, 0, 'ro', label='Punto Crítico (-1, 0)')
        ax_nyq.set_title("Diagrama de Nyquist")
        ax_nyq.legend()
        st.pyplot(fig_nyq)

    with col2:
        st.subheader("Veredicto de Estabilidad")
        poles_rhp = [p for p in ctrl.poles(G) if p.real > 0]
        P = len(poles_rhp)
        
        st.write(f"**Polos en RHP (P):** {P}")
        
        # Obtener márgenes para determinar estabilidad rápidamente
        gm, pm, wg, wp = ctrl.margin(G)
        
        if (gm > 1 or np.isinf(gm)) and pm > 0:
            st.success("✅ El sistema es ESTABLE en lazo cerrado.")
            st.write("No hay rodeos al punto crítico en sentido horario ($N=0$) y $P=0$, por lo tanto $Z=0$.")
        else:
            st.error("❌ El sistema es INESTABLE.")
            st.write("El diagrama rodea o toca el punto crítico $(-1, 0)$.")

    st.markdown("---")
    st.subheader("Estabilidad Relativa")
    st.write(f"**Margen de Fase:** {pm:.2f}°")
    st.write(f"**Margen de Ganancia:** {20*np.log10(gm):.2f} dB")
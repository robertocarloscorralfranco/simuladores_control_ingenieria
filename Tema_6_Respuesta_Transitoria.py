import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Tema 6: Respuesta Transitoria", layout="wide")

st.title("⏱️ Tema 6: Análisis de Respuesta Transitoria")
st.markdown("---")

# Menú lateral para tipo de sistema
tipo_sys = st.sidebar.selectbox(
    "Selecciona el Orden del Sistema:",
    ["Primer Orden", "Segundo Orden", "Orden Superior (Comparativa)"]
)

# ------------------------------------------------------------------
# 6.1 SISTEMAS DE PRIMER ORDEN
# ------------------------------------------------------------------
if tipo_sys == "Primer Orden":
    st.header("📈 6.1 Sistemas de Primer Orden")
    st.latex(r"G(s) = \frac{K}{\tau s + 1}")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        k = st.slider("Ganancia (K)", 0.1, 10.0, 1.0)
        tau = st.slider("Constante de tiempo (τ)", 0.1, 5.0, 1.0)
        st.info(f"El sistema alcanza el 63.2% de su valor final en t = {tau}s")

    with col2:
        sys = ctrl.TransferFunction([k], [tau, 1])
        t, y = ctrl.step_response(sys)
        
        fig, ax = plt.subplots()
        ax.plot(t, y, color='blue', lw=2)
        ax.axhline(k, color='red', linestyle='--', label=f'Estado Estable (K={k})')
        ax.axvline(tau, color='green', linestyle=':', label='1 Tau')
        ax.set_title("Respuesta al Escalón - 1er Orden")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

# ------------------------------------------------------------------
# 6.2 SISTEMAS DE SEGUNDO ORDEN
# ------------------------------------------------------------------
elif tipo_sys == "Segundo Orden":
    st.header("📉 6.2 Sistemas de Segundo Orden")
    st.latex(r"G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}")

    c1, c2 = st.columns([1, 2])
    with c1:
        wn = st.slider("Frecuencia Natural (ωn)", 0.5, 10.0, 2.0)
        zeta = st.slider("Factor de Amortiguamiento (ζ)", 0.0, 2.0, 0.5)
        
        # Clasificación
        if zeta == 0: st.error("Sistema Oscilatorio (Críticamente Inestable)")
        elif zeta < 1: st.warning("Sistema Subamortiguado")
        elif zeta == 1: st.success("Sistema Críticamente Amortiguado")
        else: st.info("Sistema Sobreamortiguado")

    with c2:
        num = [wn**2]
        den = [1, 2*zeta*wn, wn**2]
        sys = ctrl.TransferFunction(num, den)
        t, y = ctrl.step_response(sys)
        
        # Métricas de desempeño
        info = ctrl.step_info(sys)
        
        fig, ax = plt.subplots()
        ax.plot(t, y, color='purple', lw=2)
        ax.set_title(f"Respuesta con ζ = {zeta}")
        ax.grid(True)
        st.pyplot(fig)
        
        # Tabla de métricas (Nivel Maestría)
        data = {
            "Métrica": ["Sobretiro (Overshoot %)", "Tiempo de Asentamiento (2%)", "Tiempo de Pico"],
            "Valor": [f"{info['PercentageOverShoot']:.2f}%", f"{info['SettlingTime']:.2f} s", f"{info['PeakTime']:.2f} s"]
        }
        st.table(pd.DataFrame(data))

# ------------------------------------------------------------------
# 6.3 SISTEMAS DE ORDEN SUPERIOR
# ------------------------------------------------------------------
else:
    st.header("🌊 6.3 Sistemas de Orden Superior")
    st.write("Observa cómo un polo adicional (orden 3) afecta la respuesta transitoria.")
    
    p3 = st.slider("Ubicación del tercer polo (s = -p)", 0.1, 20.0, 10.0)
    
    # Sistema base 2do orden + 1 polo extra
    # G(s) = 4 / [(s^2 + 2s + 4) * (s/p3 + 1)]
    num = [4 * p3]
    den = np.polymul([1, 2, 4], [1, p3])
    sys_high = ctrl.TransferFunction(num, den)
    
    t, y = ctrl.step_response(sys_high)
    fig, ax = plt.subplots()
    ax.plot(t, y, color='orange', label=f'Polo extra en -{p3}')
    ax.set_title("Efecto de Polos Dominantes")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    st.info("A medida que el tercer polo se aleja del origen, el sistema se comporta más como uno de 2do orden (Polo Dominante).")
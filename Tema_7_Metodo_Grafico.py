import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
import sympy as sp

# 1. Configuración de página
st.set_page_config(page_title="Tema 7: Modelación por Método Gráfico", layout="wide")

st.title("📉 Tema 7: Modelación por Método Gráfico (FOPDT)")
st.markdown("---")

st.sidebar.header("Parámetros del Modelo Identificado")
k_id = st.sidebar.slider("Ganancia Identificada (K)", 0.5, 5.0, 1.0)
tau_id = st.sidebar.slider("Constante de Tiempo (tau)", 0.5, 10.0, 2.0)
l_id = st.sidebar.slider("Tiempo Muerto (L)", 0.0, 5.0, 1.0)

# 2. Selección de Caso de Estudio
opcion = st.radio(
    "Selecciona la actividad:",
    ["7.1 Identificación con Tiempo Muerto (FOPDT)", "7.2 Modelos Sobreamortiguados"]
)

# ------------------------------------------------------------------
# 7.1 IDENTIFICACIÓN CON TIEMPO MUERTO
# ------------------------------------------------------------------
if opcion == "7.1 Identificación con Tiempo Muerto (FOPDT)":
    st.header("🎯 7.1 Curva de Reacción y Parámetros FOPDT")
    st.write("Ajusta los sliders para que el modelo (línea roja) coincida con los puntos experimentales (azul).")

    # Generar "Datos Experimentales" (Planta Real Desconocida)
    # Planta real: G(s) = 2e^(-1.5s) / (3s + 1)
    t_exp = np.linspace(0, 20, 100)
    # Simulación manual de tiempo muerto para los datos "reales"
    y_real_clean = 2 * (1 - np.exp(-(t_exp - 1.5) / 3))
    y_real = np.where(t_exp < 1.5, 0, y_real_clean)

    # Simulación del Modelo Identificado (Usando Aproximación de Padé para el delay)
    num, den = ctrl.pade(l_id, n=2) # Aproximación de Padé de orden 2 para el tiempo muerto
    delay_sys = ctrl.TransferFunction(num, den)
    plant_sys = ctrl.TransferFunction([k_id], [tau_id, 1])
    sys_model = ctrl.series(delay_sys, plant_sys)
    
    t_mod, y_mod = ctrl.step_response(sys_model, t_exp)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(t_exp, y_real, 'bo', alpha=0.3, label="Datos Experimentales (Planta)")
        ax.plot(t_mod, y_mod, 'r-', lw=3, label="Modelo Identificado (FOPDT)")
        ax.axhline(k_id, color='green', linestyle='--', label=f"Estado Estable (K={k_id})")
        ax.set_title("Ajuste de Modelo por Método Gráfico")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

    with col2:
        st.subheader("Solución Matemática")
        st.write("El modelo identificado es:")
        st.latex(r"G(s) = \frac{K e^{-Ls}}{\tau s + 1}")
        st.write(f"Valores actuales:")
        st.latex(f"G(s) = \\frac{{{k_id} e^{{-{l_id}s}}}}{{{tau_id}s + 1}}")
        
        # Guía de identificación
        st.info(f"""
        **Criterio de Identificación:**
        1. **K:** Valor final de la respuesta.
        2. **L:** Tiempo donde la señal empieza a subir.
        3. **tau:** Tiempo transcurrido desde L hasta alcanzar el 63.2% de K.
        """)

# ------------------------------------------------------------------
# 7.2 MODELOS SOBREAMORTIGUADOS
# ------------------------------------------------------------------
else:
    st.header("🌊 7.2 Modelos Sobreamortiguados y Críticos")
    st.write("Identificación de sistemas de segundo orden sin oscilación.")
    
    st.latex(r"G(s) = \frac{K}{(\tau_1 s + 1)(\tau_2 s + 1)}")
    
    t2_1 = st.slider("Constante tau 1", 0.5, 5.0, 1.0)
    t2_2 = st.slider("Constante tau 2", 0.5, 5.0, 2.0)
    
    sys_over = ctrl.TransferFunction([1], np.polymul([t2_1, 1], [t2_2, 1]))
    t_over, y_over = ctrl.step_response(sys_over)
    
    fig2, ax2 = plt.subplots()
    ax2.plot(t_over, y_over, color='orange', lw=2)
    ax2.set_title("Respuesta Sobreamortiguada (Sin Oscilación)")
    ax2.grid(True)
    st.pyplot(fig2)
    
    st.write("Este tipo de curvas suelen identificarse erróneamente como de primer orden si no se analiza cuidadosamente la 'S' inicial en el origen.")
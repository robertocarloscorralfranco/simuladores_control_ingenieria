import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Tema 10: Sintonía de Controladores PID", layout="wide")

st.title("🎯 Tema 10: Sintonía de Controladores PID")
st.markdown("---")

# Menú lateral
metodo = st.sidebar.radio(
    "Selecciona el Método de Sintonía:",
    ["10.2 Ziegler-Nichols I (Lazo Abierto)", "10.3 Ziegler-Nichols II (Ganancia Última)"]
)

# ------------------------------------------------------------------
# 10.2 ZIEGLER-NICHOLS I (MÉTODO DE LA CURVA DE REACCIÓN)
# ------------------------------------------------------------------
if metodo == "10.2 Ziegler-Nichols I (Lazo Abierto)":
    st.header("📈 10.2 Método de Ziegler-Nichols basado en FOPDT")
    st.write("Utiliza los parámetros obtenidos en el Tema 7 (K, L, τ) para calcular las ganancias del controlador.")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parámetros Identificados")
        K = st.number_input("Ganancia de la Planta (K)", value=1.0)
        L = st.number_input("Tiempo Muerto (L)", value=0.5)
        tau = st.number_input("Constante de Tiempo (τ)", value=2.0)
        
        tipo_ctrl = st.selectbox("Tipo de Control:", ["P", "PI", "PID"])

    # Lógica de sintonía Z-N I
    if tipo_ctrl == "P":
        kp = tau / (K * L); ti = np.inf; td = 0
    elif tipo_ctrl == "PI":
        kp = 0.9 * tau / (K * L); ti = L / 0.3; td = 0
    else: # PID
        kp = 1.2 * tau / (K * L); ti = 2 * L; td = 0.5 * L

    ki = kp / ti if ti != np.inf else 0
    kd = kp * td

    with col2:
        st.subheader("Solución Matemática (Tabla Z-N I)")
        res_data = {
            "Parámetro": ["Ganancia Proporcional (Kp)", "Tiempo Integral (Ti)", "Tiempo Derivativo (Td)"],
            "Valor Calculado": [round(kp, 4), round(ti, 4), round(td, 4)]
        }
        st.table(pd.DataFrame(res_data))

        # Simulación del lazo cerrado
        s = ctrl.TransferFunction.s
        # Planta con aproximación de Padé para el tiempo muerto
        num_p, den_p = ctrl.pade(L, n=2)
        Pade = ctrl.TransferFunction(num_p, den_p)
        G = (K / (tau * s + 1)) * Pade
        
        C = kp + ki/s + kd*s/(0.1*s + 1) # PID con filtro
        T = ctrl.feedback(C * G, 1)
        
        t, y = ctrl.step_response(T)
        fig, ax = plt.subplots()
        ax.plot(t, y, label=f"Respuesta {tipo_ctrl} sintonizada", lw=2)
        ax.axhline(1.0, color='red', linestyle='--')
        ax.set_title("Respuesta al Escalón (Lazo Cerrado)")
        ax.grid(True); ax.legend()
        st.pyplot(fig)

# ------------------------------------------------------------------
# 10.3 ZIEGLER-NICHOLS II (MÉTODO DE GANANCIA ÚLTIMA)
# ------------------------------------------------------------------
else:
    st.header("🌀 10.3 Método de Ganancia Última (Kcr y Pcr)")
    st.write("Basado en llevar el sistema al límite de la estabilidad en lazo cerrado.")

    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.subheader("Datos de Oscilación")
        kcr = st.number_input("Ganancia Crítica (Kcr)", value=10.0)
        pcr = st.number_input("Periodo Crítico (Pcr) [seg]", value=1.5)
        
        tipo_ctrl2 = st.selectbox("Tipo de Control (Z-N II):", ["P", "PI", "PID"])

    # Lógica de sintonía Z-N II
    if tipo_ctrl2 == "P":
        kp2 = 0.5 * kcr; ti2 = np.inf; td2 = 0
    elif tipo_ctrl2 == "PI":
        kp2 = 0.45 * kcr; ti2 = pcr / 1.2; td2 = 0
    else: # PID
        kp2 = 0.6 * kcr; ti2 = 0.5 * pcr; td2 = 0.125 * pcr

    ki2 = kp2 / ti2 if ti2 != np.inf else 0
    kd2 = kp2 * td2

    with col_b:
        st.subheader("Cálculos del Controlador")
        res_data2 = {
            "Variable": ["Kp", "Ti", "Td", "Ki", "Kd"],
            "Resultado": [round(kp2,4), round(ti2,4), round(td2,4), round(ki2,4), round(kd2,4)]
        }
        st.table(pd.DataFrame(res_data2))

        # Ejemplo visual de oscilación crítica vs sintonía
        t_osc = np.linspace(0, 10, 500)
        y_critico = np.sin(2 * np.pi / pcr * t_osc) # Representación de oscilación sostenida
        
        # Simulación de respuesta sintonizada (aproximada para visualización)
        sys_tuned = ctrl.TransferFunction([kp2], [1, 2, 1 + kp2]) # Planta genérica 2do orden
        t_t, y_t = ctrl.step_response(sys_tuned)

        fig2, ax2 = plt.subplots()
        ax2.plot(t_t, y_t, color='green', label="Respuesta Sintonizada")
        ax2.axhline(1.0, color='red', ls='--')
        ax2.set_title("Mejora de la Respuesta tras Sintonía")
        ax2.legend(); ax2.grid(True)
        st.pyplot(fig2)

        st.info(r"**Fórmula PID:** $u(t) = K_p \left( e(t) + \frac{1}{T_i} \int e(t)dt + T_d \frac{de(t)}{dt} \right)$")
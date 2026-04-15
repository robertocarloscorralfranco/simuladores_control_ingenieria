import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Tema 9: Acciones de Control Básicas", layout="wide")

st.title("🎮 Tema 9: Acciones de Control Básicas")
st.markdown("---")

# Menú lateral para las acciones
accion = st.sidebar.radio(
    "Selecciona la Acción de Control:",
    ["9.1 Control ON/OFF", "9.1 y 9.3 Acciones P, I, D (Lazo Cerrado)", "9.2 Implementación Electrónica"]
)

# ------------------------------------------------------------------
# 9.1 CONTROL ON/OFF
# ------------------------------------------------------------------
if accion == "9.1 Control ON/OFF":
    st.header("🎚️ 9.1 Control Todo o Nada (ON/OFF)")
    st.write("El control más simple, común en termostatos. Presenta una oscilación característica alrededor del Setpoint.")

    histeresis = st.slider("Histéresis (Banda Muerta)", 0.0, 5.0, 1.0)
    
    # Simulación simple de ON/OFF
    t = np.linspace(0, 20, 500)
    setpoint = 50.0
    y = np.zeros_like(t)
    u = np.zeros_like(t)
    current_y = 0.0
    state = False # OFF

    for i in range(1, len(t)):
        error = setpoint - current_y
        if error > histeresis:
            state = True # ON
        elif error < -histeresis:
            state = False # OFF
        
        u[i] = 100 if state else 0
        # Dinámica simplificada de la planta (1er orden)
        current_y += (u[i] * 0.1 - current_y * 0.05) * (t[i] - t[i-1])
        y[i] = current_y

    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax[0].plot(t, y, label="Variable de Proceso (PV)", color='blue')
    ax[0].axhline(setpoint, color='red', linestyle='--', label="Setpoint (SP)")
    ax[0].set_ylabel("Temperatura / Nivel")
    ax[0].legend()
    ax[0].grid(True)

    ax[1].step(t, u, label="Acción de Control (Válvula/Calactor)", color='green')
    ax[1].set_ylabel("Estado (%)")
    ax[1].set_xlabel("Tiempo (s)")
    ax.legend()
    ax[1].grid(True)
    st.pyplot(fig)

# ------------------------------------------------------------------
# 9.1 y 9.3 ACCIONES P, I, D
# ------------------------------------------------------------------
elif accion == "9.1 y 9.3 Acciones P, I, D (Lazo Cerrado)":
    st.header("📈 Acciones P, I, D en Lazo Cerrado")
    st.write("Analiza cómo cada término afecta el sobretiro, el tiempo de asentamiento y el error.")

    st.sidebar.subheader("Parámetros PID")
    kp = st.sidebar.slider("Ganancia Proporcional (Kp)", 0.0, 20.0, 1.0)
    ki = st.sidebar.slider("Ganancia Integral (Ki)", 0.0, 10.0, 0.0)
    kd = st.sidebar.slider("Ganancia Derivativa (Kd)", 0.0, 5.0, 0.0)

    # Definición de la Planta (2do orden típica)
    # G(s) = 1 / (s^2 + 2s + 1)
    num_p = [1]
    den_p = [1, 2, 1]
    G = ctrl.TransferFunction(num_p, den_p)

    # Definición del Controlador C(s) = Kp + Ki/s + Kd*s
    # Para evitar problemas con la derivada pura, se usa un filtro o se construye por partes
    s = ctrl.TransferFunction.s
    C = kp + ki/s + kd*s/(0.1*s + 1) # Filtro de derivada para estabilidad numérica

    # Sistema en Lazo Cerrado T(s) = CG / (1 + CG)
    L = ctrl.series(C, G)
    T = ctrl.feedback(L, 1)

    t, y = ctrl.step_response(T)
    
    fig2, ax2 = plt.subplots()
    ax2.plot(t, y, lw=2)
    ax2.axhline(1.0, color='red', linestyle='--', label="Referencia")
    ax2.set_title(f"Respuesta PID (Kp={kp}, Ki={ki}, Kd={kd})")
    ax2.set_xlabel("Tiempo (s)")
    ax2.grid(True)
    st.pyplot(fig2)

    st.info("""
    **Efectos observados:**
    - **Proporcional (P):** Reduce el error pero puede causar oscilación.
    - **Integral (I):** Elimina el error en estado estable pero aumenta el sobretiro.
    - **Derivativa (D):** Provee amortiguamiento y reduce el sobretiro (anticipación).
    """)

# ------------------------------------------------------------------
# 9.2 IMPLEMENTACIÓN ELECTRÓNICA
# ------------------------------------------------------------------
else:
    st.header("🔌 9.2 Implementación con Amplificadores Operacionales")
    st.write("Modelación de un controlador PID analógico basado en circuitos OP-AMP.")
    
    
    
    st.latex(r"V_{out}(t) = -\left[ \frac{R_f}{R_i}V_{in}(t) + \frac{1}{R_i C_f}\int V_{in}(t)dt + R_f C_i \frac{dV_{in}}{dt} \right]")
    
    st.write("""
    En la industria, antes de los PLCs y microcontroladores, estas acciones se implementaban mediante:
    - **Neumática:** Fuelles y restricciones (agujas).
    - **Electrónica:** Circuitos integrados (filtros activos).
    - **Hidráulica:** Pistones y válvulas piloto.
    """)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

st.set_page_config(page_title="Tema 14: Estrategias Avanzadas", layout="wide")
st.title("🚀 Tema 14: Estrategias Avanzadas de Control")
st.markdown("---")

opcion = st.sidebar.radio(
    "Selecciona la estrategia:",
    ["14.1 Servo vs. Regulador", "14.2 Control en Cascada y Feedforward", "14.3 Control Moderno"]
)

if opcion == "14.1 Servo vs. Regulador":
    st.header("🎯 14.1 Seguimiento vs. Rechazo de Perturbaciones")
    dist_mag = st.slider("Magnitud de la Perturbación (D)", 0.0, 5.0, 2.0)
    G = ctrl.TransferFunction([1], [1, 2, 1])
    C = 2.0 + 1.0/ctrl.TransferFunction.s
    T_servo = ctrl.feedback(C*G, 1)
    T_reg = ctrl.feedback(G, C)
    t = np.linspace(0, 20, 500)
    _, y_s = ctrl.step_response(T_servo, t)
    _, y_r = ctrl.impulse_response(T_reg * dist_mag, t)
    fig, ax = plt.subplots()
    ax.plot(t, y_s, label="Servo (Referencia)", color='blue')
    ax.plot(t, y_r, label="Regulador (Perturbación)", color='red', ls='--')
    ax.legend(); ax.grid(True)
    st.pyplot(fig)

elif opcion == "14.2 Control en Cascada y Feedforward":
    st.header("⛓️ 14.2 Estructuras Complejas")
    st.info("Nota: Estas estrategias requieren medir variables intermedias o perturbaciones antes de que afecten la salida.")
    mode = st.radio("Comparativa:", ["Lazo Simple", "Control en Cascada"])
    G_v = ctrl.TransferFunction([1], [0.5, 1]) 
    G_p = ctrl.TransferFunction([1], [2, 1])
    t = np.linspace(0, 15, 500)
    if mode == "Lazo Simple":
        C = 1.5 + 0.5/ctrl.TransferFunction.s
        T = ctrl.feedback(C * G_v * G_p, 1)
    else:
        C_i = 5.0
        L_i = ctrl.feedback(C_i * G_v, 1)
        C_o = 1.2 + 0.4/ctrl.TransferFunction.s
        T = ctrl.feedback(C_o * L_i * G_p, 1)
    _, y = ctrl.step_response(T, t)
    fig2, ax2 = plt.subplots()
    ax2.plot(t, y, color='green')
    ax2.set_title(f"Respuesta: {mode}")
    ax2.grid(True)
    st.pyplot(fig2)

else:
    st.header("🧠 14.3 Control Moderno")
    st.write("El control moderno utiliza el **Espacio de Estados** para manejar sistemas multivariables.")
    st.latex(r"\dot{x} = Ax + Bu")
    st.latex(r"y = Cx + Du")
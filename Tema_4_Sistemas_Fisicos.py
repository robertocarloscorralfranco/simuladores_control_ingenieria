import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import control as ctrl

# 1. Configuración de página
st.set_page_config(page_title="Tema 4: Modelación de Sistemas Físicos", layout="wide")

st.title("⚙️ Tema 4: Modelación de Sistemas Físicos y Analogías")
st.markdown("---")

# Menú lateral
opcion = st.sidebar.radio(
    "Selecciona el sistema físico:",
    ["4.1 Sistema Mecánico (Masa-Resorte-Amortiguador)", 
     "4.2 Sistema Eléctrico (Circuito RLC)", 
     "4.3 Analogías Fuerza-Voltaje"]
)

# ------------------------------------------------------------------
# 4.1 SISTEMA MECÁNICO
# ------------------------------------------------------------------
if opcion == "4.1 Sistema Mecánico (Masa-Resorte-Amortiguador)":
    st.header("🏗️ 4.1 Modelación de Sistemas Mecánicos")
    st.write("Analiza la respuesta de una masa sujeta a una fuerza externa con amortiguamiento.")
    
    col_m1, col_m2 = st.columns([1, 2])
    
    with col_m1:
        st.subheader("Parámetros Físicos")
        m = st.slider("Masa (m) [kg]", 0.5, 20.0, 2.0)
        b = st.slider("Amortiguamiento (b) [N·s/m]", 0.1, 10.0, 1.0)
        k = st.slider("Constante elástica (k) [N/m]", 1.0, 50.0, 10.0)
        
    with col_m2:
        st.subheader("Modelo Matemático")
        st.latex(r"m\ddot{x}(t) + b\dot{x}(t) + kx(t) = F(t)")
        st.latex(r"G(s) = \frac{X(s)}{F(s)} = \frac{1}{ms^2 + bs + k}")
        
        # Simulación
        sys_mec = ctrl.TransferFunction([1], [m, b, k])
        t_mec, y_mec = ctrl.step_response(sys_mec)
        
        fig, ax = plt.subplots()
        ax.plot(t_mec, y_mec, color='brown', lw=2)
        ax.set_title("Desplazamiento de la Masa (Respuesta al Escalón)")
        ax.set_ylabel("Posición x(t) [m]")
        ax.grid(True)
        st.pyplot(fig)

# ------------------------------------------------------------------
# 4.2 SISTEMA ELÉCTRICO
# ------------------------------------------------------------------
elif opcion == "4.2 Sistema Eléctrico (Circuito RLC)":
    st.header("⚡ 4.2 Modelación de Sistemas Eléctricos")
    st.write("Estudio de la carga en un circuito RLC en serie.")

    col_e1, col_e2 = st.columns([1, 2])
    
    with col_e1:
        st.subheader("Componentes")
        L = st.slider("Inductancia (L) [H]", 0.1, 5.0, 1.0)
        R = st.slider("Resistencia (R) [Ω]", 0.1, 20.0, 2.0)
        C = st.slider("Capacitancia (C) [F]", 0.01, 1.0, 0.5)
        
    with col_e2:
        st.subheader("Ecuación de Mallas")
        st.latex(r"L\frac{di}{dt} + Ri + \frac{1}{C}\int i dt = V(t)")
        st.write("En términos de carga $q(t)$:")
        st.latex(r"L\ddot{q} + R\dot{q} + \frac{1}{C}q = V(t)")
        
        # Función de transferencia q(s)/V(s)
        sys_elec = ctrl.TransferFunction([1], [L, R, 1/C])
        t_elec, y_elec = ctrl.step_response(sys_elec)
        
        fig2, ax2 = plt.subplots()
        ax2.plot(t_elec, y_elec, color='blue', lw=2)
        ax2.set_title("Carga en el Capacitor (Respuesta al Escalón)")
        ax2.set_ylabel("Carga q(t) [C]")
        ax2.grid(True)
        st.pyplot(fig2)

# ------------------------------------------------------------------
# 4.3 ANALOGÍAS FUERZA-VOLTAJE
# ------------------------------------------------------------------
else:
    st.header("🔄 4.3 Dashboard de Analogías Físicas")
    st.write("Demostración de que sistemas de diferente naturaleza pueden ser idénticos matemáticamente.")

    st.table({
        "Variable Mecánica": ["Fuerza (F)", "Masa (m)", "Amortiguamiento (b)", "Resorte (k)", "Posición (x)"],
        "Análogo Eléctrico": ["Voltaje (V)", "Inductancia (L)", "Resistencia (R)", "Elastancia (1/C)", "Carga (q)"]
    })

    st.info("Ajusta los parámetros para que coincidan (ej. m=L, b=R, k=1/C) y verás que las gráficas se superponen.")

    val_1 = st.slider("Masa (m) / Inductancia (L)", 0.5, 10.0, 2.0)
    val_2 = st.slider("Amortiguamiento (b) / Resistencia (R)", 0.1, 10.0, 1.0)
    val_3 = st.slider("Rigidez (k) / Inversa de Capacitancia (1/C)", 1.0, 20.0, 5.0)

    # Ambos sistemas comparten el mismo denominador: [val_1, val_2, val_3]
    sys_analog = ctrl.TransferFunction([1], [val_1, val_2, val_3])
    t_a, y_a = ctrl.step_response(sys_analog)

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(t_a, y_a, color='green', lw=3, label="Respuesta unificada")
    ax3.set_title("Respuesta Temporal Compartida")
    ax3.legend()
    ax3.grid(True)
    st.pyplot(fig3)
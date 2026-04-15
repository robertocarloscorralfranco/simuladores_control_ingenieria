import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import control as ctrl

# 1. Configuración de página
st.set_page_config(page_title="Tema 3: Modelación de Sistemas Dinámicos", layout="wide")

st.title("🧩 Tema 3: Modelación de Sistemas Dinámicos")
st.markdown("---")

# Menú lateral
opcion = st.sidebar.radio(
    "Selecciona la herramienta:",
    ["3.1 De Ecuaciones Diferenciales a FT", 
     "3.2 Simplificación de Diagramas de Bloques", 
     "3.3 Regla de Mason (Calculadora de Ganancia)"]
)

# ------------------------------------------------------------------
# 3.1 DE ECUACIONES DIFERENCIALES A FT
# ------------------------------------------------------------------
if opcion == "3.1 De Ecuaciones Diferenciales a FT":
    st.header("📝 3.1 Obtención de la Función de Transferencia")
    st.write("Aplica la Transformada de Laplace a una ecuación diferencial lineal (LTI).")
    
    st.latex(r"a_2 \ddot{y}(t) + a_1 \dot{y}(t) + a_0 y(t) = b_1 \dot{x}(t) + b_0 x(t)")
    
    col_coeffs = st.columns(2)
    with col_coeffs[0]:
        a2 = st.number_input("Coeficiente d²y/dt² (a2):", value=1.0)
        a1 = st.number_input("Coeficiente dy/dt (a1):", value=2.0)
        a0 = st.number_input("Coeficiente y (a0):", value=1.0)
    with col_coeffs[1]:
        b1 = st.number_input("Coeficiente dx/dt (b1):", value=0.0)
        b0 = st.number_input("Coeficiente x (b0):", value=1.0)

    s = sp.Symbol('s')
    num_sym = b1*s + b0
    den_sym = a2*s**2 + a1*s + a0
    G_s = num_sym / den_sym

    st.subheader("Resultado Algebraico")
    st.write("Asumiendo condiciones iniciales nulas:")
    st.latex(f"G(s) = \\frac{{Y(s)}}{{X(s)}} = {sp.latex(sp.simplify(G_s))}")

# ------------------------------------------------------------------
# 3.2 SIMPLIFICACIÓN DE DIAGRAMAS DE BLOQUES
# ------------------------------------------------------------------
elif opcion == "3.2 Simplificación de Diagramas de Bloques":
    st.header("📉 3.2 Álgebra de Bloques Interactiva")
    st.write("Calcula la reducción de un sistema con bloques en serie y retroalimentación.")

    st.sidebar.subheader("Parámetros de Bloques")
    G1 = st.sidebar.slider("Ganancia G1 (Planta)", 1.0, 10.0, 5.0)
    G2 = st.sidebar.slider("Ganancia G2 (Actuador)", 1.0, 10.0, 2.0)
    H1 = st.sidebar.slider("Retroalimentación H1 (Sensor)", 0.1, 2.0, 1.0)

    # Lógica: (G1 * G2) / (1 + G1*G2*H1)
    g_p = G1 * G2
    t_s = g_p / (1 + g_p * H1)
    
    st.subheader("Reducción Paso a Paso")
    st.write("**Paso 1:** Combinar bloques en serie $G_p(s) = G_1 \cdot G_2$")
    st.latex(f"G_p = {G1} \cdot {G2} = {g_p}")
    
    st.write("**Paso 2:** Aplicar fórmula de lazo cerrado $T(s) = \\frac{G_p}{1 + G_p H_1}$")
    st.latex(f"T(s) = \\frac{{{g_p}}}{{1 + ({g_p})({H1})}}")
    
    st.success(f"**Ganancia Total del Sistema:** {t_s:.4f}")

# ------------------------------------------------------------------
# 3.3 REGLA DE MASON
# ------------------------------------------------------------------
else:
    st.header("🕸️ 3.3 Calculadora de Regla de Mason")
    st.write("Calcula la ganancia de un gráfico de flujo de señal (SFG).")
    
    st.latex(r"T = \frac{\sum P_k \Delta_k}{\Delta}")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        p1 = st.number_input("Trayectoria Directa P1:", value=10.0)
        l1 = st.number_input("Lazo 1 (L1):", value=-2.0)
        l2 = st.number_input("Lazo 2 (L2):", value=-0.5)
    
    # Determinante delta = 1 - (L1 + L2)
    delta = 1 - (l1 + l2)
    transfer = p1 / delta

    with col_m2:
        st.subheader("Cálculo del Determinante")
        st.write("Para lazos que se tocan en el nodo:")
        st.latex(f"\Delta = 1 - (L_1 + L_2) = 1 - ({l1} + {l2}) = {delta}")
        
        st.info("Resultado de Transferencia:")
        st.latex(f"T = \\frac{{{p1}}}{{{delta}}} = {transfer:.4f}")

    # Simulación de respuesta al escalón para el sistema equivalente
    # Se crea un sistema de primer orden con la ganancia calculada para visualizar estabilidad
    sys = ctrl.TransferFunction([transfer], [1, 1])
    t, y = ctrl.step_response(sys)
    fig, ax = plt.subplots()
    ax.plot(t, y, color='orange', lw=2)
    ax.set_title("Dinámica del Sistema Equivalente (Escalón)")
    ax.set_xlabel("Tiempo (s)")
    ax.grid(True, linestyle='--')
    st.pyplot(fig)
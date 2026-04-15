import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import control as ctrl

# 1. Configuración básica
st.set_page_config(page_title="Tema 1: Conceptos Básicos", layout="wide")

st.title("🚀 Tema 1: Conceptos Básicos de Ingeniería de Control")
st.markdown("---")

# 2. Menú de navegación
subtema = st.sidebar.selectbox(
    "Selecciona el ejercicio:",
    ["1.1 Calculadora de Laplace", 
     "1.2 Simplificación de Bloques", 
     "1.3 Comparativa de Sistemas"]
)

# ------------------------------------------------------------------
# 1.1 TRANSFORMADA DE LAPLACE
# ------------------------------------------------------------------
if subtema == "1.1 Calculadora de Laplace":
    st.header("1.1 Calculadora de Laplace (Paso a Paso)")
    
    t, s = sp.symbols('t s', positive=True)
    formula_text = st.text_input("Ingresa f(t) (ej: exp(-t), t**2):", "t*exp(-2*t)")
    
    try:
        f_t = sp.sympify(formula_text)
        F_s = sp.laplace_transform(f_t, t, s, noconds=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Solución Matemática")
            st.latex(r"F(s) = \mathcal{L} \{ " + sp.latex(f_t) + r" \}")
            st.info("Resultado:")
            st.latex(sp.latex(sp.simplify(F_s)))
            
        with col2:
            st.subheader("Gráfica Temporal")
            f_func = sp.lambdify(t, f_t, "numpy")
            t_vals = np.linspace(0, 10, 200)
            y_vals = f_func(t_vals)
            
            fig1, ax1 = plt.subplots()
            ax1.plot(t_vals, y_vals, color='green')
            ax1.set_xlabel('Tiempo (t)')
            ax1.grid(True)
            st.pyplot(fig1)
    except Exception as e:
        st.error(f"Error en la fórmula: {e}")

# ------------------------------------------------------------------
# 1.2 DIAGRAMA DE BLOQUES
# ------------------------------------------------------------------
elif subtema == "1.2 Simplificación de Bloques":
    st.header("1.2 Simplificación de Lazo Cerrado")
    
    k = st.sidebar.slider("Ganancia Planta (G)", 0.1, 10.0, 1.0)
    tau = st.sidebar.slider("Constante de tiempo (tau)", 0.1, 5.0, 1.0)
    h = st.sidebar.slider("Retroalimentación (H)", 0.1, 2.0, 1.0)
    
    # Cálculo simbólico
    s_sym = sp.Symbol('s')
    G = k / (tau * s_sym + 1)
    T = sp.simplify(G / (1 + G * h))
    
    st.write("Función de Transferencia del Sistema:")
    st.latex(r"T(s) = " + sp.latex(T))
    
    # Respuesta al escalón
    sys = ctrl.TransferFunction([k], [tau, 1 + k*h])
    t_st, y_st = ctrl.step_response(sys)
    
    fig2, ax2 = plt.subplots()
    ax2.plot(t_st, y_st)
    ax2.set_title("Respuesta al Escalón")
    ax2.grid(True)
    st.pyplot(fig2)

# ------------------------------------------------------------------
# 1.3 COMPARATIVA DE SISTEMAS
# ------------------------------------------------------------------
else:
    st.header("1.3 Comparativa de Sistemas")
    amp = st.slider("Amplitud de entrada", 1, 10, 5)
    t_vec = np.linspace(0, 10, 100)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Sistemas Lineales")
        y_l = amp * t_vec
        fig3, ax3 = plt.subplots()
        ax3.plot(t_vec, y_l, color='blue')
        st.pyplot(fig3)
        
    with c2:
        st.subheader("No Lineales (Saturación)")
        y_nl = np.tanh(t_vec * (amp/5))
        fig4, ax4 = plt.subplots()
        ax4.plot(t_vec, y_nl, color='red')
        st.pyplot(fig4)
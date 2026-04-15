import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# 1. Configuración de página
st.set_page_config(page_title="Tema 5: Métodos de linealización", layout="wide")

st.title("📉 Tema 5: Métodos de Linealización")
st.markdown("---")

# Menú lateral
opcion = st.sidebar.radio(
    "Selecciona el caso de estudio:",
    ["5.1 Linealización por Serie de Taylor (Teoría)", 
     "5.2 Sistema de Flujo (Válvula No Lineal)", 
     "5.3 Péndulo Simple (No Linealidad Trigonometrica)"]
)

# ------------------------------------------------------------------
# 5.1 TEORÍA DE SERIE DE TAYLOR
# ------------------------------------------------------------------
if opcion == "5.1 Linealización por Serie de Taylor (Teoría)":
    st.header("📖 5.1 Aproximación por Serie de Taylor")
    st.write("La linealización consiste en aproximar una curva por su recta tangente en un punto de operación ($x_0$).")
    
    st.latex(r"f(x) \approx f(x_0) + \frac{df}{dx}\Big|_{x=x_0}(x - x_0)")
    
    st.info("""
    Para que esta aproximación sea válida, la variación $\Delta x = (x - x_0)$ debe ser pequeña. 
    A medida que nos alejamos de $x_0$, el error de linealización aumenta.
    """)

# ------------------------------------------------------------------
# 5.2 SISTEMA DE FLUJO (RAÍZ CUADRADA)
# ------------------------------------------------------------------
elif opcion == "5.2 Sistema de Flujo (Válvula No Lineal)":
    st.header("🚰 5.2 Linealización de una Válvula de Control")
    st.write("El flujo $Q$ a través de un orificio es proporcional a la raíz cuadrada del nivel $h$: $Q = K\sqrt{h}$")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parámetros")
        k_val = st.slider("Constante de la Válvula (K)", 1.0, 10.0, 5.0)
        h0 = st.slider("Punto de Operación (h0)", 0.5, 20.0, 4.0)
        rango = st.slider("Rango de visualización (h)", 0.1, 30.0, (0.1, 25.0))

    with col2:
        # Cálculo simbólico
        h = sp.Symbol('h')
        f_h = k_val * sp.sqrt(h)
        df_dh = sp.diff(f_h, h)
        
        # Evaluar en h0
        f_h0 = float(f_h.subs(h, h0))
        m = float(df_dh.subs(h, h0)) # Pendiente
        
        st.subheader("Solución Matemática")
        st.write(f"Función: $f(h) = {k_val}\sqrt{{h}}$")
        st.write(f"Derivada evaluada en $h_0 = {h0}$:")
        st.latex(f"f'(h_0) = \\frac{{{k_val}}}{{2\sqrt{{{h0}}}}} = {m:.4f}")
        
        # Gráfica
        h_vals = np.linspace(rango[0], rango[1], 500)
        q_real = k_val * np.sqrt(h_vals)
        q_lin = f_h0 + m * (h_vals - h0)
        
        fig, ax = plt.subplots()
        ax.plot(h_vals, q_real, 'b-', label='Sistema Real (No Lineal)', lw=2)
        ax.plot(h_vals, q_lin, 'r--', label='Aproximación Lineal (Tangente)', lw=2)
        ax.scatter([h0], [f_h0], color='black', zorder=5, label=f'Punto h0={h0}')
        
        ax.set_xlabel("Nivel (h)")
        ax.set_ylabel("Flujo (Q)")
        ax.set_title("Linealización de Caudal vs Nivel")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

# ------------------------------------------------------------------
# 5.3 PÉNDULO SIMPLE
# ------------------------------------------------------------------
else:
    st.header("🏮 5.3 Péndulo Simple (Sen θ)")
    st.write("La ecuación del péndulo es $mL^2\ddot{\theta} + mgL\sin(\theta) = 0$.")
    st.write("Para ángulos pequeños, linealizamos $\sin(\theta) \approx \theta$.")

    theta_0 = st.slider("Punto de Operación θ0 (Radianes)", -np.pi, np.pi, 0.0)
    
    t_vals = np.linspace(-np.pi, np.pi, 500)
    y_real = np.sin(t_vals)
    y_lin = np.sin(theta_0) + np.cos(theta_0) * (t_vals - theta_0)

    fig2, ax2 = plt.subplots()
    ax2.plot(t_vals, y_real, 'g-', label='sin(θ)', lw=2)
    ax2.plot(t_vals, y_lin, 'r--', label='Linealización Taylor', lw=2)
    ax2.scatter([theta_0], [np.sin(theta_0)], color='black', label=f'θ0 = {theta_0:.2f}')
    
    ax2.set_ylim([-2, 2])
    ax2.set_xlabel("Ángulo θ [rad]")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)
    
    st.warning(f"Error en θ = {theta_0 + 0.5:.2f} rad: {abs(np.sin(theta_0 + 0.5) - (np.sin(theta_0) + np.cos(theta_0)*0.5)):.4f}")
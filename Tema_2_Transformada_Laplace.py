import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import control as ctrl

# 1. Configuración de página
st.set_page_config(page_title="Tema 2: Laplace y Estabilidad", layout="wide")

st.title("🎯 Tema 2: Transformada de Laplace y Estabilidad")
st.markdown("---")

# Navegación interna
opcion = st.sidebar.radio(
    "Selecciona la herramienta:",
    ["2.1 Dinámica del Plano s", 
     "2.2 Calculadora de Inversa (Paso a Paso)", 
     "2.3 Diagnóstico de Estabilidad de T(s)"]
)

# ------------------------------------------------------------------
# 2.1 DINÁMICA DEL PLANO S
# ------------------------------------------------------------------
if opcion == "2.1 Dinámica del Plano s":
    st.header("📍 2.1 Localización de Polos y Respuesta Temporal")
    st.write("Visualiza la relación directa entre la ubicación de los polos y la respuesta al impulso.")

    col_input, col_graph = st.columns([1, 2])

    with col_input:
        st.subheader("Configuración de Polos")
        sigma = st.slider("Parte Real (σ)", -5.0, 5.0, -1.0)
        omega = st.slider("Parte Imaginaria (jω)", 0.0, 10.0, 2.0)
        st.info("Un polo con σ > 0 genera una respuesta divergente (inestable).")

    with col_graph:
        # Polos complejos: (s - (sigma + omega*j))(s - (sigma - omega*j))
        den = [1, -2*sigma, sigma**2 + omega**2]
        sys = ctrl.TransferFunction([1], den)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Gráfica Plano s
        ax1.axvline(0, color='black', lw=1); ax1.axhline(0, color='black', lw=1)
        ax1.scatter([sigma, sigma], [omega, -omega], marker='x', color='red', s=100)
        ax1.set_title("Ubicación en el Plano s")
        ax1.set_xlim([-6, 6]); ax1.set_ylim([-11, 11]); ax1.grid(True)
        
        # Respuesta Temporal
        t, y = ctrl.impulse_response(sys)
        ax2.plot(t, y, color='blue')
        ax2.set_title("Respuesta al Impulso h(t)")
        ax2.grid(True)
        st.pyplot(fig)

# ------------------------------------------------------------------
# 2.2 CALCULADORA DE INVERSA
# ------------------------------------------------------------------
elif opcion == "2.2 Calculadora de Inversa (Paso a Paso)":
    st.header("🔄 2.2 Inversa de Laplace por Fracciones Parciales")
    s, t = sp.symbols('s t', positive=True)

    formula = st.text_input("Ingresa F(s) (ej: 1/(s**2 + 5*s + 6)):", "1/(s**2 + 3*s + 2)")

    try:
        F_s = sp.sympify(formula)
        f_t = sp.inverse_laplace_transform(F_s, s, t)
        frac = sp.apart(F_s)

        st.subheader("Procedimiento Simbólico")
        st.write("**1. Función en dominio s:**")
        st.latex(r"F(s) = " + sp.latex(F_s))
        st.write("**2. Descomposición por fracciones parciales:**")
        st.latex(sp.latex(frac))
        st.success("**3. Resultado en dominio t:**")
        st.latex(f"f(t) = {sp.latex(sp.simplify(f_t))}")
    except Exception as e:
        st.error(f"Error técnico: {e}")

# ------------------------------------------------------------------
# 2.3 DIAGNÓSTICO DE ESTABILIDAD
# ------------------------------------------------------------------
else:
    st.header("⚖️ 2.3 Análisis de Estabilidad de T(s)")
    
    num_str = st.text_input("Coeficientes Numerador:", "1")
    den_str = st.text_input("Coeficientes Denominador (ej. 1, 2, 10):", "1, 2, 10")

    try:
        num = [float(x.strip()) for x in num_str.split(",")]
        den = [float(x.strip()) for x in den_str.split(",")]
        sys = ctrl.TransferFunction(num, den)
        poles = ctrl.poles(sys)
        
        st.write("**Polos del Sistema:**", poles)
        
        if all(p.real < 0 for p in poles):
            st.success("✅ Sistema BIBO Estable (Semiplano Izquierdo).")
        elif any(p.real > 0 for p in poles):
            st.error("❌ Sistema Inestable (Semiplano Derecho).")
        else:
            st.warning("⚠️ Sistema Marginalmente Estable (Polos sobre el eje jω).")
    except:
        st.info("Ingresa los coeficientes separados por comas.")
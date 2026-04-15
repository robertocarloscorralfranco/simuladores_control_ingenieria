import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
import sympy as sp

# 1. Configuración de página
st.set_page_config(page_title="Tema 11: Lugar de las Raíces", layout="wide")

st.title("🌱 Tema 11: Lugar Geométrico de las Raíces (LGR)")
st.markdown("---")

# Menú lateral
opcion = st.sidebar.radio(
    "Selecciona la sección:",
    ["11.1 y 11.2 Definición y Reglas de Construcción", "11.3 Diseño de Sistemas de Control"]
)

# ------------------------------------------------------------------
# 11.1 y 11.2 DEFINICIÓN Y REGLAS
# ------------------------------------------------------------------
if opcion == "11.1 y 11.2 Definición y Reglas de Construcción":
    st.header("📌 11.1 y 11.2 Fundamentos y Reglas del LGR")
    st.write("El LGR es el lugar de los polos en lazo cerrado cuando la ganancia $K$ varía de $0$ a $\infty$.")
    
    st.latex(r"1 + K G(s)H(s) = 0")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuración de la Planta")
        # Planta genérica G(s) = 1 / (s(s+a)(s+b))
        a = st.slider("Ubicación Polo 2 (a):", 1, 10, 2)
        b = st.slider("Ubicación Polo 3 (b):", 1, 20, 5)
        
        st.info("""
        **Reglas clave:**
        - **Número de ramas:** Igual al número de polos.
        - **Simetría:** Respecto al eje real.
        - **Asíntotas:** Los polos se dirigen a los ceros (en el infinito).
        """)

    with col2:
        # Definición del sistema G(s) = 1 / [s(s+a)(s+b)]
        sys = ctrl.TransferFunction([1], [1, a+b, a*b, 0])
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ctrl.root_locus(sys, ax=ax, grid=True)
        ax.set_title("Lugar Geométrico de las Raíces")
        st.pyplot(fig)
        
        # Cálculo del Centroide (Sigma_a) y Ángulo
        n = 3 # polos
        m = 0 # ceros
        sum_poles = 0 + (-a) + (-b)
        centroid = sum_poles / (n - m)
        st.write(f"**Cálculo del Centroide (Asíntotas):**")
        st.latex(r"\sigma_a = \frac{\sum \text{Polos} - \sum \text{Ceros}}{n - m} = " + f"{centroid:.2f}")

# ------------------------------------------------------------------
# 11.3 DISEÑO DE SISTEMAS
# ------------------------------------------------------------------
else:
    st.header("🎯 11.3 Diseño basado en Ganancia K")
    st.write("Selecciona una ganancia $K$ y observa la nueva ubicación de los polos en lazo cerrado.")

    # Sistema base: G(s) = 1 / (s^2 + 2s + 2)
    k_design = st.slider("Ganancia de Diseño (K):", 0.1, 50.0, 1.0)
    
    num = [1]
    den = [1, 2, 2]
    G = ctrl.TransferFunction(num, den)
    
    # Lazo cerrado T(s) = KG / (1 + KG)
    T = ctrl.feedback(k_design * G, 1)
    poles = ctrl.poles(T)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Análisis de Polos")
        st.write(f"Para $K = {k_design}$, los polos en lazo cerrado son:")
        st.write(poles)
        
        # Gráfica de respuesta al escalón
        t, y = ctrl.step_response(T)
        fig_step, ax_step = plt.subplots()
        ax_step.plot(t, y, color='orange', lw=2)
        ax_step.axhline(1, color='red', ls='--')
        ax_step.set_title(f"Respuesta al Escalón con K={k_design}")
        ax_step.grid(True)
        st.pyplot(fig_step)

    with c2:
        st.subheader("Ubicación en el Plano s")
        fig_map, ax_map = plt.subplots()
        # Mostrar el LGR de fondo
        ctrl.root_locus(G, ax=ax_map, grid=False)
        # Resaltar la posición actual de los polos
        ax_map.scatter(poles.real, poles.imag, color='black', marker='o', s=100, label='Polos Actuales')
        ax_map.set_title("Trayectoria y Posición Actual")
        ax_map.legend()
        st.pyplot(fig_map)
        
        st.warning("Nota cómo al aumentar K, los polos se mueven hacia la derecha o aumentan su parte imaginaria, incrementando la oscilación.")
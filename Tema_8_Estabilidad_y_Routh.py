import streamlit as st
import numpy as np
import pandas as pd
import sympy as sp
import matplotlib.pyplot as plt

# 1. Configuración de página
st.set_page_config(page_title="Tema 8: Estabilidad y Routh-Hurwitz", layout="wide")

st.title("🛡️ Tema 8: Estabilidad del Sistema")
st.markdown("---")

# Menú lateral
opcion = st.sidebar.radio(
    "Selecciona el análisis:",
    ["8.1 y 8.3 Matriz de Routh-Hurwitz Automática", 
     "8.2 Error en Estado Estable (ess)"]
)

# ------------------------------------------------------------------
# LÓGICA DE ROUTH-HURWITZ (8.1 y 8.3)
# ------------------------------------------------------------------
if opcion == "8.1 y 8.3 Matriz de Routh-Hurwitz Automática":
    st.header("🧮 8.1 y 8.3 Criterio de Estabilidad de Routh-Hurwitz")
    st.write("Ingresa los coeficientes del polinomio característico $P(s)$ de mayor a menor potencia.")

    # Entrada de coeficientes
    coef_input = st.text_input("Coeficientes (ej. para s³ + 2s² + 4s + 8 ingresa: 1, 2, 4, 8):", "1, 10, 31, 1030")

    try:
        coeffs = [float(x.strip()) for x in coef_input.split(",")]
        n = len(coeffs) - 1
        
        # Construcción de la matriz de Routh
        num_rows = n + 1
        num_cols = (n + 2) // 2
        rh_matrix = np.zeros((num_rows, num_cols))

        # Llenar las dos primeras filas
        row1 = coeffs[0::2]
        row2 = coeffs[1::2]
        rh_matrix[0, :len(row1)] = row1
        rh_matrix[1, :len(row2)] = row2

        # Calcular el resto de la matriz
        for i in range(2, num_rows):
            for j in range(num_cols - 1):
                a1 = rh_matrix[i-1, 0]
                if a1 == 0:
                    a1 = 1e-6  # Evitar división por cero (épsilon)
                
                b1 = rh_matrix[i-2, 0]
                b2 = rh_matrix[i-2, j+1]
                a2 = rh_matrix[i-1, j+1]
                
                # Fórmula del determinante de Routh
                rh_matrix[i, j] = ((a1 * b2) - (b1 * a2)) / a1

        # Formatear para visualización
        rows_labels = [f"s^{n-i}" for i in range(num_rows)]
        df_routh = pd.DataFrame(rh_matrix, index=rows_labels)
        
        st.subheader("Matriz de Routh Resultante")
        st.table(df_routh)

        # Diagnóstico de Estabilidad
        first_col = rh_matrix[:, 0]
        changes = 0
        for i in range(len(first_col)-1):
            if np.sign(first_col[i]) != np.sign(first_col[i+1]):
                changes += 1

        if changes == 0:
            st.success("✅ SISTEMA ESTABLE: No hay cambios de signo en la primera columna.")
        else:
            st.error(f"❌ SISTEMA INESTABLE: Se detectaron {changes} cambios de signo.")
            st.write(f"Esto indica que existen **{changes} polos** en el semiplano derecho del plano s.")

    except Exception as e:
        st.info("Ingresa los coeficientes correctamente para generar la matriz.")

# ------------------------------------------------------------------
# ERROR EN ESTADO ESTABLE (8.2)
# ------------------------------------------------------------------
else:
    st.header("🎯 8.2 Error en Estado Estable ($e_{ss}$)")
    st.write("Analiza la precisión del sistema según el Tipo de Sistema (número de integradores en lazo abierto).")

    s = sp.Symbol('s')
    st.sidebar.subheader("Definición de G(s)H(s)")
    k = st.sidebar.number_input("Ganancia K", value=10.0)
    
    # Ejemplo de sistema Tipo 1: K / [s(s+1)(s+2)]
    num_ex = k
    den_ex = s*(s+2)*(s+5)
    gh = num_ex / den_ex

    st.write("Función de transferencia en lazo abierto $G(s)H(s)$:")
    st.latex(sp.latex(gh))

    # Cálculo de constantes de error
    kp = sp.limit(gh, s, 0)
    kv = sp.limit(s * gh, s, 0)
    ka = sp.limit(s**2 * gh, s, 0)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Constante Posición (Kp)", str(kp))
        ess_step = 1 / (1 + kp) if kp != sp.oo else 0
        st.write(f"**ess (Escalón):** {ess_step}")

    with col2:
        st.metric("Constante Velocidad (Kv)", str(kv))
        ess_ramp = 1 / kv if kv != 0 else "∞"
        st.write(f"**ess (Rampa):** {ess_ramp}")

    with col3:
        st.metric("Constante Aceleración (Ka)", str(ka))
        ess_para = 1 / ka if ka != 0 else "∞"
        st.write(f"**ess (Parábola):** {ess_para}")

    st.info("""
    **Interpretación del Tipo de Sistema:**
    - **Tipo 0:** Error constante ante escalón, infinito ante rampa.
    - **Tipo 1:** Error cero ante escalón, constante ante rampa.
    - **Tipo 2:** Error cero ante escalón y rampa, constante ante parábola.
    """)
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tema 15: Simbología ISA", layout="wide")

st.title("🏗️ Tema 15: Simbología ISA y Diagramas P&ID")
st.markdown("---")

tab1, tab2 = st.tabs(["15.1 Identificación de Instrumentos", "15.2 Tipos de Señales y Líneas"])

with tab1:
    st.header("🏷️ 15.1 Identificación (Letras de Identificación)")
    st.write("En un diagrama P&ID, los instrumentos se identifican por etiquetas (tags) como **TIC-101**.")
    
    # Tabla interactiva de letras comunes
    data = {
        "Primera Letra (Variable)": ["T (Temperatura)", "P (Presión)", "L (Nivel)", "F (Flujo)", "V (Vibración)"],
        "Letras Sucesivas (Función)": ["C (Controlador)", "I (Indicador)", "T (Transmisor)", "V (Válvula)", "A (Alarma)"]
    }
    st.table(pd.DataFrame(data))
    
    st.subheader("Ejemplos comunes:")
    st.info("- **TIC:** Controlador Indicador de Temperatura\n- **PT:** Transmisor de Presión\n- **LV:** Válvula de Nivel")

with tab2:
    st.header("📏 15.2 Líneas y Conexiones")
    st.write("La forma en que se dibujan las líneas indica la naturaleza de la señal.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Tipos de Señales:**
        - **Continua (Sólida):** Conexión de proceso (tubería).
        - **Segmentada (---):** Señal eléctrica.
        - **Cruzada (---//---):** Señal neumática.
        - **Con Círculos (-o-o-):** Señal de datos (Software/Digital).
        """)
        
    with col2:
        st.subheader("Ubicación del Instrumento")
        st.write("- **Círculo simple:** Montado en campo.")
        st.write("- **Círculo con línea media:** Montado en panel principal.")
        st.write("- **Círculo con línea doble:** Montado en panel auxiliar.")

    st.subheader("Simulador de Lazo de Control (P&ID)")
    st.write("Identifica los componentes en este lazo típico:")
    st.code("""
    [Proceso] ---> (PT) ---eléctrica---> [Controlador (PIC)] ---neumática---> (PV - Válvula)
    """)
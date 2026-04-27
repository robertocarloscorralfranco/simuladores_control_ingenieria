import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
from fpdf import FPDF
import io

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
st.set_page_config(page_title="Laboratorio Nyquist - TecMilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 25px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 25px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Tema 13: Métodos de Respuesta a la Frecuencia</p>', unsafe_allow_html=True)

# ==========================================
# CLASE DE REPORTE TÉCNICO PDF
# ==========================================
class NyquistFullReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 107, 63)
        self.cell(0, 10, 'Reporte de Analisis de Estabilidad - Universidad Tecmilenio', 0, 1, 'C')
        self.ln(5)

    def add_step(self, title, content):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 240, 235)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, content)
        self.ln(4)

def generate_full_pdf(k, den_str, gm, pm, is_stable, plot_buf, math_steps):
    pdf = NyquistFullReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Solucion Analitica y Deduccion de Estabilidad', 0, 1, 'L')
    pdf.ln(5)
    for s in math_steps:
        pdf.add_step(s['title'], s['content'])
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Validacion Grafica de Nyquist', 0, 1, 'C')
    img_data = plot_buf.getvalue()
    with open("temp_final_plot.png", "wb") as f: f.write(img_data)
    pdf.image("temp_final_plot.png", x=55, w=100)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# LÓGICA DE DATOS
# ==========================================
st.sidebar.header("Parámetros del Sistema")
k_val = st.sidebar.slider("Ganancia (K)", 0.1, 20.0, 6.0, step=0.1)
den_input = st.sidebar.text_input("Coeficientes (ej. 1, 3, 2, 0)", "1, 3, 2, 0")

try:
    coeffs = [float(x.strip()) for x in den_input.split(",")]
    a, b, c, d = (coeffs + [0]*4)[:4] 
    sys = ctrl.TransferFunction([k_val], coeffs)
    gm, pm, wg, wp = ctrl.margin(sys)
    gm_db = 20 * np.log10(gm) if (gm is not None and gm > 0) else 0.0
    pm_val = pm if pm is not None else 0.0
    is_stable = (gm_db > 0 and pm_val > 0)
except:
    st.sidebar.error("Error en coeficientes.")
    st.stop()

t1, t2, t3 = st.tabs(["Simulador y Solucion Paso a Paso", "Interpretacion Geometrizada", "Comparativa de Robustez"])

# ------------------------------------------
# TAB 1: UNIFICADO (SIMULADOR + CONSTRUCTOR)
# ------------------------------------------
with t1:
    st.markdown('<p class="section-header">Simulación Técnica y Resolución Analítica</p>', unsafe_allow_html=True)
    c_p, c_r = st.columns([1, 1])
    with c_p:
        fig, ax = plt.subplots(figsize=(5, 5))
        ctrl.nyquist_plot(sys, ax=ax, color=TEC_GREEN, warn_encirclements=False)
        ax.plot(-1, 0, 'ro', markersize=6)
        ax.set_title("Trayectoria Polar", fontsize=10)
        st.pyplot(fig)
        buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches='tight')
    with c_r:
        st.subheader("Diagnóstico de Lazo Cerrado")
        if is_stable: st.success("SISTEMA ESTABLE")
        else: st.error("SISTEMA INESTABLE")
        st.write(f"**MG:** {gm_db:.2f} dB | **MF:** {pm_val:.2f} deg")
        st.write(f"**Cruce Real (w_cp):** {wp:.4f} rad/s")

    st.markdown('<p class="section-header">Deducción Paso a Paso del Sistema</p>', unsafe_allow_html=True)
    math_steps = [
        {"title": "Paso 1: Desarrollo del Polinomio", "content": f"Expandimos el denominador para evitar errores: G(s) = {k_val} / ({a}s^3 + {b}s^2 + {c}s + {d})"},
        {"title": "Paso 2: Evaluación Frecuencial (s = jw)", "content": f"Sustituimos s por jw:\nG(jw) = {k_val} / [({d} - {b}w^2) + j({c}w - {a}w^3)]"},
        {"title": "Paso 3: El Truco del Conjugado", "content": "Multiplicamos por el conjugado complejo para separar Re e Im. Esto garantiza un denominador real."},
        {"title": "Paso 4: Separación Analítica", "content": f"Re(w) = {k_val}({d}-{b}w^2)/Denom. | Im(w) = -{k_val}({c}w-{a}w^3)/Denom."},
        {"title": "Paso 5: Intersección con el Eje Real", "content": f"Frecuencia de cruce calculada: w_cp = {wp:.4f} rad/s."},
        {"title": "Paso 6: Ganancia Crítica y Veredicto", "content": f"Veredicto: El sistema es {'Estable' if is_stable else 'Inestable'}."}
    ]
    for s in math_steps:
        st.markdown(f'<div class="step-box"><b>{s["title"]}</b><br>{s["content"]}</div>', unsafe_allow_html=True)
    pdf_bytes = generate_full_pdf(k_val, den_input, gm_db, pm_val, is_stable, buf, math_steps)
    st.download_button("Descargar Reporte Completo (PDF)", pdf_bytes, "IDC_T13_Maestria.pdf")

# ------------------------------------------
# TAB 2: INTERPRETACIÓN GEOMETRIZADA COMPLETA
# ------------------------------------------
with t2:
    st.markdown('<p class="section-header">Analisis Geometrico de Conceptos Abstractos</p>', unsafe_allow_html=True)
    st.write("Visualización técnica de los conceptos clave aplicados a su problema específico.")

    # 1. Punto Crítico
    st.subheader("1. El Punto Critico -1 + j0")
    col1a, col1b = st.columns([1.5, 1])
    with col1a:
        st.write("**Representación Matemática:** Condición exacta donde la magnitud es 1 y el desfase es -180°.")
        st.write("**Riesgo:** Invertir la señal y restarla equivale a sumarla (retroalimentación positiva), causando oscilaciones destructivas.")
    with col1b:
        f1, a1 = plt.subplots(figsize=(4, 2.5)); a1.axhline(0, color='k', lw=1); a1.axvline(0, color='k', lw=1)
        a1.add_artist(plt.Circle((0,0), 1, color='gray', ls='--', fill=False))
        a1.plot(-1, 0, 'ro', markersize=8); a1.set_xlim([-1.5, 0.5]); a1.set_ylim([-1, 1]); a1.axis('off'); st.pyplot(f1)
    
    # 2. Frecuencia de Cruce de Fase
    st.subheader(r"2. Frecuencia de Cruce de Fase ($\omega_{cp}$)")
    col2a, col2b = st.columns([1.5, 1])
    with col2a:
        st.write(f"**Definición:** Frecuencia exacta donde el ángulo llega a -180°. En su sistema ocurre a **{wp:.4f} rad/s**.")
        st.write("**Visualización:** Punto exacto donde la curva cruza el eje real negativo (Im=0).")
    with col2b:
        f2, a2 = plt.subplots(figsize=(4, 2.5))
        ctrl.nyquist_plot(sys, ax=a2, color='blue', warn_encirclements=False)
        if wp > 0:
            res_wp = ctrl.frequency_response(sys, [wp])
            # Corrección de IndexError: Acceso robusto a los datos
            r_wp = np.real(res_wp.fresp.flatten()[0])
            a2.plot(r_wp, 0, 'ko', markersize=6)
        a2.set_xlim([-2, 0.5]); a2.set_ylim([-1.5, 1.5]); a2.axis('off'); st.pyplot(f2)

    # 3. Margen de Ganancia (MG)
    st.subheader("3. Margen de Ganancia (MG)")
    col3a, col3b = st.columns([1.5, 1])
    with col3a:
        st.write(f"**Concepto:** Colchón de seguridad. Factor para multiplicar la ganancia antes de la inestabilidad.")
        st.write(f"**Su Sistema:** Soporta un aumento de **{gm:.2f} veces** la ganancia actual.")
    with col3b:
        f3, a3 = plt.subplots(figsize=(4, 2.5)); a3.axhline(0, color='k', lw=1); a3.axvline(0, color='k', lw=1)
        r_int = -1/gm if (gm is not None and gm > 0) else 0
        a3.plot([r_int, -1], [0, 0], color='orange', lw=6); a3.plot(-1, 0, 'ro'); a3.plot(r_int, 0, 'bo')
        a3.set_xlim([-1.5, 0.2]); a3.set_ylim([-0.5, 0.5]); a3.axis('off'); st.pyplot(f3)

    # 4. Margen de Fase (MF)
    st.subheader("4. Margen de Fase (MF)")
    col4a, col4b = st.columns([1.5, 1])
    with col4a:
        st.write(f"**Concepto:** Ángulo de retraso adicional tolerable antes de alcanzar -180°.")
        st.write(f"**Su Sistema:** Posee un margen de **{pm_val:.2f} grados**.")
    with col4b:
        f4, a4 = plt.subplots(figsize=(4, 2.5)); a4.axhline(0, color='k', lw=1); a4.axvline(0, color='k', lw=1)
        a4.add_artist(plt.Circle((0,0), 1, color='gray', ls='--', fill=False))
        if wg > 0:
            res_wg = ctrl.frequency_response(sys, [wg])
            # Corrección de IndexError: Acceso robusto al ángulo
            p_wg = np.angle(res_wg.fresp.flatten()[0])
            a4.plot([0, np.cos(p_wg)], [0, np.sin(p_wg)], 'g-', lw=2); a4.plot([-1, 0], [0, 0], 'r--')
        a4.set_xlim([-1.2, 0.2]); a4.set_ylim([-1.2, 0.2]); a4.axis('off'); st.pyplot(f4)

    # 5. Mapeo de Contornos
    st.subheader("5. Mapeo de Contornos (Transformación Conforme)")
    col5a, col5b = st.columns([1.5, 1])
    with col5a:
        st.write("**Definición:** Principio matemático que traduce información del plano s al plano polar.")
        st.write("**Funcionamiento:** Se evalúa un camino que rodea el semiplano derecho (inestable) para ver cuántas veces la curva resultante encierra al punto -1.")
    with col5b:
        f5, a5 = plt.subplots(figsize=(4, 2.5)); a5.axvline(0, color='k'); a5.fill_between([0, 1.5], -1.5, 1.5, color='blue', alpha=0.1)
        a5.set_title("Plano s (RHP)", fontsize=8); a5.set_xlim([-1, 1.5]); a5.set_ylim([-1.5, 1.5]); a5.axis('off'); st.pyplot(f5)

    # 6. Robustez del Sistema
    st.subheader("6. Robustez")
    col6a, col6b = st.columns([1.5, 1])
    with col6a:
        st.write(f"**Concepto:** Capacidad de mantenerse estable ante errores de modelo o desgaste físico.")
        st.write(f"**Diagnóstico:** Su sistema tiene una robustez **{'Adecuada' if gm_db > 6 else 'Crítica'}**.")
    with col6b:
        f6, a6 = plt.subplots(figsize=(4, 2.5))
        ctrl.nyquist_plot(sys, ax=a6, color=TEC_GREEN, warn_encirclements=False)
        a6.plot(-1, 0, 'ro', markersize=6); a6.set_xlim([-1.5, 0.5]); a6.set_ylim([-1, 1]); a6.axis('off'); st.pyplot(f6)

# ------------------------------------------
# TAB 3: COMPARATIVA (DISEÑO ÓPTIMO VS FALLIDO)
# ------------------------------------------
with t3:
    st.markdown('<p class="section-header">Referencia de Diseño: Correcto vs Incorrecto</p>', unsafe_allow_html=True)
    c_ok, c_no = st.columns(2)
    with c_ok:
        st.subheader("Diseño Robusto (K=2)"); s_ok = ctrl.TransferFunction([2], [1, 3, 2, 0])
        f_o, a_o = plt.subplots(figsize=(4, 4)); ctrl.nyquist_plot(s_ok, ax=a_o, color='blue', warn_encirclements=False)
        a_o.plot(-1, 0, 'ro'); st.pyplot(f_o)
    with c_no:
        st.subheader("Diseño Inestable (K=12)"); s_no = ctrl.TransferFunction([12], [1, 3, 2, 0])
        f_n, a_n = plt.subplots(figsize=(4, 4)); ctrl.nyquist_plot(s_no, ax=a_n, color='red', warn_encirclements=False)
        a_n.plot(-1, 0, 'ro'); st.pyplot(f_n)

st.markdown("---")
st.caption("Roberto Carlos Corral Franco - Universidad TecMilenio 2026")
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl
from fpdf import FPDF
import io
import time

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
st.set_page_config(page_title="UAV Control Lab - TecMilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 25px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 25px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Ingeniería de Control: Análisis de Estabilidad del UAV</p>', unsafe_allow_html=True)

# ==========================================
# CLASE DE REPORTE TÉCNICO PDF
# ==========================================
class UAVTechnicalReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 107, 63)
        self.cell(0, 10, 'Reporte de Estabilidad UAV - Universidad Tecmilenio', 0, 1, 'C')
        self.ln(5)

    def add_step(self, title, content):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 240, 235)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, content)
        self.ln(4)

def generate_pdf(k, gm, pm, is_stable, plot_buf, math_steps):
    pdf = UAVTechnicalReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Análisis de Estabilidad en Lazo Cerrado', 0, 1, 'L')
    pdf.ln(5)
    for s in math_steps:
        pdf.add_step(s['title'], s['content'])
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Validación de Trayectoria Nyquist', 0, 1, 'C')
    img_data = plot_buf.getvalue()
    with open("temp_uav_plot.png", "wb") as f: f.write(img_data)
    pdf.image("temp_uav_plot.png", x=55, w=100)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# FASE 1: DINÁMICA Y PARÁMETROS (simulador_v4)
# ==========================================
m, g = 3.2, 9.81
Ix, Iy, Iz = 0.38997, 0.974, 0.7887
dt = 0.02

if 'state' not in st.session_state:
    st.session_state.state = np.zeros(12)
    st.session_state.state[4] = 10.0 # Altitud inicial
    st.session_state.sim_time = 0.0
    st.session_state.target_z = 10.0

# ==========================================
# SIDEBAR: CONTROLES
# ==========================================
st.sidebar.header("🕹️ Parámetros de Control")
k_p = st.sidebar.slider("Ganancia Proporcional (Kp)", 0.1, 75.0, 15.0)
target_z_input = st.sidebar.slider("Setpoint Altitud (m)", 1.0, 15.0, 10.0)

# Modelo simplificado para análisis de estabilidad (Lazo Abierto)
# Basado en la identificación del simulador_v4: G(s) = 1 / [s(s+2)(s+5)]
num = [1]
den = [1, 7, 10, 0] # s^3 + 7s^2 + 10s
sys = ctrl.TransferFunction([k_p], den)
gm, pm, wg, wp = ctrl.margin(sys)
gm_db = 20 * np.log10(gm) if (gm is not None and gm > 0) else 0.0
pm_val = pm if pm is not None else 0.0
is_stable = (gm_db > 0 and pm_val > 0)

# ==========================================
# NAVEGACIÓN POR TABS
# ==========================================
t1, t2, t3 = st.tabs(["🎮 Vuelo en Tiempo Real", "📐 Resolución Analítica", "📡 Análisis Frecuencial"])

# ------------------------------------------
# TAB 1: SIMULADOR DINÁMICO
# ------------------------------------------
with t1:
    st.markdown('<p class="section-header">Simulador Cinematográfico del UAV</p>', unsafe_allow_html=True)
    
    # Lógica de simulación rápida
    for _ in range(5):
        # Control simple de altitud (solo P para demostración de estabilidad)
        error_z = target_z_input - st.session_state.state[4]
        u1 = m * (g + k_p * error_z - (k_p * 0.4) * st.session_state.state[5])
        u1 = np.clip(u1, 0.1, m*g*2)
        
        # Dinámica simplificada
        dz = st.session_state.state[5]
        ddz = (u1/m) - g
        st.session_state.state[4] += dz * dt
        st.session_state.state[5] += ddz * dt
        st.session_state.sim_time += dt

    # Gráfico de Altitud
    fig_v, ax_v = plt.subplots(figsize=(10, 3))
    ax_v.axhline(target_z_input, color='r', linestyle='--', label='Setpoint')
    ax_v.plot(st.session_state.sim_time, st.session_state.state[4], 'bo')
    ax_v.set_title("Respuesta Temporal de Altitud (Z)")
    ax_v.set_ylim([0, 20])
    ax_v.grid(True)
    st.pyplot(fig_v)
    
    if not is_stable:
        st.warning("⚠️ CUIDADO: La ganancia actual está provocando inestabilidad en el lazo cerrado.")

# ------------------------------------------
# TAB 2: SOLUCIÓN PASO A PASO
# ------------------------------------------
with t2:
    st.markdown('<p class="section-header">Deducción de Estabilidad (Criterio de Nyquist)</p>', unsafe_allow_html=True)
    
    math_steps = [
        {"title": "Paso 1: Función de Transferencia", "content": f"G(s) = {k_p} / (s^3 + 7s^2 + 10s)"},
        {"title": "Paso 2: Análisis de Polos", "content": "Polos en s=0, s=-2 y s=-5. El sistema es de tipo 1."},
        {"title": "Paso 3: Frecuencia de Cruce de Fase", "content": f"El cruce por los -180° ocurre a {wp:.4f} rad/s."},
        {"title": "Paso 4: Márgenes de Seguridad", "content": f"MG = {gm_db:.2f} dB | MF = {pm_val:.2f}°"},
        {"title": "Paso 5: Veredicto", "content": f"El sistema es {'ESTABLE' if is_stable else 'INESTABLE'} para Kp={k_p}."}
    ]
    
    for s in math_steps:
        st.markdown(f'<div class="step-box"><b>{s["title"]}</b><br>{s["content"]}</div>', unsafe_allow_html=True)
    
    # Generación de Nyquist para el reporte
    fig_n, ax_n = plt.subplots(figsize=(5, 5))
    ctrl.nyquist_plot(sys, ax=ax_n, color=TEC_GREEN, warn_encirclements=False)
    ax_n.plot(-1, 0, 'ro')
    buf = io.BytesIO(); fig_n.savefig(buf, format="png")
    
    pdf_bytes = generate_pdf(k_p, gm_db, pm_val, is_stable, buf, math_steps)
    st.download_button("📥 Descargar Reporte Técnico (PDF)", pdf_bytes, "Analisis_UAV_TecMilenio.pdf")

# ------------------------------------------
# TAB 3: DIAGRAMAS POLARES
# ------------------------------------------
with t3:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Trayectoria de Nyquist")
        st.pyplot(fig_n)
    with col_b:
        st.subheader("Respuesta en Frecuencia (Bode)")
        fig_b = plt.figure()
        ctrl.bode_plot(sys, dB=True, color='blue')
        st.pyplot(fig_b)

st.markdown("---")
st.caption("Roberto Carlos Corral Franco - Universidad TecMilenio 2026")

# Auto-refresh para la simulación
time.sleep(0.05)
st.rerun()
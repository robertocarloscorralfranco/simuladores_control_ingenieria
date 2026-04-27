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
st.set_page_config(page_title="Simulador de Estrategias Avanzadas - TecMilenio", layout="wide")

st.markdown(f"""
    <style>
    .main-title {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 28px; font-weight: bold; text-align: center; }}
    .section-header {{ color: {TEC_GREEN}; font-family: 'serif'; font-size: 20px; font-weight: bold; border-bottom: 1.5px solid {TEC_GREEN}; padding-bottom: 5px; margin-top: 20px; }}
    .step-box {{ padding: 25px; border: 1px solid #e6e6e6; border-left: 6px solid {TEC_GREEN}; background-color: #ffffff; margin-bottom: 25px; border-radius: 4px; line-height: 1.6; font-family: 'serif'; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">Tema 14: Laboratorio de Estrategias Avanzadas de Control</p>', unsafe_allow_html=True)

# ==========================================
# CLASE DE REPORTE TÉCNICO PDF
# ==========================================
class ControlAdvancedReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 107, 63)
        self.cell(0, 10, 'Reporte de Estrategias Avanzadas - Universidad Tecmilenio', 0, 1, 'C')
        self.ln(5)

    def add_step(self, title, content):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 240, 235)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, content)
        self.ln(4)

# ==========================================
# PESTAÑAS DE NAVEGACIÓN
# ==========================================
t1, t2, t3, t4 = st.tabs([
    "14.1 Servo vs Regulador", 
    "14.2 Estructuras Feedforward/Cascada", 
    "14.3 Control Óptimo/Adaptable", 
    "14.4 Control Inteligente (AI)"
])

# ------------------------------------------
# TAB 1: SERVO VS REGULADOR (CORREGIDA)
# ------------------------------------------
with t1:
    st.markdown('<p class="section-header">Dinámica de Seguimiento y Rechazo de Carga</p>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write("**Ajuste de Planta y Control**")
        tau_p = st.slider("Constante de tiempo ($\tau$)", 0.5, 5.0, 1.0)
        kp_val = st.slider("Ganancia ($K_p$)", 0.1, 10.0, 3.0)
        ti_val = st.slider("Tiempo Integral ($T_i$)", 0.1, 5.0, 1.0)
        dist_t = st.number_input("Inicio de Perturbación (s)", 5, 25, 12)

    with c2:
        t = np.linspace(0, 30, 1000)
        # Planta Gp(s) = 1 / (tau*s + 1)
        sys_p = ctrl.tf([1], [tau_p, 1])
        # Controlador PI
        cntrl = ctrl.tf([kp_val * ti_val, kp_val], [ti_val, 0])
        
        # Lazo cerrado: Referencia a Salida
        loop_ref = ctrl.feedback(cntrl * sys_p)
        t_r, y_ref = ctrl.step_response(loop_ref, t)
        
        # Lazo cerrado: Perturbación a Salida
        loop_dist = ctrl.feedback(sys_p, cntrl)
        t_d, y_dist = ctrl.step_response(loop_dist, t)
        
        # CORRECCIÓN DE BROADCASTING:
        y_final = np.copy(y_ref)
        mask = t >= dist_t
        num_indices = np.sum(mask)
        
        if num_indices > 0:
            # Restamos la respuesta a la perturbación (escalada) a partir de dist_t
            y_final[mask] -= 0.6 * y_dist[:num_indices]

        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(t, y_final, color=TEC_GREEN, lw=2, label="Respuesta de Planta")
        ax1.axhline(1, color='black', ls='--', alpha=0.5, label="Setpoint")
        ax1.axvline(dist_t, color='red', ls=':', label="Evento de Carga")
        ax1.set_title("Simulación Unificada: Respuesta Transitoria")
        ax1.legend(); ax1.grid(alpha=0.3)
        st.pyplot(fig1)

# ------------------------------------------
# TAB 2: ESTRATEGIAS AVANZADAS
# ------------------------------------------
with t2:
    mode = st.radio("Estrategia a Simular:", ["Control Antealimentado", "Control de Relación", "Control en Cascada"], horizontal=True)
    
    if mode == "Control Antealimentado":
        c1, c2 = st.columns([1, 2])
        with c1:
            k_ff = st.slider("Ganancia Compensador ($K_{ff}$)", -2.0, 0.0, -0.5)
            st.info("El control antealimentado mide la perturbación y actúa proactivamente.")
        with c2:
            t_ff = np.linspace(0, 20, 500)
            # Simulación: FB solo vs FB + FF
            y_fb_only = (t_ff > 5) * (0.5 * (1 - np.exp(-(t_ff-5)/1.5)))
            y_ff_comp = (t_ff > 5) * ((0.5 + k_ff) * (1 - np.exp(-(t_ff-5)/1.5)))
            
            fig2, ax2 = plt.subplots()
            ax2.plot(t_ff, y_fb_only, 'r--', label="Solo Feedback (Reactivo)")
            ax2.plot(t_ff, y_ff_comp, color=TEC_GREEN, label="Feedback + Feedforward (Proactivo)")
            ax2.set_title("Rechazo de Perturbación con Feedforward")
            ax2.legend(); st.pyplot(fig2)

    elif mode == "Control de Relación":
        c1, c2 = st.columns([1, 2])
        with c1:
            r_target = st.slider("Relación Objetivo ($R$)", 1.0, 15.0, 8.5)
            f_maestro = st.number_input("Caudal Maestro (L/min)", 10, 500, 100)
        with c2:
            st.metric("Flujo Esclavo Requerido", f"{f_maestro * r_target} L/min")
            x_range = np.linspace(0, 500, 100)
            fig_r, ax_r = plt.subplots()
            ax_r.plot(x_range, x_range * r_target, color=TEC_GREEN, label=f"Línea de Relación R={r_target}")
            ax_r.scatter(f_maestro, f_maestro*r_target, color='red', s=100, zorder=5)
            ax_r.set_xlabel("Flujo Maestro"); ax_r.set_ylabel("Flujo Esclavo"); ax_r.legend(); st.pyplot(fig_r)

    elif mode == "Control en Cascada":
        st.write("**Comparativa: Lazo Simple vs Lazo en Cascada**")
        inner_gain = st.slider("Ganancia Lazo Interno (Esclavo)", 1, 20, 10)
        t_cas = np.linspace(0, 15, 500)
        # Lazo simple (lento) vs Cascada (ataca perturbación rápido)
        y_simple = 1 - np.exp(-t_cas/3) * (np.cos(t_cas) + 0.3*np.sin(t_cas))
        y_casc = 1 - np.exp(-t_cas*inner_gain/5) * np.cos(t_cas) # Simulación conceptual
        
        fig_c, ax_c = plt.subplots()
        ax_c.plot(t_cas, y_simple, 'r--', label="Lazo Simple")
        ax_c.plot(t_cas, y_casc, color=TEC_GREEN, label="Lazo en Cascada")
        ax_c.set_title("Mejora en el tiempo de asentamiento")
        ax_c.legend(); st.pyplot(fig_c)

# ------------------------------------------
# TAB 3: ÓPTIMO Y ADAPTABLE
# ------------------------------------------
with t3:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write("**Control Óptimo (LQR)**")
        q_diag = st.slider("Peso del Estado (Q)", 1, 100, 50)
        r_weight = st.slider("Costo de Energía (R)", 0.1, 10.0, 1.0)
    with c2:
        # Péndulo invertido simplificado o masa-resorte
        A, B = [[0, 1], [-10, -1]], [[0], [1]]
        Q, R = np.eye(2)*q_diag, [[r_weight]]
        K, S, E = ctrl.lqr(A, B, Q, R)
        sys_opt = ctrl.ss(A - B*K, B, [[1, 0]], 0)
        t_o, y_o = ctrl.step_response(sys_opt)
        
        fig3, ax3 = plt.subplots()
        ax3.plot(t_o, y_o, color=TEC_GREEN, lw=2, label="Trayectoria Óptima")
        ax3.set_title(f"Respuesta LQR: Ganancia K = [{K[0,0]:.2f}, {K[0,1]:.2f}]")
        ax3.legend(); st.pyplot(fig3)

# ------------------------------------------
# TAB 4: CONTROL INTELIGENTE (AI)
# ------------------------------------------
with t4:
    ai_choice = st.selectbox("Técnica de Inteligencia Artificial:", ["Lógica Difusa", "Redes Neuronales", "Algoritmos Genéticos"])
    
    if ai_choice == "Lógica Difusa":
        st.write("**Diseño de Funciones de Membresía**")
        center = st.slider("Centro del conjunto 'Medio'", 20, 80, 50)
        x_fz = np.linspace(0, 100, 500)
        low = np.maximum(0, 1 - x_fz/30)
        mid = np.maximum(0, 1 - np.abs(x_fz - center)/20)
        high = np.maximum(0, (x_fz-70)/30)
        
        fig4, ax4 = plt.subplots(figsize=(8, 3))
        ax4.plot(x_fz, low, label="Frío/Bajo", color='blue')
        ax4.plot(x_fz, mid, label="Templado/Medio", color='orange')
        ax4.plot(x_fz, high, label="Caliente/Alto", color='red')
        ax4.legend(); st.pyplot(fig4)

    elif ai_choice == "Redes Neuronales":
        st.write("**Entrenamiento de Identificación de Planta**")
        lr = st.slider("Tasa de Aprendizaje ($\eta$)", 0.001, 0.5, 0.01)
        epochs = st.slider("Épocas", 50, 1000, 200)
        
        loss = np.exp(-np.linspace(0, 10, epochs)*lr*10) + 0.05*np.random.rand(epochs)
        fig5, ax5 = plt.subplots()
        ax5.plot(loss, color='purple')
        ax5.set_yscale('log'); ax5.set_title("Curva de Aprendizaje (Loss Curve)")
        ax5.set_xlabel("Iteraciones"); ax5.set_ylabel("Error Cuadrático Medio")
        st.pyplot(fig5)

    elif ai_choice == "Algoritmos Genéticos":
        st.write("**Optimización Evolutiva de Parámetros**")
        p_size = st.slider("Población", 10, 100, 50)
        gen_count = st.slider("Generaciones Máximas", 10, 50, 25)
        
        # Simulación de convergencia genética
        fitness = np.sort(np.random.rand(gen_count)) * 100
        fig6, ax6 = plt.subplots()
        ax6.step(range(gen_count), fitness, color='darkgreen', where='post')
        ax6.set_title("Evolución de la mejor Aptitud (Fitness)")
        ax6.set_ylabel("Puntaje de Aptitud"); st.pyplot(fig6)

# ==========================================
# PIE DE PÁGINA
# ==========================================
st.markdown("---")
st.markdown("**Referencias Bibliográficas (APA 7):**")
st.caption("Smith, C., & Corripio, A. (2016). *Control automático de procesos: Teoría y práctica*. Limusa.")
st.caption("Subbaram, D. (2018). *Optimal control systems*. CRC Press.")
st.caption("Prof. Roberto Carlos Corral Franco - TecMilenio 2026")
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="UAV Control Simulator - Lab", layout="wide")

# Estilo visual institucional
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #006B3F; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚁 Simulador UAV: Control de Misión y Estabilización")
st.write("Laboratorio de Ingeniería de Control - Fase 3")

# ==========================================
# CONSTANTES Y PARÁMETROS FÍSICOS (Portados de simulador_v4)
# ==========================================
m, g = 3.2, 9.81
Ix, Iy, Iz = 0.38997, 0.974, 0.7887
L = 0.8
dt = 0.05  # Paso de tiempo para la web

# Obstáculos en el entorno 3D
obstacles = [
    {'pos': np.array([3.0, 3.0, 10.0]), 'r': 2.5},
    {'pos': np.array([-4.0, 1.0, 10.0]), 'r': 2.0}
]

# ==========================================
# INICIALIZACIÓN DE ESTADO (Session State)
# ==========================================
# Streamlit se refresca de arriba a abajo; necesitamos guardar el estado del dron.
if 'state' not in st.session_state:
    st.session_state.state = np.zeros(12)
    st.session_state.state[4] = 10.0  # Altitud inicial
    st.session_state.sim_time = 0.0
    st.session_state.mission_started = False
    st.session_state.target_pos = np.array([0.0, 0.0, 10.0])
    st.session_state.planned_path = []
    st.session_state.current_wp_idx = 0
    st.session_state.hist_x, st.session_state.hist_y, st.session_state.hist_z = [], [], []
    st.session_state.hist_phi, st.session_state.hist_theta, st.session_state.hist_t = [], [], []

# ==========================================
# FUNCIONES DE DINÁMICA Y MATEMÁTICAS
# ==========================================
def uav_dynamics(st_vec, U1, U2, U3, U4, mission_active):
    x, dx, y, dy, z, dz, phi, dphi, theta, dtheta, psi, dpsi = st_vec
    wind_x = np.random.uniform(-0.5, 0.5) if mission_active else 0.0
    wind_y = np.random.uniform(-0.5, 0.5) if mission_active else 0.0
    
    ddx = (np.cos(phi)*np.sin(theta)*np.cos(psi) + np.sin(phi)*np.sin(psi)) * (U1/m) + (wind_x/m)
    ddy = (np.cos(phi)*np.sin(theta)*np.sin(psi) - np.sin(phi)*np.cos(psi)) * (U1/m) + (wind_y/m)
    ddz = (np.cos(phi)*np.cos(theta)) * (U1/m) - g
    
    ddphi = ((Iy - Iz)/Ix) * dtheta * dpsi + (U2/Ix)
    ddtheta = ((Iz - Ix)/Iy) * dphi * dpsi + (U3/Iy)
    ddpsi = ((Ix - Iy)/Iz) * dphi * dtheta + (U4/Iz)
    
    return np.array([dx, ddx, dy, ddy, dz, ddz, dphi, ddphi, dtheta, ddtheta, dpsi, ddpsi])

def get_rot_matrix(phi, theta, psi):
    Rx = np.array([[1, 0, 0], [0, np.cos(phi), -np.sin(phi)], [0, np.sin(phi), np.cos(phi)]])
    Ry = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
    Rz = np.array([[np.cos(psi), -np.sin(psi), 0], [np.sin(psi), np.cos(psi), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def generate_planned_path(start, end, obstacles):
    path = []
    steps = 25
    for i in range(steps + 1):
        p = start + (end - start) * (i / steps)
        for obs in obstacles:
            d = np.linalg.norm(p[:2] - obs['pos'][:2]) 
            if d < obs['r'] + 0.8:
                push_dir = p[:2] - obs['pos'][:2]
                push_dir = push_dir / (np.linalg.norm(push_dir) + 1e-6)
                p[:2] += push_dir * (obs['r'] + 0.8 - d)
        path.append(p)
    return np.array(path)

# ==========================================
# BARRA LATERAL (CONTROL DE PARÁMETROS)
# ==========================================
st.sidebar.header("🎮 Panel de Control")
st.sidebar.markdown("---")
slider_z = st.sidebar.slider("Altitud Objetivo Z (m)", 1.0, 15.0, 10.0)
slider_kp = st.sidebar.slider("Ganancia Kp Actitud", 1.0, 30.0, 15.0)

st.sidebar.subheader("📍 Coordenadas de Destino")
col_x, col_y = st.sidebar.columns(2)
target_x = col_x.number_input("X", value=0.0)
target_y = col_y.number_input("Y", value=0.0)

if st.sidebar.button("🚀 Iniciar Misión"):
    st.session_state.mission_started = True
    st.session_state.target_pos = np.array([target_x, target_y, slider_z])
    start_p = np.array([st.session_state.state[0], st.session_state.state[2], st.session_state.state[4]])
    st.session_state.planned_path = generate_planned_path(start_p, st.session_state.target_pos, obstacles)
    st.session_state.current_wp_idx = 1
    st.session_state.hist_x, st.session_state.hist_y, st.session_state.hist_z = [], [], []

if st.sidebar.button("🔄 Reiniciar Simulación"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# ==========================================
# LÓGICA DE CONTROL Y ACTUALIZACIÓN
# ==========================================
placeholder = st.empty()

# Ejecutar bucle de simulación
while True:
    Kp_att = slider_kp
    Kd_att = Kp_att * 0.4
    Kp_pos, Kd_pos = 0.8, 1.2
    
    active_target = st.session_state.target_pos.copy()
    active_target[2] = slider_z
    
    if st.session_state.mission_started and len(st.session_state.planned_path) > 0:
        if st.session_state.current_wp_idx < len(st.session_state.planned_path):
            active_target = st.session_state.planned_path[st.session_state.current_wp_idx]
            curr_pos = np.array([st.session_state.state[0], st.session_state.state[2], st.session_state.state[4]])
            if np.linalg.norm(curr_pos - active_target) < 0.8:
                st.session_state.current_wp_idx += 1

    # Integración de física
    x, dx, y, dy, z, dz, phi, dphi, theta, dtheta, psi, dpsi = st.session_state.state
    ex, ey, ez = active_target[0]-x, active_target[1]-y, active_target[2]-z
    
    U1 = np.clip(m * (g + Kp_pos*ez - Kd_pos*dz), 0.1, m*g*2)
    ax_ref, ay_ref = Kp_pos*ex - Kd_pos*dx, Kp_pos*ey - Kd_pos*dy
    theta_ref, phi_ref = np.clip(ax_ref*0.1, -0.5, 0.5), np.clip(-ay_ref*0.1, -0.5, 0.5)
    
    U2 = Ix * (Kp_att*(phi_ref - phi) - Kd_att*dphi)
    U3 = Iy * (Kp_att*(theta_ref - theta) - Kd_att*dtheta)
    U4 = Iz * (Kp_att*(0.0 - psi) - Kd_att*dpsi)
    
    st.session_state.state += uav_dynamics(st.session_state.state, U1, U2, U3, U4, st.session_state.mission_started) * dt
    st.session_state.sim_time += dt
    
    # Historial
    st.session_state.hist_x.append(st.session_state.state[0])
    st.session_state.hist_y.append(st.session_state.state[2])
    st.session_state.hist_z.append(st.session_state.state[4])
    st.session_state.hist_phi.append(st.session_state.state[6])
    st.session_state.hist_theta.append(st.session_state.state[8])
    st.session_state.hist_t.append(st.session_state.sim_time)

    # Renderizado de Gráficos
    with placeholder.container():
        col1, col2 = st.columns([2, 1])
        
        # 1. Gráfico 3D
        with col1:
            fig = plt.figure(figsize=(10, 7))
            ax3d = fig.add_subplot(111, projection='3d')
            ax3d.set_title("Entorno 3D: Evasión y Estabilización")
            ax3d.set_xlim([-10, 10]); ax3d.set_ylim([-10, 10]); ax3d.set_zlim([0, 15])
            
            # Dibujar obstáculos
            for obs in obstacles:
                u, v = np.mgrid[0:2*np.pi:10j, 0:np.pi:7j]
                ox = obs['pos'][0] + obs['r'] * np.cos(u) * np.sin(v)
                oy = obs['pos'][1] + obs['r'] * np.sin(u) * np.sin(v)
                oz = obs['pos'][2] + obs['r'] * np.cos(v)
                ax3d.plot_wireframe(ox, oy, oz, color='r', alpha=0.1)
            
            # Trayectoria
            ax3d.plot(st.session_state.hist_x, st.session_state.hist_y, st.session_state.hist_z, 'b-', alpha=0.6)
            
            # Dron (Brazos)
            R = get_rot_matrix(st.session_state.state[6], st.session_state.state[8], st.session_state.state[10])
            p = st.session_state.state[[0, 2, 4]].reshape(3, 1)
            px = R @ np.array([[L, -L], [0, 0], [0, 0]]) + p
            py = R @ np.array([[0, 0], [L, -L], [0, 0]]) + p
            ax3d.plot(px[0], px[1], px[2], 'r-', linewidth=3)
            ax3d.plot(py[0], py[1], py[2], 'g-', linewidth=3)
            st.pyplot(fig)

        # 2. Radar y Osciloscopio
        with col2:
            # Radar
            fig_r, axr = plt.subplots(figsize=(5, 5))
            axr.set_title("Radar 2D")
            axr.set_xlim([-10, 10]); axr.set_ylim([-10, 10]); axr.grid(True)
            for obs in obstacles:
                axr.add_patch(plt.Circle((obs['pos'][0], obs['pos'][1]), obs['r'], color='r', alpha=0.3))
            axr.plot(st.session_state.state[0], st.session_state.state[2], 'bo', markersize=8)
            axr.plot(st.session_state.target_pos[0], st.session_state.target_pos[1], 'rx')
            st.pyplot(fig_r)
            
            # Osciloscopio
            fig_o, axo = plt.subplots(figsize=(5, 3))
            axo.set_title("Control de Actitud")
            axo.plot(st.session_state.hist_t[-50:], st.session_state.hist_phi[-50:], 'r-', label="Roll")
            axo.plot(st.session_state.hist_t[-50:], st.session_state.hist_theta[-50:], 'g-', label="Pitch")
            axo.set_ylim([-0.6, 0.6]); axo.legend(loc="upper right")
            st.pyplot(fig_o)
    
    time.sleep(0.01) # Control de frecuencia de refrescostream
# Repositorio de Simuladores Interactivos para Ingeniería de Control

**Autor:** Corral-Franco, R. C. (2026).  
**Institución:** Universidad Tecmilenio, Campus Ciudad Juárez.  
**Grado:** Maestría en Educación / Facultad de Ingeniería.

---

## 1. Resumen Ejecutivo

El presente repositorio integra un compendio de **15 herramientas computacionales** diseñadas para la enseñanza avanzada de la Ingeniería de Control Clásica. Este proyecto surge como una solución tecnológica ante la necesidad de visualizar fenómenos dinámicos complejos, permitiendo al estudiante de nivel maestría interactuar con modelos matemáticos en tiempo real.

La arquitectura del sistema se fundamenta en el lenguaje de programación **Python**, empleando la biblioteca `control` para el cálculo matricial y `streamlit` para la interfaz de usuario. El enfoque principal es la validación de la estabilidad y el desempeño de sistemas lineales invariantes en el tiempo ($LTI$).

---

## 2. Fundamentación Teórica

La modelación de sistemas dinámicos constituye la base de la automatización moderna. Según establece **Ogata (2010)** en su obra fundamental:

> "El método de la transformada de Laplace permite convertir ecuaciones diferenciales complejas en ecuaciones algebraicas de una variable compleja $s$, facilitando el análisis de la respuesta transitoria y el diseño de compensadores" (p. 15).

Dicho rigor matemático se aplica en cada módulo de este repositorio, garantizando que los resultados obtenidos en las gráficas coincidan con los cálculos teóricos de la ingeniería de planta.

---

## 3. Estructura de los Simuladores

El proyecto se divide en tres ejes temáticos estratégicos:

### Módulo I: Modelación y Bases Matemáticas
* **Tema 1-3:** Transformada de Laplace, Simplificación de Bloques y Regla de Mason.
* **Tema 4:** Modelación de Sistemas Físicos (Analogías Masa-Resorte y RLC).
* **Tema 5:** Métodos de linealización mediante **Serie de Taylor**.

### Módulo II: Análisis de Respuesta y Estabilidad
* **Tema 6-7:** Respuesta transitoria y métodos gráficos de identificación de parámetros.
* **Tema 8:** Criterio de **Routh-Hurwitz** y análisis de error en estado estable ($e_{ss}$).
* **Tema 9-10:** Acciones de control básicas y sintonía de controladores **PID** bajo la metodología de **Ziegler-Nichols**.

### Módulo III: Análisis de Frecuencia y Estrategias Avanzadas
* **Tema 11:** Lugar Geométrico de las Raíces ($LGR$).
* **Tema 12-13:** Respuesta a la frecuencia mediante diagramas de **Bode** y el criterio de **Nyquist**.
* **Tema 14-15:** Control en cascada y Simbología **ISA** (norma ANSI/ISA-5.1-2009).

---

## 4. Requisitos Técnicos y Ejecución

Para garantizar la estabilidad del software, se recomienda el uso de un entorno virtual ($venv$).

### Dependencias Principales
| Librería | Función |
| :--- | :--- |
| **Streamlit** | Motor de la interfaz web interactiva. |
| **Control** | Cálculos de funciones de transferencia y estabilidad. |
| **NumPy** | Operaciones matemáticas y matrices. |
| **SymPy** | Cálculo simbólico y fracciones parciales. |

### Protocolo de Instalación
```powershell
# 1. Clonar el repositorio y acceder a la carpeta
cd SIMULADORES_DE_CONTROL

# 2. Instalar requerimientos
pip install -r requirements.txt

# 3. Ejecutar un simulador específico (Ejemplo: Tema 6)
streamlit run Tema_6_Respuesta_Transitoria.py
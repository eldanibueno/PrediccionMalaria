# 🦠 Sistema Predictivo de Malaria — Zonas Rurales de Colombia

Este proyecto es una plataforma epidemiológica computacional diseñada para el sistema médico colombiano. Utiliza el **Modelo Matemático de Ross-Macdonald** mediante **Ecuaciones Diferenciales Ordinarias (EDO) acopladas** para modelar e identificar la propagación de la malaria a través de la interacción cruzada entre humanos y el mosquito vector *Anopheles*.

## 📍 Regiones Parametrizadas
El sistema cuenta con configuraciones demográficas y epidemiológicas iniciales para tres de los focos más vulnerables en Colombia:
* **Chocó** (Alto Atrato / Quibdó)
* **Amazonas** (Leticia / Tarapacá)
* **Guaviare** (San José / Retorno)

## 🧠 Sustentación Matemática
El modelo resuelve numéricamente el sistema utilizando el método **Runge-Kutta de orden 4 y 5 (RK45)** a través de `scipy.integrate.solve_ivp`. 

Además, calcula en tiempo real el **Número Reproductivo Básico ($R_0$)** mediante la fórmula:
$$R_{0} = \sqrt{\frac{\beta_{h} \cdot \beta_{m} \cdot S_{h} \cdot S_{m}}{\gamma}}$$

Donde:
* $R_0 > 1$: Brote epidémico activo (la enfermedad se propaga).
* $R_0 < 1$: Brote controlado (la enfermedad tiende a desaparecer).

## 🚀 Tecnologías Utilizadas
* **Python 3**
* **Streamlit** (Interfaz de usuario y simulación interactiva)
* **SciPy** (Solucionador numérico de ecuaciones diferenciales)
* **Matplotlib** (Generación de curvas epidemiológicas)
* **Pandas & NumPy** (Procesamiento de matrices de datos)

## 🛠️ Instalación y Ejecución Local

1. Clonar el repositorio.
2. Instalar las dependencias del sistema:
   ```bash
   pip install -r requirements.txt

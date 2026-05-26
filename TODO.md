# Predicción de Malaria — Proyecto (Streamlit + Modelo Ross–Macdonald)

## 1) Idea del proyecto
Se construyó una aplicación web (Streamlit) para apoyar la **predicción del riesgo de malaria** en zonas rurales, usando un **modelo epidemiológico tipo Ross–Macdonald** expresado como un sistema de **ecuaciones diferenciales ordinarias (EDO)** acopladas entre:
- **Humanos**: población susceptible e infectada.
- **Mosquitos (vector)**: población susceptible e infectada.

La app permite explorar cómo cambian las curvas en el tiempo (S, I en ambos compartimentos) y cómo varía un **indicador de brote** (R₀) ante cambios en parámetros representativos de intervenciones sanitarias.

## 2) Problemática / motivación
La malaria depende de la interacción entre humanos y vectores. En la práctica, las intervenciones (toldillos, fumigación, acceso a tratamiento) afectan parámetros del modelo (transmisión y recuperación). El objetivo del proyecto es:
1. Proveer una herramienta visual y manipulable.
2. Permitir escenarios (rangos de parámetros) para observar tendencias de contagios.
3. Mostrar un diagnóstico básico vía R₀ y el pico de infectados humanos.

## 3) Qué se desarrolló
### 3.1 Interfaz de usuario (app.py)
- Pantalla principal con:
  - **Selección de región/departamento** (ajusta valores base de población y parámetros nominales).
  - **Entradas numéricas y deslizadores** para población iniciales y casos iniciales.
- **Panel de controles de intervención** (toldillos, fumigación, acceso a tratamiento) que impacta:
  - La transmisión efectiva (modulada por un factor de mitigación).
  - La tasa de recuperación **γ** basada en el acceso a tratamiento.
- Botón para **resolver** el sistema y generar resultados.
- Visualizaciones:
  - Curvas temporales para humanos (S_h, I_h).
  - Curvas temporales para mosquitos (S_m, I_m).
- Diagnóstico:
  - **R₀** calculado para el escenario.
  - Día y valor del **pico máximo de I_h**.
- Exportación:
  - Tabla de resultados y descarga CSV.

### 3.2 Motor epidemiológico (malaria_engine.py)
Incluye la lógica matemática y el solver numérico:
- `modelo_ross_macdonald(...)`: define el sistema ODE acoplado.
- `calcular_r0(...)`: estima **R₀** en función de β_h, β_m, S_h0, S_m0 y γ.
- `ejecutar_simulacion(...)`: resuelve las EDO con `scipy.integrate.solve_ivp(method='RK45')` y empaqueta curvas y tabla en una estructura `SimulationResult`.

## 4) Arquitectura del proyecto
- **app.py**
  - UI Streamlit + mapeo de sliders → parámetros del modelo.
  - Llama a `ejecutar_simulacion` y presenta los resultados.
- **malaria_engine.py**
  - Funciones del modelo y la simulación numérica.

## 5) Decisiones de diseño (resumen)
- Uso de `solve_ivp` para obtener soluciones suaves con `t_eval`.
- Separación UI / backend para mejorar mantenibilidad.
- Parametrización “por región” para proporcionar valores iniciales coherentes.
- Modelado simple de intervenciones:
  - Toldillos y fumigación reducen la transmisión (factor de mitigación).
  - Acceso a tratamiento incrementa γ (recuperación más rápida).

## 6) Estado actual del proyecto (desarrollado)
- Corregidos problemas de variables en la aplicación (p.ej. nombre de variable para el slider de acceso a tratamiento).
- Se añadió una forma de **mostrar/ocultar** controles mediante `st.session_state`, para evitar el bloqueo típico al colapsar manualmente la sidebar en Streamlit.
- Se ajustó el CSS para mantener legibilidad del texto de botones.

## 7) Cómo ejecutar
1. Instalar dependencias (si aplica) con el archivo `requeriments.txt`.
2. Ejecutar:
   ```bash
   python -m streamlit run app.py
   ```
3. Abrir la URL local que Streamlit imprime en consola.

## 8) TODO (pendientes / mejoras sugeridas)
- [ ] Mejorar el modelo incorporando estacionalidad o variación temporal de parámetros.
- [ ] Validar rangos realistas de parámetros epidemiológicos.
- [ ] Añadir explicación de interpretación clínica de R₀ y límites del modelo.
- [ ] Agregar trazas/controles para comparar escenarios (baseline vs intervención).
- [ ] Añadir tests básicos para el motor (`calcular_r0`, `modelo_ross_macdonald`).
- [ ] Revisar y refinar el diseño del panel de controles para consistencia visual.


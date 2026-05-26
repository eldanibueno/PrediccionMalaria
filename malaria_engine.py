from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

@dataclass(frozen=True)
class SimulationResult:
    t: np.ndarray
    Sh: np.ndarray
    Ih: np.ndarray
    Sm: np.ndarray
    Im: np.ndarray
    R0: float
    df_trends: pd.DataFrame

def modelo_ross_macdonald(t, y, beta_h, beta_m, gamma):
    """
    Define el sistema de ecuaciones diferenciales ordinarias acopladas.
    y = [Sh, Ih, Sm, Im]
    """
    Sh, Ih, Sm, Im = y
    
    # Ecuaciones diferenciales humanas
    dSh_dt = -beta_h * Sh * Im
    dIh_dt = (beta_h * Sh * Im) - (gamma * Ih)
    
    # Ecuaciones diferenciales del vector (mosquitos)
    dSm_dt = -beta_m * Sm * Ih
    dIm_dt = beta_m * Sm * Ih
    
    return [dSh_dt, dIh_dt, dSm_dt, dIm_dt]

def calcular_r0(beta_h: float, beta_m: float, Sh_0: float, Sm_0: float, gamma: float) -> float:
    """Calcula el Número Reproductivo Básico R0 para el sistema cruzado."""
    num = beta_h * beta_m * Sh_0 * Sm_0
    if gamma <= 0:
        return 0.0
    return float(np.sqrt(num / gamma))

def ejecutar_simulacion(
    Sh_0: float,
    Ih_0: float,
    Sm_0: float,
    Im_0: float,
    beta_h: float,
    beta_m: float,
    gamma: float,
    dias: int = 120
) -> SimulationResult:
    """
    Resuelve el sistema de ecuaciones diferenciales usando Runge-Kutta 45 (solve_ivp).
    """
    # Condiciones iniciales
    y0 = [Sh_0, Ih_0, Sm_0, Im_0]
    t_span = (0, dias)
    t_eval = np.linspace(0, dias, dias * 2) # Puntos de evaluación suaves para las gráficas
    
    # Resolver numéricamente las EDO
    solucion = solve_ivp(
        modelo_ross_macdonald,
        t_span,
        y0,
        args=(beta_h, beta_m, gamma),
        t_eval=t_eval,
        method='RK45'
    )
    
    # Extraer curvas resultantes
    t_out = solucion.t
    Sh_out, Ih_out, Sm_out, Im_out = solucion.y
    
    # Calcular R0 inicial del brote
    r0_val = calcular_r0(beta_h, beta_m, Sh_0, Sm_0, gamma)
    
    # Empaquetar tendencias en un DataFrame para análisis médico o descarga
    df_trends = pd.DataFrame({
        "Día": t_out,
        "Humanos Susceptibles (Sh)": Sh_out,
        "Humanos Infectados (Ih)": Ih_out,
        "Mosquitos Susceptibles (Sm)": Sm_out,
        "Mosquitos Infectados (Im)": Im_out
    })
    
    return SimulationResult(
        t=t_out,
        Sh=Sh_out,
        Ih=Ih_out,
        Sm=Sm_out,
        Im=Im_out,
        R0=r0_val,
        df_trends=df_trends
    )
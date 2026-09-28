"""
Módulo principal de simulación de trayectorias de persecución.
Basado en las especificaciones del TrabajoTx.pdf (Apartado 2: Simulación).
"""

import inspect
import numpy as np
from scipy.integrate import solve_ivp


def sedo_persecucion(t, y, vel_O, tray_O, vel_P, tpar, *extra_args):
    """
    Función SEDO que define el sistema de ecuaciones diferenciales del problema de persecución.
    
    Parámetros:
    -----------
    t : float
        Tiempo actual.
    y : ndarray
        Estado actual. 
        Si tpar es temporal ("True"): y = r_p (coordenadas del perseguidor).
        Si tpar es geométrico ("False"): y = [r_p, u] (perseguidor y parámetro u del objetivo).
    vel_O : callable o float
        Velocidad del objetivo v_o(t).
    tray_O : callable
        Trayectoria del objetivo: r_o(t) si tpar="True", o (r_o(u), ||r_dot_o(u)||) si tpar="False".
    vel_P : callable o float
        Velocidad del perseguidor v_p(t) o v_p(t, d).
    tpar : str o bool
        Indica si la parametrización del objetivo es temporal ("True") o geométrica ("False").
    extra_args : tuple
        Argumentos adicionales opcionales.
        
    Devuelve:
    ---------
    dydt : ndarray
        Derivadas temporales del estado.
    """
    is_temporal = str(tpar).strip().lower() in ("true", "1", "t", "temporal")
    
    if is_temporal:
        r_p = np.asarray(y, dtype=float)
        r_o = np.asarray(tray_O(t), dtype=float)
        diff = r_o - r_p
        d = np.linalg.norm(diff)
        
        # Evaluar velocidad del objetivo
        if callable(vel_O):
            vo = float(vel_O(t))
        else:
            vo = float(vel_O)
            
        # Evaluar velocidad del perseguidor
        if callable(vel_P):
            sig = inspect.signature(vel_P)
            n_params = len(sig.parameters)
            if n_params == 1:
                # Comprobar si el parámetro se llama d o distancia
                pname = list(sig.parameters.keys())[0]
                if pname in ("d", "dist", "distancia"):
                    vp = float(vel_P(d))
                else:
                    vp = float(vel_P(t))
            elif n_params == 2:
                vp = float(vel_P(t, d))
            else:
                vp = float(vel_P(t, d, *extra_args))
        else:
            vp = float(vel_P)
            
        # Evitar división por cero si d -> 0
        if d < 1e-12:
            dr_p = np.zeros_like(r_p)
        else:
            dr_p = (vp / d) * diff
            
        return dr_p
    else:
        # Parametrización geométrica con u
        y = np.asarray(y, dtype=float)
        r_p = y[:-1]
        u = float(y[-1])
        
        res_O = tray_O(u)
        if isinstance(res_O, (tuple, list)) and len(res_O) == 2:
            r_o = np.asarray(res_O[0], dtype=float)
            norm_dro = float(res_O[1])
        else:
            r_o = np.asarray(res_O, dtype=float)
            # Aproximación numérica si no devuelve la norma de la derivada
            du = 1e-6
            r_o_next = np.asarray(tray_O(u + du), dtype=float)
            norm_dro = float(np.linalg.norm(r_o_next - r_o) / du)
            
        diff = r_o - r_p
        d = np.linalg.norm(diff)
        
        if callable(vel_O):
            vo = float(vel_O(t))
        else:
            vo = float(vel_O)
            
        if callable(vel_P):
            sig = inspect.signature(vel_P)
            n_params = len(sig.parameters)
            if n_params == 1:
                pname = list(sig.parameters.keys())[0]
                if pname in ("d", "dist", "distancia"):
                    vp = float(vel_P(d))
                else:
                    vp = float(vel_P(t))
            elif n_params == 2:
                vp = float(vel_P(t, d))
            else:
                vp = float(vel_P(t, d, *extra_args))
        else:
            vp = float(vel_P)
            
        if d < 1e-12:
            dr_p = np.zeros_like(r_p)
        else:
            dr_p = (vp / d) * diff
            
        if norm_dro < 1e-12:
            du_dt = 0.0
        else:
            du_dt = vo / norm_dro
            
        return np.append(dr_p, du_dt)


# Alias con el nombre alternativo mencionado en el apéndice de especificación
sedo_P = sedo_persecucion


def persecucion(vel_O, tray_O, vel_P, edo_P, time, tray_P0, tpar="True", metodo="RK45",
                tplus=None, fout=False, eventos=None, args=None, opt_met={}):
    """
    Función que permite obtener la trayectoria de persecución resolviendo la SEDO asociada.
    
    Parámetros obligatorios y opcionales según TrabajoTx.pdf:
    ---------------------------------------------------------
    vel_O   : vo(t), función que devuelve la velocidad del objetivo en el tiempo (o float constante).
    tray_O  : ro(t) o ro(u), función vectorial que devuelve la trayectoria del objeto y, 
              en su caso, ||r_dot_o(u)||.
    vel_P   : vp(t), función que devuelve la velocidad del perseguidor en el tiempo o en función de la distancia.
    edo_P   : función que define el SEDO del problema de persecución (si es None, se usa sedo_persecucion).
    time    : intervalo de tiempo de resolución [t0, tf].
    tray_P0 : rp(0) posición inicial del perseguidor y, en su caso, del parámetro geométrico u0.
    tpar    : indica si el parámetro es el tiempo ("True") o geométrico ("False"). Por defecto "True".
    metodo  : método de resolución ('RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA'). Por defecto "RK45".
    tplus   : tiempos en que también se almacena la solución (t_eval en solve_ivp). Por defecto None.
    fout    : lógico que indica salida continua de la solución (dense_output en solve_ivp). Por defecto False.
    eventos : eventos destacables de la SEDO (events en solve_ivp). Por defecto None.
    args    : argumentos opcionales para la SEDO. Por defecto None.
    opt_met : diccionario con opciones del método seleccionado:
              first_step, min_step, max_step, rtol, atol, jac, jac_sparsity, lband, uband.
              
    Devuelve:
    ---------
    sol : OdeResult
        Objeto con el resultado devuelto por scipy.integrate.solve_ivp.
    """
    if opt_met is None:
        opt_met = {}
        
    # Filtrar o adaptar opciones soportadas directamente por scipy.integrate.solve_ivp
    solve_options = {}
    valid_solve_ivp_keys = {
        "rtol", "atol", "first_step", "max_step", "jac", "jac_sparsity",
        "vectorized", "lband", "uband"
    }
    for k, v in opt_met.items():
        if k in valid_solve_ivp_keys:
            solve_options[k] = v
            
    # Función ODE a integrar
    if edo_P is None:
        fun = lambda t, y, *extra: sedo_persecucion(t, y, vel_O, tray_O, vel_P, tpar, *extra)
    else:
        # Verificar signatura de edo_P proporcionada por el usuario
        sig = inspect.signature(edo_P)
        params_count = len(sig.parameters)
        if params_count == 2:
            fun = edo_P
        else:
            fun = lambda t, y, *extra: edo_P(t, y, vel_O, tray_O, vel_P, tpar, *extra)
            
    y0 = np.asarray(tray_P0, dtype=float)
    
    # Si tpar es False pero solo se dieron las coordenadas espaciales, añadir u0 = 0.0
    is_temporal = str(tpar).strip().lower() in ("true", "1", "t", "temporal")
    if not is_temporal:
        # Si la longitud coincide con una posición 2D o 3D y tray_O espera u
        # verificamos si se proporcionó u0
        try:
            # Prueba de evaluación para verificar si y0 incluye ya el parámetro u
            test_pos = tray_O(y0[-1])
        except Exception:
            pass

    sol = solve_ivp(
        fun=fun,
        t_span=time,
        y0=y0,
        method=metodo,
        t_eval=tplus,
        dense_output=bool(fout),
        events=eventos,
        args=args if args is not None else (),
        **solve_options
    )
    
    return sol

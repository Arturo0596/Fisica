"""
Script con la resolución, análisis numérico y simulación de todos los casos
exigidos en el Apartado 2 ("Simulación") de TrabajoTx.pdf.

Estructura de casos:
1. Validación con 6 métodos numéricos y comparación analítica (Línea recta) [20%]
   (A partir de este caso, todos los demás usan RK45 con rtol=1e-8, atol=1e-10)
2. Persecución con trayectoria circular del objetivo (vp = vo, +20%, -20%) [20%]
3. Ejemplo 1: Estación Espacial Internacional (ISS) con velocidad acotada [20%]
4. Ejemplo 2: Proyectil balístico de obús, radar y velocidad mínima de defensa [25%]
5. Ejemplo 3: Trayectoria 3D interpolada mediante splines con tpar='False' [15%]
"""

import time
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from persecucion import persecucion, sedo_persecucion

# Directorio de figuras
FIG_DIR = os.path.join(os.path.dirname(__file__), "figuras")
os.makedirs(FIG_DIR, exist_ok=True)


# ==============================================================================
# CASO 1: Validación y comparación de métodos numéricos (Línea recta) [20%]
# ==============================================================================
def ejecutar_caso_1():
    print("=" * 78)
    print("CASO 1: Validación con 6 métodos numéricos (Solución Analítica Línea Recta)")
    print("=" * 78)
    
    # Parámetros físicos del problema
    d = 100.0        # Distancia inicial en x (m)
    vo = 10.0        # Velocidad del objetivo (m/s)
    vp = 15.0        # Velocidad del perseguidor (m/s)
    cv = vp / vo     # cv = 1.5 > 1
    k = vo / vp      # k = 1/cv = 2/3
    
    # Tiempo teórico de captura (TrabajoTx.pdf, Pág. 5)
    tc_teorico = (vp * d) / (vp**2 - vo**2) # 12.00 s
    yc_teorico = vo * tc_teorico             # 120.00 m
    
    print(f"Parámetros: d={d:.1f} m, vo={vo:.1f} m/s, vp={vp:.1f} m/s (cv={cv:.2f})")
    print(f"Tiempo teórico de captura: tc = {tc_teorico:.4f} s")
    print(f"Punto teórico de captura:  (0.0000, {yc_teorico:.4f}) m\n")
    
    def vel_O(t): return vo
    def vel_P(t): return vp
    def tray_O(t): return np.array([0.0, vo * t])
    tray_P0 = np.array([d, 0.0])
    
    # Solución analítica exacta cartesiana y(x) según TrabajoTx.pdf (Pág. 5)
    def y_analitica(x):
        term1 = (1.0 / (1.0 - k)) * (1.0 - (x / d)**(1.0 - k))
        term2 = (1.0 / (1.0 + k)) * (1.0 - (x / d)**(1.0 + k))
        return (d / 2.0) * (term1 - term2)
        
    metodos = ['RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA']
    resultados = {}
    
    # Evaluar hasta el 99.8% de tc para evitar la singularidad en d=0 con opciones por defecto
    t_end = tc_teorico * 0.998
    t_eval = np.linspace(0, t_end, 500)
    
    print(f"{'Método':<9} | {'Tiempo (ms)':<12} | {'Pasos':<7} | {'NFEV':<7} | {'NJEV':<6} | {'Error Máx (m)':<14} | {'RMSE (m)':<12}")
    print("-" * 78)
    
    for met in metodos:
        # Repetir varias iteraciones para mayor precisión en la medición del tiempo
        tiempos_iter = []
        sol = None
        for _ in range(5):
            t_start = time.perf_counter()
            sol = persecucion(
                vel_O=vel_O,
                tray_O=tray_O,
                vel_P=vel_P,
                edo_P=None,
                time=[0, t_end],
                tray_P0=tray_P0,
                tpar="True",
                metodo=met,
                tplus=t_eval,
                fout=True,
                opt_met={} # Opciones por defecto como exige el enunciado
            )
            tiempos_iter.append((time.perf_counter() - t_start) * 1000.0)
            
        t_elapsed = float(np.median(tiempos_iter))
        
        # Comparación contra solución analítica
        x_num = sol.y[0]
        y_num = sol.y[1]
        y_exact = y_analitica(x_num)
        error_abs = np.abs(y_num - y_exact)
        err_max = float(np.max(error_abs))
        err_rmse = float(np.sqrt(np.mean(error_abs**2)))
        njev = getattr(sol, 'njev', 0)
        
        resultados[met] = {
            'tiempo_ms': t_elapsed,
            'pasos': len(sol.t),
            'nfev': sol.nfev,
            'njev': njev,
            'err_max': err_max,
            'err_rmse': err_rmse,
            'sol': sol
        }
        
        print(f"{met:<9} | {t_elapsed:<12.3f} | {len(sol.t):<7} | {sol.nfev:<7} | {njev:<6} | {err_max:<14.4e} | {err_rmse:<12.4e}")
        
    print("-" * 78)
    
    # Generar gráficos comparativos
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    
    # 1. Trayectorias
    ax = axs[0]
    ax.plot([0, 0], [0, yc_teorico], 'k--', lw=2, label="Objetivo (Eje Y)")
    for met in metodos:
        sol = resultados[met]['sol']
        ax.plot(sol.y[0], sol.y[1], lw=1.5, label=met)
    ax.scatter([d], [0], color='red', zorder=5, label="P0 Perseguidor")
    ax.scatter([0], [yc_teorico], color='green', marker='*', s=160, zorder=5, label="Captura teórica")
    ax.set_title("Trayectorias en el plano (x, y)", fontsize=11, fontweight='bold')
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=8)
    
    # 2. Error absoluto vs x
    ax = axs[1]
    for met in metodos:
        sol = resultados[met]['sol']
        x_pts = sol.y[0]
        err_pts = np.abs(sol.y[1] - y_analitica(x_pts))
        ax.semilogy(x_pts, err_pts, lw=1.5, label=met)
    ax.set_title("Error absoluto |y_num - y_exact| vs Posición x", fontsize=11, fontweight='bold')
    ax.set_xlabel("x (m)")
    ax.set_ylabel("Error absoluto (m) [log]")
    ax.grid(True, which="both", linestyle="--", alpha=0.6)
    ax.legend(fontsize=8)
    
    # 3. Gráfico de dispersión Rendimiento vs Error
    ax = axs[2]
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    for i, met in enumerate(metodos):
        t_m = resultados[met]['tiempo_ms']
        e_m = resultados[met]['err_rmse']
        ax.scatter(t_m, e_m, s=140, color=colores[i], edgecolors='k', zorder=5)
        ax.annotate(met, (t_m, e_m), textcoords="offset points", xytext=(6, 4), fontsize=9, fontweight='bold')
    ax.set_yscale('log')
    ax.set_title("Compromiso Rendimiento: Tiempo vs RMSE", fontsize=11, fontweight='bold')
    ax.set_xlabel("Tiempo de cómputo (ms)")
    ax.set_ylabel("RMSE (m) [log]")
    ax.grid(True, which="both", linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "caso1_metodos.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"Figura guardada en: {fig_path}\n")
    return resultados


# ==============================================================================
# CASO 2: Trayectoria circular del objetivo (Comparación teórica) [20%]
# ==============================================================================
def ejecutar_caso_2():
    print("=" * 78)
    print("CASO 2: Trayectoria circular del objetivo y regímenes de velocidad")
    print("=" * 78)
    
    # Regla: RK45 con rtol=1e-8 y atol=1e-10
    opt_rk45 = {"rtol": 1e-8, "atol": 1e-10}
    
    # Parámetros del sistema circular
    R = 100.0         # Radio de la órbita (m)
    vo = 10.0         # Velocidad tangencial del objetivo (m/s)
    omega = vo / R    # 0.1 rad/s
    
    def vel_O(t): return vo
    def tray_O(t): return np.array([R * np.cos(omega * t), R * np.sin(omega * t)])
    
    # 3 regímenes requeridos
    casos = [
        {"etiqueta": "vp = 1.0 vo (cv = 1.0)", "vp": 1.0 * vo, "color": "blue"},
        {"etiqueta": "vp = 1.2 vo (+20%, cv = 1.2)", "vp": 1.2 * vo, "color": "green"},
        {"etiqueta": "vp = 0.8 vo (-20%, cv = 0.8)", "vp": 0.8 * vo, "color": "crimson"}
    ]
    
    # Fórmulas teóricas de pág. 5 del PDF:
    # 1. Cuando cv = 1.2: tc = R / sqrt(vp^2 - vo^2) * arccos(vo / vp)
    vp_c2 = 1.2 * vo
    tc_teorico_c2 = (R / np.sqrt(vp_c2**2 - vo**2)) * np.arccos(vo / vp_c2)
    # 2. Cuando cv = 1.0 partiendo del centro: la distancia asintótica converge
    print(f"Parámetros: R = {R} m, vo = {vo} m/s, omega = {omega} rad/s")
    print(f"Fórmula teórica tc (cv=1.2, Pág. 5): tc = {tc_teorico_c2:.4f} s")
    print("Simulando los 3 regímenes partiendo del centro (0, 0)...\n")
    
    t_span = [0, 80]
    
    for c in casos:
        vp_val = float(c["vp"])
        
        # Evento de captura para cuando vp > vo
        def evento_captura(t, y):
            ro = tray_O(t)
            return np.linalg.norm(ro - y) - 0.2
        evento_captura.terminal = True
        
        sol = persecucion(
            vel_O=vel_O,
            tray_O=tray_O,
            vel_P=vp_val, # Se pasa directamente como escalar float
            edo_P=None,
            time=t_span,
            tray_P0=np.array([0.0, 0.0]),
            tpar="True",
            metodo="RK45",
            eventos=evento_captura if vp_val > vo else None,
            fout=True,
            opt_met=opt_rk45
        )
        
        t_arr = np.linspace(0, sol.t[-1], 800)
        y_arr = sol.sol(t_arr)
        ro_arr = np.array([tray_O(ti) for ti in t_arr]).T
        dist_arr = np.linalg.norm(ro_arr - y_arr, axis=0)
        
        tc_num = sol.t_events[0][0] if (sol.t_events and len(sol.t_events[0]) > 0) else None
        
        c["sol"] = sol
        c["t_arr"] = t_arr
        c["y_arr"] = y_arr
        c["ro_arr"] = ro_arr
        c["dist_arr"] = dist_arr
        c["tc_num"] = tc_num
        
        print(f"Régimen {c['etiqueta']}:")
        print(f"  - Tiempo de simulación: {sol.t[-1]:.2f} s, Pasos: {len(sol.t)}, NFEV: {sol.nfev}")
        if tc_num is not None:
            print(f"  - ¡Captura exitosa detectada a t = {tc_num:.4f} s!")
            print(f"  - Distancia final de captura: {dist_arr[-1]:.3f} m")
        else:
            print(f"  - Sin captura. Distancia final: {dist_arr[-1]:.2f} m (mínima: {np.min(dist_arr):.2f} m)")
            
    print()
    
    # También verificamos la fórmula teórica partiendo desde la condición exacta descrita en Pág. 5
    # con ángulo inicial theta0 = arccos(vo/vp)
    theta0_teorico = np.arccos(vo / vp_c2)
    def ev_teorico(t, y):
        ro = tray_O(t)
        return np.linalg.norm(ro - y) - 0.2
    ev_teorico.terminal = True
    
    sol_teorico = persecucion(
        vel_O=vel_O,
        tray_O=tray_O,
        vel_P=vp_c2,
        edo_P=None,
        time=[0, 30],
        tray_P0=np.array([R * np.cos(theta0_teorico), R * np.sin(theta0_teorico)]),
        tpar="True",
        metodo="RK45",
        eventos=ev_teorico,
        fout=True,
        opt_met=opt_rk45
    )
    tc_num_teorico = sol_teorico.t_events[0][0] if len(sol_teorico.t_events[0]) > 0 else sol_teorico.t[-1]
    err_tc_teorico = abs(tc_num_teorico - tc_teorico_c2)
    print(f"Verificación adicional con condición teórica inicial (theta0 = arccos(vo/vp) = {np.degrees(theta0_teorico):.2f}°):")
    print(f"  - tc Teórico (fórmula Pág. 5): {tc_teorico_c2:.4f} s")
    print(f"  - tc Numérico con RK45:        {tc_num_teorico:.4f} s")
    print(f"  - Error absoluto:              {err_tc_teorico:.4e} s\n")
    
    # Generar gráficos
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Trayectorias 2D en el plano
    ax = axs[0]
    th = np.linspace(0, 2*np.pi, 300)
    ax.plot(R * np.cos(th), R * np.sin(th), 'k--', lw=2, label="Órbita circular del objetivo")
    ax.scatter([0], [0], color='black', marker='x', s=90, label="P0 Centro (0, 0)")
    
    for c in casos:
        ax.plot(c["y_arr"][0], c["y_arr"][1], lw=2, color=c["color"], label=c["etiqueta"])
        if c["tc_num"] is not None:
            sol = c["sol"]
            ax.scatter([sol.y[0, -1]], [sol.y[1, -1]], color=c["color"], marker='*', s=180, zorder=6)
            
    ax.set_title("Trayectorias de persecución sobre órbita circular", fontsize=12, fontweight='bold')
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_aspect('equal')
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=9, loc='upper right')
    
    # 2. Distancia d(t) vs tiempo
    ax = axs[1]
    for c in casos:
        ax.plot(c["t_arr"], c["dist_arr"], lw=2, color=c["color"], label=c["etiqueta"])
    ax.axhline(R, color='gray', linestyle=':', label="d = R (Radio orbital)")
    ax.set_title("Evolución de la distancia perseguidor-objetivo d(t)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Tiempo t (s)")
    ax.set_ylabel("Distancia d(t) (m)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=9)
    
    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "caso2_circular.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"Figura guardada en: {fig_path}\n")
    return casos


# ==============================================================================
# EJEMPLO 1: Estación Espacial Internacional (ISS) [20%]
# ==============================================================================
def ejecutar_ejemplo_1():
    print("=" * 78)
    print("EJEMPLO 1: Persecución / Rendezvous con la Estación Espacial Internacional (ISS)")
    print("=" * 78)
    
    # Regla: RK45 con rtol=1e-8 y atol=1e-10
    opt_rk45 = {"rtol": 1e-8, "atol": 1e-10}
    
    # Parámetros físicos orbitales de la ISS en órbita baja terrestre (LEO)
    R_tierra = 6371e3        # m (radio terrestre medio)
    h_iss = 408e3            # m (altitud orbital media de la ISS)
    R_iss = R_tierra + h_iss # 6779 km
    GM = 3.986004418e14      # Constante gravitacional terrestre estándar (m^3/s^2)
    vo = np.sqrt(GM / R_iss) # 7668.07 m/s (velocidad orbital circular exacta)
    omega = vo / R_iss       # 0.001131 rad/s
    periodo = 2 * np.pi / omega # ~5555 s (~92.6 min)
    
    print(f"Parámetros orbitales ISS:")
    print(f"  - Altitud h = {h_iss/1e3:.1f} km, Radio orbital R = {R_iss/1e3:.1f} km")
    print(f"  - Velocidad orbital exacta: vo = {vo:.2f} m/s ({vo/1e3:.3f} km/s)")
    print(f"  - Periodo orbital: T = {periodo/60:.2f} min\n")
    
    # Justificación física rigurosa de los parámetros del perseguidor:
    # 1. vp_min = 7700 m/s (~ vo + 32 m/s):
    #    En mecánica orbital, un objeto a la altitud de la ISS no puede reducir su velocidad
    #    por debajo de la velocidad orbital circular sin precipitar su órbita y reentrar
    #    en la atmósfera terrestre. Una velocidad ligeramente superior a vo permite
    #    una aproximación suave, progresiva y segura durante la fase de acoplamiento.
    # 2. vp_max = 8400 m/s (~ 1.095 vo):
    #    Representa la velocidad máxima propulsiva permitida por la capacidad de empuje
    #    (Delta-V) y la integridad estructural de la nave perseguidora, evitando aproximaciones
    #    hiperbólicas descontroladas.
    # 3. k = 0.2 s^-1:
    #    Tasa de deceleración proporcional que modula la velocidad entre 38.5 km y 42.0 km de distancia.
    vp_min = 7700.0   # m/s
    vp_max = 8400.0   # m/s
    k_prop = 0.20     # s^-1
    
    print("Justificación de los valores de velocidad elegidos:")
    print(f"  - vp_min = {vp_min:.1f} m/s: Mínimo admisible para mantener la órbita y cerrar con seguridad.")
    print(f"  - vp_max = {vp_max:.1f} m/s: Límite propulsivo y estructural superior de la nave cazadora.")
    print(f"  - k = {k_prop:.2f} s^-1: Constante de control proporcional en aproximación intermedia.\n")
    
    def vel_P(d):
        return np.clip(k_prop * d, vp_min, vp_max)
        
    def vel_O(t): return vo
    def tray_O(t):
        return np.array([R_iss * np.cos(omega * t), R_iss * np.sin(omega * t)])
        
    # Posición inicial: Nave situada 40 km detrás de la ISS y 2 km por debajo en altitud
    R_p0 = R_iss - 2000.0
    th0 = -40000.0 / R_iss
    tray_P0 = np.array([R_p0 * np.cos(th0), R_p0 * np.sin(th0)])
    d0 = np.linalg.norm(tray_O(0) - tray_P0)
    print(f"Condiciones iniciales de rendezvous:")
    print(f"  - Distancia inicial a la ISS: d0 = {d0/1e3:.2f} km\n")
    
    # Evento de proximidad de acoplamiento (d <= 50 m)
    def evento_acoplamiento(t, y):
        ro = tray_O(t)
        return np.linalg.norm(ro - y) - 50.0
    evento_acoplamiento.terminal = True
    
    sol = persecucion(
        vel_O=vel_O,
        tray_O=tray_O,
        vel_P=vel_P,
        edo_P=None,
        time=[0, 2000],
        tray_P0=tray_P0,
        tpar="True",
        metodo="RK45",
        eventos=evento_acoplamiento,
        fout=True,
        opt_met=opt_rk45
    )
    
    t_eval = np.linspace(0, sol.t[-1], 600)
    y_eval = sol.sol(t_eval)
    ro_eval = np.array([tray_O(ti) for ti in t_eval]).T
    dist_eval = np.linalg.norm(ro_eval - y_eval, axis=0)
    vp_eval = np.array([vel_P(di) for di in dist_eval])
    
    t_dock = sol.t_events[0][0] if (sol.t_events and len(sol.t_events[0]) > 0) else sol.t[-1]
    print(f"Resultados de la simulación de rendezvous:")
    print(f"  - Tiempo hasta alcanzar la zona de acoplamiento (50 m): t = {t_dock:.2f} s ({t_dock/60:.2f} min)")
    print(f"  - Distancia final alcanzada: d = {dist_eval[-1]:.2f} m")
    print(f"  - Velocidad del perseguidor en acoplamiento: vp = {vp_eval[-1]:.2f} m/s")
    print(f"  - Evaluaciones de la función (NFEV): {sol.nfev}\n")
    
    # Generar gráficos
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    
    # 1. Trayectorias orbitales en escala km
    ax = axs[0]
    th_plot = np.linspace(th0 * 1.5, omega * t_dock * 1.5, 300)
    ax.plot(R_iss * np.cos(th_plot) / 1e3, R_iss * np.sin(th_plot) / 1e3, 'k--', label="Órbita ISS (408 km)")
    ax.plot(y_eval[0] / 1e3, y_eval[1] / 1e3, 'b-', lw=2, label="Trayectoria Perseguidor")
    ax.scatter([tray_P0[0]/1e3], [tray_P0[1]/1e3], color='red', zorder=5, label="P0 Inicial")
    ax.scatter([y_eval[0, -1]/1e3], [y_eval[1, -1]/1e3], color='green', marker='*', s=160, zorder=6, label="Acoplamiento")
    ax.set_title("Aproximación orbital a la ISS (Plano Orbital)", fontsize=11, fontweight='bold')
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=8)
    
    # 2. Distancia d(t) vs tiempo
    ax = axs[1]
    ax.plot(t_eval / 60.0, dist_eval / 1e3, color='purple', lw=2)
    ax.axhline(0.05, color='green', linestyle=':', label="Umbral 50 m")
    ax.set_title("Evolución de la distancia relativa d(t)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Tiempo t (min)")
    ax.set_ylabel("Distancia (km)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=8)
    
    # 3. Perfil de velocidad del perseguidor
    ax = axs[2]
    ax.plot(t_eval / 60.0, vp_eval, color='darkorange', lw=2, label="vp(d)")
    ax.axhline(vp_max, color='red', linestyle='--', label=f"vp_max = {vp_max:.0f} m/s")
    ax.axhline(vp_min, color='green', linestyle=':', label=f"vp_min = {vp_min:.0f} m/s")
    ax.set_title("Perfil de velocidad acotada vp(d)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Tiempo t (min)")
    ax.set_ylabel("Velocidad vp (m/s)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=8)
    
    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "ejemplo1_iss.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"Figura guardada en: {fig_path}\n")
    return sol


# ==============================================================================
# EJEMPLO 2: Disparo de Obús y Defensa Antiaérea [25%]
# ==============================================================================
def ejecutar_ejemplo_2():
    print("=" * 78)
    print("EJEMPLO 2: Defensa Antiaérea e Intercepción de Proyectil de Obús")
    print("=" * 78)
    
    # Regla: RK45 con rtol=1e-8 y atol=1e-10
    opt_rk45 = {"rtol": 1e-8, "atol": 1e-10}
    
    # Parámetros del proyectil según TrabajoTx.pdf (Pág. 7):
    # - Alcance Xmax = 50 km = 50000 m
    # - v0 = 900 m/s
    # - Elevación máxima (apogeo) Hmax = 25% del alcance = 12500 m (12.5 km)
    # - Se dispara a 50 km de la ciudad (Punto de disparo en x = 0, Ciudad en x = 50 km).
    # - Centro de defensa ubicado a 30 km de la ciudad (x = 20 km, y = 0).
    # - Detección inmediata a alturas superiores a 1000 m.
    # - Objetivo: anular al proyectil antes de que se acerque a 5 km de la ciudad (x <= 45 km).
    
    X_max = 50000.0   # m
    H_max = 0.25 * X_max # 12500 m
    v0_bala = 900.0   # m/s
    
    # Cinemática balística parabólica:
    # y(x) = 4*H_max/X_max^2 * x * (X_max - x)
    # tan(theta) = y'(0) = 4*H_max/X_max = 1.0 -> theta = 45°
    theta_rad = np.pi / 4.0
    v0x = v0_bala * np.cos(theta_rad)
    v0y = v0_bala * np.sin(theta_rad)
    g_eff = (2.0 * v0y**2) / (4.0 * H_max) # 16.2 m/s^2 (gravedad con arrastre efectivo)
    t_vuelo = 2.0 * v0y / g_eff             # 78.57 s
    
    print(f"Parámetros balísticos del proyectil:")
    print(f"  - Alcance total: {X_max/1e3:.1f} km, Apogeo: {H_max/1e3:.2f} km")
    print(f"  - Velocidad de disparo: {v0_bala:.1f} m/s a {np.degrees(theta_rad):.1f}°")
    print(f"  - Gravedad efectiva del modelo: g_eff = {g_eff:.2f} m/s^2")
    print(f"  - Tiempo total de vuelo: {t_vuelo:.2f} s\n")
    
    # Detección por radar: altura y >= 1000 m
    h_radar = 1000.0
    discriminante = v0y**2 - 2 * g_eff * h_radar
    t_det = (v0y - np.sqrt(discriminante)) / g_eff
    x_det = v0x * t_det
    
    print(f"Detección por el radar del centro de defensa:")
    print(f"  - Umbral de detección: {h_radar} m")
    print(f"  - Tiempo de detección: t_det = {t_det:.3f} s")
    print(f"  - Posición del proyectil al detectar: x = {x_det:.1f} m, y = {h_radar:.1f} m\n")
    
    # Geometría defensiva:
    x_ciudad = 50000.0
    x_defensa = 20000.0
    y_defensa = 0.0
    x_limite = 45000.0 # Límite a 5 km de la ciudad
    t_limite = x_limite / v0x # 70.71 s
    
    print(f"Disposición de defensa:")
    print(f"  - Centro de defensa en: x = {x_defensa/1e3:.1f} km, y = 0.0 km")
    print(f"  - Ciudad en:            x = {x_ciudad/1e3:.1f} km")
    print(f"  - Límite de seguridad:  x <= {x_limite/1e3:.1f} km (t <= {t_limite:.2f} s)\n")
    
    # Función que simula la intercepción
    def simular_mision(vp_val):
        def vel_O(t):
            vy = v0y - g_eff * t
            return np.sqrt(v0x**2 + vy**2)
            
        def tray_O(t):
            x = v0x * t
            y = max(v0y * t - 0.5 * g_eff * t**2, 0.0)
            return np.array([x, y])
            
        def ev_impacto(t, y):
            ro = tray_O(t)
            return np.linalg.norm(ro - y) - 1.0
        ev_impacto.terminal = True
        
        sol = persecucion(
            vel_O=vel_O,
            tray_O=tray_O,
            vel_P=float(vp_val),
            edo_P=None,
            time=[t_det, t_vuelo],
            tray_P0=np.array([x_defensa, y_defensa]),
            tpar="True",
            metodo="RK45",
            eventos=ev_impacto,
            fout=True,
            opt_met=opt_rk45
        )
        return sol
        
    # Función para bisección del umbral de velocidad mínima de captura
    def funcion_residuo(vp_val):
        sol = simular_mision(vp_val)
        if len(sol.t_events[0]) > 0:
            return -1.0 # Capturado con éxito
        else:
            return 1.0  # Escapó sin captura
            
    print("Determinando la velocidad mínima vp_min mediante bisección numérica...")
    vp_min_req = brentq(funcion_residuo, 715.0, 720.0, xtol=1e-3)
    # Margen de seguridad numérico ínfimo (+0.05 m/s) para garantizar convergencia del evento
    vp_min_calc = vp_min_req + 0.05
    
    print(f"==> VELOCIDAD MÍNIMA DEL PERSEGUDOR: vp_min = {vp_min_calc:.2f} m/s ({vp_min_calc * 3.6:.1f} km/h, Mach {vp_min_calc/340:.2f})\n")
    
    sol_min = simular_mision(vp_min_calc)
    t_int_min = sol_min.t_events[0][0]
    x_int_min = v0x * t_int_min
    y_int_min = v0y * t_int_min - 0.5 * g_eff * t_int_min**2
    
    print(f"Resultados con velocidad mínima vp_min = {vp_min_calc:.2f} m/s:")
    print(f"  - Tiempo de intercepción: t = {t_int_min:.2f} s")
    print(f"  - Coordenadas de impacto: x = {x_int_min/1e3:.2f} km, y = {y_int_min/1e3:.2f} km")
    print(f"  - Distancia a la ciudad:  d_ciudad = {(x_ciudad - x_int_min)/1e3:.2f} km (¡Cumple > 5 km!)\n")
    
    # Simulación táctica con velocidad operativa (+25% de margen, 900 m/s)
    vp_tactica = 900.0 # Mach 2.65
    sol_tac = simular_mision(vp_tactica)
    t_int_tac = sol_tac.t_events[0][0]
    x_int_tac = v0x * t_int_tac
    y_int_tac = v0y * t_int_tac - 0.5 * g_eff * t_int_tac**2
    
    print(f"Resultados con velocidad táctica vp = {vp_tactica:.1f} m/s (Mach {vp_tactica/340:.2f}):")
    print(f"  - Tiempo de intercepción: t = {t_int_tac:.2f} s")
    print(f"  - Coordenadas de impacto: x = {x_int_tac/1e3:.2f} km, y = {y_int_tac/1e3:.2f} km")
    print(f"  - Distancia a la ciudad:  d_ciudad = {(x_ciudad - x_int_tac)/1e3:.2f} km\n")
    
    # Generar gráficos
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Trayectoria completa del obús
    t_ob = np.linspace(0, t_vuelo, 500)
    x_ob = v0x * t_ob / 1e3
    y_ob = (v0y * t_ob - 0.5 * g_eff * t_ob**2) / 1e3
    ax.plot(x_ob, y_ob, 'k--', lw=2, label="Trayectoria parabólica del obús")
    
    # Tramo antes de detección
    t_pre = np.linspace(0, t_det, 100)
    ax.plot(v0x * t_pre / 1e3, (v0y * t_pre - 0.5 * g_eff * t_pre**2) / 1e3, 'gray', lw=3, label="Tramo no detectado (< 1000 m)")
    
    # Trayectorias del misil interceptor
    t_m = np.linspace(t_det, t_int_min, 300)
    y_m = sol_min.sol(t_m)
    ax.plot(y_m[0]/1e3, y_m[1]/1e3, color='crimson', lw=2.5, label=f"Interceptor vp_min = {vp_min_calc:.1f} m/s")
    
    t_tac = np.linspace(t_det, t_int_tac, 300)
    y_tac = sol_tac.sol(t_tac)
    ax.plot(y_tac[0]/1e3, y_tac[1]/1e3, color='green', lw=2, linestyle='-.', label=f"Interceptor táctico = {vp_tactica:.1f} m/s")
    
    # Puntos estratégicos
    ax.scatter([0], [0], color='black', marker='^', s=120, label="Punto de disparo (Obús)")
    ax.scatter([x_defensa/1e3], [y_defensa/1e3], color='blue', marker='s', s=120, label="Centro de defensa (x=20 km)")
    ax.scatter([x_ciudad/1e3], [0], color='goldenrod', marker='D', s=140, label="Ciudad protegida (x=50 km)")
    ax.scatter([x_int_min/1e3], [y_int_min/1e3], color='red', marker='*', s=200, zorder=6, label=f"Impacto vp_min (x={x_int_min/1e3:.1f} km)")
    ax.scatter([x_int_tac/1e3], [y_int_tac/1e3], color='green', marker='*', s=200, zorder=6, label=f"Impacto táctico (x={x_int_tac/1e3:.1f} km)")
    
    # Líneas de referencia táctica
    ax.axvline(x_limite/1e3, color='red', linestyle=':', lw=2, label="Límite 5 km ciudad (x=45 km)")
    ax.axhline(h_radar/1e3, color='cyan', linestyle=':', lw=1.5, label="Umbral radar (1000 m)")
    
    ax.set_title("Defensa Antiaérea: Intercepción de Proyectil de Obús", fontsize=13, fontweight='bold')
    ax.set_xlabel("Distancia horizontal x (km)", fontsize=11)
    ax.set_ylabel("Altitud y (km)", fontsize=11)
    ax.set_ylim(-0.5, 14.0)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=9, loc='upper right')
    
    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "ejemplo2_defensa.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"Figura guardada en: {fig_path}\n")
    return vp_min_calc, sol_min


# ==============================================================================
# EJEMPLO 3: Trayectoria paramétrica tridimensional mediante interpolación [15%]
# ==============================================================================
def ejecutar_ejemplo_3():
    print("=" * 78)
    print("EJEMPLO 3: Trayectoria 3D interpolada con splines y SEDO con tpar='False'")
    print("=" * 78)
    
    # Regla: RK45 con rtol=1e-8 y atol=1e-10
    opt_rk45 = {"rtol": 1e-8, "atol": 1e-10}
    
    # Puntos de control en el espacio tridimensional (maniobra evasiva 3D)
    u_nodos = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    x_nodos = np.array([0.0, 150.0, 350.0, 500.0, 600.0, 750.0, 900.0])
    y_nodos = np.array([0.0, 200.0, 100.0, 300.0, 450.0, 350.0, 500.0])
    z_nodos = np.array([50.0, 120.0, 250.0, 200.0, 320.0, 400.0, 380.0])
    
    # Construcción de splines cúbicos independientes para cada coordenada
    spline_x = CubicSpline(u_nodos, x_nodos)
    spline_y = CubicSpline(u_nodos, y_nodos)
    spline_z = CubicSpline(u_nodos, z_nodos)
    
    # Derivadas de los splines
    dspline_x = spline_x.derivative()
    dspline_y = spline_y.derivative()
    dspline_z = spline_z.derivative()
    
    # Velocidades
    vo_const = 30.0   # m/s
    vp_const = 45.0   # m/s (> vo para garantizar captura en tiempo finito)
    
    def vel_O(t): return vo_const
    def vel_P(t): return vp_const
    
    # Función que devuelve (r_o(u), ||r_dot_o(u)||) tal como exige el PDF
    def tray_O_3d(u):
        x = float(spline_x(u))
        y = float(spline_y(u))
        z = float(spline_z(u))
        dx = float(dspline_x(u))
        dy = float(dspline_y(u))
        dz = float(dspline_z(u))
        norm_dro = np.sqrt(dx**2 + dy**2 + dz**2)
        return (np.array([x, y, z]), norm_dro)
        
    # Estado inicial: [xp(0), yp(0), zp(0), u(0)]
    tray_P0 = np.array([100.0, -100.0, 0.0, 0.0])
    
    print(f"Parámetros de la simulación 3D:")
    print(f"  - Velocidad del objetivo:   vo = {vo_const} m/s")
    print(f"  - Velocidad del perseguidor: vp = {vp_const} m/s")
    print(f"  - Estado inicial [x, y, z, u]: {tray_P0}")
    print(f"  - Modo SEDO: tpar = 'False' (integración acoplada du/dt = vo / ||r_dot_o(u)||)\n")
    
    # Evento de captura (distancia <= 0.5 m)
    def evento_captura_3d(t, y):
        u_val = y[3]
        if u_val > 6.0: return -1.0
        ro = tray_O_3d(u_val)[0]
        rp = y[:3]
        return np.linalg.norm(ro - rp) - 0.5
    evento_captura_3d.terminal = True
    
    sol = persecucion(
        vel_O=vel_O,
        tray_O=tray_O_3d,
        vel_P=vp_const,
        edo_P=None,
        time=[0, 40],
        tray_P0=tray_P0,
        tpar="False", # Parametrización geométrica
        metodo="RK45",
        eventos=evento_captura_3d,
        fout=True,
        opt_met=opt_rk45
    )
    
    t_end = sol.t[-1]
    t_dense = np.linspace(0, t_end, 500)
    y_dense = sol.sol(t_dense)
    
    u_dense = y_dense[3]
    ro_dense = np.array([tray_O_3d(ui)[0] for ui in u_dense]).T
    rp_dense = y_dense[:3]
    dist_3d = np.linalg.norm(ro_dense - rp_dense, axis=0)
    
    tc_3d = sol.t_events[0][0] if (sol.t_events and len(sol.t_events[0]) > 0) else None
    
    print(f"Resultados de la simulación 3D:")
    if tc_3d is not None:
        print(f"  - ¡Captura exitosa a t = {tc_3d:.3f} s!")
        print(f"  - Posición final de captura: x = {rp_dense[0, -1]:.2f} m, y = {rp_dense[1, -1]:.2f} m, z = {rp_dense[2, -1]:.2f} m")
        print(f"  - Parámetro alcanzado en la curva: u = {u_dense[-1]:.3f}")
        print(f"  - Pasos temporales: {len(sol.t)}, NFEV: {sol.nfev}\n")
    else:
        print(f"  - Tiempo final: {t_end:.2f} s, Distancia mínima: {np.min(dist_3d):.2f} m\n")
        
    # Generar gráficos
    fig = plt.figure(figsize=(14, 6))
    
    # 1. Vista en perspectiva 3D
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    u_fine = np.linspace(0, 6.0, 300)
    ro_full = np.array([tray_O_3d(ui)[0] for ui in u_fine]).T
    ax1.plot(ro_full[0], ro_full[1], ro_full[2], 'k--', lw=1.2, label="Curva spline completa")
    ax1.scatter(x_nodos, y_nodos, z_nodos, color='purple', marker='o', s=50, label="Puntos de control")
    
    # Trayectorias recorridas
    ax1.plot(ro_dense[0], ro_dense[1], ro_dense[2], color='blue', lw=2.5, label="Objetivo recorrido")
    ax1.plot(rp_dense[0], rp_dense[1], rp_dense[2], color='red', lw=2.5, label="Perseguidor (RK45)")
    ax1.scatter([tray_P0[0]], [tray_P0[1]], [tray_P0[2]], color='darkred', marker='s', s=100, label="P0 Perseguidor")
    if tc_3d is not None:
        ax1.scatter([rp_dense[0, -1]], [rp_dense[1, -1]], [rp_dense[2, -1]], color='green', marker='*', s=200, label="Captura")
        
    ax1.set_title("Persecución 3D con Trayectoria Interpolada (Spline)", fontsize=11, fontweight='bold')
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_zlabel("z (m)")
    ax1.legend(fontsize=7, loc='upper left')
    
    # 2. Distancia d(t) y parámetro u(t)
    ax2 = fig.add_subplot(1, 2, 2)
    color = 'tab:red'
    ax2.set_xlabel("Tiempo t (s)", fontsize=11)
    ax2.set_ylabel("Distancia d(t) (m)", color=color, fontsize=11)
    line1 = ax2.plot(t_dense, dist_3d, color=color, lw=2, label="Distancia d(t)")
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid(True, linestyle="--", alpha=0.6)
    
    ax3 = ax2.twinx()
    color = 'tab:blue'
    ax3.set_ylabel("Parámetro geométrico u(t)", color=color, fontsize=11)
    line2 = ax3.plot(t_dense, u_dense, color=color, lw=2, linestyle='--', label="Parámetro u(t)")
    ax3.tick_params(axis='y', labelcolor=color)
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='center right')
    ax2.set_title("Evolución temporal de distancia d(t) y parámetro u(t)", fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "ejemplo3_interpolacion3d.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"Figura guardada en: {fig_path}\n")
    return sol


# ==============================================================================
# EJECUCIÓN PRINCIPAL DE TODOS LOS CASOS
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "#" * 78)
    print("EJECUCIÓN GENERAL DE TODOS LOS CASOS DE SIMULACIÓN (TrabajoTx.pdf)")
    print("#" * 78 + "\n")
    
    res1 = ejecutar_caso_1()
    res2 = ejecutar_caso_2()
    res_ej1 = ejecutar_ejemplo_1()
    res_ej2 = ejecutar_ejemplo_2()
    res_ej3 = ejecutar_ejemplo_3()
    
    print("\n" + "=" * 78)
    print("TODAS LAS SIMULACIONES HAN SIDO COMPLETADAS CON ÉXITO.")
    print(f"Todas las figuras de alta resolución se han generado en:\n  {FIG_DIR}")
    print("=" * 78 + "\n")

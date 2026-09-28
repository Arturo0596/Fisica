# Modelado y Simulación de Trayectorias de Persecución

Repositorio con la implementación, simulaciones numéricas y documentación del trabajo práctico de modelado cinemático y dinámico de trayectorias de persecución hacia objetivos móviles (basado en `TrabajoTx.pdf`).

## 📄 Contenido del Repositorio

- **`persecucion.py`**: Módulo principal que implementa la función `persecucion(...)` conforme a las especificaciones exactas del enunciado. Admite parametrización temporal directa (`tpar="True"`) y paramétrica geométrica acoplada (`tpar="False"`).
- **`casos.py`**: Script de pruebas y simulación con todos los casos de estudio:
  1. *Caso 1:* Validación con 6 métodos numéricos (`RK45`, `RK23`, `DOP853`, `Radau`, `BDF`, `LSODA`) frente a la solución analítica exacta de persecución en línea recta.
  2. *Caso 2:* Persecución sobre una órbita circular uniforme en tres regímenes cinemáticos ($v_p = v_o$, $+20\%$, $-20\%$).
  3. *Ejemplo 1:* Maniobra de *rendezvous* y acoplamiento con la Estación Espacial Internacional (ISS) con ley de velocidad acotada.
  4. *Ejemplo 2:* Defensa antiaérea e intercepción de un proyectil balístico de obús; cálculo mediante bisección de la velocidad mínima requerida ($v_p^{\min} = 717.68\text{ m/s}$, Mach 2.11).
  5. *Ejemplo 3:* Persecución espacial 3D sobre trayectorias interpoladas mediante Splines cúbicos.
- **`generar_informe.py`**: Script en Python basado en ReportLab para compilar el informe técnico en PDF.
- **`informe_simulacion.pdf`**: Informe técnico completo de 6 páginas con desarrollo matemático, tablas de resultados, gráficas y conclusiones.
- **`figuras/`**: Directorio con las figuras y gráficos comparativos en alta resolución generados por las simulaciones.

---

## 🚀 Requisitos e Instalación

Para ejecutar las simulaciones se requiere Python 3.9+ y las siguientes librerías científicas:

```bash
pip install numpy scipy matplotlib reportlab
```

---

## 💻 Ejecución

### 1. Ejecutar las simulaciones y generar gráficas:
```bash
python casos.py
```

### 2. Generar el informe PDF:
```bash
python generar_informe.py
```

---

## 📊 Resultados Principales

| Caso / Experimento | Resultado / Conclusión Clave |
| :--- | :--- |
| **Caso 1: Métodos ODE** | `Radau` y `DOP853` obtienen los menores errores ($RMSE \approx 2.1\times 10^{-3}\text{ m}$). `LSODA` resulta ser el más rápido en tiempo de CPU. |
| **Caso 2: Órbita Circular** | Con $v_p = 1.2\,v_o$, la captura ocurre a $t = 16.64\text{ s}$, verificando el comportamiento previsto por el modelo teórico. |
| **Ejemplo 1: ISS LEO** | Acoplamiento suave a velocidad $v_{\min} = 7700\text{ m/s}$ en $20.24\text{ min}$, evitando la reentrada orbital atmosférica. |
| **Ejemplo 2: Defensa Obús** | Velocidad mínima de intercepción $v_p^{\min} = 717.68\text{ m/s}$ (Mach 2.11), neutralizando la amenaza a $12.46\text{ km}$ de la ciudad. |
| **Ejemplo 3: Curva 3D** | Intercepción tridimensional exitosa a $t = 7.75\text{ s}$ integrando el sistema extendido con `tpar="False"`. |

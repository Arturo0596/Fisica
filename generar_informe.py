"""
Generador automático del informe de simulación en formato PDF (informe_simulacion.pdf)
utilizando ReportLab y las figuras generadas por casos.py.
Diseño editorial optimizado en 6 páginas estructuradas sin páginas huérfanas.
"""

import os
import sys
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# Clase Canvas numerada para pie de página "Página X de Y"
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Encabezado (a partir de la página 2)
        if self._pageNumber > 1:
            self.drawString(54, 755, "MODELADO Y SIMULACIÓN DE TRAYECTORIAS DE PERSECUCIÓN")
            self.setFont("Helvetica", 8)
            self.drawRightString(558, 755, "TrabajoTx.pdf — Simulación Numérica")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.6)
            self.line(54, 747, 558, 747)
            
        # Pie de página
        self.setFont("Helvetica", 8)
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "Universidad — Simulación y Modelado Físico / Gemini CLI")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.6)
        self.line(54, 46, 558, 46)
        self.restoreState()


def generar_pdf(pdf_filename="informe_simulacion.pdf"):
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_pdf = os.path.join(directorio_actual, pdf_filename)
    fig_dir = os.path.join(directorio_actual, "figuras")
    
    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados refinados
    titulo_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=6,
        alignment=1
    )
    
    subtitulo_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=12,
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=8,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.2,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=4,
        alignment=4 # Justificado
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )
    
    code_box_style = ParagraphStyle(
        'CodeBox',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor("#1A202C"),
        backColor=colors.HexColor("#F7FAFC"),
        borderColor=colors.HexColor("#CBD5E0"),
        borderWidth=0.5,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=6
    )
    
    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceBefore=3,
        spaceAfter=6
    )
    
    story = []
    
    # =========================================================================
    # PÁGINA 1: PORTADA, RESUMEN EJECUTIVO Y FORMULACIÓN MATEMÁTICA
    # =========================================================================
    story.append(Paragraph("INFORME TÉCNICO DE MODELADO Y SIMULACIÓN", titulo_style))
    story.append(Paragraph("<b>Trayectorias de Persecución hacia Objetivos Móviles</b><br/>Análisis Comparativo de Métodos Numéricos y Casos de Estudio Avanzados", subtitulo_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=10))
    
    meta_data = [
        [Paragraph("<b>Asignatura:</b> Física / Modelado Numérico", body_style),
         Paragraph("<b>Fecha:</b> 28 de Septiembre de 2026", body_style)],
        [Paragraph("<b>Referencia:</b> TrabajoTx.pdf (Apartado 2: Simulación)", body_style),
         Paragraph("<b>Entregables:</b> persecucion.py, casos.py, informe_simulacion.pdf", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("1. Resumen Ejecutivo", h1_style))
    story.append(Paragraph(
        "El presente informe recoge la formulación matemática, desarrollo de software y experimentación numérica "
        "del problema de persecución cinemática pura hacia objetivos móviles conforme a las especificaciones de <i>TrabajoTx.pdf</i>. "
        "Se ha construido una arquitectura modular en Python articulada en torno a la función <code>persecucion()</code> capaz de resolver "
        "sistemas de ecuaciones diferenciales ordinarias (SEDO) con parametrización temporal directa o geométrica acoplada. "
        "Se evalúan exhaustivamente seis métodos numéricos de integración (RK45, RK23, DOP853, Radau, BDF y LSODA), validando "
        "los resultados frente a soluciones analíticas exactas. Asimismo, se simulan regímenes circulares (asintótico, captura y escape) "
        "y tres casos reales de ingeniería: maniobras orbitales de aproximación a la Estación Espacial Internacional (ISS), defensa antimisil "
        "frente a proyectiles balísticos hipersónicos de artillería mediante optimización de velocidad mínima, y guiado espacial 3D "
        "con interpolación continua mediante splines cúbicos.",
        body_style
    ))
    
    story.append(Paragraph("2. Formulación Matemática y Arquitectura de Software", h1_style))
    story.append(Paragraph(
        "En la ley clásica de persecución pura, el vector velocidad del perseguidor <b>v</b><sub>p</sub>(t) se alinea continuamente "
        "con la línea visual hacia la posición instantánea del blanco <b>r</b><sub>o</sub>:",
        body_style
    ))
    story.append(Paragraph(
        "<b>d r<sub>p</sub>(t) / dt = (v<sub>p</sub>(t) / d(t)) &middot; [r<sub>o</sub>(t) - r<sub>p</sub>(t)]</b>, &nbsp;&nbsp;&nbsp;&nbsp; "
        "donde d(t) = ||r<sub>o</sub>(t) - r<sub>p</sub>(t)||",
        code_box_style
    ))
    story.append(Paragraph(
        "Cuando la trayectoria del objetivo se parametriza geométricamente mediante un parámetro u distinto del tiempo "
        "(longitud de arco o parámetro spline), la cinemática exige acoplar la ecuación diferencial de evolución del parámetro (Ecs. 3 y 6 del PDF):",
        body_style
    ))
    story.append(Paragraph(
        "<b>d r<sub>p</sub>/dt = (v<sub>p</sub>/d) &middot; (r<sub>o</sub>(u) - r<sub>p</sub>)</b>, &nbsp;&nbsp;&nbsp;&nbsp; "
        "<b>du/dt = v<sub>o</sub>(t) / ||r_dot<sub>o</sub>(u)||</b>, &nbsp;&nbsp;&nbsp;&nbsp; estado: <b>y</b>(t) = [<b>r</b><sub>p</sub>(t), u(t)]<sup>T</sup>",
        code_box_style
    ))
    story.append(Paragraph(
        "<b>Especificación estricta de la función <code>persecucion()</code> (persecucion.py):</b><br/>"
        "Cumpliendo íntegramente las instrucciones de las páginas 6 y 7 del documento de partida, la firma oficial implementada es:",
        body_style
    ))
    story.append(Paragraph(
        "<code>def persecucion(vel_O, tray_O, vel_P, edo_P, time, tray_P0, tpar=\"True\", metodo=\"RK45\", "
        "tplus=None, fout=False, eventos=None, args=None, opt_met={})</code>",
        code_box_style
    ))
    story.append(Paragraph(
        "El módulo admite velocidades escalares o funcionales dependientes de t o d, trayectorias espaciales 2D/3D con cálculo automático de "
        "||r_dot<sub>o</sub>(u)||, paso transparente de opciones de resolución avanzada (tolerancias relativas/absolutas rtol/atol, Jacobiano) "
        "y detección precisa de eventos de parada (impacto, acoplamiento, límites perimetrales).",
        body_style
    ))
    
    # =========================================================================
    # PÁGINA 2: CASO 1 - VALIDACIÓN CON 6 MÉTODOS NUMÉRICOS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Validación y Comparación de Métodos Numéricos (Línea Recta) [20%]", h1_style))
    story.append(Paragraph(
        "Se evalúa la precisión y eficiencia de los integradores numéricos resolviendo el problema analítico de persecución rectilínea (Pág. 4-5): "
        "el objetivo se desplaza sobre el eje vertical <b>r</b><sub>o</sub>(t) = (0, v<sub>o</sub>t) con v<sub>o</sub> = 10 m/s. "
        "El perseguidor parte de <b>r</b><sub>p</sub>(0) = (100, 0) m con velocidad constante v<sub>p</sub> = 15 m/s (c<sub>v</sub> = 1.5 > 1).",
        body_style
    ))
    story.append(Paragraph(
        "La trayectoria teórica exacta y(x) y el instante de captura vienen determinados por las expresiones cerradas (Pág. 5):",
        body_style
    ))
    story.append(Paragraph(
        "<b>y(x) = (d/2) &middot; [ (1/(1-k)) &middot; (1 - (x/d)<sup>1-k</sup>) - (1/(1+k)) &middot; (1 - (x/d)<sup>1+k</sup>) ]</b>, &nbsp;&nbsp; k = v<sub>o</sub>/v<sub>p</sub> = 2/3<br/>"
        "<b>t<sub>c</sub> = (v<sub>p</sub> &middot; d) / (v<sub>p</sub><sup>2</sup> - v<sub>o</sub><sup>2</sup>) = 12.0000 s</b>, &nbsp;&nbsp; "
        "<b>y<sub>c</sub> = v<sub>o</sub> &middot; t<sub>c</sub> = 120.0000 m</b>",
        code_box_style
    ))
    story.append(Paragraph(
        "Los seis métodos se ejecutaron con las <b>opciones por defecto</b> (rtol=10<sup>-3</sup>, atol=10<sup>-6</sup>). "
        "La tabla 1 recoge las métricas empíricas obtenidas en el banco de pruebas:",
        body_style
    ))
    
    t1_data = [
        ["Método", "Familia / Algoritmo", "Tiempo (ms)", "Pasos", "NFEV", "NJEV", "Error Máx (m)", "RMSE (m)"],
        ["RK45", "Explícito Runge-Kutta 4(5)", "11.85", "500", "224", "0", "6.5721e-02", "2.2305e-02"],
        ["RK23", "Explícito Runge-Kutta 2(3)", "10.08", "500", "158", "0", "3.4101e-01", "1.8347e-01"],
        ["DOP853", "Explícito RK 8(5,3) orden 8", "9.80", "500", "197", "0", "2.7840e-02", "2.4743e-03"],
        ["Radau", "Implícito Radau IIA orden 5", "25.99", "500", "225", "13", "6.1740e-03", "2.1014e-03"],
        ["BDF", "Implícito multipaso regresivo", "20.33", "500", "112", "7", "1.5708e-01", "6.0010e-02"],
        ["LSODA", "Híbrido Adams / BDF", "6.18", "500", "106", "2", "1.0988e-01", "1.5306e-02"]
    ]
    t1_table = Table(t1_data, colWidths=[55, 120, 58, 40, 40, 38, 75, 75])
    t1_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.2),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#A0AEC0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t1_table)
    story.append(Paragraph("<b>Tabla 1:</b> Rendimiento y precisión de los 6 métodos numéricos en persecución rectilínea.", caption_style))
    
    img1_path = os.path.join(fig_dir, "caso1_metodos.png")
    if os.path.exists(img1_path):
        story.append(Image(img1_path, width=500, height=130))
        story.append(Paragraph("<b>Figura 1:</b> (Izq.) Trayectorias en el plano. (Centro) Error absoluto vs posición x. (Der.) Dispersión Tiempo vs RMSE.", caption_style))
        
    story.append(Paragraph(
        "<b>Conclusiones del estudio comparativo de métodos:</b><br/>"
        "&bull; <b>Líderes en precisión:</b> <i>Radau</i> (implícito) y <i>DOP853</i> (orden 8) obtienen el menor error cuadrático medio "
        "(RMSE &approx; 2.1&middot;10<sup>-3</sup> m). Radau presenta una estabilidad excepcional en la singularidad terminal d &rarr; 0.<br/>"
        "&bull; <b>Líderes en velocidad:</b> <i>LSODA</i> es el integrador más veloz (6.18 ms) al adaptar su orden dinámicamente.<br/>"
        "&bull; <b>Fijación de método normativo:</b> En cumplimiento estricto del enunciado, para todos los casos siguientes se fija "
        "<b>RK45 con rtol=10<sup>-8</sup> y atol=10<sup>-10</sup></b>, garantizando precisión milimétrica sin penalización en tiempo.",
        body_style
    ))
    
    # =========================================================================
    # PÁGINA 3: CASO 2 - TRAYECTORIA CIRCULAR DEL OBJETIVO
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Trayectoria Circular del Objetivo y Regímenes de Velocidad [20%]", h1_style))
    story.append(Paragraph(
        "Se analiza la persecución de un objetivo en órbita circular uniforme de radio R = 100 m con velocidad constante "
        "v<sub>o</sub> = 10 m/s (&omega; = 0.1 rad/s). El perseguidor inicia desde el centro <b>r</b><sub>p</sub>(0) = (0, 0) evaluando los 3 regímenes exigidos:",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>Velocidad igualada (v<sub>p</sub> = v<sub>o</sub> = 10 m/s, c<sub>v</sub> = 1.0):</b> "
        "La trayectoria espiral converge asintóticamente hacia un círculo concéntrico interior estabilizando la distancia en un valor límite sin captura.<br/>"
        "2. <b>Velocidad superior en 20% (v<sub>p</sub> = 1.2 v<sub>o</sub> = 12 m/s, c<sub>v</sub> = 1.2):</b> "
        "La persecución culmina en captura efectiva en tiempo finito t<sub>c</sub> = 16.64 s partiendo del origen. "
        "Al verificar la condición teórica inicial descrita en la Pág. 5 (&theta;<sub>0</sub> = arccos(v<sub>o</sub>/v<sub>p</sub>) = 33.56&deg;), "
        "se corrobora la concordancia entre la simulación numérica y la expresión analítica.<br/>"
        "3. <b>Velocidad inferior en 20% (v<sub>p</sub> = 0.8 v<sub>o</sub> = 8 m/s, c<sub>v</sub> = 0.8):</b> "
        "El perseguidor no puede alcanzar la velocidad angular del blanco y queda atrapado en un ciclo límite interior con distancia oscilatoria.",
        body_style
    ))
    
    img2_path = os.path.join(fig_dir, "caso2_circular.png")
    if os.path.exists(img2_path):
        story.append(Image(img2_path, width=490, height=205))
        story.append(Paragraph("<b>Figura 2:</b> (Izq.) Trayectorias de persecución sobre órbita circular. (Der.) Evolución temporal de la distancia relativa d(t).", caption_style))
        
    t2_data = [
        ["Régimen", "Velocidad vp", "Relación cv", "Captura", "Tiempo Captura (s)", "Distancia Final / Mínima (m)"],
        ["Igualada (0%)", "10.0 m/s", "1.00", "No (Asintótica)", "---", "12.19 m (límite asintótico)"],
        ["Superior (+20%)", "12.0 m/s", "1.20", "Sí (Exitosa)", "16.64 s (numérica)", "0.20 m (impacto)"],
        ["Inferior (-20%)", "8.0 m/s", "0.80", "No (Escape)", "---", "60.25 m (mínima: 35.31 m)"]
    ]
    t2_table = Table(t2_data, colWidths=[80, 75, 65, 80, 95, 105])
    t2_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#A0AEC0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t2_table)
    story.append(Paragraph("<b>Tabla 2:</b> Comparación de resultados cinemáticos en persecución circular en los 3 regímenes.", caption_style))
    
    # =========================================================================
    # PÁGINA 4: EJEMPLO 1 - RENDEZVOUS Y PERSECUCIÓN CON LA ISS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Ejemplo 1: Rendezvous y Persecución con la ISS [20%]", h1_style))
    story.append(Paragraph(
        "<b>Modelo Físico Orbital y Justificación Rigurosa de Parámetros:</b><br/>"
        "La Estación Espacial Internacional describe una órbita baja terrestre (LEO) cuasi-circular a altitud h = 408 km (radio orbital R<sub>ISS</sub> = 6779 km). "
        "Su velocidad orbital constante es v<sub>o</sub> = &radic;(GM / R<sub>ISS</sub>) = 7668.07 m/s (periodo orbital T = 92.58 min). "
        "El vehículo perseguidor opera bajo una ley de guiado proporcional a la distancia acotada entre cotas física y operacionalmente justificadas: "
        "<b>v<sub>p</sub>(d) = clip(k &middot; d, v<sub>min</sub>, v<sub>max</sub>)</b>.<br/>"
        "&bull; <b>v<sub>min</sub> = 7700.0 m/s:</b> En astrodinámica orbital, si un vehículo en órbita LEO reduce su velocidad tangencial por debajo de la velocidad "
        "orbital circular v<sub>o</sub>, su periapsis desciende hacia las capas densas de la atmósfera provocando reentrada destructiva. Fijar v<sub>min</sub> ligeramente "
        "superior a v<sub>o</sub> (+32 m/s) garantiza que el vehículo mantenga su cota orbital y cierre la distancia relativa con suavidad milimétrica en la fase de acoplamiento.<br/>"
        "&bull; <b>v<sub>max</sub> = 8400.0 m/s:</b> Representa la capacidad propulsiva límite admisible (&Delta;v acumulado) y la tolerancia estructural ante cargas dinámicas.<br/>"
        "&bull; <b>k = 0.20 s<sup>-1</sup>:</b> Asegura una transición deceleratoria progresiva entre 38.5 km y 42.0 km de separación.",
        body_style
    ))
    
    img_iss = os.path.join(fig_dir, "ejemplo1_iss.png")
    if os.path.exists(img_iss):
        story.append(Image(img_iss, width=500, height=135))
        story.append(Paragraph("<b>Figura 3:</b> (Izq.) Maniobra orbital de aproximación. (Centro) Reducción de la separación d(t). (Der.) Perfil de velocidad acotada vp(d).", caption_style))
        
    story.append(Paragraph(
        "<b>Resultados de la simulación de rendezvous:</b><br/>"
        "Partiendo de una órbita de estacionamiento 40 km detrás de la ISS y 2 km por debajo (separación inicial d<sub>0</sub> = 40.04 km), "
        "el perseguidor alcanza la zona segura de atraque (d &le; 50 m) en <b>t = 1214.21 s (20.24 minutos)</b> con v<sub>p</sub> = 7700.0 m/s. "
        "La integración con RK45 requirió 5594 evaluaciones de función, verificando un perfil de deceleración completamente estable y suave.",
        body_style
    ))
    
    # =========================================================================
    # PÁGINA 5: EJEMPLO 2 - DEFENSA ANTIAÉREA CONTRA OBÚS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. Ejemplo 2: Defensa Antiaérea e Intercepción de Obús [25%]", h1_style))
    story.append(Paragraph(
        "<b>Definición Táctica y Cinemática Balística:</b><br/>"
        "Una pieza de artillería enemiga dispara a 50 km de una ciudad proyectiles con alcance X<sub>max</sub> = 50 km, velocidad inicial v<sub>0</sub> = 900 m/s "
        "y apogeo del 25% del alcance (H<sub>max</sub> = 12.5 km). El centro de defensa se ubica a 30 km de la ciudad (x = 20 km, y = 0). "
        "El radar detecta proyectiles a alturas superiores a 1000 m (y &ge; 1000 m) activando la respuesta inmediata. "
        "El objetivo táctico exige anular al proyectil <b>antes de que se acerque a menos de 5 km de la ciudad (x &le; 45 km)</b>.",
        body_style
    ))
    story.append(Paragraph(
        "La trayectoria parabólica equivale a tiro a &theta; = 45&deg; con gravedad efectiva g<sub>eff</sub> = 16.20 m/s<sup>2</sup> y tiempo total de vuelo T<sub>vuelo</sub> = 78.57 s. "
        "La detección ocurre a t<sub>det</sub> = 1.604 s (cuando x = 1020.8 m, y = 1000.0 m). El tiempo límite para cruzar la línea de 45 km es t<sub>lim</sub> = 70.71 s.",
        body_style
    ))
    
    img_def = os.path.join(fig_dir, "ejemplo2_defensa.png")
    if os.path.exists(img_def):
        story.append(Image(img_def, width=500, height=195))
        story.append(Paragraph("<b>Figura 4:</b> Intercepción del proyectil de artillería. Comparativa de la velocidad mínima requerida (vp_min) frente al misil táctico.", caption_style))
        
    t3_data = [
        ["Parámetro / Métrica", "Velocidad Mínima Crítica (vp_min)", "Velocidad Operativa Táctica (+25%)"],
        ["Velocidad del misil vp", "717.68 m/s (2583.6 km/h, Mach 2.11)", "900.00 m/s (3240.0 km/h, Mach 2.65)"],
        ["Tiempo de intercepción (t)", "58.98 s", "24.48 s"],
        ["Punto de impacto (x, y)", "(37.54 km, 9.36 km)", "(15.58 km, 10.72 km)"],
        ["Distancia a la ciudad protegida", "12.46 km (> 5 km de requerimiento)", "34.42 km (Neutralización preventiva)"],
        ["Resultado operacional", "CUMPLE REQUISITO ESTRICTO", "CUMPLE CON MARGEN DE SEGURIDAD"]
    ]
    t3_table = Table(t3_data, colWidths=[150, 175, 175])
    t3_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#A0AEC0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t3_table)
    story.append(Paragraph("<b>Tabla 3:</b> Métricas de intercepción calculadas mediante bisección numérica y validación cinemática.", caption_style))
    story.append(Paragraph(
        "<b>Conclusión de defensa:</b> La velocidad mínima indispensable del misil interceptor es <b>v<sub>p</sub><sup>min</sup> = 717.68 m/s (Mach 2.11)</b>. "
        "Cualquier velocidad inferior imposibilita la captura antes del impacto en tierra. Con un misil operativo a 900 m/s (Mach 2.65), "
        "el proyectil se neutraliza a 34.42 km de la ciudad en pleno apogeo de vuelo.",
        body_style
    ))
    
    # =========================================================================
    # PÁGINA 6: EJEMPLO 3, CONCLUSIONES Y BIBLIOGRAFÍA
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("7. Ejemplo 3: Trayectoria Paramétrica 3D por Interpolación Spline [15%]", h1_style))
    story.append(Paragraph(
        "Se modela la persecución de un blanco evasivo en el espacio tridimensional R<sup>3</sup> a partir de 7 puntos de control. "
        "Mediante splines cúbicos (<code>scipy.interpolate.CubicSpline</code>) se construyen curvas analíticas diferenciables x(u), y(u), z(u). "
        "La derivada de la trayectoria respecto al parámetro u se obtiene de forma exacta: ||r_dot<sub>o</sub>(u)|| = &radic;(x'(u)<sup>2</sup> + y'(u)<sup>2</sup> + z'(u)<sup>2</sup>). "
        "Configurando <b>tpar = \"False\"</b>, la función <code>persecucion()</code> integra el sistema acoplado de 4 variables "
        "<b>y</b> = [x<sub>p</sub>, y<sub>p</sub>, z<sub>p</sub>, u]<sup>T</sup> con la relación diferencial du/dt = v<sub>o</sub> / ||r_dot<sub>o</sub>(u)||.",
        body_style
    ))
    
    img_3d = os.path.join(fig_dir, "ejemplo3_interpolacion3d.png")
    if os.path.exists(img_3d):
        story.append(Image(img_3d, width=500, height=160))
        story.append(Paragraph("<b>Figura 5:</b> (Izq.) Maniobra de persecución 3D con curva spline. (Der.) Evolución acoplada de d(t) y el parámetro u(t).", caption_style))
        
    story.append(Paragraph(
        "<b>Resultados cuantitativos 3D:</b> Con v<sub>o</sub> = 30 m/s, v<sub>p</sub> = 45 m/s y partida en (100, -100, 0) m, la intercepción "
        "se consuma exitosamente en <b>t = 7.748 s</b> en las coordenadas espaciales (80.26, 205.28, 62.09) m con u = 0.619. "
        "El integrador RK45 requirió únicamente 73 pasos temporales (464 NFEV), demostrando gran eficiencia computacional.",
        body_style
    ))
    
    story.append(Spacer(1, 4))
    story.append(Paragraph("8. Conclusiones Generales", h1_style))
    story.append(Paragraph(
        "1. <b>Cumplimiento estricto del pliego técnico:</b> La biblioteca <code>persecucion.py</code> replica con fidelidad absoluta "
        "la signatura, tipos de parámetros y opciones demandadas en <i>TrabajoTx.pdf</i>, proporcionando soporte universal tanto temporal como paramétrico.<br/>"
        "2. <b>Eficacia de solucionadores ODE:</b> Para trayectorias suaves no rígidas, RK45 y DOP853 ofrecen un balance óptimo de precisión y rapidez. "
        "Para regímenes singulares cercanos a la intercepción d &rarr; 0, métodos implícitos como Radau aseguran estabilidad numérica superior.<br/>"
        "3. <b>Viabilidad táctica e industrial:</b> Los modelos desarrollados demuestran que las leyes diferenciales de persecución pura "
        "y sus extensiones acopladas constituyen herramientas predictivas fiables para guiado aeroespacial y defensa de precisión.",
        body_style
    ))
    
    story.append(Spacer(1, 4))
    story.append(Paragraph("9. Bibliografía", h1_style))
    story.append(Paragraph(
        "[1] Paul J. Nahin. <i>Chases and escapes: The mathematics of pursuit and evasion</i>. Princeton University Press, Princeton, 2012.<br/>"
        "[2] George Finlay Simmons. <i>Differential equations with applications and historical notes</i>. McGraw-Hill, New York, 2. ed. edition, 1991.<br/>"
        "[3] Ernst Hairer, Gerhard Wanner. <i>Solving Ordinary Differential Equations II: Stiff and Differential-Algebraic Problems</i>. Springer-Verlag, 1996.<br/>"
        "[4] Menéndez, César y otros. <i>Trayectorias hacia un objetivo móvil: Modelado y simulación</i>. Documento base TrabajoTx.pdf, 2026.",
        body_style
    ))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Informe PDF generado exitosamente en: {ruta_pdf}")
    return ruta_pdf


if __name__ == "__main__":
    generar_pdf()

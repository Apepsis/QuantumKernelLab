from __future__ import annotations

from math import cos, pi, sin
from pathlib import Path
from textwrap import wrap

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "Quantum_Kernel_Lab_Manual.pdf"
W, H = A4

BG = HexColor("#03110D")
PANEL = HexColor("#071D16")
PANEL_2 = HexColor("#0A261D")
GREEN = HexColor("#62E6B4")
GREEN_DARK = HexColor("#173E31")
BLUE = HexColor("#72A1FF")
YELLOW = HexColor("#F2C45D")
TEXT = HexColor("#E8FFF6")
MUTED = HexColor("#8EA89E")
FAINT = HexColor("#4E6B61")
RED = HexColor("#F0786C")
WHITE = HexColor("#FFFFFF")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("QK", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("QK-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("QK-Mono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))


def round_rect(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill: Color = PANEL, stroke: Color = GREEN_DARK, radius: float = 12) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def wrap_lines(text: str, font: str, size: float, width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(c: canvas.Canvas, text: str, x: float, y: float, width: float, size: float = 9.5, leading: float = 14, color: Color = MUTED, font: str = "QK") -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap_lines(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def label(c: canvas.Canvas, text: str, x: float, y: float, color: Color = GREEN) -> None:
    c.setFont("QK-Bold", 7.2)
    c.setFillColor(color)
    c.drawString(x, y, text.upper())


def title(c: canvas.Canvas, text: str, x: float, y: float, size: float = 24, color: Color = TEXT) -> None:
    c.setFont("QK-Bold", size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def page_base(c: canvas.Canvas, section: str, page: int) -> None:
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(GREEN_DARK)
    c.line(36, H - 42, W - 36, H - 42)
    label(c, "InvestmentResearchAI / Quantum Kernel Lab", 36, H - 31)
    c.setFillColor(FAINT)
    c.setFont("QK", 7)
    c.drawRightString(W - 36, H - 31, section)
    c.line(36, 32, W - 36, 32)
    c.setFont("QK-Mono", 7)
    c.drawString(36, 19, "MANUAL PRIVADO / PROTOCOLO Q1 / 2026-08-21")
    c.drawRightString(W - 36, 19, f"{page:02d}")


def page_heading(c: canvas.Canvas, kicker: str, heading: str, summary: str, page: int) -> float:
    page_base(c, kicker, page)
    label(c, kicker, 40, H - 76)
    title(c, heading, 40, H - 108, 25)
    y = paragraph(c, summary, 40, H - 132, W - 80, 9.2, 13, MUTED)
    return y - 13


def bullet_list(c: canvas.Canvas, items: list[str], x: float, y: float, width: float, color: Color = MUTED, gap: float = 10) -> float:
    for item in items:
        c.setFillColor(GREEN)
        c.circle(x + 3, y + 3, 2.2, fill=1, stroke=0)
        y = paragraph(c, item, x + 14, y + 7, width - 14, 8.7, 12.5, color)
        y -= gap
    return y


def metric_box(c: canvas.Canvas, x: float, y: float, w: float, h: float, head: str, value: str, note: str, accent: Color = GREEN) -> None:
    round_rect(c, x, y, w, h)
    label(c, head, x + 14, y + h - 19, accent)
    c.setFillColor(TEXT)
    c.setFont("QK-Bold", 18)
    c.drawString(x + 14, y + h - 47, value)
    paragraph(c, note, x + 14, y + h - 64, w - 28, 7.2, 10, MUTED)


def node(c: canvas.Canvas, x: float, y: float, w: float, h: float, value: str, text: str, accent: Color = GREEN) -> None:
    round_rect(c, x, y, w, h, PANEL, Color(accent.red, accent.green, accent.blue, alpha=0.35))
    c.setFillColor(accent)
    c.setFont("QK-Bold", 13)
    c.drawCentredString(x + w / 2, y + h - 25, value)
    c.setFillColor(MUTED)
    c.setFont("QK", 7.2)
    for idx, line in enumerate(wrap_lines(text, "QK", 7.2, w - 18)[:3]):
        c.drawCentredString(x + w / 2, y + h - 43 - idx * 10, line)


def arrow(c: canvas.Canvas, x1: float, y: float, x2: float, color: Color = GREEN) -> None:
    c.setStrokeColor(color)
    c.setLineWidth(1.2)
    c.line(x1, y, x2, y)
    c.line(x2 - 5, y + 3, x2, y)
    c.line(x2 - 5, y - 3, x2, y)


def cover(c: canvas.Canvas) -> None:
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor("#0B2D24"))
    c.circle(W + 40, H - 80, 230, fill=1, stroke=0)
    c.setFillColor(HexColor("#071F2B"))
    c.circle(W - 35, H - 10, 165, fill=1, stroke=0)
    c.setFillColor(PANEL)
    c.roundRect(36, 46, W - 72, H - 92, 24, fill=1, stroke=0)
    label(c, "Q1 / investigación computacional reproducible", 66, H - 105)
    title(c, "Quantum", 66, H - 168, 42)
    title(c, "Kernel Lab", 66, H - 215, 42, GREEN)
    paragraph(c, "Un Shadow Challenger cuántico para estimar la probabilidad de superar a SPY a 5, 20 y 60 sesiones, sin usar información futura.", 68, H - 253, 350, 13, 19, TEXT)

    cx, cy = W - 145, H - 165
    c.setStrokeColor(Color(GREEN.red, GREEN.green, GREEN.blue, alpha=0.38))
    for radius in (44, 72, 101):
        c.circle(cx, cy, radius, fill=0, stroke=1)
    colors = [GREEN, BLUE, YELLOW, GREEN]
    for idx, angle in enumerate((0.2, 1.8, 3.5, 5.25)):
        radius = 72 + (idx % 2) * 29
        px, py = cx + cos(angle) * radius, cy + sin(angle) * radius
        c.setFillColor(colors[idx])
        c.circle(px, py, 5.5, fill=1, stroke=0)
    c.setFillColor(TEXT)
    c.setFont("QK-Bold", 29)
    c.drawCentredString(cx, cy - 10, "psi")

    round_rect(c, 66, 185, W - 132, 130, PANEL_2, GREEN_DARK, 18)
    label(c, "Decisión de diseño", 84, 286, YELLOW)
    c.setFont("QK-Bold", 16)
    c.setFillColor(TEXT)
    c.drawString(84, 257, "Privado primero. Evidencia antes que espectáculo.")
    paragraph(c, "El simulador no afirma ventaja cuántica, no compra activos y nunca reemplaza automáticamente al modelo Champion. Cada resultado queda identificado por datos, configuración, código y huella SHA-256.", 84, 235, W - 168, 9.2, 14, MUTED)
    c.setFillColor(FAINT)
    c.setFont("QK-Mono", 8)
    c.drawString(66, 74, "MANUAL TÉCNICO + PROTOCOLO + GUÍA DE GITHUB")
    c.drawRightString(W - 66, 74, "EDICIÓN PRIVADA / 18 PÁGINAS")
    c.showPage()


def idea_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "01 / Idea central", "Una pregunta falsable", "La propuesta no consiste en añadir la palabra quantum a un dashboard. Consiste en una comparación temporal que puede fallar y deja evidencia de por qué falló.", page)
    metric_box(c, 40, y - 132, 162, 112, "Objetivo", "P(activo > SPY)", "Probabilidad calibrada de exceso positivo.")
    metric_box(c, 216, y - 132, 162, 112, "Horizontes", "5 / 20 / 60", "Sesiones rápidas, mensuales y de tesis.", BLUE)
    metric_box(c, 392, y - 132, 162, 112, "Métrica primaria", "Brier", "Error cuadrático probabilístico; menor es mejor.", YELLOW)
    y -= 165
    round_rect(c, 40, y - 215, W - 80, 200)
    label(c, "La hipótesis", 60, y - 42)
    c.setFont("QK-Bold", 15)
    c.setFillColor(TEXT)
    c.drawString(60, y - 72, "H1: el kernel de fidelidad reduce el Brier fuera de muestra.")
    c.setFont("QK-Bold", 15)
    c.setFillColor(RED)
    c.drawString(60, y - 104, "H0: no mejora de forma estable frente a los baselines.")
    paragraph(c, "Que H0 sobreviva también es un resultado válido. El proyecto gana credibilidad cuando conserva resultados negativos, incertidumbre y límites, en vez de optimizar la presentación después de observar la prueba.", 60, y - 137, W - 120, 9.3, 14, MUTED)
    c.showPage()


def method_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "02 / Método científico", "Del indicador a la evidencia", "Cada elección crítica se fija antes de ejecutar: variable objetivo, folds, purga, feature map, métricas, bootstrap y puertas de promoción.", page)
    steps = [
        ("01", "Preregistrar", "Congelar quantum/config.json y su hash."),
        ("02", "Reconstruir", "Generar variables point-in-time desde la historia."),
        ("03", "Comparar", "Mismas filas para logística, RBF y quantumZZ."),
        ("04", "Calibrar", "Separar calibración de fit y test."),
        ("05", "Cuantificar", "Brier, ECE, AUC y bootstrap por fecha."),
        ("06", "Archivar", "Guardar huella y nunca reescribir la evidencia."),
    ]
    box_w = (W - 100) / 2
    for idx, (number, head, note) in enumerate(steps):
        col, row = idx % 2, idx // 2
        x = 40 + col * (box_w + 20)
        by = y - 100 - row * 120
        round_rect(c, x, by, box_w, 98)
        c.setFillColor(GREEN if idx < 5 else YELLOW)
        c.setFont("QK-Mono", 13)
        c.drawString(x + 16, by + 67, number)
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 12)
        c.drawString(x + 58, by + 68, head)
        paragraph(c, note, x + 58, by + 49, box_w - 76, 8.2, 11.5, MUTED)
    c.showPage()


def math_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "03 / Fundamento matemático", "Qué calcula el kernel", "Un circuito no predice directamente. Construye una representación de cada vector y mide similitud mediante fidelidad; después un SVC clásico aprende el separador.", page)
    round_rect(c, 40, y - 145, W - 80, 130, PANEL_2)
    label(c, "Mapa de características", 60, y - 42, BLUE)
    c.setFont("QK-Mono", 16)
    c.setFillColor(TEXT)
    c.drawString(60, y - 78, "x  ->  |phi(x)> = U_phi(x)|0...0>")
    c.drawString(60, y - 112, "K(x,z) = |<phi(x)|phi(z)>|^2")
    y -= 175
    node(c, 40, y - 92, 110, 82, "x in R^15", "variables de mercado")
    arrow(c, 154, y - 50, 177)
    node(c, 181, y - 92, 110, 82, "theta in [0,pi]^4", "PCA y ángulos", BLUE)
    arrow(c, 295, y - 50, 318, BLUE)
    node(c, 322, y - 92, 110, 82, "|phi(x)>", "circuito ZZ", BLUE)
    arrow(c, 436, y - 50, 459, BLUE)
    node(c, 463, y - 92, 91, 82, "K", "matriz PSD", YELLOW)
    y -= 125
    bullet_list(c, [
        "La fidelidad queda entre 0 y 1; mide solapamiento de estados, no rentabilidad.",
        "El kernel se entrega a un SVC con kernel precomputado.",
        "La simulación exacta evita ruido de shots en Q1 y facilita reproducibilidad.",
        "El costo dominante es construir matrices O(n^2); por eso el muestreo está limitado.",
    ], 48, y, W - 96)
    c.showPage()


def data_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "04 / Datos", "Quince variables, tres etiquetas", "El laboratorio reutiliza el feature store temporal del Research Lab. No introduce noticias sin timestamp auditable ni fundamentales revisados retroactivamente.", page)
    groups = [
        ("Momentum", "ret_5, ret_20, ret_60, RSI 14"),
        ("Tendencia", "SMA 50 ratio, SMA 200 ratio"),
        ("Riesgo", "vol_20, vol_60, drawdown_252, beta_60"),
        ("Liquidez", "volume_z_20"),
        ("Mercado", "SPY ret 20/60, SMA 200 ratio, vol 60"),
    ]
    for idx, (head, note) in enumerate(groups):
        by = y - 66 - idx * 68
        round_rect(c, 40, by, 320, 54)
        label(c, head, 54, by + 34)
        paragraph(c, note, 140, by + 36, 205, 8.2, 11, TEXT)
    round_rect(c, 380, y - 340, 174, 328, PANEL_2)
    label(c, "Etiquetas", 397, y - 39, YELLOW)
    for idx, horizon in enumerate((5, 20, 60)):
        by = y - 100 - idx * 86
        c.setFillColor(GREEN if idx < 2 else BLUE)
        c.setFont("QK-Bold", 24)
        c.drawString(398, by, str(horizon))
        c.setFont("QK", 8.2)
        c.setFillColor(TEXT)
        c.drawString(440, by + 8, "sesiones")
        paragraph(c, "1 si el activo supera a SPY; 0 si no.", 398, by - 15, 135, 7.5, 10, MUTED)
    y -= 382
    paragraph(c, "Control esencial: StandardScaler, PCA y cuantiles se ajustan únicamente con fit. El año de prueba jamás cambia la representación.", 40, y, W - 80, 10, 15, YELLOW, "QK-Bold")
    c.showPage()


def temporal_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "05 / Validación temporal", "Walk-forward con doble purga", "Las etiquetas usan retornos futuros. Sin una zona purgada, una observación cercana al límite podría mirar dentro de la siguiente partición.", page)
    x0, bar_y, total_w = 48, y - 102, W - 96
    segments = [
        (0.00, 0.46, GREEN_DARK, "FIT", "pasado expansivo"),
        (0.46, 0.53, Color(YELLOW.red, YELLOW.green, YELLOW.blue, alpha=0.25), "PURGA h", "sin etiquetas cruzadas"),
        (0.53, 0.70, HexColor("#17304B"), "CALIBRACIÓN", "Platt"),
        (0.70, 0.77, Color(YELLOW.red, YELLOW.green, YELLOW.blue, alpha=0.25), "PURGA h", "sin ajuste"),
        (0.77, 1.00, HexColor("#143B31"), "TEST", "año futuro"),
    ]
    for start, end, color, head, note in segments:
        x, width = x0 + total_w * start, total_w * (end - start)
        c.setFillColor(color)
        c.roundRect(x, bar_y, width, 86, 7, fill=1, stroke=0)
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 7.5 if width < 70 else 9)
        c.drawCentredString(x + width / 2, bar_y + 52, head)
        c.setFillColor(MUTED)
        c.setFont("QK", 5.9 if width < 70 else 7)
        c.drawCentredString(x + width / 2, bar_y + 31, note)
    y -= 142
    round_rect(c, 40, y - 245, W - 80, 225)
    label(c, "Reglas comprobables", 60, y - 48)
    bullet_list(c, [
        "fit.max(date) < calibration.min(date) y la distancia excede h sesiones.",
        "calibration.max(date) < test.min(date) y la distancia excede h sesiones.",
        "Cada año de prueba aparece una sola vez en la evaluación agregada.",
        "El muestreo determinista conserva clases y cobertura temporal.",
        "Todos los modelos reciben índices idénticos; solo cambia la función de similitud.",
    ], 60, y - 79, W - 120, MUTED, 5)
    c.showPage()


def models_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "06 / Comparadores", "Tres modelos, un solo protocolo", "El modelo cuántico no puede competir contra un baseline debilitado. Logística y RBF representan referencias lineal y no lineal sólidas.", page)
    cards = [
        ("LOGISTIC", "Línea base", "Relación lineal en el espacio PCA. Probabilidad directa y lectura estable.", GREEN),
        ("SVM-RBF", "Línea base no lineal", "Similitud radial clásica, márgenes calibrados con Platt.", YELLOW),
        ("QUANTUM ZZ", "Shadow Challenger", "Fidelidad de estados de cuatro qubits, SVC y Platt.", BLUE),
    ]
    for idx, (head, role, note, accent) in enumerate(cards):
        x = 40 + idx * 176
        round_rect(c, x, y - 225, 162, 205, PANEL, Color(accent.red, accent.green, accent.blue, alpha=0.38))
        label(c, role, x + 16, y - 49, accent)
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 15)
        c.drawString(x + 16, y - 82, head)
        paragraph(c, note, x + 16, y - 108, 130, 8.2, 12, MUTED)
        c.setFillColor(accent)
        c.rect(x + 16, y - 199, 130, 3, fill=1, stroke=0)
    y -= 260
    round_rect(c, 40, y - 170, W - 80, 155, PANEL_2)
    label(c, "Condición de justicia", 58, y - 43, YELLOW)
    paragraph(c, "Si una fila no puede entrar al circuito cuántico, tampoco entra a los baselines del fold. Las métricas se agregan ponderando por tamaño de muestra. El bootstrap usa las pérdidas pareadas de las mismas fechas.", 58, y - 72, W - 116, 10, 15, TEXT)
    c.showPage()


def circuit_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "07 / Circuito", "ZZFeatureMap de cuatro qubits", "La primera revisión prioriza un circuito pequeño, reproducible y verificable. Dos repeticiones y entrelazado lineal limitan complejidad y costo.", page)
    wire_y = y - 60
    for q in range(4):
        wy = wire_y - q * 65
        c.setFont("QK-Mono", 8)
        c.setFillColor(MUTED)
        c.drawString(46, wy + 4, f"q{q}")
        c.setStrokeColor(GREEN_DARK)
        c.line(78, wy, W - 52, wy)
        gates = [(105, "H", GREEN), (190, "RZ", BLUE), (315, "ZZ", BLUE), (440, "RZ", BLUE), (515, "M", YELLOW)]
        for gx, gate, accent in gates:
            c.setFillColor(PANEL_2)
            c.setStrokeColor(accent)
            c.roundRect(gx, wy - 14, 34, 28, 6, fill=1, stroke=1)
            c.setFillColor(accent)
            c.setFont("QK-Bold", 7)
            c.drawCentredString(gx + 17, wy - 2, gate)
    for q in range(3):
        top = wire_y - q * 65
        bottom = wire_y - (q + 1) * 65
        c.setStrokeColor(BLUE)
        c.line(332, top - 14, 332, bottom + 14)
        c.circle(332, top, 3, fill=1, stroke=0)
        c.circle(332, bottom, 3, fill=1, stroke=0)
    y = wire_y - 270
    round_rect(c, 40, y - 155, W - 80, 142)
    label(c, "Lectura", 58, y - 39)
    bullet_list(c, [
        "Las rotaciones dependen de las cuatro componentes PCA en [0,pi].",
        "Los términos ZZ codifican interacciones entre componentes vecinas.",
        "La matriz se fuerza a semidefinida positiva cuando corresponde.",
        "Q1 usa shots=None: el resultado proviene de estado exacto simulado.",
    ], 58, y - 66, W - 116, MUTED, 2)
    c.showPage()


def metrics_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "08 / Evaluación", "Probabilidades, no solo aciertos", "El sistema puede acertar la clase y aun estar mal calibrado. Por eso Brier y ECE importan más que una accuracy aislada.", page)
    cards = [
        ("Brier", "mean((p-y)^2)", "Primaria", GREEN),
        ("ECE", "error de calibración", "Fiabilidad", BLUE),
        ("Log-loss", "-log P(y)", "Confianza", YELLOW),
        ("ROC-AUC", "ranking", "Discriminación", GREEN),
    ]
    for idx, (head, formula, role, accent) in enumerate(cards):
        col, row = idx % 2, idx // 2
        x, by = 40 + col * 258, y - 110 - row * 126
        round_rect(c, x, by, 242, 108)
        label(c, role, x + 15, by + 80, accent)
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 15)
        c.drawString(x + 15, by + 50, head)
        c.setFillColor(MUTED)
        c.setFont("QK-Mono", 8)
        c.drawString(x + 15, by + 26, formula)
    y -= 290
    round_rect(c, 40, y - 155, W - 80, 140, PANEL_2)
    label(c, "Bootstrap pareado por fecha", 58, y - 42, YELLOW)
    paragraph(c, "Se calcula delta = Brier(quantumZZ) - Brier(mejor clásico). Mil remuestreos seleccionan fechas completas, conservando la sección transversal diaria. Para pasar, el límite superior del intervalo del 95% debe quedar bajo cero.", 58, y - 72, W - 116, 9.4, 14, TEXT)
    c.showPage()


def governance_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "09 / Gobernanza", "Champion protegido", "Una mejora numérica no autoriza el cambio de modelo. Primero debe pasar reglas preregistradas y después una revisión humana.", page)
    gates = [
        ("3+ folds", "suficiencia temporal"),
        ("Delta Brier >= 0.002", "magnitud mínima"),
        ("ECE <= baseline + 0.01", "calibración"),
        ("IC 95% superior < 0", "separación estadística"),
        ("2 de 3 horizontes", "estabilidad"),
    ]
    for idx, (head, note) in enumerate(gates):
        by = y - 58 - idx * 66
        c.setFillColor(GREEN_DARK)
        c.roundRect(44, by, 34, 34, 8, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.setFont("QK-Bold", 12)
        c.drawCentredString(61, by + 10, str(idx + 1))
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 10)
        c.drawString(94, by + 20, head)
        c.setFillColor(MUTED)
        c.setFont("QK", 8)
        c.drawString(275, by + 20, note)
        c.setStrokeColor(GREEN_DARK)
        c.line(94, by + 6, W - 42, by + 6)
    y -= 378
    round_rect(c, 40, y - 116, W - 80, 103, Color(RED.red, RED.green, RED.blue, alpha=0.08), Color(RED.red, RED.green, RED.blue, alpha=0.35))
    label(c, "Invariante de seguridad", 58, y - 42, RED)
    paragraph(c, "automaticPromotion = false. Si todas las puertas pasan, el estado es elegible para revisión; nunca promoted. No existe ruta de trading en este módulo.", 58, y - 70, W - 116, 10, 14, TEXT, "QK-Bold")
    c.showPage()


def architecture_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "10 / Arquitectura", "Pipeline reproducible", "El feature store temporal se reconstruye, el experimento genera dos JSON y la página solamente los muestra cuando existe autorización explícita.", page)
    nodes = [
        ("Histórico", "market + SPY"),
        ("Feature store", "15 variables"),
        ("QML runner", "3 modelos"),
        ("Artefactos", "JSON + hash"),
        ("Interfaz", "Quantum Lab"),
    ]
    for idx, (head, note) in enumerate(nodes):
        x = 40 + idx * 104
        node(c, x, y - 118, 88, 100, head, note, BLUE if idx == 2 else GREEN)
        if idx < len(nodes) - 1:
            arrow(c, x + 89, y - 68, x + 101, BLUE if idx == 1 else GREEN)
    y -= 155
    round_rect(c, 40, y - 230, W - 80, 215)
    label(c, "Trazabilidad por ejecución", 58, y - 43)
    fields = [
        ("Config", "configHash"), ("Datos", "dataHash"), ("Código", "gitCommit"),
        ("Circuito", "depth / size / qubits"), ("Software", "Qiskit versions"), ("Resultado", "fingerprint"),
    ]
    for idx, (head, field) in enumerate(fields):
        col, row = idx % 3, idx // 3
        x, by = 58 + col * 164, y - 93 - row * 68
        c.setFillColor(MUTED)
        c.setFont("QK", 7.5)
        c.drawString(x, by, head)
        c.setFillColor(GREEN if head != "Resultado" else YELLOW)
        c.setFont("QK-Mono", 8)
        c.drawString(x, by - 20, field)
    c.showPage()


def interface_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "11 / Aplicación", "Una interfaz que no inventa", "Antes de la ejecución, la pestaña muestra el protocolo y dice claramente que no hay resultados. Después, compara modelos por horizonte y revela incertidumbre y gobernanza.", page)
    round_rect(c, 40, y - 360, W - 80, 344, HexColor("#061A15"), GREEN_DARK, 20)
    label(c, "Q1 / experimento cuántico preregistrado", 62, y - 48)
    title(c, "Quantum Kernel Lab", 62, y - 84, 22)
    c.setFillColor(YELLOW)
    c.roundRect(W - 182, y - 86, 118, 27, 13, fill=0, stroke=1)
    c.setFont("QK-Bold", 6.5)
    c.drawCentredString(W - 123, y - 77, "PROTOCOLO / MANUAL")
    cards = [
        ("ROL", "Shadow Challenger"), ("QUBITS", "4"), ("HORIZONTES", "5 / 20 / 60"), ("PROMOCIÓN", "Manual"),
    ]
    for idx, (head, value) in enumerate(cards):
        x = 62 + idx * 119
        round_rect(c, x, y - 164, 108, 62, PANEL)
        label(c, head, x + 11, y - 121)
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 9.5)
        c.drawString(x + 11, y - 146, value)
    round_rect(c, 62, y - 334, W - 124, 145, HexColor("#0C1D17"), Color(YELLOW.red, YELLOW.green, YELLOW.blue, alpha=0.35))
    label(c, "Ejecución deliberadamente separada", 82, y - 220, YELLOW)
    c.setFillColor(TEXT)
    c.setFont("QK-Bold", 12)
    c.drawString(82, y - 248, "El protocolo está listo; todavía no existen resultados cuánticos.")
    paragraph(c, "El workflow construirá los folds y conservará el JSON como artefacto privado. La página solo cambia si publish_results=true.", 82, y - 274, W - 164, 8.4, 12, MUTED)
    c.showPage()


def github_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "12 / GitHub", "Ejecución privada por defecto", "El workflow es manual para controlar costo y evitar que cada commit ejecute matrices cuánticas. Publicar es una decisión separada.", page)
    steps = [
        ("1", "Actions", "Selecciona Ejecutar Quantum Kernel Lab."),
        ("2", "Run workflow", "Mantén publish_results=false."),
        ("3", "Espera", "Build, Qiskit, pruebas y validación."),
        ("4", "Descarga", "Artifact privado quantum-kernel-results."),
        ("5", "Revisa", "Usa la plantilla de resultados."),
        ("6", "Autoriza", "Publica solo en una corrida posterior."),
    ]
    for idx, (number, head, note) in enumerate(steps):
        col, row = idx % 2, idx // 2
        x, by = 40 + col * 258, y - 98 - row * 116
        round_rect(c, x, by, 242, 96)
        c.setFillColor(GREEN if idx < 5 else YELLOW)
        c.circle(x + 29, by + 49, 15, fill=1, stroke=0)
        c.setFillColor(BG)
        c.setFont("QK-Bold", 10)
        c.drawCentredString(x + 29, by + 45, number)
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 10)
        c.drawString(x + 55, by + 62, head)
        paragraph(c, note, x + 55, by + 42, 165, 7.8, 11, MUTED)
    y -= 390
    paragraph(c, "Artifact privado: 30 días. Sin commit. Sin despliegue. Sin cambio de Champion.", 40, y, W - 80, 10, 15, GREEN, "QK-Bold")
    c.showPage()


def security_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "13 / Seguridad", "Qué queda dentro y fuera", "El módulo no necesita credenciales para Qiskit en simulación. Las claves de mercado siguen en GitHub Secrets o Cloudflare y nunca entran a los artefactos.", page)
    round_rect(c, 40, y - 305, 248, 288)
    label(c, "Se conserva", 58, y - 45, GREEN)
    bullet_list(c, [
        "config, semillas y versiones",
        "periodos y tamaños de cada fold",
        "métricas y bootstrap",
        "hash de datos y código",
        "circuit depth, size y qubits",
        "resultados negativos",
    ], 58, y - 77, 210, MUTED, 6)
    round_rect(c, 306, y - 305, 248, 288, Color(RED.red, RED.green, RED.blue, alpha=0.05), Color(RED.red, RED.green, RED.blue, alpha=0.25))
    label(c, "Nunca se guarda", 324, y - 45, RED)
    bullet_list(c, [
        "API keys o secrets",
        "contraseñas o tokens",
        "datos personales de Firebase",
        "órdenes de compra o venta",
        "resultados de prueba ficticios",
        "promoción automática",
    ], 324, y - 77, 210, MUTED, 6)
    y -= 340
    paragraph(c, "Antes de distribuir el ZIP, un escaneo busca patrones de secretos y excluye .env, node_modules, cachés y research_work.", 40, y, W - 80, 9.5, 14, YELLOW, "QK-Bold")
    c.showPage()


def results_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "14 / Lectura de resultados", "Tres conclusiones posibles", "La interfaz nunca debe convertir una mejora pequeña en una historia de éxito. La conclusión depende de magnitud, incertidumbre, calibración y estabilidad.", page)
    options = [
        ("NO CONCLUYENTE", "El intervalo incluye cero o el kernel no supera al baseline.", RED),
        ("PROMETEDOR", "Mejora Brier, pero faltan folds, estabilidad o calibración.", YELLOW),
        ("ELEGIBLE", "Pasa todas las puertas; requiere revisión humana y réplica.", GREEN),
    ]
    for idx, (head, note, accent) in enumerate(options):
        by = y - 105 - idx * 122
        round_rect(c, 40, by, W - 80, 100, PANEL, Color(accent.red, accent.green, accent.blue, alpha=0.35))
        c.setFillColor(accent)
        c.setFont("QK-Bold", 14)
        c.drawString(60, by + 60, head)
        paragraph(c, note, 220, by + 65, W - 300, 9, 13, TEXT)
    y -= 405
    paragraph(c, "Frase prohibida en Q1: 'demostramos ventaja cuántica'. Frase correcta: 'evaluamos una representación cuántica en simulación bajo un protocolo temporal y comparamos su calibración fuera de muestra'.", 40, y, W - 80, 9, 14, MUTED)
    c.showPage()


def roadmap_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "15 / Roadmap", "De Q1 a una línea de investigación", "Cada extensión debe convertirse en un experimento nuevo, con ID, hipótesis y puertas propias antes de observar el test.", page)
    roadmap = [
        ("Q1", "Kernel fijo", "ZZFeatureMap, simulación exacta, 4 qubits."),
        ("Q2", "Ablación", "Sin beta, sin mercado, PCA 2/3/4; test intacto."),
        ("Q3", "Kernel entrenable", "QuantumKernelTrainer solo en fit/calibración."),
        ("Q4", "Robustez al ruido", "Shots y modelos de ruido; misma muestra."),
        ("Q5", "Hardware", "Submuestra congelada y costo registrado."),
    ]
    for idx, (qid, head, note) in enumerate(roadmap):
        by = y - 66 - idx * 78
        c.setFillColor(BLUE if idx >= 2 else GREEN)
        c.setFont("QK-Bold", 11)
        c.drawString(44, by + 20, qid)
        c.setStrokeColor(GREEN_DARK)
        c.line(80, by + 24, 104, by + 24)
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 10)
        c.drawString(118, by + 24, head)
        paragraph(c, note, 244, by + 28, 304, 8.2, 11, MUTED)
    y -= 430
    round_rect(c, 40, y - 76, W - 80, 64, PANEL_2)
    label(c, "Regla", 58, y - 38, YELLOW)
    paragraph(c, "El resultado de Q1 no decide la configuración de Q2 sin declarar una nueva revisión.", 112, y - 34, W - 170, 8.6, 12, TEXT)
    c.showPage()


def files_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "16 / Entrega", "Mapa de archivos", "El paquete completo está listo para conservar localmente y, cuando decidas, subir a la raíz de GitHub sin copiar node_modules ni datos temporales.", page)
    files = [
        ("quantum/config.json", "protocolo ejecutable"),
        ("scripts/quantum_core.py", "purga, encoder, métricas, bootstrap"),
        ("scripts/run_quantum_kernel_lab.py", "runner Qiskit y baselines"),
        ("tests/test_quantum_*.py", "pruebas unitarias e integración"),
        (".github/workflows/quantum-kernel-lab.yml", "ejecución privada"),
        ("app/components/QuantumKernelLab.tsx", "interfaz"),
        ("public/data/quantum_kernel_*.json", "protocolo e historial"),
        ("docs/quantum/", "documentación auditable"),
    ]
    for idx, (path, note) in enumerate(files):
        by = y - 40 - idx * 46
        c.setFillColor(PANEL if idx % 2 == 0 else PANEL_2)
        c.roundRect(40, by - 24, W - 80, 38, 7, fill=1, stroke=0)
        c.setFillColor(GREEN if idx < 5 else BLUE)
        c.setFont("QK-Mono", 7.8)
        c.drawString(52, by - 8, path)
        c.setFillColor(MUTED)
        c.setFont("QK", 7.4)
        c.drawRightString(W - 52, by - 8, note)
    y -= 430
    paragraph(c, "Se entregan un ZIP completo, un ZIP overlay con solo los cambios, este PDF y SHA256SUMS.txt.", 40, y, W - 80, 9.5, 14, TEXT, "QK-Bold")
    c.showPage()


def references_page(c: canvas.Canvas, page: int) -> None:
    y = page_heading(c, "17 / Fuentes", "Base científica y documentación", "La idea se apoya en trabajos primarios sobre espacios de características cuánticos, generalización, riesgos de concentración y aplicaciones financieras.", page)
    references = [
        ("Havlicek et al. (2019)", "Supervised learning with quantum-enhanced feature spaces.", "doi.org/10.1038/s41586-019-0980-2"),
        ("Huang et al. (2021)", "Power of data in quantum machine learning.", "doi.org/10.1038/s41467-021-22539-9"),
        ("Thanasilp et al. (2024)", "Exponential concentration and untrainability in quantum kernel methods.", "doi.org/10.1038/s41467-024-49287-w"),
        ("Herman et al. (2023)", "A survey of quantum computing for finance.", "doi.org/10.1038/s42254-023-00603-1"),
        ("Qiskit ML 0.9.1", "Quantum kernels and FidelityStatevectorKernel API.", "qiskit-community.github.io/qiskit-machine-learning/"),
        ("GitHub Actions", "Node 24 compatible checkout, setup-python and upload-artifact.", "github.com/actions"),
    ]
    for idx, (author, paper, url) in enumerate(references):
        by = y - 70 - idx * 80
        c.setFillColor(GREEN if idx < 4 else BLUE)
        c.setFont("QK-Bold", 8.5)
        c.drawString(42, by + 25, f"0{idx + 1}")
        c.setFillColor(TEXT)
        c.setFont("QK-Bold", 9.2)
        c.drawString(78, by + 25, author)
        paragraph(c, paper, 78, by + 7, 410, 8, 11, MUTED)
        c.setFillColor(FAINT)
        c.setFont("QK-Mono", 6.5)
        c.drawString(78, by - 18, url)
    c.setFillColor(GREEN)
    c.setFont("QK-Bold", 10)
    c.drawCentredString(W / 2, 60, "FIN DEL MANUAL / EL EXPERIMENTO TODAVÍA PUEDE FALLAR")
    c.showPage()


def build() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("Quantum Kernel Lab - Manual técnico privado")
    c.setAuthor("InvestmentResearchAI")
    c.setSubject("Protocolo reproducible de quantum machine learning para predicción relativa a SPY")
    cover(c)
    pages = [
        idea_page,
        method_page,
        math_page,
        data_page,
        temporal_page,
        models_page,
        circuit_page,
        metrics_page,
        governance_page,
        architecture_page,
        interface_page,
        github_page,
        security_page,
        results_page,
        roadmap_page,
        files_page,
        references_page,
    ]
    for page_number, draw in enumerate(pages, start=2):
        draw(c, page_number)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()

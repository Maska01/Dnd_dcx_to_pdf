from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A3, A4, A5, A6, B5, ELEVENSEVENTEEN, LEGAL, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm

COLOR_PRIMARIO = HexColor("#8B0000")
COLOR_SECUNDARIO = HexColor("#1a1a1a")
COLOR_FONDO_PAGINA = HexColor("#F7F1E3")

COLOR_AZUL_TEXTO = HexColor("#1F3A93")
COLOR_AZUL_BORDE = HexColor("#5B8DEF")
COLOR_AZUL_FONDO = HexColor("#EAF1FB")

COLOR_AMA_TEXTO = HexColor("#000000")
COLOR_AMA_BORDE = HexColor("#D9B96A")
COLOR_AMA_FONDO = HexColor("#FBF3DC")

COLOR_INFO_TEXTO = HexColor("#0F4C5C")
COLOR_INFO_BORDE = HexColor("#2A9D8F")
COLOR_INFO_FONDO = HexColor("#E6F7F5")

COLOR_ENEMIGO_TEXTO = HexColor("#7A1C1C")
COLOR_ENEMIGO_BORDE = HexColor("#C0392B")
COLOR_ENEMIGO_FONDO = HexColor("#FDECEC")

COLOR_NPC_TEXTO = HexColor("#444444")
COLOR_NPC_BORDE = HexColor("#8D99AE")
COLOR_NPC_FONDO = HexColor("#F1F3F5")

COLOR_ALIADO_TEXTO = HexColor("#1E5631")
COLOR_ALIADO_BORDE = HexColor("#4CAF50")
COLOR_ALIADO_FONDO = HexColor("#EAF7EE")

COLOR_TESORO_TEXTO = HexColor("#5B2C83")
COLOR_TESORO_BORDE = HexColor("#8E44AD")
COLOR_TESORO_FONDO = HexColor("#F3E8FF")

COLOR_OBJETO_TEXTO = HexColor("#2F2F2F")
COLOR_OBJETO_BORDE = HexColor("#BFC5CC")
COLOR_OBJETO_FONDO = HexColor("#FFFFFF")

FUENTE_TITULO = "Helvetica-Bold"
FUENTE_TEXTO = "Helvetica"
TAMANO_PAGINA = A4
MARGEN = 2 * cm
MINIMO_RENGLONES_CAJA_ANTES_DE_MOVER = 3
IMAGEN_PORTADA_PREDETERMINADA = r"C:\ruta\a\tu\imagen_portada.jpg"

TAMANOS_PAGINA_DISPONIBLES = {
    "A3": A3,
    "A4": A4,
    "A5": A5,
    "A6": A6,
    "B5": B5,
    "LETTER": LETTER,
    "LEGAL": LEGAL,
    "11X17": ELEVENSEVENTEEN,
}

OPCION_TAMANO_PERSONALIZADO = "PERSONALIZADO"

FUENTES_DISPONIBLES = [
    "Helvetica",
    "Helvetica-Bold",
    "Helvetica-Oblique",
    "Helvetica-BoldOblique",
    "Times-Roman",
    "Times-Bold",
    "Times-Italic",
    "Times-BoldItalic",
    "Courier",
    "Courier-Bold",
    "Courier-Oblique",
    "Courier-BoldOblique",
]


def _color_a_hex(color):
    return f"#{color.hexval()[2:].upper()}"


def _normalizar_color_hex(color, valor_predeterminado):
    if not color:
        return valor_predeterminado

    texto = str(color).strip()
    if not texto:
        return valor_predeterminado
    if not texto.startswith("#"):
        texto = f"#{texto}"

    try:
        return _color_a_hex(HexColor(texto))
    except Exception:
        return valor_predeterminado


def obtener_configuracion_visual_predeterminada():
    return {
        "color_primario": _color_a_hex(COLOR_PRIMARIO),
        "color_secundario": _color_a_hex(COLOR_SECUNDARIO),
        "color_fondo_pagina": _color_a_hex(COLOR_FONDO_PAGINA),
        "color_azul_texto": _color_a_hex(COLOR_AZUL_TEXTO),
        "color_azul_borde": _color_a_hex(COLOR_AZUL_BORDE),
        "color_azul_fondo": _color_a_hex(COLOR_AZUL_FONDO),
        "color_ama_texto": _color_a_hex(COLOR_AMA_TEXTO),
        "color_ama_borde": _color_a_hex(COLOR_AMA_BORDE),
        "color_ama_fondo": _color_a_hex(COLOR_AMA_FONDO),
        "color_info_texto": _color_a_hex(COLOR_INFO_TEXTO),
        "color_info_borde": _color_a_hex(COLOR_INFO_BORDE),
        "color_info_fondo": _color_a_hex(COLOR_INFO_FONDO),
        "color_enemigo_texto": _color_a_hex(COLOR_ENEMIGO_TEXTO),
        "color_enemigo_borde": _color_a_hex(COLOR_ENEMIGO_BORDE),
        "color_enemigo_fondo": _color_a_hex(COLOR_ENEMIGO_FONDO),
        "color_npc_texto": _color_a_hex(COLOR_NPC_TEXTO),
        "color_npc_borde": _color_a_hex(COLOR_NPC_BORDE),
        "color_npc_fondo": _color_a_hex(COLOR_NPC_FONDO),
        "color_aliado_texto": _color_a_hex(COLOR_ALIADO_TEXTO),
        "color_aliado_borde": _color_a_hex(COLOR_ALIADO_BORDE),
        "color_aliado_fondo": _color_a_hex(COLOR_ALIADO_FONDO),
        "color_tesoro_texto": _color_a_hex(COLOR_TESORO_TEXTO),
        "color_tesoro_borde": _color_a_hex(COLOR_TESORO_BORDE),
        "color_tesoro_fondo": _color_a_hex(COLOR_TESORO_FONDO),
        "color_objeto_texto": _color_a_hex(COLOR_OBJETO_TEXTO),
        "color_objeto_borde": _color_a_hex(COLOR_OBJETO_BORDE),
        "color_objeto_fondo": _color_a_hex(COLOR_OBJETO_FONDO),
    }


def _nombre_tamano_pagina_actual():
    for nombre, tamano in TAMANOS_PAGINA_DISPONIBLES.items():
        if tuple(tamano) == tuple(TAMANO_PAGINA):
            return nombre
    return "A4"


def obtener_configuracion_documento_predeterminada():
    ancho_cm = round(TAMANO_PAGINA[0] / cm, 2)
    alto_cm = round(TAMANO_PAGINA[1] / cm, 2)
    return {
        "tamano_pagina": _nombre_tamano_pagina_actual(),
        "fuente_titulo": FUENTE_TITULO,
        "fuente_texto": FUENTE_TEXTO,
        "margen_cm": round(MARGEN / cm, 2),
        "ancho_pagina_cm": ancho_cm,
        "alto_pagina_cm": alto_cm,
    }


def aplicar_configuracion_documento(configuracion_documento):
    global FUENTE_TITULO, FUENTE_TEXTO, TAMANO_PAGINA, MARGEN

    valores = obtener_configuracion_documento_predeterminada()
    valores.update(configuracion_documento or {})

    nombre_pagina = str(valores.get("tamano_pagina", "A4")).strip().upper()
    if nombre_pagina == OPCION_TAMANO_PERSONALIZADO:
        try:
            ancho_cm = float(valores.get("ancho_pagina_cm", 21.0))
        except (TypeError, ValueError):
            ancho_cm = 21.0
        try:
            alto_cm = float(valores.get("alto_pagina_cm", 29.7))
        except (TypeError, ValueError):
            alto_cm = 29.7
        ancho_cm = min(max(ancho_cm, 5.0), 100.0)
        alto_cm = min(max(alto_cm, 5.0), 100.0)
        TAMANO_PAGINA = (ancho_cm * cm, alto_cm * cm)
    else:
        TAMANO_PAGINA = TAMANOS_PAGINA_DISPONIBLES.get(nombre_pagina, A4)

    fuente_titulo = str(valores.get("fuente_titulo", FUENTE_TITULO)).strip()
    fuente_texto = str(valores.get("fuente_texto", FUENTE_TEXTO)).strip()
    FUENTE_TITULO = fuente_titulo if fuente_titulo in FUENTES_DISPONIBLES else "Helvetica-Bold"
    FUENTE_TEXTO = fuente_texto if fuente_texto in FUENTES_DISPONIBLES else "Helvetica"

    try:
        margen_cm = float(valores.get("margen_cm", MARGEN / cm))
    except (TypeError, ValueError):
        margen_cm = 2.0
    margen_cm = min(max(margen_cm, 0.5), 5.0)
    MARGEN = margen_cm * cm


def aplicar_configuracion_visual(configuracion_visual):
    global COLOR_PRIMARIO, COLOR_SECUNDARIO, COLOR_FONDO_PAGINA
    global COLOR_AZUL_TEXTO, COLOR_AZUL_BORDE, COLOR_AZUL_FONDO
    global COLOR_AMA_TEXTO, COLOR_AMA_BORDE, COLOR_AMA_FONDO
    global COLOR_INFO_TEXTO, COLOR_INFO_BORDE, COLOR_INFO_FONDO
    global COLOR_ENEMIGO_TEXTO, COLOR_ENEMIGO_BORDE, COLOR_ENEMIGO_FONDO
    global COLOR_NPC_TEXTO, COLOR_NPC_BORDE, COLOR_NPC_FONDO
    global COLOR_ALIADO_TEXTO, COLOR_ALIADO_BORDE, COLOR_ALIADO_FONDO
    global COLOR_TESORO_TEXTO, COLOR_TESORO_BORDE, COLOR_TESORO_FONDO
    global COLOR_OBJETO_TEXTO, COLOR_OBJETO_BORDE, COLOR_OBJETO_FONDO

    valores = obtener_configuracion_visual_predeterminada()
    valores.update(configuracion_visual or {})

    COLOR_PRIMARIO = HexColor(_normalizar_color_hex(valores["color_primario"], _color_a_hex(COLOR_PRIMARIO)))
    COLOR_SECUNDARIO = HexColor(_normalizar_color_hex(valores["color_secundario"], _color_a_hex(COLOR_SECUNDARIO)))
    COLOR_FONDO_PAGINA = HexColor(_normalizar_color_hex(valores["color_fondo_pagina"], _color_a_hex(COLOR_FONDO_PAGINA)))
    COLOR_AZUL_TEXTO = HexColor(_normalizar_color_hex(valores["color_azul_texto"], _color_a_hex(COLOR_AZUL_TEXTO)))
    COLOR_AZUL_BORDE = HexColor(_normalizar_color_hex(valores["color_azul_borde"], _color_a_hex(COLOR_AZUL_BORDE)))
    COLOR_AZUL_FONDO = HexColor(_normalizar_color_hex(valores["color_azul_fondo"], _color_a_hex(COLOR_AZUL_FONDO)))
    COLOR_AMA_TEXTO = HexColor(_normalizar_color_hex(valores["color_ama_texto"], _color_a_hex(COLOR_AMA_TEXTO)))
    COLOR_AMA_BORDE = HexColor(_normalizar_color_hex(valores["color_ama_borde"], _color_a_hex(COLOR_AMA_BORDE)))
    COLOR_AMA_FONDO = HexColor(_normalizar_color_hex(valores["color_ama_fondo"], _color_a_hex(COLOR_AMA_FONDO)))
    COLOR_INFO_TEXTO = HexColor(_normalizar_color_hex(valores["color_info_texto"], _color_a_hex(COLOR_INFO_TEXTO)))
    COLOR_INFO_BORDE = HexColor(_normalizar_color_hex(valores["color_info_borde"], _color_a_hex(COLOR_INFO_BORDE)))
    COLOR_INFO_FONDO = HexColor(_normalizar_color_hex(valores["color_info_fondo"], _color_a_hex(COLOR_INFO_FONDO)))
    COLOR_ENEMIGO_TEXTO = HexColor(_normalizar_color_hex(valores["color_enemigo_texto"], _color_a_hex(COLOR_ENEMIGO_TEXTO)))
    COLOR_ENEMIGO_BORDE = HexColor(_normalizar_color_hex(valores["color_enemigo_borde"], _color_a_hex(COLOR_ENEMIGO_BORDE)))
    COLOR_ENEMIGO_FONDO = HexColor(_normalizar_color_hex(valores["color_enemigo_fondo"], _color_a_hex(COLOR_ENEMIGO_FONDO)))
    COLOR_NPC_TEXTO = HexColor(_normalizar_color_hex(valores["color_npc_texto"], _color_a_hex(COLOR_NPC_TEXTO)))
    COLOR_NPC_BORDE = HexColor(_normalizar_color_hex(valores["color_npc_borde"], _color_a_hex(COLOR_NPC_BORDE)))
    COLOR_NPC_FONDO = HexColor(_normalizar_color_hex(valores["color_npc_fondo"], _color_a_hex(COLOR_NPC_FONDO)))
    COLOR_ALIADO_TEXTO = HexColor(_normalizar_color_hex(valores["color_aliado_texto"], _color_a_hex(COLOR_ALIADO_TEXTO)))
    COLOR_ALIADO_BORDE = HexColor(_normalizar_color_hex(valores["color_aliado_borde"], _color_a_hex(COLOR_ALIADO_BORDE)))
    COLOR_ALIADO_FONDO = HexColor(_normalizar_color_hex(valores["color_aliado_fondo"], _color_a_hex(COLOR_ALIADO_FONDO)))
    COLOR_TESORO_TEXTO = HexColor(_normalizar_color_hex(valores["color_tesoro_texto"], _color_a_hex(COLOR_TESORO_TEXTO)))
    COLOR_TESORO_BORDE = HexColor(_normalizar_color_hex(valores["color_tesoro_borde"], _color_a_hex(COLOR_TESORO_BORDE)))
    COLOR_TESORO_FONDO = HexColor(_normalizar_color_hex(valores["color_tesoro_fondo"], _color_a_hex(COLOR_TESORO_FONDO)))
    COLOR_OBJETO_TEXTO = HexColor(_normalizar_color_hex(valores["color_objeto_texto"], _color_a_hex(COLOR_OBJETO_TEXTO)))
    COLOR_OBJETO_BORDE = HexColor(_normalizar_color_hex(valores["color_objeto_borde"], _color_a_hex(COLOR_OBJETO_BORDE)))
    COLOR_OBJETO_FONDO = HexColor(_normalizar_color_hex(valores["color_objeto_fondo"], _color_a_hex(COLOR_OBJETO_FONDO)))


def construir_estilos():
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name="PortadaTitulo", fontName=FUENTE_TITULO, fontSize=36, leading=42, textColor=COLOR_PRIMARIO, alignment=TA_CENTER, spaceAfter=20))
    estilos.add(ParagraphStyle(name="PortadaSubtitulo", fontName=FUENTE_TEXTO, fontSize=16, leading=20, textColor=COLOR_SECUNDARIO, alignment=TA_CENTER, spaceAfter=10))
    estilos.add(ParagraphStyle(name="PortadaAutor", fontName=FUENTE_TEXTO, fontSize=13, leading=18, textColor=COLOR_SECUNDARIO, alignment=TA_CENTER))
    estilos.add(ParagraphStyle(name="H1", fontName=FUENTE_TITULO, fontSize=22, leading=26, textColor=COLOR_PRIMARIO, spaceBefore=18, spaceAfter=12))
    estilos.add(ParagraphStyle(name="H2", fontName=FUENTE_TITULO, fontSize=16, leading=20, textColor=COLOR_PRIMARIO, spaceBefore=14, spaceAfter=8))
    estilos.add(ParagraphStyle(name="H3", fontName=FUENTE_TITULO, fontSize=13, leading=16, textColor=COLOR_SECUNDARIO, spaceBefore=10, spaceAfter=6))
    estilos.add(ParagraphStyle(name="Cuerpo", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=black, alignment=TA_JUSTIFY, spaceAfter=8))
    estilos.add(ParagraphStyle(name="CajaCita", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=COLOR_AMA_TEXTO, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8, borderColor=COLOR_AMA_BORDE, borderWidth=1, borderRadius=8, borderPadding=4, backColor=COLOR_AMA_FONDO))
    estilos.add(ParagraphStyle(name="CajaInfoAdicional", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=COLOR_INFO_TEXTO, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, spaceBefore=3, spaceAfter=8, borderColor=COLOR_INFO_BORDE, borderWidth=1, borderRadius=8, borderPadding=4, backColor=COLOR_INFO_FONDO))
    estilos.add(ParagraphStyle(name="CajaConsejoDm", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=COLOR_AZUL_TEXTO, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8, borderColor=COLOR_AZUL_BORDE, borderWidth=1, borderRadius=8, borderPadding=4, backColor=COLOR_AZUL_FONDO))
    estilos.add(ParagraphStyle(name="CajaNpc", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=COLOR_NPC_TEXTO, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8, borderColor=COLOR_NPC_BORDE, borderWidth=1, borderRadius=8, borderPadding=4, backColor=COLOR_NPC_FONDO))
    estilos.add(ParagraphStyle(name="CajaEnemigo", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=COLOR_ENEMIGO_TEXTO, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8, borderColor=COLOR_ENEMIGO_BORDE, borderWidth=1, borderRadius=8, borderPadding=4, backColor=COLOR_ENEMIGO_FONDO))
    estilos.add(ParagraphStyle(name="CajaAliado", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=COLOR_ALIADO_TEXTO, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8, borderColor=COLOR_ALIADO_BORDE, borderWidth=1, borderRadius=8, borderPadding=4, backColor=COLOR_ALIADO_FONDO))
    estilos.add(ParagraphStyle(name="CajaTesoro", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=COLOR_TESORO_TEXTO, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8, borderColor=COLOR_TESORO_BORDE, borderWidth=1, borderRadius=8, borderPadding=4, backColor=COLOR_TESORO_FONDO))
    estilos.add(ParagraphStyle(name="CajaObjeto", fontName=FUENTE_TEXTO, fontSize=11, leading=15, textColor=COLOR_OBJETO_TEXTO, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8, borderColor=COLOR_OBJETO_BORDE, borderWidth=1, borderRadius=8, borderPadding=4, backColor=COLOR_OBJETO_FONDO))
    estilos.add(ParagraphStyle(name="TituloIndice", fontName=FUENTE_TITULO, fontSize=22, leading=26, textColor=COLOR_PRIMARIO, alignment=TA_CENTER, spaceAfter=20))
    return estilos

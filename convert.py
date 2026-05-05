"""
Conversor de Word (.docx) a PDF con estilo "Aventura".

Uso:
    python convert.py entrada.docx salida.pdf
    python convert.py entrada.docx salida.pdf --titulo "Mi Aventura" --autor "Tu Nombre"

Convención del documento Word:
    - Estilo "Título 1" (Heading 1)  -> Capítulo (entra en el índice)
    - Estilo "Título 2" (Heading 2)  -> Sección (entra en el índice)
    - Estilo "Título 3" (Heading 3)  -> Subsección
    - Estilo "Cita"   (Quote)        -> Caja AMARILLA con texto negro
    - Estilo "Información adicional" o prefijo equivalente -> Caja verde-azulada
    - Estilo "Consejos" o prefijo equivalente -> Caja AZUL de Consejo para el DM
    - Párrafo que empiece con "CONSEJO PARA EL DM" -> Caja AZUL con texto azul
    - Estilo "Normal"                -> Párrafo de texto justificado
    - Listas con viñetas             -> Listas
    - Imágenes embebidas             -> Se insertan automáticamente
"""

import argparse
import io
import os
import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table as TablaDocx
from docx.text.paragraph import Paragraph as ParrafoDocx
from PIL import Image as PILImage

from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A3, A4, A5, A6, B5, LETTER, LEGAL, ELEVENSEVENTEEN
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, PageBreak, ListFlowable, ListItem, Image,
    Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# ============== Parámetros visuales (modificables) ==============
COLOR_PRIMARIO   = HexColor("#8B0000")   # rojo oscuro (títulos)
COLOR_SECUNDARIO = HexColor("#1a1a1a")
COLOR_FONDO_PAGINA = HexColor("#F7F1E3")

# Caja "Consejo para el DM" (azul)
COLOR_AZUL_TEXTO = HexColor("#1F3A93")
COLOR_AZUL_BORDE = HexColor("#5B8DEF")
COLOR_AZUL_FONDO = HexColor("#EAF1FB")

# Caja "Cita" (amarillo)
COLOR_AMA_TEXTO  = HexColor("#000000")
COLOR_AMA_BORDE  = HexColor("#D9B96A")
COLOR_AMA_FONDO  = HexColor("#FBF3DC")

# Caja "Información adicional" (verde azulado)
COLOR_INFO_TEXTO = HexColor("#0F4C5C")
COLOR_INFO_BORDE = HexColor("#2A9D8F")
COLOR_INFO_FONDO = HexColor("#E6F7F5")

# Caja "Enemigo" (rojo)
COLOR_ENEMIGO_TEXTO = HexColor("#7A1C1C")
COLOR_ENEMIGO_BORDE = HexColor("#C0392B")
COLOR_ENEMIGO_FONDO = HexColor("#FDECEC")

# Caja "NPC" (gris)
COLOR_NPC_TEXTO = HexColor("#444444")
COLOR_NPC_BORDE = HexColor("#8D99AE")
COLOR_NPC_FONDO = HexColor("#F1F3F5")

# Caja "Aliado" (verde)
COLOR_ALIADO_TEXTO = HexColor("#1E5631")
COLOR_ALIADO_BORDE = HexColor("#4CAF50")
COLOR_ALIADO_FONDO = HexColor("#EAF7EE")

FUENTE_TITULO = "Helvetica-Bold"
FUENTE_TEXTO  = "Helvetica"
TAMANO_PAGINA = A4
MARGEN        = 2 * cm

# Ruta de ejemplo para la imagen de portada (cámbiala cuando tengas la tuya)
IMAGEN_PORTADA_PREDETERMINADA = r"C:\ruta\a\tu\imagen_portada.jpg"
# ==================================================================

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


def construir_estilos():
    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="PortadaTitulo",
        fontName=FUENTE_TITULO, fontSize=36, leading=42,
        textColor=COLOR_PRIMARIO, alignment=TA_CENTER, spaceAfter=20,
    ))
    estilos.add(ParagraphStyle(
        name="PortadaSubtitulo",
        fontName=FUENTE_TEXTO, fontSize=16, leading=20,
        textColor=COLOR_SECUNDARIO, alignment=TA_CENTER, spaceAfter=10,
    ))
    estilos.add(ParagraphStyle(
        name="PortadaAutor",
        fontName=FUENTE_TEXTO, fontSize=13, leading=18,
        textColor=COLOR_SECUNDARIO, alignment=TA_CENTER,
    ))
    estilos.add(ParagraphStyle(
        name="H1",
        fontName=FUENTE_TITULO, fontSize=22, leading=26,
        textColor=COLOR_PRIMARIO, spaceBefore=18, spaceAfter=12,
    ))
    estilos.add(ParagraphStyle(
        name="H2",
        fontName=FUENTE_TITULO, fontSize=16, leading=20,
        textColor=COLOR_PRIMARIO, spaceBefore=14, spaceAfter=8,
    ))
    estilos.add(ParagraphStyle(
        name="H3",
        fontName=FUENTE_TITULO, fontSize=13, leading=16,
        textColor=COLOR_SECUNDARIO, spaceBefore=10, spaceAfter=6,
    ))
    estilos.add(ParagraphStyle(
        name="Cuerpo",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=black, alignment=TA_JUSTIFY, spaceAfter=8,
    ))
    # Caja AMARILLA (Citas)
    estilos.add(ParagraphStyle(
        name="CajaCita",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_AMA_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_AMA_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_AMA_FONDO,
    ))
    # Caja VERDE-AZULADA (Información adicional útil, no obligatoria)
    estilos.add(ParagraphStyle(
        name="CajaInfoAdicional",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_INFO_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_INFO_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_INFO_FONDO,
    ))
    # Caja AZUL (Consejo para el DM)
    estilos.add(ParagraphStyle(
        name="CajaConsejoDm",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_AZUL_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_AZUL_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_AZUL_FONDO,
    ))
    estilos.add(ParagraphStyle(
        name="CajaNpc",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_NPC_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_NPC_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_NPC_FONDO,
    ))
    estilos.add(ParagraphStyle(
        name="CajaEnemigo",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_ENEMIGO_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_ENEMIGO_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_ENEMIGO_FONDO,
    ))
    estilos.add(ParagraphStyle(
        name="CajaAliado",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_ALIADO_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_ALIADO_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_ALIADO_FONDO,
    ))
    estilos.add(ParagraphStyle(
        name="TituloIndice",
        fontName=FUENTE_TITULO, fontSize=22, leading=26,
        textColor=COLOR_PRIMARIO, alignment=TA_CENTER, spaceAfter=20,
    ))
    return estilos


def estilo_para_parrafo(p):
    nombre = (p.style.name or "").lower()
    if "heading 1" in nombre or "título 1" in nombre or "titulo 1" in nombre:
        return "H1"
    if "heading 2" in nombre or "título 2" in nombre or "titulo 2" in nombre:
        return "H2"
    if "heading 3" in nombre or "título 3" in nombre or "titulo 3" in nombre:
        return "H3"
    if ("información adicional" in nombre or "informacion adicional" in nombre or
            "info adicional" in nombre):
        return "CajaInfoAdicional"
    if "consejos" in nombre or "consejo dm" in nombre or "consejo para el dm" in nombre:
        return "CajaConsejoDm"
    if "quote" in nombre or "cita" in nombre:
        return "CajaCita"
    if "list" in nombre or "lista" in nombre:
        return "Lista"
    return "Cuerpo"


def _markdown_en_linea_a_html(texto):
    """Convierte **negrita** y *cursiva* (estilo Markdown) a HTML.

    Se aplica solo si el texto no contiene ya etiquetas <b>/<i> de los runs.
    """
    # **texto** -> <b>texto</b>  (no codicioso, sin saltos de línea)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    # *texto* -> <i>texto</i>  (evita coincidir con ** restantes)
    texto = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", texto)
    return texto


def _escapar_html(texto):
    return (texto.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def _escapar_atributo_html(texto):
    return _escapar_html(texto).replace('"', '&quot;')


def _texto_de_segmento_xml(segmento_xml):
    partes = []
    for nodo in segmento_xml.iter():
        if nodo.tag == qn("w:t"):
            partes.append(nodo.text or "")
        elif nodo.tag == qn("w:tab"):
            partes.append("    ")
        elif nodo.tag in (qn("w:br"), qn("w:cr")):
            partes.append("<br/>")
    return "".join(partes)


def _segmento_xml_a_html(segmento_xml):
    texto = _texto_de_segmento_xml(segmento_xml)
    if not texto:
        return "", False

    usa_formato = False
    if "<br/>" not in texto:
        texto = _escapar_html(texto)

    propiedades = segmento_xml.find(qn("w:rPr"))
    if propiedades is not None:
        if propiedades.find(qn("w:b")) is not None:
            texto = f"<b>{texto}</b>"
            usa_formato = True
        if propiedades.find(qn("w:i")) is not None:
            texto = f"<i>{texto}</i>"
            usa_formato = True
        if propiedades.find(qn("w:u")) is not None:
            texto = f"<u>{texto}</u>"
            usa_formato = True
    return texto, usa_formato


def _hipervinculo_xml_a_html(hipervinculo_xml, parte_documento):
    partes = []
    usa_formato = False

    for segmento_xml in hipervinculo_xml.findall(qn("w:r")):
        html_segmento, formato_segmento = _segmento_xml_a_html(segmento_xml)
        if html_segmento:
            partes.append(html_segmento)
        usa_formato = usa_formato or formato_segmento

    texto_html = "".join(partes)
    if not texto_html:
        return "", usa_formato

    rel_id = hipervinculo_xml.get(qn("r:id"))
    anchor = hipervinculo_xml.get(qn("w:anchor"))
    destino = ""
    if rel_id and rel_id in parte_documento.rels:
        destino = parte_documento.rels[rel_id].target_ref or ""
    elif anchor:
        destino = f"#{anchor}"

    if not destino:
        return texto_html, usa_formato

    destino = _escapar_atributo_html(destino)
    texto_html = (
        f'<link href="{destino}">'
        f'<u><font color="#0563C1">{texto_html}</font></u>'
        f'</link>'
    )
    return texto_html, True


def parrafo_a_html(parrafo):
    """Convierte párrafos de Word a HTML para ReportLab, incluyendo enlaces."""
    partes = []
    algun_formato_run = False

    for nodo in parrafo._p.iterchildren():
        if nodo.tag == qn("w:r"):
            html_segmento, formato_segmento = _segmento_xml_a_html(nodo)
            if html_segmento:
                partes.append(html_segmento)
            algun_formato_run = algun_formato_run or formato_segmento
        elif nodo.tag == qn("w:hyperlink"):
            html_enlace, formato_enlace = _hipervinculo_xml_a_html(nodo, parrafo.part)
            if html_enlace:
                partes.append(html_enlace)
            algun_formato_run = algun_formato_run or formato_enlace

    html = "".join(partes)
    # Si Word no marcó nada en negrita/cursiva, interpretar Markdown en línea (**...**, *...*).
    if not algun_formato_run and ("*" in html):
        html = _markdown_en_linea_a_html(html)
    return html


def extraer_imagenes_de_parrafo(parrafo, documento_word):
    """Devuelve descriptores de imágenes embebidas en el párrafo."""
    imagenes = []
    for blip in parrafo._element.findall(".//" + qn("a:blip")):
        rId = blip.get(qn("r:embed"))
        if rId and rId in documento_word.part.related_parts:
            blob = documento_word.part.related_parts[rId].blob
            dimensiones = _leer_dimensiones_imagen(blob)
            if dimensiones is None:
                continue
            ancho_px, alto_px = dimensiones
            imagenes.append({
                "blob": blob,
                "ancho_px": ancho_px,
                "alto_px": alto_px,
            })
    return imagenes


def _leer_dimensiones_imagen(blob):
    bio = io.BytesIO(blob)
    try:
        with PILImage.open(bio) as im:
            w, h = im.size
    except Exception:
        return None
    if not w or not h:
        return None
    return float(w), float(h)


def crear_flujo_imagen(blob, ancho_max, alto_max=None, permitir_ampliacion=True):
    """Crea un `Image` escalado para que entre en el área disponible."""
    dimensiones = _leer_dimensiones_imagen(blob)
    if dimensiones is None:
        return None
    w, h = dimensiones

    bio = io.BytesIO(blob)
    bio.seek(0)
    escala_ancho = float(ancho_max) / float(w) if ancho_max else 1.0
    escala_alto = float(alto_max) / float(h) if alto_max else 1.0
    escala = min(escala_ancho, escala_alto)
    if not permitir_ampliacion:
        escala = min(1.0, escala)
    ancho = max(1.0, float(w) * escala)
    alto = max(1.0, float(h) * escala)
    img = Image(bio, width=ancho, height=alto)
    img.hAlign = "CENTER"
    return img


def _item_caja_grupo_imagenes(imagenes):
    return {
        "tipo": "grupo_imagenes",
        "imagenes": list(imagenes),
    }


def _crear_items_imagenes(imagenes):
    if not imagenes:
        return []
    if len(imagenes) >= 2:
        return [_item_caja_grupo_imagenes(imagenes)]
    return [_item_caja_imagen(imagenes[0])]


def _crear_fila_de_imagenes(imagenes, ancho_disponible, alto_max=None, espacio=10):
    validas = [imagen for imagen in imagenes if imagen.get("ancho_px") and imagen.get("alto_px")]
    if not validas:
        return None

    if len(validas) == 1:
        return crear_flujo_imagen(
            validas[0]["blob"],
            ancho_disponible,
            alto_max=alto_max,
            permitir_ampliacion=True,
        )

    suma_relaciones = sum(imagen["ancho_px"] / imagen["alto_px"] for imagen in validas)
    ancho_libre = max(1.0, ancho_disponible - (espacio * (len(validas) - 1)))
    altura_objetivo = ancho_libre / suma_relaciones if suma_relaciones else 0
    if alto_max:
        altura_objetivo = min(altura_objetivo, float(alto_max))
    if altura_objetivo <= 0:
        return None

    anchos = [max(1.0, (imagen["ancho_px"] / imagen["alto_px"]) * altura_objetivo) for imagen in validas]
    ancho_minimo = min(anchos)
    altura_minima = altura_objetivo

    if altura_minima < 72 or ancho_minimo < 90:
        return None

    celdas = []
    for imagen, ancho in zip(validas, anchos):
        flujo = crear_flujo_imagen(
            imagen["blob"],
            ancho,
            alto_max=altura_objetivo,
            permitir_ampliacion=True,
        )
        if flujo is None:
            return None
        celdas.append(flujo)

    tabla = Table([celdas], colWidths=anchos, hAlign="CENTER")
    tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), espacio / 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), espacio / 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tabla


def _crear_flujos_imagenes(imagenes, ancho_disponible, alto_max=None, espacio=10):
    if not imagenes:
        return []

    fila = _crear_fila_de_imagenes(imagenes, ancho_disponible, alto_max=alto_max, espacio=espacio)
    if fila is not None:
        return [fila]

    flujos = []
    for imagen in imagenes:
        flujo = crear_flujo_imagen(
            imagen["blob"],
            ancho_disponible,
            alto_max=alto_max,
            permitir_ampliacion=True,
        )
        if flujo is not None:
            flujos.append(flujo)
    return flujos


def es_consejo_dm(texto_plano):
    # Quita asteriscos, espacios y comillas iniciales para tolerar formatos
    # tipo Markdown (**CONSEJO PARA EL DM...**).
    limpio = texto_plano.lstrip(" *_“\"'\t").lower()
    return limpio.startswith("consejo para el dm")


def _dividir_html_en_salto(html, numero_saltos):
    if numero_saltos <= 0:
        return html, ""

    tokens = re.split(r"(<[^>]+>)", html)
    izquierda = []
    derecha = []
    pila_izquierda = []
    pila_derecha = []
    tags_en_split = []
    saltos_vistos = 0
    dividido = False
    derecha_iniciada = False

    def _parsear_tag(tag):
        inner = tag[1:-1].strip()
        nombre = inner.lstrip("/").split()[0].lower() if inner else ""
        if nombre.startswith("br"):
            nombre = "br"
        es_cierre = inner.startswith("/")
        es_autocierre = inner.endswith("/") or nombre == "br"
        return nombre, es_cierre, es_autocierre

    def _actualizar_pila(pila, nombre, es_cierre, es_autocierre, tag):
        if es_cierre:
            for k in range(len(pila) - 1, -1, -1):
                if pila[k][0] == nombre:
                    del pila[k]
                    break
        elif not es_autocierre and nombre:
            pila.append((nombre, tag))

    for token in tokens:
        if token == "":
            continue

        es_tag = token.startswith("<") and token.endswith(">")
        if not es_tag:
            if dividido:
                if not derecha_iniciada and tags_en_split:
                    derecha.extend(tag for _, tag in tags_en_split)
                derecha_iniciada = True
                derecha.append(token)
            else:
                izquierda.append(token)
            continue

        nombre, es_cierre, es_autocierre = _parsear_tag(token)
        if not dividido and nombre == "br":
            saltos_vistos += 1
            if saltos_vistos >= numero_saltos:
                tags_en_split = list(pila_izquierda)
                pila_derecha = list(tags_en_split)
                dividido = True
                continue
            izquierda.append(token)
            continue

        if dividido:
            if nombre == "br" and not derecha_iniciada:
                continue
            if not derecha_iniciada and tags_en_split:
                derecha.extend(tag for _, tag in tags_en_split)
            derecha_iniciada = True
            derecha.append(token)
            _actualizar_pila(pila_derecha, nombre, es_cierre, es_autocierre, token)
        else:
            izquierda.append(token)
            _actualizar_pila(pila_izquierda, nombre, es_cierre, es_autocierre, token)

    if not dividido:
        return html, ""

    for nombre, _ in reversed(tags_en_split):
        izquierda.append(f"</{nombre}>")
    for nombre, _ in reversed(pila_derecha):
        derecha.append(f"</{nombre}>")

    return "".join(izquierda).rstrip(), "".join(derecha).lstrip()


def _buscar_prefijo_embebido(texto_plano, detector):
    lineas = re.split(r"\r\n|\r|\n", texto_plano or "")
    if len(lineas) < 2:
        return None

    hay_contenido_antes = False
    saltos_previos = 0
    for linea in lineas:
        if detector(linea):
            if hay_contenido_antes:
                return saltos_previos
        elif linea.strip():
            hay_contenido_antes = True
        saltos_previos += 1
    return None


def _extraer_bloque_prefijo_embebido(texto_html, texto_plano, detector):
    numero_saltos = _buscar_prefijo_embebido(texto_plano, detector)
    if numero_saltos is None:
        return None

    antes_html, bloque_html = _dividir_html_en_salto(texto_html, numero_saltos)
    lineas = re.split(r"\r\n|\r|\n", texto_plano or "")
    antes_plano = "\n".join(lineas[:numero_saltos]).strip()
    bloque_plano = "\n".join(lineas[numero_saltos:]).lstrip()
    if not antes_html.strip() or not bloque_html.strip() or not bloque_plano.strip():
        return None
    return antes_html, antes_plano, bloque_html, bloque_plano


def _quitar_prefijo_visible_en_html(html, caracteres_visibles):
    if caracteres_visibles <= 0:
        return html

    resultado = []
    pila_tags = []
    caracteres_restantes = caracteres_visibles
    iniciado = False
    i = 0
    n = len(html)

    while i < n:
        if html[i] == "<":
            j = html.find(">", i)
            if j == -1:
                break
            tag = html[i:j + 1]
            inner = tag[1:-1].strip()

            if inner.startswith("/"):
                nombre = inner[1:].split()[0].lower()
                for k in range(len(pila_tags) - 1, -1, -1):
                    if pila_tags[k][0] == nombre:
                        del pila_tags[k]
                        break
                if iniciado:
                    resultado.append(tag)
            elif not inner.endswith("/") and not inner.startswith("!"):
                nombre = inner.split()[0].lower()
                if nombre not in ("br",):
                    pila_tags.append((nombre, tag))
                if iniciado:
                    resultado.append(tag)
            else:
                if iniciado:
                    resultado.append(tag)
            i = j + 1
            continue

        if caracteres_restantes > 0:
            caracteres_restantes -= 1
            if caracteres_restantes == 0:
                iniciado = True
                resultado.extend(tag for _, tag in pila_tags)
            i += 1
            continue

        if not iniciado:
            iniciado = True
            resultado.extend(tag for _, tag in pila_tags)

        resultado.append(html[i])
        i += 1

    return "".join(resultado).lstrip()


def decorar_consejo_dm_html(texto_html):
    texto_plano = re.sub(r"<[^>]+>", "", texto_html)
    match = re.match(
        r'^\s*(?P<prefijo>consejo para el dm)\s*(?P<detalle>\([^)]*\))?\s*:?\s*',
        texto_plano,
        flags=re.IGNORECASE,
    )
    titulo = "Consejo para el DM"
    cuerpo = texto_html
    if match:
        detalle = (match.group("detalle") or "").strip()
        if detalle:
            titulo = f"{titulo} {detalle}"
        cuerpo = _quitar_prefijo_visible_en_html(texto_html, len(match.group(0)))

    etiqueta = (
        f'<font color="#{COLOR_AZUL_TEXTO.hexval()[2:]}"><b>{titulo}</b></font><br/>'
    )
    return etiqueta + cuerpo


def es_info_adicional(texto_plano):
    limpio = texto_plano.lstrip(" *_“\"'\t").lower()
    return (
        limpio.startswith("información adicional")
        or limpio.startswith("informacion adicional")
        or limpio.startswith("info adicional")
        or limpio.startswith("dato adicional")
    )


def decorar_info_adicional_html(texto_html):
    etiqueta = (
        f'<font color="#{COLOR_INFO_BORDE.hexval()[2:]}"><b>[i] Información adicional</b></font><br/>'
    )
    patrones = [
        r'^\s*(información adicional|informacion adicional|info adicional|dato adicional)\s*:\s*',
    ]
    for patron in patrones:
        reemplazado = re.sub(patron, etiqueta, texto_html, count=1, flags=re.IGNORECASE)
        if reemplazado != texto_html:
            return reemplazado
    return etiqueta + texto_html


def es_inicio_bloque_info(texto_plano):
    limpio = texto_plano.strip().lower()
    return limpio in (":::info", "::: info", ":::informacion", ":::información")


def es_fin_bloque_info(texto_plano):
    return texto_plano.strip() == ":::"


def es_inicio_bloque_consejo(texto_plano):
    limpio = texto_plano.strip().lower()
    return limpio in (":::consejo", "::: consejo", ":::dm", "::: dm")


def es_inicio_bloque_cita(texto_plano):
    limpio = texto_plano.strip().lower()
    return limpio in (":::cita", "::: cita", ":::quote", "::: quote")


def es_inicio_bloque_npc(texto_plano):
    limpio = texto_plano.strip().lower()
    return limpio in (":::npc", "::: npc")


def es_inicio_bloque_enemigo(texto_plano):
    limpio = texto_plano.strip().lower()
    return limpio in (":::enemigo", "::: enemigo", ":::enemy", "::: enemy")


def es_inicio_bloque_aliado(texto_plano):
    limpio = texto_plano.strip().lower()
    return limpio in (":::aliado", "::: aliado", ":::ally", "::: ally")


def es_fin_bloque_manual(texto_plano):
    return texto_plano.strip() == ":::"


def _puntos_word(longitud):
    if longitud is None:
        return 0
    try:
        return float(longitud.pt)
    except Exception:
        return 0


def _es_lista_parrafo(parrafo):
    nombre = (parrafo.style.name or "").lower()
    if "list" in nombre or "lista" in nombre:
        return True
    propiedades = parrafo._p.find(qn("w:pPr"))
    return propiedades is not None and propiedades.find(qn("w:numPr")) is not None


def _nivel_lista_parrafo(parrafo):
    propiedades = parrafo._p.find(qn("w:pPr"))
    if propiedades is not None:
        num_pr = propiedades.find(qn("w:numPr"))
        if num_pr is not None:
            ilvl = num_pr.find(qn("w:ilvl"))
            if ilvl is not None:
                try:
                    return max(0, int(ilvl.get(qn("w:val")) or 0))
                except (TypeError, ValueError):
                    pass

    nombre = (parrafo.style.name or "").lower()
    match = re.search(r"(?:list|lista)[^\d]*(\d+)$", nombre)
    if match:
        return max(0, int(match.group(1)) - 1)
    return 0


def _item_caja_desde_parrafo(parrafo, texto_html):
    return {
        "tipo": "texto",
        "html": texto_html,
        "es_lista": _es_lista_parrafo(parrafo),
        "nivel_lista": _nivel_lista_parrafo(parrafo),
        "sangria_izquierda": _puntos_word(parrafo.paragraph_format.left_indent),
        "sangria_primera_linea": _puntos_word(parrafo.paragraph_format.first_line_indent),
    }


def _item_caja_plano(texto_html):
    return {
        "tipo": "texto",
        "html": texto_html,
        "es_lista": False,
        "nivel_lista": 0,
        "sangria_izquierda": 0,
        "sangria_primera_linea": 0,
    }


def _item_caja_imagen(imagen):
    return {
        "tipo": "imagen",
        "imagen": imagen,
    }


def _item_caja_tabla(tabla_docx):
    return {
        "tipo": "tabla",
        "tabla": tabla_docx,
    }


def _agregar_imagenes_a_bloque(bloque, imagenes):
    for item in _crear_items_imagenes(imagenes):
        bloque.append(item)


def _iterar_elementos_documento(documento_word):
    for child in documento_word.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield "parrafo", ParrafoDocx(child, documento_word)
        elif child.tag == qn("w:tbl"):
            yield "tabla", TablaDocx(child, documento_word)


def _celda_docx_a_html(celda):
    partes = []
    for parrafo in celda.paragraphs:
        html = parrafo_a_html(parrafo).strip()
        if html:
            partes.append(html)
    return "<br/><br/>".join(partes) if partes else "&nbsp;"


def _tabla_docx_a_flujo(tabla_docx, ancho_max, estilo_base):
    filas = []
    max_cols = 0
    for fila in tabla_docx.rows:
        celdas = [_celda_docx_a_html(celda) for celda in fila.cells]
        filas.append(celdas)
        max_cols = max(max_cols, len(celdas))

    if not filas or max_cols == 0:
        return None

    estilo_celda = ParagraphStyle(
        name=f"{estilo_base.name}TablaCelda",
        parent=estilo_base,
        alignment=TA_LEFT,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0,
        spaceBefore=0,
        spaceAfter=0,
        borderWidth=0,
        borderPadding=0,
        backColor=None,
    )

    datos = []
    for fila in filas:
        fila_ext = fila + ["&nbsp;"] * (max_cols - len(fila))
        datos.append([Paragraph(celda_html, estilo_celda) for celda_html in fila_ext])

    ancho_col = ancho_max / max_cols
    tabla = Table(datos, colWidths=[ancho_col] * max_cols, hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.75, estilo_base.borderColor),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, 0), estilo_base.borderColor),
        ("TEXTCOLOR", (0, 0), (-1, 0), estilo_base.backColor),
        ("BACKGROUND", (0, 1), (-1, -1), estilo_base.backColor),
    ]))
    return tabla


def _crear_titulo_decorado(titulo, color):
    return f'<font color="#{color.hexval()[2:]}"><b>{titulo}</b></font><br/>'


def decorar_npc_en_html(texto_html):
    return _crear_titulo_decorado("NPC", COLOR_NPC_TEXTO) + texto_html


def decorar_enemigo_en_html(texto_html):
    return _crear_titulo_decorado("Enemigo", COLOR_ENEMIGO_TEXTO) + texto_html


def decorar_aliado_en_html(texto_html):
    return _crear_titulo_decorado("Aliado", COLOR_ALIADO_TEXTO) + texto_html


def _estilo_interno_caja(estilo_base, item, sufijo):
    estilo = ParagraphStyle(
        name=f"{estilo_base.name}Interno{sufijo}",
        parent=estilo_base,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0,
        spaceBefore=0,
        spaceAfter=6,
        borderWidth=0,
        borderPadding=0,
        backColor=None,
    )

    if item["es_lista"]:
        nivel = item["nivel_lista"]
        sangria_word = max(0, item["sangria_izquierda"])
        sangria_base = max(16 + nivel * 14, 12 + sangria_word)
        estilo.leftIndent = sangria_base
        estilo.firstLineIndent = -10
        estilo.spaceAfter = 3
    else:
        estilo.leftIndent = max(0, item["sangria_izquierda"])
        estilo.firstLineIndent = item["sangria_primera_linea"]
    return estilo


def _crear_cabecera_decorada_caja(estilo_base, decorador, sufijo):
    estilo = _estilo_interno_caja(estilo_base, _item_caja_plano(""), sufijo)
    estilo.spaceAfter = 4
    return Paragraph(decorador(""), estilo)


def _centrar_en_fila(flowable, ancho):
    tabla = Table([[flowable]], colWidths=[ancho], hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tabla


def _agrupar_cabecera_y_bloque(cabecera, bloque, ancho):
    if cabecera is None:
        return bloque
    tabla = Table(
        [[cabecera], [bloque]],
        colWidths=[ancho],
        hAlign="LEFT",
        splitByRow=1,
    )
    tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    ]))
    return tabla


def _renderizar_caja(partes, estilo_base, ancho_total, decorador=None):
    contenido = []
    primer_bloque = True
    indice = 0
    ancho_interno = max(40, ancho_total - 20)
    alto_max_imagen = max(80, TAMANO_PAGINA[1] - (2 * MARGEN) - 48)

    for parte in partes:
        if parte is None:
            if contenido and not isinstance(contenido[-1], Spacer):
                contenido.append(Spacer(1, 6))
            continue

        if parte.get("tipo") == "tabla":
            cabecera = None
            if primer_bloque and decorador is not None:
                cabecera = _crear_cabecera_decorada_caja(estilo_base, decorador, indice)
                primer_bloque = False
                indice += 1

            tabla = _tabla_docx_a_flujo(parte.get("tabla"), ancho_interno, estilo_base)
            if tabla is not None:
                contenido.append(_agrupar_cabecera_y_bloque(cabecera, tabla, ancho_interno))
                contenido.append(Spacer(1, 6))
            continue

        if parte.get("tipo") == "imagen":
            cabecera = None
            if primer_bloque and decorador is not None:
                cabecera = _crear_cabecera_decorada_caja(estilo_base, decorador, indice)
                primer_bloque = False
                indice += 1

            flujo_imagen = crear_flujo_imagen(
                (parte.get("imagen") or {}).get("blob"),
                ancho_interno,
                alto_max=alto_max_imagen,
                permitir_ampliacion=True,
            )
            if flujo_imagen is not None:
                flujo_imagen.hAlign = "CENTER"
                imagen_centrada = _centrar_en_fila(flujo_imagen, ancho_interno)
                contenido.append(_agrupar_cabecera_y_bloque(cabecera, imagen_centrada, ancho_interno))
                contenido.append(Spacer(1, 8))
            continue

        if parte.get("tipo") == "grupo_imagenes":
            cabecera = None
            if primer_bloque and decorador is not None:
                cabecera = _crear_cabecera_decorada_caja(estilo_base, decorador, indice)
                primer_bloque = False
                indice += 1

            fila_imagenes = _crear_fila_de_imagenes(
                parte.get("imagenes") or [],
                ancho_interno,
                alto_max=alto_max_imagen,
            )
            if fila_imagenes is not None:
                contenido.append(_agrupar_cabecera_y_bloque(cabecera, fila_imagenes, ancho_interno))
                contenido.append(Spacer(1, 8))
            else:
                for flujo_imagen in _crear_flujos_imagenes(
                    parte.get("imagenes") or [],
                    ancho_interno,
                    alto_max=alto_max_imagen,
                ):
                    imagen_centrada = _centrar_en_fila(flujo_imagen, ancho_interno)
                    contenido.append(_agrupar_cabecera_y_bloque(cabecera, imagen_centrada, ancho_interno))
                    cabecera = None
                    contenido.append(Spacer(1, 8))
            continue

        html = (parte.get("html") or "").strip()
        if not html:
            continue

        if primer_bloque and decorador is not None:
            html = decorador(html)

        estilo = _estilo_interno_caja(estilo_base, parte, indice)
        bullet_text = "•" if parte["es_lista"] else None
        contenido.append(Paragraph(html, estilo, bulletText=bullet_text))
        primer_bloque = False
        indice += 1

    if not contenido:
        return None

    while contenido and isinstance(contenido[0], Spacer):
        contenido.pop(0)
    while contenido and isinstance(contenido[-1], Spacer):
        contenido.pop()

    if not contenido:
        return None

    filas = [[bloque] for bloque in contenido]
    tabla = Table(
        filas,
        colWidths=[ancho_total],
        hAlign="LEFT",
        splitByRow=1,
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), estilo_base.backColor),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBEFORE", (0, 0), (-1, -1), estilo_base.borderWidth, estilo_base.borderColor),
        ("LINEAFTER", (0, 0), (-1, -1), estilo_base.borderWidth, estilo_base.borderColor),
        ("LINEABOVE", (0, 0), (-1, 0), estilo_base.borderWidth, estilo_base.borderColor),
        ("LINEBELOW", (0, -1), (-1, -1), estilo_base.borderWidth, estilo_base.borderColor),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
    ]))
    tabla.spaceBefore = 4
    tabla.spaceAfter = 8
    return tabla


class DocumentoConIndice(BaseDocTemplate):
    """Plantilla de documento que notifica entradas al índice al pasar por H1 y H2."""
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        frame = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height, id="normal")
        self.addPageTemplates([
            PageTemplate(id="Todo", frames=frame, onPage=self._dibujar_fondo_pagina)
        ])
        self._contador_marcadores = 0

    def _dibujar_fondo_pagina(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(COLOR_FONDO_PAGINA)
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], stroke=0, fill=1)
        canvas.restoreState()

    def _crear_marcador(self, texto):
        self._contador_marcadores += 1
        texto_limpio = re.sub(r"\s+", "-", texto.strip())
        texto_limpio = re.sub(r"[^\w\-]", "", texto_limpio, flags=re.UNICODE)
        texto_limpio = texto_limpio[:60] or "seccion"
        return f"marcador-{self._contador_marcadores}-{texto_limpio}"

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            estilo = flowable.style.name
            texto = flowable.getPlainText()
            if estilo == "H1":
                marcador = self._crear_marcador(texto)
                self.canv.bookmarkPage(marcador)
                self.canv.addOutlineEntry(texto, marcador, level=0, closed=False)
                self.notify("TOCEntry", (0, texto, self.page))
            elif estilo == "H2":
                marcador = self._crear_marcador(texto)
                self.canv.bookmarkPage(marcador)
                self.canv.addOutlineEntry(texto, marcador, level=1, closed=False)
                self.notify("TOCEntry", (1, texto, self.page))
            elif estilo == "H3":
                marcador = self._crear_marcador(texto)
                self.canv.bookmarkPage(marcador)
                self.canv.addOutlineEntry(texto, marcador, level=2, closed=False)


def construir_pdf(ruta_docx, ruta_pdf, titulo=None, autor=None,
                  subtitulo=None, imagen_portada=None):
    documento_word = Document(ruta_docx)
    estilos = construir_estilos()

    documento_pdf = DocumentoConIndice(
        str(ruta_pdf),
        pagesize=TAMANO_PAGINA,
        leftMargin=MARGEN, rightMargin=MARGEN,
        topMargin=MARGEN, bottomMargin=MARGEN,
        title=titulo or "Aventura",
        author=autor or "",
    )

    ancho_util = TAMANO_PAGINA[0] - 2 * MARGEN
    historia = []

    # ---------- Portada ----------
    if titulo or subtitulo or autor or imagen_portada:
        if imagen_portada and os.path.exists(imagen_portada):
            try:
                with PILImage.open(imagen_portada) as im:
                    w, h = im.size
                ratio = (h / w) if w else 1
                imagen_portada_flujo = Image(imagen_portada,
                                             width=ancho_util,
                                             height=ancho_util * ratio)
                imagen_portada_flujo.hAlign = "CENTER"
                historia.append(Spacer(1, 1 * cm))
                historia.append(imagen_portada_flujo)
                historia.append(Spacer(1, 1 * cm))
            except Exception as e:
                print(f"⚠️  No se pudo cargar la imagen de portada: {e}")
                historia.append(Spacer(1, 6 * cm))
        else:
            if imagen_portada:
                print(f"ℹ️  Imagen de portada no encontrada en: {imagen_portada} "
                      f"(se omite). Cambia la ruta cuando tengas la imagen.")
            historia.append(Spacer(1, 6 * cm))

        if titulo:
            historia.append(Paragraph(titulo, estilos["PortadaTitulo"]))
        if subtitulo:
            historia.append(Paragraph(subtitulo, estilos["PortadaSubtitulo"]))
        if autor:
            historia.append(Spacer(1, 1 * cm))
            historia.append(Paragraph(f"por <b>{autor}</b>", estilos["PortadaAutor"]))
        historia.append(PageBreak())

    # ---------- Tabla de contenidos ----------
    historia.append(Paragraph("Índice", estilos["TituloIndice"]))
    indice = TableOfContents()
    indice.levelStyles = [
        ParagraphStyle(name="IndiceNivel1", fontName=FUENTE_TITULO, fontSize=12,
                       leading=18, textColor=COLOR_PRIMARIO, leftIndent=0),
        ParagraphStyle(name="IndiceNivel2", fontName=FUENTE_TEXTO, fontSize=11,
                       leading=16, textColor=COLOR_SECUNDARIO, leftIndent=18),
    ]
    historia.append(indice)
    historia.append(PageBreak())

    # ---------- Contenido ----------
    items_lista_actual = []
    citas_pendientes = []          # bloque de citas consecutivas a fusionar
    vacios_desde_ultima_cita = 0   # nº de párrafos vacíos vistos tras la última cita
    MAX_VACIOS_FUSION_CITA = 2     # hasta 2 saltos de renglón => misma caja
    consejos_pendientes = []       # bloque de consejos consecutivos a fusionar
    modo_consejos = None           # "estilo" | "prefijo"
    vacios_desde_ultimo_consejo = 0
    MAX_VACIOS_FUSION_CONSEJO = 2  # hasta 2 saltos de renglón => misma caja
    infos_pendientes = []          # bloque de notas informativas consecutivas a fusionar
    modo_infos = None              # "estilo" | "prefijo"
    vacios_desde_ultima_info = 0   # nº de párrafos vacíos vistos tras la última info
    MAX_VACIOS_FUSION_INFO = 2     # hasta 2 saltos de renglón => misma caja

    bloque_consejo_manual = []     # bloque de párrafos dentro de :::consejo ... :::
    dentro_consejo_manual = False
    bloque_cita_manual = []        # bloque de párrafos dentro de :::cita ... :::
    dentro_cita_manual = False
    bloque_npc_manual = []         # bloque de párrafos dentro de :::npc ... :::
    dentro_npc_manual = False
    bloque_enemigo_manual = []     # bloque de párrafos dentro de :::enemigo ... :::
    dentro_enemigo_manual = False
    bloque_aliado_manual = []      # bloque de párrafos dentro de :::aliado ... :::
    dentro_aliado_manual = False
    bloque_info_manual = []        # bloque de párrafos dentro de :::info ... :::
    dentro_info = False

    def agregar_contenido_a_bloque_activo(item_caja, imagenes):
        if dentro_info:
            if item_caja is not None:
                bloque_info_manual.append(item_caja)
            if imagenes:
                _agregar_imagenes_a_bloque(bloque_info_manual, imagenes)
            return True
        if dentro_consejo_manual:
            if item_caja is not None:
                bloque_consejo_manual.append(item_caja)
            if imagenes:
                _agregar_imagenes_a_bloque(bloque_consejo_manual, imagenes)
            return True
        if dentro_cita_manual:
            if item_caja is not None:
                bloque_cita_manual.append(item_caja)
            if imagenes:
                _agregar_imagenes_a_bloque(bloque_cita_manual, imagenes)
            return True
        if dentro_npc_manual:
            if item_caja is not None:
                bloque_npc_manual.append(item_caja)
            if imagenes:
                _agregar_imagenes_a_bloque(bloque_npc_manual, imagenes)
            return True
        if dentro_enemigo_manual:
            if item_caja is not None:
                bloque_enemigo_manual.append(item_caja)
            if imagenes:
                _agregar_imagenes_a_bloque(bloque_enemigo_manual, imagenes)
            return True
        if dentro_aliado_manual:
            if item_caja is not None:
                bloque_aliado_manual.append(item_caja)
            if imagenes:
                _agregar_imagenes_a_bloque(bloque_aliado_manual, imagenes)
            return True
        return False

    def agregar_salto_a_bloque_activo():
        if dentro_consejo_manual:
            bloque_consejo_manual.append(None)
            return True
        if dentro_cita_manual:
            bloque_cita_manual.append(None)
            return True
        if dentro_npc_manual:
            bloque_npc_manual.append(None)
            return True
        if dentro_enemigo_manual:
            bloque_enemigo_manual.append(None)
            return True
        if dentro_aliado_manual:
            bloque_aliado_manual.append(None)
            return True
        if dentro_info:
            bloque_info_manual.append(None)
            return True
        return False

    def vaciar_lista():
        if items_lista_actual:
            historia.append(ListFlowable(
                [ListItem(Paragraph(t, estilos["Cuerpo"]), leftIndent=12)
                 for t in items_lista_actual],
                bulletType="bullet", start="•",
            ))
            historia.append(Spacer(1, 6))
            items_lista_actual.clear()

    def vaciar_citas():
        if citas_pendientes:
            caja = _renderizar_caja(citas_pendientes, estilos["CajaCita"], ancho_util)
            if caja is not None:
                historia.append(caja)
            citas_pendientes.clear()

    def vaciar_consejos():
        nonlocal vacios_desde_ultimo_consejo, modo_consejos
        if consejos_pendientes:
            caja = _renderizar_caja(
                consejos_pendientes,
                estilos["CajaConsejoDm"],
                ancho_util,
                decorador=decorar_consejo_dm_html,
            )
            if caja is not None:
                historia.append(caja)
            consejos_pendientes.clear()
        vacios_desde_ultimo_consejo = 0
        modo_consejos = None

    def vaciar_infos():
        nonlocal vacios_desde_ultima_info, modo_infos
        if infos_pendientes:
            caja = _renderizar_caja(
                infos_pendientes,
                estilos["CajaInfoAdicional"],
                ancho_util,
                decorador=decorar_info_adicional_html,
            )
            if caja is not None:
                historia.append(caja)
            infos_pendientes.clear()
        vacios_desde_ultima_info = 0
        modo_infos = None

    def emitir_consejo_manual():
        nonlocal dentro_consejo_manual
        if bloque_consejo_manual:
            caja = _renderizar_caja(
                bloque_consejo_manual,
                estilos["CajaConsejoDm"],
                ancho_util,
                decorador=decorar_consejo_dm_html,
            )
            if caja is not None:
                historia.append(caja)
            bloque_consejo_manual.clear()
        dentro_consejo_manual = False

    def emitir_cita_manual():
        nonlocal dentro_cita_manual
        if bloque_cita_manual:
            caja = _renderizar_caja(
                bloque_cita_manual,
                estilos["CajaCita"],
                ancho_util,
            )
            if caja is not None:
                historia.append(caja)
            bloque_cita_manual.clear()
        dentro_cita_manual = False

    def emitir_npc_manual():
        nonlocal dentro_npc_manual
        if bloque_npc_manual:
            caja = _renderizar_caja(
                bloque_npc_manual,
                estilos["CajaNpc"],
                ancho_util,
                decorador=decorar_npc_en_html,
            )
            if caja is not None:
                historia.append(caja)
            bloque_npc_manual.clear()
        dentro_npc_manual = False

    def emitir_enemigo_manual():
        nonlocal dentro_enemigo_manual
        if bloque_enemigo_manual:
            caja = _renderizar_caja(
                bloque_enemigo_manual,
                estilos["CajaEnemigo"],
                ancho_util,
                decorador=decorar_enemigo_en_html,
            )
            if caja is not None:
                historia.append(caja)
            bloque_enemigo_manual.clear()
        dentro_enemigo_manual = False

    def emitir_aliado_manual():
        nonlocal dentro_aliado_manual
        if bloque_aliado_manual:
            caja = _renderizar_caja(
                bloque_aliado_manual,
                estilos["CajaAliado"],
                ancho_util,
                decorador=decorar_aliado_en_html,
            )
            if caja is not None:
                historia.append(caja)
            bloque_aliado_manual.clear()
        dentro_aliado_manual = False

    def emitir_info_adicional():
        nonlocal dentro_info
        if bloque_info_manual:
            caja = _renderizar_caja(
                bloque_info_manual,
                estilos["CajaInfoAdicional"],
                ancho_util,
                decorador=decorar_info_adicional_html,
            )
            if caja is not None:
                historia.append(caja)
            bloque_info_manual.clear()
        dentro_info = False

    for tipo_elemento, elemento in _iterar_elementos_documento(documento_word):
        if tipo_elemento == "tabla":
            tabla_docx = elemento
            item_tabla = _item_caja_tabla(tabla_docx)

            if agregar_contenido_a_bloque_activo(item_tabla, []):
                continue

            vaciar_consejos()
            vaciar_infos()
            emitir_info_adicional()
            emitir_consejo_manual()
            emitir_cita_manual()
            emitir_npc_manual()
            emitir_enemigo_manual()
            emitir_aliado_manual()
            vaciar_citas()
            vaciar_lista()
            continue

        parrafo = elemento
        # 1) Imágenes embebidas en el párrafo
        imagenes = extraer_imagenes_de_parrafo(parrafo, documento_word)

        texto_html = parrafo_a_html(parrafo)
        texto_plano = parrafo.text or ""

        if es_inicio_bloque_info(texto_plano):
            vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            emitir_cita_manual()
            emitir_npc_manual()
            emitir_enemigo_manual()
            emitir_aliado_manual()
            vaciar_citas()
            vaciar_lista()
            dentro_info = True
            bloque_info_manual.clear()
            continue

        if es_inicio_bloque_consejo(texto_plano):
            vaciar_consejos()
            vaciar_infos()
            emitir_info_adicional()
            emitir_cita_manual()
            emitir_npc_manual()
            emitir_enemigo_manual()
            emitir_aliado_manual()
            vaciar_citas()
            vaciar_lista()
            dentro_consejo_manual = True
            bloque_consejo_manual.clear()
            continue

        if es_inicio_bloque_cita(texto_plano):
            vaciar_consejos()
            vaciar_infos()
            emitir_info_adicional()
            emitir_consejo_manual()
            emitir_npc_manual()
            emitir_enemigo_manual()
            emitir_aliado_manual()
            vaciar_citas()
            vaciar_lista()
            dentro_cita_manual = True
            bloque_cita_manual.clear()
            continue

        if es_inicio_bloque_npc(texto_plano):
            vaciar_consejos()
            vaciar_infos()
            emitir_info_adicional()
            emitir_consejo_manual()
            emitir_cita_manual()
            emitir_enemigo_manual()
            emitir_aliado_manual()
            vaciar_citas()
            vaciar_lista()
            dentro_npc_manual = True
            bloque_npc_manual.clear()
            continue

        if es_inicio_bloque_enemigo(texto_plano):
            vaciar_consejos()
            vaciar_infos()
            emitir_info_adicional()
            emitir_consejo_manual()
            emitir_cita_manual()
            emitir_npc_manual()
            emitir_aliado_manual()
            vaciar_citas()
            vaciar_lista()
            dentro_enemigo_manual = True
            bloque_enemigo_manual.clear()
            continue

        if es_inicio_bloque_aliado(texto_plano):
            vaciar_consejos()
            vaciar_infos()
            emitir_info_adicional()
            emitir_consejo_manual()
            emitir_cita_manual()
            emitir_npc_manual()
            emitir_enemigo_manual()
            vaciar_citas()
            vaciar_lista()
            dentro_aliado_manual = True
            bloque_aliado_manual.clear()
            continue

        if es_fin_bloque_manual(texto_plano) and dentro_info:
            emitir_info_adicional()
            continue

        if es_fin_bloque_manual(texto_plano) and dentro_consejo_manual:
            emitir_consejo_manual()
            continue

        if es_fin_bloque_manual(texto_plano) and dentro_cita_manual:
            emitir_cita_manual()
            continue

        if es_fin_bloque_manual(texto_plano) and dentro_npc_manual:
            emitir_npc_manual()
            continue

        if es_fin_bloque_manual(texto_plano) and dentro_enemigo_manual:
            emitir_enemigo_manual()
            continue

        if es_fin_bloque_manual(texto_plano) and dentro_aliado_manual:
            emitir_aliado_manual()
            continue

        if not texto_html.strip() and not imagenes:
            if agregar_salto_a_bloque_activo():
                continue
            # Párrafo vacío: si superamos el umbral, cerramos la caja de citas.
            if citas_pendientes:
                vacios_desde_ultima_cita += 1
                if vacios_desde_ultima_cita > MAX_VACIOS_FUSION_CITA:
                    vaciar_citas()
                    vacios_desde_ultima_cita = 0
            if consejos_pendientes:
                vacios_desde_ultimo_consejo += 1
                if vacios_desde_ultimo_consejo > MAX_VACIOS_FUSION_CONSEJO:
                    vaciar_consejos()
            if infos_pendientes:
                vacios_desde_ultima_info += 1
                if vacios_desde_ultima_info > MAX_VACIOS_FUSION_INFO:
                    vaciar_infos()
            vaciar_lista()
            # Dentro de un bloque #...# las líneas vacías se ignoran
            # (no rompen el bloque; ya separamos con <br/><br/>).
            if not dentro_info and not dentro_consejo_manual and not dentro_cita_manual and not dentro_npc_manual and not dentro_enemigo_manual and not dentro_aliado_manual:
                historia.append(Spacer(1, 4))
            continue

        clave = estilo_para_parrafo(parrafo)
        consejo_por_estilo = clave == "CajaConsejoDm"
        consejo_por_prefijo = es_consejo_dm(texto_plano)
        info_por_estilo = clave == "CajaInfoAdicional"
        info_por_prefijo = es_info_adicional(texto_plano)
        es_lista = clave == "Lista" or (
            parrafo.style.name and "List Bullet" in parrafo.style.name
        )
        es_lista = es_lista or _es_lista_parrafo(parrafo)
        item_caja = _item_caja_desde_parrafo(parrafo, texto_html)

        if agregar_contenido_a_bloque_activo(item_caja if texto_html.strip() else None, imagenes):
            continue

        if imagenes and not texto_html.strip():
            if consejos_pendientes:
                _agregar_imagenes_a_bloque(consejos_pendientes, imagenes)
                vacios_desde_ultimo_consejo = 0
                continue
            if infos_pendientes:
                _agregar_imagenes_a_bloque(infos_pendientes, imagenes)
                vacios_desde_ultima_info = 0
                continue
            if citas_pendientes:
                _agregar_imagenes_a_bloque(citas_pendientes, imagenes)
                vacios_desde_ultima_cita = 0
                continue

        if clave not in ("CajaConsejoDm", "CajaInfoAdicional", "CajaCita"):
            bloque_embebido = _extraer_bloque_prefijo_embebido(texto_html, texto_plano, es_consejo_dm)
            tipo_bloque_embebido = "consejo"
            if bloque_embebido is None:
                bloque_embebido = _extraer_bloque_prefijo_embebido(texto_html, texto_plano, es_info_adicional)
                tipo_bloque_embebido = "info"
            if bloque_embebido is not None:
                antes_html, antes_plano, bloque_html, bloque_plano = bloque_embebido
                vaciar_consejos()
                vaciar_infos()
                emitir_info_adicional()
                emitir_consejo_manual()
                emitir_cita_manual()
                vaciar_citas()

                if es_lista:
                    items_lista_actual.append(antes_html)
                else:
                    vaciar_lista()
                    historia.append(Paragraph(antes_html, estilos[clave]))

                vaciar_lista()
                item_bloque = _item_caja_plano(bloque_html)
                if tipo_bloque_embebido == "consejo":
                    consejos_pendientes.append(item_bloque)
                    if imagenes:
                        _agregar_imagenes_a_bloque(consejos_pendientes, imagenes)
                    modo_consejos = "prefijo"
                    vacios_desde_ultimo_consejo = 0
                else:
                    infos_pendientes.append(item_bloque)
                    if imagenes:
                        _agregar_imagenes_a_bloque(infos_pendientes, imagenes)
                    modo_infos = "prefijo"
                    vacios_desde_ultima_info = 0
                continue

        # 2) Consejo para el DM → caja azul (formato de un solo párrafo)
        if consejo_por_estilo or consejo_por_prefijo:
            nuevo_modo_consejo = "estilo" if consejo_por_estilo else "prefijo"
            if consejos_pendientes and modo_consejos != nuevo_modo_consejo:
                vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            emitir_cita_manual()
            vaciar_citas()
            vaciar_lista()
            item_consejo = item_caja if consejo_por_estilo else _item_caja_plano(texto_html)
            if texto_html.strip():
                consejos_pendientes.append(item_consejo)
            if imagenes:
                _agregar_imagenes_a_bloque(consejos_pendientes, imagenes)
            modo_consejos = nuevo_modo_consejo
            vacios_desde_ultimo_consejo = 0
            continue

        # 2.5) Información adicional → caja verde-azulada
        if info_por_estilo or info_por_prefijo:
            nuevo_modo_info = "estilo" if info_por_estilo else "prefijo"
            if infos_pendientes and modo_infos != nuevo_modo_info:
                vaciar_infos()
            vaciar_consejos()
            vaciar_citas()
            vaciar_lista()
            emitir_cita_manual()
            if texto_html.strip():
                infos_pendientes.append(item_caja)
            if imagenes:
                _agregar_imagenes_a_bloque(infos_pendientes, imagenes)
            modo_infos = nuevo_modo_info
            vacios_desde_ultima_info = 0
            continue

        # 3) Listas
        if es_lista:
            if consejos_pendientes and modo_consejos != "prefijo":
                if texto_html.strip():
                    consejos_pendientes.append(item_caja)
                if imagenes:
                    _agregar_imagenes_a_bloque(consejos_pendientes, imagenes)
                vacios_desde_ultimo_consejo = 0
                continue
            if infos_pendientes and modo_infos != "prefijo":
                if texto_html.strip():
                    infos_pendientes.append(item_caja)
                if imagenes:
                    _agregar_imagenes_a_bloque(infos_pendientes, imagenes)
                vacios_desde_ultima_info = 0
                continue
            if citas_pendientes:
                if texto_html.strip():
                    citas_pendientes.append(item_caja)
                if imagenes:
                    _agregar_imagenes_a_bloque(citas_pendientes, imagenes)
                vacios_desde_ultima_cita = 0
                continue
            vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            emitir_cita_manual()
            vaciar_citas()
            items_lista_actual.append(texto_html)
            continue
        else:
            vaciar_lista()

        # 4) Citas → caja amarilla (se fusionan citas consecutivas)
        if clave == "CajaCita":
            vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            emitir_cita_manual()
            if texto_html.strip():
                citas_pendientes.append(item_caja)
            if imagenes:
                _agregar_imagenes_a_bloque(citas_pendientes, imagenes)
            vacios_desde_ultima_cita = 0
            continue
        else:
            # Cualquier otro contenido cierra el bloque de citas
            vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            emitir_cita_manual()
            vaciar_citas()
            vacios_desde_ultima_cita = 0

        # 5) Resto: H1/H2/H3/Cuerpo
        if texto_html.strip():
            historia.append(Paragraph(texto_html, estilos[clave]))
        if imagenes:
            flujos_imagen = _crear_flujos_imagenes(imagenes, ancho_util)
            for flujo_imagen in flujos_imagen:
                if flujo_imagen is not None:
                    historia.append(Spacer(1, 6))
                    historia.append(flujo_imagen)
                    historia.append(Spacer(1, 6))

    emitir_consejo_manual()
    emitir_cita_manual()
    emitir_npc_manual()
    emitir_enemigo_manual()
    emitir_aliado_manual()
    emitir_info_adicional()
    vaciar_consejos()
    vaciar_infos()
    vaciar_citas()
    vaciar_lista()

    # multiBuild: necesario para que el índice se rellene en una segunda pasada
    documento_pdf.multiBuild(historia)
    print(f"✅ PDF generado: {ruta_pdf}")


def _seleccionar_archivo_dialogo(titulo, tipos_archivo, modo="abrir", archivo_inicial=None):
    """Abre un diálogo de Windows para seleccionar un archivo.

    modo: "abrir" (askopenfilename) o "guardar" (asksaveasfilename).
    Devuelve la ruta como str, o "" si el usuario cancela.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("⚠️  tkinter no está disponible; no se puede abrir el diálogo.")
        return ""

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        if modo == "guardar":
            ruta = filedialog.asksaveasfilename(
                title=titulo, filetypes=tipos_archivo,
                defaultextension=tipos_archivo[0][1].replace("*", ""),
                initialfile=archivo_inicial,
            )
        else:
            ruta = filedialog.askopenfilename(title=titulo, filetypes=tipos_archivo)
    finally:
        root.destroy()
    return ruta or ""


def _pedir_configuracion_interactiva(configuracion_inicial, configuracion_documento_inicial,
                                     titulo_inicial="", subtitulo_inicial="",
                                     autor_inicial="", portada_inicial=""):
    try:
        import tkinter as tk
        from tkinter import colorchooser, filedialog, messagebox, ttk
    except ImportError:
        print("⚠️  tkinter no está disponible; se omite el menú interactivo.")
        return {
            "configuracion_visual": dict(configuracion_inicial),
            "configuracion_documento": dict(configuracion_documento_inicial),
            "titulo": titulo_inicial or "",
            "subtitulo": subtitulo_inicial or "",
            "autor": autor_inicial or "",
            "imagen_portada": portada_inicial or "",
        }

    resultado = {"valor": None}
    raiz = tk.Tk()
    raiz.title("Configuración del PDF")
    raiz.geometry("1320x680")
    raiz.minsize(1080, 620)
    raiz.attributes("-topmost", True)

    contenedor = tk.Frame(raiz, padx=14, pady=14)
    contenedor.pack(fill="both", expand=True)

    estilo = ttk.Style(raiz)
    try:
        estilo.theme_use("vista")
    except Exception:
        pass
    estilo.configure("MenuNotebook.TNotebook", tabposition="n")
    estilo.configure("MenuNotebook.TNotebook.Tab", padding=(16, 8))

    interior = tk.Frame(contenedor)
    interior.pack(fill="both", expand=True)

    variables_color = {
        clave: tk.StringVar(value=valor)
        for clave, valor in configuracion_inicial.items()
    }
    vistas_previas = {}

    def actualizar_preview(clave):
        valor = _normalizar_color_hex(
            variables_color[clave].get(),
            configuracion_inicial[clave],
        )
        variables_color[clave].set(valor)
        vistas_previas[clave].configure(bg=valor)

    def elegir_color(clave):
        color = colorchooser.askcolor(
            color=variables_color[clave].get(),
            title="Selecciona un color",
            parent=raiz,
        )[1]
        if color:
            variables_color[clave].set(color)
            actualizar_preview(clave)

    def crear_selector_color(parent, fila, clave, etiqueta):
        tk.Label(parent, text=etiqueta, anchor="w").grid(row=fila, column=0, sticky="w", padx=(0, 8), pady=4)
        entrada = tk.Entry(parent, textvariable=variables_color[clave], width=12, justify="center")
        entrada.grid(row=fila, column=1, sticky="w", pady=4)
        preview = tk.Label(parent, width=6, relief="groove", bg=variables_color[clave].get())
        preview.grid(row=fila, column=2, padx=6, pady=4)
        vistas_previas[clave] = preview
        tk.Button(parent, text="Elegir...", command=lambda: elegir_color(clave)).grid(row=fila, column=3, sticky="w", pady=4)

    encabezado_frame = tk.Frame(interior, padx=4, pady=4)
    encabezado_frame.pack(fill="x", pady=(0, 10))
    tk.Label(
        encabezado_frame,
        text="Personaliza tu PDF antes de generarlo",
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).pack(fill="x")
    tk.Label(
        encabezado_frame,
        text=(
            "Ajusta metadatos, portada, página, fuentes, márgenes y colores. "
            "La disposición se adapta automáticamente hasta 5 columnas para que el menú sea más cómodo."
        ),
        justify="left",
        wraplength=1120,
        anchor="w",
    ).pack(fill="x", pady=(4, 0))

    notebook = ttk.Notebook(interior, style="MenuNotebook.TNotebook")
    notebook.pack(fill="both", expand=True)

    pestana_general = tk.Frame(notebook, padx=14, pady=14)
    pestana_colores_base = tk.Frame(notebook, padx=14, pady=14)
    pestana_colores_cajas = tk.Frame(notebook, padx=14, pady=14)
    pestana_colores_personajes = tk.Frame(notebook, padx=14, pady=14)
    notebook.add(pestana_general, text="General")
    notebook.add(pestana_colores_base, text="Colores base")
    notebook.add(pestana_colores_cajas, text="Cajas útiles")
    notebook.add(pestana_colores_personajes, text="NPC y combate")

    panel_superior = tk.Frame(pestana_general)
    panel_superior.pack(fill="both", expand=True)
    panel_superior.columnconfigure(0, weight=1, uniform="columna_superior")
    panel_superior.columnconfigure(1, weight=1, uniform="columna_superior")

    titulo_frame = tk.LabelFrame(panel_superior, text="Portada y metadatos", padx=10, pady=10)
    titulo_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))

    titulo_var = tk.StringVar(value=titulo_inicial or "")
    subtitulo_var = tk.StringVar(value=subtitulo_inicial or "")
    autor_var = tk.StringVar(value=autor_inicial or "")
    portada_explicita = bool(portada_inicial and portada_inicial != IMAGEN_PORTADA_PREDETERMINADA)
    portada_habilitada_var = tk.BooleanVar(value=portada_explicita)
    portada_var = tk.StringVar(value=portada_inicial if portada_explicita else "")

    tk.Label(titulo_frame, text="Título de la aventura (opcional)").grid(row=0, column=0, sticky="w")
    tk.Entry(titulo_frame, textvariable=titulo_var, width=50).grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)
    tk.Label(titulo_frame, text="Subtítulo (opcional)").grid(row=1, column=0, sticky="w")
    tk.Entry(titulo_frame, textvariable=subtitulo_var, width=50).grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)
    tk.Label(titulo_frame, text="Autor (opcional)").grid(row=2, column=0, sticky="w")
    tk.Entry(titulo_frame, textvariable=autor_var, width=50).grid(row=2, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)

    def elegir_portada():
        ruta = filedialog.askopenfilename(
            title="Selecciona la imagen de portada",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            portada_var.set(ruta)

    def actualizar_estado_portada():
        estado = "normal" if portada_habilitada_var.get() else "disabled"
        boton_portada.configure(state=estado)
        entrada_portada.configure(state="normal" if portada_habilitada_var.get() else "readonly")
        if not portada_habilitada_var.get():
            portada_var.set("")
        entrada_portada.configure(state="readonly")

    tk.Checkbutton(
        titulo_frame,
        text="Agregar portada",
        variable=portada_habilitada_var,
        command=actualizar_estado_portada,
    ).grid(row=3, column=0, sticky="w", pady=(8, 4))
    entrada_portada = tk.Entry(titulo_frame, textvariable=portada_var, width=50, state="readonly")
    entrada_portada.grid(row=3, column=1, sticky="ew", padx=(8, 8), pady=(8, 4))
    boton_portada = tk.Button(titulo_frame, text="Elegir imagen...", command=elegir_portada)
    boton_portada.grid(row=3, column=2, sticky="w", pady=(8, 4))
    titulo_frame.columnconfigure(1, weight=1)
    actualizar_estado_portada()

    documento_frame = tk.LabelFrame(panel_superior, text="Página, fuentes y márgenes", padx=10, pady=10)
    documento_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))

    tamano_pagina_var = tk.StringVar(value=configuracion_documento_inicial.get("tamano_pagina", "A4"))
    fuente_titulo_var = tk.StringVar(value=configuracion_documento_inicial.get("fuente_titulo", FUENTE_TITULO))
    fuente_texto_var = tk.StringVar(value=configuracion_documento_inicial.get("fuente_texto", FUENTE_TEXTO))
    margen_var = tk.StringVar(value=str(configuracion_documento_inicial.get("margen_cm", 2.0)))
    ancho_pagina_var = tk.StringVar(value=str(configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)))
    alto_pagina_var = tk.StringVar(value=str(configuracion_documento_inicial.get("alto_pagina_cm", 29.7)))

    tk.Label(documento_frame, text="Tamaño de página").grid(row=0, column=0, sticky="w", pady=3)
    opcion_pagina = ttk.Combobox(
        documento_frame,
        textvariable=tamano_pagina_var,
        values=[*TAMANOS_PAGINA_DISPONIBLES.keys(), OPCION_TAMANO_PERSONALIZADO],
        state="readonly",
        width=18,
    )
    opcion_pagina.grid(row=0, column=1, sticky="w", padx=(8, 0), pady=3)

    tk.Label(documento_frame, text="Ancho personalizado (cm)").grid(row=0, column=2, sticky="w", padx=(16, 0), pady=3)
    entrada_ancho = tk.Entry(documento_frame, textvariable=ancho_pagina_var, width=10)
    entrada_ancho.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=3)

    tk.Label(documento_frame, text="Alto personalizado (cm)").grid(row=1, column=2, sticky="w", padx=(16, 0), pady=3)
    entrada_alto = tk.Entry(documento_frame, textvariable=alto_pagina_var, width=10)
    entrada_alto.grid(row=1, column=3, sticky="w", padx=(8, 0), pady=3)

    tk.Label(documento_frame, text="Fuente de título").grid(row=1, column=0, sticky="w", pady=3)
    opcion_fuente_titulo = ttk.Combobox(
        documento_frame,
        textvariable=fuente_titulo_var,
        values=FUENTES_DISPONIBLES,
        state="readonly",
        width=28,
    )
    opcion_fuente_titulo.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=3)

    tk.Label(documento_frame, text="Fuente de texto").grid(row=2, column=0, sticky="w", pady=3)
    opcion_fuente_texto = ttk.Combobox(
        documento_frame,
        textvariable=fuente_texto_var,
        values=FUENTES_DISPONIBLES,
        state="readonly",
        width=28,
    )
    opcion_fuente_texto.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=3)

    tk.Label(documento_frame, text="Margen (cm)").grid(row=3, column=0, sticky="w", pady=3)
    tk.Entry(documento_frame, textvariable=margen_var, width=10).grid(row=3, column=1, sticky="w", padx=(8, 0), pady=3)
    tk.Label(documento_frame, text="Rango recomendado: 0.5 a 5.0 cm").grid(row=3, column=2, sticky="w", padx=(8, 0), pady=3)

    def actualizar_estado_tamano_personalizado(*_args):
        es_personalizado = tamano_pagina_var.get().strip().upper() == OPCION_TAMANO_PERSONALIZADO
        estado = "normal" if es_personalizado else "disabled"
        entrada_ancho.configure(state=estado)
        entrada_alto.configure(state=estado)

    tamano_pagina_var.trace_add("write", actualizar_estado_tamano_personalizado)
    actualizar_estado_tamano_personalizado()

    grupos_colores = [
        (
            "General",
            [
                ("color_primario", "Títulos"),
                ("color_secundario", "Texto general"),
                ("color_fondo_pagina", "Fondo de página"),
            ],
        ),
        (
            "Caja Consejo para el DM",
            [
                ("color_azul_texto", "Texto"),
                ("color_azul_borde", "Borde"),
                ("color_azul_fondo", "Fondo"),
            ],
        ),
        (
            "Caja Cita",
            [
                ("color_ama_texto", "Texto"),
                ("color_ama_borde", "Borde"),
                ("color_ama_fondo", "Fondo"),
            ],
        ),
        (
            "Caja Información adicional",
            [
                ("color_info_texto", "Texto"),
                ("color_info_borde", "Borde"),
                ("color_info_fondo", "Fondo"),
            ],
        ),
        (
            "Caja NPC",
            [
                ("color_npc_texto", "Texto"),
                ("color_npc_borde", "Borde"),
                ("color_npc_fondo", "Fondo"),
            ],
        ),
        (
            "Caja Enemigo",
            [
                ("color_enemigo_texto", "Texto"),
                ("color_enemigo_borde", "Borde"),
                ("color_enemigo_fondo", "Fondo"),
            ],
        ),
        (
            "Caja Aliado",
            [
                ("color_aliado_texto", "Texto"),
                ("color_aliado_borde", "Borde"),
                ("color_aliado_fondo", "Fondo"),
            ],
        ),
    ]

    distribucion_pestanas = {
        "Colores base": ["General", "Caja Consejo para el DM", "Caja Cita"],
        "Cajas útiles": ["Caja Información adicional"],
        "NPC y combate": ["Caja NPC", "Caja Enemigo", "Caja Aliado"],
    }

    contenedores_colores = {
        "Colores base": pestana_colores_base,
        "Cajas útiles": pestana_colores_cajas,
        "NPC y combate": pestana_colores_personajes,
    }

    for pestana in contenedores_colores.values():
        pestana.columnconfigure(0, weight=1, uniform="colores_tab")
        pestana.columnconfigure(1, weight=1, uniform="colores_tab")

    for nombre_pestana, nombres_grupos in distribucion_pestanas.items():
        contenedor_tab = contenedores_colores[nombre_pestana]
        for indice_grupo, nombre_grupo in enumerate(nombres_grupos):
            datos_grupo = next(grupo for grupo in grupos_colores if grupo[0] == nombre_grupo)
            _, campos = datos_grupo
            columna = indice_grupo % 2
            fila = indice_grupo // 2
            padding_x = (0, 8) if columna == 0 else (8, 0)
            frame = tk.LabelFrame(contenedor_tab, text=nombre_grupo, padx=10, pady=10)
            frame.grid(row=fila, column=columna, sticky="nsew", padx=padding_x, pady=(0, 10))
            for indice, (clave, etiqueta) in enumerate(campos):
                crear_selector_color(frame, indice, clave, etiqueta)

    tk.Label(
        pestana_colores_base,
        text="Aquí están los colores base del documento y de las cajas más frecuentes.",
        anchor="w",
        justify="left",
    ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))
    tk.Label(
        pestana_colores_cajas,
        text="La caja de información adicional queda separada para evitar saturar la vista.",
        anchor="w",
        justify="left",
    ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))
    tk.Label(
        pestana_colores_personajes,
        text="Los bloques de NPC, enemigo y aliado comparten esta pestaña para ajustes rápidos de escena.",
        anchor="w",
        justify="left",
    ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))

    botones = tk.Frame(contenedor, padx=12, pady=10)
    botones.pack(fill="x")

    def restablecer_valores():
        for clave, valor in configuracion_inicial.items():
            variables_color[clave].set(valor)
            actualizar_preview(clave)
        tamano_pagina_var.set(configuracion_documento_inicial.get("tamano_pagina", "A4"))
        fuente_titulo_var.set(configuracion_documento_inicial.get("fuente_titulo", FUENTE_TITULO))
        fuente_texto_var.set(configuracion_documento_inicial.get("fuente_texto", FUENTE_TEXTO))
        margen_var.set(str(configuracion_documento_inicial.get("margen_cm", 2.0)))
        ancho_pagina_var.set(str(configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)))
        alto_pagina_var.set(str(configuracion_documento_inicial.get("alto_pagina_cm", 29.7)))

    def cancelar():
        resultado["valor"] = None
        raiz.quit()

    def aceptar():
        configuracion_visual = {}
        for clave, valor in configuracion_inicial.items():
            color_normalizado = _normalizar_color_hex(variables_color[clave].get(), valor)
            if color_normalizado != variables_color[clave].get().strip():
                variables_color[clave].set(color_normalizado)
            try:
                HexColor(color_normalizado)
            except Exception:
                messagebox.showerror("Color inválido", f"El color para '{clave}' no es válido.")
                return
            configuracion_visual[clave] = color_normalizado

        imagen_portada = portada_var.get().strip() if portada_habilitada_var.get() else ""
        if portada_habilitada_var.get() and not imagen_portada:
            messagebox.showerror("Portada incompleta", "Selecciona la imagen de portada o desactiva la opción.")
            return

        try:
            margen_cm = float(str(margen_var.get()).replace(",", ".").strip())
        except (TypeError, ValueError):
            messagebox.showerror("Margen inválido", "El margen debe ser un número en centímetros.")
            return
        if margen_cm < 0.5 or margen_cm > 5.0:
            messagebox.showerror("Margen inválido", "El margen debe estar entre 0.5 y 5.0 cm.")
            return

        tamano_pagina = tamano_pagina_var.get().strip().upper()
        ancho_pagina_cm = configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)
        alto_pagina_cm = configuracion_documento_inicial.get("alto_pagina_cm", 29.7)
        if tamano_pagina == OPCION_TAMANO_PERSONALIZADO:
            try:
                ancho_pagina_cm = float(str(ancho_pagina_var.get()).replace(",", ".").strip())
                alto_pagina_cm = float(str(alto_pagina_var.get()).replace(",", ".").strip())
            except (TypeError, ValueError):
                messagebox.showerror("Tamaño inválido", "El ancho y alto personalizados deben ser números en centímetros.")
                return
            if not (5.0 <= ancho_pagina_cm <= 100.0 and 5.0 <= alto_pagina_cm <= 100.0):
                messagebox.showerror("Tamaño inválido", "El ancho y alto personalizados deben estar entre 5 y 100 cm.")
                return

        configuracion_documento = {
            "tamano_pagina": tamano_pagina,
            "fuente_titulo": fuente_titulo_var.get().strip(),
            "fuente_texto": fuente_texto_var.get().strip(),
            "margen_cm": margen_cm,
            "ancho_pagina_cm": ancho_pagina_cm,
            "alto_pagina_cm": alto_pagina_cm,
        }

        resultado["valor"] = {
            "configuracion_visual": configuracion_visual,
            "configuracion_documento": configuracion_documento,
            "titulo": titulo_var.get().strip(),
            "subtitulo": subtitulo_var.get().strip(),
            "autor": autor_var.get().strip(),
            "imagen_portada": imagen_portada,
        }
        raiz.quit()

    tk.Button(botones, text="Restablecer valores", command=restablecer_valores).pack(side="left")
    tk.Button(botones, text="Cancelar", command=cancelar).pack(side="right", padx=(8, 0))
    tk.Button(botones, text="Aceptar", command=aceptar).pack(side="right")

    def ajustar_tamano_ventana():
        raiz.update_idletasks()
        ancho_objetivo = max(1080, min(1320, raiz.winfo_reqwidth() + 24))
        alto_requerido = raiz.winfo_reqheight() + 20
        alto_pantalla = int(raiz.winfo_screenheight() * 0.9)
        alto_objetivo = max(620, min(alto_requerido, alto_pantalla))
        raiz.geometry(f"{ancho_objetivo}x{alto_objetivo}")

    raiz.protocol("WM_DELETE_WINDOW", cancelar)
    raiz.after(10, ajustar_tamano_ventana)
    raiz.mainloop()
    raiz.destroy()
    return resultado["valor"]


def principal():
    parser = argparse.ArgumentParser(description="Convierte un .docx a PDF estilo Aventura.")
    parser.add_argument("entrada", nargs="?", help="Archivo .docx de entrada (si se omite se abre un diálogo)")
    parser.add_argument("salida", nargs="?", help="Archivo .pdf de salida (si se omite se abre un diálogo)")
    parser.add_argument("--titulo", help="Título de la portada (opcional)")
    parser.add_argument("--subtitulo", help="Subtítulo de la portada (opcional)")
    parser.add_argument("--autor", help="Autor (opcional)")
    parser.add_argument("--portada", default=IMAGEN_PORTADA_PREDETERMINADA,
                        help=f"Ruta a la imagen de portada (por defecto: {IMAGEN_PORTADA_PREDETERMINADA})")
    parser.add_argument("--menu-interactivo", action="store_true",
                        help="Fuerza la apertura del menú interactivo de colores y metadatos.")
    parser.add_argument("--sin-menu", action="store_true",
                        help="Omite el menú interactivo incluso si se usan diálogos de archivo.")
    args = parser.parse_args()

    # --- Entrada: si no se pasa por CLI, pedirla con diálogo de Windows ---
    if args.entrada:
        entrada = Path(args.entrada)
    else:
        print("📂 Selecciona el archivo Word de entrada...")
        ruta = _seleccionar_archivo_dialogo(
            "Selecciona el archivo Word de entrada",
            [("Documentos Word", "*.docx"), ("Todos los archivos", "*.*")],
            modo="abrir",
        )
        if not ruta:
            raise SystemExit("❌ No se seleccionó ningún archivo de entrada.")
        entrada = Path(ruta)

    if not entrada.exists():
        raise SystemExit(f"No se encontró el archivo: {entrada}")

    # --- Salida: si no se pasa por CLI, pedirla con diálogo de Windows ---
    if args.salida:
        salida = Path(args.salida)
    else:
        print("💾 Selecciona dónde guardar el PDF...")
        ruta = _seleccionar_archivo_dialogo(
            "Guardar PDF como...",
            [("Archivo PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            modo="guardar",
            archivo_inicial=entrada.with_suffix(".pdf").name,
        )
        if not ruta:
            raise SystemExit("❌ No se seleccionó ruta de salida.")
        salida = Path(ruta)

    configuracion_visual = obtener_configuracion_visual_predeterminada()
    configuracion_documento = obtener_configuracion_documento_predeterminada()
    titulo = args.titulo or ""
    subtitulo = args.subtitulo or ""
    autor = args.autor or ""
    imagen_portada = args.portada or ""
    if imagen_portada == IMAGEN_PORTADA_PREDETERMINADA and not os.path.exists(imagen_portada):
        imagen_portada = ""

    usar_menu_interactivo = False
    if not args.sin_menu:
        usar_menu_interactivo = args.menu_interactivo or not (args.entrada and args.salida)

    if usar_menu_interactivo:
        portada_inicial = imagen_portada
        if portada_inicial == IMAGEN_PORTADA_PREDETERMINADA and not os.path.exists(portada_inicial):
            portada_inicial = ""

        configuracion = _pedir_configuracion_interactiva(
            configuracion_visual,
            configuracion_documento,
            titulo_inicial=titulo,
            subtitulo_inicial=subtitulo,
            autor_inicial=autor,
            portada_inicial=portada_inicial,
        )
        if configuracion is None:
            raise SystemExit("❌ Operación cancelada por el usuario.")
        configuracion_visual = configuracion["configuracion_visual"]
        configuracion_documento = configuracion["configuracion_documento"]
        titulo = configuracion["titulo"]
        subtitulo = configuracion["subtitulo"]
        autor = configuracion["autor"]
        imagen_portada = configuracion["imagen_portada"]

    aplicar_configuracion_visual(configuracion_visual)
    aplicar_configuracion_documento(configuracion_documento)

    construir_pdf(entrada, salida,
                  titulo=titulo or None, autor=autor or None,
                  subtitulo=subtitulo or None, imagen_portada=imagen_portada)


if __name__ == "__main__":
    principal()

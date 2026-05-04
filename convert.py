"""
Conversor de Word (.docx) a PDF con estilo "Aventura".

Uso:
    python convert.py entrada.docx salida.pdf
    python convert.py entrada.docx salida.pdf --titulo "Mi Aventura" --autor "Tu Nombre"

Convención del documento Word:
    - Estilo "Título 1" (Heading 1)  -> Capítulo (entra en TOC)
    - Estilo "Título 2" (Heading 2)  -> Sección (entra en TOC)
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
from PIL import Image as PILImage

from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, PageBreak, ListFlowable, ListItem, Image,
    KeepTogether, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# ============== Parámetros visuales (modificables) ==============
COLOR_PRIMARIO   = HexColor("#8B0000")   # rojo oscuro (títulos)
COLOR_SECUNDARIO = HexColor("#1a1a1a")

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

FUENTE_TITULO = "Helvetica-Bold"
FUENTE_TEXTO  = "Helvetica"
TAMANO_PAGINA = A4
MARGEN        = 2 * cm

# Ruta de ejemplo para la imagen de portada (cámbiala cuando tengas la tuya)
IMAGEN_PORTADA_DEFAULT = r"C:\ruta\a\tu\imagen_portada.jpg"
# ==================================================================


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
        name="CitaCaja",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_AMA_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_AMA_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_AMA_FONDO,
    ))
    # Caja VERDE-AZULADA (Información adicional útil, no obligatoria)
    estilos.add(ParagraphStyle(
        name="InfoAdicional",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_INFO_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_INFO_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_INFO_FONDO,
    ))
    # Caja AZUL (Consejo para el DM)
    estilos.add(ParagraphStyle(
        name="ConsejoDM",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_AZUL_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=12, spaceAfter=12,
        borderColor=COLOR_AZUL_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=5, backColor=COLOR_AZUL_FONDO,
    ))
    estilos.add(ParagraphStyle(
        name="TOCTitulo",
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
        return "InfoAdicional"
    if "consejos" in nombre or "consejo dm" in nombre or "consejo para el dm" in nombre:
        return "ConsejoDM"
    if "quote" in nombre or "cita" in nombre:
        return "CitaCaja"
    if "list" in nombre or "lista" in nombre:
        return "Lista"
    return "Cuerpo"


def _markdown_inline_a_html(texto):
    """Convierte **negrita** y *cursiva* (estilo markdown) a HTML.

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


def _texto_run_xml(run_xml):
    partes = []
    for nodo in run_xml.iter():
        if nodo.tag == qn("w:t"):
            partes.append(nodo.text or "")
        elif nodo.tag == qn("w:tab"):
            partes.append("    ")
        elif nodo.tag in (qn("w:br"), qn("w:cr")):
            partes.append("<br/>")
    return "".join(partes)


def _run_xml_a_html(run_xml):
    texto = _texto_run_xml(run_xml)
    if not texto:
        return "", False

    usa_formato = False
    if "<br/>" not in texto:
        texto = _escapar_html(texto)

    propiedades = run_xml.find(qn("w:rPr"))
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


def _hipervinculo_xml_a_html(hipervinculo_xml, doc_part):
    partes = []
    usa_formato = False

    for run_xml in hipervinculo_xml.findall(qn("w:r")):
        html_run, formato_run = _run_xml_a_html(run_xml)
        if html_run:
            partes.append(html_run)
        usa_formato = usa_formato or formato_run

    texto_html = "".join(partes)
    if not texto_html:
        return "", usa_formato

    rel_id = hipervinculo_xml.get(qn("r:id"))
    anchor = hipervinculo_xml.get(qn("w:anchor"))
    destino = ""
    if rel_id and rel_id in doc_part.rels:
        destino = doc_part.rels[rel_id].target_ref or ""
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


def runs_a_html(parrafo):
    """Convierte párrafos Word a HTML para ReportLab, incluyendo links."""
    partes = []
    algun_formato_run = False

    for nodo in parrafo._p.iterchildren():
        if nodo.tag == qn("w:r"):
            html_run, formato_run = _run_xml_a_html(nodo)
            if html_run:
                partes.append(html_run)
            algun_formato_run = algun_formato_run or formato_run
        elif nodo.tag == qn("w:hyperlink"):
            html_link, formato_link = _hipervinculo_xml_a_html(nodo, parrafo.part)
            if html_link:
                partes.append(html_link)
            algun_formato_run = algun_formato_run or formato_link

    html = "".join(partes)
    # Si Word no marcó nada en negrita/cursiva, interpretar markdown inline (**...**, *...*).
    if not algun_formato_run and ("*" in html):
        html = _markdown_inline_a_html(html)
    return html


def extraer_imagenes_de_parrafo(parrafo, doc_word):
    """Devuelve lista de bytes con las imágenes embebidas en el párrafo."""
    imagenes = []
    for blip in parrafo._element.findall(".//" + qn("a:blip")):
        rId = blip.get(qn("r:embed"))
        if rId and rId in doc_word.part.related_parts:
            imagenes.append(doc_word.part.related_parts[rId].blob)
    return imagenes


def imagen_flowable(blob, ancho_max):
    """Crea un Image escalado para que entre en la página."""
    bio = io.BytesIO(blob)
    try:
        with PILImage.open(bio) as im:
            w, h = im.size
    except Exception:
        return None
    bio.seek(0)
    ratio = (h / w) if w else 1
    ancho = min(ancho_max, float(w))
    alto = ancho * ratio
    img = Image(bio, width=ancho, height=alto)
    img.hAlign = "CENTER"
    return img


def es_consejo_dm(texto_plano):
    # Quita asteriscos, espacios y comillas iniciales para tolerar formatos
    # tipo markdown (**CONSEJO PARA EL DM...**).
    limpio = texto_plano.lstrip(" *_“\"'\t").lower()
    return limpio.startswith("consejo para el dm")


def _quitar_prefijo_visible_html(html, visible_chars):
    if visible_chars <= 0:
        return html

    resultado = []
    pila_tags = []
    chars_restantes = visible_chars
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

        if chars_restantes > 0:
            chars_restantes -= 1
            if chars_restantes == 0:
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
        cuerpo = _quitar_prefijo_visible_html(texto_html, len(match.group(0)))

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


def _pt_word(longitud):
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
        "html": texto_html,
        "es_lista": _es_lista_parrafo(parrafo),
        "nivel_lista": _nivel_lista_parrafo(parrafo),
        "left_indent": _pt_word(parrafo.paragraph_format.left_indent),
        "first_line_indent": _pt_word(parrafo.paragraph_format.first_line_indent),
    }


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
        indent_word = max(0, item["left_indent"])
        indent_base = max(16 + nivel * 14, 12 + indent_word)
        estilo.leftIndent = indent_base
        estilo.firstLineIndent = -10
        estilo.spaceAfter = 3
    else:
        estilo.leftIndent = max(0, item["left_indent"])
        estilo.firstLineIndent = item["first_line_indent"]
    return estilo


def _renderizar_caja(partes, estilo_base, ancho_total, decorador=None):
    contenido = []
    primer_bloque = True
    indice = 0

    for parte in partes:
        if parte is None:
            if contenido and not isinstance(contenido[-1], Spacer):
                contenido.append(Spacer(1, 6))
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

    tabla = Table([[contenido]], colWidths=[ancho_total], hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), estilo_base.backColor),
        ("BOX", (0, 0), (-1, -1), estilo_base.borderWidth, estilo_base.borderColor),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([Spacer(1, 4), tabla, Spacer(1, 8)])


class DocConTOC(BaseDocTemplate):
    """DocTemplate que notifica entradas a la TOC al pasar por H1/H2."""
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        frame = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height, id="normal")
        self.addPageTemplates([PageTemplate(id="Todo", frames=frame)])
        self._bookmark_counter = 0

    def _crear_bookmark(self, texto):
        self._bookmark_counter += 1
        texto_limpio = re.sub(r"\s+", "-", texto.strip())
        texto_limpio = re.sub(r"[^\w\-]", "", texto_limpio, flags=re.UNICODE)
        texto_limpio = texto_limpio[:60] or "seccion"
        return f"bookmark-{self._bookmark_counter}-{texto_limpio}"

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            estilo = flowable.style.name
            texto = flowable.getPlainText()
            if estilo == "H1":
                bookmark = self._crear_bookmark(texto)
                self.canv.bookmarkPage(bookmark)
                self.canv.addOutlineEntry(texto, bookmark, level=0, closed=False)
                self.notify("TOCEntry", (0, texto, self.page))
            elif estilo == "H2":
                bookmark = self._crear_bookmark(texto)
                self.canv.bookmarkPage(bookmark)
                self.canv.addOutlineEntry(texto, bookmark, level=1, closed=False)
                self.notify("TOCEntry", (1, texto, self.page))
            elif estilo == "H3":
                bookmark = self._crear_bookmark(texto)
                self.canv.bookmarkPage(bookmark)
                self.canv.addOutlineEntry(texto, bookmark, level=2, closed=False)


def construir_pdf(docx_path, pdf_path, titulo=None, autor=None,
                  subtitulo=None, imagen_portada=None):
    doc_word = Document(docx_path)
    estilos = construir_estilos()

    pdf = DocConTOC(
        str(pdf_path),
        pagesize=TAMANO_PAGINA,
        leftMargin=MARGEN, rightMargin=MARGEN,
        topMargin=MARGEN, bottomMargin=MARGEN,
        title=titulo or "Aventura",
        author=autor or "",
    )

    ancho_util = TAMANO_PAGINA[0] - 2 * MARGEN
    historia = []

    # ---------- Portada ----------
    if titulo or imagen_portada:
        if imagen_portada and os.path.exists(imagen_portada):
            try:
                with PILImage.open(imagen_portada) as im:
                    w, h = im.size
                ratio = (h / w) if w else 1
                img = Image(imagen_portada,
                            width=ancho_util,
                            height=ancho_util * ratio)
                img.hAlign = "CENTER"
                historia.append(Spacer(1, 1 * cm))
                historia.append(img)
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
    historia.append(Paragraph("Índice", estilos["TOCTitulo"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name="TOC1", fontName=FUENTE_TITULO, fontSize=12,
                       leading=18, textColor=COLOR_PRIMARIO, leftIndent=0),
        ParagraphStyle(name="TOC2", fontName=FUENTE_TEXTO, fontSize=11,
                       leading=16, textColor=COLOR_SECUNDARIO, leftIndent=18),
    ]
    historia.append(toc)
    historia.append(PageBreak())

    # ---------- Contenido ----------
    items_lista_actual = []
    citas_pendientes = []          # buffer de citas consecutivas a fusionar
    vacios_desde_ultima_cita = 0   # nº de párrafos vacíos vistos tras la última cita
    MAX_VACIOS_FUSION_CITA = 2     # hasta 2 saltos de renglón => misma caja
    consejos_pendientes = []       # buffer de consejos consecutivos a fusionar
    vacios_desde_ultimo_consejo = 0
    MAX_VACIOS_FUSION_CONSEJO = 2  # hasta 2 saltos de renglón => misma caja
    infos_pendientes = []          # buffer de infos consecutivas a fusionar
    vacios_desde_ultima_info = 0   # nº de párrafos vacíos vistos tras la última info
    MAX_VACIOS_FUSION_INFO = 2     # hasta 2 saltos de renglón => misma caja

    consejo_manual_buffer = []     # buffer de párrafos dentro de :::consejo ... :::
    dentro_consejo_manual = False
    info_buffer = []               # buffer de párrafos dentro de :::info ... :::
    dentro_info = False

    def _texto_plano_limpio(s):
        # Quita espacios, asteriscos y caracteres de formato comunes.
        return s.strip(" \t*_")

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
            caja = _renderizar_caja(citas_pendientes, estilos["CitaCaja"], ancho_util)
            if caja is not None:
                historia.append(caja)
            citas_pendientes.clear()

    def vaciar_consejos():
        nonlocal vacios_desde_ultimo_consejo
        if consejos_pendientes:
            caja = _renderizar_caja(
                consejos_pendientes,
                estilos["ConsejoDM"],
                ancho_util,
                decorador=decorar_consejo_dm_html,
            )
            if caja is not None:
                historia.append(caja)
            consejos_pendientes.clear()
        vacios_desde_ultimo_consejo = 0

    def vaciar_infos():
        nonlocal vacios_desde_ultima_info
        if infos_pendientes:
            caja = _renderizar_caja(
                infos_pendientes,
                estilos["InfoAdicional"],
                ancho_util,
                decorador=decorar_info_adicional_html,
            )
            if caja is not None:
                historia.append(caja)
            infos_pendientes.clear()
        vacios_desde_ultima_info = 0

    def emitir_consejo_manual():
        nonlocal dentro_consejo_manual
        if consejo_manual_buffer:
            caja = _renderizar_caja(
                consejo_manual_buffer,
                estilos["ConsejoDM"],
                ancho_util,
                decorador=decorar_consejo_dm_html,
            )
            if caja is not None:
                historia.append(caja)
            consejo_manual_buffer.clear()
        dentro_consejo_manual = False

    def emitir_info_adicional():
        nonlocal dentro_info
        if info_buffer:
            caja = _renderizar_caja(
                info_buffer,
                estilos["InfoAdicional"],
                ancho_util,
                decorador=decorar_info_adicional_html,
            )
            if caja is not None:
                historia.append(caja)
            info_buffer.clear()
        dentro_info = False

    for parrafo in doc_word.paragraphs:
        # 1) Imágenes embebidas en el párrafo
        imgs = extraer_imagenes_de_parrafo(parrafo, doc_word)
        if imgs:
            # Las imágenes interrumpen cualquier bloque abierto
            vaciar_consejos()
            vaciar_infos()
            emitir_info_adicional()
            emitir_consejo_manual()
            vaciar_citas()
            vaciar_lista()
            for blob in imgs:
                fl = imagen_flowable(blob, ancho_util)
                if fl is not None:
                    historia.append(Spacer(1, 6))
                    historia.append(fl)
                    historia.append(Spacer(1, 6))

        texto_html = runs_a_html(parrafo)
        texto_plano = parrafo.text or ""

        if es_inicio_bloque_info(texto_plano):
            vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            vaciar_citas()
            vaciar_lista()
            dentro_info = True
            info_buffer.clear()
            continue

        if es_inicio_bloque_consejo(texto_plano):
            vaciar_consejos()
            vaciar_infos()
            emitir_info_adicional()
            vaciar_citas()
            vaciar_lista()
            dentro_consejo_manual = True
            consejo_manual_buffer.clear()
            continue

        if es_fin_bloque_info(texto_plano) and dentro_info:
            emitir_info_adicional()
            continue

        if es_fin_bloque_info(texto_plano) and dentro_consejo_manual:
            emitir_consejo_manual()
            continue

        if not texto_html.strip():
            if dentro_consejo_manual:
                consejo_manual_buffer.append(None)
                continue
            if dentro_info:
                info_buffer.append(None)
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
            if not dentro_info and not dentro_consejo_manual:
                historia.append(Spacer(1, 4))
            continue

        clave = estilo_para_parrafo(parrafo)
        es_lista = clave == "Lista" or (
            parrafo.style.name and "List Bullet" in parrafo.style.name
        )
        es_lista = es_lista or _es_lista_parrafo(parrafo)
        item_caja = _item_caja_desde_parrafo(parrafo, texto_html)

        if dentro_info:
            info_buffer.append(item_caja)
            continue

        if dentro_consejo_manual:
            consejo_manual_buffer.append(item_caja)
            continue

        # 2) Consejo para el DM → caja azul (formato de un solo párrafo)
        if clave == "ConsejoDM" or es_consejo_dm(texto_plano):
            vaciar_infos()
            emitir_consejo_manual()
            vaciar_citas()
            vaciar_lista()
            consejos_pendientes.append(item_caja)
            vacios_desde_ultimo_consejo = 0
            continue

        # 2.5) Información adicional → caja verde-azulada
        if clave == "InfoAdicional" or es_info_adicional(texto_plano):
            vaciar_consejos()
            vaciar_citas()
            vaciar_lista()
            infos_pendientes.append(item_caja)
            vacios_desde_ultima_info = 0
            continue

        # 3) Listas
        if es_lista:
            if consejos_pendientes:
                consejos_pendientes.append(item_caja)
                vacios_desde_ultimo_consejo = 0
                continue
            if infos_pendientes:
                infos_pendientes.append(item_caja)
                vacios_desde_ultima_info = 0
                continue
            if citas_pendientes:
                citas_pendientes.append(item_caja)
                vacios_desde_ultima_cita = 0
                continue
            vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            vaciar_citas()
            items_lista_actual.append(texto_html)
            continue
        else:
            vaciar_lista()

        # 4) Citas → caja amarilla (se fusionan citas consecutivas)
        if clave == "CitaCaja":
            vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            citas_pendientes.append(item_caja)
            vacios_desde_ultima_cita = 0
            continue
        else:
            # Cualquier otro contenido cierra el bloque de citas
            vaciar_consejos()
            vaciar_infos()
            emitir_consejo_manual()
            vaciar_citas()
            vacios_desde_ultima_cita = 0

        # 5) Resto: H1/H2/H3/Cuerpo
        historia.append(Paragraph(texto_html, estilos[clave]))

    emitir_consejo_manual()
    emitir_info_adicional()
    vaciar_consejos()
    vaciar_infos()
    vaciar_citas()
    vaciar_lista()

    # multiBuild: necesario para que la TOC se rellene en una segunda pasada
    pdf.multiBuild(historia)
    print(f"✅ PDF generado: {pdf_path}")


def _seleccionar_archivo_dialogo(titulo, filetypes, modo="abrir", initialfile=None):
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
                title=titulo, filetypes=filetypes,
                defaultextension=filetypes[0][1].replace("*", ""),
                initialfile=initialfile,
            )
        else:
            ruta = filedialog.askopenfilename(title=titulo, filetypes=filetypes)
    finally:
        root.destroy()
    return ruta or ""


def main():
    parser = argparse.ArgumentParser(description="Convierte un .docx a PDF estilo Aventura.")
    parser.add_argument("entrada", nargs="?", help="Archivo .docx de entrada (si se omite se abre un diálogo)")
    parser.add_argument("salida", nargs="?", help="Archivo .pdf de salida (si se omite se abre un diálogo)")
    parser.add_argument("--titulo", help="Título de la portada (opcional)")
    parser.add_argument("--subtitulo", help="Subtítulo de la portada (opcional)")
    parser.add_argument("--autor", help="Autor (opcional)")
    parser.add_argument("--portada", default=IMAGEN_PORTADA_DEFAULT,
                        help=f"Ruta a la imagen de portada (por defecto: {IMAGEN_PORTADA_DEFAULT})")
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
            initialfile=entrada.with_suffix(".pdf").name,
        )
        if not ruta:
            raise SystemExit("❌ No se seleccionó ruta de salida.")
        salida = Path(ruta)

    construir_pdf(entrada, salida,
                  titulo=args.titulo, autor=args.autor,
                  subtitulo=args.subtitulo, imagen_portada=args.portada)


if __name__ == "__main__":
    main()

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
    KeepTogether,
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


def _split_html_balanceado(html, sep="#"):
    """Divide `html` por `sep` manteniendo balanceadas las etiquetas.

    Si una etiqueta queda abierta al llegar a `sep`, se cierra antes del corte
    y se reabre al inicio del siguiente segmento. Esto evita HTML inválido
    cuando el separador cae dentro de un <b>, <i>, <u>...
    """
    partes = []
    pila = []          # nombres de etiquetas abiertas (en orden)
    actual = []
    i = 0
    n = len(html)
    while i < n:
        ch = html[i]
        if ch == "<":
            j = html.find(">", i)
            if j == -1:
                actual.append(html[i:])
                break
            tag = html[i:j + 1]
            actual.append(tag)
            inner = tag[1:-1].strip()
            if inner.startswith("/"):
                nombre = inner[1:].split()[0].lower()
                # Cerrar la última coincidencia
                for k in range(len(pila) - 1, -1, -1):
                    if pila[k] == nombre:
                        del pila[k]
                        break
            elif not inner.endswith("/") and not inner.startswith("!"):
                nombre = inner.split()[0].lower()
                # br es auto-cerrada en HTML, no la apilamos
                if nombre not in ("br",):
                    pila.append(nombre)
            i = j + 1
        elif ch == sep:
            cierres = "".join(f"</{t}>" for t in reversed(pila))
            aperturas = "".join(f"<{t}>" for t in pila)
            actual.append(cierres)
            partes.append("".join(actual))
            actual = [aperturas]
            i += 1
        else:
            actual.append(ch)
            i += 1
    partes.append("".join(actual))
    return partes


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
    infos_pendientes = []          # buffer de infos consecutivas a fusionar
    vacios_desde_ultima_info = 0   # nº de párrafos vacíos vistos tras la última info
    MAX_VACIOS_FUSION_INFO = 2     # hasta 2 saltos de renglón => misma caja

    consejo_buffer = []            # buffer de párrafos dentro de un bloque #...#
    dentro_consejo = False
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
            html = "<br/><br/>".join(citas_pendientes)
            historia.append(KeepTogether(
                Paragraph(html, estilos["CitaCaja"])
            ))
            citas_pendientes.clear()

    def vaciar_infos():
        nonlocal vacios_desde_ultima_info
        if infos_pendientes:
            html = "<br/><br/>".join(infos_pendientes)
            historia.append(KeepTogether(
                Paragraph(decorar_info_adicional_html(html), estilos["InfoAdicional"])
            ))
            infos_pendientes.clear()
        vacios_desde_ultima_info = 0

    def _normalizar_html_info(partes):
        piezas = []
        ultimo_fue_salto = False
        for parte in partes:
            if parte is None:
                if not ultimo_fue_salto:
                    piezas.append("")
                    ultimo_fue_salto = True
                continue
            texto = (parte or "").strip()
            if not texto:
                continue
            piezas.append(texto)
            ultimo_fue_salto = False
        return "<br/><br/>".join(piezas)

    def emitir_consejo():
        nonlocal dentro_consejo
        if consejo_buffer:
            html = "<br/><br/>".join(consejo_buffer)
            historia.append(KeepTogether(
                Paragraph(html, estilos["ConsejoDM"])
            ))
            consejo_buffer.clear()
        dentro_consejo = False

    def emitir_info_adicional():
        nonlocal dentro_info
        if info_buffer:
            html = _normalizar_html_info(info_buffer)
            historia.append(KeepTogether(
                Paragraph(decorar_info_adicional_html(html), estilos["InfoAdicional"])
            ))
            info_buffer.clear()
        dentro_info = False

    for parrafo in doc_word.paragraphs:
        # 1) Imágenes embebidas en el párrafo
        imgs = extraer_imagenes_de_parrafo(parrafo, doc_word)
        if imgs:
            # Las imágenes interrumpen cualquier bloque abierto
            vaciar_infos()
            emitir_info_adicional()
            emitir_consejo()
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
            vaciar_infos()
            emitir_consejo()
            vaciar_citas()
            vaciar_lista()
            dentro_info = True
            info_buffer.clear()
            continue

        if es_fin_bloque_info(texto_plano):
            emitir_info_adicional()
            continue

        if not texto_html.strip():
            if dentro_info:
                info_buffer.append(None)
                continue
            # Párrafo vacío: si superamos el umbral, cerramos la caja de citas.
            if citas_pendientes:
                vacios_desde_ultima_cita += 1
                if vacios_desde_ultima_cita > MAX_VACIOS_FUSION_CITA:
                    vaciar_citas()
                    vacios_desde_ultima_cita = 0
            if infos_pendientes:
                vacios_desde_ultima_info += 1
                if vacios_desde_ultima_info > MAX_VACIOS_FUSION_INFO:
                    vaciar_infos()
            vaciar_lista()
            # Dentro de un bloque #...# las líneas vacías se ignoran
            # (no rompen el bloque; ya separamos con <br/><br/>).
            if not dentro_consejo and not dentro_info:
                historia.append(Spacer(1, 4))
            continue

        clave = estilo_para_parrafo(parrafo)
        es_lista = clave == "Lista" or (
            parrafo.style.name and "List Bullet" in parrafo.style.name
        )

        if dentro_info:
            if es_lista:
                info_buffer.append(f"• {texto_html}")
            else:
                info_buffer.append(texto_html)
            continue

        # ---------- Bloques delimitados por # ... # (también inline) ----------
        if "#" in texto_html or dentro_consejo:
            # Partimos el HTML por '#' manteniendo etiquetas balanceadas.
            segmentos = _split_html_balanceado(texto_html, "#")
            estado_dentro = dentro_consejo
            # Texto "fuera" que se acumula para reemitir como párrafo/bullet original
            html_fuera_partes = []

            def _emitir_fuera_acumulado():
                """Emite lo acumulado fuera del consejo respetando estilo del párrafo."""
                nonlocal vacios_desde_ultima_info
                contenido = "".join(html_fuera_partes).strip()
                html_fuera_partes.clear()
                if not contenido:
                    return
                if es_consejo_dm(re.sub(r"<[^>]+>", "", contenido)):
                    # Formato 'CONSEJO PARA EL DM' clásico (un solo párrafo)
                    vaciar_infos()
                    vaciar_citas()
                    vaciar_lista()
                    historia.append(KeepTogether(
                        Paragraph(contenido, estilos["ConsejoDM"])
                    ))
                    return
                if es_info_adicional(re.sub(r"<[^>]+>", "", contenido)):
                    vaciar_citas()
                    vaciar_lista()
                    infos_pendientes.append(contenido)
                    vacios_desde_ultima_info = 0
                    return
                if es_lista:
                    vaciar_infos()
                    vaciar_citas()
                    items_lista_actual.append(contenido)
                elif clave == "CitaCaja":
                    vaciar_infos()
                    vaciar_lista()
                    citas_pendientes.append(contenido)
                elif clave == "InfoAdicional":
                    vaciar_citas()
                    vaciar_lista()
                    infos_pendientes.append(contenido)
                    vacios_desde_ultima_info = 0
                else:
                    vaciar_infos()
                    vaciar_citas()
                    vaciar_lista()
                    historia.append(Paragraph(contenido, estilos[clave]))

            for i, seg in enumerate(segmentos):
                if estado_dentro:
                    # Trozo dentro del consejo
                    if seg.strip():
                        consejo_buffer.append(seg)
                else:
                    # Trozo fuera del consejo: acumular para reemitirlo entero
                    if seg:
                        html_fuera_partes.append(seg)

                # Si no es el último, hay un '#': alternamos estado y, si
                # cerramos el consejo, lo emitimos; si lo abrimos, primero
                # volcamos lo acumulado fuera.
                if i < len(segmentos) - 1:
                    if estado_dentro:
                        # Cerramos consejo
                        emitir_consejo()
                    else:
                        # Abrimos consejo: primero emitimos el contenido normal
                        # acumulado hasta este punto y luego vaciamos buffers
                        # para que el cuadro azul salga exactamente en orden.
                        _emitir_fuera_acumulado()
                        vaciar_citas()
                        vaciar_lista()
                    estado_dentro = not estado_dentro

            # Al terminar el párrafo:
            dentro_consejo = estado_dentro
            # Volcar la parte 'fuera' acumulada (si la hay) como el párrafo original
            _emitir_fuera_acumulado()

            # Si el párrafo dejó el consejo abierto, añadimos un separador entre
            # párrafos (los siguientes se concatenan con <br/><br/>).
            continue
        # ---------- Fin bloques # ... # ----------

        # 2) Consejo para el DM → caja azul (formato de un solo párrafo)
        if es_consejo_dm(texto_plano):
            vaciar_infos()
            vaciar_citas()
            vaciar_lista()
            historia.append(KeepTogether(
                Paragraph(texto_html, estilos["ConsejoDM"])
            ))
            continue

        # 2.5) Información adicional → caja verde-azulada
        if clave == "InfoAdicional" or es_info_adicional(texto_plano):
            vaciar_citas()
            vaciar_lista()
            infos_pendientes.append(texto_html)
            vacios_desde_ultima_info = 0
            continue

        # 3) Listas
        if es_lista:
            vaciar_infos()
            vaciar_citas()
            items_lista_actual.append(texto_html)
            continue
        else:
            vaciar_lista()

        # 4) Citas → caja amarilla (se fusionan citas consecutivas)
        if clave == "CitaCaja":
            vaciar_infos()
            citas_pendientes.append(texto_html)
            vacios_desde_ultima_cita = 0
            continue
        else:
            # Cualquier otro contenido cierra el bloque de citas
            vaciar_infos()
            vaciar_citas()
            vacios_desde_ultima_cita = 0

        # 5) Resto: H1/H2/H3/Cuerpo
        historia.append(Paragraph(texto_html, estilos[clave]))

    emitir_consejo()
    emitir_info_adicional()
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

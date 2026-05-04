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
        spaceBefore=10, spaceAfter=10,
        borderColor=COLOR_AMA_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=12, backColor=COLOR_AMA_FONDO,
    ))
    # Caja AZUL (Consejo para el DM)
    estilos.add(ParagraphStyle(
        name="ConsejoDM",
        fontName=FUENTE_TEXTO, fontSize=11, leading=15,
        textColor=COLOR_AZUL_TEXTO, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10,
        spaceBefore=10, spaceAfter=10,
        borderColor=COLOR_AZUL_BORDE, borderWidth=1, borderRadius=8,
        borderPadding=12, backColor=COLOR_AZUL_FONDO,
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


def runs_a_html(parrafo):
    """Convierte runs (negrita/cursiva/subrayado) a HTML para ReportLab."""
    partes = []
    algun_formato_run = False
    for r in parrafo.runs:
        texto = r.text or ""
        if not texto:
            continue
        texto = (texto.replace("&", "&amp;")
                      .replace("<", "&lt;")
                      .replace(">", "&gt;"))
        if r.bold:
            texto = f"<b>{texto}</b>"
            algun_formato_run = True
        if r.italic:
            texto = f"<i>{texto}</i>"
            algun_formato_run = True
        if r.underline:
            texto = f"<u>{texto}</u>"
            algun_formato_run = True
        partes.append(texto)
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


class DocConTOC(BaseDocTemplate):
    """DocTemplate que notifica entradas a la TOC al pasar por H1/H2."""
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        frame = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height, id="normal")
        self.addPageTemplates([PageTemplate(id="Todo", frames=frame)])

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            estilo = flowable.style.name
            texto = flowable.getPlainText()
            if estilo == "H1":
                self.notify("TOCEntry", (0, texto, self.page))
            elif estilo == "H2":
                self.notify("TOCEntry", (1, texto, self.page))


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

    for parrafo in doc_word.paragraphs:
        # 1) Imágenes embebidas en el párrafo
        imgs = extraer_imagenes_de_parrafo(parrafo, doc_word)
        if imgs:
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

        if not texto_html.strip():
            # Párrafo vacío: si superamos el umbral, cerramos la caja de citas.
            if citas_pendientes:
                vacios_desde_ultima_cita += 1
                if vacios_desde_ultima_cita > MAX_VACIOS_FUSION_CITA:
                    vaciar_citas()
                    vacios_desde_ultima_cita = 0
            vaciar_lista()
            historia.append(Spacer(1, 4))
            continue

        # 2) Consejo para el DM → caja azul
        if es_consejo_dm(texto_plano):
            vaciar_citas()
            vaciar_lista()
            historia.append(KeepTogether(
                Paragraph(texto_html, estilos["ConsejoDM"])
            ))
            continue

        clave = estilo_para_parrafo(parrafo)

        # 3) Listas
        if clave == "Lista" or (parrafo.style.name and "List Bullet" in parrafo.style.name):
            vaciar_citas()
            items_lista_actual.append(texto_html)
            continue
        else:
            vaciar_lista()

        # 4) Citas → caja amarilla (se fusionan citas consecutivas)
        if clave == "CitaCaja":
            citas_pendientes.append(texto_html)
            vacios_desde_ultima_cita = 0
            continue
        else:
            # Cualquier otro contenido cierra el bloque de citas
            vaciar_citas()
            vacios_desde_ultima_cita = 0

        # 5) Resto: H1/H2/H3/Cuerpo
        historia.append(Paragraph(texto_html, estilos[clave]))

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

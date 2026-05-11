import io
import re

from docx.oxml.ns import qn
from docx.table import Table as TablaDocx
from docx.text.paragraph import Paragraph as ParrafoDocx
from PIL import Image as PILImage

import configuracion_pdf as cfg


def estilo_para_parrafo(parrafo):
    nombre = (parrafo.style.name or "").lower()
    if "heading 1" in nombre or "título 1" in nombre or "titulo 1" in nombre:
        return "H1"
    if "heading 2" in nombre or "título 2" in nombre or "titulo 2" in nombre:
        return "H2"
    if "heading 3" in nombre or "título 3" in nombre or "titulo 3" in nombre:
        return "H3"
    if ("información adicional" in nombre or "informacion adicional" in nombre or "info adicional" in nombre):
        return "CajaInfoAdicional"
    if "consejos" in nombre or "consejo dm" in nombre or "consejo para el dm" in nombre:
        return "CajaConsejoDm"
    if "quote" in nombre or "cita" in nombre:
        return "CajaCita"
    if "list" in nombre or "lista" in nombre:
        return "Lista"
    return "Cuerpo"


def _markdown_en_linea_a_html(texto):
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", texto)
    return texto


def _escapar_html(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _escapar_atributo_html(texto):
    return _escapar_html(texto).replace('"', '&quot;')


def _parrafo_tiene_salto_de_pagina_previo(parrafo):
    propiedades = parrafo._p.find(qn("w:pPr"))
    if propiedades is None:
        return False
    nodo = propiedades.find(qn("w:pageBreakBefore"))
    if nodo is None:
        return False
    valor = (nodo.get(qn("w:val")) or "true").strip().lower()
    return valor not in ("0", "false", "off", "no")


def _parrafo_es_solo_salto_de_pagina(parrafo):
    if (parrafo.text or "").strip():
        return False
    for nodo in parrafo._p.iter():
        if nodo.tag == qn("w:br") and (nodo.get(qn("w:type")) or "").lower() == "page":
            return True
    return False


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
    texto_html = f'<link href="{destino}"><u><font color="#0563C1">{texto_html}</font></u></link>'
    return texto_html, True


def parrafo_a_html(parrafo):
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
    if not algun_formato_run and ("*" in html):
        html = _markdown_en_linea_a_html(html)
    return html


def extraer_imagenes_de_parrafo(parrafo, documento_word):
    imagenes = []
    for drawing in parrafo._element.findall(".//" + qn("w:drawing")):
        blip = drawing.find(".//" + qn("a:blip"))
        if blip is None:
            continue
        rel_id = blip.get(qn("r:embed"))
        if rel_id and rel_id in documento_word.part.related_parts:
            blob = documento_word.part.related_parts[rel_id].blob
            dimensiones = _leer_dimensiones_imagen(blob)
            if dimensiones is None:
                continue
            ancho_px, alto_px = dimensiones
            tamano_docx = _extraer_tamano_docx_de_drawing(drawing)
            imagenes.append({
                "blob": blob,
                "ancho_px": ancho_px,
                "alto_px": alto_px,
                "base_ancho_pt": tamano_docx[0] if tamano_docx else None,
                "base_alto_pt": tamano_docx[1] if tamano_docx else None,
            })
    return imagenes


def _leer_dimensiones_imagen(blob):
    bio = io.BytesIO(blob)
    try:
        with PILImage.open(bio) as imagen:
            ancho, alto = imagen.size
    except Exception:
        return None
    if not ancho or not alto:
        return None
    return float(ancho), float(alto)


def _extraer_tamano_docx_de_drawing(drawing_xml):
    extent = drawing_xml.find(".//" + qn("wp:extent"))
    if extent is None:
        extent = drawing_xml.find(".//" + qn("a:ext"))
    if extent is None:
        return None
    try:
        ancho_pt = float(extent.get("cx")) / 12700.0
        alto_pt = float(extent.get("cy")) / 12700.0
    except (TypeError, ValueError):
        return None
    if ancho_pt <= 0 or alto_pt <= 0:
        return None
    return ancho_pt, alto_pt


def es_consejo_dm(texto_plano):
    limpio = texto_plano.lstrip(" *_“\"'\t").lower()
    return limpio.startswith("consejo para el dm")


def _parsear_tag_html(tag):
    interior = tag[1:-1].strip()
    nombre = interior.lstrip("/").split()[0].lower() if interior else ""
    if nombre.startswith("br"):
        nombre = "br"
    es_cierre = interior.startswith("/")
    es_autocierre = interior.endswith("/") or nombre == "br"
    return nombre, es_cierre, es_autocierre


def _actualizar_pila_tags_html(pila, nombre, es_cierre, es_autocierre, tag):
    if es_cierre:
        for indice in range(len(pila) - 1, -1, -1):
            if pila[indice][0] == nombre:
                del pila[indice]
                break
    elif not es_autocierre and nombre:
        pila.append((nombre, tag))


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
        nombre, es_cierre, es_autocierre = _parsear_tag_html(token)
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
            _actualizar_pila_tags_html(pila_derecha, nombre, es_cierre, es_autocierre, token)
        else:
            izquierda.append(token)
            _actualizar_pila_tags_html(pila_izquierda, nombre, es_cierre, es_autocierre, token)
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
    indice = 0
    total = len(html)
    while indice < total:
        if html[indice] == "<":
            fin = html.find(">", indice)
            if fin == -1:
                break
            tag = html[indice:fin + 1]
            interior = tag[1:-1].strip()
            if interior.startswith("/"):
                nombre = interior[1:].split()[0].lower()
                for posicion in range(len(pila_tags) - 1, -1, -1):
                    if pila_tags[posicion][0] == nombre:
                        del pila_tags[posicion]
                        break
                if iniciado:
                    resultado.append(tag)
            elif not interior.endswith("/") and not interior.startswith("!"):
                nombre = interior.split()[0].lower()
                if nombre not in ("br",):
                    pila_tags.append((nombre, tag))
                if iniciado:
                    resultado.append(tag)
            elif iniciado:
                resultado.append(tag)
            indice = fin + 1
            continue
        if caracteres_restantes > 0:
            caracteres_restantes -= 1
            if caracteres_restantes == 0:
                iniciado = True
                resultado.extend(tag for _, tag in pila_tags)
            indice += 1
            continue
        if not iniciado:
            iniciado = True
            resultado.extend(tag for _, tag in pila_tags)
        resultado.append(html[indice])
        indice += 1
    return "".join(resultado).lstrip()


def decorar_consejo_dm_html(texto_html):
    texto_plano = re.sub(r"<[^>]+>", "", texto_html)
    match = re.match(r'^\s*(?P<prefijo>consejo para el dm)\s*(?P<detalle>\([^)]*\))?\s*:?\s*', texto_plano, flags=re.IGNORECASE)
    titulo = "Consejo para el DM"
    cuerpo = texto_html
    if match:
        detalle = (match.group("detalle") or "").strip()
        if detalle:
            titulo = f"{titulo} {detalle}"
        cuerpo = _quitar_prefijo_visible_en_html(texto_html, len(match.group(0)))
    etiqueta = f'<font color="#{cfg.COLOR_AZUL_TEXTO.hexval()[2:]}"><b>{titulo}</b></font><br/>'
    return etiqueta + cuerpo


def es_info_adicional(texto_plano):
    limpio = texto_plano.lstrip(" *_“\"'\t").lower()
    return limpio.startswith("información adicional") or limpio.startswith("informacion adicional") or limpio.startswith("info adicional") or limpio.startswith("dato adicional")


def decorar_info_adicional_html(texto_html):
    etiqueta = f'<font color="#{cfg.COLOR_INFO_BORDE.hexval()[2:]}"><b>[i] Información adicional</b></font><br/>'
    patrones = [r'^\s*(información adicional|informacion adicional|info adicional|dato adicional)\s*:\s*']
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


def es_inicio_bloque_tesoro(texto_plano):
    limpio = " ".join((texto_plano or "").strip().lower().split())
    return limpio in (":::tesoro", "::: tesoro", ":::premio", "::: premio", ":::tesoro :::", "::: tesoro :::", ":::premio :::", "::: premio :::")


def es_inicio_bloque_objeto(texto_plano):
    limpio = " ".join((texto_plano or "").strip().lower().split())
    return limpio in (":::objeto", "::: objeto", ":::objeto :::", "::: objeto :::")


def es_fin_bloque_manual(texto_plano):
    return texto_plano.strip() == ":::"


def _puntos_word(longitud):
    if longitud is None:
        return 0
    try:
        return float(longitud.pt)
    except Exception:
        return 0


def es_lista_parrafo(parrafo):
    nombre = (parrafo.style.name or "").lower()
    if "list" in nombre or "lista" in nombre:
        return True
    propiedades = parrafo._p.find(qn("w:pPr"))
    return propiedades is not None and propiedades.find(qn("w:numPr")) is not None


def nivel_lista_parrafo(parrafo):
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


def item_caja_desde_parrafo(parrafo, texto_html):
    return {
        "tipo": "texto",
        "html": texto_html,
        "es_lista": es_lista_parrafo(parrafo),
        "nivel_lista": nivel_lista_parrafo(parrafo),
        "sangria_izquierda": _puntos_word(parrafo.paragraph_format.left_indent),
        "sangria_primera_linea": _puntos_word(parrafo.paragraph_format.first_line_indent),
    }


def item_caja_plano(texto_html):
    return {
        "tipo": "texto",
        "html": texto_html,
        "es_lista": False,
        "nivel_lista": 0,
        "sangria_izquierda": 0,
        "sangria_primera_linea": 0,
    }


def item_caja_imagen(imagen):
    return {"tipo": "imagen", "imagen": imagen}


def item_caja_tabla(tabla_docx):
    return {"tipo": "tabla", "tabla": tabla_docx}


def item_caja_grupo_imagenes(imagenes):
    return {"tipo": "grupo_imagenes", "imagenes": list(imagenes)}


def crear_items_imagenes(imagenes):
    if not imagenes:
        return []
    if len(imagenes) >= 2:
        return [item_caja_grupo_imagenes(imagenes)]
    return [item_caja_imagen(imagenes[0])]


def agregar_imagenes_a_bloque(bloque, imagenes):
    for item in crear_items_imagenes(imagenes):
        bloque.append(item)


def iterar_elementos_documento(documento_word):
    for child in documento_word.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield "parrafo", ParrafoDocx(child, documento_word)
        elif child.tag == qn("w:tbl"):
            yield "tabla", TablaDocx(child, documento_word)


def celda_docx_a_html(celda):
    partes = []
    for parrafo in celda.paragraphs:
        html = parrafo_a_html(parrafo).strip()
        if html:
            partes.append(html)
    return "<br/><br/>".join(partes) if partes else "&nbsp;"

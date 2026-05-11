import io

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import CondPageBreak, Flowable, Image, Paragraph, Spacer, Table, TableStyle

import configuracion_pdf as cfg
from procesamiento_word import celda_docx_a_html, item_caja_plano


def crear_flujo_imagen_desde_descriptor(imagen, ancho_max, alto_max=None, permitir_ampliacion=True, usar_tamano_docx=False):
    if not imagen:
        return None
    if usar_tamano_docx and imagen.get("base_ancho_pt") and imagen.get("base_alto_pt"):
        ancho_origen = float(imagen["base_ancho_pt"])
        alto_origen = float(imagen["base_alto_pt"])
    else:
        ancho_origen = float(imagen.get("ancho_px") or 0)
        alto_origen = float(imagen.get("alto_px") or 0)
    if ancho_origen <= 0 or alto_origen <= 0:
        return None
    bio = io.BytesIO(imagen["blob"])
    bio.seek(0)
    escala_ancho = float(ancho_max) / float(ancho_origen) if ancho_max else 1.0
    escala_alto = float(alto_max) / float(alto_origen) if alto_max else 1.0
    escala = min(escala_ancho, escala_alto)
    if not permitir_ampliacion:
        escala = min(1.0, escala)
    ancho = max(1.0, float(ancho_origen) * escala)
    alto = max(1.0, float(alto_origen) * escala)
    flujo = Image(bio, width=ancho, height=alto)
    flujo.hAlign = "CENTER"
    return flujo


def crear_flujo_imagen(blob, ancho_max, alto_max=None, permitir_ampliacion=True):
    from procesamiento_word import _leer_dimensiones_imagen

    dimensiones = _leer_dimensiones_imagen(blob)
    if dimensiones is None:
        return None
    ancho_origen, alto_origen = dimensiones
    bio = io.BytesIO(blob)
    bio.seek(0)
    escala_ancho = float(ancho_max) / float(ancho_origen) if ancho_max else 1.0
    escala_alto = float(alto_max) / float(alto_origen) if alto_max else 1.0
    escala = min(escala_ancho, escala_alto)
    if not permitir_ampliacion:
        escala = min(1.0, escala)
    ancho = max(1.0, float(ancho_origen) * escala)
    alto = max(1.0, float(alto_origen) * escala)
    imagen = Image(bio, width=ancho, height=alto)
    imagen.hAlign = "CENTER"
    return imagen


def crear_fila_de_imagenes(imagenes, ancho_disponible, alto_max=None, espacio=10):
    validas = [imagen for imagen in imagenes if imagen.get("ancho_px") and imagen.get("alto_px")]
    if not validas:
        return None
    if len(validas) == 1:
        return crear_flujo_imagen_desde_descriptor(validas[0], ancho_disponible, alto_max=alto_max, permitir_ampliacion=False, usar_tamano_docx=True)
    suma_relaciones = sum(imagen["ancho_px"] / imagen["alto_px"] for imagen in validas)
    ancho_libre = max(1.0, ancho_disponible - (espacio * (len(validas) - 1)))
    altura_objetivo = ancho_libre / suma_relaciones if suma_relaciones else 0
    if alto_max:
        altura_objetivo = min(altura_objetivo, float(alto_max))
    if altura_objetivo <= 0:
        return None
    anchos = [max(1.0, (imagen["ancho_px"] / imagen["alto_px"]) * altura_objetivo) for imagen in validas]
    if altura_objetivo < 72 or min(anchos) < 90:
        return None
    celdas = []
    for imagen, ancho in zip(validas, anchos):
        flujo = crear_flujo_imagen(imagen["blob"], ancho, alto_max=altura_objetivo, permitir_ampliacion=True)
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


def crear_flujos_imagenes(imagenes, ancho_disponible, alto_max=None, espacio=10):
    if not imagenes:
        return []
    fila = crear_fila_de_imagenes(imagenes, ancho_disponible, alto_max=alto_max, espacio=espacio)
    if fila is not None:
        return [fila]
    flujos = []
    for imagen in imagenes:
        flujo = crear_flujo_imagen_desde_descriptor(imagen, ancho_disponible, alto_max=alto_max, permitir_ampliacion=False, usar_tamano_docx=True)
        if flujo is not None:
            flujos.append(flujo)
    return flujos


def tabla_docx_a_flujo(tabla_docx, ancho_max, estilo_base):
    filas = []
    max_cols = 0
    for fila in tabla_docx.rows:
        celdas = [celda_docx_a_html(celda) for celda in fila.cells]
        filas.append(celdas)
        max_cols = max(max_cols, len(celdas))
    if not filas or max_cols == 0:
        return None
    estilo_celda = ParagraphStyle(name=f"{estilo_base.name}TablaCelda", parent=estilo_base, alignment=TA_LEFT, leftIndent=0, rightIndent=0, firstLineIndent=0, spaceBefore=0, spaceAfter=0, borderWidth=0, borderPadding=0, backColor=None)
    datos = []
    for fila in filas:
        fila_extendida = fila + ["&nbsp;"] * (max_cols - len(fila))
        datos.append([Paragraph(celda_html, estilo_celda) for celda_html in fila_extendida])
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


def crear_titulo_decorado(titulo, color):
    return f'<font color="#{color.hexval()[2:]}"><b>{titulo}</b></font><br/>'


def decorar_npc_en_html(texto_html):
    return crear_titulo_decorado("NPC", cfg.COLOR_NPC_TEXTO) + texto_html


def decorar_enemigo_en_html(texto_html):
    return crear_titulo_decorado("Enemigo", cfg.COLOR_ENEMIGO_TEXTO) + texto_html


def decorar_aliado_en_html(texto_html):
    return crear_titulo_decorado("Aliado", cfg.COLOR_ALIADO_TEXTO) + texto_html


def decorar_tesoro_en_html(texto_html):
    return crear_titulo_decorado("Tesoro", cfg.COLOR_TESORO_TEXTO) + texto_html


def decorar_premio_en_html(texto_html):
    return crear_titulo_decorado("Premio", cfg.COLOR_TESORO_TEXTO) + texto_html


def decorar_objeto_en_html(texto_html):
    return crear_titulo_decorado("Objeto", cfg.COLOR_OBJETO_TEXTO) + texto_html


def estilo_interno_caja(estilo_base, item, sufijo):
    estilo = ParagraphStyle(name=f"{estilo_base.name}Interno{sufijo}", parent=estilo_base, leftIndent=0, rightIndent=0, firstLineIndent=0, spaceBefore=0, spaceAfter=6, borderWidth=0, borderPadding=0, backColor=None)
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


def crear_cabecera_decorada_caja(estilo_base, decorador, sufijo):
    estilo = estilo_interno_caja(estilo_base, item_caja_plano(""), sufijo)
    estilo.spaceAfter = 4
    return Paragraph(decorador(""), estilo)


def altura_minima_visible_caja(estilo_base, decorador=None):
    altura = max(estilo_base.leading * cfg.MINIMO_RENGLONES_CAJA_ANTES_DE_MOVER, estilo_base.fontSize)
    altura += 12
    if decorador is not None:
        altura += estilo_base.leading + 4
    return altura


class CajaPartible(Flowable):
    def __init__(self, elementos, estilo_base, ancho_total, left_padding=10, right_padding=10, top_padding=6, bottom_padding=6, space_before=2, space_after=4):
        super().__init__()
        self.elementos = list(elementos)
        self.estilo_base = estilo_base
        self.ancho_total = ancho_total
        self.left_padding = left_padding
        self.right_padding = right_padding
        self.top_padding = top_padding
        self.bottom_padding = bottom_padding
        self.spaceBefore = space_before
        self.spaceAfter = space_after
        self._layout = []
        self.width = ancho_total
        self.height = 0

    @staticmethod
    def _recortar_espaciadores(elementos):
        recortados = list(elementos)
        while recortados and isinstance(recortados[0], Spacer):
            recortados.pop(0)
        while recortados and isinstance(recortados[-1], Spacer):
            recortados.pop()
        return recortados

    def _ancho_interno(self, ancho_disponible=None):
        ancho = self.ancho_total if ancho_disponible is None else ancho_disponible
        return max(20, ancho - self.left_padding - self.right_padding)

    @staticmethod
    def _espacio_antes(elemento):
        try:
            return max(0, float(elemento.getSpaceBefore() or 0))
        except Exception:
            return 0

    @staticmethod
    def _espacio_despues(elemento):
        try:
            return max(0, float(elemento.getSpaceAfter() or 0))
        except Exception:
            return 0

    def _medir_elemento(self, elemento, ancho_interno, alto_disponible):
        ancho, alto = elemento.wrap(ancho_interno, max(0, alto_disponible))
        return ancho, alto, self._espacio_antes(elemento), self._espacio_despues(elemento)

    @staticmethod
    def _es_elemento_de_texto(elemento):
        return isinstance(elemento, Paragraph)

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        ancho_interno = self._ancho_interno(availWidth)
        self._layout = []
        altura_total = self.top_padding + self.bottom_padding
        for elemento in self.elementos:
            ancho, alto, espacio_antes, espacio_despues = self._medir_elemento(elemento, ancho_interno, availHeight)
            self._layout.append((elemento, ancho, alto, espacio_antes, espacio_despues))
            altura_total += espacio_antes + alto + espacio_despues
        self.height = altura_total
        return availWidth, altura_total

    def split(self, availWidth, availHeight):
        if not self.elementos:
            return []
        ancho_interno = self._ancho_interno(availWidth)
        alto_contenido = max(0, availHeight - self.top_padding - self.bottom_padding)
        if alto_contenido <= 0:
            return []
        fragmento_actual = []
        altura_usada = 0
        for indice, elemento in enumerate(self.elementos):
            ancho, alto, espacio_antes, espacio_despues = self._medir_elemento(elemento, ancho_interno, alto_contenido - altura_usada)
            altura_necesaria = espacio_antes + alto + espacio_despues
            if altura_usada + altura_necesaria <= alto_contenido + 0.1:
                fragmento_actual.append(elemento)
                altura_usada += altura_necesaria
                continue
            if not self._es_elemento_de_texto(elemento):
                if fragmento_actual:
                    resto = self._recortar_espaciadores([elemento] + self.elementos[indice + 1:])
                    if resto:
                        return [self._clonar(fragmento_actual), self._clonar(resto)]
                    return [self._clonar(fragmento_actual)]
                partes_no_texto = self._recortar_espaciadores(elemento.split(ancho_interno, alto_contenido))
                if partes_no_texto:
                    primera_parte = partes_no_texto[0]
                    resto = self._recortar_espaciadores(list(partes_no_texto[1:]) + self.elementos[indice + 1:])
                    if resto:
                        return [self._clonar([primera_parte]), self._clonar(resto)]
                    return [self._clonar([primera_parte])]
                return []
            alto_para_split = max(0, alto_contenido - altura_usada - espacio_antes - espacio_despues)
            partes = self._recortar_espaciadores(elemento.split(ancho_interno, alto_para_split))
            if partes:
                primera_parte = partes[0]
                _, alto_primera, _, _ = self._medir_elemento(primera_parte, ancho_interno, alto_para_split)
                altura_primera = espacio_antes + alto_primera + espacio_despues
                if altura_usada + altura_primera <= alto_contenido + 0.1:
                    fragmento_actual.append(primera_parte)
                    resto = self._recortar_espaciadores(list(partes[1:]) + self.elementos[indice + 1:])
                    if fragmento_actual and resto:
                        return [self._clonar(fragmento_actual), self._clonar(resto)]
            if fragmento_actual:
                resto = self._recortar_espaciadores([elemento] + self.elementos[indice + 1:])
                if resto:
                    return [self._clonar(fragmento_actual), self._clonar(resto)]
            return []
        return []

    def _clonar(self, elementos):
        return CajaPartible(elementos, self.estilo_base, self.ancho_total, left_padding=self.left_padding, right_padding=self.right_padding, top_padding=self.top_padding, bottom_padding=self.bottom_padding, space_before=self.spaceBefore, space_after=self.spaceAfter)

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        if self.estilo_base.backColor is not None:
            canvas.setFillColor(self.estilo_base.backColor)
            canvas.setStrokeColor(self.estilo_base.backColor)
            canvas.rect(0, 0, self.width, self.height, stroke=0, fill=1)
        if self.estilo_base.borderWidth:
            canvas.setStrokeColor(self.estilo_base.borderColor)
            canvas.setLineWidth(self.estilo_base.borderWidth)
            canvas.rect(0, 0, self.width, self.height, stroke=1, fill=0)
        y = self.height - self.top_padding
        ancho_interno = self._ancho_interno(self.width)
        for elemento, ancho, alto, espacio_antes, espacio_despues in self._layout:
            y -= espacio_antes
            y -= alto
            elemento.drawOn(canvas, self.left_padding, y, _sW=max(0, ancho_interno - ancho))
            y -= espacio_despues
        canvas.restoreState()


def centrar_en_fila(elemento, ancho):
    tabla = Table([[elemento]], colWidths=[ancho], hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tabla


class BloqueVisualConCabecera(Flowable):
    def __init__(self, cabecera, bloque, espacio=4):
        super().__init__()
        self.cabecera = cabecera
        self.bloque = bloque
        self.espacio = espacio
        self.width = 0
        self.height = 0
        self._layout = None

    def wrap(self, availWidth, availHeight):
        ancho_cabecera, alto_cabecera = self.cabecera.wrap(availWidth, availHeight)
        ancho_bloque, alto_bloque = self.bloque.wrap(availWidth, max(0, availHeight - alto_cabecera - self.espacio))
        self.width = max(ancho_cabecera, ancho_bloque)
        self.height = alto_cabecera + self.espacio + alto_bloque
        self._layout = (ancho_cabecera, alto_cabecera, ancho_bloque, alto_bloque)
        return self.width, self.height

    def split(self, availWidth, availHeight):
        _, alto_total = self.wrap(availWidth, availHeight)
        if alto_total <= availHeight + 0.1:
            return []
        _, alto_cabecera, _, _ = self._layout
        alto_para_bloque = max(0, availHeight - alto_cabecera - self.espacio)
        if alto_para_bloque <= 0:
            return []
        partes_bloque = self.bloque.split(availWidth, alto_para_bloque)
        if not partes_bloque:
            return []
        primera_parte = BloqueVisualConCabecera(self.cabecera, partes_bloque[0], espacio=self.espacio)
        return [primera_parte] + list(partes_bloque[1:])

    def draw(self):
        if self._layout is None:
            self.wrap(self.width or 0, 0)
        ancho_cabecera, _, ancho_bloque, alto_bloque = self._layout
        self.cabecera.drawOn(self.canv, 0, alto_bloque + self.espacio, _sW=max(0, self.width - ancho_cabecera))
        self.bloque.drawOn(self.canv, 0, 0, _sW=max(0, self.width - ancho_bloque))


def agrupar_cabecera_y_bloque(cabecera, bloque):
    if cabecera is None:
        return bloque
    return BloqueVisualConCabecera(cabecera, bloque, espacio=4)


def obtener_cabecera_de_caja(primer_bloque, decorador, estilo_base, indice):
    if not primer_bloque or decorador is None:
        return None, primer_bloque, indice
    cabecera = crear_cabecera_decorada_caja(estilo_base, decorador, indice)
    return cabecera, False, indice + 1


def agregar_separador_a_contenido_caja(contenido, alto):
    if contenido and not isinstance(contenido[-1], Spacer):
        contenido.append(Spacer(1, alto))


def agregar_bloque_visual_a_contenido_caja(contenido, bloque, cabecera, alto_separador):
    if bloque is None:
        return
    contenido.append(agrupar_cabecera_y_bloque(cabecera, bloque))
    agregar_separador_a_contenido_caja(contenido, alto_separador)


def calcular_ancho_tabla_en_caja(ancho_interno, margen_extra=8):
    return max(40, ancho_interno - margen_extra)


def agregar_tabla_a_caja(contenido, parte, estilo_base, ancho_interno, cabecera):
    ancho_tabla = calcular_ancho_tabla_en_caja(ancho_interno)
    tabla = tabla_docx_a_flujo(parte.get("tabla"), ancho_tabla, estilo_base)
    if tabla is not None:
        tabla.hAlign = "CENTER"
    agregar_bloque_visual_a_contenido_caja(contenido, tabla, cabecera, 6)


def agregar_imagen_a_caja(contenido, parte, ancho_interno, alto_max_imagen, cabecera):
    flujo_imagen = crear_flujo_imagen_desde_descriptor(parte.get("imagen") or {}, ancho_interno, alto_max=alto_max_imagen, permitir_ampliacion=False, usar_tamano_docx=True)
    if flujo_imagen is None:
        return
    flujo_imagen.hAlign = "CENTER"
    imagen_centrada = centrar_en_fila(flujo_imagen, ancho_interno)
    agregar_bloque_visual_a_contenido_caja(contenido, imagen_centrada, cabecera, 8)


def agregar_grupo_imagenes_a_caja(contenido, parte, ancho_interno, alto_max_imagen, cabecera):
    fila_imagenes = crear_fila_de_imagenes(parte.get("imagenes") or [], ancho_interno, alto_max=alto_max_imagen)
    if fila_imagenes is not None:
        agregar_bloque_visual_a_contenido_caja(contenido, fila_imagenes, cabecera, 8)
        return
    cabecera_actual = cabecera
    for flujo_imagen in crear_flujos_imagenes(parte.get("imagenes") or [], ancho_interno, alto_max=alto_max_imagen):
        imagen_centrada = centrar_en_fila(flujo_imagen, ancho_interno)
        agregar_bloque_visual_a_contenido_caja(contenido, imagen_centrada, cabecera_actual, 8)
        cabecera_actual = None


def agregar_texto_a_caja(contenido, parte, estilo_base, decorador, primer_bloque, indice):
    html = (parte.get("html") or "").strip()
    if not html:
        return primer_bloque, indice
    if primer_bloque and decorador is not None:
        html = decorador(html)
    estilo = estilo_interno_caja(estilo_base, parte, indice)
    bullet_text = "•" if parte["es_lista"] else None
    contenido.append(Paragraph(html, estilo, bulletText=bullet_text))
    return False, indice + 1


def normalizar_contenido_caja(contenido):
    while contenido and isinstance(contenido[0], Spacer):
        contenido.pop(0)
    while contenido and isinstance(contenido[-1], Spacer):
        contenido.pop()
    return contenido


def crear_caja_partible(contenido, estilo_base, ancho_total):
    return CajaPartible(contenido, estilo_base, ancho_total, left_padding=10, right_padding=10, top_padding=6, bottom_padding=6, space_before=2, space_after=4)


def renderizar_caja(partes, estilo_base, ancho_total, decorador=None):
    contenido = []
    primer_bloque = True
    indice = 0
    ancho_interno = max(40, ancho_total - 20)
    alto_max_imagen = max(80, cfg.TAMANO_PAGINA[1] - (2 * cfg.MARGEN) - 48)
    for parte in partes:
        if parte is None:
            agregar_separador_a_contenido_caja(contenido, 6)
            continue
        if parte.get("tipo") == "tabla":
            cabecera, primer_bloque, indice = obtener_cabecera_de_caja(primer_bloque, decorador, estilo_base, indice)
            agregar_tabla_a_caja(contenido, parte, estilo_base, ancho_interno, cabecera)
            continue
        if parte.get("tipo") == "imagen":
            cabecera, primer_bloque, indice = obtener_cabecera_de_caja(primer_bloque, decorador, estilo_base, indice)
            agregar_imagen_a_caja(contenido, parte, ancho_interno, alto_max_imagen, cabecera)
            continue
        if parte.get("tipo") == "grupo_imagenes":
            cabecera, primer_bloque, indice = obtener_cabecera_de_caja(primer_bloque, decorador, estilo_base, indice)
            agregar_grupo_imagenes_a_caja(contenido, parte, ancho_interno, alto_max_imagen, cabecera)
            continue
        primer_bloque, indice = agregar_texto_a_caja(contenido, parte, estilo_base, decorador, primer_bloque, indice)
    if not contenido:
        return None
    contenido = normalizar_contenido_caja(contenido)
    if not contenido:
        return None
    caja = crear_caja_partible(contenido, estilo_base, ancho_total)
    alto_util_pagina = max(40, cfg.TAMANO_PAGINA[1] - (2 * cfg.MARGEN))
    altura_minima = altura_minima_visible_caja(estilo_base, decorador)
    try:
        _, alto_caja = caja.wrap(ancho_total, alto_util_pagina)
    except Exception:
        return [caja]
    umbral_salto = min(alto_caja, altura_minima)
    if umbral_salto > 0:
        return [CondPageBreak(umbral_salto), caja]
    return [caja]

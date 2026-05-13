from pathlib import Path

from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A3, A4, A5, A6, B5, ELEVENSEVENTEEN, LEGAL, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase.ttfonts import TTFont

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
MARGEN_MINIMO_CM = 0.5
MARGEN_MINIMO_ADORNOS_CM = 1.5
MARGEN_MAXIMO_CM = 3.5
ADORNOS_MARGEN_ACTIVOS = False
ESTILO_ADORNO_MARGEN = "CLASICO"
IMAGEN_ADORNO_MARGEN = ""
PACK_DECORACION_CAJAS = "NINGUNO"
PORTADA_PAGINA_COMPLETA = False
PORTADA_MODO_AJUSTE = "CUBRIR"
MINIMO_RENGLONES_CAJA_ANTES_DE_MOVER = 3
IMAGEN_PORTADA_PREDETERMINADA = r"C:\ruta\a\tu\imagen_portada.jpg"

MODOS_AJUSTE_PORTADA_DISPONIBLES = {
    "Cubrir hoja completa": "CUBRIR",
    "Encajar completa sin recorte": "ENCAJAR",
}


def normalizar_modo_ajuste_portada(valor):
    texto = str(valor or "").strip().upper()
    if texto == "ENCAJAR":
        return "ENCAJAR"
    return "CUBRIR"


def obtener_etiqueta_modo_ajuste_portada(valor):
    codigo = normalizar_modo_ajuste_portada(valor)
    for etiqueta, valor_codigo in MODOS_AJUSTE_PORTADA_DISPONIBLES.items():
        if valor_codigo == codigo:
            return etiqueta
    return "Cubrir hoja completa"

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

ESTILOS_ADORNO_MARGEN_DISPONIBLES = {
    "Clásico": "CLASICO",
    "Floral": "FLORAL",
    "Geométrico": "GEOMETRICO",
    "Personalizado (PNG)": "PERSONALIZADO",
}

PACKS_DECORACION_CAJAS_DISPONIBLES = {
    "Sin pack adicional": "NINGUNO",
    "Pergamino Noble": "PERGAMINO_NOBLE",
    "Grimorio Arcano": "GRIMORIO_ARCANO",
    "Heráldica de Campaña": "HERALDICA_CAMPANA",
}


def normalizar_pack_decoracion_cajas(valor):
    texto = str(valor or "").strip().upper()
    if texto in {"PERGAMINO_NOBLE", "GRIMORIO_ARCANO", "HERALDICA_CAMPANA"}:
        return texto
    return "NINGUNO"


def obtener_etiqueta_pack_decoracion_cajas(valor):
    codigo = normalizar_pack_decoracion_cajas(valor)
    for etiqueta, valor_codigo in PACKS_DECORACION_CAJAS_DISPONIBLES.items():
        if valor_codigo == codigo:
            return etiqueta
    return "Sin pack adicional"

DIRECTORIO_FUENTES = Path(__file__).resolve().parent / "fonts"

FUENTES_BASE_DISPONIBLES = [
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

SUFIJOS_VARIANTE_FUENTE = [
    ("bolditalic", (True, True)),
    ("boldoblique", (True, True)),
    ("bold-italic", (True, True)),
    ("bold_oblique", (True, True)),
    ("bold italic", (True, True)),
    ("bold oblique", (True, True)),
    ("italic", (False, True)),
    ("oblique", (False, True)),
    ("bold", (True, False)),
    ("regular", (False, False)),
]

EXTENSIONES_FUENTE_ADMITIDAS = {".ttf", ".otf"}

FUENTES_PERSONALIZADAS = {}


def _normalizar_nombre_fuente(texto):
    return " ".join(str(texto).replace("_", " ").replace("-", " ").split()).strip()


def _inferir_familia_y_estilo_fuente(nombre_archivo):
    base = _normalizar_nombre_fuente(nombre_archivo)
    base_minusculas = base.casefold()
    for sufijo, estilo in SUFIJOS_VARIANTE_FUENTE:
        sufijo_normalizado = _normalizar_nombre_fuente(sufijo)
        if not base_minusculas.endswith(sufijo_normalizado.casefold()):
            continue
        familia = base[: len(base) - len(sufijo_normalizado)].strip(" -_")
        familia = _normalizar_nombre_fuente(familia)
        if familia:
            return familia, estilo
    return base, (False, False)


def _nombre_registrado_fuente(familia, es_negrita, es_cursiva):
    if es_negrita and es_cursiva:
        return f"{familia}-BoldItalic"
    if es_negrita:
        return f"{familia}-Bold"
    if es_cursiva:
        return f"{familia}-Italic"
    return familia


def _recopilar_archivos_fuente_personalizados():
    if not DIRECTORIO_FUENTES.exists():
        return {}
    fuentes_encontradas = {}
    for ruta_fuente in sorted(DIRECTORIO_FUENTES.rglob("*")):
        if not ruta_fuente.is_file() or ruta_fuente.suffix.lower() not in EXTENSIONES_FUENTE_ADMITIDAS:
            continue
        familia, estilo = _inferir_familia_y_estilo_fuente(ruta_fuente.stem)
        if not familia:
            continue
        variantes = fuentes_encontradas.setdefault(familia, {})
        variantes.setdefault(estilo, ruta_fuente)
    return fuentes_encontradas


def _registrar_fuente_tt(nombre_registrado, ruta_fuente):
    if nombre_registrado in pdfmetrics.getRegisteredFontNames():
        return True
    try:
        pdfmetrics.registerFont(TTFont(nombre_registrado, str(ruta_fuente)))
        return True
    except Exception:
        return False


def registrar_fuente_personalizada(nombre_fuente):
    variantes = FUENTES_PERSONALIZADAS.get(nombre_fuente)
    if not variantes:
        return False

    registros = {}
    for estilo, ruta_fuente in variantes.items():
        nombre_registrado = _nombre_registrado_fuente(nombre_fuente, *estilo)
        if _registrar_fuente_tt(nombre_registrado, ruta_fuente):
            registros[estilo] = nombre_registrado

    if not registros:
        return False

    nombre_regular = registros.get((False, False))
    if nombre_regular is None:
        estilo_predeterminado = next(iter(registros))
        nombre_regular = nombre_fuente
        _registrar_fuente_tt(nombre_regular, variantes[estilo_predeterminado])
        registros[(False, False)] = nombre_regular

    addMapping(nombre_fuente, 0, 0, registros.get((False, False), nombre_regular))
    addMapping(nombre_fuente, 1, 0, registros.get((True, False), nombre_regular))
    addMapping(nombre_fuente, 0, 1, registros.get((False, True), nombre_regular))
    addMapping(nombre_fuente, 1, 1, registros.get((True, True), registros.get((True, False), registros.get((False, True), nombre_regular))) )
    return True


def recargar_fuentes_disponibles():
    global FUENTES_PERSONALIZADAS, FUENTES_DISPONIBLES
    FUENTES_PERSONALIZADAS = _recopilar_archivos_fuente_personalizados()
    for nombre_fuente in FUENTES_PERSONALIZADAS:
        registrar_fuente_personalizada(nombre_fuente)
    FUENTES_DISPONIBLES = [*FUENTES_BASE_DISPONIBLES, *sorted(FUENTES_PERSONALIZADAS.keys(), key=str.casefold)]
    return list(FUENTES_DISPONIBLES)


def obtener_fuentes_disponibles():
    return recargar_fuentes_disponibles()


def fuente_disponible(nombre_fuente):
    if nombre_fuente in FUENTES_BASE_DISPONIBLES:
        return True
    recargar_fuentes_disponibles()
    if nombre_fuente in FUENTES_PERSONALIZADAS:
        return registrar_fuente_personalizada(nombre_fuente)
    return False


FUENTES_DISPONIBLES = recargar_fuentes_disponibles()


def normalizar_estilo_adorno_margen(valor):
    texto = str(valor or "").strip()
    if not texto:
        return ESTILO_ADORNO_MARGEN
    texto_mayusculas = texto.upper()
    if texto_mayusculas in ESTILOS_ADORNO_MARGEN_DISPONIBLES.values():
        return texto_mayusculas
    texto_normalizado = " ".join(texto.split()).casefold()
    for etiqueta, codigo in ESTILOS_ADORNO_MARGEN_DISPONIBLES.items():
        if texto_normalizado == etiqueta.casefold():
            return codigo
    return ESTILO_ADORNO_MARGEN


def obtener_etiqueta_estilo_adorno_margen(codigo):
    codigo_normalizado = normalizar_estilo_adorno_margen(codigo)
    for etiqueta, valor in ESTILOS_ADORNO_MARGEN_DISPONIBLES.items():
        if valor == codigo_normalizado:
            return etiqueta
    return next(iter(ESTILOS_ADORNO_MARGEN_DISPONIBLES))


def obtener_margen_minimo_cm(adornos_activos=False):
    return MARGEN_MINIMO_ADORNOS_CM if adornos_activos else MARGEN_MINIMO_CM


def normalizar_margen_cm(valor, adornos_activos=False, valor_predeterminado=2.0):
    try:
        margen_cm = float(valor)
    except (TypeError, ValueError):
        margen_cm = valor_predeterminado
    margen_minimo = obtener_margen_minimo_cm(adornos_activos)
    return min(max(margen_cm, margen_minimo), MARGEN_MAXIMO_CM)


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
        "adornos_margen_activos": ADORNOS_MARGEN_ACTIVOS,
        "estilo_adorno_margen": ESTILO_ADORNO_MARGEN,
        "imagen_adorno_margen": IMAGEN_ADORNO_MARGEN,
        "pack_decoracion_cajas": PACK_DECORACION_CAJAS,
        "portada_pagina_completa": PORTADA_PAGINA_COMPLETA,
        "portada_modo_ajuste": PORTADA_MODO_AJUSTE,
    }


def aplicar_configuracion_documento(configuracion_documento):
    global FUENTE_TITULO, FUENTE_TEXTO, TAMANO_PAGINA, MARGEN
    global ADORNOS_MARGEN_ACTIVOS, ESTILO_ADORNO_MARGEN, IMAGEN_ADORNO_MARGEN, PACK_DECORACION_CAJAS, PORTADA_PAGINA_COMPLETA, PORTADA_MODO_AJUSTE

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
    FUENTE_TITULO = fuente_titulo if fuente_disponible(fuente_titulo) else "Helvetica-Bold"
    FUENTE_TEXTO = fuente_texto if fuente_disponible(fuente_texto) else "Helvetica"

    ADORNOS_MARGEN_ACTIVOS = bool(valores.get("adornos_margen_activos", ADORNOS_MARGEN_ACTIVOS))
    ESTILO_ADORNO_MARGEN = normalizar_estilo_adorno_margen(valores.get("estilo_adorno_margen", ESTILO_ADORNO_MARGEN))
    IMAGEN_ADORNO_MARGEN = str(valores.get("imagen_adorno_margen", IMAGEN_ADORNO_MARGEN) or "").strip()
    PACK_DECORACION_CAJAS = normalizar_pack_decoracion_cajas(valores.get("pack_decoracion_cajas", PACK_DECORACION_CAJAS))
    PORTADA_PAGINA_COMPLETA = bool(valores.get("portada_pagina_completa", PORTADA_PAGINA_COMPLETA))
    PORTADA_MODO_AJUSTE = normalizar_modo_ajuste_portada(valores.get("portada_modo_ajuste", PORTADA_MODO_AJUSTE))

    margen_cm = normalizar_margen_cm(valores.get("margen_cm", MARGEN / cm), adornos_activos=ADORNOS_MARGEN_ACTIVOS)
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

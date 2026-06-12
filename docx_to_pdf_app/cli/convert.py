import argparse
import os
from pathlib import Path

from reportlab.lib.pagesizes import A3, A4, A5, A6, B5, ELEVENSEVENTEEN, LEGAL, LETTER
from reportlab.lib.units import cm

from ..core import configuracion_pdf as cfg
from ..pdf.constructor_pdf import DocumentoConIndice, construir_pdf as _construir_pdf
from ..ui.interfaz_usuario import (
    abrir_pdf_con_aplicacion_predeterminada,
    abrir_y_notificar_pdf_generado,
    pedir_configuracion_interactiva,
    seleccionar_archivo_dialogo,
    mostrar_aviso_generacion,
)
from ..core.procesamiento_word import (
    _dividir_html_en_salto,
    _extraer_bloque_prefijo_embebido,
    _quitar_prefijo_visible_en_html,
    agregar_imagenes_a_bloque,
    celda_docx_a_html,
    crear_items_imagenes,
    decorar_consejo_dm_html,
    decorar_info_adicional_html,
    es_consejo_dm,
    es_fin_bloque_manual,
    es_info_adicional,
    es_inicio_bloque_aliado,
    es_inicio_bloque_consejo,
    es_inicio_bloque_cita,
    es_inicio_bloque_enemigo,
    es_inicio_bloque_info,
    es_inicio_bloque_npc,
    es_inicio_bloque_objeto,
    es_inicio_bloque_tesoro,
    es_lista_parrafo,
    estilo_para_parrafo,
    extraer_imagenes_de_parrafo,
    item_caja_desde_parrafo,
    item_caja_grupo_imagenes,
    item_caja_imagen,
    item_caja_plano,
    item_caja_tabla,
    iterar_elementos_documento,
    nivel_lista_parrafo,
    parrafo_a_html,
)
from ..pdf.renderizado_cajas import (
    BloqueVisualConCabecera,
    CajaPartible,
    crear_fila_de_imagenes,
    crear_flujo_imagen,
    crear_flujo_imagen_desde_descriptor,
    crear_flujos_imagenes,
    decorar_aliado_en_html,
    decorar_enemigo_en_html,
    decorar_npc_en_html,
    decorar_objeto_en_html,
    decorar_premio_en_html,
    decorar_tesoro_en_html,
    renderizar_caja,
    tabla_docx_a_flujo,
)

NOMBRES_CONFIG_MUTABLES = [
    "COLOR_PRIMARIO",
    "COLOR_SECUNDARIO",
    "COLOR_TEXTO_GENERAL",
    "COLOR_FONDO_PAGINA",
    "COLOR_CONSEJO_TEXTO",
    "COLOR_CONSEJO_BORDE",
    "COLOR_CONSEJO_FONDO",
    "COLOR_CITA_TEXTO",
    "COLOR_CITA_BORDE",
    "COLOR_CITA_FONDO",
    "COLOR_INFO_TEXTO",
    "COLOR_INFO_BORDE",
    "COLOR_INFO_FONDO",
    "COLOR_ENEMIGO_TEXTO",
    "COLOR_ENEMIGO_BORDE",
    "COLOR_ENEMIGO_FONDO",
    "COLOR_NPC_TEXTO",
    "COLOR_NPC_BORDE",
    "COLOR_NPC_FONDO",
    "COLOR_ALIADO_TEXTO",
    "COLOR_ALIADO_BORDE",
    "COLOR_ALIADO_FONDO",
    "COLOR_TESORO_TEXTO",
    "COLOR_TESORO_BORDE",
    "COLOR_TESORO_FONDO",
    "COLOR_PUZZLE_TEXTO",
    "COLOR_PUZZLE_BORDE",
    "COLOR_PUZZLE_FONDO",
    "COLOR_OBJETO_TEXTO",
    "COLOR_OBJETO_BORDE",
    "COLOR_OBJETO_FONDO",
    "FUENTE_TITULO",
    "FUENTE_TEXTO",
    "TAMANO_PAGINA",
    "MARGEN",
    "ANCHO_BORDE_CAJAS",
    "ESPACIO_ANTES_CAJAS",
    "ESPACIO_DESPUES_CAJAS",
    "ADORNOS_MARGEN_ACTIVOS",
    "ESTILO_ADORNO_MARGEN",
    "IMAGEN_ADORNO_MARGEN",
    "PACK_DECORACION_CAJAS",
    "PORTADA_PAGINA_COMPLETA",
    "PORTADA_MODO_AJUSTE",
    "MINIMO_RENGLONES_CAJA_ANTES_DE_MOVER",
    "IMAGEN_PORTADA_PREDETERMINADA",
]

for _nombre_config in NOMBRES_CONFIG_MUTABLES:
    globals()[_nombre_config] = getattr(cfg, _nombre_config)

IMAGEN_PORTADA_PREDETERMINADA = cfg.IMAGEN_PORTADA_PREDETERMINADA


def _sincronizar_estado_global_desde_configuracion():
    for nombre in NOMBRES_CONFIG_MUTABLES:
        globals()[nombre] = getattr(cfg, nombre)


def _sincronizar_estado_global_hacia_configuracion():
    for nombre in NOMBRES_CONFIG_MUTABLES:
        setattr(cfg, nombre, globals()[nombre])



def obtener_configuracion_visual_predeterminada():
    _sincronizar_estado_global_hacia_configuracion()
    return cfg.obtener_configuracion_visual_predeterminada()



def obtener_configuracion_documento_predeterminada():
    _sincronizar_estado_global_hacia_configuracion()
    return cfg.obtener_configuracion_documento_predeterminada()



def aplicar_configuracion_visual(configuracion_visual):
    _sincronizar_estado_global_hacia_configuracion()
    cfg.aplicar_configuracion_visual(configuracion_visual)
    _sincronizar_estado_global_desde_configuracion()



def aplicar_configuracion_documento(configuracion_documento):
    _sincronizar_estado_global_hacia_configuracion()
    cfg.aplicar_configuracion_documento(configuracion_documento)
    _sincronizar_estado_global_desde_configuracion()



def construir_estilos():
    _sincronizar_estado_global_hacia_configuracion()
    return cfg.construir_estilos()



def construir_pdf(ruta_docx, ruta_pdf, titulo=None, autor=None, subtitulo=None, imagen_portada=None):
    _sincronizar_estado_global_hacia_configuracion()
    return _construir_pdf(ruta_docx, ruta_pdf, titulo=titulo, autor=autor, subtitulo=subtitulo, imagen_portada=imagen_portada)



_seleccionar_archivo_dialogo = seleccionar_archivo_dialogo
_mostrar_aviso_generacion = mostrar_aviso_generacion
_abrir_pdf_con_aplicacion_predeterminada = abrir_pdf_con_aplicacion_predeterminada
_abrir_y_notificar_pdf_generado = abrir_y_notificar_pdf_generado



def _pedir_configuracion_interactiva(*args, **kwargs):
    _sincronizar_estado_global_hacia_configuracion()
    return pedir_configuracion_interactiva(*args, **kwargs)


def _ruta_texto(ruta):
    return str(ruta) if ruta else ""


def _resolver_imagen_portada_predeterminada(ruta_portada):
    ruta = _ruta_texto(ruta_portada).strip()
    if ruta == IMAGEN_PORTADA_PREDETERMINADA and not os.path.exists(ruta):
        return ""
    return ruta


def _resolver_ruta_entrada(entrada):
    if entrada is not None:
        return entrada
    print("📂 Selecciona el archivo Word de entrada...")
    ruta = _seleccionar_archivo_dialogo(
        "Selecciona el archivo Word de entrada",
        [("Documentos Word", "*.docx"), ("Todos los archivos", "*.*")],
        modo="abrir",
    )
    if not ruta:
        raise SystemExit("❌ No se seleccionó ningún archivo de entrada.")
    return Path(ruta)


def _resolver_ruta_salida(salida, entrada):
    if salida is not None:
        return salida
    print("💾 Selecciona dónde guardar el PDF...")
    ruta = _seleccionar_archivo_dialogo(
        "Guardar PDF como...",
        [("Archivo PDF", "*.pdf"), ("Todos los archivos", "*.*")],
        modo="guardar",
        archivo_inicial=entrada.with_suffix(".pdf").name,
    )
    if not ruta:
        raise SystemExit("❌ No se seleccionó ruta de salida.")
    return Path(ruta)


def _resolver_salida_inicial(entrada, salida):
    if salida is not None:
        return _ruta_texto(salida)
    if entrada is not None:
        return _ruta_texto(entrada.with_suffix(".pdf"))
    return ""


def _generar_pdf_desde_configuracion_interactiva(configuracion):
    entrada = Path(configuracion["entrada"])
    salida = Path(configuracion["salida"])
    aplicar_configuracion_visual(configuracion["configuracion_visual"])
    aplicar_configuracion_documento(configuracion["configuracion_documento"])
    construir_pdf(
        entrada,
        salida,
        titulo=configuracion["titulo"] or None,
        autor=configuracion["autor"] or None,
        subtitulo=configuracion["subtitulo"] or None,
        imagen_portada=configuracion["imagen_portada"],
    )
    _abrir_y_notificar_pdf_generado(salida)


def _ejecutar_modo_interactivo(entrada, salida, titulo, subtitulo, autor, imagen_portada, configuracion_visual, configuracion_documento):
    _pedir_configuracion_interactiva(
        configuracion_visual,
        configuracion_documento,
        titulo_inicial=titulo,
        subtitulo_inicial=subtitulo,
        autor_inicial=autor,
        portada_inicial=_resolver_imagen_portada_predeterminada(imagen_portada),
        entrada_inicial=_ruta_texto(entrada),
        salida_inicial=_resolver_salida_inicial(entrada, salida),
        accion_aceptar=_generar_pdf_desde_configuracion_interactiva,
    )


def _ejecutar_modo_directo(entrada, salida, titulo, subtitulo, autor, imagen_portada, configuracion_visual, configuracion_documento):
    entrada = _resolver_ruta_entrada(entrada)
    salida = _resolver_ruta_salida(salida, entrada)
    if not entrada.exists():
        raise SystemExit(f"No se encontró el archivo: {entrada}")

    aplicar_configuracion_visual(configuracion_visual)
    aplicar_configuracion_documento(configuracion_documento)
    construir_pdf(
        entrada,
        salida,
        titulo=titulo or None,
        autor=autor or None,
        subtitulo=subtitulo or None,
        imagen_portada=imagen_portada,
    )
    _abrir_y_notificar_pdf_generado(salida)


_renderizar_caja = renderizar_caja
_tabla_docx_a_flujo = tabla_docx_a_flujo
_crear_flujo_imagen_desde_descriptor = crear_flujo_imagen_desde_descriptor
_crear_flujos_imagenes = crear_flujos_imagenes
_crear_fila_de_imagenes = crear_fila_de_imagenes



def principal():
    parser = argparse.ArgumentParser(description="Convierte un .docx a PDF estilo Aventura.")
    parser.add_argument("entrada", nargs="?", help="Archivo .docx de entrada")
    parser.add_argument("salida", nargs="?", help="Archivo .pdf de salida")
    parser.add_argument("--titulo", help="Título de la portada (opcional)")
    parser.add_argument("--subtitulo", help="Subtítulo de la portada (opcional)")
    parser.add_argument("--autor", help="Autor (opcional)")
    parser.add_argument("--portada", default=IMAGEN_PORTADA_PREDETERMINADA, help=f"Ruta a la imagen de portada (por defecto: {IMAGEN_PORTADA_PREDETERMINADA})")
    parser.add_argument("--menu-interactivo", action="store_true", help="Fuerza la apertura del menú interactivo de colores y metadatos.")
    parser.add_argument("--sin-menu", action="store_true", help="Omite el menú interactivo incluso si se usan diálogos de archivo.")
    args = parser.parse_args()

    entrada = Path(args.entrada) if args.entrada else None
    salida = Path(args.salida) if args.salida else None

    configuracion_visual = obtener_configuracion_visual_predeterminada()
    configuracion_documento = obtener_configuracion_documento_predeterminada()
    titulo = (args.titulo or "").strip()
    subtitulo = (args.subtitulo or "").strip()
    autor = (args.autor or "").strip()
    imagen_portada = _resolver_imagen_portada_predeterminada(args.portada)

    usar_menu_interactivo = not args.sin_menu and (args.menu_interactivo or not (entrada and salida))
    if usar_menu_interactivo:
        _ejecutar_modo_interactivo(
            entrada,
            salida,
            titulo,
            subtitulo,
            autor,
            imagen_portada,
            configuracion_visual,
            configuracion_documento,
        )
        return

    _ejecutar_modo_directo(
        entrada,
        salida,
        titulo,
        subtitulo,
        autor,
        imagen_portada,
        configuracion_visual,
        configuracion_documento,
    )



_sincronizar_estado_global_desde_configuracion()


if __name__ == "__main__":
    principal()

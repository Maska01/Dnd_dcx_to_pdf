from dataclasses import dataclass, field


@dataclass
class EstadoRutasUI:
    entrada_var: object = None
    salida_var: object = None
    estado_rutas_var: object = None
    entrada_archivo: object = None
    salida_archivo: object = None
    estado_rutas_label: object = None


@dataclass
class EstadoPortadaUI:
    titulo_var: object = None
    subtitulo_var: object = None
    autor_var: object = None
    portada_habilitada_var: object = None
    portada_var: object = None
    portada_pagina_completa_var: object = None
    portada_modo_ajuste_var: object = None
    entrada_portada: object = None
    boton_portada: object = None
    check_portada_pagina_completa: object = None
    combo_portada_modo_ajuste: object = None
    etiqueta_ayuda_portada: object = None
    etiqueta_validacion_portada: object = None
    resumen_portada_var: object = None


@dataclass
class EstadoDocumentoUI:
    tamano_pagina_var: object = None
    fuente_titulo_var: object = None
    fuente_texto_var: object = None
    margen_var: object = None
    ancho_borde_cajas_var: object = None
    espacio_antes_cajas_var: object = None
    espacio_despues_cajas_var: object = None
    ancho_pagina_var: object = None
    alto_pagina_var: object = None
    adornos_habilitados_var: object = None
    decoracion_cajas_habilitada_var: object = None
    estilo_adorno_var: object = None
    imagen_adorno_var: object = None
    pack_decoracion_cajas_var: object = None
    entrada_ancho: object = None
    entrada_alto: object = None
    etiqueta_ayuda_tamano: object = None
    etiqueta_validacion_tamano: object = None
    etiqueta_validacion_margen: object = None
    resumen_documento_var: object = None
    combo_margen: object = None
    etiqueta_rango_margen: object = None
    combo_estilo_adorno: object = None
    combo_pack_decoracion_cajas: object = None
    entrada_imagen_adorno: object = None
    boton_imagen_adorno: object = None
    canvas_preview_adorno: object = None
    canvas_preview_cajas: object = None
    etiqueta_estado_margenes: object = None
    etiqueta_estado_cajas: object = None
    etiqueta_validacion_adorno: object = None


@dataclass
class EstadoOperacionUI:
    estado_operacion_var: object = None
    etiqueta_estado_operacion: object = None


@dataclass
class EstadoDialogoUI:
    rutas: EstadoRutasUI = field(default_factory=EstadoRutasUI)
    portada: EstadoPortadaUI = field(default_factory=EstadoPortadaUI)
    documento: EstadoDocumentoUI = field(default_factory=EstadoDocumentoUI)
    operacion: EstadoOperacionUI = field(default_factory=EstadoOperacionUI)
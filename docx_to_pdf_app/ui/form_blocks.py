from ..core import configuracion_pdf as cfg


def construir_bloque_archivos(dialog, interior):
    archivos_frame = dialog.tk.LabelFrame(interior, text="Archivos", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    archivos_frame.pack(fill="x")
    dialog._asignar_estado_ui("rutas", "entrada_var", dialog.tk.StringVar(value=dialog.entrada_inicial))
    salida_inicial = dialog._salida_inicial_normalizada()
    dialog._asignar_estado_ui("rutas", "salida_var", dialog.tk.StringVar(value=salida_inicial))
    dialog._asignar_estado_ui("rutas", "estado_rutas_var", dialog.tk.StringVar(value="Selecciona un archivo de entrada y una ruta PDF de salida para continuar."))
    dialog.ultima_salida_sugerida = salida_inicial if dialog._es_ruta_salida_valida(salida_inicial) else ""

    dialog.tk.Label(
        archivos_frame,
        text="Elige el Word de entrada y dónde guardar el PDF.",
        font=dialog.subtituloLabel_font_cnf,
        justify="left",
        anchor="w",
        wraplength=760,
    ).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))

    dialog.tk.Label(archivos_frame, text="Entrada (.docx/.txt)", font=dialog.normalLabel_font_cnf).grid(row=1, column=0, sticky="w", pady=3)
    dialog._asignar_estado_ui("rutas", "entrada_archivo", dialog.tk.Entry(archivos_frame, textvariable=dialog.entrada_var, width=54))
    dialog.entrada_archivo.grid(row=1, column=1, sticky="ew", padx=(8, 8), pady=3)
    dialog.tk.Button(archivos_frame, text="Elegir archivo...", command=dialog.elegir_archivo_entrada).grid(row=1, column=2, sticky="w", pady=3)

    dialog.tk.Label(archivos_frame, text="Salida (.pdf)", font=dialog.normalLabel_font_cnf).grid(row=2, column=0, sticky="w", pady=3)
    dialog._asignar_estado_ui("rutas", "salida_archivo", dialog.tk.Entry(archivos_frame, textvariable=dialog.salida_var, width=54))
    dialog.salida_archivo.grid(row=2, column=1, sticky="ew", padx=(8, 8), pady=3)
    dialog.tk.Button(archivos_frame, text="Elegir destino...", command=dialog.elegir_archivo_salida).grid(row=2, column=2, sticky="w", pady=3)

    dialog._asignar_estado_ui("rutas", "estado_rutas_label", dialog.tk.Label(archivos_frame, textvariable=dialog.estado_rutas_var, font=dialog.helperLabel_font_cnf, anchor="w", justify="left"))
    dialog.estado_rutas_label.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(8, 0))
    archivos_frame.columnconfigure(0, minsize=160)
    archivos_frame.columnconfigure(1, weight=1)
    dialog.entrada_var.trace_add("write", dialog.actualizar_estado_rutas)
    dialog.salida_var.trace_add("write", dialog.actualizar_estado_rutas)


def construir_bloque_portada(dialog, panel_superior):
    titulo_frame = dialog.tk.LabelFrame(panel_superior, text="Portada y metadatos", font=dialog.tituloLabel_font_cnf, padx=8, pady=10)
    titulo_frame.grid(row=0, column=0, sticky="new")
    dialog._asignar_estado_ui("portada", "titulo_var", dialog.tk.StringVar(value=dialog.titulo_inicial))
    dialog._asignar_estado_ui("portada", "subtitulo_var", dialog.tk.StringVar(value=dialog.subtitulo_inicial))
    dialog._asignar_estado_ui("portada", "autor_var", dialog.tk.StringVar(value=dialog.autor_inicial))
    portada_explicita = bool(dialog.portada_inicial and dialog.portada_inicial != cfg.IMAGEN_PORTADA_PREDETERMINADA)
    dialog._asignar_estado_ui("portada", "portada_habilitada_var", dialog.tk.BooleanVar(value=portada_explicita))
    dialog._asignar_estado_ui("portada", "portada_var", dialog.tk.StringVar(value=dialog.portada_inicial if portada_explicita else ""))
    dialog._asignar_estado_ui("portada", "portada_pagina_completa_var", dialog.tk.BooleanVar(value=bool(dialog.configuracion_documento_inicial.get("portada_pagina_completa", False))))
    dialog._asignar_estado_ui("portada", "portada_modo_ajuste_var", dialog.tk.StringVar(value=cfg.obtener_etiqueta_modo_ajuste_portada(dialog.configuracion_documento_inicial.get("portada_modo_ajuste", "CUBRIR"))))

    dialog.tk.Label(titulo_frame, text="Título (opcional)", font=dialog.normalLabel_font_cnf).grid(row=0, column=0, sticky="w")
    dialog.tk.Entry(titulo_frame, textvariable=dialog.titulo_var, font=dialog.normalLabel_font_cnf, width=36).grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=8)
    dialog.tk.Label(titulo_frame, text="Subtítulo (opcional)", font=dialog.normalLabel_font_cnf).grid(row=1, column=0, sticky="w")
    dialog.tk.Entry(titulo_frame, textvariable=dialog.subtitulo_var, font=dialog.normalLabel_font_cnf, width=36).grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=8)
    dialog.tk.Label(titulo_frame, text="Autor (opcional)", font=dialog.normalLabel_font_cnf).grid(row=2, column=0, sticky="w")
    dialog.tk.Entry(titulo_frame, textvariable=dialog.autor_var, font=dialog.normalLabel_font_cnf, width=36).grid(row=2, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=8)
    dialog.tk.Label(titulo_frame, text="Portada", font=dialog.tituloLabel_font_cnf).grid(row=3, column=0, sticky="w", pady=(10, 4))
    dialog.tk.Checkbutton(titulo_frame, text="Usar portada", variable=dialog.portada_habilitada_var, command=dialog.actualizar_estado_portada, font=dialog.normalLabel_font_cnf).grid(row=4, column=0, sticky="w", pady=(2, 4))

    dialog._asignar_estado_ui("portada", "entrada_portada", dialog.tk.Entry(titulo_frame, textvariable=dialog.portada_var, font=dialog.normalLabel_font_cnf, width=42, state="readonly"))
    dialog.entrada_portada.grid(row=4, column=1, sticky="ew", padx=(8, 8), pady=(2, 4))
    dialog._asignar_estado_ui("portada", "boton_portada", dialog.tk.Button(titulo_frame, text="Elegir imagen...", command=dialog.elegir_portada, font=dialog.normalLabel_font_cnf))
    dialog.boton_portada.grid(row=4, column=2, sticky="w", pady=(2, 4))
    dialog._asignar_estado_ui(
        "portada",
        "check_portada_pagina_completa",
        dialog.tk.Checkbutton(
            titulo_frame,
            text="Ajustar a página completa",
            variable=dialog.portada_pagina_completa_var,
            font=dialog.normalLabel_font_cnf,
            command=dialog.actualizar_estado_portada,
        ),
    )
    dialog.check_portada_pagina_completa.grid(row=5, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=(0, 8))
    dialog.tk.Label(titulo_frame, text="Modo", font=dialog.normalLabel_font_cnf).grid(row=6, column=0, sticky="w", pady=(4, 8))
    dialog._asignar_estado_ui(
        "portada",
        "combo_portada_modo_ajuste",
        dialog.ttk.Combobox(
            titulo_frame,
            textvariable=dialog.portada_modo_ajuste_var,
            font=dialog.normalLabel_font_cnf,
            values=list(cfg.MODOS_AJUSTE_PORTADA_DISPONIBLES.keys()),
            state="readonly",
            width=28,
        ),
    )
    dialog.combo_portada_modo_ajuste.grid(row=6, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=(4, 8))
    dialog._asignar_estado_ui("portada", "etiqueta_ayuda_portada", dialog.tk.Label(titulo_frame, text="", font=dialog.helperLabel_font_cnf, anchor="w", justify="left", wraplength=760, fg="#5F5F5F"))
    dialog.etiqueta_ayuda_portada.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(4, 4))
    dialog._asignar_estado_ui("portada", "etiqueta_validacion_portada", dialog.tk.Label(titulo_frame, text="", font=dialog.helperLabel_font_cnf, anchor="w", justify="left", wraplength=760, fg="#5F5F5F"))
    dialog.etiqueta_validacion_portada.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(4, 4))
    titulo_frame.columnconfigure(1, weight=1)
    dialog.titulo_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_portada())
    dialog.subtitulo_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_portada())
    dialog.autor_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_portada())
    dialog.actualizar_estado_portada()


def construir_panel_resumen_portada(dialog, parent):
    resumen_frame = dialog.tk.LabelFrame(parent, text="Resumen rápido", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    resumen_frame.pack(fill="both", expand=True)
    dialog._asignar_estado_ui("portada", "resumen_portada_var", dialog.tk.StringVar(value=""))
    dialog._agregar_texto_resumen(resumen_frame, dialog.resumen_portada_var, wraplength=260)
    dialog._actualizar_resumen_portada()


def construir_panel_ayuda_portada(dialog, parent):
    ayuda_frame = dialog.tk.LabelFrame(parent, text="Sugerencias", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    ayuda_frame.pack(fill="both", expand=False)
    dialog._agregar_lista_sugerencias(ayuda_frame, ["Usa título y subtítulo solo si deben aparecer en la portada.", "Activa página completa si la imagen debe cubrir toda la hoja.", "Si no quieres portada, deja solo los metadatos y continúa."], wraplength=760)


def construir_bloque_documento(dialog, panel_superior):
    documento_frame = dialog.tk.LabelFrame(panel_superior, text="Páginas y fuentes", font=dialog.tituloLabel_font_cnf, padx=8, pady=10)
    documento_frame.grid(row=1, column=0, sticky="nsew")
    fuentes_disponibles = cfg.obtener_fuentes_disponibles()
    dialog._asignar_estado_ui("documento", "tamano_pagina_var", dialog.tk.StringVar(value=dialog.configuracion_documento_inicial.get("tamano_pagina", "A4")))
    dialog._asignar_estado_ui("documento", "fuente_titulo_var", dialog.tk.StringVar(value=dialog.configuracion_documento_inicial.get("fuente_titulo", cfg.FUENTE_TITULO)))
    dialog._asignar_estado_ui("documento", "fuente_texto_var", dialog.tk.StringVar(value=dialog.configuracion_documento_inicial.get("fuente_texto", cfg.FUENTE_TEXTO)))
    dialog._asignar_estado_ui("documento", "ancho_pagina_var", dialog.tk.StringVar(value=str(dialog.configuracion_documento_inicial.get("ancho_pagina_cm", 21.0))))
    dialog._asignar_estado_ui("documento", "alto_pagina_var", dialog.tk.StringVar(value=str(dialog.configuracion_documento_inicial.get("alto_pagina_cm", 29.7))))

    documento_frame.columnconfigure(0, weight=1)
    documento_frame.columnconfigure(1, weight=1)
    dialog.tk.Label(documento_frame, text="Formato", font=dialog.subtituloLabel_font_cnf).grid(row=0, column=0, sticky="w", pady=(10, 5))
    dialog.tk.Label(documento_frame, text="Tamaño", font=dialog.normalLabel_font_cnf).grid(row=1, column=0, sticky="w", padx=(10, 0), pady=5)
    dialog.ttk.Combobox(documento_frame, textvariable=dialog.tamano_pagina_var, font=dialog.normalLabel_font_cnf, values=[*cfg.TAMANOS_PAGINA_DISPONIBLES.keys(), cfg.OPCION_TAMANO_PERSONALIZADO], state="readonly", width=16).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=5)
    dialog.tk.Label(documento_frame, text="Ancho (cm)", font=dialog.normalLabel_font_cnf).grid(row=2, column=0, sticky="w", padx=(10, 0), pady=5)
    dialog._asignar_estado_ui("documento", "entrada_ancho", dialog.tk.Entry(documento_frame, textvariable=dialog.ancho_pagina_var, font=dialog.normalLabel_font_cnf, width=10))
    dialog.entrada_ancho.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=5)
    dialog.tk.Label(documento_frame, text="Alto (cm)", font=dialog.normalLabel_font_cnf).grid(row=3, column=0, sticky="w", padx=(10, 0), pady=5)
    dialog._asignar_estado_ui("documento", "entrada_alto", dialog.tk.Entry(documento_frame, textvariable=dialog.alto_pagina_var, font=dialog.normalLabel_font_cnf, width=10))
    dialog.entrada_alto.grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=5)
    dialog._asignar_estado_ui("documento", "etiqueta_ayuda_tamano", dialog.tk.Label(documento_frame, text="", font=dialog.normalLabel_font_cnf, anchor="w", justify="left", wraplength=760, fg="#5F5F5F"))
    dialog.etiqueta_ayuda_tamano.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(10, 0))
    dialog._asignar_estado_ui("documento", "etiqueta_validacion_tamano", dialog.tk.Label(documento_frame, text="", font=dialog.normalLabel_font_cnf, anchor="w", justify="left", wraplength=760, fg="#5F5F5F"))
    dialog.etiqueta_validacion_tamano.grid(row=5, column=0, columnspan=4, sticky="ew", pady=(10, 0))
    dialog.tk.Label(documento_frame, text="Tipografía", font=dialog.subtituloLabel_font_cnf).grid(row=6, column=0, sticky="w", pady=(20, 5))
    dialog.tk.Label(documento_frame, text="Fuente títulos", font=dialog.normalLabel_font_cnf).grid(row=7, column=0, sticky="w", padx=(10, 0), pady=5)
    dialog.ttk.Combobox(documento_frame, textvariable=dialog.fuente_titulo_var, font=dialog.normalLabel_font_cnf, values=fuentes_disponibles, state="readonly", width=24).grid(row=7, column=1, sticky="ew", padx=(8, 0), pady=5)
    dialog.tk.Label(documento_frame, text="Fuente de texto", font=dialog.normalLabel_font_cnf).grid(row=8, column=0, sticky="w", padx=(10, 0), pady=(5, 20))
    dialog.ttk.Combobox(documento_frame, textvariable=dialog.fuente_texto_var, font=dialog.normalLabel_font_cnf, values=fuentes_disponibles, state="readonly", width=24).grid(row=8, column=1, sticky="ew", padx=(8, 0), pady=(5, 20))

    dialog.tamano_pagina_var.trace_add("write", dialog.actualizar_estado_tamano_personalizado)
    dialog.tamano_pagina_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())
    dialog.fuente_titulo_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())
    dialog.fuente_texto_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())
    dialog.ancho_pagina_var.trace_add("write", lambda *_args: dialog._actualizar_validacion_tamano())
    dialog.ancho_pagina_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())
    dialog.alto_pagina_var.trace_add("write", lambda *_args: dialog._actualizar_validacion_tamano())
    dialog.alto_pagina_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())
    dialog.actualizar_estado_tamano_personalizado()
    dialog._actualizar_resumen_documento()


def construir_panel_resumen_documento(dialog, parent):
    resumen_frame = dialog.tk.LabelFrame(parent, text="Vista rápida", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    resumen_frame.pack(fill="x", expand=False)
    dialog._asignar_estado_ui("documento", "resumen_documento_var", dialog.tk.StringVar(value=""))
    dialog._agregar_texto_resumen(resumen_frame, dialog.resumen_documento_var, wraplength=260)
    ayuda_frame = dialog.tk.LabelFrame(parent, text="Consejos", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    ayuda_frame.pack(fill="both", expand=True, pady=(6, 0))
    dialog._agregar_lista_sugerencias(ayuda_frame, ["Usa tamaño de pagina estándar si no necesitas medidas exactas.", "Elige fuentes legibles para bloques largos de texto."], wraplength=260)
    dialog._actualizar_resumen_documento()


def inicializar_estado_decoracion(dialog):
    adornos_activos = bool(dialog.configuracion_documento_inicial.get("adornos_margen_activos", False))
    estilo_inicial = cfg.normalizar_estilo_adorno_margen(dialog.configuracion_documento_inicial.get("estilo_adorno_margen", cfg.ESTILO_ADORNO_MARGEN))
    imagen_inicial = str(dialog.configuracion_documento_inicial.get("imagen_adorno_margen", "") or "").strip()
    pack_inicial = cfg.normalizar_pack_decoracion_cajas(dialog.configuracion_documento_inicial.get("pack_decoracion_cajas", "NINGUNO"))
    dialog._asignar_estado_ui("documento", "adornos_habilitados_var", dialog.tk.BooleanVar(value=adornos_activos))
    dialog._asignar_estado_ui("documento", "decoracion_cajas_habilitada_var", dialog.tk.BooleanVar(value=pack_inicial != "NINGUNO"))
    dialog._asignar_estado_ui("documento", "estilo_adorno_var", dialog.tk.StringVar(value=cfg.obtener_etiqueta_estilo_adorno_margen(estilo_inicial)))
    dialog._asignar_estado_ui("documento", "imagen_adorno_var", dialog.tk.StringVar(value=imagen_inicial))
    dialog._asignar_estado_ui("documento", "pack_decoracion_cajas_var", dialog.tk.StringVar(value=cfg.obtener_etiqueta_pack_decoracion_cajas(pack_inicial if pack_inicial != "NINGUNO" else "PERGAMINO_NOBLE")))


def construir_bloque_configuracion_cajas(dialog, parent, row=0):
    configuracion_frame = dialog.tk.LabelFrame(parent, text="Ajustes globales", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    configuracion_frame.grid(row=row, column=0, sticky="ew", pady=(0, 6))
    configuracion_frame.columnconfigure(1, weight=1)
    configuracion_frame.columnconfigure(3, weight=1)
    dialog._agregar_descripcion_seccion(configuracion_frame, "Ajusta el borde y el espaciado que usarán todas las cajas.", row=0, columnspan=4, wraplength=dialog.ancho_contenido_compacto)
    dialog._asignar_estado_ui("documento", "ancho_borde_cajas_var", dialog.tk.StringVar(value=str(dialog.configuracion_documento_inicial.get("ancho_borde_cajas", 2.0))))
    dialog._asignar_estado_ui("documento", "espacio_antes_cajas_var", dialog.tk.StringVar(value=str(dialog.configuracion_documento_inicial.get("espacio_antes_cajas", 6.0))))
    dialog._asignar_estado_ui("documento", "espacio_despues_cajas_var", dialog.tk.StringVar(value=str(dialog.configuracion_documento_inicial.get("espacio_despues_cajas", 8.0))))
    dialog.tk.Label(configuracion_frame, text="Borde (pt)", font=dialog.normalLabel_font_cnf).grid(row=1, column=0, sticky="w", padx=(16, 0), pady=3)
    dialog.tk.Entry(configuracion_frame, textvariable=dialog.ancho_borde_cajas_var, width=10).grid(row=1, column=1, sticky="w", padx=(8, 10), pady=3)
    dialog.tk.Label(configuracion_frame, text="Espacio antes (pt)", font=dialog.normalLabel_font_cnf).grid(row=2, column=0, sticky="w", padx=(16, 0), pady=3)
    dialog.tk.Entry(configuracion_frame, textvariable=dialog.espacio_antes_cajas_var, width=10).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=3)
    dialog.tk.Label(configuracion_frame, text="Espacio después (pt)", font=dialog.normalLabel_font_cnf).grid(row=3, column=0, sticky="w", padx=(16, 0), pady=3)
    dialog.tk.Entry(configuracion_frame, textvariable=dialog.espacio_despues_cajas_var, width=10).grid(row=3, column=1, sticky="w", padx=(8, 0), pady=3)
    dialog.ancho_borde_cajas_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())
    dialog.espacio_antes_cajas_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())
    dialog.espacio_despues_cajas_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())


def construir_bloque_adornos_cajas(dialog, parent, row=0):
    cajas_frame = dialog.tk.LabelFrame(parent, text="Configuración de Cajas", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    cajas_frame.grid(row=row, column=0, sticky="new")
    cajas_frame.columnconfigure(1, weight=1)
    dialog._agregar_descripcion_seccion(cajas_frame, "Elige el estilo global de las cajas temáticas.", row=0, columnspan=1, wraplength=dialog.ancho_contenido_compacto)
    dialog.tk.Checkbutton(cajas_frame, text="Activar decoración", font=dialog.normalLabel_font_cnf, variable=dialog.decoracion_cajas_habilitada_var, command=dialog.actualizar_estado_adornos).grid(row=2, column=0, columnspan=1, sticky="w")
    dialog.tk.Label(cajas_frame, text="Estilo", font=dialog.normalLabel_font_cnf).grid(row=3, column=0, sticky="w", pady=(8, 3))
    dialog._asignar_estado_ui("documento", "combo_pack_decoracion_cajas", dialog.ttk.Combobox(cajas_frame, textvariable=dialog.pack_decoracion_cajas_var, values=[etiqueta for etiqueta, codigo in cfg.PACKS_DECORACION_CAJAS_DISPONIBLES.items() if codigo != "NINGUNO"], font=dialog.normalLabel_font_cnf, state="readonly", width=24))
    dialog.combo_pack_decoracion_cajas.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(8, 3))
    dialog.combo_pack_decoracion_cajas.bind("<<ComboboxSelected>>", dialog.actualizar_estado_adornos)
    dialog._asignar_estado_ui("documento", "etiqueta_estado_cajas", dialog.tk.Label(cajas_frame, text="", anchor="w", justify="left", wraplength=460, fg="#5F5F5F", font=dialog.normalLabel_font_cnf))
    dialog.etiqueta_estado_cajas.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 0))
    preview_cajas_frame = dialog.tk.Frame(cajas_frame, padx=6)
    preview_cajas_frame.grid(row=0, column=3, rowspan=4, sticky="ne", padx=(12, 0))
    dialog.tk.Label(preview_cajas_frame, text="Vista previa de cajas", font=dialog.normalLabel_font_cnf, anchor="w").pack(fill="x")
    dialog._asignar_estado_ui("documento", "canvas_preview_cajas", dialog.tk.Canvas(preview_cajas_frame, width=180, height=112, bg="#FFFFFF", highlightthickness=1, highlightbackground="#C8BBA8"))
    dialog.canvas_preview_cajas.pack(pady=(6, 0))


def construir_bloque_configuracion_margenes(dialog, parent):
    margenes_frame = dialog.tk.LabelFrame(parent, text="Configuración de márgenes", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    margenes_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
    margenes_frame.columnconfigure(1, weight=1)
    dialog._agregar_descripcion_seccion(margenes_frame, "Ajusta aquí el margen disponible para el contenido del documento.", row=0, columnspan=4, wraplength=dialog.ancho_contenido_compacto)
    dialog.tk.Label(margenes_frame, text="Margen (cm)", font=dialog.normalLabel_font_cnf).grid(row=1, column=0, sticky="w", pady=3)
    dialog._asignar_estado_ui("documento", "margen_var", dialog.tk.StringVar(value=dialog._formatear_margen_cm(dialog._ajustar_margen_a_lista(dialog.configuracion_documento_inicial.get("margen_cm", 2.0), adornos_activos=bool(dialog.configuracion_documento_inicial.get("adornos_margen_activos", False))))))
    dialog._asignar_estado_ui("documento", "combo_margen", dialog.ttk.Combobox(margenes_frame, textvariable=dialog.margen_var, font=dialog.normalLabel_font_cnf, values=dialog._opciones_margen_disponibles(bool(dialog.adornos_habilitados_var and dialog.adornos_habilitados_var.get())), state="readonly", width=10))
    dialog.combo_margen.grid(row=1, column=1, sticky="w", pady=3)
    dialog._asignar_estado_ui("documento", "etiqueta_rango_margen", dialog.tk.Label(margenes_frame, text="", font=dialog.normalLabel_font_cnf, fg=dialog.color_texto_suave))
    dialog.etiqueta_rango_margen.grid(row=2, column=0, columnspan=2, sticky="w", pady=3)
    dialog._asignar_estado_ui("documento", "etiqueta_validacion_margen", dialog.tk.Label(margenes_frame, text="", font=dialog.normalLabel_font_cnf, anchor="w", justify="left", wraplength=760, fg="#5F5F5F"))
    dialog.etiqueta_validacion_margen.grid(row=3, column=0, columnspan=4, sticky="ew")
    dialog.margen_var.trace_add("write", dialog._registrar_margen_seleccionado)
    dialog._actualizar_opciones_margen()
    dialog._actualizar_etiqueta_rango_margen()
    dialog.margen_var.trace_add("write", lambda *_args: dialog._actualizar_resumen_documento())
    dialog.margen_var.trace_add("write", lambda *_args: dialog._actualizar_validacion_margen())


def construir_bloque_adornos_margenes(dialog, parent, row=0):
    margenes_frame = dialog.tk.LabelFrame(parent, text="Decoración de márgenes", font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    margenes_frame.grid(row=row, column=0, sticky="new")
    margenes_frame.columnconfigure(1, weight=1)
    dialog._agregar_descripcion_seccion(margenes_frame, "Estas opciones afectan el borde de cada página.", row=0, columnspan=3, wraplength=260)
    dialog.tk.Checkbutton(margenes_frame, text="Activar decoración", font=dialog.normalLabel_font_cnf, variable=dialog.adornos_habilitados_var, command=dialog.actualizar_estado_adornos).grid(row=2, column=0, columnspan=2, sticky="w")
    dialog.tk.Label(margenes_frame, text="Estilo", font=dialog.normalLabel_font_cnf).grid(row=3, column=0, sticky="w", pady=(8, 3))
    dialog._asignar_estado_ui("documento", "combo_estilo_adorno", dialog.ttk.Combobox(margenes_frame, textvariable=dialog.estilo_adorno_var, font=dialog.normalLabel_font_cnf, values=list(cfg.ESTILOS_ADORNO_MARGEN_DISPONIBLES.keys()), state="readonly", width=24))
    dialog.combo_estilo_adorno.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(8, 3))
    dialog.combo_estilo_adorno.bind("<<ComboboxSelected>>", lambda _evento: dialog.actualizar_estado_adornos())
    dialog.tk.Label(margenes_frame, text="PNG personalizado", font=dialog.normalLabel_font_cnf).grid(row=4, column=0, sticky="w", pady=3)
    dialog._asignar_estado_ui("documento", "entrada_imagen_adorno", dialog.tk.Entry(margenes_frame, textvariable=dialog.imagen_adorno_var, width=42, state="readonly"))
    dialog.entrada_imagen_adorno.grid(row=4, column=1, sticky="ew", padx=(8, 8), pady=3)
    dialog._asignar_estado_ui("documento", "boton_imagen_adorno", dialog.tk.Button(margenes_frame, text="Elegir PNG...", font=dialog.normalLabel_font_cnf, command=dialog.elegir_imagen_adorno))
    dialog.boton_imagen_adorno.grid(row=4, column=2, sticky="w", pady=3)
    dialog._asignar_estado_ui("documento", "etiqueta_estado_margenes", dialog.tk.Label(margenes_frame, text="", anchor="w", justify="left", wraplength=460, fg="#5F5F5F", font=dialog.normalLabel_font_cnf))
    dialog.etiqueta_estado_margenes.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(8, 0))
    dialog._asignar_estado_ui("documento", "etiqueta_validacion_adorno", dialog.tk.Label(margenes_frame, text="", anchor="w", justify="left", wraplength=460, fg="#5F5F5F", font=dialog.normalLabel_font_cnf))
    dialog.etiqueta_validacion_adorno.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(8, 0))
    preview_margenes_frame = dialog.tk.Frame(margenes_frame, padx=6)
    preview_margenes_frame.grid(row=0, column=3, rowspan=7, sticky="ne", padx=(12, 0))
    dialog.tk.Label(preview_margenes_frame, text="Vista previa de márgenes", anchor="w", font=dialog.normalLabel_font_cnf).pack(fill="x")
    dialog._asignar_estado_ui("documento", "canvas_preview_adorno", dialog.tk.Canvas(preview_margenes_frame, width=160, height=220, bg="#FFFFFF", highlightthickness=1, highlightbackground="#C8BBA8"))
    dialog.canvas_preview_adorno.pack(pady=(6, 0))
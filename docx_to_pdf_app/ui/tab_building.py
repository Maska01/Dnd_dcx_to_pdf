def construir_pagina_personalizacion(dialog, interior):
    notebook, pestana_portada_metadatos, pestana_documento, pestana_margenes, pestana_cajas, pestana_colores_cajas, pestana_colores_personajes = crear_notebook(dialog, interior)
    dialog.notebook = notebook
    construir_pestana_portada_metadatos(dialog, pestana_portada_metadatos)
    construir_pestana_documento(dialog, pestana_documento)
    dialog._inicializar_estado_decoracion()
    construir_pestana_margenes(dialog, pestana_margenes)
    construir_pestana_cajas(dialog, pestana_cajas)
    dialog._finalizar_estado_decoracion()
    dialog._construir_pestanas_colores(pestana_colores_cajas, pestana_colores_personajes)


def crear_notebook(dialog, interior):
    notebook = dialog.ttk.Notebook(interior, style="MenuNotebook.TNotebook")
    style = dialog.ttk.Style(dialog.raiz)
    style.configure("MenuNotebook.TNotebook.Tab", font=("Segoe UI", 10, "bold"))

    notebook.pack(fill="both", expand=False)
    pestana_portada_metadatos = dialog.tk.Frame(notebook, padx=8, pady=8)
    pestana_documento = dialog.tk.Frame(notebook, padx=8, pady=8)
    pestana_margenes = dialog.tk.Frame(notebook, padx=8, pady=8)
    pestana_cajas = dialog.tk.Frame(notebook, padx=8, pady=8)
    pestana_colores_cajas = dialog.tk.Frame(notebook, padx=8, pady=8)
    pestana_colores_personajes = dialog.tk.Frame(notebook, padx=8, pady=8)
    notebook.add(pestana_documento, text="Páginas y fuentes")
    notebook.add(pestana_margenes, text="Configuración de márgenes")
    notebook.add(pestana_cajas, text="Configuración de Cajas")
    notebook.add(pestana_colores_cajas, text="Cajas útiles")
    notebook.add(pestana_colores_personajes, text="NPC y combate")
    notebook.add(pestana_portada_metadatos, text="Portada y metadatos")
    return notebook, pestana_portada_metadatos, pestana_documento, pestana_margenes, pestana_cajas, pestana_colores_cajas, pestana_colores_personajes


def construir_pestana_portada_metadatos(dialog, pestana_portada_metadatos):
    dialog._construir_panel_dos_columnas(
        pestana_portada_metadatos,
        dialog._construir_bloque_portada,
        dialog._construir_panel_resumen_portada,
        con_row_inferior=True,
        construir_row_inferior=dialog._construir_panel_ayuda_portada,
    )


def construir_pestana_documento(dialog, pestana_documento):
    dialog._construir_panel_dos_columnas(
        pestana_documento,
        dialog._construir_bloque_documento,
        dialog._construir_panel_resumen_documento,
    )


def construir_pestana_margenes(dialog, pestana_margenes):
    contenedor = dialog.tk.Frame(pestana_margenes)
    contenedor.pack(fill="both", expand=True)
    contenedor.columnconfigure(0, weight=1)
    dialog._construir_bloque_configuracion_margenes(contenedor)
    dialog._construir_bloque_adornos_margenes(contenedor, row=2)


def construir_pestana_cajas(dialog, pestana_cajas):
    contenedor = dialog.tk.Frame(pestana_cajas)
    contenedor.pack(fill="both", expand=True)
    contenedor.columnconfigure(0, weight=1)
    dialog._construir_bloque_configuracion_cajas(contenedor, row=0)
    dialog._construir_bloque_adornos_cajas(contenedor, row=2)


def crear_contenedor_tarjetas_colores(dialog, pestana, numero_columnas=2):
    contenedor_tarjetas = dialog.tk.Frame(pestana)
    contenedor_tarjetas.grid(row=0, column=0, sticky="ew")
    contenedor_tarjetas.columnconfigure(0, weight=1)
    for columna in range(1, numero_columnas + 1):
        contenedor_tarjetas.columnconfigure(columna, weight=0, minsize=260, uniform="tarjetas_colores")
    contenedor_tarjetas.columnconfigure(numero_columnas + 1, weight=1)
    return contenedor_tarjetas


def construir_tarjeta_colores_grupo(dialog, contenedor_tab, nombre_grupo, campos, indice_grupo, numero_columnas=2):
    columna = (indice_grupo % numero_columnas) + 1
    row = indice_grupo // numero_columnas
    padding_x = (0, 8) if columna == 1 else (8, 0) if columna == numero_columnas else (8, 8)
    frame = dialog.tk.LabelFrame(contenedor_tab, text=nombre_grupo, font=dialog.tituloLabel_font_cnf, padx=10, pady=10)
    frame.grid(row=row, column=columna, sticky="new", padx=padding_x, pady=(0, 10))
    frame.columnconfigure(0, minsize=88)
    frame.columnconfigure(1, minsize=84)
    frame.columnconfigure(3, minsize=66)
    for indice, (clave, etiqueta) in enumerate(campos):
        dialog.crear_selector_color(frame, indice, clave, etiqueta)


def construir_pestanas_colores(dialog, pestana_colores_cajas, pestana_colores_personajes, columnas_por_pestana=None):
    grupos_colores = dialog._grupos_colores_disponibles()
    distribucion_pestanas = {
        "Cajas útiles": ["Caja Consejo para el DM", "Caja Cita", "Caja Información adicional", "Caja Tesoro/Premio", "Caja Puzzle/Acertijo/Rompecabezas", "Caja Objeto"],
        "NPC y combate": ["Caja NPC", "Caja Enemigo", "Caja Aliado"],
    }
    columnas_por_pestana = columnas_por_pestana or {}
    contenedores = {"Cajas útiles": pestana_colores_cajas, "NPC y combate": pestana_colores_personajes}
    for nombre_pestana, pestana in contenedores.items():
        numero_columnas = columnas_por_pestana.get(nombre_pestana, 2)
        pestana.columnconfigure(0, weight=1)
        pestana.rowconfigure(0, weight=1)
        pestana.rowconfigure(1, weight=0)
        contenedor_tarjetas = crear_contenedor_tarjetas_colores(dialog, pestana, numero_columnas=numero_columnas)
        for indice_grupo, nombre_grupo in enumerate(distribucion_pestanas[nombre_pestana]):
            _, campos = next(grupo for grupo in grupos_colores if grupo[0] == nombre_grupo)
            construir_tarjeta_colores_grupo(
                dialog,
                contenedor_tarjetas,
                nombre_grupo,
                campos,
                indice_grupo,
                numero_columnas=numero_columnas,
            )
        if nombre_pestana == "Cajas útiles":
            dialog._agregar_descripcion_seccion(
                pestana,
                "Aquí puedes ajustar consejo para el DM, cita, información adicional, tesoro/premio, puzzle/acertijo/rompecabezas y objeto sin mezclarlo con NPC o combate.",
                row=1,
                columnspan=1,
                wraplength=760,
            )
        else:
            dialog._agregar_descripcion_seccion(
                pestana,
                "Los bloques de NPC, enemigo y aliado comparten esta pestaña para ajustes rápidos de escena.",
                row=1,
                columnspan=1,
                wraplength=760,
            )
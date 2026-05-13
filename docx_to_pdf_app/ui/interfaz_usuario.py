import os
from pathlib import Path

from PIL import Image as PILImage, ImageTk
from reportlab.lib.colors import HexColor

from ..core import configuracion_pdf as cfg


def seleccionar_archivo_dialogo(titulo, tipos_archivo, modo="abrir", archivo_inicial=None):
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("⚠️  tkinter no está disponible; no se puede abrir el diálogo.")
        return ""
    raiz = tk.Tk()
    raiz.withdraw()
    raiz.attributes("-topmost", True)
    try:
        if modo == "guardar":
            ruta = filedialog.asksaveasfilename(title=titulo, filetypes=tipos_archivo, defaultextension=tipos_archivo[0][1].replace("*", ""), initialfile=archivo_inicial)
        else:
            ruta = filedialog.askopenfilename(title=titulo, filetypes=tipos_archivo)
    finally:
        raiz.destroy()
    return ruta or ""


def mostrar_aviso_generacion(titulo, mensaje):
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        print(f"ℹ️  {titulo}: {mensaje}")
        return
    raiz = tk.Tk()
    raiz.withdraw()
    raiz.attributes("-topmost", True)
    try:
        messagebox.showinfo(titulo, mensaje, parent=raiz)
    finally:
        raiz.destroy()


def abrir_pdf_con_aplicacion_predeterminada(ruta_pdf):
    ruta_pdf = str(ruta_pdf)
    if hasattr(os, "startfile"):
        os.startfile(ruta_pdf)
        return
    import subprocess
    import sys
    if sys.platform == "darwin":
        subprocess.Popen(["open", ruta_pdf])
    else:
        subprocess.Popen(["xdg-open", ruta_pdf])


def abrir_y_notificar_pdf_generado(ruta_pdf, abridor=None, notificador=None):
    ruta_pdf = Path(ruta_pdf)
    abridor = abridor or abrir_pdf_con_aplicacion_predeterminada
    notificador = notificador or mostrar_aviso_generacion
    abridor(ruta_pdf)
    notificador("PDF generado", f"El PDF se generó correctamente y se abrió con la aplicación predeterminada.\n\nRuta:\n{ruta_pdf}")


class DialogoConfiguracionInteractiva:
    def __init__(self, configuracion_inicial, configuracion_documento_inicial, titulo_inicial="", subtitulo_inicial="", autor_inicial="", portada_inicial="", entrada_inicial="", salida_inicial="", accion_aceptar=None):
        self.configuracion_inicial = dict(configuracion_inicial)
        self.configuracion_documento_inicial = dict(configuracion_documento_inicial)
        self.titulo_inicial = titulo_inicial or ""
        self.subtitulo_inicial = subtitulo_inicial or ""
        self.autor_inicial = autor_inicial or ""
        self.portada_inicial = portada_inicial or ""
        self.entrada_inicial = str(entrada_inicial or "").strip()
        self.salida_inicial = str(salida_inicial or "").strip()
        self.accion_aceptar = accion_aceptar
        self.resultado = {"valor": None}
        self.tk = None
        self.ttk = None
        self.colorchooser = None
        self.filedialog = None
        self.messagebox = None
        self.raiz = None
        self.variables_color = {}
        self.vistas_previas = {}
        self.notebook = None
        self.contenedor_principal = None
        self.interior_principal = None
        self.barra_botones = None
        self.entrada_var = None
        self.salida_var = None
        self.estado_rutas_var = None
        self.titulo_encabezado = None
        self.descripcion_encabezado = None
        self.contenedor_paginas = None
        self.pagina_archivos = None
        self.pagina_personalizacion = None
        self.resumen_entrada_var = None
        self.resumen_salida_var = None
        self.entrada_archivo = None
        self.salida_archivo = None
        self.estado_rutas_label = None
        self.entrada_portada = None
        self.boton_portada = None
        self.etiqueta_ayuda_portada = None
        self.entrada_ancho = None
        self.entrada_alto = None
        self.etiqueta_ayuda_tamano = None
        self.titulo_var = None
        self.subtitulo_var = None
        self.autor_var = None
        self.portada_habilitada_var = None
        self.portada_var = None
        self.portada_pagina_completa_var = None
        self.check_portada_pagina_completa = None
        self.portada_modo_ajuste_var = None
        self.combo_portada_modo_ajuste = None
        self.tamano_pagina_var = None
        self.fuente_titulo_var = None
        self.fuente_texto_var = None
        self.margen_var = None
        self.combo_margen = None
        self.etiqueta_rango_margen = None
        self.ancho_pagina_var = None
        self.alto_pagina_var = None
        self.adornos_habilitados_var = None
        self.decoracion_cajas_habilitada_var = None
        self.estilo_adorno_var = None
        self.imagen_adorno_var = None
        self.pack_decoracion_cajas_var = None
        self.combo_estilo_adorno = None
        self.combo_pack_decoracion_cajas = None
        self.entrada_imagen_adorno = None
        self.boton_imagen_adorno = None
        self.canvas_preview_adorno = None
        self.canvas_preview_cajas = None
        self.preview_adorno_imagen = None
        self.etiqueta_estado_margenes = None
        self.etiqueta_estado_cajas = None
        self.boton_cancelar = None
        self.boton_continuar = None
        self.boton_regresar = None
        self.boton_aceptar = None
        self.boton_restablecer = None
        self.estado_operacion_var = None
        self.etiqueta_estado_operacion = None
        self.ultima_salida_sugerida = ""
        self.pagina_actual = "archivos"
        self.margen_sin_adornos_guardado = None
        self.margen_con_adornos_guardado = None
        self.adornos_activos_previos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        self.ancho_ventana_objetivo = 980
        self.alto_ventana_objetivo = 760
        self.ancho_ventana_minimo = 900
        self.alto_ventana_minimo = 700

    def ejecutar(self):
        if not self._importar_tkinter():
            entrada = self.entrada_inicial
            salida = self._salida_inicial_normalizada()
            if not self._es_ruta_entrada_valida(entrada) or not self._es_ruta_salida_valida(salida):
                print("⚠️  tkinter no está disponible y no hay rutas válidas de entrada/salida para continuar.")
                return None
            print("⚠️  tkinter no está disponible; se omite el menú interactivo.")
            return {
                "entrada": entrada,
                "salida": salida,
                "configuracion_visual": dict(self.configuracion_inicial),
                "configuracion_documento": dict(self.configuracion_documento_inicial),
                "titulo": self.titulo_inicial,
                "subtitulo": self.subtitulo_inicial,
                "autor": self.autor_inicial,
                "imagen_portada": self.portada_inicial,
            }
        self._crear_ventana()
        self._construir_interfaz()
        self._calcular_dimensiones_compartidas_ventana()
        self.raiz.protocol("WM_DELETE_WINDOW", self.cancelar)
        self.raiz.after(10, self.ajustar_tamano_ventana)
        self.raiz.mainloop()
        self.raiz.destroy()
        return self.resultado["valor"]

    def _importar_tkinter(self):
        try:
            import tkinter as tk
            from tkinter import colorchooser, filedialog, messagebox, ttk
        except ImportError:
            return False
        self.tk = tk
        self.colorchooser = colorchooser
        self.filedialog = filedialog
        self.messagebox = messagebox
        self.ttk = ttk
        return True

    def _crear_ventana(self):
        self.raiz = self.tk.Tk()
        self.raiz.title("Configuración del PDF")
        self._configurar_dimensiones_ventana()
        self.raiz.geometry(f"{self.ancho_ventana_objetivo}x{self.alto_ventana_objetivo}")
        self.raiz.minsize(self.ancho_ventana_minimo, self.alto_ventana_minimo)

    def _configurar_dimensiones_ventana(self):
        ancho_pantalla = max(800, int(self.raiz.winfo_screenwidth()))
        alto_pantalla = max(600, int(self.raiz.winfo_screenheight()))
        ancho_objetivo = min(980, max(820, ancho_pantalla - 80))
        alto_objetivo = min(760, max(680, alto_pantalla - 100))
        ancho_minimo = min(ancho_objetivo, max(820, ancho_pantalla - 140))
        alto_minimo = min(alto_objetivo, max(640, alto_pantalla - 160))
        self.ancho_ventana_objetivo = ancho_objetivo
        self.alto_ventana_objetivo = alto_objetivo
        self.ancho_ventana_minimo = ancho_minimo
        self.alto_ventana_minimo = alto_minimo

    def _construir_interfaz(self):
        contenedor = self.tk.Frame(self.raiz, padx=10, pady=10)
        contenedor.pack(fill="both", expand=True)
        self.contenedor_principal = contenedor
        self._configurar_estilo_notebook()
        interior = self.tk.Frame(contenedor)
        interior.pack(fill="both", expand=True)
        self.interior_principal = interior
        self.variables_color = {clave: self.tk.StringVar(value=valor) for clave, valor in self.configuracion_inicial.items()}
        self.encabezado(interior)
        self.contenedor_paginas = self.tk.Frame(interior)
        self.contenedor_paginas.pack(fill="both", expand=True)
        self.pagina_archivos = self.tk.Frame(self.contenedor_paginas)
        self.pagina_personalizacion = self.tk.Frame(self.contenedor_paginas)
        self._construir_bloque_archivos(self.pagina_archivos)
        self._construir_pagina_personalizacion(self.pagina_personalizacion)
        self._construir_botones(contenedor)
        self._mostrar_pagina_archivos()
        self.actualizar_estado_rutas()

    def _configurar_estilo_notebook(self):
        estilo = self.ttk.Style(self.raiz)
        try:
            estilo.theme_use("vista")
        except Exception:
            pass
        estilo.configure("MenuNotebook.TNotebook", tabposition="n")
        estilo.configure("MenuNotebook.TNotebook.Tab", padding=(12, 6))
        estilo.configure("Primario.TButton", padding=(14, 8), font=("Segoe UI", 9, "bold"))
        estilo.configure("Secundario.TButton", padding=(10, 8))

    def encabezado(self, interior):
        encabezado_frame = self.tk.Frame(interior, padx=4, pady=4)
        encabezado_frame.pack(fill="x", pady=(0, 8))
        self.titulo_encabezado = self.tk.Label(encabezado_frame, text="Personaliza tu PDF antes de generarlo", font=("Segoe UI", 16, "bold"), anchor="w")
        self.titulo_encabezado.pack(fill="x")
        self.descripcion_encabezado = self.tk.Label(encabezado_frame, text="Primero elige una entrada `.docx` y una salida `.pdf` válidas. Después podrás continuar a la personalización.", justify="left", wraplength=900, anchor="w")
        self.descripcion_encabezado.pack(fill="x", pady=(4, 0))

    def _construir_bloque_archivos(self, interior):
        archivos_frame = self.tk.LabelFrame(interior, text="Archivos", padx=8, pady=8)
        archivos_frame.pack(fill="x", pady=(0, 8))
        self.entrada_var = self.tk.StringVar(value=self.entrada_inicial)
        salida_inicial = self._salida_inicial_normalizada()
        self.salida_var = self.tk.StringVar(value=salida_inicial)
        self.estado_rutas_var = self.tk.StringVar(value="Selecciona un archivo Word de entrada y una ruta PDF de salida para continuar.")
        self.ultima_salida_sugerida = salida_inicial if self._es_ruta_salida_valida(salida_inicial) else ""

        self.tk.Label(archivos_frame, text="Archivo Word de entrada").grid(row=0, column=0, sticky="w", pady=3)
        self.entrada_archivo = self.tk.Entry(archivos_frame, textvariable=self.entrada_var, width=66)
        self.entrada_archivo.grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=3)
        self.tk.Button(archivos_frame, text="Elegir archivo...", command=self.elegir_archivo_entrada).grid(row=0, column=2, sticky="w", pady=3)

        self.tk.Label(archivos_frame, text="Archivo PDF de salida").grid(row=1, column=0, sticky="w", pady=3)
        self.salida_archivo = self.tk.Entry(archivos_frame, textvariable=self.salida_var, width=66)
        self.salida_archivo.grid(row=1, column=1, sticky="ew", padx=(8, 8), pady=3)
        self.tk.Button(archivos_frame, text="Elegir destino...", command=self.elegir_archivo_salida).grid(row=1, column=2, sticky="w", pady=3)

        self.estado_rutas_label = self.tk.Label(archivos_frame, textvariable=self.estado_rutas_var, anchor="w", justify="left")
        self.estado_rutas_label.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        archivos_frame.columnconfigure(1, weight=1)
        self.entrada_var.trace_add("write", self.actualizar_estado_rutas)
        self.salida_var.trace_add("write", self.actualizar_estado_rutas)

    def _construir_pagina_personalizacion(self, interior):
        resumen_frame = self.tk.LabelFrame(interior, text="Rutas seleccionadas", padx=8, pady=8)
        resumen_frame.pack(fill="x", pady=(0, 8))
        self.resumen_entrada_var = self.tk.StringVar(value=self.entrada_inicial)
        self.resumen_salida_var = self.tk.StringVar(value=self._salida_inicial_normalizada())
        self.tk.Label(resumen_frame, text="Entrada").grid(row=0, column=0, sticky="nw")
        self.tk.Label(resumen_frame, textvariable=self.resumen_entrada_var, anchor="w", justify="left", wraplength=720).grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.tk.Label(resumen_frame, text="Salida").grid(row=1, column=0, sticky="nw", pady=(6, 0))
        self.tk.Label(resumen_frame, textvariable=self.resumen_salida_var, anchor="w", justify="left", wraplength=720).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))
        resumen_frame.columnconfigure(1, weight=1)

        notebook, pestana_general, pestana_decoracion, pestana_colores_base, pestana_colores_cajas, pestana_colores_personajes = self._crear_notebook(interior)
        self.notebook = notebook
        self._construir_pestana_general(pestana_general)
        self._construir_pestana_decoracion(pestana_decoracion)
        self._construir_pestanas_colores(pestana_colores_base, pestana_colores_cajas, pestana_colores_personajes)

    def _crear_notebook(self, interior):
        notebook = self.ttk.Notebook(interior, style="MenuNotebook.TNotebook")
        notebook.pack(fill="both", expand=True)
        pestana_general = self.tk.Frame(notebook, padx=10, pady=10)
        pestana_decoracion = self.tk.Frame(notebook, padx=10, pady=10)
        pestana_colores_base = self.tk.Frame(notebook, padx=10, pady=10)
        pestana_colores_cajas = self.tk.Frame(notebook, padx=10, pady=10)
        pestana_colores_personajes = self.tk.Frame(notebook, padx=10, pady=10)
        notebook.add(pestana_general, text="General")
        notebook.add(pestana_decoracion, text="Decoración")
        notebook.add(pestana_colores_base, text="Colores base")
        notebook.add(pestana_colores_cajas, text="Cajas útiles")
        notebook.add(pestana_colores_personajes, text="NPC y combate")
        return notebook, pestana_general, pestana_decoracion, pestana_colores_base, pestana_colores_cajas, pestana_colores_personajes

    def _construir_pestana_general(self, pestana_general):
        panel_superior = self.tk.Frame(pestana_general)
        panel_superior.pack(fill="both", expand=True)
        panel_superior.columnconfigure(0, weight=1)
        self._construir_bloque_portada(panel_superior)
        self._construir_bloque_documento(panel_superior)

    def _construir_pestana_decoracion(self, pestana_decoracion):
        contenedor = self.tk.Frame(pestana_decoracion)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=1)

        descripcion = self.tk.Label(
            contenedor,
            text="Controla aquí los marcos decorativos del documento con presets o con un PNG transparente personalizado.",
            anchor="w",
            justify="left",
            wraplength=860,
        )
        descripcion.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self._construir_bloque_adornos(contenedor, fila=1)

    def _construir_bloque_portada(self, panel_superior):
        titulo_frame = self.tk.LabelFrame(panel_superior, text="Portada y metadatos", padx=8, pady=8)
        titulo_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.titulo_var = self.tk.StringVar(value=self.titulo_inicial)
        self.subtitulo_var = self.tk.StringVar(value=self.subtitulo_inicial)
        self.autor_var = self.tk.StringVar(value=self.autor_inicial)
        portada_explicita = bool(self.portada_inicial and self.portada_inicial != cfg.IMAGEN_PORTADA_PREDETERMINADA)
        self.portada_habilitada_var = self.tk.BooleanVar(value=portada_explicita)
        self.portada_var = self.tk.StringVar(value=self.portada_inicial if portada_explicita else "")
        self.portada_pagina_completa_var = self.tk.BooleanVar(value=bool(self.configuracion_documento_inicial.get("portada_pagina_completa", False)))
        self.portada_modo_ajuste_var = self.tk.StringVar(value=cfg.obtener_etiqueta_modo_ajuste_portada(self.configuracion_documento_inicial.get("portada_modo_ajuste", "CUBRIR")))
        self.tk.Label(titulo_frame, text="Título de la aventura (opcional)").grid(row=0, column=0, sticky="w")
        self.tk.Entry(titulo_frame, textvariable=self.titulo_var, width=42).grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)
        self.tk.Label(titulo_frame, text="Subtítulo (opcional)").grid(row=1, column=0, sticky="w")
        self.tk.Entry(titulo_frame, textvariable=self.subtitulo_var, width=42).grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)
        self.tk.Label(titulo_frame, text="Autor (opcional)").grid(row=2, column=0, sticky="w")
        self.tk.Entry(titulo_frame, textvariable=self.autor_var, width=42).grid(row=2, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)
        self.tk.Checkbutton(titulo_frame, text="Agregar portada", variable=self.portada_habilitada_var, command=self.actualizar_estado_portada).grid(row=3, column=0, sticky="w", pady=(8, 4))
        self.entrada_portada = self.tk.Entry(titulo_frame, textvariable=self.portada_var, width=42, state="readonly")
        self.entrada_portada.grid(row=3, column=1, sticky="ew", padx=(8, 8), pady=(8, 4))
        self.boton_portada = self.tk.Button(titulo_frame, text="Elegir imagen...", command=self.elegir_portada)
        self.boton_portada.grid(row=3, column=2, sticky="w", pady=(8, 4))
        self.check_portada_pagina_completa = self.tk.Checkbutton(
            titulo_frame,
            text="Ajustar imagen a hoja entera",
            variable=self.portada_pagina_completa_var,
            command=self.actualizar_estado_portada,
        )
        self.check_portada_pagina_completa.grid(row=4, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=(0, 4))
        self.tk.Label(titulo_frame, text="Modo de ajuste").grid(row=5, column=0, sticky="w", pady=(0, 4))
        self.combo_portada_modo_ajuste = self.ttk.Combobox(
            titulo_frame,
            textvariable=self.portada_modo_ajuste_var,
            values=list(cfg.MODOS_AJUSTE_PORTADA_DISPONIBLES.keys()),
            state="readonly",
            width=28,
        )
        self.combo_portada_modo_ajuste.grid(row=5, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=(0, 4))
        self.etiqueta_ayuda_portada = self.tk.Label(titulo_frame, text="", anchor="w", justify="left", wraplength=820, fg="#5F5F5F")
        self.etiqueta_ayuda_portada.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        titulo_frame.columnconfigure(1, weight=1)
        self.actualizar_estado_portada()

    def _construir_bloque_documento(self, panel_superior):
        documento_frame = self.tk.LabelFrame(panel_superior, text="Página, fuentes y márgenes", padx=8, pady=8)
        documento_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        fuentes_disponibles = cfg.obtener_fuentes_disponibles()
        adornos_iniciales = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        self.tamano_pagina_var = self.tk.StringVar(value=self.configuracion_documento_inicial.get("tamano_pagina", "A4"))
        self.fuente_titulo_var = self.tk.StringVar(value=self.configuracion_documento_inicial.get("fuente_titulo", cfg.FUENTE_TITULO))
        self.fuente_texto_var = self.tk.StringVar(value=self.configuracion_documento_inicial.get("fuente_texto", cfg.FUENTE_TEXTO))
        self.margen_var = self.tk.StringVar(value=self._formatear_margen_cm(self._ajustar_margen_a_lista(self.configuracion_documento_inicial.get("margen_cm", 2.0), adornos_activos=adornos_iniciales)))
        self.ancho_pagina_var = self.tk.StringVar(value=str(self.configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)))
        self.alto_pagina_var = self.tk.StringVar(value=str(self.configuracion_documento_inicial.get("alto_pagina_cm", 29.7)))
        self.tk.Label(documento_frame, text="Tamaño de página").grid(row=0, column=0, sticky="w", pady=3)
        self.ttk.Combobox(documento_frame, textvariable=self.tamano_pagina_var, values=[*cfg.TAMANOS_PAGINA_DISPONIBLES.keys(), cfg.OPCION_TAMANO_PERSONALIZADO], state="readonly", width=16).grid(row=0, column=1, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Ancho personalizado (cm)").grid(row=0, column=2, sticky="w", padx=(16, 0), pady=3)
        self.entrada_ancho = self.tk.Entry(documento_frame, textvariable=self.ancho_pagina_var, width=10)
        self.entrada_ancho.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Alto personalizado (cm)").grid(row=1, column=2, sticky="w", padx=(16, 0), pady=3)
        self.entrada_alto = self.tk.Entry(documento_frame, textvariable=self.alto_pagina_var, width=10)
        self.entrada_alto.grid(row=1, column=3, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Fuente de título").grid(row=1, column=0, sticky="w", pady=3)
        self.ttk.Combobox(documento_frame, textvariable=self.fuente_titulo_var, values=fuentes_disponibles, state="readonly", width=24).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Fuente de texto").grid(row=2, column=0, sticky="w", pady=3)
        self.ttk.Combobox(documento_frame, textvariable=self.fuente_texto_var, values=fuentes_disponibles, state="readonly", width=24).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Margen (cm)").grid(row=3, column=0, sticky="w", pady=3)
        self.combo_margen = self.ttk.Combobox(documento_frame, textvariable=self.margen_var, values=self._opciones_margen_disponibles(adornos_iniciales), state="readonly", width=10)
        self.combo_margen.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=3)
        self.etiqueta_rango_margen = self.tk.Label(documento_frame, text="")
        self.etiqueta_rango_margen.grid(row=3, column=2, sticky="w", padx=(8, 0), pady=3)
        self.etiqueta_ayuda_tamano = self.tk.Label(documento_frame, text="", anchor="w", justify="left", wraplength=620, fg="#5F5F5F")
        self.etiqueta_ayuda_tamano.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(6, 0))
        self.margen_var.trace_add("write", self._registrar_margen_seleccionado)
        self.tamano_pagina_var.trace_add("write", self.actualizar_estado_tamano_personalizado)
        self.actualizar_estado_tamano_personalizado()
        self._actualizar_etiqueta_rango_margen()

    def _construir_bloque_adornos(self, parent, fila=0):
        decoracion_frame = self.tk.Frame(parent)
        decoracion_frame.grid(row=fila, column=0, sticky="nsew")
        decoracion_frame.columnconfigure(0, weight=1)

        adornos_activos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        estilo_inicial = cfg.normalizar_estilo_adorno_margen(self.configuracion_documento_inicial.get("estilo_adorno_margen", cfg.ESTILO_ADORNO_MARGEN))
        imagen_inicial = str(self.configuracion_documento_inicial.get("imagen_adorno_margen", "") or "").strip()
        pack_inicial = cfg.normalizar_pack_decoracion_cajas(self.configuracion_documento_inicial.get("pack_decoracion_cajas", "NINGUNO"))

        self.adornos_habilitados_var = self.tk.BooleanVar(value=adornos_activos)
        self.decoracion_cajas_habilitada_var = self.tk.BooleanVar(value=pack_inicial != "NINGUNO")
        self.estilo_adorno_var = self.tk.StringVar(value=cfg.obtener_etiqueta_estilo_adorno_margen(estilo_inicial))
        self.imagen_adorno_var = self.tk.StringVar(value=imagen_inicial)
        self.pack_decoracion_cajas_var = self.tk.StringVar(value=cfg.obtener_etiqueta_pack_decoracion_cajas(pack_inicial if pack_inicial != "NINGUNO" else "PERGAMINO_NOBLE"))

        margenes_frame = self.tk.LabelFrame(decoracion_frame, text="Decoración de márgenes", padx=10, pady=10)
        margenes_frame.grid(row=0, column=0, sticky="ew")
        margenes_frame.columnconfigure(1, weight=1)
        cajas_frame = self.tk.LabelFrame(decoracion_frame, text="Decoración de cajas", padx=10, pady=10)
        cajas_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        cajas_frame.columnconfigure(1, weight=1)

        self.tk.Label(
            margenes_frame,
            text="Estas opciones afectan el borde decorativo de cada página del PDF.",
            anchor="w",
            justify="left",
            wraplength=520,
        ).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        self.tk.Checkbutton(margenes_frame, text="Activar florituras en los márgenes", variable=self.adornos_habilitados_var, command=self.actualizar_estado_adornos).grid(row=1, column=0, columnspan=2, sticky="w")
        self.tk.Label(margenes_frame, text="Estilo").grid(row=2, column=0, sticky="w", pady=(8, 3))
        self.combo_estilo_adorno = self.ttk.Combobox(margenes_frame, textvariable=self.estilo_adorno_var, values=list(cfg.ESTILOS_ADORNO_MARGEN_DISPONIBLES.keys()), state="readonly", width=24)
        self.combo_estilo_adorno.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(8, 3))
        self.combo_estilo_adorno.bind("<<ComboboxSelected>>", lambda _evento: self.actualizar_estado_adornos())

        self.tk.Label(margenes_frame, text="PNG personalizado").grid(row=3, column=0, sticky="w", pady=3)
        self.entrada_imagen_adorno = self.tk.Entry(margenes_frame, textvariable=self.imagen_adorno_var, width=42, state="readonly")
        self.entrada_imagen_adorno.grid(row=3, column=1, sticky="ew", padx=(8, 8), pady=3)
        self.boton_imagen_adorno = self.tk.Button(margenes_frame, text="Elegir PNG...", command=self.elegir_imagen_adorno)
        self.boton_imagen_adorno.grid(row=3, column=2, sticky="w", pady=3)

        self.etiqueta_estado_margenes = self.tk.Label(margenes_frame, text="", anchor="w", justify="left", wraplength=520, fg="#5F5F5F")
        self.etiqueta_estado_margenes.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        preview_margenes_frame = self.tk.Frame(margenes_frame, padx=8)
        preview_margenes_frame.grid(row=0, column=3, rowspan=5, sticky="ne", padx=(16, 0))
        self.tk.Label(preview_margenes_frame, text="Vista previa de márgenes", anchor="w").pack(fill="x")
        self.canvas_preview_adorno = self.tk.Canvas(preview_margenes_frame, width=160, height=220, bg="#FFFFFF", highlightthickness=1, highlightbackground="#C8BBA8")
        self.canvas_preview_adorno.pack(pady=(6, 0))

        self.tk.Label(
            cajas_frame,
            text="Estas opciones solo cambian el estilo de las cajas temáticas del documento; no afectan los márgenes de página.",
            anchor="w",
            justify="left",
            wraplength=520,
        ).grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        self.tk.Checkbutton(cajas_frame, text="Activar decoraciones para las cajas", variable=self.decoracion_cajas_habilitada_var, command=self.actualizar_estado_adornos).grid(row=1, column=0, columnspan=2, sticky="w")
        self.tk.Label(cajas_frame, text="Pack decorativo para cajas").grid(row=2, column=0, sticky="w", pady=(8, 3))
        self.combo_pack_decoracion_cajas = self.ttk.Combobox(
            cajas_frame,
            textvariable=self.pack_decoracion_cajas_var,
            values=[etiqueta for etiqueta, codigo in cfg.PACKS_DECORACION_CAJAS_DISPONIBLES.items() if codigo != "NINGUNO"],
            state="readonly",
            width=24,
        )
        self.combo_pack_decoracion_cajas.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(8, 3))
        self.combo_pack_decoracion_cajas.bind("<<ComboboxSelected>>", self.actualizar_estado_adornos)

        self.etiqueta_estado_cajas = self.tk.Label(cajas_frame, text="", anchor="w", justify="left", wraplength=520, fg="#5F5F5F")
        self.etiqueta_estado_cajas.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        preview_cajas_frame = self.tk.Frame(cajas_frame, padx=8)
        preview_cajas_frame.grid(row=0, column=3, rowspan=4, sticky="ne", padx=(16, 0))
        self.tk.Label(preview_cajas_frame, text="Vista previa de cajas", anchor="w").pack(fill="x")
        self.canvas_preview_cajas = self.tk.Canvas(preview_cajas_frame, width=180, height=112, bg="#FFFFFF", highlightthickness=1, highlightbackground="#C8BBA8")
        self.canvas_preview_cajas.pack(pady=(6, 0))

        self.imagen_adorno_var.trace_add("write", self._actualizar_preview_adornos)
        self._inicializar_estado_margenes()
        self._actualizar_opciones_margen()
        self.actualizar_estado_adornos()

    def _construir_pestanas_colores(self, pestana_colores_base, pestana_colores_cajas, pestana_colores_personajes):
        grupos_colores = [
            ("General", [("color_primario", "Títulos"), ("color_secundario", "Texto general"), ("color_fondo_pagina", "Fondo de página")]),
            ("Caja Consejo para el DM", [("color_azul_texto", "Texto"), ("color_azul_borde", "Borde"), ("color_azul_fondo", "Fondo")]),
            ("Caja Cita", [("color_ama_texto", "Texto"), ("color_ama_borde", "Borde"), ("color_ama_fondo", "Fondo")]),
            ("Caja Información adicional", [("color_info_texto", "Texto"), ("color_info_borde", "Borde"), ("color_info_fondo", "Fondo")]),
            ("Caja NPC", [("color_npc_texto", "Texto"), ("color_npc_borde", "Borde"), ("color_npc_fondo", "Fondo")]),
            ("Caja Enemigo", [("color_enemigo_texto", "Texto"), ("color_enemigo_borde", "Borde"), ("color_enemigo_fondo", "Fondo")]),
            ("Caja Aliado", [("color_aliado_texto", "Texto"), ("color_aliado_borde", "Borde"), ("color_aliado_fondo", "Fondo")]),
            ("Caja Tesoro/Premio", [("color_tesoro_texto", "Texto"), ("color_tesoro_borde", "Borde"), ("color_tesoro_fondo", "Fondo")]),
            ("Caja Objeto", [("color_objeto_texto", "Texto"), ("color_objeto_borde", "Borde"), ("color_objeto_fondo", "Fondo")]),
        ]
        distribucion_pestanas = {
            "Colores base": ["General", "Caja Consejo para el DM", "Caja Cita"],
            "Cajas útiles": ["Caja Información adicional", "Caja Tesoro/Premio", "Caja Objeto"],
            "NPC y combate": ["Caja NPC", "Caja Enemigo", "Caja Aliado"],
        }
        contenedores = {"Colores base": pestana_colores_base, "Cajas útiles": pestana_colores_cajas, "NPC y combate": pestana_colores_personajes}
        contenedores_tarjetas = {}
        for nombre_pestana, pestana in contenedores.items():
            contenedor_tarjetas = self.tk.Frame(pestana)
            contenedor_tarjetas.pack(fill="x", anchor="n")
            contenedor_tarjetas.columnconfigure(0, weight=1)
            contenedor_tarjetas.columnconfigure(1, weight=0, minsize=300, uniform="tarjetas_colores")
            contenedor_tarjetas.columnconfigure(2, weight=0, minsize=300, uniform="tarjetas_colores")
            contenedor_tarjetas.columnconfigure(3, weight=1)
            contenedores_tarjetas[nombre_pestana] = contenedor_tarjetas
        for nombre_pestana, nombres_grupos in distribucion_pestanas.items():
            contenedor_tab = contenedores_tarjetas[nombre_pestana]
            for indice_grupo, nombre_grupo in enumerate(nombres_grupos):
                _, campos = next(grupo for grupo in grupos_colores if grupo[0] == nombre_grupo)
                columna = (indice_grupo % 2) + 1
                fila = indice_grupo // 2
                padding_x = (0, 8) if columna == 1 else (8, 0)
                frame = self.tk.LabelFrame(contenedor_tab, text=nombre_grupo, padx=10, pady=10)
                frame.grid(row=fila, column=columna, sticky="new", padx=padding_x, pady=(0, 10))
                frame.columnconfigure(0, minsize=88)
                frame.columnconfigure(1, minsize=84)
                frame.columnconfigure(3, minsize=66)
                for indice, (clave, etiqueta) in enumerate(campos):
                    self.crear_selector_color(frame, indice, clave, etiqueta)
        self.tk.Label(pestana_colores_base, text="Aquí están los colores base del documento y de las cajas más frecuentes.", anchor="w", justify="left", wraplength=760).pack(fill="x", pady=(8, 0))
        self.tk.Label(pestana_colores_cajas, text="Aquí puedes ajustar información adicional, tesoro/premio y objeto sin mezclarlo con NPC o combate.", anchor="w", justify="left", wraplength=760).pack(fill="x", pady=(8, 0))
        self.tk.Label(pestana_colores_personajes, text="Los bloques de NPC, enemigo y aliado comparten esta pestaña para ajustes rápidos de escena.", anchor="w", justify="left", wraplength=760).pack(fill="x", pady=(8, 0))

    def _construir_botones(self, contenedor):
        botones = self.tk.Frame(contenedor, padx=10, pady=8)
        botones.pack(fill="x")
        self.barra_botones = botones
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)
        self.estado_operacion_var = self.tk.StringVar(value="")
        self.etiqueta_estado_operacion = self.tk.Label(botones, textvariable=self.estado_operacion_var, anchor="w", justify="left", fg="#5F5F5F")
        self.etiqueta_estado_operacion.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        acciones_izquierda = self.tk.Frame(botones)
        acciones_izquierda.grid(row=1, column=0, sticky="w")
        acciones_derecha = self.tk.Frame(botones)
        acciones_derecha.grid(row=1, column=1, sticky="e")

        self.boton_restablecer = self.ttk.Button(acciones_izquierda, text="Restablecer valores", style="Secundario.TButton", command=self.restablecer_valores)
        self.boton_regresar = self.ttk.Button(acciones_izquierda, text="Regresar", style="Secundario.TButton", command=self.regresar_a_archivos)

        self.boton_cancelar = self.ttk.Button(acciones_derecha, text="Cancelar", style="Secundario.TButton", command=self.cancelar)
        self.boton_continuar = self.ttk.Button(acciones_derecha, text="Continuar", style="Primario.TButton", command=self.continuar_a_personalizacion)
        self.boton_aceptar = self.ttk.Button(acciones_derecha, text="Aceptar", style="Primario.TButton", command=self.aceptar)

    def actualizar_preview(self, clave):
        valor = cfg._normalizar_color_hex(self.variables_color[clave].get(), self.configuracion_inicial[clave])
        self.variables_color[clave].set(valor)
        self.vistas_previas[clave].configure(bg=valor)
        if clave in {"color_fondo_pagina", "color_info_texto", "color_info_borde", "color_info_fondo"}:
            self._actualizar_preview_adornos()

    def elegir_color(self, clave):
        color = self.colorchooser.askcolor(color=self.variables_color[clave].get(), title="Selecciona un color", parent=self.raiz)[1]
        if color:
            self.variables_color[clave].set(color)
            self.actualizar_preview(clave)

    def crear_selector_color(self, parent, fila, clave, etiqueta):
        self.tk.Label(parent, text=etiqueta, anchor="w").grid(row=fila, column=0, sticky="w", padx=(0, 8), pady=4)
        entrada_color = self.tk.Entry(parent, textvariable=self.variables_color[clave], width=10, justify="center")
        entrada_color.grid(row=fila, column=1, sticky="w", pady=4)
        entrada_color.bind("<FocusOut>", lambda _evento, clave_actual=clave: self._confirmar_color(clave_actual))
        entrada_color.bind("<Return>", lambda _evento, clave_actual=clave: self._confirmar_color(clave_actual))
        preview = self.tk.Label(parent, width=5, relief="groove", bg=self.variables_color[clave].get())
        preview.grid(row=fila, column=2, padx=5, pady=4)
        self.vistas_previas[clave] = preview
        self.tk.Button(parent, text="Elegir...", command=lambda clave_actual=clave: self.elegir_color(clave_actual)).grid(row=fila, column=3, sticky="w", pady=4)

    def _confirmar_color(self, clave):
        if clave not in self.variables_color:
            return
        self.actualizar_preview(clave)

    @staticmethod
    def _ruta_texto(ruta):
        return str(ruta or "").strip()

    def _salida_inicial_normalizada(self):
        salida_inicial = self._normalizar_ruta_salida(self.salida_inicial)
        if salida_inicial:
            return salida_inicial
        return self._sugerir_salida_desde_entrada(self.entrada_inicial)

    def _es_ruta_entrada_valida(self, ruta_texto):
        texto = self._ruta_texto(ruta_texto)
        if not texto:
            return False
        ruta = Path(texto)
        return ruta.exists() and ruta.is_file() and ruta.suffix.lower() == ".docx"

    def _normalizar_ruta_salida(self, ruta_texto):
        texto = self._ruta_texto(ruta_texto)
        if not texto:
            return ""
        ruta = Path(texto)
        if ruta.suffix.lower() != ".pdf":
            ruta = ruta.with_suffix(".pdf")
        return str(ruta)

    def _es_ruta_salida_valida(self, ruta_texto):
        texto = self._normalizar_ruta_salida(ruta_texto)
        if not texto:
            return False
        ruta = Path(texto)
        if ruta.suffix.lower() != ".pdf" or not ruta.name:
            return False
        directorio = ruta.parent if str(ruta.parent) else Path(".")
        return directorio.exists() and directorio.is_dir()

    def _rutas_actuales_validas(self):
        return self._es_ruta_entrada_valida(self.entrada_var.get()) and self._es_ruta_salida_valida(self.salida_var.get())

    def _sugerir_salida_desde_entrada(self, ruta_entrada_texto):
        if not self._es_ruta_entrada_valida(ruta_entrada_texto):
            return ""
        return str(Path(ruta_entrada_texto).with_suffix(".pdf"))

    def _actualizar_resumen_rutas(self):
        if self.resumen_entrada_var is not None:
            self.resumen_entrada_var.set(self.entrada_var.get().strip())
        if self.resumen_salida_var is not None:
            self.resumen_salida_var.set(self._normalizar_ruta_salida(self.salida_var.get()))

    def _mostrar_pagina_archivos(self):
        self.pagina_actual = "archivos"
        self.pagina_personalizacion.pack_forget()
        self.pagina_archivos.pack(fill="both", expand=True)
        self.titulo_encabezado.configure(text="Personaliza tu PDF antes de generarlo")
        self.descripcion_encabezado.configure(text="Primero elige una entrada `.docx` y una salida `.pdf` válidas. Después podrás continuar a la personalización.", wraplength=860)
        self.boton_restablecer.pack_forget()
        self.boton_regresar.pack_forget()
        self.boton_aceptar.pack_forget()
        self.boton_continuar.pack_forget()
        self.boton_cancelar.pack_forget()
        self.boton_cancelar.pack(side="left")
        self.boton_continuar.pack(side="left", padx=(14, 0))
        self.raiz.minsize(self.ancho_ventana_minimo, self.alto_ventana_minimo)

    def _mostrar_pagina_personalizacion(self):
        self.pagina_actual = "personalizacion"
        self.pagina_archivos.pack_forget()
        self.pagina_personalizacion.pack(fill="both", expand=True)
        self.titulo_encabezado.configure(text="Personaliza tu PDF")
        self.descripcion_encabezado.configure(text="Ajusta metadatos, portada, página, fuentes, márgenes y colores. Puedes volver atrás si necesitas cambiar la entrada o la salida.", wraplength=860)
        self._actualizar_resumen_rutas()
        self.boton_restablecer.pack_forget()
        self.boton_regresar.pack_forget()
        self.boton_aceptar.pack_forget()
        self.boton_continuar.pack_forget()
        self.boton_cancelar.pack_forget()
        self.boton_restablecer.pack(side="left")
        self.boton_regresar.pack(side="left", padx=(8, 0))
        self.boton_cancelar.pack(side="left")
        self.boton_aceptar.pack(side="left", padx=(14, 0))
        self.raiz.minsize(self.ancho_ventana_minimo, self.alto_ventana_minimo)

    def _calcular_dimensiones_compartidas_ventana(self):
        if self.raiz is None:
            return
        self.raiz.update_idletasks()
        ancho_pantalla = max(800, int(self.raiz.winfo_screenwidth()))
        alto_pantalla = max(600, int(self.raiz.winfo_screenheight()))

        ancho_paginas = max(self.pagina_archivos.winfo_reqwidth(), self.pagina_personalizacion.winfo_reqwidth())
        alto_paginas = max(self.pagina_archivos.winfo_reqheight(), self.pagina_personalizacion.winfo_reqheight())
        ancho_encabezado = max(self.titulo_encabezado.winfo_reqwidth(), self.descripcion_encabezado.winfo_reqwidth())
        alto_encabezado = self.titulo_encabezado.winfo_reqheight() + self.descripcion_encabezado.winfo_reqheight() + 20
        ancho_botones = self.barra_botones.winfo_reqwidth() if self.barra_botones is not None else 0
        alto_botones = self.barra_botones.winfo_reqheight() if self.barra_botones is not None else 0

        ancho_requerido = max(ancho_paginas, ancho_encabezado, ancho_botones) + 80
        alto_requerido = alto_paginas + alto_encabezado + alto_botones + 70

        ancho_objetivo = min(max(self.ancho_ventana_objetivo, ancho_requerido), ancho_pantalla)
        alto_objetivo = min(max(self.alto_ventana_objetivo, alto_requerido), int(alto_pantalla * 0.9))
        ancho_minimo = min(ancho_objetivo, max(self.ancho_ventana_minimo, ancho_requerido))
        alto_minimo = min(alto_objetivo, max(self.alto_ventana_minimo, alto_requerido))

        self.ancho_ventana_objetivo = ancho_objetivo
        self.alto_ventana_objetivo = alto_objetivo
        self.ancho_ventana_minimo = ancho_minimo
        self.alto_ventana_minimo = alto_minimo
        self.raiz.minsize(self.ancho_ventana_minimo, self.alto_ventana_minimo)

    def continuar_a_personalizacion(self):
        if not self._rutas_actuales_validas():
            self.messagebox.showerror("Rutas inválidas", "Selecciona un archivo `.docx` existente y una salida `.pdf` válida antes de continuar.")
            return
        self._mostrar_pagina_personalizacion()

    def regresar_a_archivos(self):
        self._mostrar_pagina_archivos()

    def elegir_archivo_entrada(self):
        ruta = self.filedialog.askopenfilename(title="Selecciona el archivo Word de entrada", filetypes=[("Documentos Word", "*.docx"), ("Todos los archivos", "*.*")], parent=self.raiz)
        if not ruta:
            return
        salida_actual = self._normalizar_ruta_salida(self.salida_var.get())
        self.entrada_var.set(ruta)
        salida_sugerida = self._sugerir_salida_desde_entrada(ruta)
        if not salida_actual or salida_actual == self.ultima_salida_sugerida:
            self.salida_var.set(salida_sugerida)
            self.ultima_salida_sugerida = salida_sugerida

    def elegir_archivo_salida(self):
        entrada_actual = self.entrada_var.get().strip()
        nombre_inicial = Path(entrada_actual).with_suffix(".pdf").name if self._es_ruta_entrada_valida(entrada_actual) else "salida.pdf"
        ruta = self.filedialog.asksaveasfilename(title="Guardar PDF como...", filetypes=[("Archivo PDF", "*.pdf"), ("Todos los archivos", "*.*")], defaultextension=".pdf", initialfile=nombre_inicial, parent=self.raiz)
        if ruta:
            ruta_normalizada = self._normalizar_ruta_salida(ruta)
            self.salida_var.set(ruta_normalizada)
            self.ultima_salida_sugerida = ruta_normalizada

    def elegir_portada(self):
        ruta = self.filedialog.askopenfilename(title="Selecciona la imagen de portada", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"), ("Todos los archivos", "*.*")], parent=self.raiz)
        if ruta:
            self.portada_var.set(ruta)

    def elegir_imagen_adorno(self):
        ruta = self.filedialog.askopenfilename(title="Selecciona un PNG para adornar los márgenes", filetypes=[("PNG con transparencia", "*.png"), ("Todos los archivos", "*.*")], parent=self.raiz)
        if ruta:
            self.imagen_adorno_var.set(ruta)

    def _codigo_estilo_adorno_seleccionado(self):
        return cfg.ESTILOS_ADORNO_MARGEN_DISPONIBLES.get(self.estilo_adorno_var.get(), cfg.ESTILO_ADORNO_MARGEN)

    @staticmethod
    def _formatear_margen_cm(valor):
        return f"{valor:.1f}"

    @staticmethod
    def _valores_margen_disponibles(adornos_activos=False):
        minimo = cfg.obtener_margen_minimo_cm(adornos_activos)
        valores = []
        valor_actual = minimo
        while valor_actual <= cfg.MARGEN_MAXIMO_CM + 1e-9:
            valores.append(round(valor_actual, 2))
            valor_actual += 0.5
        return valores

    def _opciones_margen_disponibles(self, adornos_activos=False):
        return [self._formatear_margen_cm(valor) for valor in self._valores_margen_disponibles(adornos_activos)]

    def _ajustar_margen_a_lista(self, valor, adornos_activos=False, valor_predeterminado=2.0):
        margen_normalizado = cfg.normalizar_margen_cm(valor, adornos_activos=adornos_activos, valor_predeterminado=valor_predeterminado)
        valores_disponibles = self._valores_margen_disponibles(adornos_activos)
        return min(valores_disponibles, key=lambda opcion: (abs(opcion - margen_normalizado), opcion))

    def _obtener_margen_actual_cm(self):
        try:
            return float(str(self.margen_var.get()).replace(",", ".").strip())
        except (AttributeError, TypeError, ValueError):
            return None

    def _inicializar_estado_margenes(self):
        adornos_activos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        margen_inicial = self._ajustar_margen_a_lista(self.configuracion_documento_inicial.get("margen_cm", 2.0), adornos_activos=adornos_activos)
        self.margen_var.set(self._formatear_margen_cm(margen_inicial))
        if adornos_activos:
            self.margen_con_adornos_guardado = margen_inicial
            self.margen_sin_adornos_guardado = self._ajustar_margen_a_lista(margen_inicial, adornos_activos=False)
        else:
            self.margen_sin_adornos_guardado = margen_inicial
            self.margen_con_adornos_guardado = None

    def _actualizar_opciones_margen(self):
        adornos_activos = bool(self.adornos_habilitados_var and self.adornos_habilitados_var.get())
        opciones = self._opciones_margen_disponibles(adornos_activos)
        if self.combo_margen is not None:
            self.combo_margen.configure(values=opciones, state="readonly")
        margen_actual = self._obtener_margen_actual_cm()
        if margen_actual is None:
            margen_actual = 2.0
        margen_ajustado = self._ajustar_margen_a_lista(margen_actual, adornos_activos=adornos_activos)
        texto_ajustado = self._formatear_margen_cm(margen_ajustado)
        if self.margen_var is not None and self.margen_var.get() != texto_ajustado:
            self.margen_var.set(texto_ajustado)

    def _registrar_margen_seleccionado(self, *_args):
        if self.margen_var is None:
            return
        adornos_activos = bool(self.adornos_habilitados_var and self.adornos_habilitados_var.get())
        margen_actual = self._obtener_margen_actual_cm()
        if margen_actual is None:
            return
        margen_ajustado = self._ajustar_margen_a_lista(margen_actual, adornos_activos=adornos_activos)
        texto_ajustado = self._formatear_margen_cm(margen_ajustado)
        if self.margen_var.get() != texto_ajustado:
            self.margen_var.set(texto_ajustado)
            return
        if adornos_activos:
            self.margen_con_adornos_guardado = margen_ajustado
        else:
            self.margen_sin_adornos_guardado = margen_ajustado

    def _actualizar_etiqueta_rango_margen(self):
        if self.etiqueta_rango_margen is None:
            return
        minimo_cm = cfg.obtener_margen_minimo_cm(bool(self.adornos_habilitados_var and self.adornos_habilitados_var.get()))
        if minimo_cm > cfg.MARGEN_MINIMO_CM:
            texto = f"Rango recomendado: {self._formatear_margen_cm(minimo_cm)} a {self._formatear_margen_cm(cfg.MARGEN_MAXIMO_CM)} cm con adornos"
        else:
            texto = f"Rango recomendado: {self._formatear_margen_cm(cfg.MARGEN_MINIMO_CM)} a {self._formatear_margen_cm(cfg.MARGEN_MAXIMO_CM)} cm"
        self.etiqueta_rango_margen.configure(text=texto)

    def _sincronizar_margen_con_adornos(self):
        if self.margen_var is None or self.adornos_habilitados_var is None:
            return
        adornos_activos = bool(self.adornos_habilitados_var.get())
        margen_actual = self._obtener_margen_actual_cm()
        if adornos_activos:
            if not self.adornos_activos_previos:
                if margen_actual is not None:
                    self.margen_sin_adornos_guardado = self._ajustar_margen_a_lista(margen_actual, adornos_activos=False)
                minimo_decorado = cfg.obtener_margen_minimo_cm(True)
                if self.margen_con_adornos_guardado is not None:
                    margen_destino = self._ajustar_margen_a_lista(self.margen_con_adornos_guardado, adornos_activos=True)
                elif margen_actual is not None and margen_actual >= minimo_decorado:
                    margen_destino = self._ajustar_margen_a_lista(margen_actual, adornos_activos=True)
                else:
                    margen_destino = self._ajustar_margen_a_lista(minimo_decorado, adornos_activos=True)
                self.margen_var.set(self._formatear_margen_cm(margen_destino))
            elif margen_actual is None:
                margen_destino = self.margen_con_adornos_guardado if self.margen_con_adornos_guardado is not None else cfg.obtener_margen_minimo_cm(True)
                self.margen_var.set(self._formatear_margen_cm(self._ajustar_margen_a_lista(margen_destino, adornos_activos=True)))
        else:
            if self.adornos_activos_previos:
                if margen_actual is not None:
                    self.margen_con_adornos_guardado = self._ajustar_margen_a_lista(margen_actual, adornos_activos=True)
                margen_destino = self.margen_sin_adornos_guardado
                if margen_destino is None:
                    base = margen_actual if margen_actual is not None else cfg.MARGEN_MINIMO_CM
                    margen_destino = self._ajustar_margen_a_lista(base, adornos_activos=False)
                else:
                    margen_destino = self._ajustar_margen_a_lista(margen_destino, adornos_activos=False)
                self.margen_var.set(self._formatear_margen_cm(margen_destino))
            elif margen_actual is None:
                margen_destino = self.margen_sin_adornos_guardado if self.margen_sin_adornos_guardado is not None else cfg.MARGEN_MINIMO_CM
                self.margen_var.set(self._formatear_margen_cm(self._ajustar_margen_a_lista(margen_destino, adornos_activos=False)))
        self.adornos_activos_previos = adornos_activos

    def actualizar_estado_adornos(self, *_args):
        adornos_activos = self.adornos_habilitados_var.get()
        cajas_activas = bool(self.decoracion_cajas_habilitada_var and self.decoracion_cajas_habilitada_var.get())
        estilo_personalizado = self._codigo_estilo_adorno_seleccionado() == "PERSONALIZADO"
        self._sincronizar_margen_con_adornos()
        self._actualizar_opciones_margen()
        self._actualizar_etiqueta_rango_margen()
        if self.combo_estilo_adorno is not None:
            self.combo_estilo_adorno.configure(state="readonly" if adornos_activos else "disabled")
        if self.combo_pack_decoracion_cajas is not None:
            self.combo_pack_decoracion_cajas.configure(state="readonly" if cajas_activas else "disabled")
        if self.boton_imagen_adorno is not None:
            self.boton_imagen_adorno.configure(state="normal" if adornos_activos and estilo_personalizado else "disabled")
        if self.entrada_imagen_adorno is not None:
            self.entrada_imagen_adorno.configure(state="readonly")
        if self.etiqueta_estado_margenes is not None:
            if not adornos_activos:
                texto_margenes = "Las florituras de margen están desactivadas. Puedes reactivarlas sin perder el preset o el PNG que ya seleccionaste."
            elif estilo_personalizado:
                if self.imagen_adorno_var.get().strip():
                    texto_margenes = "Se usará el PNG seleccionado como borde completo de página. Lo ideal es dejar el centro transparente para no tapar el contenido."
                else:
                    texto_margenes = "Has elegido borde personalizado. Selecciona un PNG transparente para completar la decoración de márgenes."
            else:
                texto_margenes = f"Se aplicará el preset {self.estilo_adorno_var.get()} en los márgenes de cada página y el margen mínimo pasará al rango decorado mientras esté activo."
            self.etiqueta_estado_margenes.configure(text=texto_margenes)
        if self.etiqueta_estado_cajas is not None:
            pack_actual = cfg.PACKS_DECORACION_CAJAS_DISPONIBLES.get(self.pack_decoracion_cajas_var.get(), "NINGUNO") if self.pack_decoracion_cajas_var is not None else "NINGUNO"
            if not cajas_activas:
                texto_cajas = "La decoración de cajas está desactivada. Las cajas especiales conservarán su estilo actual."
            elif pack_actual == "NINGUNO":
                texto_cajas = "Selecciona un pack para aplicar un estilo decorativo coherente a todas las cajas del documento."
            else:
                texto_cajas = f"Las cajas especiales usarán el pack {self.pack_decoracion_cajas_var.get()}. Esta opción no cambia los márgenes de página."
            self.etiqueta_estado_cajas.configure(text=texto_cajas)
        self._actualizar_preview_adornos()

    def _codigo_pack_cajas_seleccionado(self):
        if self.pack_decoracion_cajas_var is None:
            return "NINGUNO"
        return cfg.PACKS_DECORACION_CAJAS_DISPONIBLES.get(self.pack_decoracion_cajas_var.get(), "NINGUNO")

    def _actualizar_preview_adornos(self, *_args):
        if self.canvas_preview_adorno is None:
            self._actualizar_preview_cajas()
            return
        canvas = self.canvas_preview_adorno
        canvas.delete("all")
        color_fondo = self.variables_color.get("color_fondo_pagina")
        fondo = color_fondo.get() if color_fondo is not None else "#F7F1E3"
        fondo = cfg._normalizar_color_hex(fondo, "#F7F1E3")
        page_box = self._obtener_geometria_preview_margen(canvas)
        x1, y1, x2, y2 = page_box
        canvas.create_rectangle(x1, y1, x2, y2, fill=fondo, outline="#D4C5AF")

        if not self.adornos_habilitados_var.get():
            canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="Sin adornos", fill="#666666", font=("Segoe UI", 9))
            self.preview_adorno_imagen = None
            self._actualizar_preview_cajas()
            return

        estilo = self._codigo_estilo_adorno_seleccionado()
        if estilo == "PERSONALIZADO":
            self._dibujar_preview_adorno_personalizado(canvas, page_box)
            self._actualizar_preview_cajas()
            return
        if estilo == "FLORAL":
            self._dibujar_preview_adorno_floral(canvas, page_box)
            self._actualizar_preview_cajas()
            return
        if estilo == "GEOMETRICO":
            self._dibujar_preview_adorno_geometrico(canvas, page_box)
        else:
            self._dibujar_preview_adorno_clasico(canvas, page_box)
        self._actualizar_preview_cajas()

    @staticmethod
    def _obtener_geometria_preview_margen(canvas):
        ancho_canvas = int(float(canvas.cget("width")))
        alto_canvas = int(float(canvas.cget("height")))
        aspecto_pagina = 21.0 / 29.7
        max_ancho = max(60, ancho_canvas - 24)
        max_alto = max(80, alto_canvas - 20)
        ancho_pagina = max_ancho
        alto_pagina = ancho_pagina / aspecto_pagina
        if alto_pagina > max_alto:
            alto_pagina = max_alto
            ancho_pagina = alto_pagina * aspecto_pagina
        x1 = int(round((ancho_canvas - ancho_pagina) / 2))
        y1 = int(round((alto_canvas - alto_pagina) / 2))
        x2 = int(round(x1 + ancho_pagina))
        y2 = int(round(y1 + alto_pagina))
        return x1, y1, x2, y2

    def _actualizar_preview_cajas(self):
        if self.canvas_preview_cajas is None:
            return
        canvas = self.canvas_preview_cajas
        canvas.delete("all")
        color_fondo = self.variables_color.get("color_fondo_pagina")
        fondo_pagina = color_fondo.get() if color_fondo is not None else "#F7F1E3"
        fondo_pagina = cfg._normalizar_color_hex(fondo_pagina, "#F7F1E3")
        canvas.create_rectangle(0, 0, 180, 112, fill=fondo_pagina, outline="")
        color_borde = cfg._normalizar_color_hex(self.variables_color.get("color_info_borde").get(), "#2AA198") if self.variables_color.get("color_info_borde") is not None else "#2AA198"

        if not (self.decoracion_cajas_habilitada_var and self.decoracion_cajas_habilitada_var.get()):
            self._dibujar_preview_caja_base(canvas, "NINGUNO")
            return

        pack = self._codigo_pack_cajas_seleccionado()
        self._dibujar_preview_caja_base(canvas, pack)
        if pack == "PERGAMINO_NOBLE":
            self._dibujar_preview_pack_pergamino_noble(canvas, color_borde)
        elif pack == "GRIMORIO_ARCANO":
            self._dibujar_preview_pack_grimorio_arcano(canvas, color_borde)
        elif pack == "HERALDICA_CAMPANA":
            self._dibujar_preview_pack_heraldica_campana(canvas)

    @staticmethod
    def _dibujar_preview_caja_redondeada(canvas, x1, y1, x2, y2, radio, fill, outline, width=1):
        radio = max(0, min(radio, (x2 - x1) / 2, (y2 - y1) / 2))
        if radio <= 0:
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)
            return
        canvas.create_rectangle(x1 + radio, y1, x2 - radio, y2, fill=fill, outline="")
        canvas.create_rectangle(x1, y1 + radio, x2, y2 - radio, fill=fill, outline="")
        canvas.create_arc(x1, y1, x1 + (2 * radio), y1 + (2 * radio), start=90, extent=90, style="pieslice", fill=fill, outline="")
        canvas.create_arc(x2 - (2 * radio), y1, x2, y1 + (2 * radio), start=0, extent=90, style="pieslice", fill=fill, outline="")
        canvas.create_arc(x1, y2 - (2 * radio), x1 + (2 * radio), y2, start=180, extent=90, style="pieslice", fill=fill, outline="")
        canvas.create_arc(x2 - (2 * radio), y2 - (2 * radio), x2, y2, start=270, extent=90, style="pieslice", fill=fill, outline="")
        canvas.create_line(x1 + radio, y1, x2 - radio, y1, fill=outline, width=width)
        canvas.create_line(x1 + radio, y2, x2 - radio, y2, fill=outline, width=width)
        canvas.create_line(x1, y1 + radio, x1, y2 - radio, fill=outline, width=width)
        canvas.create_line(x2, y1 + radio, x2, y2 - radio, fill=outline, width=width)
        canvas.create_arc(x1, y1, x1 + (2 * radio), y1 + (2 * radio), start=90, extent=90, style="arc", outline=outline, width=width)
        canvas.create_arc(x2 - (2 * radio), y1, x2, y1 + (2 * radio), start=0, extent=90, style="arc", outline=outline, width=width)
        canvas.create_arc(x1, y2 - (2 * radio), x1 + (2 * radio), y2, start=180, extent=90, style="arc", outline=outline, width=width)
        canvas.create_arc(x2 - (2 * radio), y2 - (2 * radio), x2, y2, start=270, extent=90, style="arc", outline=outline, width=width)

    def _dibujar_preview_caja_base(self, canvas, pack):
        color_borde = cfg._normalizar_color_hex(self.variables_color.get("color_info_borde").get(), "#2AA198") if self.variables_color.get("color_info_borde") is not None else "#2AA198"
        color_fondo = cfg._normalizar_color_hex(self.variables_color.get("color_info_fondo").get(), "#E7F6F5") if self.variables_color.get("color_info_fondo") is not None else "#E7F6F5"
        if pack == "PERGAMINO_NOBLE":
            self._dibujar_preview_caja_redondeada(canvas, 16, 20, 164, 94, 10, color_fondo, color_borde, width=2)
            return
        if pack == "HERALDICA_CAMPANA":
            self._dibujar_preview_caja_redondeada(canvas, 16, 20, 164, 94, 8, color_fondo, color_borde, width=2)
            return
        canvas.create_rectangle(16, 20, 164, 94, fill=color_fondo, outline=color_borde, width=2)

    @staticmethod
    def _dibujar_preview_pack_pergamino_noble(canvas, color_borde):
        canvas.create_arc(16, 20, 36, 40, start=90, extent=90, style="arc", outline=color_borde, width=2)
        canvas.create_arc(144, 20, 164, 40, start=0, extent=90, style="arc", outline=color_borde, width=2)
        canvas.create_arc(16, 74, 36, 94, start=180, extent=90, style="arc", outline=color_borde, width=2)
        canvas.create_arc(144, 74, 164, 94, start=270, extent=90, style="arc", outline=color_borde, width=2)
        canvas.create_line(48, 28, 132, 28, fill=color_borde)
        canvas.create_line(48, 86, 132, 86, fill=color_borde)
        for pos_x, pos_y, dir_x, dir_y in [(28, 32, 1, 1), (152, 32, -1, 1), (28, 82, 1, -1), (152, 82, -1, -1)]:
            canvas.create_line(
                pos_x,
                pos_y + (4 * dir_y),
                pos_x,
                pos_y,
                pos_x + (8 * dir_x),
                pos_y,
                pos_x + (8 * dir_x),
                pos_y + (4 * dir_y),
                smooth=True,
                fill=color_borde,
                width=1,
            )
            canvas.create_oval(
                pos_x + (4 * dir_x) - 1.2,
                pos_y + (2 * dir_y) - 1.2,
                pos_x + (4 * dir_x) + 1.2,
                pos_y + (2 * dir_y) + 1.2,
                outline=color_borde,
            )

    @staticmethod
    def _dibujar_preview_pack_grimorio_arcano(canvas, color_borde):
        canvas.create_rectangle(22, 26, 158, 88, outline=color_borde)
        for cx, cy in [(90, 24), (90, 90), (20, 57), (160, 57)]:
            canvas.create_polygon(cx, cy - 4, cx + 4, cy, cx, cy + 4, cx - 4, cy, outline=color_borde, fill="")
        for pos_x, pos_y in [(28, 32), (152, 32), (28, 82), (152, 82)]:
            canvas.create_line(pos_x - 4, pos_y, pos_x + 4, pos_y, fill=color_borde)
            canvas.create_line(pos_x, pos_y - 4, pos_x, pos_y + 4, fill=color_borde)

    @staticmethod
    def _dibujar_preview_pack_heraldica_campana(canvas):
        canvas.create_arc(16, 20, 32, 36, start=90, extent=90, style="arc", outline="#2AA198", width=2)
        canvas.create_arc(148, 20, 164, 36, start=0, extent=90, style="arc", outline="#2AA198", width=2)
        canvas.create_arc(16, 78, 32, 94, start=180, extent=90, style="arc", outline="#2AA198", width=2)
        canvas.create_arc(148, 78, 164, 94, start=270, extent=90, style="arc", outline="#2AA198", width=2)
        canvas.create_line(32, 24, 148, 24, fill="#2AA198")
        canvas.create_line(32, 90, 148, 90, fill="#2AA198")
        canvas.create_line(76, 24, 90, 16, 104, 24, fill="#2AA198", smooth=True)
        for x, y in [(22, 26), (158, 26), (22, 88), (158, 88)]:
            canvas.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5, outline="#2AA198")

    def _dibujar_preview_adorno_personalizado(self, canvas, page_box):
        x1, y1, x2, y2 = page_box
        ruta = self.imagen_adorno_var.get().strip()
        if not ruta or not Path(ruta).is_file():
            canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="Selecciona un PNG\ntransparente", fill="#666666", justify="center", font=("Segoe UI", 9))
            canvas.create_rectangle(x1 + 8, y1 + 8, x2 - 8, y2 - 8, outline="#8B0000", dash=(4, 3))
            self.preview_adorno_imagen = None
            return
        try:
            imagen = PILImage.open(ruta).convert("RGBA")
            imagen.thumbnail((max(20, (x2 - x1) - 8), max(20, (y2 - y1) - 8)), PILImage.Resampling.LANCZOS)
            self.preview_adorno_imagen = ImageTk.PhotoImage(imagen)
            canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=self.preview_adorno_imagen)
        except Exception:
            canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="No se pudo cargar\nel PNG", fill="#7A1C1C", justify="center", font=("Segoe UI", 9))
            self.preview_adorno_imagen = None

    @staticmethod
    def _dibujar_preview_adorno_clasico(canvas, page_box):
        x1, y1, x2, y2 = page_box
        margen_ext = 8
        margen_int = 16
        canvas.create_rectangle(x1 + margen_ext, y1 + margen_ext, x2 - margen_ext, y2 - margen_ext, outline="#8B0000", width=2)
        canvas.create_rectangle(x1 + margen_int, y1 + margen_int, x2 - margen_int, y2 - margen_int, outline="#333333")
        centro_x = (x1 + x2) / 2
        centro_y = (y1 + y2) / 2
        for px, py in [(centro_x, y1 + margen_ext), (centro_x, y2 - margen_ext), (x1 + margen_ext, centro_y), (x2 - margen_ext, centro_y)]:
            canvas.create_oval(px - 3, py - 3, px + 3, py + 3, outline="#333333")
        for esquina_x, esquina_y, direccion_x, direccion_y in [
            (x1 + margen_int, y1 + margen_int, 1, 1),
            (x2 - margen_int, y1 + margen_int, -1, 1),
            (x1 + margen_int, y2 - margen_int, 1, -1),
            (x2 - margen_int, y2 - margen_int, -1, -1),
        ]:
            canvas.create_line(esquina_x, esquina_y, esquina_x + (10 * direccion_x), esquina_y, fill="#333333")
            canvas.create_line(esquina_x, esquina_y, esquina_x, esquina_y + (10 * direccion_y), fill="#333333")
            canvas.create_line(
                esquina_x + (2 * direccion_x),
                esquina_y + (8 * direccion_y),
                esquina_x + (4 * direccion_x),
                esquina_y + (4 * direccion_y),
                esquina_x + (8 * direccion_x),
                esquina_y + (4 * direccion_y),
                esquina_x + (8 * direccion_x),
                esquina_y + (2 * direccion_y),
                smooth=True,
                fill="#333333",
            )
            canvas.create_oval(
                esquina_x + (4 * direccion_x) - 1.5,
                esquina_y + (4 * direccion_y) - 1.5,
                esquina_x + (4 * direccion_x) + 1.5,
                esquina_y + (4 * direccion_y) + 1.5,
                outline="#333333",
            )

    @staticmethod
    def _dibujar_preview_adorno_geometrico(canvas, page_box):
        x1, y1, x2, y2 = page_box
        margen = 8
        canvas.create_rectangle(x1 + margen, y1 + margen, x2 - margen, y2 - margen, outline="#333333", width=2, dash=(5, 3))
        for x1, y1, x2, y2 in [
            (page_box[0] + margen, page_box[1] + margen, page_box[0] + margen + 18, page_box[1] + margen),
            (page_box[0] + margen, page_box[1] + margen, page_box[0] + margen, page_box[1] + margen + 18),
            (page_box[2] - margen, page_box[1] + margen, page_box[2] - margen - 18, page_box[1] + margen),
            (page_box[2] - margen, page_box[1] + margen, page_box[2] - margen, page_box[1] + margen + 18),
            (page_box[0] + margen, page_box[3] - margen, page_box[0] + margen + 18, page_box[3] - margen),
            (page_box[0] + margen, page_box[3] - margen, page_box[0] + margen, page_box[3] - margen - 18),
            (page_box[2] - margen, page_box[3] - margen, page_box[2] - margen - 18, page_box[3] - margen),
            (page_box[2] - margen, page_box[3] - margen, page_box[2] - margen, page_box[3] - margen - 18),
        ]:
            canvas.create_line(x1, y1, x2, y2, fill="#8B0000", width=2)
        for centro_x, centro_y in [
            (page_box[0] + 20, page_box[1] + 20),
            (page_box[2] - 20, page_box[1] + 20),
            (page_box[0] + 20, page_box[3] - 20),
            (page_box[2] - 20, page_box[3] - 20),
        ]:
            canvas.create_line(centro_x, centro_y - 5, centro_x + 5, centro_y, fill="#8B0000")
            canvas.create_line(centro_x + 5, centro_y, centro_x, centro_y + 5, fill="#8B0000")
            canvas.create_line(centro_x, centro_y + 5, centro_x - 5, centro_y, fill="#8B0000")
            canvas.create_line(centro_x - 5, centro_y, centro_x, centro_y - 5, fill="#8B0000")
            canvas.create_line(centro_x - 2, centro_y, centro_x + 2, centro_y, fill="#8B0000")
            canvas.create_line(centro_x, centro_y - 2, centro_x, centro_y + 2, fill="#8B0000")
            canvas.create_oval(centro_x - 1, centro_y - 1, centro_x + 1, centro_y + 1, outline="#8B0000")
        centro_x = (page_box[0] + page_box[2]) / 2
        centro_y = (page_box[1] + page_box[3]) / 2
        for centro_x, centro_y in [(page_box[0] + margen, centro_y), (page_box[2] - margen, centro_y), (centro_x, page_box[1] + margen), (centro_x, page_box[3] - margen)]:
            canvas.create_line(centro_x - 7, centro_y, centro_x, centro_y - 7, fill="#8B0000")
            canvas.create_line(centro_x, centro_y - 7, centro_x + 7, centro_y, fill="#8B0000")
            canvas.create_line(centro_x + 7, centro_y, centro_x, centro_y + 7, fill="#8B0000")
            canvas.create_line(centro_x, centro_y + 7, centro_x - 7, centro_y, fill="#8B0000")
            canvas.create_oval(centro_x - 1.2, centro_y - 1.2, centro_x + 1.2, centro_y + 1.2, outline="#8B0000")

    @staticmethod
    def _dibujar_preview_adorno_floral(canvas, page_box):
        x1, y1, x2, y2 = page_box
        borde_ext = 10
        borde_int = 17
        canvas.create_rectangle(x1 + borde_ext, y1 + borde_ext, x2 - borde_ext, y2 - borde_ext, outline="#8B0000", width=1)
        canvas.create_rectangle(x1 + borde_int, y1 + borde_int, x2 - borde_int, y2 - borde_int, outline="#333333")

        arriba = y1 + borde_int + 5
        abajo = y2 - borde_int - 5
        izquierda = x1 + borde_int + 5
        derecha = x2 - borde_int - 5

        for puntos in [
            (izquierda, abajo, izquierda + 4, abajo, izquierda + 9, abajo - 5, izquierda + 14, abajo - 10),
            (izquierda, abajo, izquierda, abajo - 4, izquierda + 5, abajo - 9, izquierda + 14, abajo - 10),
            (derecha, abajo, derecha - 4, abajo, derecha - 9, abajo - 5, derecha - 14, abajo - 10),
            (derecha, abajo, derecha, abajo - 4, derecha - 5, abajo - 9, derecha - 14, abajo - 10),
            (izquierda, arriba, izquierda + 4, arriba, izquierda + 9, arriba + 5, izquierda + 14, arriba + 10),
            (izquierda, arriba, izquierda, arriba + 4, izquierda + 5, arriba + 9, izquierda + 14, arriba + 10),
            (derecha, arriba, derecha - 4, arriba, derecha - 9, arriba + 5, derecha - 14, arriba + 10),
            (derecha, arriba, derecha, arriba + 4, derecha - 5, arriba + 9, derecha - 14, arriba + 10),
        ]:
            canvas.create_line(*puntos, smooth=True, fill="#333333")

        canvas.create_line(izquierda + 2, arriba + 2, izquierda + 10, arriba + 10, fill="#333333")
        canvas.create_line(derecha - 2, arriba + 2, derecha - 10, arriba + 10, fill="#333333")
        canvas.create_line(izquierda + 2, abajo - 2, izquierda + 10, abajo - 10, fill="#333333")
        canvas.create_line(derecha - 2, abajo - 2, derecha - 10, abajo - 10, fill="#333333")
        for x, y in [(izquierda + 7, arriba + 7), (derecha - 7, arriba + 7), (izquierda + 7, abajo - 7), (derecha - 7, abajo - 7)]:
            canvas.create_oval(x - 1.5, y - 1.5, x + 1.5, y + 1.5, outline="#333333")

        centro_x = (x1 + x2) / 2
        canvas.create_line(centro_x - 18, y1 + borde_ext, centro_x - 12, y1 + borde_ext, centro_x - 6, y1 + 3, centro_x, y1 + 7, smooth=True, fill="#333333")
        canvas.create_line(centro_x + 18, y1 + borde_ext, centro_x + 12, y1 + borde_ext, centro_x + 6, y1 + 3, centro_x, y1 + 7, smooth=True, fill="#333333")
        canvas.create_line(centro_x - 11, y1 + borde_ext + 4, centro_x - 6, y1 + 2, centro_x - 2, y1 + 1, centro_x, y1 + 7, smooth=True, fill="#333333")
        canvas.create_line(centro_x + 11, y1 + borde_ext + 4, centro_x + 6, y1 + 2, centro_x + 2, y1 + 1, centro_x, y1 + 7, smooth=True, fill="#333333")
        canvas.create_oval(centro_x - 1.5, y1 + 5.5, centro_x + 1.5, y1 + 8.5, outline="#333333")

        canvas.create_line(centro_x - 18, y2 - borde_ext, centro_x - 12, y2 - borde_ext, centro_x - 6, y2 - 3, centro_x, y2 - 7, smooth=True, fill="#333333")
        canvas.create_line(centro_x + 18, y2 - borde_ext, centro_x + 12, y2 - borde_ext, centro_x + 6, y2 - 3, centro_x, y2 - 7, smooth=True, fill="#333333")
        canvas.create_line(centro_x - 11, y2 - borde_ext - 4, centro_x - 6, y2 - 2, centro_x - 2, y2 - 1, centro_x, y2 - 7, smooth=True, fill="#333333")
        canvas.create_line(centro_x + 11, y2 - borde_ext - 4, centro_x + 6, y2 - 2, centro_x + 2, y2 - 1, centro_x, y2 - 7, smooth=True, fill="#333333")
        canvas.create_oval(centro_x - 1.5, y2 - 8.5, centro_x + 1.5, y2 - 5.5, outline="#333333")

        centro_y = (y1 + y2) / 2
        canvas.create_line(x1 + borde_ext, centro_y, x1 + borde_ext + 8, centro_y, fill="#333333")
        canvas.create_line(x2 - borde_ext, centro_y, x2 - borde_ext - 8, centro_y, fill="#333333")
        canvas.create_oval(x1 + borde_ext + 3, centro_y - 1.5, x1 + borde_ext + 6, centro_y + 1.5, outline="#333333")
        canvas.create_oval(x2 - borde_ext - 6, centro_y - 1.5, x2 - borde_ext - 3, centro_y + 1.5, outline="#333333")

    def actualizar_estado_rutas(self, *_args):
        entrada_texto = self.entrada_var.get().strip()
        salida_texto = self.salida_var.get().strip()
        entrada_valida = self._es_ruta_entrada_valida(entrada_texto)
        salida_valida = self._es_ruta_salida_valida(salida_texto)
        if salida_texto:
            salida_normalizada = self._normalizar_ruta_salida(salida_texto)
            if salida_normalizada != salida_texto:
                self.salida_var.set(salida_normalizada)
                return
        if entrada_valida and salida_valida:
            self.estado_rutas_var.set("Rutas válidas. Pulsa `Continuar` para abrir las opciones de personalización.")
            self.estado_rutas_label.configure(fg="#1E5631")
        elif not entrada_texto and not salida_texto:
            self.estado_rutas_var.set("Selecciona un archivo Word de entrada y una ruta PDF de salida para continuar.")
            self.estado_rutas_label.configure(fg="#7A1C1C")
        elif not entrada_valida:
            self.estado_rutas_var.set("La entrada debe apuntar a un archivo `.docx` existente.")
            self.estado_rutas_label.configure(fg="#7A1C1C")
        else:
            self.estado_rutas_var.set("La salida debe ser una ruta `.pdf` válida en una carpeta existente.")
            self.estado_rutas_label.configure(fg="#7A1C1C")
        if self.boton_continuar is not None:
            self.boton_continuar.configure(state="normal" if entrada_valida and salida_valida else "disabled")
        self._actualizar_resumen_rutas()

    def actualizar_estado_portada(self):
        estado = "normal" if self.portada_habilitada_var.get() else "disabled"
        self.boton_portada.configure(state=estado)
        self.entrada_portada.configure(state="readonly")
        if self.check_portada_pagina_completa is not None:
            self.check_portada_pagina_completa.configure(state=estado)
        estado_modo = "readonly" if self.portada_habilitada_var.get() and self.portada_pagina_completa_var.get() else "disabled"
        if self.combo_portada_modo_ajuste is not None:
            self.combo_portada_modo_ajuste.configure(state=estado_modo)
        if self.etiqueta_ayuda_portada is not None:
            ruta_portada = self.portada_var.get().strip()
            if self.portada_habilitada_var.get():
                if ruta_portada:
                    if self.portada_pagina_completa_var is not None and self.portada_pagina_completa_var.get():
                        modo = cfg.MODOS_AJUSTE_PORTADA_DISPONIBLES.get(self.portada_modo_ajuste_var.get(), "CUBRIR") if self.portada_modo_ajuste_var is not None else "CUBRIR"
                        if modo == "ENCAJAR":
                            texto = "La portada está activa y la imagen se redimensionará en ancho y alto para ocupar toda la hoja sin recorte, aunque su proporción original cambie."
                        else:
                            texto = "La portada está activa y la imagen cubrirá toda la primera página. Si la proporción no coincide con el papel, el PDF recortará los bordes sobrantes."
                    else:
                        texto = "La portada está activa y usará la imagen seleccionada centrada dentro del área útil. Si la desactivas, la ruta se conservará por si quieres reactivarla luego."
                else:
                    texto = "Activa la portada solo si quieres añadir una imagen inicial al PDF. Puedes dejar título, subtítulo y autor vacíos sin problema."
            else:
                texto = "La portada está desactivada. Si ya elegiste una imagen, se conserva para que puedas recuperarla más tarde con un clic."
            self.etiqueta_ayuda_portada.configure(text=texto)

    def actualizar_estado_tamano_personalizado(self, *_args):
        es_personalizado = self.tamano_pagina_var.get().strip().upper() == cfg.OPCION_TAMANO_PERSONALIZADO
        estado = "normal" if es_personalizado else "disabled"
        self.entrada_ancho.configure(state=estado)
        self.entrada_alto.configure(state=estado)
        if self.etiqueta_ayuda_tamano is not None:
            if es_personalizado:
                texto = "Introduce ancho y alto entre 5 y 100 cm. Estos campos solo se aplican cuando el tamaño de página es PERSONALIZADO."
            else:
                texto = "Usa un tamaño estándar para una configuración rápida, o cambia a PERSONALIZADO si necesitas medidas exactas."
            self.etiqueta_ayuda_tamano.configure(text=texto)

    def restablecer_valores(self):
        for clave, valor in self.configuracion_inicial.items():
            self.variables_color[clave].set(valor)
            self.actualizar_preview(clave)
        self.titulo_var.set(self.titulo_inicial)
        self.subtitulo_var.set(self.subtitulo_inicial)
        self.autor_var.set(self.autor_inicial)
        self.tamano_pagina_var.set(self.configuracion_documento_inicial.get("tamano_pagina", "A4"))
        self.fuente_titulo_var.set(self.configuracion_documento_inicial.get("fuente_titulo", cfg.FUENTE_TITULO))
        self.fuente_texto_var.set(self.configuracion_documento_inicial.get("fuente_texto", cfg.FUENTE_TEXTO))
        self.margen_var.set(self._formatear_margen_cm(self._ajustar_margen_a_lista(self.configuracion_documento_inicial.get("margen_cm", 2.0), adornos_activos=bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False)))))
        self.margen_sin_adornos_guardado = None
        self.margen_con_adornos_guardado = None
        self.adornos_activos_previos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        self.ancho_pagina_var.set(str(self.configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)))
        self.alto_pagina_var.set(str(self.configuracion_documento_inicial.get("alto_pagina_cm", 29.7)))
        self.adornos_habilitados_var.set(bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False)))
        self.estilo_adorno_var.set(cfg.obtener_etiqueta_estilo_adorno_margen(self.configuracion_documento_inicial.get("estilo_adorno_margen", cfg.ESTILO_ADORNO_MARGEN)))
        self.imagen_adorno_var.set(str(self.configuracion_documento_inicial.get("imagen_adorno_margen", "") or "").strip())
        pack_inicial = cfg.normalizar_pack_decoracion_cajas(self.configuracion_documento_inicial.get("pack_decoracion_cajas", "NINGUNO"))
        self.decoracion_cajas_habilitada_var.set(pack_inicial != "NINGUNO")
        self.pack_decoracion_cajas_var.set(cfg.obtener_etiqueta_pack_decoracion_cajas(pack_inicial if pack_inicial != "NINGUNO" else "PERGAMINO_NOBLE"))
        self._inicializar_estado_margenes()
        self._actualizar_opciones_margen()
        portada_explicita = bool(self.portada_inicial and self.portada_inicial != cfg.IMAGEN_PORTADA_PREDETERMINADA)
        self.portada_habilitada_var.set(portada_explicita)
        self.portada_var.set(self.portada_inicial if portada_explicita else "")
        self.portada_pagina_completa_var.set(bool(self.configuracion_documento_inicial.get("portada_pagina_completa", False)))
        self.portada_modo_ajuste_var.set(cfg.obtener_etiqueta_modo_ajuste_portada(self.configuracion_documento_inicial.get("portada_modo_ajuste", "CUBRIR")))
        self.actualizar_estado_portada()
        self.actualizar_estado_tamano_personalizado()
        self.actualizar_estado_adornos()

    def cancelar(self):
        self.resultado["valor"] = None
        self.raiz.quit()

    def _establecer_estado_operacion(self, texto, color="#5F5F5F"):
        if self.estado_operacion_var is not None:
            self.estado_operacion_var.set(texto)
        if self.etiqueta_estado_operacion is not None:
            self.etiqueta_estado_operacion.configure(fg=color)

    def _establecer_estado_controles_generacion(self, generando=False):
        estado_secundario = "disabled" if generando else "normal"
        estado_primario = "disabled" if generando else "normal"
        if self.boton_aceptar is not None:
            self.boton_aceptar.configure(state=estado_primario)
        if self.boton_continuar is not None:
            self.boton_continuar.configure(state=estado_primario if self._rutas_actuales_validas() else "disabled")
        if self.boton_cancelar is not None:
            self.boton_cancelar.configure(state=estado_secundario)
        if self.boton_regresar is not None:
            self.boton_regresar.configure(state=estado_secundario)
        if self.boton_restablecer is not None:
            self.boton_restablecer.configure(state=estado_secundario)
        if self.raiz is not None:
            self.raiz.configure(cursor="watch" if generando else "")

    def aceptar(self):
        entrada = self.entrada_var.get().strip()
        salida = self._normalizar_ruta_salida(self.salida_var.get())
        if not self._es_ruta_entrada_valida(entrada):
            self.messagebox.showerror("Entrada inválida", "Selecciona un archivo `.docx` de entrada válido.")
            return
        if not self._es_ruta_salida_valida(salida):
            self.messagebox.showerror("Salida inválida", "Selecciona una ruta de salida `.pdf` válida.")
            return
        configuracion_visual = {}
        for clave, valor in self.configuracion_inicial.items():
            color_normalizado = cfg._normalizar_color_hex(self.variables_color[clave].get(), valor)
            if color_normalizado != self.variables_color[clave].get().strip():
                self.variables_color[clave].set(color_normalizado)
            try:
                HexColor(color_normalizado)
            except Exception:
                self.messagebox.showerror("Color inválido", f"El color para '{clave}' no es válido.")
                return
            configuracion_visual[clave] = color_normalizado
        imagen_portada = self.portada_var.get().strip() if self.portada_habilitada_var.get() else ""
        if self.portada_habilitada_var.get() and not imagen_portada:
            self.messagebox.showerror("Portada incompleta", "Selecciona la imagen de portada o desactiva la opción.")
            return
        adornos_margen_activos = bool(self.adornos_habilitados_var.get())
        margen_minimo_cm = cfg.obtener_margen_minimo_cm(adornos_margen_activos)
        try:
            margen_cm = float(str(self.margen_var.get()).replace(",", ".").strip())
        except (TypeError, ValueError):
            self.messagebox.showerror("Margen inválido", "El margen debe ser un número en centímetros.")
            return
        margen_cm = self._ajustar_margen_a_lista(margen_cm, adornos_activos=adornos_margen_activos)
        if margen_cm < margen_minimo_cm:
            margen_cm = self._ajustar_margen_a_lista(margen_minimo_cm, adornos_activos=adornos_margen_activos)
            self.margen_var.set(self._formatear_margen_cm(margen_cm))
        if margen_cm > cfg.MARGEN_MAXIMO_CM:
            self.messagebox.showerror("Margen inválido", f"El margen debe estar entre {self._formatear_margen_cm(margen_minimo_cm)} y {self._formatear_margen_cm(cfg.MARGEN_MAXIMO_CM)} cm.")
            return
        margen_cm = self._ajustar_margen_a_lista(margen_cm, adornos_activos=adornos_margen_activos)
        self.margen_var.set(self._formatear_margen_cm(margen_cm))
        tamano_pagina = self.tamano_pagina_var.get().strip().upper()
        ancho_pagina_cm = self.configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)
        alto_pagina_cm = self.configuracion_documento_inicial.get("alto_pagina_cm", 29.7)
        if tamano_pagina == cfg.OPCION_TAMANO_PERSONALIZADO:
            try:
                ancho_pagina_cm = float(str(self.ancho_pagina_var.get()).replace(",", ".").strip())
                alto_pagina_cm = float(str(self.alto_pagina_var.get()).replace(",", ".").strip())
            except (TypeError, ValueError):
                self.messagebox.showerror("Tamaño inválido", "El ancho y alto personalizados deben ser números en centímetros.")
                return
            if not (5.0 <= ancho_pagina_cm <= 100.0 and 5.0 <= alto_pagina_cm <= 100.0):
                self.messagebox.showerror("Tamaño inválido", "El ancho y alto personalizados deben estar entre 5 y 100 cm.")
                return
        estilo_adorno_margen = self._codigo_estilo_adorno_seleccionado()
        imagen_adorno_margen = self.imagen_adorno_var.get().strip()
        decoracion_cajas_activa = bool(self.decoracion_cajas_habilitada_var.get()) if self.decoracion_cajas_habilitada_var is not None else False
        if adornos_margen_activos and estilo_adorno_margen == "PERSONALIZADO":
            if not imagen_adorno_margen:
                self.messagebox.showerror("Adorno incompleto", "Selecciona un PNG transparente para el borde personalizado o cambia a un preset.")
                return
            ruta_adorno = Path(imagen_adorno_margen)
            if not ruta_adorno.exists() or not ruta_adorno.is_file() or ruta_adorno.suffix.lower() != ".png":
                self.messagebox.showerror("PNG inválido", "El adorno personalizado debe ser un archivo `.png` existente.")
                return
        configuracion_documento = {
            "tamano_pagina": tamano_pagina,
            "fuente_titulo": self.fuente_titulo_var.get().strip(),
            "fuente_texto": self.fuente_texto_var.get().strip(),
            "margen_cm": margen_cm,
            "ancho_pagina_cm": ancho_pagina_cm,
            "alto_pagina_cm": alto_pagina_cm,
            "adornos_margen_activos": adornos_margen_activos,
            "estilo_adorno_margen": estilo_adorno_margen,
            "imagen_adorno_margen": imagen_adorno_margen,
            "pack_decoracion_cajas": self._codigo_pack_cajas_seleccionado() if decoracion_cajas_activa else "NINGUNO",
            "portada_pagina_completa": bool(self.portada_pagina_completa_var.get()),
            "portada_modo_ajuste": cfg.MODOS_AJUSTE_PORTADA_DISPONIBLES.get(self.portada_modo_ajuste_var.get(), "CUBRIR"),
        }
        self.resultado["valor"] = {
            "entrada": entrada,
            "salida": salida,
            "configuracion_visual": configuracion_visual,
            "configuracion_documento": configuracion_documento,
            "titulo": self.titulo_var.get().strip(),
            "subtitulo": self.subtitulo_var.get().strip(),
            "autor": self.autor_var.get().strip(),
            "imagen_portada": imagen_portada,
        }
        if self.accion_aceptar is not None:
            self._establecer_estado_controles_generacion(generando=True)
            self._establecer_estado_operacion("Generando PDF...", color="#1E5631")
            self.raiz.update_idletasks()
            try:
                self.accion_aceptar(dict(self.resultado["valor"]))
            except Exception as error:
                self._establecer_estado_operacion("No se pudo generar el PDF. Revisa los datos e inténtalo de nuevo.", color="#7A1C1C")
                self.messagebox.showerror("Error al generar el PDF", str(error))
            else:
                self._establecer_estado_operacion("PDF generado correctamente. Puedes cambiar opciones y volver a generar si lo necesitas.", color="#1E5631")
            finally:
                self._establecer_estado_controles_generacion(generando=False)
            return
        self.raiz.quit()

    def ajustar_tamano_ventana(self):
        self.raiz.update_idletasks()
        ancho_pantalla = self.raiz.winfo_screenwidth()
        alto_pantalla = self.raiz.winfo_screenheight()
        ancho_requerido = max(self.ancho_ventana_minimo, self.raiz.winfo_reqwidth())
        alto_requerido = max(self.alto_ventana_minimo, self.raiz.winfo_reqheight())
        ancho_objetivo = min(max(self.ancho_ventana_objetivo, ancho_requerido), ancho_pantalla)
        alto_objetivo = min(max(self.alto_ventana_objetivo, alto_requerido), int(alto_pantalla * 0.9))
        x_actual = self.raiz.winfo_x()
        y_actual = self.raiz.winfo_y()
        ancho_actual = max(1, self.raiz.winfo_width())
        alto_actual = max(1, self.raiz.winfo_height())
        centro_x = x_actual + (ancho_actual // 2)
        centro_y = y_actual + (alto_actual // 2)
        x_objetivo = max(0, min(centro_x - (ancho_objetivo // 2), ancho_pantalla - ancho_objetivo))
        y_objetivo = max(0, min(centro_y - (alto_objetivo // 2), alto_pantalla - alto_objetivo))
        self.raiz.geometry(f"{ancho_objetivo}x{alto_objetivo}+{x_objetivo}+{y_objetivo}")


def pedir_configuracion_interactiva(configuracion_inicial, configuracion_documento_inicial, titulo_inicial="", subtitulo_inicial="", autor_inicial="", portada_inicial="", entrada_inicial="", salida_inicial="", accion_aceptar=None):
    dialogo = DialogoConfiguracionInteractiva(configuracion_inicial, configuracion_documento_inicial, titulo_inicial=titulo_inicial, subtitulo_inicial=subtitulo_inicial, autor_inicial=autor_inicial, portada_inicial=portada_inicial, entrada_inicial=entrada_inicial, salida_inicial=salida_inicial, accion_aceptar=accion_aceptar)
    return dialogo.ejecutar()

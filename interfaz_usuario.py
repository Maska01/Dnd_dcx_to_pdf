import os
from pathlib import Path

from PIL import Image as PILImage, ImageTk
from reportlab.lib.colors import HexColor

import configuracion_pdf as cfg


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
    def __init__(self, configuracion_inicial, configuracion_documento_inicial, titulo_inicial="", subtitulo_inicial="", autor_inicial="", portada_inicial="", entrada_inicial="", salida_inicial=""):
        self.configuracion_inicial = dict(configuracion_inicial)
        self.configuracion_documento_inicial = dict(configuracion_documento_inicial)
        self.titulo_inicial = titulo_inicial or ""
        self.subtitulo_inicial = subtitulo_inicial or ""
        self.autor_inicial = autor_inicial or ""
        self.portada_inicial = portada_inicial or ""
        self.entrada_inicial = str(entrada_inicial or "").strip()
        self.salida_inicial = str(salida_inicial or "").strip()
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
        self.tamano_pagina_var = None
        self.fuente_titulo_var = None
        self.fuente_texto_var = None
        self.margen_var = None
        self.combo_margen = None
        self.etiqueta_rango_margen = None
        self.ancho_pagina_var = None
        self.alto_pagina_var = None
        self.adornos_habilitados_var = None
        self.estilo_adorno_var = None
        self.imagen_adorno_var = None
        self.combo_estilo_adorno = None
        self.entrada_imagen_adorno = None
        self.boton_imagen_adorno = None
        self.canvas_preview_adorno = None
        self.preview_adorno_imagen = None
        self.etiqueta_estado_adorno = None
        self.boton_cancelar = None
        self.boton_continuar = None
        self.boton_regresar = None
        self.boton_aceptar = None
        self.boton_restablecer = None
        self.ultima_salida_sugerida = ""
        self.pagina_actual = "archivos"
        self.margen_sin_adornos_guardado = None
        self.margen_con_adornos_guardado = None
        self.adornos_activos_previos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        self.ancho_ventana_objetivo = 980
        self.alto_ventana_objetivo = 700
        self.ancho_ventana_minimo = 860
        self.alto_ventana_minimo = 620

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
        alto_objetivo = min(700, max(620, alto_pantalla - 120))
        ancho_minimo = min(ancho_objetivo, max(760, ancho_pantalla - 140))
        alto_minimo = min(alto_objetivo, max(560, alto_pantalla - 180))
        self.ancho_ventana_objetivo = ancho_objetivo
        self.alto_ventana_objetivo = alto_objetivo
        self.ancho_ventana_minimo = ancho_minimo
        self.alto_ventana_minimo = alto_minimo

    def _construir_interfaz(self):
        contenedor = self.tk.Frame(self.raiz, padx=14, pady=14)
        contenedor.pack(fill="both", expand=True)
        self._configurar_estilo_notebook()
        interior = self.tk.Frame(contenedor)
        interior.pack(fill="both", expand=True)
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
        estilo.configure("MenuNotebook.TNotebook.Tab", padding=(16, 8))
        estilo.configure("Primario.TButton", padding=(14, 8), font=("Segoe UI", 9, "bold"))
        estilo.configure("Secundario.TButton", padding=(10, 8))

    def encabezado(self, interior):
        encabezado_frame = self.tk.Frame(interior, padx=4, pady=4)
        encabezado_frame.pack(fill="x", pady=(0, 10))
        self.titulo_encabezado = self.tk.Label(encabezado_frame, text="Personaliza tu PDF antes de generarlo", font=("Segoe UI", 16, "bold"), anchor="w")
        self.titulo_encabezado.pack(fill="x")
        self.descripcion_encabezado = self.tk.Label(encabezado_frame, text="Primero elige una entrada `.docx` y una salida `.pdf` válidas. Después podrás continuar a la personalización.", justify="left", wraplength=860, anchor="w")
        self.descripcion_encabezado.pack(fill="x", pady=(4, 0))

    def _construir_bloque_archivos(self, interior):
        archivos_frame = self.tk.LabelFrame(interior, text="Archivos", padx=10, pady=10)
        archivos_frame.pack(fill="x", pady=(0, 10))
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
        resumen_frame = self.tk.LabelFrame(interior, text="Rutas seleccionadas", padx=10, pady=10)
        resumen_frame.pack(fill="x", pady=(0, 10))
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
        pestana_general = self.tk.Frame(notebook, padx=14, pady=14)
        pestana_decoracion = self.tk.Frame(notebook, padx=14, pady=14)
        pestana_colores_base = self.tk.Frame(notebook, padx=14, pady=14)
        pestana_colores_cajas = self.tk.Frame(notebook, padx=14, pady=14)
        pestana_colores_personajes = self.tk.Frame(notebook, padx=14, pady=14)
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
            text="Controla aquí las florituras y marcos decorativos del documento. Puedes usar un estilo predefinido o un PNG transparente personalizado.",
            anchor="w",
            justify="left",
            wraplength=780,
        )
        descripcion.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._construir_bloque_adornos(contenedor, fila=1)

    def _construir_bloque_portada(self, panel_superior):
        titulo_frame = self.tk.LabelFrame(panel_superior, text="Portada y metadatos", padx=10, pady=10)
        titulo_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.titulo_var = self.tk.StringVar(value=self.titulo_inicial)
        self.subtitulo_var = self.tk.StringVar(value=self.subtitulo_inicial)
        self.autor_var = self.tk.StringVar(value=self.autor_inicial)
        portada_explicita = bool(self.portada_inicial and self.portada_inicial != cfg.IMAGEN_PORTADA_PREDETERMINADA)
        self.portada_habilitada_var = self.tk.BooleanVar(value=portada_explicita)
        self.portada_var = self.tk.StringVar(value=self.portada_inicial if portada_explicita else "")
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
        self.etiqueta_ayuda_portada = self.tk.Label(titulo_frame, text="", anchor="w", justify="left", wraplength=720, fg="#5F5F5F")
        self.etiqueta_ayuda_portada.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        titulo_frame.columnconfigure(1, weight=1)
        self.actualizar_estado_portada()

    def _construir_bloque_documento(self, panel_superior):
        documento_frame = self.tk.LabelFrame(panel_superior, text="Página, fuentes y márgenes", padx=10, pady=10)
        documento_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
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
        self.etiqueta_ayuda_tamano = self.tk.Label(documento_frame, text="", anchor="w", justify="left", wraplength=520, fg="#5F5F5F")
        self.etiqueta_ayuda_tamano.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(6, 0))
        self.margen_var.trace_add("write", self._registrar_margen_seleccionado)
        self.tamano_pagina_var.trace_add("write", self.actualizar_estado_tamano_personalizado)
        self.actualizar_estado_tamano_personalizado()
        self._actualizar_etiqueta_rango_margen()

    def _construir_bloque_adornos(self, parent, fila=0):
        adornos_frame = self.tk.LabelFrame(parent, text="Adornos de margen", padx=10, pady=10)
        adornos_frame.grid(row=fila, column=0, sticky="nsew")

        adornos_activos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        estilo_inicial = cfg.normalizar_estilo_adorno_margen(self.configuracion_documento_inicial.get("estilo_adorno_margen", cfg.ESTILO_ADORNO_MARGEN))
        imagen_inicial = str(self.configuracion_documento_inicial.get("imagen_adorno_margen", "") or "").strip()

        self.adornos_habilitados_var = self.tk.BooleanVar(value=adornos_activos)
        self.estilo_adorno_var = self.tk.StringVar(value=cfg.obtener_etiqueta_estilo_adorno_margen(estilo_inicial))
        self.imagen_adorno_var = self.tk.StringVar(value=imagen_inicial)

        self.tk.Checkbutton(adornos_frame, text="Activar florituras en los márgenes", variable=self.adornos_habilitados_var, command=self.actualizar_estado_adornos).grid(row=0, column=0, columnspan=2, sticky="w")
        self.tk.Label(adornos_frame, text="Estilo").grid(row=1, column=0, sticky="w", pady=(8, 3))
        self.combo_estilo_adorno = self.ttk.Combobox(adornos_frame, textvariable=self.estilo_adorno_var, values=list(cfg.ESTILOS_ADORNO_MARGEN_DISPONIBLES.keys()), state="readonly", width=24)
        self.combo_estilo_adorno.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 3))
        self.combo_estilo_adorno.bind("<<ComboboxSelected>>", lambda _evento: self.actualizar_estado_adornos())

        self.tk.Label(adornos_frame, text="PNG personalizado").grid(row=2, column=0, sticky="w", pady=3)
        self.entrada_imagen_adorno = self.tk.Entry(adornos_frame, textvariable=self.imagen_adorno_var, width=42, state="readonly")
        self.entrada_imagen_adorno.grid(row=2, column=1, sticky="ew", padx=(8, 8), pady=3)
        self.boton_imagen_adorno = self.tk.Button(adornos_frame, text="Elegir PNG...", command=self.elegir_imagen_adorno)
        self.boton_imagen_adorno.grid(row=2, column=2, sticky="w", pady=3)

        ayuda = self.tk.Label(
            adornos_frame,
            text="Usa presets para un marco rápido o un PNG transparente ya preparado como borde completo de página.",
            anchor="w",
            justify="left",
            wraplength=470,
        )
        ayuda.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        self.etiqueta_estado_adorno = self.tk.Label(adornos_frame, text="", anchor="w", justify="left", wraplength=470, fg="#5F5F5F")
        self.etiqueta_estado_adorno.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(6, 0))

        preview_frame = self.tk.Frame(adornos_frame, padx=8)
        preview_frame.grid(row=0, column=3, rowspan=5, sticky="ne", padx=(16, 0))
        self.tk.Label(preview_frame, text="Vista previa", anchor="w").pack(fill="x")
        self.canvas_preview_adorno = self.tk.Canvas(preview_frame, width=180, height=120, bg="#FFFFFF", highlightthickness=1, highlightbackground="#C8BBA8")
        self.canvas_preview_adorno.pack(pady=(6, 0))

        adornos_frame.columnconfigure(1, weight=1)
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
        botones = self.tk.Frame(contenedor, padx=12, pady=12)
        botones.pack(fill="x")
        acciones_izquierda = self.tk.Frame(botones)
        acciones_izquierda.pack(side="left")
        acciones_derecha = self.tk.Frame(botones)
        acciones_derecha.pack(side="right")

        self.boton_restablecer = self.ttk.Button(acciones_izquierda, text="Restablecer valores", width=18, style="Secundario.TButton", command=self.restablecer_valores)
        self.boton_regresar = self.ttk.Button(acciones_izquierda, text="Regresar", width=12, style="Secundario.TButton", command=self.regresar_a_archivos)

        self.boton_cancelar = self.ttk.Button(acciones_derecha, text="Cancelar", width=12, style="Secundario.TButton", command=self.cancelar)
        self.boton_continuar = self.ttk.Button(acciones_derecha, text="Continuar", width=15, style="Primario.TButton", command=self.continuar_a_personalizacion)
        self.boton_aceptar = self.ttk.Button(acciones_derecha, text="Aceptar", width=15, style="Primario.TButton", command=self.aceptar)

    def actualizar_preview(self, clave):
        valor = cfg._normalizar_color_hex(self.variables_color[clave].get(), self.configuracion_inicial[clave])
        self.variables_color[clave].set(valor)
        self.vistas_previas[clave].configure(bg=valor)

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
        self.ajustar_tamano_ventana()

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
        self.ajustar_tamano_ventana()

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
        estilo_personalizado = self._codigo_estilo_adorno_seleccionado() == "PERSONALIZADO"
        self._sincronizar_margen_con_adornos()
        self._actualizar_opciones_margen()
        self._actualizar_etiqueta_rango_margen()
        if self.combo_estilo_adorno is not None:
            self.combo_estilo_adorno.configure(state="readonly" if adornos_activos else "disabled")
        if self.boton_imagen_adorno is not None:
            self.boton_imagen_adorno.configure(state="normal" if adornos_activos and estilo_personalizado else "disabled")
        if self.entrada_imagen_adorno is not None:
            self.entrada_imagen_adorno.configure(state="readonly")
        if self.etiqueta_estado_adorno is not None:
            if not adornos_activos:
                texto_estado = "Los adornos están desactivados. Puedes activarlos más tarde sin perder el PNG o el preset que ya tengas elegido."
            elif estilo_personalizado:
                if self.imagen_adorno_var.get().strip():
                    texto_estado = "Se usará el PNG seleccionado como borde completo de página. Conviene dejar el centro transparente para no tapar el contenido."
                else:
                    texto_estado = "Has elegido borde personalizado. Selecciona un PNG transparente para completar esta opción."
            else:
                texto_estado = f"Se aplicará el preset {self.estilo_adorno_var.get()} y el margen mínimo pasará al rango decorado mientras esté activo."
            self.etiqueta_estado_adorno.configure(text=texto_estado)
        self._actualizar_preview_adornos()

    def _actualizar_preview_adornos(self, *_args):
        if self.canvas_preview_adorno is None:
            return
        canvas = self.canvas_preview_adorno
        canvas.delete("all")
        color_fondo = self.variables_color.get("color_fondo_pagina")
        fondo = color_fondo.get() if color_fondo is not None else "#F7F1E3"
        fondo = cfg._normalizar_color_hex(fondo, "#F7F1E3")
        canvas.create_rectangle(16, 8, 164, 112, fill=fondo, outline="#D4C5AF")

        if not self.adornos_habilitados_var.get():
            canvas.create_text(90, 60, text="Sin adornos", fill="#666666", font=("Segoe UI", 9))
            self.preview_adorno_imagen = None
            return

        estilo = self._codigo_estilo_adorno_seleccionado()
        if estilo == "PERSONALIZADO":
            self._dibujar_preview_adorno_personalizado(canvas)
            return
        if estilo == "FLORAL":
            self._dibujar_preview_adorno_floral(canvas)
            return
        if estilo == "GEOMETRICO":
            self._dibujar_preview_adorno_geometrico(canvas)
            return
        self._dibujar_preview_adorno_clasico(canvas)

    def _dibujar_preview_adorno_personalizado(self, canvas):
        ruta = self.imagen_adorno_var.get().strip()
        if not ruta or not Path(ruta).is_file():
            canvas.create_text(90, 54, text="Selecciona un PNG\ntransparente", fill="#666666", justify="center", font=("Segoe UI", 9))
            canvas.create_rectangle(26, 18, 154, 102, outline="#8B0000", dash=(4, 3))
            self.preview_adorno_imagen = None
            return
        try:
            imagen = PILImage.open(ruta).convert("RGBA")
            imagen.thumbnail((148, 104), PILImage.Resampling.LANCZOS)
            self.preview_adorno_imagen = ImageTk.PhotoImage(imagen)
            canvas.create_image(90, 60, image=self.preview_adorno_imagen)
        except Exception:
            canvas.create_text(90, 60, text="No se pudo cargar\nel PNG", fill="#7A1C1C", justify="center", font=("Segoe UI", 9))
            self.preview_adorno_imagen = None

    @staticmethod
    def _dibujar_preview_adorno_clasico(canvas):
        canvas.create_rectangle(26, 18, 154, 102, outline="#8B0000", width=2)
        canvas.create_rectangle(34, 26, 146, 94, outline="#333333")
        for x, y in [(90, 18), (90, 102), (26, 60), (154, 60)]:
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, outline="#333333")
        for esquina_x, esquina_y, direccion_x, direccion_y in [
            (34, 26, 1, 1),
            (146, 26, -1, 1),
            (34, 94, 1, -1),
            (146, 94, -1, -1),
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
    def _dibujar_preview_adorno_geometrico(canvas):
        canvas.create_rectangle(26, 18, 154, 102, outline="#333333", width=2, dash=(5, 3))
        for x1, y1, x2, y2 in [
            (26, 18, 44, 18), (26, 18, 26, 36),
            (154, 18, 136, 18), (154, 18, 154, 36),
            (26, 102, 44, 102), (26, 102, 26, 84),
            (154, 102, 136, 102), (154, 102, 154, 84),
        ]:
            canvas.create_line(x1, y1, x2, y2, fill="#8B0000", width=2)
        for centro_x, centro_y in [(38, 30), (142, 30), (38, 90), (142, 90)]:
            canvas.create_line(centro_x, centro_y - 5, centro_x + 5, centro_y, fill="#8B0000")
            canvas.create_line(centro_x + 5, centro_y, centro_x, centro_y + 5, fill="#8B0000")
            canvas.create_line(centro_x, centro_y + 5, centro_x - 5, centro_y, fill="#8B0000")
            canvas.create_line(centro_x - 5, centro_y, centro_x, centro_y - 5, fill="#8B0000")
            canvas.create_line(centro_x - 2, centro_y, centro_x + 2, centro_y, fill="#8B0000")
            canvas.create_line(centro_x, centro_y - 2, centro_x, centro_y + 2, fill="#8B0000")
            canvas.create_oval(centro_x - 1, centro_y - 1, centro_x + 1, centro_y + 1, outline="#8B0000")
        for centro_x, centro_y in [(26, 60), (154, 60), (90, 18), (90, 102)]:
            canvas.create_line(centro_x - 7, centro_y, centro_x, centro_y - 7, fill="#8B0000")
            canvas.create_line(centro_x, centro_y - 7, centro_x + 7, centro_y, fill="#8B0000")
            canvas.create_line(centro_x + 7, centro_y, centro_x, centro_y + 7, fill="#8B0000")
            canvas.create_line(centro_x, centro_y + 7, centro_x - 7, centro_y, fill="#8B0000")
            canvas.create_oval(centro_x - 1.2, centro_y - 1.2, centro_x + 1.2, centro_y + 1.2, outline="#8B0000")

    @staticmethod
    def _dibujar_preview_adorno_floral(canvas):
        canvas.create_rectangle(28, 20, 152, 100, outline="#8B0000", width=1)
        canvas.create_rectangle(35, 27, 145, 93, outline="#333333")

        for puntos in [
            (40, 88, 44, 88, 49, 83, 54, 78),
            (40, 88, 40, 84, 45, 79, 54, 78),
            (140, 88, 136, 88, 131, 83, 126, 78),
            (140, 88, 140, 84, 135, 79, 126, 78),
            (40, 32, 44, 32, 49, 37, 54, 42),
            (40, 32, 40, 36, 45, 41, 54, 42),
            (140, 32, 136, 32, 131, 37, 126, 42),
            (140, 32, 140, 36, 135, 41, 126, 42),
        ]:
            canvas.create_line(*puntos, smooth=True, fill="#333333")

        canvas.create_line(42, 34, 50, 42, fill="#333333")
        canvas.create_line(138, 34, 130, 42, fill="#333333")
        canvas.create_line(42, 86, 50, 78, fill="#333333")
        canvas.create_line(138, 86, 130, 78, fill="#333333")
        for x, y in [(47, 39), (133, 39), (47, 81), (133, 81)]:
            canvas.create_oval(x - 1.5, y - 1.5, x + 1.5, y + 1.5, outline="#333333")

        canvas.create_line(72, 20, 78, 20, 84, 13, 90, 17, smooth=True, fill="#333333")
        canvas.create_line(108, 20, 102, 20, 96, 13, 90, 17, smooth=True, fill="#333333")
        canvas.create_line(79, 24, 84, 16, 88, 15, 90, 21, smooth=True, fill="#333333")
        canvas.create_line(101, 24, 96, 16, 92, 15, 90, 21, smooth=True, fill="#333333")
        canvas.create_oval(88.5, 19.5, 91.5, 22.5, outline="#333333")

        canvas.create_line(72, 100, 78, 100, 84, 107, 90, 103, smooth=True, fill="#333333")
        canvas.create_line(108, 100, 102, 100, 96, 107, 90, 103, smooth=True, fill="#333333")
        canvas.create_line(79, 96, 84, 104, 88, 105, 90, 99, smooth=True, fill="#333333")
        canvas.create_line(101, 96, 96, 104, 92, 105, 90, 99, smooth=True, fill="#333333")
        canvas.create_oval(88.5, 97.5, 91.5, 100.5, outline="#333333")

        canvas.create_line(28, 60, 36, 60, fill="#333333")
        canvas.create_line(152, 60, 144, 60, fill="#333333")
        canvas.create_oval(32, 58.5, 35, 61.5, outline="#333333")
        canvas.create_oval(145, 58.5, 148, 61.5, outline="#333333")

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
        if self.etiqueta_ayuda_portada is not None:
            ruta_portada = self.portada_var.get().strip()
            if self.portada_habilitada_var.get():
                if ruta_portada:
                    texto = "La portada está activa y usará la imagen seleccionada. Si la desactivas, la ruta se conservará por si quieres reactivarla luego."
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
        self._inicializar_estado_margenes()
        self._actualizar_opciones_margen()
        portada_explicita = bool(self.portada_inicial and self.portada_inicial != cfg.IMAGEN_PORTADA_PREDETERMINADA)
        self.portada_habilitada_var.set(portada_explicita)
        self.portada_var.set(self.portada_inicial if portada_explicita else "")
        self.actualizar_estado_portada()
        self.actualizar_estado_tamano_personalizado()
        self.actualizar_estado_adornos()

    def cancelar(self):
        self.resultado["valor"] = None
        self.raiz.quit()

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
        self.raiz.quit()

    def ajustar_tamano_ventana(self):
        self.raiz.update_idletasks()
        ancho_objetivo = min(self.ancho_ventana_objetivo, self.raiz.winfo_screenwidth())
        alto_objetivo = min(self.alto_ventana_objetivo, int(self.raiz.winfo_screenheight() * 0.9))
        ancho_pantalla = self.raiz.winfo_screenwidth()
        x_actual = self.raiz.winfo_x()
        y_actual = self.raiz.winfo_y()
        ancho_actual = max(1, self.raiz.winfo_width())
        alto_actual = max(1, self.raiz.winfo_height())
        centro_x = x_actual + (ancho_actual // 2)
        centro_y = y_actual + (alto_actual // 2)
        x_objetivo = max(0, min(centro_x - (ancho_objetivo // 2), ancho_pantalla - ancho_objetivo))
        y_objetivo = max(0, min(centro_y - (alto_objetivo // 2), self.raiz.winfo_screenheight() - alto_objetivo))
        self.raiz.geometry(f"{ancho_objetivo}x{alto_objetivo}+{x_objetivo}+{y_objetivo}")


def pedir_configuracion_interactiva(configuracion_inicial, configuracion_documento_inicial, titulo_inicial="", subtitulo_inicial="", autor_inicial="", portada_inicial="", entrada_inicial="", salida_inicial=""):
    dialogo = DialogoConfiguracionInteractiva(configuracion_inicial, configuracion_documento_inicial, titulo_inicial=titulo_inicial, subtitulo_inicial=subtitulo_inicial, autor_inicial=autor_inicial, portada_inicial=portada_inicial, entrada_inicial=entrada_inicial, salida_inicial=salida_inicial)
    return dialogo.ejecutar()

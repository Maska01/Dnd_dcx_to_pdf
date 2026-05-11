import os
from pathlib import Path

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
    def __init__(self, configuracion_inicial, configuracion_documento_inicial, titulo_inicial="", subtitulo_inicial="", autor_inicial="", portada_inicial=""):
        self.configuracion_inicial = dict(configuracion_inicial)
        self.configuracion_documento_inicial = dict(configuracion_documento_inicial)
        self.titulo_inicial = titulo_inicial or ""
        self.subtitulo_inicial = subtitulo_inicial or ""
        self.autor_inicial = autor_inicial or ""
        self.portada_inicial = portada_inicial or ""
        self.resultado = {"valor": None}
        self.tk = None
        self.ttk = None
        self.colorchooser = None
        self.filedialog = None
        self.messagebox = None
        self.raiz = None
        self.variables_color = {}
        self.vistas_previas = {}

    def ejecutar(self):
        if not self._importar_tkinter():
            print("⚠️  tkinter no está disponible; se omite el menú interactivo.")
            return {
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
        self.raiz.geometry("1320x680")
        self.raiz.minsize(1080, 620)
        self.raiz.attributes("-topmost", True)

    def _construir_interfaz(self):
        contenedor = self.tk.Frame(self.raiz, padx=14, pady=14)
        contenedor.pack(fill="both", expand=True)
        self._configurar_estilo_notebook()
        interior = self.tk.Frame(contenedor)
        interior.pack(fill="both", expand=True)
        self.variables_color = {clave: self.tk.StringVar(value=valor) for clave, valor in self.configuracion_inicial.items()}
        self.encabezado(interior)
        notebook, pestana_general, pestana_colores_base, pestana_colores_cajas, pestana_colores_personajes = self._crear_notebook(interior)
        self._construir_pestana_general(pestana_general)
        self._construir_pestanas_colores(pestana_colores_base, pestana_colores_cajas, pestana_colores_personajes)
        self._construir_botones(contenedor)

    def _configurar_estilo_notebook(self):
        estilo = self.ttk.Style(self.raiz)
        try:
            estilo.theme_use("vista")
        except Exception:
            pass
        estilo.configure("MenuNotebook.TNotebook", tabposition="n")
        estilo.configure("MenuNotebook.TNotebook.Tab", padding=(16, 8))

    def encabezado(self, interior):
        encabezado_frame = self.tk.Frame(interior, padx=4, pady=4)
        encabezado_frame.pack(fill="x", pady=(0, 10))
        self.tk.Label(encabezado_frame, text="Personaliza tu PDF antes de generarlo", font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x")
        self.tk.Label(encabezado_frame, text="Ajusta metadatos, portada, página, fuentes, márgenes y colores. La disposición se adapta automáticamente hasta 5 columnas para que el menú sea más cómodo.", justify="left", wraplength=1120, anchor="w").pack(fill="x", pady=(4, 0))

    def _crear_notebook(self, interior):
        notebook = self.ttk.Notebook(interior, style="MenuNotebook.TNotebook")
        notebook.pack(fill="both", expand=True)
        pestana_general = self.tk.Frame(notebook, padx=14, pady=14)
        pestana_colores_base = self.tk.Frame(notebook, padx=14, pady=14)
        pestana_colores_cajas = self.tk.Frame(notebook, padx=14, pady=14)
        pestana_colores_personajes = self.tk.Frame(notebook, padx=14, pady=14)
        notebook.add(pestana_general, text="General")
        notebook.add(pestana_colores_base, text="Colores base")
        notebook.add(pestana_colores_cajas, text="Cajas útiles")
        notebook.add(pestana_colores_personajes, text="NPC y combate")
        return notebook, pestana_general, pestana_colores_base, pestana_colores_cajas, pestana_colores_personajes

    def _construir_pestana_general(self, pestana_general):
        panel_superior = self.tk.Frame(pestana_general)
        panel_superior.pack(fill="both", expand=True)
        panel_superior.columnconfigure(0, weight=1, uniform="columna_superior")
        panel_superior.columnconfigure(1, weight=1, uniform="columna_superior")
        self._construir_bloque_portada(panel_superior)
        self._construir_bloque_documento(panel_superior)

    def _construir_bloque_portada(self, panel_superior):
        titulo_frame = self.tk.LabelFrame(panel_superior, text="Portada y metadatos", padx=10, pady=10)
        titulo_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        self.titulo_var = self.tk.StringVar(value=self.titulo_inicial)
        self.subtitulo_var = self.tk.StringVar(value=self.subtitulo_inicial)
        self.autor_var = self.tk.StringVar(value=self.autor_inicial)
        portada_explicita = bool(self.portada_inicial and self.portada_inicial != cfg.IMAGEN_PORTADA_PREDETERMINADA)
        self.portada_habilitada_var = self.tk.BooleanVar(value=portada_explicita)
        self.portada_var = self.tk.StringVar(value=self.portada_inicial if portada_explicita else "")
        self.tk.Label(titulo_frame, text="Título de la aventura (opcional)").grid(row=0, column=0, sticky="w")
        self.tk.Entry(titulo_frame, textvariable=self.titulo_var, width=50).grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)
        self.tk.Label(titulo_frame, text="Subtítulo (opcional)").grid(row=1, column=0, sticky="w")
        self.tk.Entry(titulo_frame, textvariable=self.subtitulo_var, width=50).grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)
        self.tk.Label(titulo_frame, text="Autor (opcional)").grid(row=2, column=0, sticky="w")
        self.tk.Entry(titulo_frame, textvariable=self.autor_var, width=50).grid(row=2, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3)
        self.tk.Checkbutton(titulo_frame, text="Agregar portada", variable=self.portada_habilitada_var, command=self.actualizar_estado_portada).grid(row=3, column=0, sticky="w", pady=(8, 4))
        self.entrada_portada = self.tk.Entry(titulo_frame, textvariable=self.portada_var, width=50, state="readonly")
        self.entrada_portada.grid(row=3, column=1, sticky="ew", padx=(8, 8), pady=(8, 4))
        self.boton_portada = self.tk.Button(titulo_frame, text="Elegir imagen...", command=self.elegir_portada)
        self.boton_portada.grid(row=3, column=2, sticky="w", pady=(8, 4))
        titulo_frame.columnconfigure(1, weight=1)
        self.actualizar_estado_portada()

    def _construir_bloque_documento(self, panel_superior):
        documento_frame = self.tk.LabelFrame(panel_superior, text="Página, fuentes y márgenes", padx=10, pady=10)
        documento_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))
        self.tamano_pagina_var = self.tk.StringVar(value=self.configuracion_documento_inicial.get("tamano_pagina", "A4"))
        self.fuente_titulo_var = self.tk.StringVar(value=self.configuracion_documento_inicial.get("fuente_titulo", cfg.FUENTE_TITULO))
        self.fuente_texto_var = self.tk.StringVar(value=self.configuracion_documento_inicial.get("fuente_texto", cfg.FUENTE_TEXTO))
        self.margen_var = self.tk.StringVar(value=str(self.configuracion_documento_inicial.get("margen_cm", 2.0)))
        self.ancho_pagina_var = self.tk.StringVar(value=str(self.configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)))
        self.alto_pagina_var = self.tk.StringVar(value=str(self.configuracion_documento_inicial.get("alto_pagina_cm", 29.7)))
        self.tk.Label(documento_frame, text="Tamaño de página").grid(row=0, column=0, sticky="w", pady=3)
        self.ttk.Combobox(documento_frame, textvariable=self.tamano_pagina_var, values=[*cfg.TAMANOS_PAGINA_DISPONIBLES.keys(), cfg.OPCION_TAMANO_PERSONALIZADO], state="readonly", width=18).grid(row=0, column=1, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Ancho personalizado (cm)").grid(row=0, column=2, sticky="w", padx=(16, 0), pady=3)
        self.entrada_ancho = self.tk.Entry(documento_frame, textvariable=self.ancho_pagina_var, width=10)
        self.entrada_ancho.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Alto personalizado (cm)").grid(row=1, column=2, sticky="w", padx=(16, 0), pady=3)
        self.entrada_alto = self.tk.Entry(documento_frame, textvariable=self.alto_pagina_var, width=10)
        self.entrada_alto.grid(row=1, column=3, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Fuente de título").grid(row=1, column=0, sticky="w", pady=3)
        self.ttk.Combobox(documento_frame, textvariable=self.fuente_titulo_var, values=cfg.FUENTES_DISPONIBLES, state="readonly", width=28).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Fuente de texto").grid(row=2, column=0, sticky="w", pady=3)
        self.ttk.Combobox(documento_frame, textvariable=self.fuente_texto_var, values=cfg.FUENTES_DISPONIBLES, state="readonly", width=28).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Margen (cm)").grid(row=3, column=0, sticky="w", pady=3)
        self.tk.Entry(documento_frame, textvariable=self.margen_var, width=10).grid(row=3, column=1, sticky="w", padx=(8, 0), pady=3)
        self.tk.Label(documento_frame, text="Rango recomendado: 0.5 a 5.0 cm").grid(row=3, column=2, sticky="w", padx=(8, 0), pady=3)
        self.tamano_pagina_var.trace_add("write", self.actualizar_estado_tamano_personalizado)
        self.actualizar_estado_tamano_personalizado()

    def _construir_pestanas_colores(self, pestana_colores_base, pestana_colores_cajas, pestana_colores_personajes):
        grupos_colores = [("General", [("color_primario", "Títulos"), ("color_secundario", "Texto general"), ("color_fondo_pagina", "Fondo de página")]), ("Caja Consejo para el DM", [("color_azul_texto", "Texto"), ("color_azul_borde", "Borde"), ("color_azul_fondo", "Fondo")]), ("Caja Cita", [("color_ama_texto", "Texto"), ("color_ama_borde", "Borde"), ("color_ama_fondo", "Fondo")]), ("Caja Información adicional", [("color_info_texto", "Texto"), ("color_info_borde", "Borde"), ("color_info_fondo", "Fondo")]), ("Caja NPC", [("color_npc_texto", "Texto"), ("color_npc_borde", "Borde"), ("color_npc_fondo", "Fondo")]), ("Caja Enemigo", [("color_enemigo_texto", "Texto"), ("color_enemigo_borde", "Borde"), ("color_enemigo_fondo", "Fondo")]), ("Caja Aliado", [("color_aliado_texto", "Texto"), ("color_aliado_borde", "Borde"), ("color_aliado_fondo", "Fondo")]), ("Caja Tesoro/Premio", [("color_tesoro_texto", "Texto"), ("color_tesoro_borde", "Borde"), ("color_tesoro_fondo", "Fondo")]), ("Caja Objeto", [("color_objeto_texto", "Texto"), ("color_objeto_borde", "Borde"), ("color_objeto_fondo", "Fondo")])]
        distribucion_pestanas = {"Colores base": ["General", "Caja Consejo para el DM", "Caja Cita"], "Cajas útiles": ["Caja Información adicional", "Caja Tesoro/Premio", "Caja Objeto"], "NPC y combate": ["Caja NPC", "Caja Enemigo", "Caja Aliado"]}
        contenedores = {"Colores base": pestana_colores_base, "Cajas útiles": pestana_colores_cajas, "NPC y combate": pestana_colores_personajes}
        for pestana in contenedores.values():
            pestana.columnconfigure(0, weight=1, uniform="colores_tab")
            pestana.columnconfigure(1, weight=1, uniform="colores_tab")
        for nombre_pestana, nombres_grupos in distribucion_pestanas.items():
            contenedor_tab = contenedores[nombre_pestana]
            for indice_grupo, nombre_grupo in enumerate(nombres_grupos):
                _, campos = next(grupo for grupo in grupos_colores if grupo[0] == nombre_grupo)
                columna = indice_grupo % 2
                fila = indice_grupo // 2
                padding_x = (0, 8) if columna == 0 else (8, 0)
                frame = self.tk.LabelFrame(contenedor_tab, text=nombre_grupo, padx=10, pady=10)
                frame.grid(row=fila, column=columna, sticky="nsew", padx=padding_x, pady=(0, 10))
                for indice, (clave, etiqueta) in enumerate(campos):
                    self.crear_selector_color(frame, indice, clave, etiqueta)
        self.tk.Label(pestana_colores_base, text="Aquí están los colores base del documento y de las cajas más frecuentes.", anchor="w", justify="left").grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        self.tk.Label(pestana_colores_cajas, text="Aquí puedes ajustar información adicional, tesoro/premio y objeto sin mezclarlo con NPC o combate.", anchor="w", justify="left").grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        self.tk.Label(pestana_colores_personajes, text="Los bloques de NPC, enemigo y aliado comparten esta pestaña para ajustes rápidos de escena.", anchor="w", justify="left").grid(row=10, column=0, columnspan=2, sticky="ew", pady=(4, 0))

    def _construir_botones(self, contenedor):
        botones = self.tk.Frame(contenedor, padx=12, pady=10)
        botones.pack(fill="x")
        self.tk.Button(botones, text="Restablecer valores", command=self.restablecer_valores).pack(side="left")
        self.tk.Button(botones, text="Cancelar", command=self.cancelar).pack(side="right", padx=(8, 0))
        self.tk.Button(botones, text="Aceptar", command=self.aceptar).pack(side="right")

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
        self.tk.Entry(parent, textvariable=self.variables_color[clave], width=12, justify="center").grid(row=fila, column=1, sticky="w", pady=4)
        preview = self.tk.Label(parent, width=6, relief="groove", bg=self.variables_color[clave].get())
        preview.grid(row=fila, column=2, padx=6, pady=4)
        self.vistas_previas[clave] = preview
        self.tk.Button(parent, text="Elegir...", command=lambda clave_actual=clave: self.elegir_color(clave_actual)).grid(row=fila, column=3, sticky="w", pady=4)

    def elegir_portada(self):
        ruta = self.filedialog.askopenfilename(title="Selecciona la imagen de portada", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"), ("Todos los archivos", "*.*")])
        if ruta:
            self.portada_var.set(ruta)

    def actualizar_estado_portada(self):
        estado = "normal" if self.portada_habilitada_var.get() else "disabled"
        self.boton_portada.configure(state=estado)
        self.entrada_portada.configure(state="normal" if self.portada_habilitada_var.get() else "readonly")
        if not self.portada_habilitada_var.get():
            self.portada_var.set("")
        self.entrada_portada.configure(state="readonly")

    def actualizar_estado_tamano_personalizado(self, *_args):
        es_personalizado = self.tamano_pagina_var.get().strip().upper() == cfg.OPCION_TAMANO_PERSONALIZADO
        estado = "normal" if es_personalizado else "disabled"
        self.entrada_ancho.configure(state=estado)
        self.entrada_alto.configure(state=estado)

    def restablecer_valores(self):
        for clave, valor in self.configuracion_inicial.items():
            self.variables_color[clave].set(valor)
            self.actualizar_preview(clave)
        self.tamano_pagina_var.set(self.configuracion_documento_inicial.get("tamano_pagina", "A4"))
        self.fuente_titulo_var.set(self.configuracion_documento_inicial.get("fuente_titulo", cfg.FUENTE_TITULO))
        self.fuente_texto_var.set(self.configuracion_documento_inicial.get("fuente_texto", cfg.FUENTE_TEXTO))
        self.margen_var.set(str(self.configuracion_documento_inicial.get("margen_cm", 2.0)))
        self.ancho_pagina_var.set(str(self.configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)))
        self.alto_pagina_var.set(str(self.configuracion_documento_inicial.get("alto_pagina_cm", 29.7)))

    def cancelar(self):
        self.resultado["valor"] = None
        self.raiz.quit()

    def aceptar(self):
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
        try:
            margen_cm = float(str(self.margen_var.get()).replace(",", ".").strip())
        except (TypeError, ValueError):
            self.messagebox.showerror("Margen inválido", "El margen debe ser un número en centímetros.")
            return
        if margen_cm < 0.5 or margen_cm > 5.0:
            self.messagebox.showerror("Margen inválido", "El margen debe estar entre 0.5 y 5.0 cm.")
            return
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
        configuracion_documento = {"tamano_pagina": tamano_pagina, "fuente_titulo": self.fuente_titulo_var.get().strip(), "fuente_texto": self.fuente_texto_var.get().strip(), "margen_cm": margen_cm, "ancho_pagina_cm": ancho_pagina_cm, "alto_pagina_cm": alto_pagina_cm}
        self.resultado["valor"] = {"configuracion_visual": configuracion_visual, "configuracion_documento": configuracion_documento, "titulo": self.titulo_var.get().strip(), "subtitulo": self.subtitulo_var.get().strip(), "autor": self.autor_var.get().strip(), "imagen_portada": imagen_portada}
        self.raiz.quit()

    def ajustar_tamano_ventana(self):
        self.raiz.update_idletasks()
        ancho_objetivo = max(1080, min(1320, self.raiz.winfo_reqwidth() + 24))
        alto_requerido = self.raiz.winfo_reqheight() + 20
        alto_pantalla = int(self.raiz.winfo_screenheight() * 0.9)
        alto_objetivo = max(620, min(alto_requerido, alto_pantalla))
        self.raiz.geometry(f"{ancho_objetivo}x{alto_objetivo}")


def pedir_configuracion_interactiva(configuracion_inicial, configuracion_documento_inicial, titulo_inicial="", subtitulo_inicial="", autor_inicial="", portada_inicial=""):
    dialogo = DialogoConfiguracionInteractiva(configuracion_inicial, configuracion_documento_inicial, titulo_inicial=titulo_inicial, subtitulo_inicial=subtitulo_inicial, autor_inicial=autor_inicial, portada_inicial=portada_inicial)
    return dialogo.ejecutar()

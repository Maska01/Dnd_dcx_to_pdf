import os
from pathlib import Path
import subprocess
import sys

from reportlab.lib.colors import HexColor

from ..core import configuracion_pdf as cfg
from .dialog_state import EstadoDialogoUI
from . import form_blocks
from . import preview_rendering
from . import tab_building
import tkinter.font as tkFont


def _crear_raiz_tk_oculta():
    import tkinter as tk

    raiz = tk.Tk()
    raiz.withdraw()
    raiz.attributes("-topmost", True)
    return raiz

def seleccionar_archivo_dialogo(titulo, tipos_archivo, modo="abrir", archivo_inicial=None):
    try:
        from tkinter import filedialog
    except ImportError:
        print("⚠️  tkinter no está disponible; no se puede abrir el diálogo.")
        return ""
    raiz = _crear_raiz_tk_oculta()
    try:
        if modo == "guardar":
            extension_predeterminada = ""
            if tipos_archivo:
                extension_predeterminada = tipos_archivo[0][1].replace("*", "")
            ruta = filedialog.asksaveasfilename(title=titulo, filetypes=tipos_archivo, defaultextension=extension_predeterminada, initialfile=archivo_inicial)
        else:
            ruta = filedialog.askopenfilename(title=titulo, filetypes=tipos_archivo)
    finally:
        raiz.destroy()
    return ruta or ""


def mostrar_aviso_generacion(titulo, mensaje):
    print(f"ℹ️  {titulo}: {mensaje}")


def abrir_pdf_con_aplicacion_predeterminada(ruta_pdf):
    ruta_pdf = Path(ruta_pdf)
    if not ruta_pdf.is_file():
        raise FileNotFoundError(f"No se encontró el PDF generado: {ruta_pdf}")
    try:
        if hasattr(os, "startfile"):
            os.startfile(str(ruta_pdf))
            return
        comando = ["open", str(ruta_pdf)] if sys.platform == "darwin" else ["xdg-open", str(ruta_pdf)]
        subprocess.Popen(comando)
    except OSError as error:
        raise RuntimeError(f"No se pudo abrir el PDF con la aplicación predeterminada: {ruta_pdf}") from error


def abrir_y_notificar_pdf_generado(ruta_pdf, abridor=None, notificador=None):
    ruta_pdf = Path(ruta_pdf)
    abridor = abridor or abrir_pdf_con_aplicacion_predeterminada
    notificador = notificador or mostrar_aviso_generacion
    abridor(ruta_pdf)
    notificador("PDF generado", f"El PDF se generó correctamente y se abrió con la aplicación predeterminada.\n\nRuta:\n{ruta_pdf}")


class DialogoConfiguracionInteractiva:
    ANCHO_VENTANA_OBJETIVO_BASE = 720
    ALTO_VENTANA_OBJETIVO_BASE = 640
    ANCHO_VENTANA_MINIMO_BASE = 620
    ALTO_VENTANA_MINIMO_BASE = 580
    ANCHO_CONTENIDO_COMPACTO_BASE = 640
    ANCHO_TARJETA_ARCHIVOS_BASE = 700
    COLOR_TEXTO = "#1F1F1F"
    COLOR_EXITO = "#1E5631"
    COLOR_ERROR = "#7A1C1C"
    COLOR_MUTED = "#5F5F5F"
    COLOR_PASO_INACTIVO = "#EFE7DA"
    COLOR_FLECHA_PASOS = "#7A7A7A"

    def __init__(self, configuracion_inicial, configuracion_documento_inicial, titulo_inicial="", subtitulo_inicial="", autor_inicial="", portada_inicial="", entrada_inicial="", salida_inicial="", accion_aceptar=None):
        self.configuracion_inicial = dict(configuracion_inicial)
        self.configuracion_documento_inicial = dict(configuracion_documento_inicial)
        self.columnas_cajas = 3
        self.columnas_npc_combate = 3
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
        self.estado_ui = EstadoDialogoUI()
        self.variables_color = {}
        self.vistas_previas = {}
        self.notebook = None
        self.contenedor_principal = None
        self.interior_principal = None
        self.barra_botones = None
        self.entrada_var = None
        self.salida_var = None
        self.estado_rutas_var = None
        self.descripcion_pasos_var = None
        self.titulo_encabezado = None
        self.descripcion_encabezado = None
        self.etiqueta_paso_archivos = None
        self.etiqueta_paso_personalizacion = None
        self.contenedor_paginas = None
        self.pagina_archivos = None
        self.pagina_personalizacion = None
        self.entrada_archivo = None
        self.salida_archivo = None
        self.estado_rutas_label = None
        self.entrada_portada = None
        self.boton_portada = None
        self.etiqueta_ayuda_portada = None
        self.etiqueta_validacion_portada = None
        self.entrada_ancho = None
        self.entrada_alto = None
        self.etiqueta_ayuda_tamano = None
        self.etiqueta_validacion_tamano = None
        self.etiqueta_validacion_margen = None
        self.resumen_portada_var = None
        self.resumen_documento_var = None
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
        self.ancho_borde_cajas_var = None
        self.espacio_antes_cajas_var = None
        self.espacio_despues_cajas_var = None
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
        self.etiqueta_validacion_adorno = None
        self.boton_cancelar = None
        self.boton_continuar = None
        self.boton_regresar = None
        self.boton_aceptar = None
        self.boton_aceptar_y_abrir = None
        self.boton_restablecer = None
        self.estado_operacion_var = None
        self.etiqueta_estado_operacion = None
        self.ultima_salida_sugerida = ""
        self.pagina_actual = "archivos"
        self.margen_sin_adornos_guardado = None
        self.margen_con_adornos_guardado = None
        self.adornos_activos_previos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        self.ancho_ventana_objetivo = self.ANCHO_VENTANA_OBJETIVO_BASE
        self.alto_ventana_objetivo = self.ALTO_VENTANA_OBJETIVO_BASE
        self.ancho_ventana_minimo = self.ANCHO_VENTANA_MINIMO_BASE
        self.alto_ventana_minimo = self.ALTO_VENTANA_MINIMO_BASE
        self.ancho_contenido_compacto = self.ANCHO_CONTENIDO_COMPACTO_BASE
        self.ancho_tarjeta_archivos = self.ANCHO_TARJETA_ARCHIVOS_BASE
        self.color_superficie = "#F6F2EA"
        self.color_panel = "#FFFDFC"
        self.color_borde_suave = "#D7CEC0"
        self.color_texto_suave = "#6B665D"
        self.color_acento = "#1E5631"

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
        self.raiz.configure(bg=self.color_superficie)
        self._configurar_fuentes_base()
        self._configurar_dimensiones_ventana()
        self.raiz.geometry(f"{self.ancho_ventana_objetivo}x{self.alto_ventana_objetivo}")
        self.raiz.minsize(self.ancho_ventana_minimo, self.alto_ventana_minimo)

    def _configurar_fuentes_base(self):
        self.tituloLabel_font_cnf = tkFont.Font(root=self.raiz, family="Segoe UI", size=13, weight="bold")
        self.subtituloLabel_font_cnf = tkFont.Font(root=self.raiz, family="Segoe UI", size=11, weight="bold")
        self.normalLabel_font_cnf = tkFont.Font(root=self.raiz, family="Segoe UI", size=10)
        self.helperLabel_font_cnf = tkFont.Font(root=self.raiz, family="Segoe UI", size=9)

    def _configurar_dimensiones_ventana(self):
        ancho_pantalla = max(800, int(self.raiz.winfo_screenwidth()))
        alto_pantalla = max(600, int(self.raiz.winfo_screenheight()))
        ancho_objetivo = min(self.ANCHO_VENTANA_OBJETIVO_BASE, max(self.ANCHO_VENTANA_OBJETIVO_BASE - 40, ancho_pantalla - 150))
        alto_objetivo = min(self.ALTO_VENTANA_OBJETIVO_BASE + 100, max(self.ALTO_VENTANA_OBJETIVO_BASE, alto_pantalla - 110))
        ancho_minimo = min(ancho_objetivo, max(self.ANCHO_VENTANA_MINIMO_BASE, ancho_pantalla - 220))
        alto_minimo = min(alto_objetivo, max(self.ALTO_VENTANA_MINIMO_BASE + 40, alto_pantalla - 180))
        self.ancho_ventana_objetivo = ancho_objetivo
        self.alto_ventana_objetivo = alto_objetivo
        self.ancho_ventana_minimo = ancho_minimo
        self.alto_ventana_minimo = alto_minimo

    def _construir_interfaz(self):
        contenedor = self.tk.Frame(self.raiz, padx=8, pady=8, bg=self.color_superficie)
        contenedor.pack(fill="both", expand=True)
        self.contenedor_principal = contenedor
        self._configurar_estilo_notebook()
        interior = self.tk.Frame(contenedor, bg=self.color_superficie)
        interior.pack(fill="both", expand=True)
        self.interior_principal = interior
        self.variables_color = {clave: self.tk.StringVar(value=valor) for clave, valor in self.configuracion_inicial.items()}
        self.encabezado(interior)
        self._construir_indicador_pasos(interior)
        self.contenedor_paginas = self.tk.Frame(interior)
        self.contenedor_paginas.pack(fill="both", expand=True)
        self.pagina_archivos = self.tk.Frame(self.contenedor_paginas)
        self.pagina_personalizacion = self.tk.Frame(self.contenedor_paginas)
        self._construir_pagina_archivos(self.pagina_archivos)
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
        estilo.configure("MenuNotebook.TNotebook.Tab", padding=(10, 5))
        estilo.configure("Primario.TButton", padding=(12, 7), font=("Segoe UI", 9, "bold"))
        estilo.configure("Secundario.TButton", padding=(9, 7))

    def encabezado(self, interior):
        encabezado_frame = self.tk.Frame(interior, padx=2, pady=2, bg=self.color_superficie)
        encabezado_frame.pack(fill="x", pady=(0, 6))
        self.titulo_encabezado = self.tk.Label(encabezado_frame, text="Personaliza tu PDF antes de generarlo", font=("Segoe UI", 16, "bold"), anchor="w", bg=self.color_superficie, fg=self.COLOR_TEXTO)
        self.titulo_encabezado.pack(fill="x")
        self.descripcion_encabezado = self.tk.Label(encabezado_frame, text="Primero elige un `.docx` o `.txt` y un destino `.pdf`. Después ajusta el estilo del documento.", justify="left", wraplength=self.ancho_contenido_compacto, anchor="w", bg=self.color_superficie, fg=self.color_texto_suave)
        self.descripcion_encabezado.pack(fill="x", pady=(4, 0))
        self.tk.Frame(encabezado_frame, height=1, bg=self.color_borde_suave).pack(fill="x", pady=(8, 0))

    def _construir_indicador_pasos(self, interior):
        pasos_frame = self.tk.Frame(interior, padx=4, pady=2, bg=self.color_superficie)
        pasos_frame.pack(fill="x", pady=(0, 6))
        pasos_frame.columnconfigure(0, weight=0)
        pasos_frame.columnconfigure(1, weight=0)
        pasos_frame.columnconfigure(2, weight=0)
        pasos_frame.columnconfigure(3, weight=1)
        self.etiqueta_paso_archivos = self.tk.Label(pasos_frame, text="1. Archivos", padx=10, pady=4, relief="solid", borderwidth=1)
        self.etiqueta_paso_archivos.grid(row=0, column=0, sticky="w")
        self.tk.Label(pasos_frame, text="→", fg=self.COLOR_FLECHA_PASOS, bg=self.color_superficie).grid(row=0, column=1, padx=8)
        self.etiqueta_paso_personalizacion = self.tk.Label(pasos_frame, text="2. Personalización", padx=10, pady=4, relief="solid", borderwidth=1)
        self.etiqueta_paso_personalizacion.grid(row=0, column=2, sticky="w")
        self.descripcion_pasos_var = self.tk.StringVar(value="Paso 1 de 2 · Elige entrada y salida.")
        self.tk.Label(pasos_frame, textvariable=self.descripcion_pasos_var, anchor="e", justify="right", fg=self.color_texto_suave, bg=self.color_superficie).grid(row=0, column=3, sticky="e")
        self._actualizar_indicador_pasos()

    def _actualizar_indicador_pasos(self):
        estilos = {
            True: {"bg": self.color_acento, "fg": "#FFFFFF", "font": ("Segoe UI", 9, "bold"), "relief": "solid", "borderwidth": 1},
            False: {"bg": self.COLOR_PASO_INACTIVO, "fg": self.color_texto_suave, "font": ("Segoe UI", 9), "relief": "solid", "borderwidth": 1},
        }
        paso_archivos_activo = self.pagina_actual == "archivos"
        paso_personalizacion_activo = self.pagina_actual == "personalizacion"
        if self.etiqueta_paso_archivos is not None:
            self.etiqueta_paso_archivos.configure(**estilos[paso_archivos_activo])
        if self.etiqueta_paso_personalizacion is not None:
            self.etiqueta_paso_personalizacion.configure(**estilos[paso_personalizacion_activo])
        if self.descripcion_pasos_var is not None:
            if paso_archivos_activo:
                self.descripcion_pasos_var.set("Paso 1 de 2 · Elige entrada y salida.")
            else:
                self.descripcion_pasos_var.set("Paso 2 de 2 · Ajusta el estilo antes de generar.")

    def _construir_panel_dos_columnas(self, parent, construir_columna_izquierda, construir_columna_derecha, con_row_inferior=False, construir_row_inferior=None):
        panel_superior = self.tk.Frame(parent)
        panel_superior.pack(fill="both", expand=True, anchor="n")
        panel_superior.columnconfigure(0, weight=2)
        panel_superior.columnconfigure(1, weight=1)
        if con_row_inferior:
            panel_superior.rowconfigure(1, weight=1)

        columna_izquierda = self.tk.Frame(panel_superior)
        columna_izquierda.grid(row=0, column=0, sticky="new", padx=(0, 4))
        columna_izquierda.columnconfigure(0, weight=1)
        columna_derecha = self.tk.Frame(panel_superior)
        columna_derecha.grid(row=0, column=1, sticky="nsew")
        columna_derecha.columnconfigure(0, weight=1)

        construir_columna_izquierda(columna_izquierda)
        construir_columna_derecha(columna_derecha)

        if con_row_inferior and construir_row_inferior is not None:
            row_inferior = self.tk.Frame(panel_superior)
            row_inferior.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(4, 0), pady=(2, 0))
            construir_row_inferior(row_inferior)

    def _agregar_descripcion_seccion(self, parent, texto, row, columnspan, wraplength):
        return self.tk.Label(
            parent,
            text=texto,
            font=self.normalLabel_font_cnf,
            anchor="w",
            justify="left",
            wraplength=wraplength,
        ).grid(row=row, column=0, columnspan=columnspan, sticky="ew", pady=(0, 8))

    def _asignar_estado_ui(self, grupo, nombre, valor):
        setattr(getattr(self.estado_ui, grupo), nombre, valor)
        setattr(self, nombre, valor)
        return valor

    def _construir_bloque_archivos(self, interior):
        form_blocks.construir_bloque_archivos(self, interior)

    def _construir_pagina_archivos(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        parent.grid_columnconfigure(1, weight=0)
        parent.grid_columnconfigure(2, weight=1)

        contenedor_centrado = self.tk.Frame(parent, width=self.ancho_tarjeta_archivos, bg=self.color_superficie)
        contenedor_centrado.grid(row=1, column=1, sticky="n")
        contenedor_centrado.grid_propagate(False)

        tarjeta_archivos = self.tk.Frame(
            contenedor_centrado,
            highlightthickness=1,
            highlightbackground=self.color_borde_suave,
            highlightcolor=self.color_borde_suave,
            padx=10,
            pady=10,
        )
        tarjeta_archivos.pack(fill="x")
        self._construir_bloque_archivos(tarjeta_archivos)

    def _construir_pagina_personalizacion(self, interior):
        tab_building.construir_pagina_personalizacion(self, interior)

    def _crear_notebook(self, interior):
        return tab_building.crear_notebook(self, interior)
        

    def _construir_pestana_portada_metadatos(self, pestana_portada_metadatos):
        tab_building.construir_pestana_portada_metadatos(self, pestana_portada_metadatos)

    def _construir_pestana_documento(self, pestana_documento):
        tab_building.construir_pestana_documento(self, pestana_documento)

    def _construir_pestana_margenes(self, pestana_margenes):
        tab_building.construir_pestana_margenes(self, pestana_margenes)

    def _construir_pestana_cajas(self, pestana_cajas):
        tab_building.construir_pestana_cajas(self, pestana_cajas)

    def _construir_bloque_portada(self, panel_superior):
        form_blocks.construir_bloque_portada(self, panel_superior)

    def _construir_panel_resumen_portada(self, parent):
        form_blocks.construir_panel_resumen_portada(self, parent)

    def _construir_panel_ayuda_portada(self, parent):
        form_blocks.construir_panel_ayuda_portada(self, parent)

    def _actualizar_resumen_portada(self):
        portada = self.estado_ui.portada
        if portada.resumen_portada_var is None:
            return
        titulo = portada.titulo_var.get().strip() if portada.titulo_var is not None else ""
        subtitulo = portada.subtitulo_var.get().strip() if portada.subtitulo_var is not None else ""
        autor = portada.autor_var.get().strip() if portada.autor_var is not None else ""
        portada_activa = bool(portada.portada_habilitada_var and portada.portada_habilitada_var.get())
        portada_texto = "Activa" if portada_activa else "Desactivada"
        if portada_activa and portada.portada_pagina_completa_var is not None and portada.portada_pagina_completa_var.get():
            portada_texto += " · página completa"
        lineas = [
            f"Título: {titulo or 'Sin título'}",
            f"Subtítulo: {subtitulo or 'Sin subtítulo'}",
            f"Autor: {autor or 'Sin autor'}",
            f"Portada: {portada_texto}",
        ]
        if portada.portada_var is not None and portada.portada_var.get().strip():
            lineas.append("Imagen seleccionada correctamente.")
        self._establecer_resumen(portada.resumen_portada_var, lineas)

    def _construir_bloque_documento(self, panel_superior):
        form_blocks.construir_bloque_documento(self, panel_superior)

    def _construir_panel_resumen_documento(self, parent):
        form_blocks.construir_panel_resumen_documento(self, parent)

    def _agregar_texto_resumen(self, parent, variable_texto, wraplength):
        return self.tk.Label(
            parent,
            textvariable=variable_texto,
            anchor="nw",
            justify="left",
            wraplength=wraplength,
            fg=self.color_texto_suave,
            font=self.normalLabel_font_cnf,
        ).pack(fill="both", expand=True)

    def _agregar_lista_sugerencias(self, parent, mensajes, wraplength):
        for mensaje in mensajes:
            self.tk.Label(
                parent,
                text=f"• {mensaje}",
                anchor="w",
                justify="left",
                wraplength=wraplength,
                fg=self.color_texto_suave,
                font=self.normalLabel_font_cnf,
            ).pack(fill="x", pady=2)

    @staticmethod
    def _formatear_resumen(lineas):
        return "\n\n".join(lineas)

    def _establecer_resumen(self, variable_texto, lineas):
        variable_texto.set(self._formatear_resumen(lineas))

    @staticmethod
    def _estado_portada(portada_habilitada, portada_pagina_completa, ruta_portada, ruta_existente):
        if not portada_habilitada:
            return "Portada desactivada. Puedes activarla más tarde sin perder la imagen seleccionada.", "#5F5F5F"
        if not ruta_portada:
            return "Falta seleccionar la imagen de portada.", "#7A1C1C"
        if not ruta_existente:
            return "La imagen de portada ya no existe en esa ruta.", "#7A1C1C"
        if portada_pagina_completa:
            return "Portada lista para generarse con la imagen seleccionada.", "#1E5631"
        return "Portada lista para generarse con la imagen seleccionada.", "#1E5631"

    @staticmethod
    def _estado_tamano_personalizado(tamano, ancho, alto):
        if tamano.upper() != cfg.OPCION_TAMANO_PERSONALIZADO:
            return f"Se usará el tamaño de página {tamano}.", "#1E5631"
        try:
            ancho_valor = float(str(ancho).replace(",", ".").strip())
            alto_valor = float(str(alto).replace(",", ".").strip())
        except (AttributeError, TypeError, ValueError):
            return "El ancho y el alto personalizados deben ser números válidos.", "#7A1C1C"
        if not (5.0 <= ancho_valor <= 100.0 and 5.0 <= alto_valor <= 100.0):
            return "El tamaño personalizado debe quedar entre 5 y 100 cm en ambos lados.", "#7A1C1C"
        return f"Página personalizada lista: {ancho_valor:.1f} × {alto_valor:.1f} cm.", "#1E5631"

    def _actualizar_resumen_documento(self):
        documento = self.estado_ui.documento
        if documento.resumen_documento_var is None:
            return
        tamano = documento.tamano_pagina_var.get().strip() if documento.tamano_pagina_var is not None else "A4"
        margen = documento.margen_var.get().strip() if documento.margen_var is not None else "2.0"
        fuente_titulo = documento.fuente_titulo_var.get().strip() if documento.fuente_titulo_var is not None else cfg.FUENTE_TITULO
        fuente_texto = documento.fuente_texto_var.get().strip() if documento.fuente_texto_var is not None else cfg.FUENTE_TEXTO
        if tamano.upper() == cfg.OPCION_TAMANO_PERSONALIZADO:
            ancho = documento.ancho_pagina_var.get().strip() if documento.ancho_pagina_var is not None else "21.0"
            alto = documento.alto_pagina_var.get().strip() if documento.alto_pagina_var is not None else "29.7"
            tamano_texto = f"Personalizado · {ancho} × {alto} cm"
        else:
            tamano_texto = tamano
        self._establecer_resumen(
            documento.resumen_documento_var,
            [
                f"Tamaño: {tamano_texto}",
                f"Fuente títulos: {fuente_titulo}",
                f"Fuente texto: {fuente_texto}",
                f"Margen actual: {margen} cm",
                f"Borde cajas: {documento.ancho_borde_cajas_var.get().strip() if documento.ancho_borde_cajas_var is not None else '2.0'} pt",
                f"Espacios cajas: {documento.espacio_antes_cajas_var.get().strip() if documento.espacio_antes_cajas_var is not None else '6.0'} / {documento.espacio_despues_cajas_var.get().strip() if documento.espacio_despues_cajas_var is not None else '8.0'} pt",
            ],
        )

    def _inicializar_estado_decoracion(self):
        form_blocks.inicializar_estado_decoracion(self)

    def _construir_bloque_configuracion_cajas(self, parent, row=0):
        form_blocks.construir_bloque_configuracion_cajas(self, parent, row=row)
    

    def _construir_bloque_adornos_cajas(self, parent, row=0):
        form_blocks.construir_bloque_adornos_cajas(self, parent, row=row)

    def _finalizar_estado_decoracion(self):
        self.imagen_adorno_var.trace_add("write", self._actualizar_preview_adornos)
        self.imagen_adorno_var.trace_add("write", lambda *_args: self._actualizar_validacion_adorno())
        self._inicializar_estado_margenes()
        self._actualizar_opciones_margen()
        self.actualizar_estado_adornos()

    def _grupos_colores_disponibles(self):
        return [
            ("Caja Consejo para el DM", [("COLOR_CONSEJO_TEXTO", "Texto"), ("COLOR_CONSEJO_TITULO", "Título"), ("COLOR_CONSEJO_BORDE", "Borde"), ("COLOR_CONSEJO_FONDO", "Fondo")]),
            ("Caja Cita", [("COLOR_CITA_TEXTO", "Texto"), ("COLOR_CITA_TITULO", "Título"), ("COLOR_CITA_BORDE", "Borde"), ("COLOR_CITA_FONDO", "Fondo")]),
            ("Caja Información adicional", [("color_info_texto", "Texto"), ("color_info_titulo", "Título"), ("color_info_borde", "Borde"), ("color_info_fondo", "Fondo")]),
            ("Caja NPC", [("color_npc_texto", "Texto"), ("color_npc_titulo", "Título"), ("color_npc_borde", "Borde"), ("color_npc_fondo", "Fondo")]),
            ("Caja Enemigo", [("color_enemigo_texto", "Texto"), ("color_enemigo_titulo", "Título"), ("color_enemigo_borde", "Borde"), ("color_enemigo_fondo", "Fondo")]),
            ("Caja Aliado", [("color_aliado_texto", "Texto"), ("color_aliado_titulo", "Título"), ("color_aliado_borde", "Borde"), ("color_aliado_fondo", "Fondo")]),
            ("Caja Tesoro/Premio", [("color_tesoro_texto", "Texto"), ("color_tesoro_titulo", "Título"), ("color_tesoro_borde", "Borde"), ("color_tesoro_fondo", "Fondo")]),
            ("Caja Puzzle/Acertijo/Rompecabezas", [("color_puzzle_texto", "Texto"), ("color_puzzle_titulo", "Título"), ("color_puzzle_borde", "Borde"), ("color_puzzle_fondo", "Fondo")]),
            ("Caja Objeto", [("color_objeto_texto", "Texto"), ("color_objeto_titulo", "Título"), ("color_objeto_borde", "Borde"), ("color_objeto_fondo", "Fondo")]),
        ]

    def _crear_contenedor_tarjetas_colores(self, pestana):
        return tab_building.crear_contenedor_tarjetas_colores(self, pestana)

    def _construir_tarjeta_colores_grupo(self, contenedor_tab, nombre_grupo, campos, indice_grupo):
        tab_building.construir_tarjeta_colores_grupo(self, contenedor_tab, nombre_grupo, campos, indice_grupo)

    def _columnas_pestanas_colores(self):
        return {
            "Cajas útiles": self.columnas_cajas,
            "NPC y combate": self.columnas_npc_combate,
        }

    def _construir_pestanas_colores(self, pestana_colores_cajas, pestana_colores_personajes):
        tab_building.construir_pestanas_colores(
            self,
            pestana_colores_cajas,
            pestana_colores_personajes,
            columnas_por_pestana=self._columnas_pestanas_colores(),
        )

    def _construir_bloque_configuracion_margenes(self, parent):
        form_blocks.construir_bloque_configuracion_margenes(self, parent)

    def _construir_bloque_adornos_margenes(self, parent, row=0):
        form_blocks.construir_bloque_adornos_margenes(self, parent, row=row)

    def _construir_botones(self, contenedor):
        botones = self.tk.Frame(contenedor, padx=6, pady=8, bg=self.color_superficie)
        botones.pack(fill="x")
        self.barra_botones = botones
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)
        self.tk.Frame(botones, height=1, bg=self.color_borde_suave).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self._asignar_estado_ui("operacion", "estado_operacion_var", self.tk.StringVar(value=""))
        self._asignar_estado_ui("operacion", "etiqueta_estado_operacion", self.tk.Label(botones, textvariable=self.estado_operacion_var, anchor="w", justify="left", fg=self.color_texto_suave, bg=self.color_superficie))
        self.etiqueta_estado_operacion.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        acciones_izquierda = self.tk.Frame(botones, bg=self.color_superficie)
        acciones_izquierda.grid(row=2, column=0, sticky="w")
        acciones_derecha = self.tk.Frame(botones, bg=self.color_superficie)
        acciones_derecha.grid(row=2, column=1, sticky="e")

        self.boton_restablecer = self._crear_boton_accion(acciones_izquierda, "Restablecer valores", self.restablecer_valores, estilo="Secundario.TButton")
        self.boton_regresar = self._crear_boton_accion(acciones_izquierda, "Regresar", self.regresar_a_archivos, estilo="Secundario.TButton")

        self.boton_cancelar = self._crear_boton_accion(acciones_derecha, "Cancelar", self.cancelar, estilo="Secundario.TButton")
        self.boton_continuar = self._crear_boton_accion(acciones_derecha, "Continuar", self.continuar_a_personalizacion, estilo="Primario.TButton")
        self.boton_aceptar = self._crear_boton_accion(acciones_derecha, "Generar PDF", self.aceptar, estilo="Primario.TButton")
        self.boton_aceptar_y_abrir = self._crear_boton_accion(acciones_derecha, "Generar y abrir", self.aceptar_y_abrir, estilo="Secundario.TButton")

    def _crear_boton_accion(self, parent, texto, comando, estilo="Secundario.TButton"):
        return self.ttk.Button(parent, text=texto, style=estilo, command=comando)

    def actualizar_preview(self, clave):
        valor = cfg._normalizar_color_hex(self.variables_color[clave].get(), self.configuracion_inicial[clave])
        self.variables_color[clave].set(valor)
        vista_previa = self.vistas_previas.get(clave)
        if vista_previa is not None:
            vista_previa.configure(bg=valor)
        if clave in {"color_primario", "color_secundario", "color_fondo_pagina", "color_info_texto", "color_info_borde", "color_info_fondo"}:
            self._actualizar_preview_adornos()

    def elegir_color(self, clave):
        color = self.colorchooser.askcolor(color=self.variables_color[clave].get(), title="Selecciona un color", parent=self.raiz)[1]
        if color:
            self.variables_color[clave].set(color)
            self.actualizar_preview(clave)

    def crear_selector_color(self, parent, row, clave, etiqueta):
        self.tk.Label(parent, text=etiqueta, anchor="w").grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        entrada_color = self.tk.Entry(parent, textvariable=self.variables_color[clave], width=10, justify="center")
        entrada_color.grid(row=row, column=1, sticky="w", pady=4)
        entrada_color.bind("<FocusOut>", lambda _evento, clave_actual=clave: self._confirmar_color(clave_actual))
        entrada_color.bind("<Return>", lambda _evento, clave_actual=clave: self._confirmar_color(clave_actual))
        preview = self.tk.Label(parent, width=5, relief="groove", bg=self.variables_color[clave].get())
        preview.grid(row=row, column=2, padx=5, pady=4)
        self.vistas_previas[clave] = preview
        self.tk.Button(parent, text="Elegir...", command=lambda clave_actual=clave: self.elegir_color(clave_actual)).grid(row=row, column=3, sticky="w", pady=4)

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
        return ruta.exists() and ruta.is_file() and ruta.suffix.lower() in {".docx", ".txt"}

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

    def _mostrar_pagina(self, pagina, titulo, descripcion, botones_principales):
        self.pagina_actual = pagina
        self._actualizar_indicador_pasos()
        self.pagina_archivos.pack_forget()
        self.pagina_personalizacion.pack_forget()
        getattr(self, f"pagina_{pagina}").pack(fill="both", expand=True)
        self.titulo_encabezado.configure(text=titulo)
        self.descripcion_encabezado.configure(text=descripcion, wraplength=self.ancho_contenido_compacto)
        for boton in [self.boton_restablecer, self.boton_regresar, self.boton_aceptar, self.boton_aceptar_y_abrir, self.boton_continuar, self.boton_cancelar]:
            boton.pack_forget()
        for boton, opciones_pack in botones_principales:
            boton.pack(**opciones_pack)
        self.raiz.minsize(self.ancho_ventana_minimo, self.alto_ventana_minimo)

    def _mostrar_pagina_archivos(self):
        self._mostrar_pagina(
            "archivos",
            "Personaliza tu PDF antes de generarlo",
            "Primero elige un `.docx` o `.txt` y un destino `.pdf`. Después ajusta el estilo del documento.",
            [
                (self.boton_cancelar, {"side": "left"}),
                (self.boton_continuar, {"side": "left", "padx": (14, 0)}),
            ],
        )

    def _mostrar_pagina_personalizacion(self):
        self._mostrar_pagina(
            "personalizacion",
            "Configura el contenido y el estilo del PDF",
            "Usa las pestañas para ajustar portada, página, decoración y colores. Puedes volver atrás si necesitas cambiar rutas.",
            [
                (self.boton_restablecer, {"side": "left"}),
                (self.boton_regresar, {"side": "left", "padx": (8, 0)}),
                (self.boton_cancelar, {"side": "left", "padx": (16, 0)}),
                (self.boton_aceptar, {"side": "left", "padx": (14, 0)}),
                (self.boton_aceptar_y_abrir, {"side": "left", "padx": (8, 0)}),
            ],
        )

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

        ancho_requerido = max(ancho_paginas, ancho_encabezado, ancho_botones) + 60
        alto_requerido = alto_paginas + alto_encabezado + alto_botones + 60

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
            self.messagebox.showerror("Rutas inválidas", "Selecciona un archivo `.docx` o `.txt` existente y una salida `.pdf` válida antes de continuar.")
            return
        self._mostrar_pagina_personalizacion()

    def regresar_a_archivos(self):
        self._mostrar_pagina_archivos()

    def elegir_archivo_entrada(self):
        ruta = self.filedialog.askopenfilename(title="Selecciona el archivo de entrada", filetypes=[("Documentos compatibles", "*.docx *.txt"), ("Documentos Word", "*.docx"), ("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")], parent=self.raiz)
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
            self.actualizar_estado_portada()

    def elegir_imagen_adorno(self):
        ruta = self.filedialog.askopenfilename(title="Selecciona un PNG para adornar los márgenes", filetypes=[("PNG con transparencia", "*.png"), ("Todos los archivos", "*.*")], parent=self.raiz)
        if ruta:
            self.imagen_adorno_var.set(ruta)
            self.actualizar_estado_adornos()

    def _codigo_estilo_adorno_seleccionado(self):
        if self.estilo_adorno_var is None:
            return cfg.ESTILO_ADORNO_MARGEN
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
        adornos_activos = bool(self.adornos_habilitados_var and self.adornos_habilitados_var.get())
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
        self._actualizar_validacion_adorno()
        self._actualizar_validacion_margen()
        self._actualizar_preview_adornos()

    def _codigo_pack_cajas_seleccionado(self):
        if self.pack_decoracion_cajas_var is None:
            return "NINGUNO"
        return cfg.PACKS_DECORACION_CAJAS_DISPONIBLES.get(self.pack_decoracion_cajas_var.get(), "NINGUNO")

    def _actualizar_preview_adornos(self, *_args):
        preview_rendering.actualizar_preview_adornos(self, *_args)

    @staticmethod
    def _obtener_geometria_preview_margen(canvas):
        return preview_rendering.obtener_geometria_preview_margen(canvas)

    def _actualizar_preview_cajas(self):
        preview_rendering.actualizar_preview_cajas(self)

    @staticmethod
    def _dibujar_preview_caja_redondeada(canvas, x1, y1, x2, y2, radio, fill, outline, width=1):
        preview_rendering.dibujar_preview_caja_redondeada(canvas, x1, y1, x2, y2, radio, fill, outline, width=width)

    def _dibujar_preview_caja_base(self, canvas, pack):
        preview_rendering.dibujar_preview_caja_base(self, canvas, pack)

    @staticmethod
    def _dibujar_preview_pack_pergamino_noble(canvas, color_borde):
        preview_rendering.dibujar_preview_pack_pergamino_noble(canvas, color_borde)

    @staticmethod
    def _dibujar_preview_pack_grimorio_arcano(canvas, color_borde):
        preview_rendering.dibujar_preview_pack_grimorio_arcano(canvas, color_borde)

    @staticmethod
    def _dibujar_preview_pack_heraldica_campana(canvas):
        preview_rendering.dibujar_preview_pack_heraldica_campana(canvas)

    def _dibujar_preview_adorno_personalizado(self, canvas, page_box):
        preview_rendering.dibujar_preview_adorno_personalizado(self, canvas, page_box)

    def _color_preview(self, clave, valor_predeterminado):
        variable = self.variables_color.get(clave) if self.variables_color is not None else None
        if variable is None:
            return cfg._normalizar_color_hex(valor_predeterminado, valor_predeterminado)
        return cfg._normalizar_color_hex(variable.get(), valor_predeterminado)

    def _dibujar_preview_adorno_clasico(self, canvas, page_box):
        preview_rendering.dibujar_preview_adorno_clasico(self, canvas, page_box)

    def _dibujar_preview_adorno_geometrico(self, canvas, page_box):
        preview_rendering.dibujar_preview_adorno_geometrico(self, canvas, page_box)

    def _dibujar_preview_adorno_floral(self, canvas, page_box):
        preview_rendering.dibujar_preview_adorno_floral(self, canvas, page_box)

    def _configurar_etiqueta_estado(self, etiqueta, texto, color="#5F5F5F"):
        if etiqueta is None:
            return
        etiqueta.configure(text=texto, fg=color)

    @staticmethod
    def _configurar_estado_widget(widget, habilitado=True, solo_lectura=False):
        if widget is None:
            return
        estado = "readonly" if habilitado and solo_lectura else ("normal" if habilitado else "disabled")
        widget.configure(state=estado)

    @staticmethod
    def _valor_variable(variable, predeterminado=""):
        if variable is None:
            return predeterminado
        valor = variable.get()
        if valor is None:
            return predeterminado
        return valor

    def _valor_limpio_variable(self, variable, predeterminado=""):
        return str(self._valor_variable(variable, predeterminado) or "").strip()

    @staticmethod
    def _var_activa(variable):
        return bool(variable and variable.get())

    def _leer_float_en_rango(self, valor_texto, minimo, maximo, titulo_error, mensaje_no_numero, mensaje_fuera_rango):
        try:
            valor = float(str(valor_texto).replace(",", ".").strip())
        except (AttributeError, TypeError, ValueError):
            self._reportar_error_generacion(titulo_error, mensaje_no_numero)
            return None
        if not (minimo <= valor <= maximo):
            self._reportar_error_generacion(titulo_error, mensaje_fuera_rango)
            return None
        return valor

    def _configurar_estado_rutas(self, texto, color="#5F5F5F"):
        if self.estado_rutas_var is not None:
            self.estado_rutas_var.set(texto)
        if self.estado_rutas_label is not None:
            self.estado_rutas_label.configure(fg=color)

    def _actualizar_validacion_portada(self):
        if self.etiqueta_validacion_portada is None or self.portada_habilitada_var is None:
            return
        ruta = self.portada_var.get().strip() if self.portada_var is not None else ""
        ruta_existente = bool(ruta and Path(ruta).exists() and Path(ruta).is_file())
        texto, color = self._estado_portada(
            bool(self.portada_habilitada_var.get()),
            bool(self.portada_pagina_completa_var is not None and self.portada_pagina_completa_var.get()),
            ruta,
            ruta_existente,
        )
        self._configurar_etiqueta_estado(self.etiqueta_validacion_portada, texto, color=color)

    def _actualizar_validacion_tamano(self):
        if self.etiqueta_validacion_tamano is None or self.tamano_pagina_var is None:
            return
        texto, color = self._estado_tamano_personalizado(
            self.tamano_pagina_var.get().strip(),
            self.ancho_pagina_var.get() if self.ancho_pagina_var is not None else "",
            self.alto_pagina_var.get() if self.alto_pagina_var is not None else "",
        )
        self._configurar_etiqueta_estado(self.etiqueta_validacion_tamano, texto, color=color)

    def _actualizar_validacion_margen(self):
        if self.etiqueta_validacion_margen is None:
            return
        margen_cm = self._obtener_margen_actual_cm()
        adornos_activos = bool(self.adornos_habilitados_var and self.adornos_habilitados_var.get())
        minimo_cm = cfg.obtener_margen_minimo_cm(adornos_activos)
        if margen_cm is None:
            self._configurar_etiqueta_estado(self.etiqueta_validacion_margen, "No se pudo interpretar el margen actual.", color="#7A1C1C")
            return
        if margen_cm < minimo_cm or margen_cm > cfg.MARGEN_MAXIMO_CM:
            self._configurar_etiqueta_estado(self.etiqueta_validacion_margen, f"El margen debe estar entre {self._formatear_margen_cm(minimo_cm)} y {self._formatear_margen_cm(cfg.MARGEN_MAXIMO_CM)} cm.", color="#7A1C1C")
            return
        texto = f"Margen listo: {self._formatear_margen_cm(margen_cm)} cm"
        if adornos_activos:
            texto += " con decoración de márgenes activa."
        else:
            texto += "."
        self._configurar_etiqueta_estado(self.etiqueta_validacion_margen, texto, color="#1E5631")

    def _actualizar_validacion_adorno(self):
        if self.etiqueta_validacion_adorno is None:
            return
        adornos_activos = bool(self.adornos_habilitados_var and self.adornos_habilitados_var.get())
        if not adornos_activos:
            self._configurar_etiqueta_estado(self.etiqueta_validacion_adorno, "Decoración de márgenes desactivada. El PDF mantendrá solo el margen normal.")
            return
        if self._codigo_estilo_adorno_seleccionado() != "PERSONALIZADO":
            self._configurar_etiqueta_estado(self.etiqueta_validacion_adorno, f"Preset {self.estilo_adorno_var.get()} listo para aplicarse en todas las páginas.", color="#1E5631")
            return
        ruta = self.imagen_adorno_var.get().strip() if self.imagen_adorno_var is not None else ""
        if not ruta:
            self._configurar_etiqueta_estado(self.etiqueta_validacion_adorno, "Falta seleccionar un PNG transparente para el borde personalizado.", color="#7A1C1C")
            return
        ruta_png = Path(ruta)
        if not ruta_png.exists() or not ruta_png.is_file() or ruta_png.suffix.lower() != ".png":
            self._configurar_etiqueta_estado(self.etiqueta_validacion_adorno, "El adorno personalizado debe ser un archivo `.png` existente.", color="#7A1C1C")
            return
        self._configurar_etiqueta_estado(self.etiqueta_validacion_adorno, "PNG personalizado listo. Intenta dejar el centro transparente para no tapar el contenido.", color="#1E5631")

    def _actualizar_validaciones_inline(self):
        self._actualizar_validacion_portada()
        self._actualizar_validacion_tamano()
        self._actualizar_validacion_margen()
        self._actualizar_validacion_adorno()

    def actualizar_estado_rutas(self, *_args):
        rutas = self.estado_ui.rutas
        entrada_texto = str(self._valor_variable(rutas.entrada_var, "")).strip()
        salida_texto = str(self._valor_variable(rutas.salida_var, "")).strip()
        entrada_valida = self._es_ruta_entrada_valida(entrada_texto)
        salida_valida = self._es_ruta_salida_valida(salida_texto)
        if salida_texto:
            salida_normalizada = self._normalizar_ruta_salida(salida_texto)
            if salida_normalizada != salida_texto:
                rutas.salida_var.set(salida_normalizada)
                return

        estado_por_ruta = {
            (True, True): ("Rutas válidas. Pulsa `Continuar` para abrir las opciones de personalización.", "#1E5631"),
            (False, False): ("Selecciona un archivo de entrada y una ruta PDF de salida para continuar.", "#7A1C1C"),
            (False, True): ("La entrada debe apuntar a un archivo `.docx` o `.txt` existente.", "#7A1C1C"),
            (True, False): ("La salida debe ser una ruta `.pdf` válida en una carpeta existente.", "#7A1C1C"),
        }
        texto, color = estado_por_ruta[(entrada_valida, salida_valida)]

        self._configurar_estado_rutas(texto, color)
        if self.boton_continuar is not None:
            self.boton_continuar.configure(state="normal" if entrada_valida and salida_valida else "disabled")

    def actualizar_estado_portada(self):
        portada = self.estado_ui.portada
        portada_activa = self._var_activa(portada.portada_habilitada_var)
        self._configurar_estado_widget(portada.boton_portada, portada_activa)
        self._configurar_estado_widget(portada.entrada_portada, True, solo_lectura=True)
        if portada.check_portada_pagina_completa is not None:
            self._configurar_estado_widget(portada.check_portada_pagina_completa, portada_activa)
        self._configurar_estado_widget(
            portada.combo_portada_modo_ajuste,
            portada_activa and self._var_activa(portada.portada_pagina_completa_var),
            solo_lectura=True,
        )
        if portada.etiqueta_ayuda_portada is not None:
            ruta_portada = self._valor_limpio_variable(portada.portada_var)
            if not portada_activa:
                texto = "La portada está desactivada. Si ya elegiste una imagen, se conserva para que puedas recuperarla más tarde con un clic."
            elif not ruta_portada:
                texto = "Activa la portada solo si quieres añadir una imagen inicial al PDF. Puedes dejar título, subtítulo y autor vacíos sin problema."
            elif self._var_activa(portada.portada_pagina_completa_var):
                modo = cfg.MODOS_AJUSTE_PORTADA_DISPONIBLES.get(portada.portada_modo_ajuste_var.get(), "CUBRIR") if portada.portada_modo_ajuste_var is not None else "CUBRIR"
                if modo == "ENCAJAR":
                    texto = "La portada está activa y la imagen se redimensionará en ancho y alto para ocupar toda la hoja sin recorte, aunque su proporción original cambie."
                else:
                    texto = "La portada está activa y la imagen cubrirá toda la primera página. Si la proporción no coincide con el papel, el PDF recortará los bordes sobrantes."
            else:
                texto = "La portada está activa y usará la imagen seleccionada centrada dentro del área útil. Si la desactivas, la ruta se conservará por si quieres reactivarla luego."
            portada.etiqueta_ayuda_portada.configure(text=texto)
        self._actualizar_validacion_portada()

    def actualizar_estado_tamano_personalizado(self, *_args):
        documento = self.estado_ui.documento
        es_personalizado = str(self._valor_variable(documento.tamano_pagina_var, "A4")).strip().upper() == cfg.OPCION_TAMANO_PERSONALIZADO
        self._configurar_estado_widget(documento.entrada_ancho, es_personalizado)
        self._configurar_estado_widget(documento.entrada_alto, es_personalizado)
        if documento.etiqueta_ayuda_tamano is not None:
            if es_personalizado:
                texto = "Introduce ancho y alto entre 5 y 100 cm."
            else:
                texto = "Para medidas exactas, usa la opción Personalizado."
            documento.etiqueta_ayuda_tamano.configure(text=texto)
        self._actualizar_validacion_tamano()

    def restablecer_valores(self):
        self._restablecer_colores_visuales()
        self._restablecer_estado_portada()
        self._restablecer_estado_documento()
        self._restablecer_estado_decoracion()
        self.actualizar_estado_portada()
        self.actualizar_estado_tamano_personalizado()
        self.actualizar_estado_adornos()
        self._actualizar_validaciones_inline()

    def _restablecer_colores_visuales(self):
        for clave, valor in self.configuracion_inicial.items():
            self.variables_color[clave].set(valor)
            self.actualizar_preview(clave)

    def _restablecer_estado_portada(self):
        portada = self.estado_ui.portada
        portada.titulo_var.set(self.titulo_inicial)
        portada.subtitulo_var.set(self.subtitulo_inicial)
        portada.autor_var.set(self.autor_inicial)
        portada_explicita = bool(self.portada_inicial and self.portada_inicial != cfg.IMAGEN_PORTADA_PREDETERMINADA)
        portada.portada_habilitada_var.set(portada_explicita)
        portada.portada_var.set(self.portada_inicial if portada_explicita else "")
        portada.portada_pagina_completa_var.set(bool(self.configuracion_documento_inicial.get("portada_pagina_completa", False)))
        portada.portada_modo_ajuste_var.set(cfg.obtener_etiqueta_modo_ajuste_portada(self.configuracion_documento_inicial.get("portada_modo_ajuste", "CUBRIR")))

    def _restablecer_estado_documento(self):
        documento = self.estado_ui.documento
        documento.tamano_pagina_var.set(self.configuracion_documento_inicial.get("tamano_pagina", "A4"))
        documento.fuente_titulo_var.set(self.configuracion_documento_inicial.get("fuente_titulo", cfg.FUENTE_TITULO))
        documento.fuente_texto_var.set(self.configuracion_documento_inicial.get("fuente_texto", cfg.FUENTE_TEXTO))
        documento.margen_var.set(self._formatear_margen_cm(self._ajustar_margen_a_lista(self.configuracion_documento_inicial.get("margen_cm", 2.0), adornos_activos=bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False)))))
        documento.ancho_borde_cajas_var.set(str(self.configuracion_documento_inicial.get("ancho_borde_cajas", 2.0)))
        documento.espacio_antes_cajas_var.set(str(self.configuracion_documento_inicial.get("espacio_antes_cajas", 6.0)))
        documento.espacio_despues_cajas_var.set(str(self.configuracion_documento_inicial.get("espacio_despues_cajas", 8.0)))
        self.margen_sin_adornos_guardado = None
        self.margen_con_adornos_guardado = None
        self.adornos_activos_previos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        documento.ancho_pagina_var.set(str(self.configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)))
        documento.alto_pagina_var.set(str(self.configuracion_documento_inicial.get("alto_pagina_cm", 29.7)))

    def _restablecer_estado_decoracion(self):
        documento = self.estado_ui.documento
        documento.adornos_habilitados_var.set(bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False)))
        documento.estilo_adorno_var.set(cfg.obtener_etiqueta_estilo_adorno_margen(self.configuracion_documento_inicial.get("estilo_adorno_margen", cfg.ESTILO_ADORNO_MARGEN)))
        documento.imagen_adorno_var.set(str(self.configuracion_documento_inicial.get("imagen_adorno_margen", "") or "").strip())
        self.margen_sin_adornos_guardado = None
        self.margen_con_adornos_guardado = None
        self.adornos_activos_previos = bool(self.configuracion_documento_inicial.get("adornos_margen_activos", False))
        pack_inicial = cfg.normalizar_pack_decoracion_cajas(self.configuracion_documento_inicial.get("pack_decoracion_cajas", "NINGUNO"))
        documento.decoracion_cajas_habilitada_var.set(pack_inicial != "NINGUNO")
        documento.pack_decoracion_cajas_var.set(cfg.obtener_etiqueta_pack_decoracion_cajas(pack_inicial if pack_inicial != "NINGUNO" else "PERGAMINO_NOBLE"))
        self._inicializar_estado_margenes()
        self._actualizar_opciones_margen()

    def cancelar(self):
        self.resultado["valor"] = None
        self.raiz.quit()

    def _establecer_estado_operacion(self, texto, color="#5F5F5F"):
        if self.estado_operacion_var is not None:
            self.estado_operacion_var.set(texto)
        if self.etiqueta_estado_operacion is not None:
            self.etiqueta_estado_operacion.configure(fg=color)

    def _reportar_error_generacion(self, titulo, mensaje):
        self._establecer_estado_operacion(f"{titulo}: {mensaje}", color=self.COLOR_ERROR)
        print(f"ERROR: {titulo}: {mensaje}")

    def _establecer_estado_controles_generacion(self, generando=False):
        controles_habilitados = not generando
        self._configurar_estado_widget(self.boton_aceptar, controles_habilitados)
        self._configurar_estado_widget(self.boton_aceptar_y_abrir, controles_habilitados)
        self._configurar_estado_widget(self.boton_cancelar, controles_habilitados)
        self._configurar_estado_widget(self.boton_regresar, controles_habilitados)
        self._configurar_estado_widget(self.boton_restablecer, controles_habilitados)
        self._configurar_estado_widget(self.boton_continuar, controles_habilitados and self._rutas_actuales_validas())
        if self.raiz is not None:
            self.raiz.configure(cursor="watch" if generando else "")

    def _construir_configuracion_visual(self):
        configuracion_visual = {}
        for clave, valor_predeterminado in self.configuracion_inicial.items():
            color_normalizado = cfg._normalizar_color_hex(self.variables_color[clave].get(), valor_predeterminado)
            if color_normalizado != self.variables_color[clave].get().strip():
                self.variables_color[clave].set(color_normalizado)
            try:
                HexColor(color_normalizado)
            except Exception:
                self._reportar_error_generacion("Color inválido", f"El color para '{clave}' no es válido.")
                return None
            configuracion_visual[clave] = color_normalizado
        return configuracion_visual

    def _obtener_imagen_portada_seleccionada(self):
        portada = self.estado_ui.portada
        portada_activa = bool(portada.portada_habilitada_var.get())
        imagen_portada = self._valor_limpio_variable(portada.portada_var) if portada_activa else ""
        if not portada_activa:
            return imagen_portada
        if not imagen_portada:
            self._reportar_error_generacion("Portada incompleta", "Selecciona la imagen de portada o desactiva la opción.")
            return None
        ruta_portada = Path(imagen_portada)
        if not ruta_portada.is_file():
            self._reportar_error_generacion("Portada inválida", "La imagen de portada debe existir en disco antes de generar el PDF.")
            return None
        return imagen_portada

    def _leer_rutas_configuradas(self):
        rutas = self.estado_ui.rutas
        entrada = self._valor_limpio_variable(rutas.entrada_var)
        salida = self._normalizar_ruta_salida(self._valor_variable(rutas.salida_var, ""))
        if not self._es_ruta_entrada_valida(entrada):
            self._reportar_error_generacion("Entrada inválida", "Selecciona un archivo `.docx` o `.txt` de entrada válido.")
            return None
        if not self._es_ruta_salida_valida(salida):
            self._reportar_error_generacion("Salida inválida", "Selecciona una ruta de salida `.pdf` válida.")
            return None
        return {"entrada": entrada, "salida": salida}

    def _leer_configuracion_tamano_pagina(self):
        documento = self.estado_ui.documento
        tamano_pagina = documento.tamano_pagina_var.get().strip().upper()
        ancho_pagina_cm = self.configuracion_documento_inicial.get("ancho_pagina_cm", 21.0)
        alto_pagina_cm = self.configuracion_documento_inicial.get("alto_pagina_cm", 29.7)
        if tamano_pagina != cfg.OPCION_TAMANO_PERSONALIZADO:
            return tamano_pagina, ancho_pagina_cm, alto_pagina_cm

        ancho_pagina_cm = self._leer_float_en_rango(
            documento.ancho_pagina_var.get(),
            5.0,
            100.0,
            "Tamaño inválido",
            "El ancho personalizado debe ser un número en centímetros.",
            "El ancho personalizado debe estar entre 5 y 100 cm.",
        )
        alto_pagina_cm = self._leer_float_en_rango(
            documento.alto_pagina_var.get(),
            5.0,
            100.0,
            "Tamaño inválido",
            "El alto personalizado debe ser un número en centímetros.",
            "El alto personalizado debe estar entre 5 y 100 cm.",
        )
        if ancho_pagina_cm is None or alto_pagina_cm is None:
            return None
        return tamano_pagina, ancho_pagina_cm, alto_pagina_cm

    def _leer_configuracion_cajas(self):
        documento = self.estado_ui.documento
        ancho_borde_cajas = self._leer_float_en_rango(
            documento.ancho_borde_cajas_var.get(),
            0.0,
            10.0,
            "Borde inválido",
            "El ancho del borde de las cajas debe ser un número.",
            "El ancho del borde de las cajas debe estar entre 0 y 10 pt.",
        )
        if ancho_borde_cajas is None:
            return None
        espacio_antes_cajas = self._leer_float_en_rango(
            documento.espacio_antes_cajas_var.get(),
            0.0,
            40.0,
            "Espaciado inválido",
            "El espacio antes de las cajas debe ser un número.",
            "El espacio antes de las cajas debe estar entre 0 y 40 pt.",
        )
        espacio_despues_cajas = self._leer_float_en_rango(
            documento.espacio_despues_cajas_var.get(),
            0.0,
            40.0,
            "Espaciado inválido",
            "El espacio después de las cajas debe ser un número.",
            "El espacio después de las cajas debe estar entre 0 y 40 pt.",
        )
        if espacio_antes_cajas is None or espacio_despues_cajas is None:
            return None
        return {
            "ancho_borde_cajas": ancho_borde_cajas,
            "espacio_antes_cajas": espacio_antes_cajas,
            "espacio_despues_cajas": espacio_despues_cajas,
        }

    def _leer_margen_configurado(self, adornos_margen_activos):
        documento = self.estado_ui.documento
        margen_minimo_cm = cfg.obtener_margen_minimo_cm(adornos_margen_activos)
        margen_cm = self._leer_float_en_rango(
            documento.margen_var.get(),
            margen_minimo_cm,
            cfg.MARGEN_MAXIMO_CM,
            "Margen inválido",
            "El margen debe ser un número en centímetros.",
            f"El margen debe estar entre {self._formatear_margen_cm(margen_minimo_cm)} y {self._formatear_margen_cm(cfg.MARGEN_MAXIMO_CM)} cm.",
        )
        if margen_cm is None:
            return None
        margen_ajustado = self._ajustar_margen_a_lista(margen_cm, adornos_activos=adornos_margen_activos)
        if margen_ajustado < margen_minimo_cm:
            margen_ajustado = self._ajustar_margen_a_lista(margen_minimo_cm, adornos_activos=adornos_margen_activos)
        documento.margen_var.set(self._formatear_margen_cm(margen_ajustado))
        return margen_ajustado

    def _validar_adorno_personalizado(self, adornos_margen_activos, estilo_adorno_margen, imagen_adorno_margen):
        if not adornos_margen_activos or estilo_adorno_margen != "PERSONALIZADO":
            return True
        if not imagen_adorno_margen:
            self._reportar_error_generacion("Adorno incompleto", "Selecciona un PNG transparente para el borde personalizado o cambia a un preset.")
            return False
        ruta_adorno = Path(imagen_adorno_margen)
        if not ruta_adorno.is_file() or ruta_adorno.suffix.lower() != ".png":
            self._reportar_error_generacion("PNG inválido", "El adorno personalizado debe ser un archivo `.png` existente.")
            return False
        return True

    def _leer_configuracion_base_documento(self):
        documento = self.estado_ui.documento
        return {
            "fuente_titulo": documento.fuente_titulo_var.get().strip(),
            "fuente_texto": documento.fuente_texto_var.get().strip(),
        }

    def _leer_configuracion_portada_documento(self):
        portada = self.estado_ui.portada
        return {
            "portada_pagina_completa": bool(portada.portada_pagina_completa_var.get()),
            "portada_modo_ajuste": cfg.MODOS_AJUSTE_PORTADA_DISPONIBLES.get(portada.portada_modo_ajuste_var.get(), "CUBRIR"),
        }

    def _leer_configuracion_decoracion(self):
        documento = self.estado_ui.documento
        adornos_margen_activos = bool(documento.adornos_habilitados_var.get())
        estilo_adorno_margen = self._codigo_estilo_adorno_seleccionado()
        imagen_adorno_margen = self._valor_limpio_variable(documento.imagen_adorno_var)
        if not self._validar_adorno_personalizado(adornos_margen_activos, estilo_adorno_margen, imagen_adorno_margen):
            return None
        decoracion_cajas_activa = bool(documento.decoracion_cajas_habilitada_var.get()) if documento.decoracion_cajas_habilitada_var is not None else False
        return {
            "adornos_margen_activos": adornos_margen_activos,
            "estilo_adorno_margen": estilo_adorno_margen,
            "imagen_adorno_margen": imagen_adorno_margen,
            "pack_decoracion_cajas": self._codigo_pack_cajas_seleccionado() if decoracion_cajas_activa else "NINGUNO",
        }

    def _leer_datos_portada(self):
        portada = self.estado_ui.portada
        imagen_portada = self._obtener_imagen_portada_seleccionada()
        if imagen_portada is None:
            return None
        return {
            "titulo": portada.titulo_var.get().strip(),
            "subtitulo": portada.subtitulo_var.get().strip(),
            "autor": portada.autor_var.get().strip(),
            "imagen_portada": imagen_portada,
        }

    def _construir_configuracion_documento(self):
        configuracion_decoracion = self._leer_configuracion_decoracion()
        if configuracion_decoracion is None:
            return None

        adornos_margen_activos = configuracion_decoracion["adornos_margen_activos"]
        margen_cm = self._leer_margen_configurado(adornos_margen_activos)
        if margen_cm is None:
            return None

        tamano_pagina = self._leer_configuracion_tamano_pagina()
        if tamano_pagina is None:
            return None
        tamano_codigo, ancho_pagina_cm, alto_pagina_cm = tamano_pagina

        configuracion_cajas = self._leer_configuracion_cajas()
        if configuracion_cajas is None:
            return None

        configuracion_documento = {
            "tamano_pagina": tamano_codigo,
            "margen_cm": margen_cm,
            "ancho_pagina_cm": ancho_pagina_cm,
            "alto_pagina_cm": alto_pagina_cm,
        }
        configuracion_documento.update(self._leer_configuracion_base_documento())
        configuracion_documento.update(configuracion_cajas)
        configuracion_documento.update(configuracion_decoracion)
        configuracion_documento.update(self._leer_configuracion_portada_documento())
        return configuracion_documento

    def aceptar(self):
        return self._procesar_aceptacion(abrir_pdf_al_generar=False)

    def aceptar_y_abrir(self):
        return self._procesar_aceptacion(abrir_pdf_al_generar=True)

    def _procesar_aceptacion(self, abrir_pdf_al_generar=False):
        self._actualizar_validaciones_inline()
        rutas = self._leer_rutas_configuradas()
        if rutas is None:
            return
        configuracion_visual = self._construir_configuracion_visual()
        if configuracion_visual is None:
            return
        datos_portada = self._leer_datos_portada()
        if datos_portada is None:
            return
        configuracion_documento = self._construir_configuracion_documento()
        if configuracion_documento is None:
            return
        resultado = {
            "configuracion_visual": configuracion_visual,
            "configuracion_documento": configuracion_documento,
            "abrir_pdf_al_generar": bool(abrir_pdf_al_generar),
        }
        resultado.update(rutas)
        resultado.update(datos_portada)
        self.resultado["valor"] = resultado
        if self.accion_aceptar is not None:
            self._establecer_estado_controles_generacion(generando=True)
            self._establecer_estado_operacion("Generando PDF y abriendo el resultado..." if abrir_pdf_al_generar else "Generando PDF...", color=self.COLOR_EXITO)
            self.raiz.update_idletasks()
            try:
                self.accion_aceptar(dict(self.resultado["valor"]))
            except Exception as error:
                self._establecer_estado_operacion("No se pudo generar el PDF. Revisa los datos e inténtalo de nuevo.", color=self.COLOR_ERROR)
                print(f"ERROR: Error al generar el PDF: {error}")
            else:
                texto_ok = "PDF generado y abierto correctamente. Puedes ajustar opciones y volver a generar si lo necesitas." if abrir_pdf_al_generar else "PDF generado correctamente. Puedes ajustar opciones y volver a generar si lo necesitas."
                self._establecer_estado_operacion(texto_ok, color=self.COLOR_EXITO)
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

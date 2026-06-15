from pathlib import Path

from PIL import Image as PILImage, ImageTk

from ..core import configuracion_pdf as cfg


def actualizar_preview_adornos(dialog, *_args):
    if dialog.canvas_preview_adorno is None:
        actualizar_preview_cajas(dialog)
        return
    canvas = dialog.canvas_preview_adorno
    canvas.delete("all")
    fondo = dialog._color_preview("color_fondo_pagina", "#F7F1E3")
    page_box = obtener_geometria_preview_margen(canvas)
    x1, y1, x2, y2 = page_box
    canvas.create_rectangle(x1, y1, x2, y2, fill=fondo, outline="#D4C5AF")

    if not (dialog.adornos_habilitados_var and dialog.adornos_habilitados_var.get()):
        canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="Sin adornos", fill="#666666", font=("Segoe UI", 9))
        dialog.preview_adorno_imagen = None
        actualizar_preview_cajas(dialog)
        return

    estilo = dialog._codigo_estilo_adorno_seleccionado()
    if estilo == "PERSONALIZADO":
        dibujar_preview_adorno_personalizado(dialog, canvas, page_box)
        actualizar_preview_cajas(dialog)
        return
    if estilo == "FLORAL":
        dibujar_preview_adorno_floral(dialog, canvas, page_box)
        actualizar_preview_cajas(dialog)
        return
    if estilo == "GEOMETRICO":
        dibujar_preview_adorno_geometrico(dialog, canvas, page_box)
    else:
        dibujar_preview_adorno_clasico(dialog, canvas, page_box)
    actualizar_preview_cajas(dialog)


def obtener_geometria_preview_margen(canvas):
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


def actualizar_preview_cajas(dialog):
    if dialog.canvas_preview_cajas is None:
        return
    canvas = dialog.canvas_preview_cajas
    canvas.delete("all")
    color_fondo = dialog.variables_color.get("color_fondo_pagina")
    fondo_pagina = color_fondo.get() if color_fondo is not None else "#F7F1E3"
    fondo_pagina = cfg._normalizar_color_hex(fondo_pagina, "#F7F1E3")
    canvas.create_rectangle(0, 0, 180, 112, fill=fondo_pagina, outline="")
    color_borde = cfg._normalizar_color_hex(dialog.variables_color.get("color_info_borde").get(), "#2AA198") if dialog.variables_color.get("color_info_borde") is not None else "#2AA198"

    if not (dialog.decoracion_cajas_habilitada_var and dialog.decoracion_cajas_habilitada_var.get()):
        dibujar_preview_caja_base(dialog, canvas, "NINGUNO")
        return

    pack = dialog._codigo_pack_cajas_seleccionado()
    dibujar_preview_caja_base(dialog, canvas, pack)
    if pack == "PERGAMINO_NOBLE":
        dibujar_preview_pack_pergamino_noble(canvas, color_borde)
    elif pack == "GRIMORIO_ARCANO":
        dibujar_preview_pack_grimorio_arcano(canvas, color_borde)
    elif pack == "HERALDICA_CAMPANA":
        dibujar_preview_pack_heraldica_campana(canvas)


def dibujar_preview_caja_redondeada(canvas, x1, y1, x2, y2, radio, fill, outline, width=1):
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


def dibujar_preview_caja_base(dialog, canvas, pack):
    color_borde_var = dialog.variables_color.get("color_info_borde")
    color_fondo_var = dialog.variables_color.get("color_info_fondo")
    color_borde = cfg._normalizar_color_hex(color_borde_var.get(), "#2AA198") if color_borde_var is not None else "#2AA198"
    color_fondo = cfg._normalizar_color_hex(color_fondo_var.get(), "#E7F6F5") if color_fondo_var is not None else "#E7F6F5"
    if pack == "PERGAMINO_NOBLE":
        dibujar_preview_caja_redondeada(canvas, 16, 20, 164, 94, 10, color_fondo, color_borde, width=2)
        return
    if pack == "HERALDICA_CAMPANA":
        dibujar_preview_caja_redondeada(canvas, 16, 20, 164, 94, 8, color_fondo, color_borde, width=2)
        return
    canvas.create_rectangle(16, 20, 164, 94, fill=color_fondo, outline=color_borde, width=2)


def dibujar_preview_pack_pergamino_noble(canvas, color_borde):
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


def dibujar_preview_pack_grimorio_arcano(canvas, color_borde):
    canvas.create_rectangle(22, 26, 158, 88, outline=color_borde)
    for cx, cy in [(90, 24), (90, 90), (20, 57), (160, 57)]:
        canvas.create_polygon(cx, cy - 4, cx + 4, cy, cx, cy + 4, cx - 4, cy, outline=color_borde, fill="")
    for pos_x, pos_y in [(28, 32), (152, 32), (28, 82), (152, 82)]:
        canvas.create_line(pos_x - 4, pos_y, pos_x + 4, pos_y, fill=color_borde)
        canvas.create_line(pos_x, pos_y - 4, pos_x, pos_y + 4, fill=color_borde)


def dibujar_preview_pack_heraldica_campana(canvas):
    canvas.create_arc(16, 20, 32, 36, start=90, extent=90, style="arc", outline="#2AA198", width=2)
    canvas.create_arc(148, 20, 164, 36, start=0, extent=90, style="arc", outline="#2AA198", width=2)
    canvas.create_arc(16, 78, 32, 94, start=180, extent=90, style="arc", outline="#2AA198", width=2)
    canvas.create_arc(148, 78, 164, 94, start=270, extent=90, style="arc", outline="#2AA198", width=2)
    canvas.create_line(32, 24, 148, 24, fill="#2AA198")
    canvas.create_line(32, 90, 148, 90, fill="#2AA198")
    canvas.create_line(76, 24, 90, 16, 104, 24, fill="#2AA198", smooth=True)
    for x, y in [(22, 26), (158, 26), (22, 88), (158, 88)]:
        canvas.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5, outline="#2AA198")


def dibujar_preview_adorno_personalizado(dialog, canvas, page_box):
    x1, y1, x2, y2 = page_box
    ruta = dialog.imagen_adorno_var.get().strip()
    if not ruta or not Path(ruta).is_file():
        canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="Selecciona un PNG\ntransparente", fill="#666666", justify="center", font=("Segoe UI", 9))
        canvas.create_rectangle(x1 + 8, y1 + 8, x2 - 8, y2 - 8, outline="#8B0000", dash=(4, 3))
        dialog.preview_adorno_imagen = None
        return
    try:
        imagen = PILImage.open(ruta).convert("RGBA")
        imagen.thumbnail((max(20, (x2 - x1) - 8), max(20, (y2 - y1) - 8)), PILImage.Resampling.LANCZOS)
        dialog.preview_adorno_imagen = ImageTk.PhotoImage(imagen)
        canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=dialog.preview_adorno_imagen)
    except Exception:
        canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="No se pudo cargar\nel PNG", fill="#7A1C1C", justify="center", font=("Segoe UI", 9))
        dialog.preview_adorno_imagen = None


def dibujar_preview_adorno_clasico(dialog, canvas, page_box):
    x1, y1, x2, y2 = page_box
    margen_ext = 8
    margen_int = 16
    color_primario = dialog._color_preview("color_primario", "#8B0000")
    color_secundario = dialog._color_preview("color_secundario", "#333333")
    canvas.create_rectangle(x1 + margen_ext, y1 + margen_ext, x2 - margen_ext, y2 - margen_ext, outline=color_primario, width=2)
    canvas.create_rectangle(x1 + margen_int, y1 + margen_int, x2 - margen_int, y2 - margen_int, outline=color_secundario)
    centro_x = (x1 + x2) / 2
    centro_y = (y1 + y2) / 2
    for px, py in [(centro_x, y1 + margen_ext), (centro_x, y2 - margen_ext), (x1 + margen_ext, centro_y), (x2 - margen_ext, centro_y)]:
        canvas.create_oval(px - 3, py - 3, px + 3, py + 3, outline=color_secundario)
    for esquina_x, esquina_y, direccion_x, direccion_y in [
        (x1 + margen_int, y1 + margen_int, 1, 1),
        (x2 - margen_int, y1 + margen_int, -1, 1),
        (x1 + margen_int, y2 - margen_int, 1, -1),
        (x2 - margen_int, y2 - margen_int, -1, -1),
    ]:
        canvas.create_line(esquina_x, esquina_y, esquina_x + (10 * direccion_x), esquina_y, fill=color_secundario)
        canvas.create_line(esquina_x, esquina_y, esquina_x, esquina_y + (10 * direccion_y), fill=color_secundario)
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
            fill=color_secundario,
        )
        canvas.create_oval(
            esquina_x + (4 * direccion_x) - 1.5,
            esquina_y + (4 * direccion_y) - 1.5,
            esquina_x + (4 * direccion_x) + 1.5,
            esquina_y + (4 * direccion_y) + 1.5,
            outline=color_secundario,
        )


def dibujar_preview_adorno_geometrico(dialog, canvas, page_box):
    x1, y1, x2, y2 = page_box
    margen = 8
    color_primario = dialog._color_preview("color_primario", "#8B0000")
    color_secundario = dialog._color_preview("color_secundario", "#333333")
    canvas.create_rectangle(x1 + margen, y1 + margen, x2 - margen, y2 - margen, outline=color_secundario, width=2, dash=(5, 3))
    for linea_x1, linea_y1, linea_x2, linea_y2 in [
        (page_box[0] + margen, page_box[1] + margen, page_box[0] + margen + 18, page_box[1] + margen),
        (page_box[0] + margen, page_box[1] + margen, page_box[0] + margen, page_box[1] + margen + 18),
        (page_box[2] - margen, page_box[1] + margen, page_box[2] - margen - 18, page_box[1] + margen),
        (page_box[2] - margen, page_box[1] + margen, page_box[2] - margen, page_box[1] + margen + 18),
        (page_box[0] + margen, page_box[3] - margen, page_box[0] + margen + 18, page_box[3] - margen),
        (page_box[0] + margen, page_box[3] - margen, page_box[0] + margen, page_box[3] - margen - 18),
        (page_box[2] - margen, page_box[3] - margen, page_box[2] - margen - 18, page_box[3] - margen),
        (page_box[2] - margen, page_box[3] - margen, page_box[2] - margen, page_box[3] - margen - 18),
    ]:
        canvas.create_line(linea_x1, linea_y1, linea_x2, linea_y2, fill=color_primario, width=2)
    for centro_x, centro_y in [
        (page_box[0] + 20, page_box[1] + 20),
        (page_box[2] - 20, page_box[1] + 20),
        (page_box[0] + 20, page_box[3] - 20),
        (page_box[2] - 20, page_box[3] - 20),
    ]:
        canvas.create_line(centro_x, centro_y - 5, centro_x + 5, centro_y, fill=color_primario)
        canvas.create_line(centro_x + 5, centro_y, centro_x, centro_y + 5, fill=color_primario)
        canvas.create_line(centro_x, centro_y + 5, centro_x - 5, centro_y, fill=color_primario)
        canvas.create_line(centro_x - 5, centro_y, centro_x, centro_y - 5, fill=color_primario)
        canvas.create_line(centro_x - 2, centro_y, centro_x + 2, centro_y, fill=color_primario)
        canvas.create_line(centro_x, centro_y - 2, centro_x, centro_y + 2, fill=color_primario)
        canvas.create_oval(centro_x - 1, centro_y - 1, centro_x + 1, centro_y + 1, outline=color_primario)
    centro_x = (page_box[0] + page_box[2]) / 2
    centro_y = (page_box[1] + page_box[3]) / 2
    for centro_x, centro_y in [(page_box[0] + margen, centro_y), (page_box[2] - margen, centro_y), (centro_x, page_box[1] + margen), (centro_x, page_box[3] - margen)]:
        canvas.create_line(centro_x - 7, centro_y, centro_x, centro_y - 7, fill=color_primario)
        canvas.create_line(centro_x, centro_y - 7, centro_x + 7, centro_y, fill=color_primario)
        canvas.create_line(centro_x + 7, centro_y, centro_x, centro_y + 7, fill=color_primario)
        canvas.create_line(centro_x, centro_y + 7, centro_x - 7, centro_y, fill=color_primario)
        canvas.create_oval(centro_x - 1.2, centro_y - 1.2, centro_x + 1.2, centro_y + 1.2, outline=color_primario)


def dibujar_preview_adorno_floral(dialog, canvas, page_box):
    x1, y1, x2, y2 = page_box
    borde_ext = 10
    borde_int = 17
    color_primario = dialog._color_preview("color_primario", "#8B0000")
    color_secundario = dialog._color_preview("color_secundario", "#333333")
    canvas.create_rectangle(x1 + borde_ext, y1 + borde_ext, x2 - borde_ext, y2 - borde_ext, outline=color_primario, width=1)
    canvas.create_rectangle(x1 + borde_int, y1 + borde_int, x2 - borde_int, y2 - borde_int, outline=color_secundario)

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
        canvas.create_line(*puntos, smooth=True, fill=color_secundario)

    canvas.create_line(izquierda + 2, arriba + 2, izquierda + 10, arriba + 10, fill=color_secundario)
    canvas.create_line(derecha - 2, arriba + 2, derecha - 10, arriba + 10, fill=color_secundario)
    canvas.create_line(izquierda + 2, abajo - 2, izquierda + 10, abajo - 10, fill=color_secundario)
    canvas.create_line(derecha - 2, abajo - 2, derecha - 10, abajo - 10, fill=color_secundario)
    for x, y in [(izquierda + 7, arriba + 7), (derecha - 7, arriba + 7), (izquierda + 7, abajo - 7), (derecha - 7, abajo - 7)]:
        canvas.create_oval(x - 1.5, y - 1.5, x + 1.5, y + 1.5, outline=color_secundario)

    centro_x = (x1 + x2) / 2
    canvas.create_line(centro_x - 18, y1 + borde_ext, centro_x - 12, y1 + borde_ext, centro_x - 6, y1 + 3, centro_x, y1 + 7, smooth=True, fill=color_secundario)
    canvas.create_line(centro_x + 18, y1 + borde_ext, centro_x + 12, y1 + borde_ext, centro_x + 6, y1 + 3, centro_x, y1 + 7, smooth=True, fill=color_secundario)
    canvas.create_line(centro_x - 11, y1 + borde_ext + 4, centro_x - 6, y1 + 2, centro_x - 2, y1 + 1, centro_x, y1 + 7, smooth=True, fill=color_secundario)
    canvas.create_line(centro_x + 11, y1 + borde_ext + 4, centro_x + 6, y1 + 2, centro_x + 2, y1 + 1, centro_x, y1 + 7, smooth=True, fill=color_secundario)
    canvas.create_oval(centro_x - 1.5, y1 + 5.5, centro_x + 1.5, y1 + 8.5, outline=color_secundario)

    canvas.create_line(centro_x - 18, y2 - borde_ext, centro_x - 12, y2 - borde_ext, centro_x - 6, y2 - 3, centro_x, y2 - 7, smooth=True, fill=color_secundario)
    canvas.create_line(centro_x + 18, y2 - borde_ext, centro_x + 12, y2 - borde_ext, centro_x + 6, y2 - 3, centro_x, y2 - 7, smooth=True, fill=color_secundario)
    canvas.create_line(centro_x - 11, y2 - borde_ext - 4, centro_x - 6, y2 - 2, centro_x - 2, y2 - 1, centro_x, y2 - 7, smooth=True, fill=color_secundario)
    canvas.create_line(centro_x + 11, y2 - borde_ext - 4, centro_x + 6, y2 - 2, centro_x + 2, y2 - 1, centro_x, y2 - 7, smooth=True, fill=color_secundario)
    canvas.create_oval(centro_x - 1.5, y2 - 8.5, centro_x + 1.5, y2 - 5.5, outline=color_secundario)

    centro_y = (y1 + y2) / 2
    canvas.create_line(x1 + borde_ext, centro_y, x1 + borde_ext + 8, centro_y, fill=color_secundario)
    canvas.create_line(x2 - borde_ext, centro_y, x2 - borde_ext - 8, centro_y, fill=color_secundario)
    canvas.create_oval(x1 + borde_ext + 3, centro_y - 1.5, x1 + borde_ext + 6, centro_y + 1.5, outline=color_secundario)
    canvas.create_oval(x2 - borde_ext - 6, centro_y - 1.5, x2 - borde_ext - 3, centro_y + 1.5, outline=color_secundario)
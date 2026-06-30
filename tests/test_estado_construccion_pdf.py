"""Tests de caracterización para EstadoConstruccionPdf - apertura/cierre de bloques."""
import pytest

from docx_to_pdf_app.core import configuracion_pdf as cfg
from docx_to_pdf_app.core.procesamiento_word import item_caja_plano


def _crear_estado():
    """Crea un EstadoConstruccionPdf con estilos y historia mínimos."""
    from docx_to_pdf_app.pdf.constructor_pdf import EstadoConstruccionPdf
    estilos = cfg.construir_estilos()
    ancho_util = 400.0
    estado = EstadoConstruccionPdf(
        historia=[],
        estilos=estilos,
        ancho_util=ancho_util,
    )
    return estado


class TestEstadoInicialLimpio:
    """Verificar que el estado se crea con valores neutros."""

    def test_sin_bloques_activos(self):
        estado = _crear_estado()
        assert estado.dentro_consejo_manual is False
        assert estado.dentro_cita_manual is False
        assert estado.dentro_npc_manual is False
        assert estado.dentro_enemigo_manual is False
        assert estado.dentro_aliado_manual is False
        assert estado.dentro_tesoro_manual is False
        assert estado.dentro_puzzle_manual is False
        assert estado.dentro_objeto_manual is False
        assert estado.dentro_info is False

    def test_historia_vacia(self):
        estado = _crear_estado()
        assert estado.historia == []

    def test_buffers_vacios(self):
        estado = _crear_estado()
        assert estado.bloque_consejo_manual == []
        assert estado.bloque_cita_manual == []
        assert estado.bloque_npc_manual == []
        assert estado.bloque_enemigo_manual == []
        assert estado.bloque_aliado_manual == []
        assert estado.bloque_tesoro_manual == []
        assert estado.bloque_puzzle_manual == []
        assert estado.bloque_objeto_manual == []
        assert estado.bloque_info_manual == []


class TestAgregarContenidoABloqueActivo:
    """Verificar que agregar_contenido_a_bloque_activo enruta al bloque correcto."""

    def test_sin_bloque_activo_devuelve_false(self):
        estado = _crear_estado()
        resultado = estado.agregar_contenido_a_bloque_activo("item html", [])
        assert resultado is False

    def test_dentro_consejo_agrega_al_buffer(self):
        estado = _crear_estado()
        estado.dentro_consejo_manual = True
        item = item_caja_plano("contenido consejo")
        resultado = estado.agregar_contenido_a_bloque_activo(item, [])
        assert resultado is True
        assert item in estado.bloque_consejo_manual

    def test_dentro_cita_agrega_al_buffer(self):
        estado = _crear_estado()
        estado.dentro_cita_manual = True
        item = item_caja_plano("contenido cita")
        resultado = estado.agregar_contenido_a_bloque_activo(item, [])
        assert resultado is True
        assert item in estado.bloque_cita_manual

    def test_dentro_npc_agrega_al_buffer(self):
        estado = _crear_estado()
        estado.dentro_npc_manual = True
        item = item_caja_plano("npc data")
        resultado = estado.agregar_contenido_a_bloque_activo(item, [])
        assert resultado is True
        assert item in estado.bloque_npc_manual

    def test_dentro_enemigo_agrega_al_buffer(self):
        estado = _crear_estado()
        estado.dentro_enemigo_manual = True
        item = item_caja_plano("enemigo data")
        resultado = estado.agregar_contenido_a_bloque_activo(item, [])
        assert resultado is True
        assert item in estado.bloque_enemigo_manual

    def test_dentro_info_agrega_al_buffer(self):
        estado = _crear_estado()
        estado.dentro_info = True
        item = item_caja_plano("info data")
        resultado = estado.agregar_contenido_a_bloque_activo(item, [])
        assert resultado is True
        assert item in estado.bloque_info_manual

    def test_item_none_no_se_agrega(self):
        estado = _crear_estado()
        estado.dentro_consejo_manual = True
        estado.agregar_contenido_a_bloque_activo(None, [])
        assert estado.bloque_consejo_manual == []

    def test_prioridad_info_sobre_consejo(self):
        """Si ambos están activos, info tiene prioridad (aparece primero en la lista)."""
        estado = _crear_estado()
        estado.dentro_info = True
        estado.dentro_consejo_manual = True
        item = item_caja_plano("dato")
        estado.agregar_contenido_a_bloque_activo(item, [])
        assert item in estado.bloque_info_manual
        assert estado.bloque_consejo_manual == []


class TestAgregarSaltoABloqueActivo:
    """Verificar agregar_salto_a_bloque_activo."""

    def test_sin_bloque_activo_devuelve_false(self):
        estado = _crear_estado()
        assert estado.agregar_salto_a_bloque_activo() is False

    def test_con_consejo_activo(self):
        estado = _crear_estado()
        estado.dentro_consejo_manual = True
        assert estado.agregar_salto_a_bloque_activo() is True
        assert None in estado.bloque_consejo_manual


class TestEmitirBloquesManual:
    """Verificar emitir_*_manual limpia buffer y flag."""

    def test_emitir_consejo_vacia_y_desactiva(self):
        estado = _crear_estado()
        estado.dentro_consejo_manual = True
        estado.bloque_consejo_manual.append(item_caja_plano("contenido test"))
        estado.emitir_consejo_manual()
        assert estado.dentro_consejo_manual is False
        assert estado.bloque_consejo_manual == []
        # Debe haber generado algo en historia
        assert len(estado.historia) > 0

    def test_emitir_cita_vacia_y_desactiva(self):
        estado = _crear_estado()
        estado.dentro_cita_manual = True
        estado.bloque_cita_manual.append(item_caja_plano("cita test"))
        estado.emitir_cita_manual()
        assert estado.dentro_cita_manual is False
        assert estado.bloque_cita_manual == []
        assert len(estado.historia) > 0

    def test_emitir_consejo_sin_contenido_no_falla(self):
        estado = _crear_estado()
        estado.dentro_consejo_manual = True
        estado.emitir_consejo_manual()
        assert estado.dentro_consejo_manual is False
        assert estado.historia == []

    def test_emitir_npc_vacia_y_desactiva(self):
        estado = _crear_estado()
        estado.dentro_npc_manual = True
        estado.bloque_npc_manual.append(item_caja_plano("npc data"))
        estado.emitir_npc_manual()
        assert estado.dentro_npc_manual is False
        assert estado.bloque_npc_manual == []

    def test_emitir_enemigo(self):
        estado = _crear_estado()
        estado.dentro_enemigo_manual = True
        estado.bloque_enemigo_manual.append(item_caja_plano("enemigo data"))
        estado.emitir_enemigo_manual()
        assert estado.dentro_enemigo_manual is False

    def test_emitir_aliado(self):
        estado = _crear_estado()
        estado.dentro_aliado_manual = True
        estado.bloque_aliado_manual.append(item_caja_plano("aliado data"))
        estado.emitir_aliado_manual()
        assert estado.dentro_aliado_manual is False

    def test_emitir_tesoro(self):
        estado = _crear_estado()
        estado.dentro_tesoro_manual = True
        estado.bloque_tesoro_manual.append(item_caja_plano("tesoro data"))
        estado.emitir_tesoro_manual()
        assert estado.dentro_tesoro_manual is False
        assert estado.titulo_tesoro_manual == "Tesoro"

    def test_emitir_puzzle(self):
        estado = _crear_estado()
        estado.dentro_puzzle_manual = True
        estado.bloque_puzzle_manual.append(item_caja_plano("puzzle data"))
        estado.emitir_puzzle_manual()
        assert estado.dentro_puzzle_manual is False
        assert estado.titulo_puzzle_manual == "Puzzle"

    def test_emitir_objeto(self):
        estado = _crear_estado()
        estado.dentro_objeto_manual = True
        estado.bloque_objeto_manual.append(item_caja_plano("objeto data"))
        estado.emitir_objeto_manual()
        assert estado.dentro_objeto_manual is False

    def test_emitir_info_adicional(self):
        estado = _crear_estado()
        estado.dentro_info = True
        estado.bloque_info_manual.append(item_caja_plano("info data"))
        estado.emitir_info_adicional()
        assert estado.dentro_info is False


class TestVaciarLista:
    """Verificar vaciar_lista."""

    def test_lista_vacia_no_produce_flowable(self):
        estado = _crear_estado()
        estado.vaciar_lista()
        assert estado.historia == []

    def test_lista_con_items_produce_flowable(self):
        estado = _crear_estado()
        estado.items_lista_actual.extend(["Item 1", "Item 2"])
        estado.vaciar_lista()
        assert len(estado.historia) > 0
        assert estado.items_lista_actual == []

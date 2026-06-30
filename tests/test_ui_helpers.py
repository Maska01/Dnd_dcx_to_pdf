"""Tests de caracterización para helpers de UI sin necesidad de Tk real."""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from docx_to_pdf_app.core import configuracion_pdf as cfg


class TestEstadoTamanoPersonalizado:
    """Verificar _estado_tamano_personalizado (método estático)."""

    @staticmethod
    def _estado(tamano, ancho, alto):
        from docx_to_pdf_app.ui.interfaz_usuario import DialogoConfiguracionInteractiva
        return DialogoConfiguracionInteractiva._estado_tamano_personalizado(tamano, ancho, alto)

    def test_tamano_estandar_a4(self):
        texto, color = self._estado("A4", "21.0", "29.7")
        assert "A4" in texto
        assert color == "#1E5631"

    def test_personalizado_valido(self):
        texto, color = self._estado("PERSONALIZADO", "15.0", "20.0")
        assert "15.0" in texto
        assert "20.0" in texto
        assert color == "#1E5631"

    def test_personalizado_invalido_no_numerico(self):
        texto, color = self._estado("PERSONALIZADO", "abc", "20.0")
        assert color == "#7A1C1C"

    def test_personalizado_fuera_de_rango(self):
        texto, color = self._estado("PERSONALIZADO", "2.0", "200.0")
        assert color == "#7A1C1C"

    def test_personalizado_limite_inferior(self):
        texto, color = self._estado("PERSONALIZADO", "5.0", "5.0")
        assert color == "#1E5631"

    def test_personalizado_limite_superior(self):
        texto, color = self._estado("PERSONALIZADO", "100.0", "100.0")
        assert color == "#1E5631"


class TestNormalizarRutaSalida:
    """Verificar _normalizar_ruta_salida sin levantar UI."""

    def _crear_dialogo_minimo(self):
        from docx_to_pdf_app.ui.interfaz_usuario import DialogoConfiguracionInteractiva
        dialogo = object.__new__(DialogoConfiguracionInteractiva)
        return dialogo

    def test_vacia(self):
        d = self._crear_dialogo_minimo()
        assert d._normalizar_ruta_salida("") == ""

    def test_con_extension_pdf(self):
        d = self._crear_dialogo_minimo()
        resultado = d._normalizar_ruta_salida("archivo.pdf")
        assert resultado == "archivo.pdf"

    def test_sin_extension_pdf(self):
        d = self._crear_dialogo_minimo()
        resultado = d._normalizar_ruta_salida("archivo.docx")
        assert resultado.endswith(".pdf")

    def test_solo_espacios(self):
        d = self._crear_dialogo_minimo()
        assert d._normalizar_ruta_salida("   ") == ""

    def test_none_como_string(self):
        d = self._crear_dialogo_minimo()
        assert d._normalizar_ruta_salida(None) == ""


class TestEsRutaEntradaValida:
    """Verificar _es_ruta_entrada_valida sin UI."""

    def _crear_dialogo_minimo(self):
        from docx_to_pdf_app.ui.interfaz_usuario import DialogoConfiguracionInteractiva
        dialogo = object.__new__(DialogoConfiguracionInteractiva)
        return dialogo

    def test_vacia(self):
        d = self._crear_dialogo_minimo()
        assert d._es_ruta_entrada_valida("") is False

    def test_archivo_inexistente(self):
        d = self._crear_dialogo_minimo()
        assert d._es_ruta_entrada_valida("/ruta/inventada/no_existe.docx") is False

    def test_archivo_existente_docx(self):
        d = self._crear_dialogo_minimo()
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            f.write(b"contenido")
            ruta = f.name
        try:
            assert d._es_ruta_entrada_valida(ruta) is True
        finally:
            os.unlink(ruta)

    def test_archivo_existente_txt(self):
        d = self._crear_dialogo_minimo()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"contenido")
            ruta = f.name
        try:
            assert d._es_ruta_entrada_valida(ruta) is True
        finally:
            os.unlink(ruta)

    def test_archivo_existente_extension_invalida(self):
        d = self._crear_dialogo_minimo()
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"contenido")
            ruta = f.name
        try:
            assert d._es_ruta_entrada_valida(ruta) is False
        finally:
            os.unlink(ruta)


class TestEsRutaSalidaValida:
    """Verificar _es_ruta_salida_valida sin UI."""

    def _crear_dialogo_minimo(self):
        from docx_to_pdf_app.ui.interfaz_usuario import DialogoConfiguracionInteractiva
        dialogo = object.__new__(DialogoConfiguracionInteractiva)
        return dialogo

    def test_vacia(self):
        d = self._crear_dialogo_minimo()
        assert d._es_ruta_salida_valida("") is False

    def test_directorio_existente(self):
        d = self._crear_dialogo_minimo()
        directorio = tempfile.gettempdir()
        ruta = os.path.join(directorio, "salida_test.pdf")
        assert d._es_ruta_salida_valida(ruta) is True

    def test_directorio_inexistente(self):
        d = self._crear_dialogo_minimo()
        assert d._es_ruta_salida_valida("/directorio/inventado/salida.pdf") is False

    def test_sin_extension_se_normaliza(self):
        d = self._crear_dialogo_minimo()
        directorio = tempfile.gettempdir()
        ruta = os.path.join(directorio, "salida_test.docx")
        # _normalizar_ruta_salida adds .pdf so it should be valid
        assert d._es_ruta_salida_valida(ruta) is True

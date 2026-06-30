"""Tests de caracterización para configuracion_pdf.py - configuración visual."""
import pytest

from docx_to_pdf_app.core import configuracion_pdf as cfg


class TestObtenerConfiguracionVisualPredeterminada:
    """Verificar claves devueltas por obtener_configuracion_visual_predeterminada."""

    def test_devuelve_diccionario(self):
        resultado = cfg.obtener_configuracion_visual_predeterminada()
        assert isinstance(resultado, dict)

    def test_contiene_claves_principales(self):
        resultado = cfg.obtener_configuracion_visual_predeterminada()
        claves_esperadas = [
            "color_primario",
            "color_secundario",
            "color_texto_general",
            "color_fondo_pagina",
        ]
        for clave in claves_esperadas:
            assert clave in resultado, f"Falta clave: {clave}"

    def test_contiene_claves_cajas(self):
        resultado = cfg.obtener_configuracion_visual_predeterminada()
        prefijos_caja = [
            "COLOR_CONSEJO", "COLOR_CITA",
            "color_info", "color_enemigo", "color_npc",
            "color_aliado", "color_tesoro", "color_puzzle", "color_objeto",
        ]
        for prefijo in prefijos_caja:
            sufijos = ["_TEXTO", "_BORDE", "_FONDO", "_TITULO"] if prefijo.startswith("COLOR_") else ["_texto", "_borde", "_fondo", "_titulo"]
            for sufijo in sufijos:
                clave = f"{prefijo}{sufijo}"
                assert clave in resultado, f"Falta clave: {clave}"

    def test_valores_son_hex_validos(self):
        resultado = cfg.obtener_configuracion_visual_predeterminada()
        import re
        patron_hex = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for clave, valor in resultado.items():
            assert patron_hex.match(valor), f"{clave}={valor} no es hex válido"


class TestNormalizarColorHex:
    """Verificar normalización de hex válidos e inválidos."""

    def test_hex_valido_con_hash(self):
        resultado = cfg._normalizar_color_hex("#FF0000", "#000000")
        assert resultado == "#FF0000"

    def test_hex_valido_sin_hash(self):
        resultado = cfg._normalizar_color_hex("00FF00", "#000000")
        assert resultado == "#00FF00"

    def test_hex_invalido_devuelve_predeterminado(self):
        resultado = cfg._normalizar_color_hex("xyz", "#AABBCC")
        assert resultado == "#AABBCC"

    def test_vacio_devuelve_predeterminado(self):
        resultado = cfg._normalizar_color_hex("", "#112233")
        assert resultado == "#112233"

    def test_none_devuelve_predeterminado(self):
        resultado = cfg._normalizar_color_hex(None, "#445566")
        assert resultado == "#445566"

    def test_hex_minusculas_normalizado_a_mayusculas(self):
        resultado = cfg._normalizar_color_hex("#abcdef", "#000000")
        assert resultado == "#ABCDEF"

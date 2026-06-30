"""Tests de caracterización para configuracion_pdf.py - configuración de documento."""
import pytest

from docx_to_pdf_app.core import configuracion_pdf as cfg


class TestNormalizarMargenCm:
    """Verificar normalización de margen con y sin adornos."""

    def test_margen_normal_dentro_de_rango(self):
        resultado = cfg.normalizar_margen_cm(2.0)
        assert resultado == 2.0

    def test_margen_por_debajo_del_minimo_sin_adornos(self):
        resultado = cfg.normalizar_margen_cm(0.1, adornos_activos=False)
        assert resultado == cfg.MARGEN_MINIMO_CM

    def test_margen_por_debajo_del_minimo_con_adornos(self):
        resultado = cfg.normalizar_margen_cm(0.1, adornos_activos=True)
        assert resultado == cfg.MARGEN_MINIMO_ADORNOS_CM

    def test_margen_por_encima_del_maximo(self):
        resultado = cfg.normalizar_margen_cm(10.0)
        assert resultado == cfg.MARGEN_MAXIMO_CM

    def test_margen_invalido_usa_predeterminado(self):
        resultado = cfg.normalizar_margen_cm("abc", valor_predeterminado=2.5)
        assert resultado == 2.5

    def test_margen_none_usa_predeterminado(self):
        resultado = cfg.normalizar_margen_cm(None, valor_predeterminado=2.0)
        assert resultado == 2.0

    def test_minimo_con_adornos_mayor_que_sin_adornos(self):
        assert cfg.MARGEN_MINIMO_ADORNOS_CM > cfg.MARGEN_MINIMO_CM


class TestObtenerConfiguracionDocumentoPredeterminada:
    """Verificar estructura y valores de configuración de documento."""

    def test_devuelve_diccionario(self):
        resultado = cfg.obtener_configuracion_documento_predeterminada()
        assert isinstance(resultado, dict)

    def test_contiene_claves_basicas(self):
        resultado = cfg.obtener_configuracion_documento_predeterminada()
        claves = ["tamano_pagina", "fuente_titulo", "fuente_texto", "margen_cm",
                  "ancho_borde_cajas", "espacio_antes_cajas", "espacio_despues_cajas"]
        for clave in claves:
            assert clave in resultado, f"Falta clave: {clave}"

    def test_tamano_pagina_predeterminado_es_a4(self):
        resultado = cfg.obtener_configuracion_documento_predeterminada()
        assert resultado["tamano_pagina"] == "A4"

    def test_fuentes_predeterminadas(self):
        resultado = cfg.obtener_configuracion_documento_predeterminada()
        assert resultado["fuente_titulo"] == "Helvetica-Bold"
        assert resultado["fuente_texto"] == "Helvetica"


class TestNormalizarModosAjustePortada:
    """Verificar normalización de modos de ajuste de portada."""

    def test_cubrir(self):
        assert cfg.normalizar_modo_ajuste_portada("CUBRIR") == "CUBRIR"

    def test_encajar(self):
        assert cfg.normalizar_modo_ajuste_portada("ENCAJAR") == "ENCAJAR"

    def test_encajar_minusculas(self):
        assert cfg.normalizar_modo_ajuste_portada("encajar") == "ENCAJAR"

    def test_valor_invalido_default_cubrir(self):
        assert cfg.normalizar_modo_ajuste_portada("otro") == "CUBRIR"

    def test_none_default_cubrir(self):
        assert cfg.normalizar_modo_ajuste_portada(None) == "CUBRIR"

    def test_vacio_default_cubrir(self):
        assert cfg.normalizar_modo_ajuste_portada("") == "CUBRIR"


class TestNormalizarPackDecoracionCajas:
    """Verificar normalización de packs de decoración."""

    def test_pergamino_noble(self):
        assert cfg.normalizar_pack_decoracion_cajas("PERGAMINO_NOBLE") == "PERGAMINO_NOBLE"

    def test_grimorio_arcano(self):
        assert cfg.normalizar_pack_decoracion_cajas("GRIMORIO_ARCANO") == "GRIMORIO_ARCANO"

    def test_valor_invalido_default_ninguno(self):
        assert cfg.normalizar_pack_decoracion_cajas("inventado") == "NINGUNO"

    def test_none_default_ninguno(self):
        assert cfg.normalizar_pack_decoracion_cajas(None) == "NINGUNO"


class TestNormalizarEstiloAdornoMargen:
    """Verificar normalización de estilo de adorno de margen."""

    def test_clasico_mayusculas(self):
        assert cfg.normalizar_estilo_adorno_margen("CLASICO") == "CLASICO"

    def test_floral(self):
        assert cfg.normalizar_estilo_adorno_margen("FLORAL") == "FLORAL"

    def test_etiqueta_legible(self):
        assert cfg.normalizar_estilo_adorno_margen("Clásico") == "CLASICO"

    def test_vacio_usa_predeterminado(self):
        resultado = cfg.normalizar_estilo_adorno_margen("")
        assert resultado == cfg.ESTILO_ADORNO_MARGEN

    def test_none_usa_predeterminado(self):
        resultado = cfg.normalizar_estilo_adorno_margen(None)
        assert resultado == cfg.ESTILO_ADORNO_MARGEN

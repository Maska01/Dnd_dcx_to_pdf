"""Tests de caracterización para procesamiento_word.py - funciones de detección de bloques."""
import pytest

from docx_to_pdf_app.core import procesamiento_word as pw


class TestEstiloParaParrafo:
    """Verificar estilo_para_parrafo con objetos mock mínimos."""

    class _MockEstilo:
        def __init__(self, name):
            self.name = name

    class _MockParrafo:
        def __init__(self, style_name):
            self.style = TestEstiloParaParrafo._MockEstilo(style_name)

    def test_heading_1(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Heading 1")) == "H1"

    def test_titulo_1(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Título 1")) == "H1"

    def test_heading_2(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Heading 2")) == "H2"

    def test_heading_3(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Heading 3")) == "H3"

    def test_informacion_adicional(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Información adicional")) == "CajaInfoAdicional"

    def test_consejo_dm(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Consejo DM")) == "CajaConsejoDm"

    def test_quote(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Quote")) == "CajaCita"

    def test_cita(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Cita")) == "CajaCita"

    def test_lista(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Lista")) == "Lista"

    def test_list_paragraph(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("List Paragraph")) == "Lista"

    def test_normal(self):
        assert pw.estilo_para_parrafo(self._MockParrafo("Normal")) == "Cuerpo"

    def test_estilo_none(self):
        assert pw.estilo_para_parrafo(self._MockParrafo(None)) == "Cuerpo"


class TestEsConsejoDm:
    """Verificar es_consejo_dm."""

    def test_texto_consejo_basico(self):
        assert pw.es_consejo_dm("Consejo para el DM: algo útil") is True

    def test_con_formato_previo(self):
        assert pw.es_consejo_dm("**Consejo para el DM: texto") is True

    def test_con_espacios_previos(self):
        assert pw.es_consejo_dm("  Consejo para el DM") is True

    def test_texto_normal(self):
        assert pw.es_consejo_dm("Este es un texto normal") is False

    def test_vacio(self):
        assert pw.es_consejo_dm("") is False


class TestEsInfoAdicional:
    """Verificar es_info_adicional."""

    def test_informacion_adicional(self):
        assert pw.es_info_adicional("Información adicional: detalle") is True

    def test_info_adicional(self):
        assert pw.es_info_adicional("Info adicional: detalle") is True

    def test_dato_adicional(self):
        assert pw.es_info_adicional("Dato adicional: detalle") is True

    def test_sin_acento(self):
        assert pw.es_info_adicional("Informacion adicional: detalle") is True

    def test_con_formato(self):
        assert pw.es_info_adicional("  **Información adicional: foo") is True

    def test_texto_normal(self):
        assert pw.es_info_adicional("Esto no es info") is False


class TestEsInicioBloque:
    """Verificar funciones es_inicio_bloque_*."""

    def test_inicio_info(self):
        assert pw.es_inicio_bloque_info(":::info") is True
        assert pw.es_inicio_bloque_info("::: info") is True
        assert pw.es_inicio_bloque_info(":::información") is True
        assert pw.es_inicio_bloque_info("texto normal") is False

    def test_inicio_consejo(self):
        assert pw.es_inicio_bloque_consejo(":::consejo") is True
        assert pw.es_inicio_bloque_consejo("::: consejo") is True
        assert pw.es_inicio_bloque_consejo(":::dm") is True
        assert pw.es_inicio_bloque_consejo("texto") is False

    def test_inicio_cita(self):
        assert pw.es_inicio_bloque_cita(":::cita") is True
        assert pw.es_inicio_bloque_cita("::: cita") is True
        assert pw.es_inicio_bloque_cita(":::quote") is True
        assert pw.es_inicio_bloque_cita("texto") is False

    def test_inicio_npc(self):
        assert pw.es_inicio_bloque_npc(":::npc") is True
        assert pw.es_inicio_bloque_npc("::: npc") is True
        assert pw.es_inicio_bloque_npc("texto") is False

    def test_inicio_enemigo(self):
        assert pw.es_inicio_bloque_enemigo(":::enemigo") is True
        assert pw.es_inicio_bloque_enemigo("::: enemigo") is True
        assert pw.es_inicio_bloque_enemigo(":::enemy") is True
        assert pw.es_inicio_bloque_enemigo("texto") is False

    def test_inicio_aliado(self):
        assert pw.es_inicio_bloque_aliado(":::aliado") is True
        assert pw.es_inicio_bloque_aliado("::: aliado") is True
        assert pw.es_inicio_bloque_aliado(":::ally") is True
        assert pw.es_inicio_bloque_aliado("texto") is False

    def test_inicio_tesoro(self):
        assert pw.es_inicio_bloque_tesoro(":::tesoro") is True
        assert pw.es_inicio_bloque_tesoro("::: tesoro") is True
        assert pw.es_inicio_bloque_tesoro(":::premio") is True
        assert pw.es_inicio_bloque_tesoro("texto") is False

    def test_inicio_puzzle(self):
        assert pw.es_inicio_bloque_puzzle(":::puzzle") is True
        assert pw.es_inicio_bloque_puzzle("::: puzzle") is True
        assert pw.es_inicio_bloque_puzzle(":::acertijo") is True
        assert pw.es_inicio_bloque_puzzle(":::rompecabezas") is True
        assert pw.es_inicio_bloque_puzzle("texto") is False

    def test_inicio_objeto(self):
        assert pw.es_inicio_bloque_objeto(":::objeto") is True
        assert pw.es_inicio_bloque_objeto("::: objeto") is True
        assert pw.es_inicio_bloque_objeto("texto") is False

    def test_fin_bloque_manual(self):
        assert pw.es_fin_bloque_manual(":::") is True
        assert pw.es_fin_bloque_manual("  :::  ") is True
        assert pw.es_fin_bloque_manual(":::info") is False
        assert pw.es_fin_bloque_manual("texto") is False


class TestDividirHtmlEnSalto:
    """Verificar _dividir_html_en_salto."""

    def test_sin_saltos(self):
        izq, der = pw._dividir_html_en_salto("texto simple", 1)
        assert izq == "texto simple"
        assert der == ""

    def test_un_salto(self):
        html = "linea1<br/>linea2"
        izq, der = pw._dividir_html_en_salto(html, 1)
        assert "linea1" in izq
        assert "linea2" in der

    def test_cero_saltos_devuelve_original(self):
        html = "linea1<br/>linea2"
        izq, der = pw._dividir_html_en_salto(html, 0)
        assert izq == html
        assert der == ""

    def test_con_tags_anidados(self):
        html = "<b>negrita</b><br/>normal"
        izq, der = pw._dividir_html_en_salto(html, 1)
        assert "negrita" in izq
        assert "normal" in der


class TestExtraerBloquePrefijo:
    """Verificar _extraer_bloque_prefijo_embebido."""

    def test_con_prefijo_detectado(self):
        texto_html = "contexto previo<br/>Consejo para el DM: contenido"
        texto_plano = "contexto previo\nConsejo para el DM: contenido"
        resultado = pw._extraer_bloque_prefijo_embebido(texto_html, texto_plano, pw.es_consejo_dm)
        assert resultado is not None
        antes_html, antes_plano, bloque_html, bloque_plano = resultado
        assert "contexto previo" in antes_html
        assert "Consejo para el DM" in bloque_plano

    def test_sin_prefijo(self):
        texto_html = "Consejo para el DM: contenido"
        texto_plano = "Consejo para el DM: contenido"
        resultado = pw._extraer_bloque_prefijo_embebido(texto_html, texto_plano, pw.es_consejo_dm)
        assert resultado is None

    def test_solo_una_linea(self):
        resultado = pw._extraer_bloque_prefijo_embebido("solo", "solo", pw.es_consejo_dm)
        assert resultado is None

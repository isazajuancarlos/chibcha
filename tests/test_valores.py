# SPDX-License-Identifier: Apache-2.0
"""Los valores y, sobre todo, que la librería se niegue a adivinar."""
from datetime import date
from decimal import Decimal

import pytest

from chibcha import (
    AñoNoDisponible,
    ValorSinVerificar,
    Valor,
    _buscar,
    aplica_auxilio_transporte,
    auxilio_transporte,
    incremento_arriendo,
    ipc,
    jornada_en,
    smmlv,
    tarifa_arl,
    tasa,
    uvt,
    valor_hora,
)
from chibcha.valores import IPC, SMMLV, UVT
from chibcha.valores import AUXILIO_TRANSPORTE as AUXILIO_TRANSPORTE_TABLA


class TestNoAdivina:
    """Lo que separa esta librería de la tabla de la que salió."""

    def test_un_año_futuro_levanta_en_vez_de_dar_el_ultimo(self):
        # El código de origen devolvía el valor más reciente con un
        # `logger.warning`. Los avisos no los lee nadie y la liquidación sale
        # con un número que parece bueno.
        with pytest.raises(AñoNoDisponible) as e:
            smmlv(2035)
        assert "2035" in str(e.value)
        assert "2014" in str(e.value), "debe decir qué años sí tiene"

    def test_un_año_anterior_a_la_serie_tampoco_se_extrapola(self):
        with pytest.raises(AñoNoDisponible):
            uvt(1999)

    def test_el_mensaje_explica_por_que_no_aproxima(self):
        with pytest.raises(AñoNoDisponible) as e:
            auxilio_transporte(2040)
        assert "aproximado" in str(e.value).lower()


class TestTrazabilidad:
    def test_todo_valor_trae_su_norma(self):
        """Es la razón de ser: el número sustenta, la norma defiende."""
        for tabla in (SMMLV, AUXILIO_TRANSPORTE_TABLA, UVT, IPC):
            for año, valor in tabla.items():
                assert valor.norma, f"{año} sin norma"
                assert len(valor.norma) > 8, f"{año}: la norma no identifica nada"

    def test_el_smmlv_cita_su_decreto(self):
        assert smmlv(2026).norma == "Decreto 1469 del 29/12/2025"

    def test_la_uvt_cita_su_resolucion_de_la_dian(self):
        assert "DIAN" in uvt(2026).norma

    def test_los_montos_son_decimal_no_float(self):
        """Con float, un cálculo de retención se desvía en los centavos y no
        cuadra con el que hizo la DIAN."""
        assert isinstance(smmlv(2026).monto, Decimal)
        assert isinstance(uvt(2026).monto, Decimal)


class TestIPC:
    """La serie llegó corrida un año desde 2023 y eso sube arriendos de más."""

    def test_2024_es_5_20_y_no_9_28(self):
        assert ipc(2024).monto == Decimal("5.20")

    def test_2025_es_5_10(self):
        assert ipc(2025).monto == Decimal("5.10")

    def test_2022_seguia_bien(self):
        assert ipc(2022).monto == Decimal("13.12")

    def test_2023_es_9_28_y_esta_COTEJADO(self):
        """Cotejado el 2026-08-14 contra la fuente primaria.

        El comunicado del DANE se titula literalmente «En diciembre de 2023 la
        variación anual del IPC fue 9,28%» (`cp-IPC-dic2023.pdf`, 2024-01-09).
        Antes salía con `verificado=False` y la librería se negaba a entregarlo.
        """
        v = ipc(2023)
        assert v.monto == Decimal("9.28")
        assert v.verificado


class TestSeNiegaASalirSinCotejar:
    """El mecanismo de `ValorSinVerificar`, contra fuente SINTÉTICA.

    Antes esto se probaba con `ipc(2023)`, que era el único valor sin cotejar del
    árbol. Al cotejarlo el 2026-08-14 no queda NINGUNO —comprobado: cero
    `verificado=False` en `valores.py`—, y unas pruebas que solo miran datos
    limpios pasan igual con el mecanismo funcionando y con el mecanismo BORRADO.
    Es la directiva 33: un banco de solo negativos sobre artefactos limpios no
    discrimina, por muchos casos que tenga.

    Así que se prueba con una tabla inventada, y por la MISMA costura que usa el
    camino real (`_buscar`), no por un atajo: si el rojo falla por el arnés, no
    prueba nada.
    """

    TABLA = {
        2030: Valor(Decimal("1.00"), "norma inventada", verificado=False,
                    nota="Señuelo del banco."),
        2031: Valor(Decimal("2.00"), "norma inventada"),
    }

    def test_el_sin_cotejar_se_niega(self):
        with pytest.raises(ValorSinVerificar) as e:
            _buscar(self.TABLA, 2030, "señuelo")
        assert "cotejado" in str(e.value)

    def test_pero_se_puede_pedir_a_sabiendas(self):
        v = _buscar(self.TABLA, 2030, "señuelo", admitir_sin_verificar=True)
        assert v.monto == Decimal("1.00")

    def test_y_el_COTEJADO_sale_sin_pedir_permiso(self):
        """La pareja. Sin ella pasaría igual un mecanismo que se niega a todo."""
        assert _buscar(self.TABLA, 2031, "señuelo").monto == Decimal("2.00")


class TestArriendo:
    """Ley 820 de 2003, art. 20: el tope es el IPC del año anterior."""

    def test_usa_el_ipc_del_año_anterior(self):
        r = incremento_arriendo(Decimal("1000000"), 2025)
        assert r["año_del_ipc"] == 2024
        assert r["ipc_aplicado"] == Decimal("5.20")

    def test_calcula_el_tope_no_una_sugerencia(self):
        r = incremento_arriendo(Decimal("1000000"), 2025)
        assert r["incremento_maximo"] == Decimal("52000")
        assert r["canon_maximo"] == Decimal("1052000")

    def test_trae_el_fundamento_para_ponerlo_en_la_carta(self):
        r = incremento_arriendo(Decimal("800000"), 2025)
        assert r["fundamento"] == "Ley 820 de 2003, art. 20"
        assert "DANE" in str(r["fuente"])

    def test_el_error_de_la_serie_corrida_valia_cuatro_puntos(self):
        """Con el 9,28 % que traía el código, un canon de un millón subía
        41.000 pesos por encima del máximo legal."""
        legal = incremento_arriendo(Decimal("1000000"), 2025)["incremento_maximo"]
        con_el_dato_viejo = Decimal("1000000") * Decimal("9.28") / 100
        assert con_el_dato_viejo - legal == Decimal("40800")


class TestJornada:
    """La Ley 2466 de 2025 la cambia por etapas, incluso a mitad de año."""

    def test_antes_de_la_reforma_eran_48_horas(self):
        assert jornada_en(date(2020, 6, 1)).horas_semana == 48

    def test_en_2026_van_44_y_la_nocturna_empieza_a_las_7(self):
        j = jornada_en(date(2026, 3, 1))
        assert j.horas_semana == 44
        assert j.inicio_nocturna == 19

    def test_el_cambio_de_mitad_de_2026_se_respeta(self):
        assert jornada_en(date(2026, 6, 30)).horas_semana == 44
        assert jornada_en(date(2026, 7, 1)).horas_semana == 42

    def test_el_dominical_sube_por_etapas(self):
        assert jornada_en(date(2026, 1, 1)).recargo_dominical == Decimal("0.80")
        assert jornada_en(date(2026, 7, 1)).recargo_dominical == Decimal("0.90")
        assert jornada_en(date(2027, 7, 1)).recargo_dominical == Decimal("1.00")

    def test_cada_regimen_cita_su_ley(self):
        assert "2466" in jornada_en(date(2026, 8, 1)).norma
        assert "CST" in jornada_en(date(2019, 1, 1)).norma


class TestValorHora:
    def test_la_misma_mensualidad_vale_mas_por_hora_al_bajar_la_jornada(self):
        """Es lo que más se olvida al liquidar extras de 2025 en adelante."""
        con_48 = valor_hora(Decimal("2000000"), date(2020, 1, 1))
        con_42 = valor_hora(Decimal("2000000"), date(2027, 8, 1))
        assert con_42 > con_48


class TestAuxilioTransporte:
    def test_le_corresponde_a_quien_gana_hasta_dos_minimos(self):
        tope = smmlv(2026).monto * 2
        assert aplica_auxilio_transporte(tope, 2026)
        assert aplica_auxilio_transporte(tope - 1, 2026)
        assert not aplica_auxilio_transporte(tope + 1, 2026)


class TestTasas:
    def test_salud_es_4_y_8_5(self):
        assert tasa("salud_empleado").porcentaje == Decimal("0.04")
        assert tasa("salud_empleador").porcentaje == Decimal("0.085")

    def test_cada_tasa_cita_su_ley(self):
        assert tasa("pension_empleado").norma == "Ley 797 de 2003"

    def test_una_tasa_inexistente_dice_cuales_hay(self):
        with pytest.raises(AñoNoDisponible) as e:
            tasa("salud_empleadr")
        assert "salud_empleado" in str(e.value)

    def test_las_cinco_clases_de_arl(self):
        assert tarifa_arl(1)[0] == Decimal("0.00522")
        assert tarifa_arl(5)[0] == Decimal("0.06960")
        with pytest.raises(AñoNoDisponible):
            tarifa_arl(6)

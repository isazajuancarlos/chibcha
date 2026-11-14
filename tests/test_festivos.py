# SPDX-License-Identifier: Apache-2.0
"""Festivos colombianos y conteo de términos.

Las fechas fijadas aquí se contrastaron contra el calendario oficial. No se
generan con el mismo código que se está probando, que sería comprobar que una
función es igual a sí misma.
"""
from datetime import date

import pytest

from chibcha import (
    dias_habiles_entre,
    es_dia_habil,
    es_festivo,
    festivos_de,
    siguiente_dia_habil,
    sumar_dias_habiles,
)
from chibcha.festivos import domingo_de_pascua, lunes_siguiente


class TestPascua:
    """Butcher, contrastado contra fechas conocidas."""

    @pytest.mark.parametrize("año,esperado", [
        (2024, date(2024, 3, 31)),
        (2025, date(2025, 4, 20)),
        (2026, date(2026, 4, 5)),
        (2027, date(2027, 3, 28)),
        (2000, date(2000, 4, 23)),
        (1999, date(1999, 4, 4)),
    ])
    def test_domingo_de_resurreccion(self, año, esperado):
        assert domingo_de_pascua(año) == esperado


class TestLeyEmiliani:
    def test_lo_que_ya_cae_lunes_no_se_mueve(self):
        lunes = date(2026, 1, 5)
        assert lunes.weekday() == 0
        assert lunes_siguiente(lunes) == lunes

    def test_reyes_2026_se_corre_del_martes_al_lunes_12(self):
        assert date(2026, 1, 6).weekday() == 1
        assert not es_festivo(date(2026, 1, 6))
        assert es_festivo(date(2026, 1, 12))

    def test_los_fijos_NO_se_mueven_aunque_caigan_en_domingo(self):
        # El 1 de noviembre de 2026 es domingo y Todos los Santos SÍ se traslada;
        # el 8 de diciembre de 2026 es martes y NO se traslada.
        assert es_festivo(date(2026, 12, 8)), "Inmaculada se celebra en su fecha"

    def test_jueves_y_viernes_santo_no_se_trasladan(self):
        pascua = domingo_de_pascua(2026)
        assert es_festivo(pascua - __import__("datetime").timedelta(days=3))
        assert es_festivo(pascua - __import__("datetime").timedelta(days=2))


class TestCuantosSon:
    """Casi siempre dieciocho. Algunos años, diecisiete.

    Se suele decir que Colombia tiene dieciocho festivos, y es casi cierto.
    Hay años en que DOS de las fiestas trasladables caen en el mismo lunes y
    se funden en un solo día de descanso.

    Pasa entre San Pedro y San Pablo (29 de junio) y el Sagrado Corazón (68
    días después de la Pascua): cuando el 29 cae sábado o domingo, los dos se
    corren al mismo lunes. Ocurrió en 2025 —lunes 30 de junio— y vuelve a
    ocurrir en 2030.

    Esta prueba nació afirmando que siempre eran dieciocho y falló. El
    calendario tenía razón.
    """

    #: Años del rango probado en que dos trasladables coinciden.
    COLISIONAN = {2025, 2030}

    @pytest.mark.parametrize("año", range(2020, 2031))
    def test_son_dieciocho_salvo_cuando_dos_caen_el_mismo_lunes(self, año):
        esperados = 17 if año in self.COLISIONAN else 18
        assert len(festivos_de(año)) == esperados, (
            f"{año}: {sorted(festivos_de(año))}"
        )

    @pytest.mark.parametrize("año,dia", [(2025, date(2025, 6, 30)),
                                         (2030, date(2030, 7, 1))])
    def test_la_colision_es_entre_san_pedro_y_el_sagrado_corazon(self, año, dia):
        """Un solo festivo ese lunes, no dos días de descanso."""
        assert es_festivo(dia)
        assert sum(1 for f in festivos_de(año) if f == dia) == 1

    def test_cada_festivo_trae_su_nombre(self):
        for f, nombre in festivos_de(2026).items():
            assert nombre, f"{f} sin nombre"


class TestFechasConocidas2026:
    @pytest.mark.parametrize("dia,nombre", [
        (date(2026, 1, 1), "Año Nuevo"),
        (date(2026, 1, 12), "Reyes Magos"),
        (date(2026, 3, 23), "San José"),
        (date(2026, 5, 1), "Día del Trabajo"),
        (date(2026, 7, 20), "Independencia"),
        (date(2026, 8, 7), "Batalla de Boyacá"),
        (date(2026, 12, 25), "Navidad"),
    ])
    def test_festivos_de_2026(self, dia, nombre):
        assert es_festivo(dia)
        assert festivos_de(2026)[dia] == nombre

    def test_un_dia_cualquiera_no_es_festivo(self):
        assert not es_festivo(date(2026, 2, 17))


class TestDiasHabiles:
    def test_el_sabado_no_es_habil(self):
        sabado = date(2026, 2, 21)
        assert sabado.weekday() == 5
        assert not es_dia_habil(sabado)

    def test_un_festivo_entre_semana_no_es_habil(self):
        assert not es_dia_habil(date(2026, 1, 12))

    def test_el_siguiente_habil_salta_el_puente(self):
        # Viernes 9 de enero de 2026 → el lunes 12 es festivo → martes 13.
        assert siguiente_dia_habil(date(2026, 1, 9)) == date(2026, 1, 13)

    def test_siguiente_habil_avanza_aunque_hoy_sea_habil(self):
        martes = date(2026, 2, 17)
        assert es_dia_habil(martes)
        assert siguiente_dia_habil(martes) == date(2026, 2, 18)

    def test_sumar_cero_no_mueve_nada(self):
        for d in (date(2026, 2, 17), date(2026, 2, 21), date(2026, 1, 12)):
            assert sumar_dias_habiles(d, 0) == d

    def test_sumar_habiles_salta_fines_de_semana_y_festivos(self):
        # Del jueves 8 de enero de 2026, cinco hábiles: 9, 13, 14, 15, 16.
        assert sumar_dias_habiles(date(2026, 1, 8), 5) == date(2026, 1, 16)

    def test_se_puede_contar_hacia_atras(self):
        ida = sumar_dias_habiles(date(2026, 2, 2), 7)
        assert sumar_dias_habiles(ida, -7) == date(2026, 2, 2)

    def test_el_termino_de_cinco_dias_vence_donde_debe(self):
        """Un plazo que empieza el lunes 2 de febrero de 2026 vence el lunes 9:
        no el viernes, que es el error de contar corridos."""
        assert sumar_dias_habiles(date(2026, 2, 2), 5) == date(2026, 2, 9)

    def test_contar_entre_fechas_excluye_el_inicio_e_incluye_el_fin(self):
        assert dias_habiles_entre(date(2026, 2, 2), date(2026, 2, 9)) == 5

    def test_contar_al_reves_da_negativo(self):
        assert dias_habiles_entre(date(2026, 2, 9), date(2026, 2, 2)) == -5

    def test_entre_la_misma_fecha_no_hay_dias(self):
        assert dias_habiles_entre(date(2026, 2, 2), date(2026, 2, 2)) == 0

    def test_sumar_y_contar_son_coherentes(self):
        """Si sumar 10 hábiles lleva a X, entre el origen y X hay 10 hábiles."""
        origen = date(2026, 3, 16)
        destino = sumar_dias_habiles(origen, 10)
        assert dias_habiles_entre(origen, destino) == 10

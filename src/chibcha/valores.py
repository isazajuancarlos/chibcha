# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Juan Carlos Isaza
"""Los valores, cada uno con la norma que lo fijó.

Esa es la razón de ser de esta librería. Un número suelto —«el SMMLV de 2024 es
1.300.000»— no sirve para sustentar una liquidación ni para contestar una
objeción. El número CON su decreto sí, y es lo que un juez, un revisor fiscal o
un auditor van a pedir.

=== POR QUÉ NINGÚN VALOR SE ADIVINA ===

La regla de toda la librería: si un año no está, se levanta `AñoNoDisponible`.
Nunca se devuelve «el más cercano».

Viene de un error real. El código del que salió esto respondía la consulta de un
año desconocido con el valor del año más reciente y un `logger.warning`. Los
avisos no los lee nadie: quien pidiera el SMMLV de 2030 recibía el de 2026 y
liquidaba con él. Un número equivocado presentado como correcto es peor que un
error, porque nadie lo busca.

=== EL IPC LLEGÓ CORRIDO UN AÑO ===

La serie de IPC del código original estaba desplazada desde 2023: tenía 13,12 %
en 2023 (que es el de 2022) y 9,28 % en 2024 (que es el de 2023). No es un
detalle: el IPC es el techo del reajuste anual del canon de arrendamiento de
vivienda urbana (Ley 820 de 2003, art. 20). Con 9,28 % en vez de 5,20 % se
sube un arriendo cuatro puntos por encima del máximo legal, y el arrendador
queda expuesto a la restitución de lo cobrado de más.

Los valores de 2024 y 2025 se corrigieron contra los boletines del DANE. Los que
no se pudieron verificar uno por uno se marcan como `verificado=False` y la
librería se niega a usarlos salvo que se le pida expresamente.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


class AñoNoDisponible(LookupError):
    """No hay dato para ese año. A propósito no se sustituye por otro."""


class ValorSinVerificar(LookupError):
    """El dato está, pero no se ha cotejado con la fuente oficial."""


@dataclass(frozen=True)
class Valor:
    """Un valor legislativo y de dónde sale."""

    monto: Decimal
    #: Decreto, resolución o ley que lo fija. Es la mitad del producto.
    norma: str
    #: Falso mientras nadie haya cotejado el número con la publicación oficial.
    verificado: bool = True
    nota: Optional[str] = None

    def __str__(self) -> str:
        marca = "" if self.verificado else " [SIN VERIFICAR]"
        return f"{self.monto} ({self.norma}){marca}"


# ---------------------------------------------------------------------------
# Salario mínimo mensual legal vigente
# ---------------------------------------------------------------------------
SMMLV: dict[int, Valor] = {
    2026: Valor(Decimal("1750905"), "Decreto 1469 del 29/12/2025"),
    2025: Valor(Decimal("1423500"), "Decreto 2293 del 24/12/2024"),
    2024: Valor(Decimal("1300000"), "Decreto 2292 del 29/12/2023"),
    2023: Valor(Decimal("1160000"), "Decreto 2613 del 27/12/2022"),
    2022: Valor(Decimal("1000000"), "Decreto 1724 del 15/12/2021"),
    2021: Valor(Decimal("908526"), "Decreto 1785 del 29/12/2020"),
    2020: Valor(Decimal("877803"), "Decreto 2360 del 26/12/2019"),
    2019: Valor(Decimal("828116"), "Decreto 2451 del 27/12/2018"),
    2018: Valor(Decimal("781242"), "Decreto 2269 del 30/12/2017"),
    2017: Valor(Decimal("737717"), "Decreto 2209 del 30/12/2016"),
    2016: Valor(Decimal("689455"), "Decreto 2552 del 30/12/2015"),
    2015: Valor(Decimal("644350"), "Decreto 2731 del 30/12/2014"),
    2014: Valor(Decimal("616000"), "Decreto 3068 del 30/12/2013"),
}

# ---------------------------------------------------------------------------
# Auxilio de transporte
# ---------------------------------------------------------------------------
AUXILIO_TRANSPORTE: dict[int, Valor] = {
    2026: Valor(Decimal("249095"), "Decreto 1470 del 29/12/2025"),
    2025: Valor(Decimal("200000"), "Decreto 2294 del 24/12/2024"),
    2024: Valor(Decimal("162000"), "Decreto 2293 del 29/12/2023"),
    2023: Valor(Decimal("140606"), "Decreto 2614 del 27/12/2022"),
    2022: Valor(Decimal("117172"), "Decreto 1725 del 15/12/2021"),
    2021: Valor(Decimal("106454"), "Decreto 1786 del 29/12/2020"),
    2020: Valor(Decimal("102854"), "Decreto 2361 del 26/12/2019"),
    2019: Valor(Decimal("97032"), "Decreto 2452 del 27/12/2018"),
    2018: Valor(Decimal("88211"), "Decreto 2270 del 30/12/2017"),
    2017: Valor(Decimal("83140"), "Decreto 2210 del 30/12/2016"),
    2016: Valor(Decimal("77700"), "Decreto 2553 del 30/12/2015"),
    2015: Valor(Decimal("74000"), "Decreto 2732 del 30/12/2014"),
    2014: Valor(Decimal("72000"), "Decreto 3069 del 30/12/2013"),
}

# ---------------------------------------------------------------------------
# Unidad de Valor Tributario
# ---------------------------------------------------------------------------
UVT: dict[int, Valor] = {
    2026: Valor(Decimal("52374"), "Resolución DIAN 238 del 15/12/2025"),
    2025: Valor(Decimal("49799"), "Resolución DIAN 187 del 26/11/2024"),
    2024: Valor(Decimal("47065"), "Resolución DIAN 1264 del 21/11/2023"),
    2023: Valor(Decimal("42412"), "Resolución DIAN 1232 del 18/11/2022"),
    2022: Valor(Decimal("38004"), "Resolución DIAN 140 del 25/11/2021"),
    2021: Valor(Decimal("36308"), "Resolución DIAN 111 del 11/12/2020"),
    2020: Valor(Decimal("35607"), "Resolución DIAN 84 del 28/11/2019"),
    2019: Valor(Decimal("34270"), "Resolución DIAN 56 del 22/11/2018"),
    2018: Valor(Decimal("33156"), "Resolución DIAN 63 del 24/11/2017"),
    2017: Valor(Decimal("31859"), "Resolución DIAN 71 del 21/11/2016"),
    2016: Valor(Decimal("29753"), "Resolución DIAN 115 del 06/11/2015"),
    2015: Valor(Decimal("28279"), "Resolución DIAN 245 del 03/12/2014"),
    2014: Valor(Decimal("27485"), "Resolución DIAN 227 del 31/10/2013"),
}

# ---------------------------------------------------------------------------
# IPC — variación anual diciembre contra diciembre
#
# Es el techo del reajuste del canon de arrendamiento de vivienda urbana
# (Ley 820/2003, art. 20). El del año N se publica a comienzos del año N+1 y es
# el que rige los reajustes de N+1: por eso `incremento_arriendo` pide el año
# del contrato y usa el IPC del año anterior.
# ---------------------------------------------------------------------------
IPC: dict[int, Valor] = {
    2025: Valor(Decimal("5.10"), "DANE, boletín IPC diciembre 2025"),
    2024: Valor(Decimal("5.20"), "DANE, boletín IPC diciembre 2024"),
    # COTEJADO EL 2026-08-14 contra la fuente primaria: el comunicado del DANE
    # se titula literalmente «En diciembre de 2023 la variación anual del IPC fue
    # 9,28%» (cp-IPC-dic2023.pdf, publicado el 2024-01-09 junto al boletín
    # técnico bol-IPC-dic2023.pdf). Deja de estar sin verificar.
    #
    # Se conserva escrito de qué se corrigió, porque el error de origen era caro:
    # la serie venía DESPLAZADA un año y ponía 13,12 % en 2023, que es el de
    # 2022. El IPC es el techo del reajuste anual del canon de arrendamiento de
    # vivienda urbana (Ley 820 de 2003, art. 20), así que ese desplazamiento
    # subía un arriendo casi cuatro puntos por encima del máximo legal.
    2023: Valor(Decimal("9.28"), "DANE, boletín IPC diciembre 2023"),
    2022: Valor(Decimal("13.12"), "DANE, boletín IPC diciembre 2022"),
    2021: Valor(Decimal("5.62"), "DANE, boletín IPC diciembre 2021"),
    2020: Valor(Decimal("1.61"), "DANE, boletín IPC diciembre 2020"),
    2019: Valor(Decimal("3.80"), "DANE, boletín IPC diciembre 2019"),
    2018: Valor(Decimal("3.18"), "DANE, boletín IPC diciembre 2018"),
    2017: Valor(Decimal("4.09"), "DANE, boletín IPC diciembre 2017"),
    2016: Valor(Decimal("5.75"), "DANE, boletín IPC diciembre 2016"),
    2015: Valor(Decimal("6.77"), "DANE, boletín IPC diciembre 2015"),
    2014: Valor(Decimal("3.66"), "DANE, boletín IPC diciembre 2014"),
}

# ---------------------------------------------------------------------------
# Aportes a seguridad social y parafiscales
#
# Son porcentajes sobre el ingreso base de cotización. No cambian con el año
# sino con la ley, así que llevan la fecha desde la que rigen.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Tasa:
    porcentaje: Decimal
    desde: date
    norma: str


TASAS: dict[str, Tasa] = {
    "salud_empleado": Tasa(Decimal("0.04"), date(2007, 1, 1), "Ley 1122 de 2007"),
    "salud_empleador": Tasa(Decimal("0.085"), date(2007, 1, 1), "Ley 1122 de 2007"),
    "pension_empleado": Tasa(Decimal("0.04"), date(2003, 1, 1), "Ley 797 de 2003"),
    "pension_empleador": Tasa(Decimal("0.12"), date(2003, 1, 1), "Ley 797 de 2003"),
    "caja_compensacion": Tasa(Decimal("0.04"), date(1982, 1, 1), "Ley 21 de 1982"),
    "icbf": Tasa(Decimal("0.03"), date(1988, 1, 1), "Ley 89 de 1988"),
    "sena": Tasa(Decimal("0.02"), date(1994, 1, 1), "Ley 119 de 1994"),
}

#: Tarifas de riesgos laborales por clase (Decreto 1295 de 1994). Son la tarifa
#: MÍNIMA de cada clase; la efectiva la fija la ARL dentro del rango.
ARL: dict[int, tuple[Decimal, str]] = {
    1: (Decimal("0.00522"), "Riesgo mínimo"),
    2: (Decimal("0.01044"), "Riesgo bajo"),
    3: (Decimal("0.02436"), "Riesgo medio"),
    4: (Decimal("0.04350"), "Riesgo alto"),
    5: (Decimal("0.06960"), "Riesgo máximo"),
}


# ---------------------------------------------------------------------------
# Jornada y recargos
#
# La Ley 2466 de 2025 los cambia por etapas, así que no se pueden guardar por
# año: cada régimen lleva su ventana de vigencia y se busca por fecha.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Jornada:
    desde: date
    hasta: Optional[date]
    #: Hora en que empieza la jornada nocturna (formato 24 h).
    inicio_nocturna: int
    recargo_nocturno: Decimal
    recargo_dominical: Decimal
    horas_semana: int
    norma: str

    def rige_en(self, cuando: date) -> bool:
        if cuando < self.desde:
            return False
        return self.hasta is None or cuando <= self.hasta


JORNADAS: tuple[Jornada, ...] = (
    Jornada(date(2027, 7, 1), None, 19, Decimal("0.35"), Decimal("1.00"), 42,
            "Ley 2466 de 2025"),
    Jornada(date(2026, 7, 1), date(2027, 6, 30), 19, Decimal("0.35"), Decimal("0.90"), 42,
            "Ley 2466 de 2025"),
    Jornada(date(2025, 12, 25), date(2026, 6, 30), 19, Decimal("0.35"), Decimal("0.80"), 44,
            "Ley 2466 de 2025"),
    Jornada(date(2025, 7, 15), date(2025, 12, 24), 21, Decimal("0.35"), Decimal("0.80"), 44,
            "Ley 2101 de 2021"),
    Jornada(date(2025, 7, 1), date(2025, 7, 14), 21, Decimal("0.35"), Decimal("0.80"), 46,
            "Ley 2101 de 2021 y Ley 2466 de 2025"),
    Jornada(date(2024, 7, 15), date(2025, 6, 30), 21, Decimal("0.35"), Decimal("0.75"), 46,
            "Ley 2101 de 2021"),
    Jornada(date(2023, 7, 15), date(2024, 7, 14), 21, Decimal("0.35"), Decimal("0.75"), 47,
            "Ley 2101 de 2021"),
    Jornada(date(2014, 1, 1), date(2023, 7, 14), 21, Decimal("0.35"), Decimal("0.75"), 48,
            "CST, arts. 160 y 168"),
)

#: Recargos de horas extras sobre el valor de la hora ordinaria (CST, art. 168).
HORAS_EXTRAS: dict[str, Decimal] = {
    "extra_diurna": Decimal("0.25"),
    "extra_nocturna": Decimal("0.75"),
    "extra_dominical_diurna": Decimal("1.00"),
    "extra_dominical_nocturna": Decimal("1.50"),
}

# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Juan Carlos Isaza
"""Chibcha — constantes legislativas colombianas con su norma al lado.

    >>> from datetime import date
    >>> from chibcha import smmlv, uvt, incremento_arriendo
    >>> smmlv(2026).monto
    Decimal('1750905')
    >>> smmlv(2026).norma
    'Decreto 1469 del 29/12/2025'

Todo devuelve `Valor`, no un número pelado: el monto sirve para calcular y la
norma para sustentar. En una liquidación laboral, una declaración de renta o un
reajuste de canon, el número sin su fuente no se puede defender.

Si un año no está, se levanta `AñoNoDisponible`. Nunca se devuelve el año más
cercano: un valor equivocado que parece correcto no lo revisa nadie.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from .festivos import (
    dias_habiles_entre,
    es_dia_habil,
    es_festivo,
    festivos_de,
    siguiente_dia_habil,
    sumar_dias_habiles,
)
from .valores import (
    ARL,
    AUXILIO_TRANSPORTE,
    HORAS_EXTRAS,
    IPC,
    JORNADAS,
    SMMLV,
    TASAS,
    UVT,
    AñoNoDisponible,
    Jornada,
    Tasa,
    Valor,
    ValorSinVerificar,
)

__version__ = "0.1.0"

__all__ = [
    "smmlv", "auxilio_transporte", "uvt", "ipc",
    "tasa", "tarifa_arl", "jornada_en", "incremento_arriendo",
    "aplica_auxilio_transporte", "valor_hora",
    "festivos_de", "es_festivo", "es_dia_habil", "siguiente_dia_habil",
    "sumar_dias_habiles", "dias_habiles_entre",
    "Valor", "Tasa", "Jornada", "AñoNoDisponible", "ValorSinVerificar",
    "SMMLV", "AUXILIO_TRANSPORTE", "UVT", "IPC", "TASAS", "ARL", "JORNADAS",
    "HORAS_EXTRAS",
]


def _buscar(tabla: dict[int, Valor], año: Optional[int], que: str,
            *, admitir_sin_verificar: bool = False) -> Valor:
    año = año if año is not None else date.today().year
    try:
        valor = tabla[año]
    except KeyError:
        disponibles = f"{min(tabla)}–{max(tabla)}"
        raise AñoNoDisponible(
            f"No hay {que} para {año}. Disponible: {disponibles}. "
            f"Esta librería no sustituye por el año más cercano: un valor "
            f"aproximado en una liquidación no se distingue de uno correcto."
        ) from None
    if not valor.verificado and not admitir_sin_verificar:
        raise ValorSinVerificar(
            f"El {que} de {año} ({valor.monto}) no se ha cotejado con la fuente "
            f"oficial. {valor.nota or ''} "
            f"Si aun así lo quiere, pase admitir_sin_verificar=True."
        )
    return valor


def smmlv(año: Optional[int] = None, **kw) -> Valor:
    """Salario mínimo mensual legal vigente."""
    return _buscar(SMMLV, año, "SMMLV", **kw)


def auxilio_transporte(año: Optional[int] = None, **kw) -> Valor:
    """Auxilio de transporte mensual."""
    return _buscar(AUXILIO_TRANSPORTE, año, "auxilio de transporte", **kw)


def uvt(año: Optional[int] = None, **kw) -> Valor:
    """Unidad de Valor Tributario."""
    return _buscar(UVT, año, "UVT", **kw)


def ipc(año: Optional[int] = None, **kw) -> Valor:
    """Variación anual del IPC, diciembre contra diciembre, en porcentaje."""
    return _buscar(IPC, año, "IPC", **kw)


def tasa(nombre: str) -> Tasa:
    """Aporte a seguridad social o parafiscal, por nombre."""
    try:
        return TASAS[nombre]
    except KeyError:
        raise AñoNoDisponible(
            f"No existe la tasa «{nombre}». Hay: {', '.join(sorted(TASAS))}."
        ) from None


def tarifa_arl(clase_riesgo: int) -> tuple[Decimal, str]:
    """Tarifa mínima de riesgos laborales de una clase (Decreto 1295/1994).

    Es la MÍNIMA de la clase, no necesariamente la que cobra la ARL: dentro de
    cada clase hay un rango y la administradora fija la efectiva.
    """
    if clase_riesgo not in ARL:
        raise AñoNoDisponible(f"La clase de riesgo va de 1 a 5, no {clase_riesgo}.")
    return ARL[clase_riesgo]


def jornada_en(cuando: Optional[date] = None) -> Jornada:
    """Jornada y recargos que rigen en una fecha.

    Se busca por fecha y no por año porque la Ley 2466 de 2025 los cambia por
    etapas, incluso a mitad de año.
    """
    cuando = cuando or date.today()
    for j in JORNADAS:
        if j.rige_en(cuando):
            return j
    raise AñoNoDisponible(
        f"No hay régimen de jornada registrado para {cuando.isoformat()}. "
        f"El más antiguo empieza el {min(j.desde for j in JORNADAS).isoformat()}."
    )


def aplica_auxilio_transporte(salario: Decimal, año: Optional[int] = None) -> bool:
    """Si al trabajador le corresponde auxilio de transporte.

    Le corresponde a quien devengue hasta DOS salarios mínimos (Ley 15 de 1959
    y concordantes). El tope es inclusive.
    """
    return Decimal(salario) <= smmlv(año).monto * 2


def valor_hora(salario_mensual: Decimal, cuando: Optional[date] = None) -> Decimal:
    """Valor de la hora ordinaria.

    Depende de la jornada vigente, que la Ley 2466 de 2025 está bajando de 47 a
    42 horas: la MISMA mensualidad vale más por hora cada vez que baja. Es el
    detalle que más se olvida al liquidar horas extras de 2025 en adelante.
    """
    horas_mes = Decimal(jornada_en(cuando).horas_semana) * Decimal("4.3333")
    return (Decimal(salario_mensual) / horas_mes).quantize(Decimal("0.01"),
                                                          rounding=ROUND_HALF_UP)


def incremento_arriendo(canon: Decimal, año_del_reajuste: Optional[int] = None,
                        **kw) -> dict[str, object]:
    """Reajuste anual del canon de arrendamiento de vivienda urbana.

    El artículo 20 de la Ley 820 de 2003 lo limita al IPC del año calendario
    ANTERIOR. Se pide el año en que se hace el reajuste y se usa el IPC del
    año previo, que es el publicado.

    Devuelve el tope legal, no una recomendación: el arrendador puede subir
    menos, nunca más. Cobrar por encima expone a restituir lo cobrado de más.
    """
    año_del_reajuste = año_del_reajuste or date.today().year
    indice = ipc(año_del_reajuste - 1, **kw)
    canon = Decimal(canon)
    aumento = (canon * indice.monto / Decimal(100)).quantize(Decimal("1"),
                                                            rounding=ROUND_HALF_UP)
    return {
        "canon_anterior": canon,
        "incremento_maximo": aumento,
        "canon_maximo": canon + aumento,
        "ipc_aplicado": indice.monto,
        "año_del_ipc": año_del_reajuste - 1,
        "fuente": indice.norma,
        "fundamento": "Ley 820 de 2003, art. 20",
    }

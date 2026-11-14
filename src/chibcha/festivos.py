# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Juan Carlos Isaza
"""Festivos colombianos y días hábiles.

Colombia tiene dieciocho festivos al año, y doce de ellos se mueven. La Ley 51
de 1983 —la «ley Emiliani»— traslada al lunes siguiente los que no caen en
lunes, salvo una lista tasada que se celebra en su fecha exacta. Encima, cinco
dependen de la Pascua, que es móvil.

De ahí que no se puedan poner en una tabla: hay que calcularlos. Y de ahí que
tantos plazos se cuenten mal, porque un término «de diez días hábiles» en abril
no cae donde uno cree.

    >>> from datetime import date
    >>> es_festivo(date(2026, 1, 12))   # Reyes, corrido al lunes
    True
    >>> es_festivo(date(2026, 1, 6))    # el 6 ya no es festivo
    False
"""

from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache

#: Los que NO se mueven: se celebran en su fecha, caiga el día que caiga.
FIJOS: tuple[tuple[int, int, str], ...] = (
    (1, 1, "Año Nuevo"),
    (5, 1, "Día del Trabajo"),
    (7, 20, "Independencia"),
    (8, 7, "Batalla de Boyacá"),
    (12, 8, "Inmaculada Concepción"),
    (12, 25, "Navidad"),
)

#: Los que la Ley 51 de 1983 traslada al lunes siguiente.
TRASLADABLES: tuple[tuple[int, int, str], ...] = (
    (1, 6, "Reyes Magos"),
    (3, 19, "San José"),
    (6, 29, "San Pedro y San Pablo"),
    (8, 15, "Asunción de la Virgen"),
    (10, 12, "Día de la Raza"),
    (11, 1, "Todos los Santos"),
    (11, 11, "Independencia de Cartagena"),
)

#: Días después del Domingo de Pascua, y si se trasladan al lunes.
#: Jueves y Viernes Santo son los únicos religiosos que NO se mueven.
PASCUALES: tuple[tuple[int, bool, str], ...] = (
    (-3, False, "Jueves Santo"),
    (-2, False, "Viernes Santo"),
    (39, True, "Ascensión del Señor"),
    (60, True, "Corpus Christi"),
    (68, True, "Sagrado Corazón de Jesús"),
)


def domingo_de_pascua(año: int) -> date:
    """Domingo de Resurrección, por el algoritmo de Butcher (calendario gregoriano)."""
    a = año % 19
    b, c = divmod(año, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ele = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ele) // 451
    mes, dia = divmod(h + ele - 7 * m + 114, 31)
    return date(año, mes, dia + 1)


def lunes_siguiente(d: date) -> date:
    """El traslado de la ley Emiliani. Si ya es lunes, se queda donde está."""
    if d.weekday() == 0:
        return d
    return d + timedelta(days=(7 - d.weekday()) % 7)


@lru_cache(maxsize=128)
def _festivos(año: int) -> frozenset[date]:
    dias = {date(año, m, d) for m, d, _ in FIJOS}
    dias |= {lunes_siguiente(date(año, m, d)) for m, d, _ in TRASLADABLES}
    pascua = domingo_de_pascua(año)
    for desfase, traslada, _ in PASCUALES:
        f = pascua + timedelta(days=desfase)
        dias.add(lunes_siguiente(f) if traslada else f)
    return frozenset(dias)


def festivos_de(año: int) -> dict[date, str]:
    """Los festivos del año con su nombre, ordenados."""
    nombrados: dict[date, str] = {}
    for m, d, nombre in FIJOS:
        nombrados[date(año, m, d)] = nombre
    for m, d, nombre in TRASLADABLES:
        nombrados[lunes_siguiente(date(año, m, d))] = nombre
    pascua = domingo_de_pascua(año)
    for desfase, traslada, nombre in PASCUALES:
        f = pascua + timedelta(days=desfase)
        nombrados[lunes_siguiente(f) if traslada else f] = nombre
    return dict(sorted(nombrados.items()))


def es_festivo(d: date) -> bool:
    return d in _festivos(d.year)


def es_dia_habil(d: date) -> bool:
    """Hábil es de lunes a viernes y que no sea festivo.

    El sábado NO es hábil aquí. Para términos judiciales y administrativos es
    lo correcto; si su contrato cuenta el sábado, no use esta función.
    """
    return d.weekday() < 5 and not es_festivo(d)


def siguiente_dia_habil(d: date) -> date:
    """El primer hábil DESPUÉS de la fecha dada, aunque esa ya lo sea."""
    siguiente = d + timedelta(days=1)
    while not es_dia_habil(siguiente):
        siguiente += timedelta(days=1)
    return siguiente


def sumar_dias_habiles(d: date, dias: int) -> date:
    """Corre una fecha `dias` hábiles hacia adelante o hacia atrás.

    Con `dias=0` devuelve la misma fecha, sea hábil o no: sumar cero no debe
    mover nada.
    """
    if dias == 0:
        return d
    paso = timedelta(days=1 if dias > 0 else -1)
    restantes, actual = abs(dias), d
    while restantes:
        actual += paso
        if es_dia_habil(actual):
            restantes -= 1
    return actual


def dias_habiles_entre(inicio: date, fin: date) -> int:
    """Hábiles entre dos fechas, sin contar la de inicio y contando la de fin.

    Es el conteo de los términos: un plazo «de cinco días hábiles» que empieza
    el lunes vence el lunes siguiente, no el viernes.
    """
    if fin < inicio:
        return -dias_habiles_entre(fin, inicio)
    total, actual = 0, inicio
    while actual < fin:
        actual += timedelta(days=1)
        if es_dia_habil(actual):
            total += 1
    return total

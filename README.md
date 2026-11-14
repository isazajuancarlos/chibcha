# Chibcha

**Constantes legislativas colombianas con la norma que las fija.**

```python
from chibcha import smmlv, uvt, incremento_arriendo

smmlv(2026).monto      # Decimal('1750905')
smmlv(2026).norma      # 'Decreto 1469 del 29/12/2025'
```

Nada devuelve un número pelado. Devuelve el número **y de dónde sale**, porque
en una liquidación laboral, una declaración de renta o un reajuste de canon, el
valor sin su fuente no se puede sustentar ante nadie.

## Qué trae

| | Cobertura |
|---|---|
| Salario mínimo (SMMLV) | 2014–2026, con su decreto |
| Auxilio de transporte | 2014–2026, con su decreto |
| UVT | 2014–2026, con su resolución DIAN |
| IPC anual (dic./dic.) | 2014–2025, boletines DANE |
| Aportes y parafiscales | salud, pensión, caja, ICBF, SENA, con su ley |
| Tarifas de ARL | las cinco clases del Decreto 1295/1994 |
| Jornada y recargos | ocho regímenes con vigencia, incluida la Ley 2466 de 2025 |
| Festivos y días hábiles | cualquier año, con la Ley 51 de 1983 |

## Dos decisiones que la hacen distinta

### No adivina

Si un año no está, **levanta una excepción**. No devuelve «el más cercano».

```python
smmlv(2035)
# AñoNoDisponible: No hay SMMLV para 2035. Disponible: 2014–2026.
# Esta librería no sustituye por el año más cercano: un valor aproximado
# en una liquidación no se distingue de uno correcto.
```

Sale de un error real en el código del que nació: respondía los años
desconocidos con el valor más reciente y un `logger.warning`. Los avisos no los
lee nadie. Un número equivocado que parece correcto no lo revisa nadie tampoco.

### Distingue lo verificado de lo que no

Cada valor sabe si alguien lo cotejó con la publicación oficial. Los que no,
se niegan a salir salvo que se pidan a sabiendas:

```python
ipc(2023)
# ValorSinVerificar: El IPC de 2023 (9.28) no se ha cotejado con la fuente oficial.

ipc(2023, admitir_sin_verificar=True).monto   # Decimal('9.28')
```

## Arrendamientos

El artículo 20 de la Ley 820 de 2003 limita el reajuste anual del canon de
vivienda urbana al IPC del año **anterior**. La librería lo calcula con su
fundamento, para que se pueda poner en la carta:

```python
incremento_arriendo(1_000_000, 2025)
# {'canon_anterior': Decimal('1000000'),
#  'incremento_maximo': Decimal('52000'),
#  'canon_maximo': Decimal('1052000'),
#  'ipc_aplicado': Decimal('5.20'),
#  'año_del_ipc': 2024,
#  'fuente': 'DANE, boletín IPC diciembre 2024',
#  'fundamento': 'Ley 820 de 2003, art. 20'}
```

> La serie de IPC de la que se extrajo esta librería venía **corrida un año**
> desde 2023: usaba 9,28 % donde correspondía 5,20 %. Sobre un canon de un
> millón, eso son 40.800 pesos por encima del máximo legal, todos los meses, y
> el arrendador expuesto a restituir lo cobrado de más.

## Jornada laboral

La Ley 2466 de 2025 baja la jornada y sube el recargo dominical **por etapas**,
algunas a mitad de año. No caben en una tabla por año:

```python
jornada_en(date(2026, 6, 30)).horas_semana   # 44
jornada_en(date(2026, 7,  1)).horas_semana   # 42
jornada_en(date(2027, 7,  1)).recargo_dominical  # Decimal('1.00')
```

Y por eso `valor_hora` depende de la fecha: la misma mensualidad vale **más por
hora** cada vez que la jornada baja. Es lo que más se olvida al liquidar horas
extras de 2025 en adelante.

## Festivos y términos

Dieciocho al año, doce de ellos móviles, cinco atados a la Pascua:

```python
es_festivo(date(2026, 1, 6))    # False — Reyes se corrió
es_festivo(date(2026, 1, 12))   # True

sumar_dias_habiles(date(2026, 2, 2), 5)   # date(2026, 2, 9)
```

Un plazo de cinco días hábiles que empieza el lunes vence el **lunes
siguiente**, no el viernes. Ahí se equivocan la mitad de los cómputos.

## Instalación

```bash
pip install chibcha
```

Sin dependencias. Python 3.10 o superior.

## Advertencia

Esta librería **no es asesoría jurídica ni contable** y no sustituye la
consulta de la norma vigente. Las normas cambian; los valores aquí son una
compilación, no una fuente oficial. Antes de usar un valor en algo que produzca
efectos, cotéjelo con la publicación que se cita.

## Licencia

Apache-2.0. Los valores legislativos provienen de normas y publicaciones
oficiales colombianas, de dominio público conforme al artículo 41 de la Ley 23
de 1982; la compilación, la verificación y el código sí son obra protegida.
Ver [NOTICE](NOTICE).

© 2026 Juan Carlos Isaza.

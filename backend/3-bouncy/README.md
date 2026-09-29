# Backend 3 — Números bouncy

Implementación independiente en Python y TypeScript del problema de encontrar el menor número para el que la proporción de números bouncy sea exactamente un porcentaje dado.

## Python

```powershell
cd backend/3-bouncy/python
python -m pytest -q
python bouncy.py 99
```

La función `least_number_with_bouncy_ratio(percent: int) -> int` está disponible desde `bouncy.py`. Acepta porcentajes enteros de 1 a 99; para valores inválidos lanza `TypeError` o `ValueError`. La CLI imprime el resultado y termina con error para entradas inválidas.

## Node.js / TypeScript

```powershell
cd backend/3-bouncy/typescript
npm install
npm test
npm run build
npm start -- 99
```

Las funciones `leastNumberWithBouncyRatio(percent: number): number` y `least_number_with_bouncy_ratio(percent: number): number` se exportan desde `src/index.ts`; ambas son el mismo callable, y la segunda conserva el nombre de Python para facilitar la paridad entre lenguajes. El paquete compilado expone ese módulo y registra el comando `bouncy-ratio` como CLI (`bouncy-ratio 99`). Para generar el módulo y el ejecutable antes de consumir/publicar el paquete, ejecutar `npm run build`.

Ambas implementaciones validan 50 % → 538, 90 % → 21780 y 99 % → 1587000. La comparación de proporciones es entera: `100 × cantidad_bouncy === porcentaje × número`; no se usa coma flotante.

## Complejidad

Si `N` es la respuesta, se examinan secuencialmente los enteros del 1 al `N`. Para cada entero se inspeccionan como máximo sus `d = O(log N)` dígitos decimales. Por tanto, el tiempo es **O(N log N)** y el espacio auxiliar es **O(log N)** por la representación decimal del entero. No se almacena la secuencia de números visitados.

## Tiempo medido para 99 %

Medición de pared con PowerShell `Measure-Command`, ejecutando cada CLI desde Windows (incluye el arranque del intérprete/runtime):

| Implementación | Comando medido | Resultado | Tiempo |
| --- | --- | ---: | ---: |
| Python 3.14.5 | `python bouncy.py 99` | 1587000 | **1,14 s** |
| Node.js 24.15.0 + TypeScript compilado | `node dist/cli.js 99` | 1587000 | **0,153 s** |

Los tiempos dependen del equipo y del estado del sistema; se incluyen como referencia reproducible, no como garantía de rendimiento.

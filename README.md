# Mi Libro de Navidad de Trazos y Actividades

Generador en Python del interior (PDF) de un libro de actividades de
preescritura navideño para niños de 3 a 5 años, listo para Amazon KDP.

## Uso rápido

```bash
make venv        # crea .venv e instala dependencias (reportlab, pypdf, pillow, pytest)
make build       # genera output/libro_navidad_trazos.pdf y ejecuta el preflight
make test        # tests automáticos
make previews    # vistas previas PNG a 300 DPI en output/previews/
make color       # variante con interior a color
make nobleed     # variante 8.5 x 11 sin sangrado
```

Opciones del script: `python scripts/build_book.py --help`
(`--color`, `--no-bleed`, `--seed N` para otros laberintos, `--author`).

## Especificaciones KDP

| Concepto | Valor |
|---|---|
| Tamaño de corte | 8.5 x 11 in |
| Página con sangrado | 8.625 x 11.25 in (+0.125 in arriba, abajo y en el borde exterior; el lomo no lleva sangrado) |
| Margen de seguridad | 0.5 in exterior/superior/inferior, 0.625 in interior (mínimo KDP: 0.375 in) |
| Páginas | 40 (par, dentro del rango 24-828) |
| Fuentes | TrueType incrustadas (subconjunto) |
| Gráficos | 100 % vectoriales, sin imágenes rasterizadas: nítidos a 300 DPI o más |
| Color | B/N por defecto (grises solo con K en CMYK); `--color` para interior a color |

En KDP elige **"Con sangrado"** al subir el interior de la versión por defecto.

## Contenido (40 páginas)

| Págs. | Sección |
|---|---|
| 1-3 | Portada, "Este libro pertenece a…" y guía para adultos con leyenda de símbolos |
| 4-20 | Trazo progresivo: horizontales (reno → trineo, regalos → casas), verticales (nieve cayendo, estrellas → árboles), diagonales (adornos del árbol, estrellas fugaces), arcos, olas, zigzag, bucles, espirales, círculos, formas y dibujos completos |
| 21-28 | Une los puntos (8 a 12 puntos): regalo, estrella, gorro de Papá Noel, campana, arbolito, casita, bola, calcetín |
| 29-35 | Laberintos de 3x3 a 6x7 casillas |
| 36-38 | Escenas a página completa para colorear |
| 39 | Soluciones de los laberintos |
| 40 | Diploma |

Cada página de actividad incluye un dibujo de recompensa "¡Colorea!" en la
esquina exterior. La primera línea de cada ejercicio es un ejemplo continuo;
el resto son punteadas, con punto de inicio y flecha de dirección.

## Estructura

```
assets/fonts/              fuentes TTF incrustables (DejaVu Sans + licencia)
src/navidad_book/
  config.py                geometría KDP (corte, sangrado, márgenes por lado de página)
  fonts.py, palette.py     fuentes y paletas B/N y color
  layout.py                PageContext: texto, registro de cajas y validación
  graphics.py              biblioteca de dibujos vectoriales navideños
  draw.py                  líneas punteadas de trazo, punto de inicio, flechas
  frame.py                 cabecera, pie, nieve a sangre y recompensa
  maze.py                  generador y solucionador de laberintos (con semilla)
  pages/                   front, tracing, dots, mazes, coloring, ending
  book.py                  plan de páginas y ensamblado del PDF
scripts/build_book.py      CLI de generación
scripts/preflight.py       revisión independiente del PDF generado
tests/test_book.py
```

## Controles de calidad

1. **Durante la generación** (`layout.py`): cada texto y dibujo registra su
   caja. La build falla si algo sale del área de seguridad, si un texto se
   solapa con otro texto o con un dibujo, si el pie de página invade el
   contenido o si el fondo a sangre no llega al borde.
2. **Sobre el PDF** (`preflight.py`): número de páginas, MediaBox/TrimBox,
   fuentes incrustadas, ausencia de imágenes rasterizadas y posición de cada
   texto dentro del área de seguridad.

## Personalización

- **Tipografía**: para preescolar se recomienda una "a" de un solo piso
  (p. ej. *Andika*, licencia OFL). Copia los `.ttf` en `assets/fonts/` y
  cambia `FONT_FILES` en `fonts.py`.
- **Textos**: título y subtítulo en `config.py`; cada página define su propio
  título e instrucción en `pages/`.
- **Portada**: KDP necesita un PDF de cubierta aparte (con lomo), que este
  proyecto no genera.

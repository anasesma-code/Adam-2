# Comparador de precios de supermercados 🛒

Agente que, dada una lista de alimentos, busca su precio actual en
**Mercadona, Lidl, Eroski, Dia y Carrefour** y te dice dónde sale más barato
(comparando también por €/kg o €/L, porque los formatos cambian).

Usa la API de Claude con búsqueda web y lectura de páginas: consulta las tiendas
online oficiales y, si un producto no aparece allí, comparadores de precios,
citando la fuente. Si no encuentra un precio, lo dice en vez de inventarlo.

## Instalación

```bash
cd comparador_precios
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # o bien: ant auth login
```

## Uso

```bash
# Consulta directa
python comparador.py "leche entera, huevos, aceite de oliva virgen extra"

# Con tu código postal (algunas tiendas cambian precios por zona)
python comparador.py --cp 28001 "pan de molde, plátanos"

# Modo conversación: puedes hacer preguntas de seguimiento
python comparador.py
🛒 > leche, yogur natural, café molido
🛒 > ¿y si la leche es sin lactosa?
🛒 > salir
```

La respuesta trae una tabla por alimento (súper, producto, formato, precio y
precio unitario), cuál es el más barato y, si pides varios, un resumen de la
cesta indicando en qué supermercado conviene hacer toda la compra.

## Notas

- Los precios salen de la web en el momento de la consulta; pueden variar por
  zona, ofertas o stock en tienda física.
- Cada consulta hace varias búsquedas web, así que tarda un poco (de segundos
  a un par de minutos según el número de alimentos) y consume créditos de la API.
- Tests: `python -m pytest test_comparador.py`

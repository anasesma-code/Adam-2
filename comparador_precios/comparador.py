"""Agente comparador de precios de supermercados españoles.

Le dices una lista de alimentos y busca en la web el precio actual de cada uno
en Mercadona, Lidl, Eroski, Dia y Carrefour, y te dice dónde sale más barato.

Uso:
    python comparador.py                       # modo conversación
    python comparador.py "leche, huevos, aceite de oliva"
    python comparador.py --cp 28001 "pan de molde"
"""

from __future__ import annotations

import argparse
import sys

import anthropic

MODEL = "claude-opus-5-5"
SUPERMERCADOS = ["Mercadona", "Lidl", "Eroski", "Dia", "Carrefour"]
MAX_CONTINUACIONES = 8

SYSTEM_PROMPT = """\
Eres un comparador de precios de supermercados en España. El usuario te da uno o
varios alimentos y tú averiguas cuánto cuestan HOY en estos cinco supermercados:
Mercadona, Lidl, Eroski, Dia y Carrefour.

Cómo trabajar:
- Usa la búsqueda web y la lectura de páginas para encontrar precios reales y
  actuales. Prioriza las tiendas online oficiales (tienda.mercadona.es, lidl.es,
  supermercado.eroski.es, dia.es, carrefour.es). Si una tienda no muestra el
  producto online, puedes usar comparadores de precios fiables, indicando la fuente.
- Compara productos equivalentes: misma categoría y formato parecido (p. ej.
  leche entera brik 1 L de marca blanca). Por defecto elige la marca propia o la
  opción más barata de cada súper, salvo que el usuario pida una marca concreta.
- Como los formatos varían, compara siempre por precio unitario (€/kg, €/L o
  €/unidad) además del precio del envase.
- Si no encuentras un precio, escribe "no encontrado"; nunca te lo inventes.
- Si un alimento es ambiguo (p. ej. "queso"), elige la variante más común y dilo.

Formato de la respuesta (en español, Markdown):
1. Para cada alimento, una tabla con columnas:
   Supermercado | Producto | Formato | Precio | Precio unitario
   y debajo una línea "**Más barato: <súper>**" con el ahorro frente al más caro.
2. Si hay varios alimentos, al final un "Resumen de la cesta": el súper más
   barato para cada alimento y qué supermercado sale más barato comprando toda
   la cesta en un solo sitio (sumando solo los productos encontrados en todos).
3. Una nota breve con la fecha de consulta y que los precios pueden variar según
   la zona y las ofertas.
Sé conciso: nada de explicar cómo has buscado.
"""

TOOLS = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
        "max_uses": 30,
        "user_location": {"type": "approximate", "country": "ES", "timezone": "Europe/Madrid"},
    },
    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 30},
]


def _pregunta(alimentos: str, codigo_postal: str | None) -> str:
    texto = f"Compara el precio de: {alimentos}"
    if codigo_postal:
        texto += f"\n(Mi código postal es {codigo_postal}; úsalo si la tienda pide zona.)"
    return texto


def _mostrar(texto: str) -> None:
    try:
        from rich.console import Console
        from rich.markdown import Markdown

        Console().print(Markdown(texto))
    except ImportError:
        print(texto)


def consultar(client: anthropic.Anthropic, messages: list) -> str:
    """Ejecuta un turno del agente. Añade la respuesta a `messages` y devuelve el texto."""
    for _ in range(MAX_CONTINUACIONES):
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=32000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            for event in stream:
                if event.type == "content_block_start":
                    tipo = event.content_block.type
                    if tipo == "server_tool_use":
                        nombre = event.content_block.name
                        print("  · buscando..." if nombre == "web_search" else "  · leyendo página...",
                              file=sys.stderr, flush=True)
            response = stream.get_final_message()

        if messages[-1]["role"] == "assistant":
            # continuación de un pause_turn: forma parte del mismo turno del asistente
            messages[-1]["content"] = list(messages[-1]["content"]) + list(response.content)
        else:
            messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "pause_turn":
            continue  # el servidor sigue buscando donde lo dejó
        if response.stop_reason == "refusal":
            return "_No he podido completar esta consulta. Prueba a reformularla._"

        texto = "".join(b.text for b in response.content if b.type == "text").strip()
        if response.stop_reason == "max_tokens":
            texto += "\n\n_(Respuesta cortada: prueba con menos alimentos a la vez.)_"
        return texto
    return "_La búsqueda se ha alargado demasiado; prueba con menos alimentos a la vez._"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara precios en Mercadona, Lidl, Eroski, Dia y Carrefour.")
    parser.add_argument("alimentos", nargs="*", help="alimentos a comparar, p. ej. 'leche, huevos'")
    parser.add_argument("--cp", help="código postal (los precios online pueden depender de la zona)")
    args = parser.parse_args()

    client = anthropic.Anthropic()
    messages: list = []

    def turno(texto_usuario: str) -> None:
        messages.append({"role": "user", "content": texto_usuario})
        try:
            _mostrar(consultar(client, messages))
        except anthropic.AuthenticationError:
            sys.exit("Falta la clave de la API: exporta ANTHROPIC_API_KEY o ejecuta `ant auth login`.")
        except anthropic.RateLimitError:
            messages.pop()
            print("Demasiadas peticiones; espera un momento y vuelve a intentarlo.", file=sys.stderr)
        except (anthropic.APIConnectionError, anthropic.APIStatusError) as e:
            messages.pop()
            print(f"Error al consultar la API: {e}", file=sys.stderr)

    if args.alimentos:
        turno(_pregunta(" ".join(args.alimentos), args.cp))
        return 0

    print(f"Comparador de precios ({', '.join(SUPERMERCADOS)}).")
    print("Escribe alimentos separados por comas, o preguntas de seguimiento. 'salir' para terminar.\n")
    primero = True
    while True:
        try:
            linea = input("🛒 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not linea:
            continue
        if linea.lower() in {"salir", "exit", "quit"}:
            return 0
        turno(_pregunta(linea, args.cp) if primero else linea)
        primero = False


if __name__ == "__main__":
    sys.exit(main())
